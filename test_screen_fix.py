"""
測試智能篩選功能修復
"""

import requests

API_BASE = 'http://localhost:5000/api'

print("="*80)
print("測試智能篩選功能")
print("="*80)

# 1. 檢查本地股票
print("\n【1】檢查本地股票")
try:
    response = requests.get(f'{API_BASE}/local-stocks', timeout=10)
    data = response.json()

    if data['success']:
        stocks_data = data['data']
        print(f"✅ 本地股票總數: {stocks_data['total']}")
        print(f"   美股: {stocks_data['us_count']} 支")
        print(f"   台股: {stocks_data['tw_count']} 支")

        if stocks_data['total'] == 0:
            print("\n❌ 本地沒有股票數據！")
            print("請先下載一些股票，例如：")
            print("  - 在前端下載頁面輸入 AAPL,MSFT,TSLA")
            print("  - 或輸入 2330,2317,2454")
            exit(1)
    else:
        print(f"❌ {data['message']}")
        exit(1)

except Exception as e:
    print(f"❌ 錯誤: {e}")
    exit(1)

# 2. 測試智能篩選（全部市場）
print("\n【2】測試智能篩選 - 全部市場")
try:
    response = requests.post(
        f'{API_BASE}/screen',
        json={
            'market': 'all',
            'min_score': 30,
            'min_expected_return': 0,
            'min_risk_reward': 0,
            'action_filter': 'all'
        },
        headers={'Content-Type': 'application/json'},
        timeout=300  # 篩選可能需要較長時間
    )

    print(f"狀態碼: {response.status_code}")
    data = response.json()

    if data['success']:
        results = data['data']['results']
        print(f"\n✅ {data['message']}")
        print(f"\n前 5 名結果:")
        print("-"*80)

        for i, stock in enumerate(results[:5], 1):
            print(f"{i}. {stock['symbol']}")
            print(f"   評分: {stock['score']:.1f}/100")
            print(f"   信號: {stock['signal']}")
            print(f"   預期報酬: {stock['expected_return']*100:+.2f}%")
            print(f"   風險報酬比: {stock['risk_reward_ratio']:.2f}")
            print(f"   風險等級: {stock['risk_level']}")
            print()
    else:
        print(f"❌ {data['message']}")

except Exception as e:
    print(f"❌ 錯誤: {e}")

# 3. 測試智能篩選（僅美股）
print("\n【3】測試智能篩選 - 僅美股，評分 > 60")
try:
    response = requests.post(
        f'{API_BASE}/screen',
        json={
            'market': 'US',
            'min_score': 60,
            'min_expected_return': 0.05,  # 5%
            'min_risk_reward': 1.0,
            'action_filter': 'all'
        },
        headers={'Content-Type': 'application/json'},
        timeout=300
    )

    data = response.json()

    if data['success']:
        results = data['data']['results']
        print(f"✅ {data['message']}")

        if results:
            print(f"\n符合條件的美股:")
            for stock in results:
                print(f"  • {stock['symbol']}: {stock['score']:.1f}分, {stock['signal']}")
    else:
        print(f"⚠️ {data['message']}")

except Exception as e:
    print(f"❌ 錯誤: {e}")

# 4. 測試智能篩選（僅台股）
print("\n【4】測試智能篩選 - 僅台股")
try:
    response = requests.post(
        f'{API_BASE}/screen',
        json={
            'market': 'TW',
            'min_score': 40,
            'min_expected_return': 0,
            'min_risk_reward': 0,
            'action_filter': 'all'
        },
        headers={'Content-Type': 'application/json'},
        timeout=300
    )

    data = response.json()

    if data['success']:
        results = data['data']['results']
        print(f"✅ {data['message']}")

        if results:
            print(f"\n符合條件的台股:")
            for stock in results:
                print(f"  • {stock['symbol']}: {stock['score']:.1f}分, {stock['signal']}")
    else:
        print(f"⚠️ {data['message']}")

except Exception as e:
    print(f"❌ 錯誤: {e}")

print("\n" + "="*80)
print("測試完成")
print("="*80)
