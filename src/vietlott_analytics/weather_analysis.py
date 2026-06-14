from __future__ import annotations

import csv
import hashlib
import math
import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from statistics import fmean

from .io import ProductDataset


@dataclass(frozen=True, slots=True)
class WeatherDay:
    day: date
    venue_id: str
    venue_name: str
    temperature_mean: float
    temperature_min: float
    temperature_max: float
    humidity_mean: float


def load_weather_days(datasets_dir: Path) -> dict[date, WeatherDay]:
    path = datasets_dir / "weather" / "daily.csv"
    if not path.exists():
        return {}
    rows: dict[date, WeatherDay] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            day = date.fromisoformat(row["date"])
            rows[day] = WeatherDay(
                day=day,
                venue_id=row["venue_id"],
                venue_name=row["venue_name"],
                temperature_mean=float(row["temperature_2m_mean"]),
                temperature_min=float(row["temperature_2m_min"]),
                temperature_max=float(row["temperature_2m_max"]),
                humidity_mean=float(row["relative_humidity_2m_mean"]),
            )
    return rows


def build_weather_report(
    dataset: ProductDataset,
    weather_days: dict[date, WeatherDay],
) -> dict[str, object]:
    daily_outcomes: dict[date, list[float]] = defaultdict(list)
    daily_draws: dict[date, int] = defaultdict(int)
    for observation in dataset.observations:
        values = _observation_feature(dataset, observation)
        if values:
            daily_outcomes[observation.draw_date].extend(values)
            daily_draws[observation.draw_date] += 1

    matched_dates = sorted(set(daily_outcomes) & set(weather_days))
    matched_draws = sum(daily_draws[day] for day in matched_dates)
    total_draws = len(dataset.observations)
    venue_days: dict[str, int] = defaultdict(int)
    venue_names: dict[str, str] = {}
    samples: list[dict[str, object]] = []
    for day in matched_dates:
        weather = weather_days[day]
        venue_days[weather.venue_id] += 1
        venue_names[weather.venue_id] = weather.venue_name
        samples.append(
            {
                "date": day,
                "venue_id": weather.venue_id,
                "temperature": weather.temperature_mean,
                "humidity": weather.humidity_mean,
                "outcome": fmean(daily_outcomes[day]),
                "draws": daily_draws[day],
            }
        )

    associations = [
        _association(samples, "temperature", dataset.product.slug),
        _association(samples, "humidity", dataset.product.slug),
    ]
    q_values = _benjamini_hochberg([item["p_value"] for item in associations])
    for item, q_value in zip(associations, q_values, strict=True):
        item["q_value_bh"] = _round(q_value, 6)
        item["status"] = (
            "watch"
            if q_value < 0.05 and abs(float(item["correlation"])) >= 0.1
            else "descriptive"
        )

    temperature_bands = _temperature_bands(samples)
    watched = [item for item in associations if item["status"] == "watch"]
    if len(matched_dates) < 30:
        conclusion = "Chưa đủ ngày có cả kết quả quay và dữ liệu thời tiết để kiểm tra."
    elif watched:
        strongest = max(watched, key=lambda item: abs(float(item["correlation"])))
        conclusion = (
            f"Có liên hệ cần theo dõi với {strongest['label'].lower()}, "
            "nhưng dữ liệu ngoài trời chưa chứng minh nguyên nhân trong phòng quay."
        )
    else:
        conclusion = (
            "Chưa thấy liên hệ thực dụng ổn định sau khi đã loại bớt ảnh hưởng của "
            "tháng, năm và địa điểm quay."
        )

    return {
        "schema_version": 1,
        "status": "ready" if matched_dates else "missing",
        "source": {
            "name": "Open-Meteo Historical Weather API",
            "model": "ERA5-Land",
            "documentation": "https://open-meteo.com/en/docs/historical-weather-api",
            "venue_source": (
                "https://www.vietlott.vn/vi/tin-tuc/"
                "20199-thong-bao-thay-doi-dia-diem-trung-tam-quay-so-mo-thuong/"
            ),
        },
        "coverage": {
            "matched_draws": matched_draws,
            "total_draws": total_draws,
            "matched_days": len(matched_dates),
            "coverage_rate": _round(matched_draws / total_draws if total_draws else 0),
            "first_date": matched_dates[0].isoformat() if matched_dates else None,
            "latest_date": matched_dates[-1].isoformat() if matched_dates else None,
            "venues": [
                {
                    "id": venue_id,
                    "name": venue_names[venue_id],
                    "days": days,
                }
                for venue_id, days in sorted(venue_days.items())
            ],
        },
        "outcome_feature": {
            "label": (
                "Tổng trung bình của bộ số trong ngày"
                if dataset.product.kind.value == "number_set"
                else "Tổng chữ số trung bình trong ngày"
            ),
            "unit": "điểm mô tả",
        },
        "associations": associations,
        "temperature_bands": temperature_bands,
        "conclusion": conclusion,
        "method": (
            "Mỗi ngày chỉ tạo một điểm dữ liệu. Tương quan được tính sau khi trừ "
            "trung bình trong cùng tháng-năm và địa điểm; p được hoán vị trong các "
            "khối đó, q hiệu chỉnh hai phép kiểm."
        ),
        "limitations": [
            "Đây là thời tiết ngoài trời tái phân tích, không phải cảm biến trong phòng quay.",
            "Dữ liệu theo ngày không biết nhiệt độ đúng phút quay hoặc hoạt động điều hòa.",
            "Không có mã máy, mã bộ bi, bảo trì và luồng khí để suy luận cơ chế.",
        ],
    }


