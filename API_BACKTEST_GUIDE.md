# 回測 API 使用指南

## 概述

回測系統已整合到 Web 伺服器中,可透過 RESTful API 使用。

## API 端點

### 1. 執行回測

**端點**: `POST /api/backtest`

**功能**: 對單一股票執行完整的歷史回測

**請求範例**:

```bash
curl -X POST http://localhost:5000/api/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "2330",
    "initial_capital": 1000000,
    "position_size": 0.3,
    "stop_loss": -0.08,
    "take_profit": 0.15,
    "rebalance_days": 5,
    "strategy": "enhanced"
  }'
```

**參數說明**:

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `symbol` | string | 必填 | 股票代碼 (如: 2330) |
| `initial_capital` | number | 1000000 | 初始資金 |
| `position_size` | number | 0.3 | 單次倉位比例 (0.0-1.0) |
| `stop_loss` | number | -0.08 | 停損比例 (負數, 如 -0.08 = -8%) |
| `take_profit` | number | 0.15 | 停利比例 (正數, 如 0.15 = 15%) |
| `rebalance_days` | number | 5 | 重新評估天數 |
| `strategy` | string | "enhanced" | 策略類型: "basic" 或 "enhanced" |

**回應範例**:

```json
{
  "success": true,
  "message": "回測完成",
  "timestamp": "2025-11-24T...",
  "data": {
    "symbol": "2330",
    "strategy": "enhanced",
    "parameters": {
      "initial_capital": 1000000,
      "position_size": 0.3,
      "stop_loss": -0.08,
      "take_profit": 0.15,
      "rebalance_days": 5
    },
    "results": {
      "initial_capital": 1000000,
      "final_equity": 1156000,
      "total_return": 0.156,
      "total_return_pct": 15.6
    },
    "metrics": {
      "total_trades": 12,
      "winning_trades": 9,
      "losing_trades": 3,
      "win_rate": 0.75,
      "avg_profit": 13000,
      "avg_profit_pct": 0.065,
      "max_profit": 45000,
      "max_loss": -18000,
      "profit_factor": 3.0,
      "sharpe_ratio": 1.85,
      "max_drawdown": 0.125,
      "avg_holding_days": 18.5
    },
    "trades": [
      {
        "entry_date": "2024-01-15",
        "exit_date": "2024-02-03",
        "entry_price": 450.0,
        "exit_price": 485.0,
        "shares": 2000,
        "profit": 70000,
        "profit_pct": 0.0778,
        "days_held": 19,
        "exit_reason": "停利 (+7.78%)"
      }
    ],
    "equity_curve": [
      {
        "date": "2024-01-15",
        "equity": 1000000,
        "capital": 1000000,
        "position_value": 0
      }
    ],
    "data_period": {
      "start": "2023-01-01",
      "end": "2024-12-31",
      "total_days": 500
    }
  }
}
```

### 2. 參數比較回測

**端點**: `POST /api/backtest_compare`

**功能**: 比較多組參數的回測結果,找出最佳參數組合

**請求範例**:

```bash
curl -X POST http://localhost:5000/api/backtest_compare \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "2330",
    "param_sets": [
      {"position_size": 0.2, "stop_loss": -0.05, "take_profit": 0.10},
      {"position_size": 0.3, "stop_loss": -0.08, "take_profit": 0.15},
      {"position_size": 0.5, "stop_loss": -0.10, "take_profit": 0.20}
    ]
  }'
```

**參數說明**:

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `symbol` | string | 必填 | 股票代碼 |
| `param_sets` | array | 預設3組 | 參數組合陣列 |

**回應範例**:

```json
{
  "success": true,
  "message": "參數比較完成",
  "data": {
    "symbol": "2330",
    "results": [
      {
        "parameters": {
          "position_size": 0.2,
          "stop_loss": -0.05,
          "take_profit": 0.10
        },
        "total_return": 0.089,
        "win_rate": 0.68,
        "sharpe_ratio": 1.45,
        "max_drawdown": 0.08,
        "total_trades": 15
      },
      {
        "parameters": {
          "position_size": 0.3,
          "stop_loss": -0.08,
          "take_profit": 0.15
        },
        "total_return": 0.156,
        "win_rate": 0.75,
        "sharpe_ratio": 1.85,
        "max_drawdown": 0.125,
        "total_trades": 12
      }
    ],
    "best_parameters": {
      "position_size": 0.3,
      "stop_loss": -0.08,
      "take_profit": 0.15
    }
  }
}
```

## Python 範例

### 基本回測

```python
import requests

# 執行回測
response = requests.post('http://localhost:5000/api/backtest', json={
    'symbol': '2330',
    'initial_capital': 1000000,
    'position_size': 0.3,
    'stop_loss': -0.08,
    'take_profit': 0.15
})

data = response.json()

if data['success']:
    results = data['data']['results']
    metrics = data['data']['metrics']

    print(f"總報酬: {results['total_return_pct']:.2f}%")
    print(f"勝率: {metrics['win_rate']*100:.1f}%")
    print(f"Sharpe比率: {metrics['sharpe_ratio']:.2f}")
else:
    print(f"錯誤: {data['message']}")
```

### 參數優化

