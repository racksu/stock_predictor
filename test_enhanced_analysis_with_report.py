"""
Test Script for Enhanced Analysis with Detailed Reporting
Taiwan Stock Prediction System v5.0

This script demonstrates the new detailed analysis features with comprehensive
reasoning for each scoring component across all five dimensions.

Usage:
    python test_enhanced_analysis_with_report.py

Author: Taiwan Stock Prediction System
Version: 5.0
Date: 2025-11-26
"""

import sys
import os
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from detailed_analysis_reporter import DetailedAnalysisReporter


def create_sample_stock_data_bullish():
    """
    Create sample stock data representing a bullish scenario.

    Scenario: Strong uptrend with positive indicators across all dimensions
    - Technical: Strong momentum, positive crossovers
    - Market: Heavy institutional buying
    - Chips: Increasing margin purchase, short covering
    - Macro: Low VIX, weak dollar, falling yields
    - Sentiment: Very positive news coverage
    """
    return {
        # Technical indicators
        'kd': {
            'k': 65.5,
            'd': 58.2,
            'trend': 'golden_cross'
        },
        'obv': {
            'current': 25000000,
            'trend': 'rising',
            'change_pct': 8.5
        },
        'price': {
            'current': 585.0,
            'trend': 'rising'
        },
        'moving_averages': {
            'ma5': 585,
            'ma10': 580,
            'ma20': 575,
            'ma60': 560
        },
        'rsi': {
            'current': 62.5,
            'trend': 'rising'
        },
        'macd': {
            'macd': 3.2,
            'signal': 2.1,
            'histogram': 1.1,
            'histogram_expanding': True
        },

        # Market data (institutional investors)
        'foreign_investors': {
            'net_buy': 2500000,
            'trend': 'strong_buying'
        },
        'investment_trust': {
            'net_buy': 800000
        },
        'dealer_proprietary': {
            'net_buy': 350000
        },

        # Chips data (margin trading)
        'margin_purchase': {
            'change': 1200000,
            'balance': 8000000,
            'ratio': 28.5
        },
        'short_selling': {
            'change': -250000,
            'balance': 400000
        },
        'chips_concentration': {
            'score': 78
        }
    }


def create_sample_stock_data_bearish():
    """
    Create sample stock data representing a bearish scenario.

    Scenario: Strong downtrend with negative indicators across all dimensions
    - Technical: Weak momentum, death crosses
    - Market: Heavy institutional selling
    - Chips: Decreasing margin purchase, short buildup
    - Macro: High VIX, strong dollar, rising yields
    - Sentiment: Negative news coverage
    """
    return {
        # Technical indicators
        'kd': {
            'k': 25.5,
            'd': 35.8,
            'trend': 'death_cross'
        },
        'obv': {
            'current': 12000000,
            'trend': 'falling',
            'change_pct': -7.2
        },
        'price': {
            'current': 485.0,
            'trend': 'falling'
        },
        'moving_averages': {
            'ma5': 485,
            'ma10': 495,
            'ma20': 505,
            'ma60': 520
        },
        'rsi': {
            'current': 32.5,
            'trend': 'falling'
        },
        'macd': {
            'macd': -2.8,
            'signal': -1.5,
            'histogram': -1.3,
            'histogram_expanding': True
        },

        # Market data (institutional investors)
        'foreign_investors': {
            'net_buy': -1800000,
            'trend': 'strong_selling'
        },
        'investment_trust': {
            'net_buy': -600000
        },
        'dealer_proprietary': {
            'net_buy': -200000
        },

        # Chips data (margin trading)
        'margin_purchase': {
            'change': -900000,
            'balance': 4000000,
            'ratio': 42.5
        },
        'short_selling': {
            'change': 180000,
            'balance': 850000
        },
        'chips_concentration': {
            'score': 35
        }
    }