def _observation_feature(dataset: ProductDataset, observation) -> list[float]:
    if dataset.product.kind.value == "number_set":
        return [float(sum(observation.values))] if observation.values else []
    return [float(sum(int(digit) for digit in outcome)) for outcome in observation.outcomes]


def _association(
    samples: list[dict[str, object]],
    variable: str,
    product_slug: str,
) -> dict[str, object]:
    label = "Nhiệt độ trung bình" if variable == "temperature" else "Độ ẩm trung bình"
    if len(samples) < 12:
        return {
            "variable": variable,
            "label": label,
            "correlation": 0.0,
            "p_value": 1.0,
            "sample_days": len(samples),
        }
    groups: dict[tuple[int, int, str], list[int]] = defaultdict(list)
    for index, sample in enumerate(samples):
        day = sample["date"]
        groups[(day.year, day.month, str(sample["venue_id"]))].append(index)

    x = [float(sample[variable]) for sample in samples]
    y = [float(sample["outcome"]) for sample in samples]
    x_residual = _center_within_groups(x, groups)
    y_residual = _center_within_groups(y, groups)
    observed = _pearson(x_residual, y_residual)
    seed = int.from_bytes(
        hashlib.sha256(f"{product_slug}:{variable}:weather-v1".encode()).digest()[:8],
        "big",
    )
    rng = random.Random(seed)
    extreme = 0
    permutations = 499
    for _ in range(permutations):
        shuffled = list(y_residual)
        for indices in groups.values():
            values = [shuffled[index] for index in indices]
            rng.shuffle(values)
            for index, value in zip(indices, values, strict=True):
                shuffled[index] = value
        if abs(_pearson(x_residual, shuffled)) >= abs(observed) - 1e-12:
            extreme += 1
    return {
        "variable": variable,
        "label": label,
        "correlation": _round(observed, 6),
        "p_value": _round((extreme + 1) / (permutations + 1), 6),
        "sample_days": len(samples),
        "practical_threshold": 0.1,
    }


def _center_within_groups(
    values: list[float],
    groups: dict[tuple[int, int, str], list[int]],
) -> list[float]:
    centered = [0.0] * len(values)
    for indices in groups.values():
        mean = fmean(values[index] for index in indices)
        for index in indices:
            centered[index] = values[index] - mean
    return centered


def _pearson(left: list[float], right: list[float]) -> float:
    if not left or len(left) != len(right):
        return 0.0
    left_mean = fmean(left)
    right_mean = fmean(right)
    numerator = sum(
        (left_value - left_mean) * (right_value - right_mean)
        for left_value, right_value in zip(left, right, strict=True)
    )
    left_sum = sum((value - left_mean) ** 2 for value in left)
    right_sum = sum((value - right_mean) ** 2 for value in right)
    denominator = math.sqrt(left_sum * right_sum)
    return numerator / denominator if denominator else 0.0


def _temperature_bands(samples: list[dict[str, object]]) -> list[dict[str, object]]:
    if not samples:
        return []
    temperatures = sorted(float(sample["temperature"]) for sample in samples)
    lower = _quantile(temperatures, 1 / 3)
    upper = _quantile(temperatures, 2 / 3)
    bands = (
        ("cool", "Mát hơn", float("-inf"), lower),
        ("middle", "Trung bình", lower, upper),
        ("warm", "Nóng hơn", upper, float("inf")),
    )
    rows = []
    for band_id, label, minimum, maximum in bands:
        selected = [
            sample
            for sample in samples
            if minimum < float(sample["temperature"]) <= maximum
        ]
        rows.append(
            {
                "id": band_id,
                "label": label,
                "days": len(selected),
                "draws": sum(int(sample["draws"]) for sample in selected),
                "temperature_mean": _round(
                    fmean(float(sample["temperature"]) for sample in selected)
                )
                if selected
                else None,
                "outcome_mean": _round(
                    fmean(float(sample["outcome"]) for sample in selected)
                )
                if selected
                else None,
            }
        )
    return rows


def _quantile(values: list[float], probability: float) -> float:
    if len(values) == 1:
        return values[0]
    position = (len(values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return values[lower]
    fraction = position - lower
    return values[lower] * (1 - fraction) + values[upper] * fraction


def _benjamini_hochberg(values: list[float]) -> list[float]:
    total = len(values)
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    adjusted = [1.0] * total
    running = 1.0
    for rank, (original_index, value) in reversed(list(enumerate(indexed, start=1))):
        running = min(running, value * total / rank)
        adjusted[original_index] = min(1.0, running)
    return adjusted


def _round(value: float, digits: int = 6) -> float:
    return round(float(value), digits)
