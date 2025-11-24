"""
快速測試回測系統
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from backtesting_engine import BacktestingEngine
from unified_stock_data_manager import UnifiedStockDataManager

def quick_test():
    """快速測試回測功能"""
    print("\n" + "="*80)
    print("回測系統快速測試")
    print("="*80 + "\n")

    # 1. 載入數據
    print("步驟 1: 載入股票數據...")
    manager = UnifiedStockDataManager(data_dir='./stock_data')

    # 嘗試載入本地數據
    df = manager.load_stock_data('2330')

    if df is None or len(df) < 200:
        print("  本地無數據，嘗試下載...")
        df = manager.download_stock_data('2330', period='1y')

    if df is None or len(df) < 200:
        print("  [失敗] 無法獲取足夠的數據")
        return False

    print(f"  [成功] 載入 {len(df)} 筆數據")
    print(f"  期間: {df['date'].iloc[0]} ~ {df['date'].iloc[-1]}")

    # 2. 創建回測引擎
    print("\n步驟 2: 初始化回測引擎...")
    engine = BacktestingEngine(
        initial_capital=1000000,
        commission_rate=0.001425,
        tax_rate=0.003,
        slippage=0.001
    )
    print("  [成功] 引擎初始化完成")

    # 3. 執行回測
    print("\n步驟 3: 執行回測 (這可能需要一些時間)...")
    try:
        results = engine.run_backtest(
            df=df,
            strategy='enhanced',
            position_size=0.3,
            stop_loss=-0.08,
            take_profit=0.15,
            rebalance_days=5
        )
        print("  [成功] 回測完成")
    except Exception as e:
        print(f"  [失敗] 回測錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 4. 檢查結果
    print("\n步驟 4: 驗證結果...")

    checks = []

    # 檢查基本數據
    checks.append(("初始資金", results['initial_capital'] == 1000000))
    checks.append(("最終淨值存在", results['final_equity'] > 0))
    checks.append(("總報酬計算", 'total_return' in results))
    checks.append(("交易記錄", len(results['trades']) >= 0))
    checks.append(("績效指標", 'metrics' in results))
    checks.append(("資金曲線", len(results['equity_curve']) > 0))

    all_passed = True
    for check_name, passed in checks:
        status = "[通過]" if passed else "[失敗]"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False

    # 5. 顯示簡要結果
    if all_passed:
        print("\n" + "="*80)
        print("測試結果摘要")
        print("="*80)
        print(f"初始資金: ${results['initial_capital']:,.0f}")
        print(f"最終淨值: ${results['final_equity']:,.0f}")
        print(f"總報酬率: {results['total_return']*100:+.2f}%")
        print(f"交易次數: {results['metrics']['total_trades']}")
        if results['metrics']['total_trades'] > 0:
            print(f"勝率: {results['metrics']['win_rate']*100:.2f}%")
            print(f"最大回撤: {results['metrics']['max_drawdown']*100:.2f}%")
            print(f"Sharpe比率: {results['metrics']['sharpe_ratio']:.2f}")
        print("="*80)

        print("\n[成功] 回測系統測試通過！")
        print("\n提示: 執行 'python backtesting_examples.py' 查看更多範例")
        return True
    else:
        print("\n[警告] 部分測試未通過")
        return False


if __name__ == "__main__":
    try:
        success = quick_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n測試已中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n[錯誤] 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
