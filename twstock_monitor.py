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

def _parse_float(val):
    """Parse float from TWSE API value; returns None for missing/dash values."""
    if not val or val == "-":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def fetch_prices(stock_ids):
    """Fetch all stock prices in a single API request."""
    try:
        data = twstock.realtime.get(stock_ids)
        if not data or not data.get("success"):
            print(f"\n[警告] 取得股價失敗：rtcode={data.get('rtcode')}, msg={data.get('rtmessage')}", file=sys.stderr)
            return {sid: None for sid in stock_ids}
        results = {}
        for sid in stock_ids:
            info = data.get(sid)
            if not info or not info.get("success"):
                results[sid] = None
                continue
            rt = info["realtime"]
            results[sid] = {
                "price":  _parse_float(rt["latest_trade_price"]),
                "open":   _parse_float(rt["open"]),
                "high":   _parse_float(rt["high"]),
                "low":    _parse_float(rt["low"]),
                "volume": rt["accumulate_trade_volume"],
                "time":   info["info"]["time"],
            }
        return results
    except Exception as e:
        print(f"\n[錯誤] 取得股價例外：{e}", file=sys.stderr)
        return {sid: None for sid in stock_ids}

def check_alert(stock, price):
    if price is None:
        return []
    upper = stock.get("upper")
    lower = stock.get("lower")
    margin = 5 if price >= 1000 else 1
    if upper and price >= upper:
        return [("red", f"⚠ 已達上限 {upper}!")]
    if lower and price <= lower:
        return [("red", f"⚠ 已達下限 {lower}!")]
    if upper and price >= upper - margin:
        return [("yellow", f"▲ 接近上限 {upper}")]
    if lower and price <= lower + margin:
        return [("yellow", f"▼ 接近下限 {lower}")]
    return []

def cjk_len(s):
    return sum(2 if ord(c) > 127 else 1 for c in s)

def ljust_cjk(s, width):
    return s + ' ' * max(width - cjk_len(s), 0)

def rjust_cjk(s, width):
    return ' ' * max(width - cjk_len(s), 0) + s

def render_table(stocks, results):
    os.system("cls" if os.name == "nt" else "clear")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "=" * 65
    print(line)
    print(f"  台股即時報價監控  |  更新時間: {now}  |  按 Ctrl+C 結束")
    print(line)
    header = (f"{ljust_cjk('代號', 6)} {ljust_cjk('名稱', 6)}"
              f" {rjust_cjk('現價', 8)} {rjust_cjk('開盤', 8)}"
              f" {rjust_cjk('最高', 8)} {rjust_cjk('最低', 8)}"
              f" {rjust_cjk('成交量', 8)}  狀態")
    print(header)
    print("-" * 65)

    has_alert = False
    for stock, data in zip(stocks, results):
        sid   = stock["id"]
        name  = stock.get("name", sid)
        if data is None:
            row = (f"{sid:<6} {ljust_cjk(name, 6)}"
                   f" {'--':>8} {'--':>8} {'--':>8} {'--':>8} {'--':>8}  無法取得")
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

        stale = data.get("stale", False)
        price_str = (f"~{price:.1f}" if stale else f"{price:.1f}") if price is not None else "--"
        open_str  = f"{open_:.1f}" if open_ is not None else "--"
        high_str  = f"{high:.1f}"  if high  is not None else "--"
        low_str   = f"{low:.1f}"   if low   is not None else "--"

        row = (f"{sid:<6} {ljust_cjk(name, 6)}"
               f" {price_str:>8} {open_str:>8} {high_str:>8} {low_str:>8} {volume:>8}  {status}")
        print(f"{color}{row}{RESET}")

    print(line)
    if has_alert:
        beep_alert()

def main():
    config = load_config()
    stocks   = config["stocks"]
    interval = config.get("interval", 5)
    last_prices = {}  # sid → 上次成交價

    print("載入設定完成，開始監控...")
    time.sleep(1)

    try:
        while True:
            stock_ids = [s["id"] for s in stocks]
            price_map = fetch_prices(stock_ids)
            results = []
            for sid in stock_ids:
                data = price_map.get(sid)
                if data is not None:
                    if data["price"] is not None:
                        last_prices[sid] = data["price"]
                    elif sid in last_prices:
                        data = {**data, "price": last_prices[sid], "stale": True}
                results.append(data)
            render_table(stocks, results)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n監控已停止。")

if __name__ == "__main__":
    main()
