import os
import sys
import json
import time
import datetime
import urllib.request

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

TAIFEX_BASE = "https://openapi.taifex.com.tw/v1"

DEFAULT_CONFIG = {
    "interval": 30,
    "contracts": [
        {"id": "TX",   "name": "台指期",   "upper": 34000, "lower": 32000},
        {"id": "2330", "name": "台積電期", "upper": 1900,  "lower": 1760}
    ]
}

def load_config(path="futures_config.json"):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        print(f"已建立預設設定檔 {path}，請編輯後重新執行。")
        sys.exit(0)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def fetch_json(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def build_ssf_map():
    """Build mapping: stock_code -> futures contract symbol (e.g. '2330' -> 'CDF')"""
    data = fetch_json(f"{TAIFEX_BASE}/SSFLists")
    return {item["StockCode"]: item["Contract"] for item in data}

def fetch_market_data():
    """Fetch all futures daily market report, return dict keyed by contract+month."""
    data = fetch_json(f"{TAIFEX_BASE}/DailyMarketReportFut")
    # Group by contract code, keep only 一般 session, nearest month first
    contracts = {}
    for item in data:
        if item.get("TradingSession") != "一般":
            continue
        code = item["Contract"]
        month = item.get("ContractMonth(Week)", "")
        # Keep the nearest (smallest) month per contract
        if code not in contracts or month < contracts[code]["month"]:
            contracts[code] = {
                "month":  month,
                "price":  item.get("Last", ""),
                "open":   item.get("Open", ""),
                "high":   item.get("High", ""),
                "low":    item.get("Low", ""),
                "volume": item.get("Volume", ""),
                "bid":    item.get("BestBid", ""),
                "ask":    item.get("BestAsk", ""),
                "change": item.get("Change", ""),
            }
    return contracts

def resolve_contract(contract_id, ssf_map):
    """Return futures contract symbol for a given id.
    - Pure digits (e.g. '2330') -> look up in ssf_map
    - Otherwise (e.g. 'TX') -> use directly
    """
    if contract_id.isdigit():
        return ssf_map.get(contract_id)
    return contract_id

def parse_price(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None

def check_alert(contract, price):
    if price is None:
        return []
    alerts = []
    upper = contract.get("upper")
    lower = contract.get("lower")
    margin = 5 if price >= 1000 else 1
    if upper and price >= upper:
        alerts.append(("red", f"⚠ 已達上限 {upper}!"))
    elif upper and price >= upper - margin:
        alerts.append(("yellow", f"▲ 接近上限 {upper}"))
    if lower and price <= lower:
        alerts.append(("red", f"⚠ 已達下限 {lower}!"))
    elif lower and price <= lower + margin:
        alerts.append(("yellow", f"▼ 接近下限 {lower}"))
    return alerts

def render_table(contracts, ssf_map, market_data):
    os.system("cls" if os.name == "nt" else "clear")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "=" * 80
    print(line)
    print(f"  台灣期貨即時報價監控  |  更新時間: {now}  |  按 Ctrl+C 結束")
    print(line)
    header = f"{'代號':<6} {'名稱':<10} {'現價':>9} {'開盤':>9} {'最高':>9} {'最低':>9} {'漲跌':>7} {'成交量':>8}  狀態"
    print(header)
    print("-" * 80)

    has_alert = False
    for c in contracts:
        cid   = c["id"]
        name  = c.get("name", cid)
        sym   = resolve_contract(cid, ssf_map)

        if sym is None:
            row = f"{cid:<6} {name:<10} {'--':>9} {'--':>9} {'--':>9} {'--':>9} {'--':>7} {'--':>8}  查無期貨代碼"
            print(f"{YELLOW}{row}{RESET}")
            continue

        d = market_data.get(sym)
        if d is None:
            row = f"{cid:<6} {name:<10} {'--':>9} {'--':>9} {'--':>9} {'--':>9} {'--':>7} {'--':>8}  無法取得"
            print(f"{YELLOW}{row}{RESET}")
            continue

        price  = parse_price(d["price"])
        open_  = parse_price(d["open"])
        high   = parse_price(d["high"])
        low    = parse_price(d["low"])
        change = d["change"]
        volume = d["volume"]
        month  = d["month"]

        alerts = check_alert(c, price)
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
        change_str = change if change else "--"

        row = f"{sym:<6} {name:<10} {price_str:>9} {open_str:>9} {high_str:>9} {low_str:>9} {change_str:>7} {volume:>8}  {status}"
        print(f"{color}{row}{RESET}")

    print(line)
    print(f"  ※ 資料為延遲報價（非即時）")
    if has_alert:
        beep_alert()

def main():
    config    = load_config()
    contracts = config["contracts"]
    interval  = config.get("interval", 30)

    print("載入設定，取得期貨代碼對應表...")
    try:
        ssf_map = build_ssf_map()
    except Exception as e:
        print(f"無法取得個股期貨列表：{e}")
        ssf_map = {}

    print(f"共 {len(ssf_map)} 支個股期貨，開始監控...")
    time.sleep(1)

    try:
        while True:
            try:
                market_data = fetch_market_data()
                render_table(contracts, ssf_map, market_data)
            except Exception as e:
                print(f"\n取得資料失敗：{e}，{interval} 秒後重試...")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n監控已停止。")

if __name__ == "__main__":
    main()