def create_sample_stock_data_mixed():
    """
    Create sample stock data representing a mixed scenario.

    Scenario: Conflicting signals across different dimensions
    - Technical: Some bullish, some bearish
    - Market: Mixed institutional activity
    - Chips: Neutral positioning
    - Macro: Moderate conditions
    - Sentiment: Neutral coverage
    """
    return {
        # Technical indicators
        'kd': {
            'k': 52.5,
            'd': 48.2,
            'trend': 'neutral'
        },
        'obv': {
            'current': 18000000,
            'trend': 'neutral',
            'change_pct': 1.2
        },
        'price': {
            'current': 535.0,
            'trend': 'sideways'
        },
        'moving_averages': {
            'ma5': 537,
            'ma10': 535,
            'ma20': 533,
            'ma60': 530
        },
        'rsi': {
            'current': 51.5,
            'trend': 'neutral'
        },
        'macd': {
            'macd': 0.5,
            'signal': 0.4,
            'histogram': 0.1,
            'histogram_expanding': False
        },

        # Market data (institutional investors)
        'foreign_investors': {
            'net_buy': 300000,
            'trend': 'light_buying'
        },
        'investment_trust': {
            'net_buy': -150000
        },
        'dealer_proprietary': {
            'net_buy': 50000
        },

        # Chips data (margin trading)
        'margin_purchase': {
            'change': 100000,
            'balance': 6000000,
            'ratio': 32.0
        },
        'short_selling': {
            'change': -20000,
            'balance': 600000
        },
        'chips_concentration': {
            'score': 55
        }
    }


def create_analysis_results_bullish():
    """Create analysis results for bullish scenario."""
    return {
        'technical': {'score': 78},
        'market': {'score': 75},
        'chips': {'score': 72},
        'macro': {
            'score': 68,
            'vix': {'level': 14.5, 'change': -3.2},
            'dollar_index': {'level': 101.2, 'trend': 'weakening'},
            'treasury_yield': {'level': 3.8, 'change': -0.15}
        },
        'sentiment': {
            'score': 80,
            'sentiment_score': 0.62,
            'article_count': 32,
            'trend': 'improving',
            'variance': 0.12,
            'key_themes': [
                'Record quarterly earnings',
                'Strong AI chip demand',
                'Expanding market share',
                'Innovation leadership'
            ]
        }
    }


def create_analysis_results_bearish():
    """Create analysis results for bearish scenario."""
    return {
        'technical': {'score': 28},
        'market': {'score': 32},
        'chips': {'score': 35},
        'macro': {
            'score': 38,
            'vix': {'level': 28.5, 'change': 5.8},
            'dollar_index': {'level': 106.8, 'trend': 'strengthening'},
            'treasury_yield': {'level': 4.9, 'change': 0.25}
        },
        'sentiment': {
            'score': 25,
            'sentiment_score': -0.48,
            'article_count': 28,
            'trend': 'deteriorating',
            'variance': 0.18,
            'key_themes': [
                'Weak demand outlook',
                'Competitive pressure',
                'Margin compression',
                'Market share loss'
            ]
        }
    }


def create_analysis_results_mixed():
    """Create analysis results for mixed scenario."""
    return {
        'technical': {'score': 52},
        'market': {'score': 48},
        'chips': {'score': 50},
        'macro': {
            'score': 55,
            'vix': {'level': 19.5, 'change': 0.8},
            'dollar_index': {'level': 103.5, 'trend': 'neutral'},
            'treasury_yield': {'level': 4.2, 'change': 0.05}
        },
        'sentiment': {
            'score': 53,
            'sentiment_score': 0.08,
            'article_count': 18,
            'trend': 'stable',
            'variance': 0.25,
            'key_themes': [
                'Steady performance',
                'Awaiting catalysts',
                'Industry consolidation'
            ]
        }
    }


def run_test_scenario(scenario_name: str, stock_code: str, stock_data: dict,
                     analysis_results: dict):
    """
    Run a test scenario and generate detailed report.

    Args:
        scenario_name: Name of the scenario (e.g., "Bullish", "Bearish")
        stock_code: Stock symbol
        stock_data: Historical stock data and indicators
        analysis_results: Analysis results from all dimensions
    """
    print("\n" + "=" * 80)
    print(f"TESTING SCENARIO: {scenario_name}")
    print("=" * 80)

    # Create reporter
    reporter = DetailedAnalysisReporter()

    # Generate comprehensive report
    report = reporter.generate_comprehensive_report(
        stock_code=stock_code,
        stock_data=stock_data,
        analysis_results=analysis_results
    )

    # Format and display report
    text_report = reporter.format_report_as_text(report)
    print(text_report)

    # Save reports to files
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    txt_filename = f'reports/analysis_{stock_code}_{scenario_name.lower()}_{timestamp}.txt'
    json_filename = f'reports/analysis_{stock_code}_{scenario_name.lower()}_{timestamp}.json'

    # Create reports directory if it doesn't exist
    os.makedirs('reports', exist_ok=True)

    # Save text report
    with open(txt_filename, 'w', encoding='utf-8') as f:
        f.write(text_report)

    # Save JSON report
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\nReports saved:")
    print(f"  - Text: {txt_filename}")
    print(f"  - JSON: {json_filename}")

    return report


