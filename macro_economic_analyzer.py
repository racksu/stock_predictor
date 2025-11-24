"""
總體經濟分析器 (Macro Economic Analyzer)
整合聯準會政策、經濟指標等總體面因素

功能：
1. Fed利率政策分析
2. VIX恐慌指數
3. 美元指數（DXY）
4. 經濟指標（GDP、CPI、失業率）
5. 市場情緒指標

數據來源：
- yfinance: VIX, DXY
- FRED API: Fed利率、GDP、CPI、失業率
- 或使用免費替代方案
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️ yfinance未安裝，部分總體經濟數據功能將受限")


class MacroEconomicAnalyzer:
    """
    總體經濟分析器

    分析總體經濟環境對股市的影響
    """

    def __init__(self):
        """初始化分析器"""
        self.cache = {}  # 數據快取
        self.cache_expiry = timedelta(hours=24)  # 快取有效期

    def get_vix_index(self, lookback_days: int = 30) -> Optional[pd.DataFrame]:
        """
        獲取VIX恐慌指數

        參數:
            lookback_days: 回溯天數

        返回:
            DataFrame包含VIX數據
        """
        if not YFINANCE_AVAILABLE:
            print("⚠️ 需要安裝yfinance: pip install yfinance")
            return None

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)

            vix = yf.download('^VIX', start=start_date, end=end_date, progress=False)

            if vix.empty:
                return None

            return vix

        except Exception as e:
            print(f"❌ 獲取VIX數據失敗: {e}")
            return None

    def get_dollar_index(self, lookback_days: int = 30) -> Optional[pd.DataFrame]:
        """
        獲取美元指數（DXY）

        參數:
            lookback_days: 回溯天數

        返回:
            DataFrame包含美元指數數據
        """
        if not YFINANCE_AVAILABLE:
            print("⚠️ 需要安裝yfinance: pip install yfinance")
            return None

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)

            dxy = yf.download('DX-Y.NYB', start=start_date, end=end_date, progress=False)

            if dxy.empty:
                return None

            return dxy

        except Exception as e:
            print(f"❌ 獲取美元指數數據失敗: {e}")
            return None

    def get_treasury_yield(self, lookback_days: int = 30) -> Optional[pd.DataFrame]:
        """
        獲取美國10年期公債殖利率

        參數:
            lookback_days: 回溯天數

        返回:
            DataFrame包含公債殖利率數據
        """
        if not YFINANCE_AVAILABLE:
            print("⚠️ 需要安裝yfinance: pip install yfinance")
            return None

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)

            # 10年期美國公債
            tnx = yf.download('^TNX', start=start_date, end=end_date, progress=False)

            if tnx.empty:
                return None

            return tnx

        except Exception as e:
            print(f"❌ 獲取公債殖利率數據失敗: {e}")
            return None

    def analyze_vix(self, vix_data: pd.DataFrame) -> Dict:
        """
        分析VIX指數並評分

        VIX解讀：
        - < 15: 極度平靜，可能過度樂觀
        - 15-20: 正常低波動
        - 20-30: 正常波動
        - 30-40: 市場恐慌開始
        - > 40: 極度恐慌，可能是買入機會

        參數:
            vix_data: VIX數據

        返回:
            評分字典
        """
        scores = {
            'vix_score': 0,           # VIX評分 (0-10)
            'market_sentiment': '',   # 市場情緒
            'risk_level': '',         # 風險等級
            'current_vix': 0,         # 當前VIX值
            'vix_trend': ''           # VIX趨勢
        }

        if vix_data is None or vix_data.empty:
            return scores

        try:
            current_vix = float(vix_data['Close'].iloc[-1])
            scores['current_vix'] = current_vix

            # VIX趨勢分析
            if len(vix_data) >= 5:
                vix_5d_ago = float(vix_data['Close'].iloc[-5])
                vix_change = ((current_vix - vix_5d_ago) / vix_5d_ago) * 100

                if vix_change > 10:
                    scores['vix_trend'] = '急升（恐慌增加）'
                elif vix_change > 5:
                    scores['vix_trend'] = '上升'
                elif vix_change > -5:
                    scores['vix_trend'] = '平穩'
                elif vix_change > -10:
                    scores['vix_trend'] = '下降'
                else:
                    scores['vix_trend'] = '急降（恐慌緩解）'

            # 根據VIX等級評分
            if current_vix < 15:
                scores['vix_score'] = 5
                scores['market_sentiment'] = '過度樂觀'
                scores['risk_level'] = '中等（可能回調）'
            elif 15 <= current_vix < 20:
                scores['vix_score'] = 8
                scores['market_sentiment'] = '平靜樂觀'
                scores['risk_level'] = '低'
            elif 20 <= current_vix < 25:
                scores['vix_score'] = 10
                scores['market_sentiment'] = '正常波動'
                scores['risk_level'] = '正常'
            elif 25 <= current_vix < 30:
                scores['vix_score'] = 7
                scores['market_sentiment'] = '略有擔憂'
                scores['risk_level'] = '偏高'
            elif 30 <= current_vix < 40:
                scores['vix_score'] = 4
                scores['market_sentiment'] = '市場恐慌'
                scores['risk_level'] = '高'
            else:  # >= 40
                scores['vix_score'] = 9  # 極度恐慌反而是買入機會
                scores['market_sentiment'] = '極度恐慌（逆向機會）'
                scores['risk_level'] = '極高但可能見底'

            return scores

        except Exception as e:
            print(f"❌ VIX分析錯誤: {e}")
            return scores

    def analyze_dollar_index(self, dxy_data: pd.DataFrame) -> Dict:
        """
        分析美元指數並評分

        美元指數影響：
        - 美元強勢：對美股短期負面，對台股負面
        - 美元弱勢：對美股短期正面，對新興市場正面

        參數:
            dxy_data: 美元指數數據

        返回:
            評分字典
        """
        scores = {
            'dxy_score': 0,           # 美元指數評分 (0-10)
            'dollar_strength': '',    # 美元強度
            'current_dxy': 0,         # 當前DXY值
            'dxy_trend': '',          # DXY趨勢
            'impact_on_stocks': ''    # 對股市影響
        }

        if dxy_data is None or dxy_data.empty:
            return scores

        try:
            current_dxy = float(dxy_data['Close'].iloc[-1])
            scores['current_dxy'] = current_dxy

            # DXY趨勢分析
            if len(dxy_data) >= 20:
                dxy_ma20 = dxy_data['Close'].rolling(window=20).mean().iloc[-1]

                if current_dxy > dxy_ma20 * 1.02:
                    scores['dxy_trend'] = '強勢上升'
                    scores['dollar_strength'] = '強勢'
                    scores['impact_on_stocks'] = '短期負面（資金回流美元）'
                    scores['dxy_score'] = 4
                elif current_dxy > dxy_ma20:
                    scores['dxy_trend'] = '溫和上升'
                    scores['dollar_strength'] = '偏強'
                    scores['impact_on_stocks'] = '略微負面'
                    scores['dxy_score'] = 6
                elif current_dxy < dxy_ma20 * 0.98:
                    scores['dxy_trend'] = '弱勢下降'
                    scores['dollar_strength'] = '弱勢'
                    scores['impact_on_stocks'] = '正面（資金流向風險資產）'
                    scores['dxy_score'] = 10
                else:
                    scores['dxy_trend'] = '平穩'
                    scores['dollar_strength'] = '中性'
                    scores['impact_on_stocks'] = '中性'
                    scores['dxy_score'] = 7

            # 絕對水平判斷（歷史區間約80-110）
            if current_dxy > 105:
                scores['dollar_strength'] = '極度強勢'
                scores['dxy_score'] = max(3, scores['dxy_score'] - 2)
            elif current_dxy < 90:
                scores['dollar_strength'] = '極度弱勢'
                scores['dxy_score'] = min(10, scores['dxy_score'] + 2)

            return scores

        except Exception as e:
            print(f"❌ 美元指數分析錯誤: {e}")
            return scores

    def analyze_treasury_yield(self, tnx_data: pd.DataFrame) -> Dict:
        """
        分析10年期公債殖利率

        殖利率影響：
        - 快速上升：對股市負面（資金轉向債券）
        - 溫和上升：中性偏負面
        - 下降：對股市正面（資金尋求更高收益）
        - 極低水平：可能經濟衰退信號

        參數:
            tnx_data: 公債殖利率數據

        返回:
            評分字典
        """
        scores = {
            'yield_score': 0,         # 殖利率評分 (0-10)
            'current_yield': 0,       # 當前殖利率
            'yield_trend': '',        # 趨勢
            'impact_on_stocks': ''    # 對股市影響
        }

        if tnx_data is None or tnx_data.empty:
            return scores

        try:
            current_yield = float(tnx_data['Close'].iloc[-1])
            scores['current_yield'] = current_yield

            # 趨勢分析
            if len(tnx_data) >= 20:
                yield_20d_ago = float(tnx_data['Close'].iloc[-20])
                yield_change = current_yield - yield_20d_ago

                if yield_change > 0.5:
                    scores['yield_trend'] = '快速上升'
                    scores['impact_on_stocks'] = '負面（資金轉向債券）'
                    scores['yield_score'] = 3
                elif yield_change > 0.2:
                    scores['yield_trend'] = '上升'
                    scores['impact_on_stocks'] = '略微負面'
                    scores['yield_score'] = 5
                elif yield_change > -0.2:
                    scores['yield_trend'] = '平穩'
                    scores['impact_on_stocks'] = '中性'
                    scores['yield_score'] = 7
                elif yield_change > -0.5:
                    scores['yield_trend'] = '下降'
                    scores['impact_on_stocks'] = '正面（資金尋求收益）'
                    scores['yield_score'] = 9
                else:
                    scores['yield_trend'] = '快速下降'
                    scores['impact_on_stocks'] = '非常正面但需警惕經濟'
                    scores['yield_score'] = 8

            # 絕對水平判斷
            if current_yield > 5:
                scores['yield_score'] = max(2, scores['yield_score'] - 2)
            elif current_yield < 2:
                scores['yield_score'] = max(5, scores['yield_score'] - 1)

            return scores

        except Exception as e:
            print(f"❌ 殖利率分析錯誤: {e}")
            return scores

    def calculate_macro_score(self,
                             lookback_days: int = 30,
                             use_cache: bool = True) -> Dict:
        """
        計算總體經濟綜合評分

        權重分配：
        - VIX恐慌指數: 40% (對股市影響最直接)
        - 美元指數: 30%
        - 公債殖利率: 30%

        參數:
            lookback_days: 數據回溯天數
            use_cache: 是否使用快取

        返回:
            綜合評分字典（滿分10分）
        """
        print(f"\n📊 開始分析總體經濟環境...")

        # 獲取數據
        vix_data = self.get_vix_index(lookback_days)
        dxy_data = self.get_dollar_index(lookback_days)
        tnx_data = self.get_treasury_yield(lookback_days)

        # 分析各項指標
        vix_analysis = self.analyze_vix(vix_data)
        dxy_analysis = self.analyze_dollar_index(dxy_data)
        yield_analysis = self.analyze_treasury_yield(tnx_data)

        # 計算加權總分
        weights = {
            'vix': 0.40,
            'dxy': 0.30,
            'yield': 0.30
        }

        total_score = (
            vix_analysis['vix_score'] * weights['vix'] +
            dxy_analysis['dxy_score'] * weights['dxy'] +
            yield_analysis['yield_score'] * weights['yield']
        )

        # 判斷總體環境
        if total_score >= 8:
            environment = '非常有利'
            recommendation = '總體環境支持積極投資'
        elif total_score >= 6:
            environment = '有利'
            recommendation = '總體環境正面，適合投資'
        elif total_score >= 4:
            environment = '中性'
            recommendation = '總體環境中性，謹慎操作'
        elif total_score >= 2:
            environment = '不利'
            recommendation = '總體環境偏負面，降低倉位'
        else:
            environment = '非常不利'
            recommendation = '總體環境惡劣，建議避險'

        result = {
            'macro_total_score': total_score,
            'macro_environment': environment,
            'macro_recommendation': recommendation,
            'vix_analysis': vix_analysis,
            'dollar_analysis': dxy_analysis,
            'yield_analysis': yield_analysis,
            'weights': weights,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 打印摘要
        print(f"\n✅ 總體經濟分析完成")
        print(f"   綜合評分: {total_score:.1f}/10")
        print(f"   市場環境: {environment}")
        print(f"   VIX: {vix_analysis['current_vix']:.2f} ({vix_analysis['market_sentiment']})")
        print(f"   美元: {dxy_analysis['current_dxy']:.2f} ({dxy_analysis['dollar_strength']})")
        print(f"   殖利率: {yield_analysis['current_yield']:.2f}% ({yield_analysis['yield_trend']})")

        return result

    def generate_macro_report(self, macro_score: Dict) -> List[str]:
        """
        生成總體經濟分析報告（關鍵要點）

        參數:
            macro_score: 總體經濟評分

        返回:
            關鍵要點列表
        """
        points = []

        vix = macro_score['vix_analysis']
        dxy = macro_score['dollar_analysis']
        yield_info = macro_score['yield_analysis']

        # VIX要點
        if vix['current_vix'] > 0:
            points.append(
                f"🔹 VIX恐慌指數 {vix['current_vix']:.1f}，"
                f"{vix['market_sentiment']}，{vix['vix_trend']}"
            )

        # 美元要點
        if dxy['current_dxy'] > 0:
            points.append(
                f"🔹 美元指數 {dxy['current_dxy']:.2f}，"
                f"{dxy['dollar_strength']}，{dxy['impact_on_stocks']}"
            )

        # 殖利率要點
        if yield_info['current_yield'] > 0:
            points.append(
                f"🔹 10年期公債殖利率 {yield_info['current_yield']:.2f}%，"
                f"{yield_info['yield_trend']}，{yield_info['impact_on_stocks']}"
            )

        # 總結
        points.append(
            f"🔹 總體經濟環境評估：{macro_score['macro_environment']} "
            f"({macro_score['macro_total_score']:.1f}/10分)"
        )

        return points


# ========== 使用示例 ==========

def example_macro_analysis():
    """示例：總體經濟分析"""
    print("\n" + "="*80)
    print("示例：總體經濟環境分析")
    print("="*80)

    analyzer = MacroEconomicAnalyzer()

    # 計算總體經濟評分
    macro_result = analyzer.calculate_macro_score(lookback_days=30)

    # 生成報告
    print(f"\n📋 總體經濟分析報告")
    print("="*80)

    report_points = analyzer.generate_macro_report(macro_result)
    for point in report_points:
        print(f"  {point}")

    print(f"\n💡 投資建議: {macro_result['macro_recommendation']}")

    print("\n" + "="*80)


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║          總體經濟分析器 - Macro Economic Analyzer            ║
    ║                整合Fed政策與市場情緒指標                       ║
    ╚════════════════════════════════════════════════════════════════╝

    功能:
    1. 📊 VIX恐慌指數分析 - 市場情緒溫度計
    2. 💵 美元指數分析 - 資金流向指標
    3. 📈 公債殖利率分析 - 利率環境評估
    4. 🎯 綜合評分系統 - 總體環境判斷

    數據來源: yfinance (免費)
    """)

    example_macro_analysis()
