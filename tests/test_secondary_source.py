from datetime import date

import pytest

from vietlott_collector.config import PRODUCT_SPECS
from vietlott_collector.incremental_update import _store_secondary_batch
from vietlott_collector.models import DrawRecord, PrizeRecord
from vietlott_collector.sources.secondary import SecondaryBatch, parse_secondary_page
from vietlott_collector.storage import SqliteDatasetStore


def test_parse_secondary_keno_and_bingo() -> None:
    keno_numbers = "".join(
        f'<span class="kq">{number:02d}</span>' for number in range(1, 21)
    )
    keno = parse_secondary_page(
        PRODUCT_SPECS["keno"],
        f"""
        <article class="xskeno">
          <span class="kyve">#0284690</span>
          <span class="ngay">14/06/2026</span>
          <div class="result">{keno_numbers}</div>
        </article>
        """,
        source_url="https://xosominhngoc.net.vn/kqxs-keno",
    )
    bingo = parse_secondary_page(
        PRODUCT_SPECS["bingo18"],
        """
        <article class="xsbingo18">
          <span class="kyve">#0171757</span>
          <span class="ngay">14/06/2026</span>
          <div class="result">
            <span class="kq">5</span><span class="kq">6</span><span class="kq">4</span>
          </div>
        </article>
        """,
        source_url="https://xosominhngoc.net.vn/kqxs-bingo18",
    )

    assert keno.draws[0].result["numbers"] == list(range(1, 21))
    assert keno.draws[0].attributes["official_verification_status"] == "pending"
    assert bingo.draws[0].result["digits"] == [5, 6, 4]
    assert bingo.draws[0].attributes["total"] == 15


def test_parse_secondary_matrix_result_and_prizes() -> None:
    batch = parse_secondary_page(
        PRODUCT_SPECS["power655"],
        """
        <div class="xspower">
          <span class="kyve">#001358</span>
          <span class="ngay">13/06/2026</span>
          <div class="result">
            <span class="kq">02</span><span class="kq">08</span>
            <span class="kq">19</span><span class="kq">33</span>
            <span class="kq">36</span><span class="kq">47</span>
            <span class="kq">42</span>
          </div>
          <table><tbody>
            <tr><td>Jackpot 1</td><td>6 số</td><td>0</td><td>46.360.660.800</td></tr>
            <tr><td>Giải nhất</td><td>5 số</td><td>19</td><td>40.000.000</td></tr>
          </tbody></table>
        </div>
        """,
        source_url="https://xosominhngoc.net.vn/kqxs-power-655",
    )

    assert batch.draws[0].result["numbers"] == [2, 8, 19, 33, 36, 47]
    assert batch.draws[0].result["special_numbers"] == [42]
    assert batch.draws[0].draw_id == "01358"
    assert batch.draws[0].prize_status == "secondary_complete"
    assert batch.prizes[0].prize_value_vnd == 46_360_660_800
    assert batch.prizes[1].winner_count == 19


def test_parse_secondary_max3d_tiers() -> None:
    batch = parse_secondary_page(
        PRODUCT_SPECS["max3d"],
        """
        <article class="xsmax3d">
          <span class="kyve">#001092</span>
          <span class="ngay">12/06/2026</span>
          <table class="table_max3d"><tbody>
            <tr>
              <td>Giải ĐB <span class="giaiMax3d">1Tr</span>
                  <span class="max3d_sl">(38)</span></td>
              <td class="max3d_number"><span class="kq">350</span><span class="kq">839</span></td>
              <td>Giải ĐB <span class="giaiMax3d">1Tỷ</span>
                  <span class="max3d_sl">(0)</span></td>
            </tr>
            <tr>
              <td>Giải Nhất <span class="giaiMax3d">350K</span>
                  <span class="max3d_sl">(33)</span></td>
              <td class="max3d_number">
                <span class="kq">975</span><span class="kq">955</span>
                <span class="kq">069</span><span class="kq">405</span>
              </td><td>Giải Nhất <span class="giaiMax3d">40Tr</span></td>
            </tr>
            <tr>
              <td>Giải Nhì</td><td class="max3d_number">
                <span class="kq">896</span><span class="kq">451</span>
                <span class="kq">810</span><span class="kq">851</span>
                <span class="kq">841</span><span class="kq">328</span>
              </td><td>Giải Nhì</td>
            </tr>
            <tr>
              <td>Giải Ba</td><td class="max3d_number">
                <span class="kq">397</span><span class="kq">888</span>
                <span class="kq">977</span><span class="kq">204</span>
                <span class="kq">623</span><span class="kq">070</span>
                <span class="kq">140</span><span class="kq">332</span>
              </td><td>Giải Ba</td>
            </tr>
          </tbody></table>
        </article>
        """,
        source_url="https://xosominhngoc.net.vn/kqxs-max3d",
    )

    assert batch.draws[0].result["tiers"]["special"] == ["350", "839"]
    assert batch.draws[0].result["tiers"]["third"][-1] == "332"
    assert batch.prizes[0].prize_value_vnd == 1_000_000


