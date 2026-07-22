from __future__ import annotations

import csv
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from vietlott_analytics.catalog import PRODUCTS
from vietlott_analytics.io import Observation, ProductDataset
from vietlott_analytics.weather_analysis import (
    WeatherDay,
    build_weather_report,
    load_weather_days,
)


def test_weather_report_uses_one_sample_per_day_and_reports_coverage() -> None:
    product = PRODUCTS["keno"]
    start = date(2025, 1, 22)
    observations = []
    weather = {}
    for day_index in range(60):
        draw_date = start + timedelta(days=day_index)
        weather[draw_date] = WeatherDay(
            day=draw_date,
            venue_id="tam_trinh",
            venue_name="VTC Online",
            temperature_mean=16 + day_index % 20,
            temperature_min=12,
            temperature_max=36,
            humidity_mean=55 + day_index % 30,
        )
        for draw_index in range(3):
            observations.append(
                Observation(
                    draw_id=str(day_index * 3 + draw_index + 1).zfill(7),
                    draw_date=draw_date,
                    values=tuple(range(1 + draw_index, 21 + draw_index)),
                )
            )
    dataset = ProductDataset(
        product=product,
        observations=observations,
        source_counts=Counter({"vietlott.vn": len(observations)}),
        status_counts=Counter({"confirmed": len(observations)}),
        validation_counts=Counter({"valid": len(observations)}),
    )

    report = build_weather_report(dataset, weather)

    assert report["status"] == "ready"
    assert report["coverage"]["matched_days"] == 60
    assert report["coverage"]["matched_draws"] == 180
    assert report["coverage"]["venues"] == [
        {"id": "tam_trinh", "name": "VTC Online", "days": 60}
    ]
    assert all(item["sample_days"] == 60 for item in report["associations"])
    assert len(report["temperature_bands"]) == 3
    assert sum(item["days"] for item in report["temperature_bands"]) == 60


def test_load_weather_days_reads_reproducible_csv(tmp_path: Path) -> None:
    weather_dir = tmp_path / "weather"
    weather_dir.mkdir()
    path = weather_dir / "daily.csv"
    fields = [
        "date",
        "venue_id",
        "venue_name",
        "temperature_2m_mean",
        "temperature_2m_min",
        "temperature_2m_max",
        "relative_humidity_2m_mean",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow(
            {
                "date": "2025-01-22",
                "venue_id": "tam_trinh",
                "venue_name": "VTC Online",
                "temperature_2m_mean": "18.8",
                "temperature_2m_min": "15.1",
                "temperature_2m_max": "23.1",
                "relative_humidity_2m_mean": "82",
            }
        )

    rows = load_weather_days(tmp_path)

    assert rows[date(2025, 1, 22)].venue_id == "tam_trinh"
    assert rows[date(2025, 1, 22)].temperature_mean == 18.8
