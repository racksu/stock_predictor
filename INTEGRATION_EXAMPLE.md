# 回測系統整合範例

## 概述

回測系統已完全整合到你的股票預測系統中!現在你可以:
1. ✅ 透過 Web API 執行回測
2. ✅ 驗證預測策略的實際表現
3. ✅ 自動優化停損停利參數
4. ✅ 在實際交易前建立信心

## 快速開始

### 步驟 1: 啟動 Web 伺服器

```bash
cd "C:\Users\rack\Desktop\台股預測系統"
python web_server_enhanced_v3.1.py
```

你應該會看到:
```
╔════════════════════════════════════════════════════════════════╗
║          多市場智能選股系統 v4.1 Enhanced                    ║
║          Multi-Market Stock Picker Web Server                ║
╚════════════════════════════════════════════════════════════════╝

✅ 基礎模組載入成功
✅ 增強版模組載入成功
✅ 回測模組載入成功  <-- 這個很重要!

🌐 Web 介面: http://localhost:5000

📡 API 端點：
...
✅ POST /api/backtest            - 執行回測 (NEW!)
✅ POST /api/backtest_compare    - 參數比較回測 (NEW!)
```

### 步驟 2: 執行你的第一個回測

開啟新的命令視窗,執行測試腳本:

```bash
python test_backtest_api.py
```

按照提示輸入股票代碼 (例如: 2330),系統會自動執行回測並顯示結果。

## 使用場景

### 場景 1: 驗證單一股票策略

**情境**: 你想買台積電 (2330),想知道這個策略過去的表現如何

**做法**:

```python
import requests

# 執行回測
response = requests.post('http://localhost:5000/api/backtest', json={
    'symbol': '2330',
    'initial_capital': 1000000,
    'position_size': 0.3,      # 每次買30%倉位
    'stop_loss': -0.08,        # -8% 停損
    'take_profit': 0.15,       # +15% 停利
    'strategy': 'enhanced'     # 使用你的增強版策略
})

data = response.json()
if data['success']:
    results = data['data']
    print(f"歷史總報酬: {results['results']['total_return_pct']:+.2f}%")
    print(f"勝率: {results['metrics']['win_rate']*100:.1f}%")
    print(f"最大回撤: {results['metrics']['max_drawdown']*100:.1f}%")
```

**輸出範例**:
```
歷史總報酬: +15.6%
勝率: 75.0%
最大回撤: 12.5%
```

**結論**: 如果歷史表現良好,你對這個策略會更有信心!

---

### 場景 2: 優化停損停利參數

**情境**: 你不確定該設多少停損和停利,想找出最佳參數

**做法**:

```python
import requests

# 比較3組不同的參數
response = requests.post('http://localhost:5000/api/backtest_compare', json={
    'symbol': '2330',
    'param_sets': [
        # 保守型: 小倉位,快停損停利
        {'position_size': 0.2, 'stop_loss': -0.05, 'take_profit': 0.10},

        # 平衡型: 中等設定
        {'position_size': 0.3, 'stop_loss': -0.08, 'take_profit': 0.15},

        # 積極型: 大倉位,寬停損停利
        {'position_size': 0.5, 'stop_loss': -0.10, 'take_profit': 0.20},
    ]
})

data = response.json()
if data['success']:
    # 顯示比較結果
    print("參數比較結果:")
    for i, result in enumerate(data['data']['results'], 1):
        params = result['parameters']
        print(f"\n方案 {i}:")
        print(f"  倉位: {params['position_size']*100:.0f}%")
        print(f"  停損: {params['stop_loss']*100:.0f}%")
        print(f"  停利: {params['take_profit']*100:.0f}%")
        print(f"  報酬率: {result['total_return']*100:+.2f}%")
        print(f"  Sharpe比率: {result['sharpe_ratio']:.2f}")

    # 顯示最佳參數
    best = data['data']['best_parameters']
    print(f"\n🏆 最佳參數 (根據Sharpe比率):")
    print(f"  倉位: {best['position_size']*100:.0f}%")
    print(f"  停損: {best['stop_loss']*100:.0f}%")
    print(f"  停利: {best['take_profit']*100:.0f}%")
```

**輸出範例**:
```
參數比較結果:

方案 1:
  倉位: 20%
  停損: -5%
  停利: 10%
  報酬率: +8.9%
  Sharpe比率: 1.45

方案 2:
  倉位: 30%
  停損: -8%
  停利: 15%
  報酬率: +15.6%
  Sharpe比率: 1.85

方案 3:
  倉位: 50%
  停損: -10%
  停利: 20%
  報酬率: +18.2%
  Sharpe比率: 1.32

🏆 最佳參數 (根據Sharpe比率):
  倉位: 30%
  停損: -8%
  停利: 15%
```

**結論**: 方案2的風險調整後報酬最好,是最佳選擇!

---

### 場景 3: 批量測試多支股票

**情境**: 你的篩選系統找到10支潛力股,想知道哪支歷史表現最好

**做法**:

```python
import requests

# 潛力股列表
symbols = ['2330', '2317', '2454', '3008', '2308']

results_summary = []

for symbol in symbols:
    print(f"回測 {symbol}...")

    # 執行回測
    response = requests.post('http://localhost:5000/api/backtest', json={
        'symbol': symbol,
        'initial_capital': 1000000,
        'position_size': 0.3,
        'stop_loss': -0.08,
        'take_profit': 0.15
    })

    if response.json()['success']:
        data = response.json()['data']
        results_summary.append({
            'symbol': symbol,
            'total_return': data['results']['total_return_pct'],
            'win_rate': data['metrics']['win_rate'],
            'sharpe': data['metrics']['sharpe_ratio'],
            'max_drawdown': data['metrics']['max_drawdown']
        })

# 依報酬率排序
results_summary.sort(key=lambda x: x['total_return'], reverse=True)

# 顯示排名
print("\n回測結果排名:")
print(f"{'排名':<6} {'代碼':<8} {'報酬率':<12} {'勝率':<10} {'Sharpe':<10} {'回撤':<10}")
print("-" * 60)

for i, result in enumerate(results_summary, 1):
    print(f"{i:<6} {result['symbol']:<8} "
          f"{result['total_return']:>+10.2f}% "
          f"{result['win_rate']*100:>8.1f}% "
          f"{result['sharpe']:>8.2f} "
          f"{result['max_drawdown']*100:>8.1f}%")
```

