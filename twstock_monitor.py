import os
import sys
import json
import time
import datetime
import twstock

# Force UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Windows beep support
try:
    import winsound
    def beep_alert():
        winsound.Beep(1000, 500)
except ImportError:
    def beep_alert():
        print("\a", end="", flush=True)

# ANSI color codes
RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
RESET  = "\033[0m"

DEFAULT_CONFIG = {
    "interval": 5,
    "stocks": [
        {"id": "2330", "name": "台積電", "upper": 1000, "lower": 900}
    ]
}

def load_config(path="config.json"):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        print(f"已建立預設設定檔 {path}，請編輯後重新執行。")
        sys.exit(0)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def fetch_price(stock_id):
    try:
        info = twstock.realtime.get(stock_id)
        if not info or not info.get("success"):
            return None
        rt = info["realtime"]
        return {
            "price":  float(rt["latest_trade_price"]) if rt["latest_trade_price"] else None,
            "open":   float(rt["open"])  if rt["open"]  else None,
            "high":   float(rt["high"])  if rt["high"]  else None,
            "low":    float(rt["low"])   if rt["low"]   else None,
            "volume": rt["accumulate_trade_volume"],
            "time":   info["info"]["time"],
        }
    except Exception:
        return None

def check_alert(stock, price):
    if price is None:
        return []
    alerts = []
    upper = stock.get("upper")
    lower = stock.get("lower")
    if upper and price >= upper:
        alerts.append(("red", f"⚠ 已達上限 {upper}!"))
    elif upper and price >= upper * 0.9:
        alerts.append(("yellow", f"▲ 接近上限 {upper}"))
    if lower and price <= lower:
        alerts.append(("red", f"⚠ 已達下限 {lower}!"))
    elif lower and price <= lower * 1.1:
        alerts.append(("yellow", f"▼ 接近下限 {lower}"))
    return alerts

def render_table(stocks, results):
    os.system("cls" if os.name == "nt" else "clear")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "=" * 72
    print(line)
    print(f"  台股即時報價監控  |  更新時間: {now}  |  按 Ctrl+C 結束")
    print(line)
    header = f"{'代號':<6} {'名稱':<8} {'現價':>8} {'開盤':>8} {'最高':>8} {'最低':>8} {'成交量':>10}  狀態"
    print(header)
    print("-" * 72)

    has_alert = False
    for stock, data in zip(stocks, results):
        sid   = stock["id"]
        name  = stock.get("name", sid)
        if data is None:
            row = f"{sid:<6} {name:<8} {'--':>8} {'--':>8} {'--':>8} {'--':>8} {'--':>10}  無法取得"
            print(f"{YELLOW}{row}{RESET}")
            continue

        price  = data["price"]
        open_  = data["open"]
        high   = data["high"]
        low    = data["low"]
        volume = data["volume"]

        alerts = check_alert(stock, price)
        if any(a[0] == "red" for a in alerts):
            has_alert = True
            color = RED
        elif alerts:
            color = YELLOW
        else:
            color = GREEN

        status = "  ".join(a[1] for a in alerts) if alerts else "✓"

        price_str  = f"{price:.1f}"  if price  is not None else "--"
        open_str   = f"{open_:.1f}" if open_  is not None else "--"
        high_str   = f"{high:.1f}"  if high   is not None else "--"
        low_str    = f"{low:.1f}"   if low    is not None else "--"

        row = f"{sid:<6} {name:<8} {price_str:>8} {open_str:>8} {high_str:>8} {low_str:>8} {volume:>10}  {status}"
        print(f"{color}{row}{RESET}")

    print(line)
    if has_alert:
        beep_alert()

def main():
    config = load_config()
    stocks   = config["stocks"]
    interval = config.get("interval", 5)

    print("載入設定完成，開始監控...")
    time.sleep(1)

    try:
        while True:
            results = [fetch_price(s["id"]) for s in stocks]
            render_table(stocks, results)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n監控已停止。")

if __name__ == "__main__":
    main()
