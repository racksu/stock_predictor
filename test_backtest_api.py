"""
Test Backtest API
測試回測API功能
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """測試健康檢查"""
    print("\n" + "="*60)
    print("測試 1: 健康檢查")
    print("="*60)

    response = requests.get(f"{BASE_URL}/api/health")
    data = response.json()

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")

    if data['data']['features']['backtesting']:
        print("✓ 回測模組已啟用")
    else:
        print("✗ 回測模組未啟用")

    return data['data']['features']['backtesting']


def test_backtest(symbol='2330'):
    """測試回測功能"""
    print("\n" + "="*60)
    print(f"測試 2: 執行回測 - {symbol}")
    print("="*60)

    payload = {
        'symbol': symbol,
        'initial_capital': 1000000,
        'position_size': 0.3,
        'stop_loss': -0.08,
        'take_profit': 0.15,
        'rebalance_days': 5,
        'strategy': 'enhanced'
    }

    print(f"Request: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    print("\n執行中...")

    try:
        response = requests.post(
            f"{BASE_URL}/api/backtest",
            json=payload,
            timeout=120
        )

        data = response.json()

        if data['success']:
            print("\n✓ 回測成功!")
            print("\n結果摘要:")
            print(f"  股票代碼: {data['data']['symbol']}")
            print(f"  策略: {data['data']['strategy']}")
            print(f"  初始資金: ${data['data']['results']['initial_capital']:,.0f}")
            print(f"  最終淨值: ${data['data']['results']['final_equity']:,.0f}")
            print(f"  總報酬: {data['data']['results']['total_return_pct']:+.2f}%")

            metrics = data['data']['metrics']
            print(f"\n績效指標:")
            print(f"  交易次數: {metrics['total_trades']}")
            print(f"  勝率: {metrics['win_rate']*100:.2f}%")
            print(f"  最大回撤: {metrics['max_drawdown']*100:.2f}%")
            print(f"  Sharpe比率: {metrics['sharpe_ratio']:.2f}")
            print(f"  獲利因子: {metrics['profit_factor']:.2f}")

            print(f"\n交易明細 (前5筆):")
            for i, trade in enumerate(data['data']['trades'][:5], 1):
                print(f"  {i}. {trade['entry_date']} -> {trade['exit_date']}: "
                      f"{trade['profit_pct']*100:+.2f}% ({trade['exit_reason']})")

            return True
        else:
            print(f"\n✗ 回測失敗: {data['message']}")
            return False

    except requests.Timeout:
        print("\n✗ 請求超時 (回測可能需要較長時間)")
        return False
    except Exception as e:
        print(f"\n✗ 錯誤: {e}")
        return False


def test_backtest_compare(symbol='2330'):
    """測試參數比較"""
    print("\n" + "="*60)
    print(f"測試 3: 參數比較 - {symbol}")
    print("="*60)

    payload = {
        'symbol': symbol,
        'param_sets': [
            {'position_size': 0.2, 'stop_loss': -0.05, 'take_profit': 0.10},
            {'position_size': 0.3, 'stop_loss': -0.08, 'take_profit': 0.15},
            {'position_size': 0.5, 'stop_loss': -0.10, 'take_profit': 0.20},
        ]
    }

    print(f"測試 {len(payload['param_sets'])} 組參數...")
    print("\n執行中...")

    try:
        response = requests.post(
            f"{BASE_URL}/api/backtest_compare",
            json=payload,
            timeout=300
        )

        data = response.json()

        if data['success']:
            print("\n✓ 參數比較成功!")
            print("\n比較結果:")
            print(f"{'倉位':<8} {'停損':<8} {'停利':<8} {'報酬率':<12} {'勝率':<10} {'Sharpe':<10}")
            print("-" * 60)

            for result in data['data']['results']:
                params = result['parameters']
                print(f"{params['position_size']*100:>6.0f}% "
                      f"{params['stop_loss']*100:>6.0f}% "
                      f"{params['take_profit']*100:>6.0f}% "
                      f"{result['total_return']*100:>+10.2f}% "
                      f"{result['win_rate']*100:>8.1f}% "
                      f"{result['sharpe_ratio']:>8.2f}")

            best = data['data']['best_parameters']
            print(f"\n最佳參數:")
            print(f"  倉位: {best['position_size']*100:.0f}%")
            print(f"  停損: {best['stop_loss']*100:.0f}%")
            print(f"  停利: {best['take_profit']*100:.0f}%")

            return True
        else:
            print(f"\n✗ 參數比較失敗: {data['message']}")
            return False

    except requests.Timeout:
        print("\n✗ 請求超時 (參數比較需要較長時間)")
        return False
    except Exception as e:
        print(f"\n✗ 錯誤: {e}")
        return False


def main():
    """主測試流程"""
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║         回測 API 測試                                  ║")
    print("╚════════════════════════════════════════════════════════╝")

    print("\n提示: 請確保 Web 伺服器正在運行")
    print("      執行: python web_server_enhanced_v3.1.py")

    input("\n按 Enter 開始測試...")

    # 測試 1: 健康檢查
    backtest_available = test_health()

    if not backtest_available:
        print("\n⚠️ 回測模組未啟用，無法繼續測試")
        return

    # 測試 2: 執行回測
    symbol = input("\n請輸入股票代碼 (預設 2330): ").strip() or '2330'
    test_backtest(symbol)

    # 測試 3: 參數比較
    if input("\n是否執行參數比較測試? (y/n, 預設 n): ").strip().lower() == 'y':
        test_backtest_compare(symbol)

    print("\n" + "="*60)
    print("測試完成!")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n測試已中斷")
    except requests.ConnectionError:
        print("\n✗ 無法連接到伺服器")
        print("  請確保 web_server_enhanced_v3.1.py 正在運行")
    except Exception as e:
        print(f"\n✗ 錯誤: {e}")
        import traceback
        traceback.print_exc()
