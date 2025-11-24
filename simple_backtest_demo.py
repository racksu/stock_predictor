"""
Simple Backtesting Demo
Demonstrates backtesting without unicode issues
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import backtesting engine
from backtesting_engine import BacktestingEngine, EnhancedStockAnalyzer

def create_sample_data():
    """Create sample stock data for demo"""
    print("Creating sample data...")

    # Generate 500 days of sample data
    dates = pd.date_range(end=datetime.now(), periods=500, freq='D')

    # Simulate price movement
    np.random.seed(42)
    returns = np.random.randn(500) * 0.02  # 2% daily volatility
    price = 100 * np.exp(returns.cumsum())

    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'open': price * (1 + np.random.randn(500) * 0.005),
        'high': price * (1 + abs(np.random.randn(500)) * 0.01),
        'low': price * (1 - abs(np.random.randn(500)) * 0.01),
        'close': price,
        'volume': np.random.randint(1000000, 10000000, 500)
    })

    print(f"Sample data created: {len(df)} rows")
    print(f"Date range: {df['date'].iloc[0].date()} to {df['date'].iloc[-1].date()}")
    print(f"Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")

    return df


def demo_backtest():
    """Run a simple backtest demo"""
    print("\n" + "="*80)
    print("BACKTESTING SYSTEM DEMO")
    print("="*80 + "\n")

    # Step 1: Create sample data
    print("Step 1: Prepare data")
    df = create_sample_data()

    # Step 2: Initialize backtest engine
    print("\nStep 2: Initialize backtesting engine")
    engine = BacktestingEngine(
        initial_capital=1000000,
        commission_rate=0.001425,
        tax_rate=0.003,
        slippage=0.001
    )
    print("Engine initialized with:")
    print(f"  Initial capital: $1,000,000")
    print(f"  Commission: 0.1425%")
    print(f"  Tax: 0.3%")
    print(f"  Slippage: 0.1%")

    # Step 3: Run backtest
    print("\nStep 3: Run backtest")
    print("This may take a moment...")

    results = engine.run_backtest(
        df=df,
        strategy='enhanced',
        position_size=0.3,
        stop_loss=-0.08,
        take_profit=0.15,
        rebalance_days=5
    )

    # Step 4: Display results
    print("\n" + "="*80)
    print("BACKTEST RESULTS")
    print("="*80)

    print(f"\nOverall Performance:")
    print(f"  Initial Capital: ${results['initial_capital']:,.0f}")
    print(f"  Final Equity: ${results['final_equity']:,.0f}")
    print(f"  Total Return: {results['total_return']*100:+.2f}%")

    m = results['metrics']
    print(f"\nTrading Statistics:")
    print(f"  Total Trades: {m['total_trades']}")
    print(f"  Winning Trades: {m['winning_trades']}")
    print(f"  Losing Trades: {m['losing_trades']}")
    print(f"  Win Rate: {m['win_rate']*100:.2f}%")
    print(f"  Avg Holding Days: {m['avg_holding_days']:.1f}")

    print(f"\nProfit Analysis:")
    print(f"  Average Profit: ${m['avg_profit']:,.0f} ({m['avg_profit_pct']*100:+.2f}%)")
    print(f"  Max Profit: ${m['max_profit']:,.0f}")
    print(f"  Max Loss: ${m['max_loss']:,.0f}")
    print(f"  Profit Factor: {m['profit_factor']:.2f}")

    print(f"\nRisk Metrics:")
    print(f"  Max Drawdown: {m['max_drawdown']*100:.2f}%")
    print(f"  Sharpe Ratio: {m['sharpe_ratio']:.2f}")

    # Step 5: Show trade details
    if results['trades']:
        print(f"\nTrade Details (first 5 trades):")
        print("-" * 80)
        print(f"{'Entry Date':<12} {'Exit Date':<12} {'Entry $':<10} {'Exit $':<10} "
              f"{'Return':<10} {'Days':<8} {'Reason':<15}")
        print("-" * 80)

        for trade in results['trades'][:5]:
            print(f"{str(trade['entry_date'].date()):<12} "
                  f"{str(trade['exit_date'].date()):<12} "
                  f"${trade['entry_price']:<9.2f} "
                  f"${trade['exit_price']:<9.2f} "
                  f"{trade['profit_pct']*100:>+8.2f}% "
                  f"{trade['days_held']:>6} "
                  f"{trade['exit_reason']:<15}")

        if len(results['trades']) > 5:
            print(f"... and {len(results['trades']) - 5} more trades")

    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80)

    print("\nNext steps:")
    print("  1. Run 'python backtesting_examples.py' for more examples")
    print("  2. Test with real stock data from your system")
    print("  3. Optimize parameters for better results")
    print("  4. Read BACKTESTING_README.md for detailed documentation")

    return results


if __name__ == "__main__":
    try:
        results = demo_backtest()
        print("\nDemo completed successfully!")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
