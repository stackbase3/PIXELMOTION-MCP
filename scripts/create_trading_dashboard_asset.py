"""
Generates a realistic, pixel-perfect 1920x1080 Trading Journal Dashboard reference asset.
"""

import os
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def generate_trading_dashboard(output_path: str):
    width, height = 1920, 1080
    img = Image.new("RGBA", (width, height), (11, 14, 20, 255))
    draw = ImageDraw.Draw(img)

    # 1. Top Navigation Bar (0, 0, 1920, 64)
    draw.rectangle([0, 0, width, 64], fill=(15, 19, 29, 255), outline=(37, 49, 76, 255), width=1)
    # Brand
    draw.rectangle([24, 18, 52, 46], fill=(56, 189, 248, 255))
    draw.text((64, 22), "EDGEFLOW", fill=(255, 255, 255, 255))
    draw.text((150, 24), "TRADING JOURNAL", fill=(148, 163, 184, 255))
    # Account Badge
    draw.rounded_rectangle([320, 16, 560, 48], radius=6, fill=(22, 28, 42, 255), outline=(56, 189, 248, 120), width=1)
    draw.text((336, 24), "Live Futures: $124,500.00", fill=(56, 189, 248, 255))
    # Date Filter Button
    draw.rounded_rectangle([1580, 16, 1720, 48], radius=6, fill=(22, 28, 42, 255), outline=(51, 65, 85, 255), width=1)
    draw.text((1600, 24), "Last 30 Days", fill=(226, 232, 240, 255))
    # Primary CTA Button (Target for cursor walkthrough)
    draw.rounded_rectangle([1740, 16, 1890, 48], radius=6, fill=(56, 189, 248, 255))
    draw.text((1770, 24), "+ Log Trade", fill=(15, 23, 42, 255))

    # 2. Left Sidebar (0, 64, 220, 1080)
    draw.rectangle([0, 64, 220, height], fill=(15, 19, 29, 255), outline=(37, 49, 76, 255), width=1)
    tabs = ["Overview", "Trade Log", "Edge Analytics", "Equity Curve", "Risk Matrix", "Settings"]
    for i, tab in enumerate(tabs):
        ty = 88 + (i * 48)
        is_active = (i == 0)
        if is_active:
            draw.rounded_rectangle([12, ty, 208, ty + 38], radius=6, fill=(56, 189, 248, 30), outline=(56, 189, 248, 180), width=1)
            draw.text((28, ty + 10), tab, fill=(56, 189, 248, 255))
        else:
            draw.text((28, ty + 10), tab, fill=(148, 163, 184, 255))

    # 3. KPI Metric Cards (top row: 244 to 1890, y: 84 to 194)
    kpis = [
        ("Net Cumulative P&L", "+$28,450.00", "+22.8% this month", (16, 185, 129, 255)),
        ("Win Rate", "68.4%", "41 Winners / 19 Losers", (56, 189, 248, 255)),
        ("Profit Factor", "2.84", "Gross Win/Loss Ratio", (16, 185, 129, 255)),
        ("Expectancy", "+1.82 R", "Avg Trade Value", (245, 158, 11, 255))
    ]
    card_w = 394
    for idx, (label, val, sub, col) in enumerate(kpis):
        cx = 244 + (idx * (card_w + 16))
        cy = 84
        draw.rounded_rectangle([cx, cy, cx + card_w, cy + 110], radius=8, fill=(22, 28, 42, 255), outline=(37, 49, 76, 255), width=1)
        draw.text((cx + 18, cy + 16), label.upper(), fill=(148, 163, 184, 255))
        draw.text((cx + 18, cy + 42), val, fill=(255, 255, 255, 255))
        draw.text((cx + 18, cy + 80), sub, fill=col)

    # 4. Main Equity Curve Panel (Left center: 244, 214, width 1080, height 420)
    chart_x, chart_y, chart_w, chart_h = 244, 214, 1080, 420
    draw.rounded_rectangle([chart_x, chart_y, chart_x + chart_w, chart_y + chart_h], radius=8, fill=(22, 28, 42, 255), outline=(37, 49, 76, 255), width=1)
    draw.text((chart_x + 20, chart_y + 18), "EQUITY ACCUMULATION CURVE", fill=(255, 255, 255, 255))
    draw.text((chart_x + 20, chart_y + 40), "Real-time mark-to-market performance", fill=(148, 163, 184, 255))

    # Draw grid lines & equity curve path
    for gy in range(chart_y + 80, chart_y + chart_h - 40, 60):
        draw.line([chart_x + 20, gy, chart_x + chart_w - 20, gy], fill=(30, 41, 59, 255), width=1)

    # Simulated upward trending equity points
    points = []
    np.random.seed(42)
    cy_val = chart_y + chart_h - 70
    points.append((chart_x + 30, cy_val))
    step_x = (chart_w - 60) / 25
    for i in range(1, 26):
        px = chart_x + 30 + (i * step_x)
        delta_y = np.random.normal(loc=-10, scale=8)
        cy_val = max(chart_y + 80, min(chart_y + chart_h - 60, cy_val + delta_y))
        points.append((px, cy_val))

    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=(16, 185, 129, 255), width=3)
    # Area highlight
    for p in points[::3]:
        draw.ellipse([p[0]-4, p[1]-4, p[0]+4, p[1]+4], fill=(56, 189, 248, 255))

    # 5. Right Feature Card: Setup Win Rates (1344, 214, width 546, height 420)
    setup_x, setup_y, setup_w, setup_h = 1344, 214, 546, 420
    draw.rounded_rectangle([setup_x, setup_y, setup_x + setup_w, setup_y + setup_h], radius=8, fill=(22, 28, 42, 255), outline=(37, 49, 76, 255), width=1)
    draw.text((setup_x + 20, setup_y + 18), "SETUP ALPHA DISTRIBUTION", fill=(255, 255, 255, 255))
    setups = [
        ("Opening Range Breakout", "74.2%", "+$14,200", 0.74),
        ("Liquidity Sweep Reversal", "68.8%", "+$8,950", 0.68),
        ("VWAP Trend Continuation", "62.5%", "+$4,100", 0.62),
        ("Mean Reversion Fade", "55.0%", "+$1,200", 0.55)
    ]
    for i, (name, wr, pnl, ratio) in enumerate(setups):
        sy = setup_y + 70 + (i * 78)
        draw.text((setup_x + 20, sy), name, fill=(226, 232, 240, 255))
        draw.text((setup_x + setup_w - 120, sy), pnl, fill=(16, 185, 129, 255))
        # Progress bar
        bar_bg = [setup_x + 20, sy + 28, setup_x + setup_w - 20, sy + 38]
        draw.rounded_rectangle(bar_bg, radius=4, fill=(30, 41, 59, 255))
        bar_fill = [setup_x + 20, sy + 28, setup_x + 20 + int((setup_w - 40) * ratio), sy + 38]
        draw.rounded_rectangle(bar_fill, radius=4, fill=(56, 189, 248, 255))

    # 6. Bottom Trade Execution Log (244, 654, width 1646, height 390)
    table_x, table_y, table_w, table_h = 244, 654, 1646, 390
    draw.rounded_rectangle([table_x, table_y, table_x + table_w, table_y + table_h], radius=8, fill=(22, 28, 42, 255), outline=(37, 49, 76, 255), width=1)
    draw.text((table_x + 20, table_y + 18), "VERIFIED TRADE EXECUTIONS", fill=(255, 255, 255, 255))

    # Header Row
    headers = [("TIME", 30), ("CONTRACT", 160), ("SIDE", 320), ("ENTRY", 440), ("EXIT", 580), ("RETURN", 720), ("P&L", 880), ("SETUP", 1060)]
    for hname, hx in headers:
        draw.text((table_x + hx, table_y + 54), hname, fill=(148, 163, 184, 255))
    draw.line([table_x + 20, table_y + 80, table_x + table_w - 20, table_y + 80], fill=(37, 49, 76, 255), width=1)

    trades = [
        ("09:34:12", "NQ 100 E-mini", "LONG", "20,412.50", "20,488.25", "+3.2R", "+$1,515.00", "Opening Range Breakout"),
        ("10:15:40", "ES S&P 500", "SHORT", "5,842.25", "5,821.50", "+2.4R", "+$1,037.50", "Liquidity Sweep"),
        ("11:22:04", "CL Crude Oil", "LONG", "70.45", "71.60", "+2.8R", "+$1,150.00", "VWAP Continuation"),
        ("13:45:18", "NQ 100 E-mini", "LONG", "20,450.00", "20,530.00", "+4.0R", "+$1,600.00", "Trend Reversal Breakout"),
        ("15:10:02", "ES S&P 500", "SHORT", "5,835.00", "5,840.50", "-1.0R", "-$275.00", "Failed Breakdown")
    ]
    for idx, (t_time, contract, side, entry, exit_p, r_mult, pnl, setup_name) in enumerate(trades):
        ry = table_y + 96 + (idx * 52)
        draw.text((table_x + 30, ry), t_time, fill=(148, 163, 184, 255))
        draw.text((table_x + 160, ry), contract, fill=(255, 255, 255, 255))
        side_color = (16, 185, 129, 255) if side == "LONG" else (239, 68, 68, 255)
        draw.text((table_x + 320, ry), side, fill=side_color)
        draw.text((table_x + 440, ry), entry, fill=(226, 232, 240, 255))
        draw.text((table_x + 580, ry), exit_p, fill=(226, 232, 240, 255))
        draw.text((table_x + 720, ry), r_mult, fill=side_color)
        draw.text((table_x + 880, ry), pnl, fill=side_color)
        draw.text((table_x + 1060, ry), setup_name, fill=(148, 163, 184, 255))
        draw.line([table_x + 20, ry + 36, table_x + table_w - 20, ry + 36], fill=(22, 28, 42, 255), width=1)

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_p))
    print(f"Generated realistic Trading Journal reference at {out_p.resolve()}")

if __name__ == "__main__":
    out_dir = Path("pixelmotion/data/test_assets")
    generate_trading_dashboard(str(out_dir / "trading_journal_dashboard.png"))