```python
import requests

# 比較不同參數
response = requests.post('http://localhost:5000/api/backtest_compare', json={
    'symbol': '2330',
    'param_sets': [
        {'position_size': 0.2, 'stop_loss': -0.05, 'take_profit': 0.10},
        {'position_size': 0.3, 'stop_loss': -0.08, 'take_profit': 0.15},
        {'position_size': 0.5, 'stop_loss': -0.10, 'take_profit': 0.20},
    ]
})

data = response.json()

if data['success']:
    # 顯示比較結果
    for result in data['data']['results']:
        params = result['parameters']
        print(f"倉位 {params['position_size']*100:.0f}%, "
              f"報酬 {result['total_return']*100:+.2f}%, "
              f"Sharpe {result['sharpe_ratio']:.2f}")

    # 顯示最佳參數
    best = data['data']['best_parameters']
    print(f"\n最佳參數: 倉位 {best['position_size']*100:.0f}%, "
          f"停損 {best['stop_loss']*100:.0f}%, "
          f"停利 {best['take_profit']*100:.0f}%")
```

## JavaScript 範例

### 基本回測

```javascript
async function runBacktest(symbol) {
    const response = await fetch('http://localhost:5000/api/backtest', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            symbol: symbol,
            initial_capital: 1000000,
            position_size: 0.3,
            stop_loss: -0.08,
            take_profit: 0.15
        })
    });

    const data = await response.json();

    if (data.success) {
        const { results, metrics } = data.data;
        console.log(`總報酬: ${results.total_return_pct.toFixed(2)}%`);
        console.log(`勝率: ${(metrics.win_rate * 100).toFixed(1)}%`);
        console.log(`Sharpe比率: ${metrics.sharpe_ratio.toFixed(2)}`);

        return data.data;
    } else {
        console.error('回測失敗:', data.message);
        return null;
    }
}

// 使用範例
runBacktest('2330').then(result => {
    if (result) {
        // 處理結果
        displayBacktestResults(result);
    }
});
```

### 參數比較

```javascript
async function compareParameters(symbol, paramSets) {
    const response = await fetch('http://localhost:5000/api/backtest_compare', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            symbol: symbol,
            param_sets: paramSets
        })
    });

    const data = await response.json();

    if (data.success) {
        // 顯示比較結果
        data.data.results.forEach(result => {
            const params = result.parameters;
            console.log(`倉位 ${params.position_size*100}%, ` +
                       `報酬 ${(result.total_return*100).toFixed(2)}%, ` +
                       `Sharpe ${result.sharpe_ratio.toFixed(2)}`);
        });

        // 返回最佳參數
        return data.data.best_parameters;
    } else {
        console.error('參數比較失敗:', data.message);
        return null;
    }
}

// 使用範例
const paramSets = [
    {position_size: 0.2, stop_loss: -0.05, take_profit: 0.10},
    {position_size: 0.3, stop_loss: -0.08, take_profit: 0.15},
    {position_size: 0.5, stop_loss: -0.10, take_profit: 0.20}
];

compareParameters('2330', paramSets).then(bestParams => {
    if (bestParams) {
        console.log('最佳參數:', bestParams);
    }
});
```

## 錯誤處理

### 常見錯誤

| 錯誤訊息 | 原因 | 解決方法 |
|---------|------|---------|
| "回測系統未初始化" | 回測模組載入失敗 | 檢查 backtesting_engine.py 是否存在 |
| "請提供股票代碼" | 缺少必填參數 symbol | 在請求中添加 symbol 參數 |
| "數據不足" | 股票歷史數據少於200筆 | 確認股票已下載足夠數據 |
| "回測失敗" | 執行過程發生錯誤 | 查看伺服器日誌獲取詳細錯誤 |

### 錯誤回應範例

```json
{
  "success": false,
  "message": "數據不足，需要至少200筆交易數據",
  "timestamp": "2025-11-24T..."
}
```

## 注意事項

1. **執行時間**: 回測可能需要數秒到數分鐘,取決於數據量和參數組合數量
2. **數據要求**: 至少需要200筆歷史交易數據才能執行回測
3. **並行限制**: 建議避免同時執行多個回測請求,以免伺服器負載過高
4. **參數範圍**:
   - position_size: 0.1 ~ 1.0 (建議 0.2 ~ 0.5)
   - stop_loss: -0.20 ~ -0.03 (建議 -0.10 ~ -0.05)
   - take_profit: 0.05 ~ 0.30 (建議 0.10 ~ 0.20)

## 測試

使用提供的測試腳本:

```bash
# 確保伺服器正在運行
python web_server_enhanced_v3.1.py

# 在另一個終端執行測試
python test_backtest_api.py
```

## 整合到現有系統

回測 API 可以輕鬆整合到現有的 Web 應用中:

1. **分析頁面**: 在股票分析結果旁添加"執行回測"按鈕
2. **篩選頁面**: 對篩選結果批量執行回測,找出最佳標的
3. **參數優化**: 自動尋找最佳的停損停利參數
4. **策略驗證**: 在實際交易前驗證策略的歷史表現

---

**需要幫助?**
- 查看 [BACKTESTING_README.md](BACKTESTING_README.md) 了解回測系統詳情
- 查看 [backtesting_examples.py](backtesting_examples.py) 了解更多範例
- 執行 `python test_backtest_api.py` 測試 API 功能
