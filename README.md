# twstock — 台股即時報價監控工具

統一的市場監控框架，即時監控多支台灣股票與期貨報價，並在達到自訂到價時發出警示。

---

## 快速開始

### 安裝依賴

```bash
pip install -r requirements-dev.txt
```

### 啟動監控

```bash
python monitor.py
```

首次執行會自動建立 `monitor_config.json` 設定檔，包含股票與期貨配置。

---

## 系統架構

此專案採用模組化設計，支援多個數據源：

- **TWSE 股票**：台灣證券交易所上市／上櫃股票（twstock 套件）
- **Taifex 期貨**：台灣期貨交易所台指期與個股期貨

詳見 [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 配置

### 設定檔 `monitor_config.json`

統一配置格式包含股票與期貨：

```json
{
  "stocks": [
    {
      "id": "2330",
      "name": "台積電",
      "upper": 1900,
      "lower": 1760,
      "enabled": true
    },
    {
      "id": "2317",
      "name": "鴻海",
      "upper": 200,
      "lower": 150,
      "enabled": true
    }
  ],
  "futures": [
    {
      "id": "TX",
      "name": "台灣指數期貨",
      "upper": 34000,
      "lower": 32000,
      "enabled": true
    },
    {
      "id": "QFF",
      "name": "台積電期貨",
      "upper": 1900,
      "lower": 1760,
      "enabled": true
    }
  ],
  "monitor": {
    "stock_interval": 5,
    "futures_interval": 30,
    "retry_max_attempts": 3,
    "retry_backoff_seconds": 2,
    "beep_enabled": true,
    "log_level": "INFO",
    "log_file": null
  }
}
```

### 股票配置欄位

| 欄位 | 說明 | 必填 |
|------|------|------|
| `id` | 股票代號（台股四位數代號） | ✓ |
| `name` | 自訂顯示名稱 | 選填 |
| `upper` | 到價上限，達到此價格發出警示 | 選填 |
| `lower` | 到價下限，跌到此價格發出警示 | 選填 |
| `enabled` | 是否監控（預設 true） | 選填 |

### 期貨配置欄位

| 欄位 | 說明 | 必填 |
|------|------|------|
| `id` | 期貨合約代碼（如 `TX` 或 `QFF`） | ✓ |
| `name` | 自訂顯示名稱 | 選填 |
| `upper` | 到價上限 | 選填 |
| `lower` | 到價下限 | 選填 |
| `enabled` | 是否監控（預設 true） | 選填 |

**個股期貨代碼對應：**使用 Taifex 期貨合約代碼（如 `2330` 對應 `QFF`）

### 監控設定欄位

| 欄位 | 說明 | 預設值 |
|------|------|--------|
| `stock_interval` | 股票報價刷新間隔（秒） | 5 |
| `futures_interval` | 期貨報價刷新間隔（秒） | 30 |
| `retry_max_attempts` | API 重試次數 | 3 |
| `retry_backoff_seconds` | 重試退避時間（秒） | 2 |
| `beep_enabled` | 到價時發出警示音 | true |
| `log_level` | 日誌等級（DEBUG/INFO/WARNING/ERROR） | INFO |
| `log_file` | 日誌檔案路徑（null 則不記錄到檔案） | null |

詳見 [CONFIG_GUIDE.md](CONFIG_GUIDE.md)

---

## 監控畫面

```
================================================================================
  台灣股票期貨即時報價監控  |  更新時間: 2026-04-18 14:30:00  |  按 Ctrl+C 結束
================================================================================
代號   名稱       現價     開盤     最高     最低   漲跌/成交   狀態
--------------------------------------------------------------------------------
2330   台積電    1830.0  1810.0  1835.0  1805.0      13467  OK
2317   鴻海       199.0   197.0   200.5   196.5      28494  [HIGH] 接近上限 200
TX     台灣指數期 33120   32793   33243   32652   -321 64049  OK
QFF    台積電期  1830    1810    1835    1805      -20 13467  OK
================================================================================
  ※ 資料為延遲報價（非即時）
```

---

## 警示狀態說明

| 狀態 | 顏色 | 說明 |
|------|------|------|
| OK | 綠色 | 價格在正常範圍內 |
| [HIGH] 接近上限 | 黃色 | 現價 ≥ 上限 − margin |
| [LOW] 接近下限 | 黃色 | 現價 ≤ 下限 + margin |
| [UPPER] 已達上限 | 紅色 + 嗶聲 | 現價 ≥ 上限 |
| [LOWER] 已達下限 | 紅色 + 嗶聲 | 現價 ≤ 下限 |

**接近閾值 margin 規則：**

| 股價／期貨價格 | margin |
|--------------|--------|
| ≥ 1000 | 5（即上限 -5 / 下限 +5 觸發黃燈） |
| < 1000 | 1（即上限 -1 / 下限 +1 觸發黃燈） |

---

## 命令列選項

```bash
python monitor.py [OPTIONS]
```

| 選項 | 說明 |
|------|------|
| `--config PATH` | 指定配置檔路徑（預設 `monitor_config.json`） |
| `--verbose` | 詳細日誌輸出（設定為 DEBUG） |
| `--log-file PATH` | 日誌檔案路徑 |
| `--help` | 顯示幫助訊息 |

---

## 結束程式

按 `Ctrl + C` 即可停止監控。

---

## 進階說明

- [架構設計](ARCHITECTURE.md)
- [配置指南](CONFIG_GUIDE.md)
- [外掛開發](PLUGIN_DEVELOPMENT.md)
- [故障排除](TROUBLESHOOTING.md)
- [遷移指南](MIGRATION_GUIDE.md)
