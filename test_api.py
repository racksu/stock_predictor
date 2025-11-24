"""
API 測試腳本
用於測試後端 API 是否正常工作
"""

import requests
import json

API_BASE = 'http://localhost:5000/api'

print("=" * 80)
print("API 測試腳本")
print("請確保 web_server_enhanced_v3.1.py 已經在運行")
print("=" * 80)

# 測試 1: 健康檢查
print("\n【測試 1】健康檢查")
try:
    response = requests.get(f'{API_BASE}/health', timeout=5)
    print(f"狀態碼: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 服務器運行正常")
        print(f"核心模組: {data['data']['features']}")
    else:
        print(f"❌ 服務器響應異常")
except requests.exceptions.ConnectionError:
    print("❌ 無法連接到服務器")
    print("請先運行: python web_server_enhanced_v3.1.py")
    exit(1)
except Exception as e:
    print(f"❌ 錯誤: {e}")
    exit(1)

# 測試 2: 下載單支美股
print("\n【測試 2】下載單支美股 (AAPL)")
try:
    payload = {
        'method': 'single',
        'symbol': 'AAPL',
        'period': '5d'
    }
    response = requests.post(
        f'{API_BASE}/download',
        json=payload,
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    print(f"狀態碼: {response.status_code}")
    data = response.json()

    if data['success']:
        print(f"✅ {data['message']}")
        if 'data' in data and data['data']:
            print(f"   數據詳情:")
            for key, value in data['data'].items():
                print(f"   - {key}: {value}")
    else:
        print(f"❌ {data['message']}")
except Exception as e:
    print(f"❌ 錯誤: {e}")
    import traceback
    traceback.print_exc()

# 測試 3: 下載單支台股
print("\n【測試 3】下載單支台股 (2330)")
try:
    payload = {
        'method': 'single',
        'symbol': '2330',
        'period': '5d'
    }
    response = requests.post(
        f'{API_BASE}/download',
        json=payload,
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    print(f"狀態碼: {response.status_code}")
    data = response.json()

    if data['success']:
        print(f"✅ {data['message']}")
        if 'data' in data and data['data']:
            print(f"   數據詳情:")
            for key, value in data['data'].items():
                print(f"   - {key}: {value}")
    else:
        print(f"❌ {data['message']}")
except Exception as e:
    print(f"❌ 錯誤: {e}")
    import traceback
    traceback.print_exc()

# 測試 4: 查看本地股票
print("\n【測試 4】查看本地股票列表")
try:
    response = requests.get(f'{API_BASE}/local-stocks', timeout=10)
    print(f"狀態碼: {response.status_code}")
    data = response.json()

    if data['success']:
        print(f"✅ {data['message']}")
        if 'data' in data and data['data']:
            print(f"   總計: {data['data']['total']} 支")
            print(f"   美股: {data['data']['us_count']} 支")
            print(f"   台股: {data['data']['tw_count']} 支")
    else:
        print(f"❌ {data['message']}")
except Exception as e:
    print(f"❌ 錯誤: {e}")

print("\n" + "=" * 80)
print("測試完成")
print("=" * 80)
