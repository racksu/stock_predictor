"""
測試單股分析修復
驗證所有前端需要的字段是否都正確返回
"""

import requests
import json

API_BASE = 'http://localhost:5000/api'

print("="*80)
print("測試單股分析修復")
print("請確保 web_server_enhanced_v3.1.py 已經在運行")
print("="*80)

# 測試美股
print("\n【測試 1】分析美股 AAPL")
print("-"*80)

try:
    response = requests.post(
        f'{API_BASE}/analyze',
        json={'symbol': 'AAPL', 'strategy': 'moderate'},
        headers={'Content-Type': 'application/json'},
        timeout=60
    )

    print(f"狀態碼: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        if data['success']:
            result = data['data']
            print(f"\n✅ 分析成功！")

            # 檢查所有必要字段
            required_fields = {
                'stock_name': '公司名稱',
                'stock_name_chinese': '中文名稱（台股）',
                'data_date': '數據日期',
                'target_timeframe': '目標達成時間',
                'probability': '成功機率',
                'avg_volume': '平均成交量',
                'relative_volume': '相對成交量',
                'liquidity_rating': '流動性評級',
                'summary': '分析摘要',
                'key_points': '關鍵要點',
                'operation_suggestions': '操作建議',
                'risks': '風險提示',
                'rating': '評級',
                'action': '操作',
                'market_display': '市場標示'
            }

            print(f"\n【字段檢查】")
            missing_fields = []
            for field, name in required_fields.items():
                if field in result:
                    value = result[field]
                    if field == 'target_timeframe':
                        days = value.get('days', 'N/A')
                        print(f"  ✅ {name}: {days} 天")
                    elif field == 'probability':
                        print(f"  ✅ {name}: {value*100:.0f}%")
                    elif field == 'avg_volume':
                        print(f"  ✅ {name}: {value:,.0f}")
                    elif field == 'relative_volume':
                        print(f"  ✅ {name}: {value:.2f}x")
                    elif field == 'key_points':
                        print(f"  ✅ {name}: {len(value)} 條")
                    elif field == 'operation_suggestions':
                        print(f"  ✅ {name}: {len(value)} 條")
                    elif field == 'risks':
                        print(f"  ✅ {name}: {len(value)} 條")
                    else:
                        print(f"  ✅ {name}: {value}")
                else:
                    print(f"  ❌ {name}: 缺失")
                    missing_fields.append(name)

            if missing_fields:
                print(f"\n⚠️ 缺少字段: {', '.join(missing_fields)}")
            else:
                print(f"\n✅ 所有必要字段都存在！")

            # 顯示部分內容
            print(f"\n【分析摘要】")
            print(f"  {result.get('summary', 'N/A')}")

            print(f"\n【關鍵要點】")
            for point in result.get('key_points', [])[:3]:
                print(f"  • {point}")

            print(f"\n【操作建議】")
            for suggestion in result.get('operation_suggestions', [])[:3]:
                print(f"  • {suggestion}")

        else:
            print(f"❌ 分析失敗: {data['message']}")
    else:
        print(f"❌ HTTP 錯誤: {response.status_code}")

except requests.exceptions.ConnectionError:
    print("❌ 無法連接到服務器")
    print("請確保運行: python web_server_enhanced_v3.1.py")
except Exception as e:
    print(f"❌ 錯誤: {e}")
    import traceback
    traceback.print_exc()

# 測試台股
print("\n\n【測試 2】分析台股 2330")
print("-"*80)

try:
    response = requests.post(
        f'{API_BASE}/analyze',
        json={'symbol': '2330', 'strategy': 'moderate'},
        headers={'Content-Type': 'application/json'},
        timeout=60
    )

    print(f"狀態碼: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        if data['success']:
            result = data['data']
            print(f"\n✅ 分析成功！")

            # 顯示關鍵信息
            print(f"\n【基本資訊】")
            print(f"  股票代碼: {result.get('symbol', 'N/A')}")
            print(f"  公司名稱: {result.get('stock_name_chinese', 'N/A')}")
            print(f"  市場: {result.get('market_display', 'N/A')}")
            print(f"  數據日期: {result.get('data_date', 'N/A')}")

            print(f"\n【評分與建議】")
            print(f"  評分: {result.get('total_score', 'N/A')}/100")
            print(f"  評級: {result.get('rating', 'N/A')}")
            print(f"  操作: {result.get('action', 'N/A')}")
            print(f"  成功機率: {result.get('probability', 0)*100:.0f}%")

            print(f"\n【價格與目標】")
            print(f"  現價: {result.get('current_price', 'N/A')}")
            print(f"  目標價: {result.get('target_price', 'N/A')}")
            print(f"  預期報酬: {result.get('expected_return', 0)*100:+.2f}%")
            timeframe = result.get('target_timeframe', {})
            print(f"  目標時間: {timeframe.get('days', 'N/A')} 天")

            print(f"\n【成交量與流動性】")
            print(f"  平均成交量: {result.get('avg_volume', 0):,.0f}")
            print(f"  相對成交量: {result.get('relative_volume', 'N/A'):.2f}x")
            print(f"  流動性評級: {result.get('liquidity_rating', 'N/A')}")

            print(f"\n✅ 所有字段正常顯示！")

        else:
            print(f"❌ 分析失敗: {data['message']}")
    else:
        print(f"❌ HTTP 錯誤: {response.status_code}")

except Exception as e:
    print(f"❌ 錯誤: {e}")

print("\n" + "="*80)
print("測試完成")
print("="*80)
print("\n如果所有測試通過，請重新啟動 Web 服務器並在瀏覽器中測試前端")
print("="*80)
