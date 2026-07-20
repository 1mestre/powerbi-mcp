"""
html_generators.py
==================
Generates self-contained HTML strings for use inside Power BI's "HTML Content"
visual (by Daniel Marsh-Patrick).

Each function receives plain Python data (lists/dicts/numbers) derived from a
DAX query executed via pbi_connector, and returns a single HTML string that can
be:

  1. Returned directly to the AI agent as a DAX measure expression:
         measure 'My Chart' = "<html>..."
     The agent then writes it to a .tmdl file via add_measure_to_tmdl().

  2. Previewed standalone in a browser for quick iteration.

Visual types available
----------------------
  gen_bar_chart          – Horizontal gauge-style bar chart (1–N rows)
  gen_donut_chart        – SVG donut / ring chart (up to 6 slices)
  gen_kpi_card           – KPI card with attainment progress bar + flip effect
  gen_clustered_bar      – Clustered horizontal bar chart (multi-series)
  gen_stacked_column     – Stacked vertical column chart
  gen_line_chart         – Simple SVG polyline / time-series chart
  gen_html_table         – Styled HTML table with conditional row colouring

Design conventions (matching the Fasaclox pattern)
---------------------------------------------------
* Font: Segoe UI, sans-serif  (native Power BI font)
* All CSS is inlined / scoped with short class names to avoid conflicts inside
  the sandboxed iframe that the HTML Content visual creates.
* No external CDN or JS library references – everything is vanilla CSS + SVG.
* Colours follow a professional dark-accent palette compatible with both light
  and dark Power BI themes.
"""

