const docsNumberFormatter = new Intl.NumberFormat("vi-VN");

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const [manifestResponse, qualityResponse] = await Promise.all([
      fetch("data/manifest.json", { cache: "no-store" }),
      fetch("data/dataset-quality.json", { cache: "no-store" }),
    ]);
    if (!manifestResponse.ok) throw new Error(`HTTP ${manifestResponse.status}`);
    const manifest = await manifestResponse.json();
    document.querySelectorAll("[data-manifest]").forEach((node) => {
      const value = manifest[node.dataset.manifest];
      node.textContent =
        typeof value === "number"
          ? docsNumberFormatter.format(value)
          : normalizeDocsText(value);
    });
    renderCoverage(manifest.products);
    if (qualityResponse.ok) {
      renderSourceQuality(await qualityResponse.json(), manifest.products);
    }
  } catch (error) {
    const table = document.getElementById("coverage-table");
    if (table) table.textContent = `Không đọc được manifest: ${error.message}`;
  }
});

function renderCoverage(products) {
  const rows = products
    .map(
      (product) => `
        <tr>
          <td>${escapeDocs(product.name)}</td>
          <td>${docsNumberFormatter.format(product.confirmed_draws)}</td>
          <td>${escapeDocs(formatDocsDate(product.first_date))}</td>
          <td>${escapeDocs(formatDocsDate(product.latest_date))}</td>
          <td>${product.active ? "Đang hoạt động" : "Lịch sử"}</td>
        </tr>`,
    )
    .join("");
  document.getElementById("coverage-table").innerHTML = `
    <table class="data-table">
      <thead><tr><th>Sản phẩm</th><th>Kỳ xác nhận</th><th>Từ ngày</th><th>Đến ngày</th><th>Trạng thái</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
}

function renderSourceQuality(quality, products) {
  const target = document.getElementById("source-quality-table");
  if (!target) return;
  const names = new Map(products.map((product) => [product.slug, product.name]));
  const rows = Object.entries(quality.products || {})
    .map(([slug, product]) => {
      const origins = product.source_origin || {};
      const agreement = product.source_agreement || {};
      const crossChecked =
        Number(agreement.official_verified_match || 0)
        + Number(agreement.multi_source_consensus || 0);
      const official = Number(origins.official || 0);
      const rows = Number(product.rows || 0);
      const unknown = Number(origins.unknown || 0);
      return `
        <tr>
          <td>${escapeDocs(names.get(slug) || slug)}</td>
          <td>${formatDocsPercent(official, rows)}</td>
          <td>${formatDocsPercent(crossChecked, rows)}</td>
          <td>${formatDocsPercent(product.result_coverage?.rows_with_result || 0, rows)}</td>
          <td>${formatDocsPercent(product.prize_coverage?.draws_with_prize_rows || 0, rows)}</td>
          <td>${docsNumberFormatter.format(unknown)}</td>
        </tr>`;
    })
    .join("");
  target.innerHTML = `
    <table class="data-table">
      <thead>
        <tr>
          <th>Sản phẩm</th>
          <th>Nguồn chính thức</th>
          <th>Đã đối chiếu</th>
          <th>Phủ kết quả</th>
          <th>Phủ giải thưởng</th>
          <th>Chưa truy nguồn</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>`;
}

function formatDocsPercent(numerator, denominator) {
  if (!denominator) return "0%";
  return (Number(numerator) / Number(denominator)).toLocaleString("vi-VN", {
    style: "percent",
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });
}

function formatDocsDate(value) {
  const [year, month, day] = value.split("-");
  return `${day}/${month}/${year}`;
}

function escapeDocs(value) {
  return normalizeDocsText(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function normalizeDocsText(value) {
  return String(value).normalize("NFC");
}