def test_secondary_store_rejects_a_conflicting_existing_draw(tmp_path) -> None:
    source_url = "https://xosominhngoc.net.vn/kqxs-power-655"
    record = DrawRecord(
        product="power655",
        draw_id="01359",
        draw_date=date(2026, 6, 16),
        result={"numbers": [1, 2, 3, 4, 5, 6], "special_numbers": [7]},
        source_url=source_url,
        prize_status="secondary_complete",
        validation_status="valid",
    )
    prize = PrizeRecord(
        product="power655",
        draw_id="01359",
        game_variant="Giá trị Jackpot 2",
        prize_tier="Jackpot 1",
        winning_rule="6 số",
        winner_count=0,
        prize_value_vnd=50_000_000_000,
        details={"data_source": "xosominhngoc_net_vn"},
        source_url=source_url,
    )
    store = SqliteDatasetStore(tmp_path)
    try:
        report = _store_secondary_batch(
            store,
            SecondaryBatch(draws=[record], prizes=[prize], source_url=source_url),
        )
        assert report["draws_inserted"] == 1

        conflicting = DrawRecord(
            product="power655",
            draw_id="01359",
            draw_date=date(2026, 6, 16),
            result={"numbers": [1, 2, 3, 4, 5, 8], "special_numbers": [7]},
            source_url=source_url,
            prize_status="secondary_complete",
            validation_status="valid",
        )
        with pytest.raises(RuntimeError, match="conflicts with stored draw"):
            _store_secondary_batch(
                store,
                SecondaryBatch(
                    draws=[conflicting],
                    prizes=[prize],
                    source_url=source_url,
                ),
            )
    finally:
        store.close()


def test_parse_modern_secondary_vlitem() -> None:
    html = """
    <ul class="vlds vl-mega">
      <li>
        <a class="vlitem" href="/kqxs-mega-645-ngay-21-10-2026"
           title="Kết quả Mega 6/45 kỳ #001578 ngày 21/10/2026">
          <span class="vlky"><b>#001578</b><time datetime="2026-10-21">T.Tư 21/10/2026</time></span>
          <span class="vlso">
            <span class="kq">04</span><span class="kq">10</span><span class="kq">14</span>
            <span class="kq">22</span><span class="kq">25</span><span class="kq">44</span>
          </span>
          <span class="vljp"><small>Jackpot</small><b>31.281.381.500</b></span>
        </a>
      </li>
    </ul>
    """
    batch = parse_secondary_page(
        PRODUCT_SPECS["mega645"],
        html,
        source_url="https://xosominhngoc.net.vn/kqxs-mega-645",
    )
    assert len(batch.draws) == 1
    assert batch.draws[0].draw_id == "01578"
    assert batch.draws[0].draw_date == date(2026, 10, 21)
    assert batch.draws[0].result["numbers"] == [4, 10, 14, 22, 25, 44]
    assert batch.draws[0].validation_status == "valid"