from typing import Any


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _fmt_number(value: float, prefix: str = "", suffix: str = "",
                decimals: int = 0) -> str:
    """Format a numeric value with thousands separator and optional pre/suffix."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    fmt = f"{{:,.{decimals}f}}"
    return f"{prefix}{fmt.format(v)}{suffix}"


def _pct(part: float, total: float, decimals: int = 1) -> float:
    """Safe percentage calculation; returns 0 if total is 0."""
    try:
        return round((float(part) / float(total)) * 100, decimals) if total else 0.0
    except (TypeError, ZeroDivisionError):
        return 0.0


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, float(value)))


# ---------------------------------------------------------------------------
# 1. gen_bar_chart  –  Horizontal gauge-style bar chart
# ---------------------------------------------------------------------------

def gen_bar_chart(
    data: list[dict],
    label_key: str,
    value_key: str,
    title: str = "Bar Chart",
    color: str = "#3b82f6",
    value_prefix: str = "",
    value_suffix: str = "",
    value_decimals: int = 0,
) -> str:
    """Horizontal gauge-style bar chart.

    Args:
        data:           List of row dicts from execute_dax().
        label_key:      Column name to use as the bar label.
        value_key:      Column name to use as the bar value.
        title:          Chart title displayed at the top.
        color:          CSS colour for the filled bar (hex, rgb, or named).
        value_prefix:   String prepended to displayed values (e.g. "$").
        value_suffix:   String appended to displayed values (e.g. " units").
        value_decimals: Decimal places in the displayed value label.

    Returns:
        Self-contained HTML string ready for Power BI HTML Content visual.
    """
    if not data:
        return "<div style='font-family:Segoe UI;padding:12px;color:#888'>No data</div>"

    max_val = max((float(row.get(value_key, 0) or 0) for row in data), default=1)
    max_val = max_val or 1

    rows_html = ""
    for row in data:
        label = str(row.get(label_key, ""))
        val   = float(row.get(value_key, 0) or 0)
        pct   = _clamp(val / max_val * 100)
        fmt   = _fmt_number(val, value_prefix, value_suffix, value_decimals)
        rows_html += f"""
        <div class="bc-row">
          <div class="bc-label">{label}</div>
          <div class="bc-track">
            <div class="bc-fill" style="width:{pct}%;background:{color}"></div>
          </div>
          <div class="bc-val">{fmt}</div>
        </div>"""

    return f"""<style>
  .bc{{font-family:Segoe UI,sans-serif;padding:12px 16px;width:100%;box-sizing:border-box}}
  .bc-title{{font-size:13px;font-weight:700;color:#1e293b;margin-bottom:10px}}
  .bc-row{{display:flex;align-items:center;margin-bottom:6px;gap:8px}}
  .bc-label{{min-width:110px;font-size:12px;color:#475569;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
  .bc-track{{flex:1;height:14px;background:#e2e8f0;border-radius:7px;overflow:hidden}}
  .bc-fill{{height:100%;border-radius:7px;transition:width .4s ease}}
  .bc-val{{min-width:60px;font-size:12px;color:#1e293b;text-align:right;font-weight:600}}
</style>
<div class="bc">
  <div class="bc-title">{title}</div>
  {rows_html}
</div>"""


# ---------------------------------------------------------------------------
# 2. gen_donut_chart  –  SVG donut / ring chart
# ---------------------------------------------------------------------------

def gen_donut_chart(
    data: list[dict],
    label_key: str,
    value_key: str,
    title: str = "Donut Chart",
    colors: list[str] | None = None,
) -> str:
    """SVG donut chart with legend.

    Args:
        data:      List of row dicts (max 8 slices rendered cleanly).
        label_key: Column name for slice labels.
        value_key: Column name for slice values (numeric).
        title:     Chart title.
        colors:    Optional list of CSS colour strings; defaults to a curated palette.

    Returns:
        Self-contained HTML string.
    """
    _DEFAULT_COLORS = [
        "#3b82f6", "#10b981", "#f59e0b", "#ef4444",
        "#8b5cf6", "#06b6d4", "#f97316", "#84cc16",
    ]
    if not colors:
        colors = _DEFAULT_COLORS

    if not data:
        return "<div style='font-family:Segoe UI;padding:12px;color:#888'>No data</div>"

    total = sum(float(row.get(value_key, 0) or 0) for row in data)
    total = total or 1

    R = 80          # outer radius
    r = 52          # inner radius (hole)
    CX = CY = 100   # centre of 200×200 viewBox
    CIRC = 2 * 3.14159265 * R  # circumference

    # Build SVG slices
    offset = 0.0
    slices = ""
    legend = ""
    for i, row in enumerate(data):
        label = str(row.get(label_key, ""))
        val   = float(row.get(value_key, 0) or 0)
        pct   = val / total
        arc   = round(pct * CIRC, 4)
        gap   = round(CIRC - arc, 4)
        c     = colors[i % len(colors)]
        pct_label = f"{round(pct * 100, 1)}%"

        slices += (
            f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="{c}" '
            f'stroke-width="{R - r}" '
            f'stroke-dasharray="{arc} {gap}" '
            f'stroke-dashoffset="-{round(offset, 4)}" />'
        )
        offset += arc

        legend += (
            f'<div class="dn-leg-row">'
            f'<span class="dn-dot" style="background:{c}"></span>'
            f'<span class="dn-lname">{label}</span>'
            f'<span class="dn-lpct">{pct_label}</span>'
            f'</div>'
        )

    return f"""<style>
  .dn{{font-family:Segoe UI,sans-serif;padding:10px 14px;width:100%;box-sizing:border-box}}
  .dn-title{{font-size:13px;font-weight:700;color:#1e293b;margin-bottom:8px}}
  .dn-wrap{{display:flex;align-items:center;gap:16px}}
  .dn-svg-wrap{{position:relative;width:120px;height:120px;flex-shrink:0}}
  .dn-svg{{transform:rotate(-90deg)}}
  .dn-center{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}}
  .dn-total{{font-size:11px;font-weight:700;color:#1e293b}}
  .dn-sub{{font-size:9px;color:#94a3b8}}
  .dn-legend{{display:flex;flex-direction:column;gap:4px;overflow:hidden}}
  .dn-leg-row{{display:flex;align-items:center;gap:6px}}
  .dn-dot{{width:10px;height:10px;border-radius:50%;flex-shrink:0}}
  .dn-lname{{font-size:11px;color:#475569;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
  .dn-lpct{{font-size:11px;font-weight:600;color:#1e293b;min-width:36px;text-align:right}}
</style>
<div class="dn">
  <div class="dn-title">{title}</div>
  <div class="dn-wrap">
    <div class="dn-svg-wrap">
      <svg class="dn-svg" width="120" height="120" viewBox="0 0 200 200">
        {slices}
      </svg>
      <div class="dn-center">
        <span class="dn-total">{len(data)}</span>
        <span class="dn-sub">categories</span>
      </div>
    </div>
    <div class="dn-legend">{legend}</div>
  </div>
</div>"""


# ---------------------------------------------------------------------------
# 3. gen_kpi_card  –  KPI attainment card with progress bar
# ---------------------------------------------------------------------------

def gen_kpi_card(
    value: float,
    target: float,
    label: str = "KPI",
    value_prefix: str = "",
    value_suffix: str = "",
    value_decimals: int = 0,
    subtitle: str = "",
) -> str:
    """KPI card showing actual value, target, attainment % and a progress bar.

    Args:
        value:          Actual / current value.
        target:         Target value.
        label:          Card title (e.g. "Total Revenue").
        value_prefix:   Prefix for displayed values (e.g. "$").
        value_suffix:   Suffix for displayed values (e.g. " units").
        value_decimals: Decimal places.
        subtitle:       Optional small text under the title (e.g. "YTD 2024").

    Returns:
        Self-contained HTML string.
    """
    attain     = _pct(value, target, 1) if target else 0.0
    bar_w      = _clamp(attain)
    fmt_val    = _fmt_number(value,  value_prefix, value_suffix, value_decimals)
    fmt_target = _fmt_number(target, value_prefix, value_suffix, value_decimals)
    gap        = abs(target - value)
    fmt_gap    = _fmt_number(gap, value_prefix, value_suffix, value_decimals)
    gap_label  = "Left to reach target" if value < target else "Exceeded target by"
    attain_str = f"{attain:.1f}%"

    # Tier colour
    if attain >= 100:
        tier_color = "#10b981"   # green
        tier_bg    = "#ecfdf5"
    elif attain >= 70:
        tier_color = "#3b82f6"   # blue
        tier_bg    = "#eff6ff"
    elif attain >= 40:
        tier_color = "#f59e0b"   # amber
        tier_bg    = "#fffbeb"
    else:
        tier_color = "#ef4444"   # red
        tier_bg    = "#fef2f2"

    sub_html = f'<div class="kc-sub">{subtitle}</div>' if subtitle else ""

    return f"""<style>
  .kc{{font-family:Segoe UI,sans-serif;padding:14px 18px;border-radius:12px;
       border:1px solid #e2e8f0;width:100%;box-sizing:border-box;background:#fff}}
  .kc-label{{font-size:11px;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:.05em}}
  .kc-sub{{font-size:10px;color:#cbd5e1;margin-bottom:4px}}
  .kc-val{{font-size:28px;font-weight:800;color:#0f172a;line-height:1.1;margin:4px 0}}
  .kc-row{{display:flex;justify-content:space-between;align-items:center;margin-top:10px}}
  .kc-target{{font-size:11px;color:#64748b}}
  .kc-badge{{font-size:12px;font-weight:700;padding:2px 8px;border-radius:20px;
             color:{tier_color};background:{tier_bg}}}
  .kc-track{{height:8px;background:#f1f5f9;border-radius:4px;overflow:hidden;margin-top:8px}}
  .kc-fill{{height:100%;border-radius:4px;background:{tier_color};width:{bar_w}%}}
  .kc-footer{{display:flex;justify-content:space-between;margin-top:6px}}
  .kc-gap{{font-size:10px;color:#94a3b8}}
  .kc-pct{{font-size:10px;font-weight:600;color:{tier_color}}}
</style>
<div class="kc">
  <div class="kc-label">{label}</div>
  {sub_html}
  <div class="kc-val">{fmt_val}</div>
  <div class="kc-row">
    <span class="kc-target">Target: {fmt_target}</span>
    <span class="kc-badge">{attain_str}</span>
  </div>
  <div class="kc-track"><div class="kc-fill"></div></div>
  <div class="kc-footer">
    <span class="kc-gap">{gap_label}: {fmt_gap}</span>
    <span class="kc-pct">{attain_str} attained</span>
  </div>
</div>"""


# ---------------------------------------------------------------------------
# 4. gen_clustered_bar  –  Multi-series clustered horizontal bar chart
# ---------------------------------------------------------------------------

def gen_clustered_bar(
    data: list[dict],
    label_key: str,
    series: list[dict],
    title: str = "Clustered Bar Chart",
) -> str:
    """Multi-series clustered horizontal bar chart.

    Args:
        data:       List of row dicts from execute_dax().
        label_key:  Column name for the category label (Y axis).
        series:     List of series descriptors, each a dict with keys:
                      - "key"    : column name in data
                      - "label"  : display name in the legend
                      - "color"  : CSS colour string
        title:      Chart title.

    Example series:
        [
          {"key": "Sales", "label": "Net Sales", "color": "#3b82f6"},
          {"key": "Cost",  "label": "Costs",     "color": "#ef4444"},
        ]

    Returns:
        Self-contained HTML string.
    """
    if not data or not series:
        return "<div style='font-family:Segoe UI;padding:12px;color:#888'>No data</div>"

    all_vals = [
        float(row.get(s["key"], 0) or 0)
        for row in data for s in series
    ]
    max_val = max(all_vals, default=1) or 1

    rows_html = ""
    for row in data:
        category = str(row.get(label_key, ""))
        bars_html = ""
        for s in series:
            val = float(row.get(s["key"], 0) or 0)
            pct = _clamp(val / max_val * 100)
            fmt = _fmt_number(val)
            bars_html += f"""
          <div class="cb-series-row">
            <div class="cb-slabel">{s["label"]}</div>
            <div class="cb-track">
              <div class="cb-fill" style="width:{pct}%;background:{s['color']}"></div>
            </div>
            <div class="cb-sval">{fmt}</div>
          </div>"""
        rows_html += f"""
      <div class="cb-group">
        <div class="cb-cat">{category}</div>
        {bars_html}
      </div>"""

    legend_html = "".join(
        f'<span class="cb-leg-item"><span class="cb-leg-dot" style="background:{s["color"]}"></span>{s["label"]}</span>'
        for s in series
    )

    return f"""<style>
  .cb{{font-family:Segoe UI,sans-serif;padding:12px 16px;width:100%;box-sizing:border-box}}
  .cb-title{{font-size:13px;font-weight:700;color:#1e293b;margin-bottom:6px}}
  .cb-legend{{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:10px}}
  .cb-leg-item{{display:flex;align-items:center;gap:4px;font-size:11px;color:#475569}}
  .cb-leg-dot{{width:9px;height:9px;border-radius:50%}}
  .cb-group{{margin-bottom:10px}}
  .cb-cat{{font-size:12px;font-weight:600;color:#334155;margin-bottom:4px}}
  .cb-series-row{{display:flex;align-items:center;gap:8px;margin-bottom:3px}}
  .cb-slabel{{min-width:70px;font-size:11px;color:#94a3b8;white-space:nowrap}}
  .cb-track{{flex:1;height:11px;background:#f1f5f9;border-radius:6px;overflow:hidden}}
  .cb-fill{{height:100%;border-radius:6px;transition:width .4s ease}}
  .cb-sval{{min-width:50px;font-size:11px;color:#1e293b;font-weight:600;text-align:right}}
</style>
<div class="cb">
  <div class="cb-title">{title}</div>
  <div class="cb-legend">{legend_html}</div>
  {rows_html}
</div>"""


# ---------------------------------------------------------------------------
# 5. gen_stacked_column  –  Vertical stacked column chart (SVG)
# ---------------------------------------------------------------------------

def gen_stacked_column(
    data: list[dict],
    label_key: str,
    series: list[dict],
    title: str = "Stacked Column Chart",
    chart_height: int = 160,
) -> str:
    """Vertical stacked column chart rendered with inline SVG.

    Args:
        data:         List of row dicts.
        label_key:    Column name for X-axis labels.
        series:       Same format as gen_clustered_bar series.
        title:        Chart title.
        chart_height: Pixel height of the SVG drawing area.

    Returns:
        Self-contained HTML string.
    """
    if not data or not series:
        return "<div style='font-family:Segoe UI;padding:12px;color:#888'>No data</div>"

    # Compute column totals for scale
    totals = [
        sum(float(row.get(s["key"], 0) or 0) for s in series)
        for row in data
    ]
    max_total = max(totals, default=1) or 1

    n_cols   = len(data)
    COL_W    = 36
    COL_GAP  = 20
    PAD_L    = 10
    SVG_W    = PAD_L * 2 + n_cols * (COL_W + COL_GAP) - COL_GAP
    SVG_H    = chart_height
    LABEL_H  = 24

    columns_svg = ""
    for ci, row in enumerate(data):
        x       = PAD_L + ci * (COL_W + COL_GAP)
        total   = totals[ci]
        seg_y   = SVG_H - LABEL_H   # start from top of bar area (bottom-up)

        for s in series:
            val  = float(row.get(s["key"], 0) or 0)
            h    = round((val / max_total) * (SVG_H - LABEL_H), 2) if max_total else 0
            seg_y -= h
            if h > 0:
                columns_svg += (
                    f'<rect x="{x}" y="{round(seg_y, 2)}" width="{COL_W}" height="{round(h, 2)}" '
                    f'fill="{s["color"]}" rx="2"/>'
                )

        # X-axis label
        label_x = x + COL_W / 2
        label   = str(row.get(label_key, ""))[:8]  # truncate long labels
        columns_svg += (
            f'<text x="{round(label_x, 1)}" y="{SVG_H - 6}" '
            f'text-anchor="middle" font-size="10" fill="#64748b">{label}</text>'
        )

    legend_html = "".join(
        f'<span class="sc-leg-item"><span class="sc-leg-dot" style="background:{s["color"]}"></span>{s["label"]}</span>'
        for s in series
    )

    return f"""<style>
  .sc{{font-family:Segoe UI,sans-serif;padding:12px 16px;width:100%;box-sizing:border-box}}
  .sc-title{{font-size:13px;font-weight:700;color:#1e293b;margin-bottom:6px}}
  .sc-legend{{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:8px}}
  .sc-leg-item{{display:flex;align-items:center;gap:4px;font-size:11px;color:#475569}}
  .sc-leg-dot{{width:9px;height:9px;border-radius:50%}}
  .sc-svg{{overflow:visible}}
</style>
<div class="sc">
  <div class="sc-title">{title}</div>
  <div class="sc-legend">{legend_html}</div>
  <svg class="sc-svg" width="{SVG_W}" height="{SVG_H}" viewBox="0 0 {SVG_W} {SVG_H}">
    {columns_svg}
  </svg>
</div>"""


# ---------------------------------------------------------------------------
# 6. gen_line_chart  –  SVG polyline time-series chart
# ---------------------------------------------------------------------------

def gen_line_chart(
    data: list[dict],
    x_key: str,
    series: list[dict],
    title: str = "Line Chart",
    chart_height: int = 140,
) -> str:
    """SVG polyline line chart, supports multiple series.

    Args:
        data:         List of row dicts ordered by X axis.
        x_key:        Column name for the X axis (dates or categories).
        series:       List of series dicts: {"key", "label", "color"}.
        title:        Chart title.
        chart_height: Pixel height of the chart area.

    Returns:
        Self-contained HTML string.
    """
    if not data or not series:
        return "<div style='font-family:Segoe UI;padding:12px;color:#888'>No data</div>"

    PAD_L, PAD_R, PAD_T, PAD_B = 10, 10, 10, 24
    SVG_W    = 340
    SVG_H    = chart_height
    PLOT_W   = SVG_W - PAD_L - PAD_R
    PLOT_H   = SVG_H - PAD_T - PAD_B

    n      = len(data)
    all_vals = [
        float(row.get(s["key"], 0) or 0)
        for row in data for s in series
    ]
    y_max = max(all_vals, default=1) or 1
    y_min = min(all_vals, default=0)
    y_range = (y_max - y_min) or 1

    def px(xi: int, val: float) -> tuple[float, float]:
        fx = PAD_L + (xi / (n - 1)) * PLOT_W if n > 1 else PAD_L + PLOT_W / 2
        fy = PAD_T + PLOT_H - ((val - y_min) / y_range) * PLOT_H
        return round(fx, 2), round(fy, 2)

    lines_svg = ""
    for s in series:
        pts = " ".join(f"{px(i, float(row.get(s['key'], 0) or 0))[0]},{px(i, float(row.get(s['key'], 0) or 0))[1]}" for i, row in enumerate(data))
        lines_svg += (
            f'<polyline points="{pts}" fill="none" stroke="{s["color"]}" '
            f'stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'
        )

    # X-axis tick labels (show first, middle, last)
    ticks_svg = ""
    tick_indices = list(dict.fromkeys([0, n // 2, n - 1])) if n > 1 else [0]
    for ti in tick_indices:
        row = data[ti]
        lbl = str(row.get(x_key, ""))[:10]
        fx, _ = px(ti, y_min)
        ticks_svg += (
            f'<text x="{fx}" y="{SVG_H - 4}" text-anchor="middle" '
            f'font-size="9" fill="#94a3b8">{lbl}</text>'
        )

    legend_html = "".join(
        f'<span class="lc-leg-item"><span class="lc-leg-line" style="background:{s["color"]}"></span>{s["label"]}</span>'
        for s in series
    )

    return f"""<style>
  .lc{{font-family:Segoe UI,sans-serif;padding:12px 16px;width:100%;box-sizing:border-box}}
  .lc-title{{font-size:13px;font-weight:700;color:#1e293b;margin-bottom:6px}}
  .lc-legend{{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:6px}}
  .lc-leg-item{{display:flex;align-items:center;gap:6px;font-size:11px;color:#475569}}
  .lc-leg-line{{width:16px;height:3px;border-radius:2px}}
</style>
<div class="lc">
  <div class="lc-title">{title}</div>
  <div class="lc-legend">{legend_html}</div>
  <svg width="{SVG_W}" height="{SVG_H}" viewBox="0 0 {SVG_W} {SVG_H}" style="overflow:visible">
    <line x1="{PAD_L}" y1="{PAD_T + PLOT_H}" x2="{PAD_L + PLOT_W}" y2="{PAD_T + PLOT_H}"
          stroke="#e2e8f0" stroke-width="1"/>
    {lines_svg}
    {ticks_svg}
  </svg>
</div>"""


# ---------------------------------------------------------------------------
# 7. gen_html_table  –  Styled HTML table
# ---------------------------------------------------------------------------

def gen_html_table(
    data: list[dict],
    columns: list[dict] | None = None,
    title: str = "Table",
    stripe: bool = True,
    max_rows: int = 50,
) -> str:
    """Styled HTML table, compatible with Power BI HTML Content visual.

    Args:
        data:     List of row dicts from execute_dax().
        columns:  Optional list of column descriptors:
                    [{"key": "col_name", "label": "Display Name",
                      "align": "left"|"right"|"center",
                      "prefix": "$", "suffix": "", "decimals": 0}]
                  If None, all keys from the first row are used.
        title:    Table title displayed above.
        stripe:   Alternating row background (zebra striping).
        max_rows: Maximum rows to render (avoids iframe overflow).

    Returns:
        Self-contained HTML string.
    """
    if not data:
        return "<div style='font-family:Segoe UI;padding:12px;color:#888'>No data</div>"

    if columns is None:
        columns = [{"key": k, "label": k, "align": "left"} for k in data[0].keys()]

    header_cells = "".join(
        f'<th style="text-align:{c.get("align","left")}">{c["label"]}</th>'
        for c in columns
    )

    rows_html = ""
    for ri, row in enumerate(data[:max_rows]):
        bg = "#f8fafc" if (stripe and ri % 2 == 0) else "#ffffff"
        cells = ""
        for c in columns:
            raw = row.get(c["key"], "")
            if raw is None:
                raw = ""
            try:
                raw = float(raw)
                txt = _fmt_number(raw, c.get("prefix", ""), c.get("suffix", ""), c.get("decimals", 0))
                align = c.get("align", "right")
            except (TypeError, ValueError):
                txt   = str(raw)
                align = c.get("align", "left")
            cells += f'<td style="text-align:{align}">{txt}</td>'
        rows_html += f'<tr style="background:{bg}">{cells}</tr>'

    return f"""<style>
  .ht{{font-family:Segoe UI,sans-serif;padding:10px 12px;width:100%;box-sizing:border-box}}
  .ht-title{{font-size:13px;font-weight:700;color:#1e293b;margin-bottom:8px}}
  .ht table{{width:100%;border-collapse:collapse;font-size:12px}}
  .ht th{{background:#1e293b;color:#f8fafc;padding:7px 10px;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.04em}}
  .ht td{{padding:6px 10px;color:#334155;border-bottom:1px solid #f1f5f9}}
  .ht tr:last-child td{{border-bottom:none}}
</style>
<div class="ht">
  <div class="ht-title">{title}</div>
  <table>
    <thead><tr>{header_cells}</tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>"""