def test_all_scenarios():
    """Test all three scenarios: Bullish, Bearish, and Mixed."""

    print("=" * 80)
    print("TAIWAN STOCK PREDICTION SYSTEM v5.0")
    print("Enhanced Analysis with Detailed Reporting - Test Suite")
    print("=" * 80)
    print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis test suite demonstrates the five-dimensional analysis system")
    print("with comprehensive reasoning for each scoring component.\n")

    # Test Scenario 1: Bullish (e.g., TSMC 2330)
    print("\n" + ">" * 80)
    print("SCENARIO 1: STRONG BULLISH TREND")
    print("Stock: 2330 (TSMC) - Simulated strong uptrend scenario")
    print(">" * 80)

    bullish_data = create_sample_stock_data_bullish()
    bullish_results = create_analysis_results_bullish()
    report_bullish = run_test_scenario(
        scenario_name="Bullish",
        stock_code="2330",
        stock_data=bullish_data,
        analysis_results=bullish_results
    )

    # Test Scenario 2: Bearish (e.g., hypothetical weak stock)
    print("\n\n" + ">" * 80)
    print("SCENARIO 2: STRONG BEARISH TREND")
    print("Stock: 1234 (Hypothetical) - Simulated strong downtrend scenario")
    print(">" * 80)

    bearish_data = create_sample_stock_data_bearish()
    bearish_results = create_analysis_results_bearish()
    report_bearish = run_test_scenario(
        scenario_name="Bearish",
        stock_code="1234",
        stock_data=bearish_data,
        analysis_results=bearish_results
    )

    # Test Scenario 3: Mixed (e.g., consolidating stock)
    print("\n\n" + ">" * 80)
    print("SCENARIO 3: MIXED SIGNALS / CONSOLIDATION")
    print("Stock: 2317 (Hon Hai) - Simulated consolidation scenario")
    print(">" * 80)

    mixed_data = create_sample_stock_data_mixed()
    mixed_results = create_analysis_results_mixed()
    report_mixed = run_test_scenario(
        scenario_name="Mixed",
        stock_code="2317",
        stock_data=mixed_data,
        analysis_results=mixed_results
    )

    # Summary comparison
    print("\n\n" + "=" * 80)
    print("COMPARATIVE SUMMARY OF ALL SCENARIOS")
    print("=" * 80)

    scenarios = [
        ("BULLISH (2330)", report_bullish),
        ("BEARISH (1234)", report_bearish),
        ("MIXED (2317)", report_mixed)
    ]

    print(f"\n{'Scenario':<20} {'Overall Score':<15} {'Recommendation':<20} {'Confidence':<15}")
    print("-" * 70)

    for name, report in scenarios:
        score = report['overall_score']
        rec = report['recommendation']
        print(f"{name:<20} {score:<15.2f} {rec['action']:<20} {rec['confidence']:<15}")

    print("\n" + "=" * 80)
    print("DIMENSION-BY-DIMENSION COMPARISON")
    print("=" * 80)

    dimensions = ['technical', 'market', 'chips', 'macro', 'sentiment']
    weights = [0.30, 0.20, 0.20, 0.15, 0.15]

    print(f"\n{'Dimension':<20} {'Bullish':<12} {'Bearish':<12} {'Mixed':<12} {'Weight':<10}")
    print("-" * 70)

    for dim, weight in zip(dimensions, weights):
        bull_score = report_bullish['dimension_scores'][dim]
        bear_score = report_bearish['dimension_scores'][dim]
        mix_score = report_mixed['dimension_scores'][dim]
        print(f"{dim.capitalize():<20} {bull_score:<12.2f} {bear_score:<12.2f} {mix_score:<12.2f} {weight*100:<10.0f}%")

    print("\n" + "=" * 80)
    print("KEY INSIGHTS FROM TESTING")
    print("=" * 80)

    print("\n1. BULLISH SCENARIO (2330):")
    print(f"   - Overall Score: {report_bullish['overall_score']:.2f}")
    print(f"   - Recommendation: {report_bullish['recommendation']['action']}")
    print(f"   - Key Strengths: {len(report_bullish['strengths'])} factors")
    print(f"   - Risk Warnings: {len(report_bullish['risk_warnings'])} factors")

    print("\n2. BEARISH SCENARIO (1234):")
    print(f"   - Overall Score: {report_bearish['overall_score']:.2f}")
    print(f"   - Recommendation: {report_bearish['recommendation']['action']}")
    print(f"   - Key Strengths: {len(report_bearish['strengths'])} factors")
    print(f"   - Risk Warnings: {len(report_bearish['risk_warnings'])} factors")

    print("\n3. MIXED SCENARIO (2317):")
    print(f"   - Overall Score: {report_mixed['overall_score']:.2f}")
    print(f"   - Recommendation: {report_mixed['recommendation']['action']}")
    print(f"   - Key Strengths: {len(report_mixed['strengths'])} factors")
    print(f"   - Risk Warnings: {len(report_mixed['risk_warnings'])} factors")

    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print("\nAll detailed reports have been saved to the 'reports/' directory.")
    print("Review the JSON files for programmatic access to the analysis data.")
    print("Review the TXT files for human-readable formatted reports.")