**輸出範例**:
```
回測 2330...
回測 2317...
回測 2454...
回測 3008...
回測 2308...

回測結果排名:
排名   代碼     報酬率        勝率       Sharpe     回撤
------------------------------------------------------------
1      2454        +22.5%      82.0%      2.15      8.5%
2      2330        +15.6%      75.0%      1.85     12.5%
3      2317        +12.3%      71.4%      1.62     10.2%
4      3008         +8.9%      66.7%      1.28     15.3%
5      2308         +4.2%      58.3%      0.85     18.7%
```

**結論**: 2454 表現最好,是首選!

---

## 實際工作流程建議

### 完整的策略驗證流程

1. **步驟 1: 選股**
   - 使用你的篩選系統找出潛力股
   - 或者手動輸入感興趣的股票

2. **步驟 2: 預測分析**
   - 執行 `/api/analyze` 或 `/api/analyze_enhanced`
   - 獲得技術評分和買入建議

3. **步驟 3: 回測驗證** ⬅️ 新增!
   - 執行 `/api/backtest` 查看歷史表現
   - 確認策略在過去是否有效

4. **步驟 4: 參數優化** ⬅️ 新增!
   - 執行 `/api/backtest_compare`
   - 找出最佳的停損停利設定

5. **步驟 5: 決策**
   - 如果預測+回測都良好 → 考慮進場
   - 如果有一個表現不好 → 觀望或尋找其他標的

6. **步驟 6: 執行交易**
   - 使用回測找出的最佳參數
   - 嚴格執行停損停利

### 決策矩陣

| 預測評分 | 回測報酬 | 回測勝率 | 建議 |
|---------|---------|---------|------|
| 高 (>70) | 正 (>10%) | 高 (>70%) | 🟢 強力買入 |
| 高 (>70) | 正 (>10%) | 中 (50-70%) | 🟡 謹慎買入 |
| 高 (>70) | 負或低 | 低 (<50%) | 🔴 觀望 |
| 中 (50-70) | 正 (>15%) | 高 (>75%) | 🟡 可考慮 |
| 低 (<50) | - | - | 🔴 不建議 |

## 進階應用

### 1. 定期回測

定期回測你的持倉,確保策略仍然有效:

```python
# 每週執行一次
holdings = ['2330', '2454', '2317']

for symbol in holdings:
    response = requests.post('http://localhost:5000/api/backtest', json={
        'symbol': symbol,
        'initial_capital': 1000000,
        'position_size': 0.3,
        'stop_loss': -0.08,
        'take_profit': 0.15
    })

    # 如果表現轉差,考慮調整或出場
    data = response.json()['data']
    if data['metrics']['sharpe_ratio'] < 1.0:
        print(f"⚠️ {symbol} 表現轉差,建議檢查")
```

### 2. 回測報告自動化

將回測結果自動保存為報告:

```python
import json
from datetime import datetime

# 執行回測
response = requests.post('http://localhost:5000/api/backtest', json={
    'symbol': '2330',
    'initial_capital': 1000000,
    'position_size': 0.3,
    'stop_loss': -0.08,
    'take_profit': 0.15
})

# 保存完整結果
if response.json()['success']:
    filename = f"backtest_2330_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(response.json()['data'], f, indent=2, ensure_ascii=False)

    print(f"回測報告已保存: {filename}")
```

### 3. 整合到交易日誌

記錄每次交易的回測結果,追蹤策略表現:

```python
trade_log = {
    'date': '2025-11-24',
    'symbol': '2330',
    'action': 'BUY',
    'price': 580,
    'backtest_return': 15.6,
    'backtest_winrate': 75.0,
    'backtest_sharpe': 1.85,
    'confidence': 'HIGH'
}

# 保存到CSV或數據庫
```

## 常見問題

### Q: 回測需要多久?
A: 通常5-30秒,取決於數據量。參數比較會需要更長時間。

### Q: 我可以同時回測多支股票嗎?
A: 建議依序執行,避免伺服器負載過高。

### Q: 歷史表現好就代表未來也會好嗎?
A: 不一定!回測只能作為參考,市場環境會改變。建議:
- 結合當前分析
- 控制倉位
- 嚴格停損
- 持續監控

### Q: 如果回測表現不好怎麼辦?
A:
1. 檢查是否有足夠的歷史數據
2. 嘗試調整參數
3. 考慮換其他標的
4. 最重要: **不要強行交易表現不好的標的!**

## 總結

回測系統已經完全整合到你的預測系統中,提供了:

✅ **驗證**: 確認策略實際有效
✅ **優化**: 找出最佳參數設定
✅ **信心**: 基於數據的決策
✅ **風控**: 了解最大風險

記住: **好的策略 = 良好的預測 + 經過驗證的回測結果**

開始使用回測系統,讓你的交易決策更有依據! 🚀📈

---

**需要幫助?**
- API 文檔: [API_BACKTEST_GUIDE.md](API_BACKTEST_GUIDE.md)
- 回測詳細說明: [BACKTESTING_README.md](BACKTESTING_README.md)
- 測試 API: `python test_backtest_api.py`