def test_parse_modern_secondary_vlitem_max3d() -> None:
    html = """
    <ul class="vlds vl-max3d">
      <li>
        <a class="vlitem" href="/kqxs-max3d-ngay-21-10-2026"
           title="Kết quả Max3D kỳ #001148 ngày 21/10/2026">
          <span class="vlky"><b>#001148</b><time datetime="2026-10-21">T.Tư 21/10/2026</time></span>
          <span class="vlso">
            <span class="vlg gdb"><em>ĐB</em><span class="vlbs"><span class="vlb">
              <span class="kq db">456</span><span class="kq db">213</span>
            </span></span></span>
            <span class="vlg gnhat"><em>Nhất</em><span class="vlbs"><span class="vlb">
              <span class="kq">650</span><span class="kq">872</span>
              <span class="kq">687</span><span class="kq">369</span>
            </span></span></span>
            <span class="vlg gnhi"><em>Nhì</em><span class="vlbs">
              <span class="vlb">
                <span class="kq">671</span><span class="kq">563</span><span class="kq">220</span>
              </span>
              <span class="vlb">
                <span class="kq">419</span><span class="kq">023</span><span class="kq">222</span>
              </span>
            </span></span>
            <span class="vlg gba"><em>Ba</em><span class="vlbs">
              <span class="vlb">
                <span class="kq">523</span><span class="kq">509</span>
                <span class="kq">237</span><span class="kq">385</span>
              </span>
              <span class="vlb">
                <span class="kq">452</span><span class="kq">403</span>
                <span class="kq">243</span><span class="kq">682</span>
              </span>
            </span></span>
          </span>
        </a>
      </li>
    </ul>
    """
    batch = parse_secondary_page(
        PRODUCT_SPECS["max3d"],
        html,
        source_url="https://xosominhngoc.net.vn/kqxs-max3d",
    )
    assert len(batch.draws) == 1
    assert batch.draws[0].draw_id == "01148"
    assert batch.draws[0].result["tiers"]["special"] == ["456", "213"]
    assert batch.draws[0].result["tiers"]["third"][-1] == "682"
    assert batch.draws[0].validation_status == "valid"


def test_parse_modern_secondary_with_client_prizes() -> None:
    class MockClient:
        def get_text(self, url: str) -> str:
            return """
            <table class="tblsltmega">
              <thead><tr><th>Giải</th><th>Trùng</th><th>SL</th><th>Giá trị</th></tr></thead>
              <tbody>
                <tr><td>Jackpot</td><td>6 số</td><td>1</td><td>31.281.381.500</td></tr>
                <tr><td>Giải nhất</td><td>5 số</td><td>63</td><td>10.000.000</td></tr>
              </tbody>
            </table>
            """

    html = """
    <a class="vlitem" href="/kqxs-mega-645-ngay-21-10-2026">
      <span class="vlky"><b>#001578</b><time datetime="2026-10-21">21/10/2026</time></span>
      <span class="vlso">
        <span class="kq">04</span><span class="kq">10</span><span class="kq">14</span>
        <span class="kq">22</span><span class="kq">25</span><span class="kq">44</span>
      </span>
    </a>
    """
    batch = parse_secondary_page(
        PRODUCT_SPECS["mega645"],
        html,
        source_url="https://xosominhngoc.net.vn/kqxs-mega-645",
        client=MockClient(),  # type: ignore[arg-type]
    )
    assert len(batch.draws) == 1
    assert batch.draws[0].prize_status == "secondary_complete"
    assert len(batch.prizes) == 2
    assert batch.prizes[0].prize_value_vnd == 31_281_381_500
    assert batch.prizes[1].winner_count == 63


def test_secondary_result_source_paginates_for_fast_products() -> None:
    from vietlott_collector.sources.secondary import SecondaryResultSource

    class MockPaginationClient:
        def get_text(self, url: str) -> str:
            if "kqxs-bingo18" in url:
                return """
                <a class="vlitem" href="#">
                  <span class="vlky"><b>#0192390</b><time datetime="2026-10-21">21/10/2026</time></span>
                  <span class="vlso"><span class="kq">1</span><span class="kq">2</span><span class="kq">3</span></span>
                </a>
                """
            if "page=1" in url:
                return """
                <a class="vlitem" href="#">
                  <span class="vlky"><b>#0192389</b><time datetime="2026-10-21">21/10/2026</time></span>
                  <span class="vlso"><span class="kq">4</span><span class="kq">5</span><span class="kq">6</span></span>
                </a>
                <a class="vlitem" href="#">
                  <span class="vlky"><b>#0192388</b><time datetime="2026-10-21">21/10/2026</time></span>
                  <span class="vlso"><span class="kq">2</span><span class="kq">2</span><span class="kq">2</span></span>
                </a>
                """
            return ""

    source = SecondaryResultSource(MockPaginationClient())  # type: ignore[arg-type]
    batch = source.fetch(
        PRODUCT_SPECS["bingo18"],
        existing_ids={"0192388"},
        max_pages=2,
    )
    assert len(batch.draws) == 2
    assert batch.draws[0].draw_id == "0192390"
    assert batch.draws[1].draw_id == "0192389"