def demonstrate_single_indicator_analysis():
    """
    Demonstrate detailed analysis of individual indicators with step-by-step reasoning.
    """
    print("\n\n" + "=" * 80)
    print("DETAILED INDICATOR ANALYSIS DEMONSTRATION")
    print("=" * 80)
    print("\nThis section demonstrates how the system generates detailed reasoning")
    print("for each individual indicator within the five-dimensional framework.\n")

    reporter = DetailedAnalysisReporter()

    # Example 1: KD Indicator
    print("\n" + "-" * 80)
    print("EXAMPLE 1: KD INDICATOR ANALYSIS")
    print("-" * 80)

    kd_stock_data = {
        'kd': {'k': 82.5, 'd': 75.2}
    }

    kd_analysis = reporter._analyze_kd_indicator(kd_stock_data)
    print(f"\nK Value: {kd_analysis['k_value']:.2f}")
    print(f"D Value: {kd_analysis['d_value']:.2f}")
    print(f"Signal: {kd_analysis['signal'].upper()}")
    print(f"Score: {kd_analysis['score']:.2f}/100")
    print("\nReasoning:")
    for i, reason in enumerate(kd_analysis['reasoning'], 1):
        print(f"  {i}. {reason}")

    # Example 2: OBV Indicator
    print("\n" + "-" * 80)
    print("EXAMPLE 2: OBV INDICATOR ANALYSIS")
    print("-" * 80)

    obv_stock_data = {
        'obv': {
            'current': 20000000,
            'trend': 'rising',
            'change_pct': 12.5
        },
        'price': {
            'trend': 'rising'
        }
    }

    obv_analysis = reporter._analyze_obv_indicator(obv_stock_data)
    print(f"\nCurrent OBV: {obv_analysis['current_obv']:,.0f}")
    print(f"Trend: {obv_analysis['trend'].upper()}")
    print(f"Change: {obv_analysis['change_pct']:+.2f}%")
    print(f"Signal: {obv_analysis['signal'].upper()}")
    print(f"Score: {obv_analysis['score']:.2f}/100")
    print("\nReasoning:")
    for i, reason in enumerate(obv_analysis['reasoning'], 1):
        print(f"  {i}. {reason}")

    # Example 3: RSI Indicator
    print("\n" + "-" * 80)
    print("EXAMPLE 3: RSI INDICATOR ANALYSIS")
    print("-" * 80)

    rsi_stock_data = {
        'rsi': {
            'current': 28.5,
            'trend': 'falling'
        }
    }

    rsi_analysis = reporter._analyze_rsi_indicator(rsi_stock_data)
    print(f"\nCurrent RSI: {rsi_analysis['current_rsi']:.2f}")
    print(f"Trend: {rsi_analysis['trend'].upper()}")
    print(f"Signal: {rsi_analysis['signal'].upper()}")
    print(f"Score: {rsi_analysis['score']:.2f}/100")
    print("\nReasoning:")
    for i, reason in enumerate(rsi_analysis['reasoning'], 1):
        print(f"  {i}. {reason}")

    print("\n" + "=" * 80)
    print("Individual indicator demonstrations show how each component")
    print("contributes detailed reasoning to the overall analysis framework.")
    print("=" * 80)


def main():
    """Main test function."""
    try:
        # Run comprehensive test suite
        test_all_scenarios()

        # Demonstrate individual indicator analysis
        demonstrate_single_indicator_analysis()

        print("\n\n" + "=" * 80)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Review the generated reports in the 'reports/' directory")
        print("2. Examine the detailed reasoning for each indicator")
        print("3. Integrate with live data sources (market data APIs, NewsAPI)")
        print("4. Customize weights and thresholds for your trading strategy")
        print("5. Set up automated daily analysis runs")

    except Exception as e:
        print(f"\n\nERROR: Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
