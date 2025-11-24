"""
AI輿情分析器 (Sentiment Analyzer)
分析股票新聞、社群媒體熱度與情緒

功能：
1. 新聞情緒分析
2. 熱度評分
3. 情緒趨勢
4. 綜合輿情評分

數據來源：
- NewsAPI (免費額度)
- 可擴展：Reddit、Twitter等
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 嘗試導入新聞API
try:
    from newsapi import NewsApiClient
    NEWSAPI_AVAILABLE = True
except ImportError:
    NEWSAPI_AVAILABLE = False
    print("⚠️ NewsAPI未安裝，新聞分析功能將受限")
    print("   安裝方式: pip install newsapi-python")

# 嘗試導入情緒分析庫
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("⚠️ VADER情緒分析未安裝，將使用簡化版分析")
    print("   安裝方式: pip install vaderSentiment")


class SentimentAnalyzer:
    """
    AI輿情分析器

    分析股票在新聞和社群媒體中的熱度與情緒
    """

    def __init__(self, newsapi_key: Optional[str] = None):
        """
        初始化分析器

        參數:
            newsapi_key: NewsAPI密鑰（可選，免費註冊：https://newsapi.org）
        """
        self.newsapi_key = newsapi_key
        self.newsapi = None

        # 初始化NewsAPI客戶端
        if NEWSAPI_AVAILABLE and newsapi_key:
            try:
                self.newsapi = NewsApiClient(api_key=newsapi_key)
                print("✅ NewsAPI已初始化")
            except Exception as e:
                print(f"⚠️ NewsAPI初始化失敗: {e}")

        # 初始化情緒分析器
        if VADER_AVAILABLE:
            self.vader = SentimentIntensityAnalyzer()
            print("✅ VADER情緒分析器已初始化")
        else:
            self.vader = None

    def get_stock_news(self,
                      symbol: str,
                      company_name: str = None,
                      days_back: int = 7,
                      language: str = 'en') -> List[Dict]:
        """
        獲取股票相關新聞

        參數:
            symbol: 股票代碼
            company_name: 公司名稱（可選，用於更精確搜索）
            days_back: 回溯天數
            language: 語言（'en', 'zh'等）

        返回:
            新聞列表
        """
        if not self.newsapi:
            print("⚠️ NewsAPI未配置，無法獲取新聞")
            return []

        try:
            # 計算日期範圍
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)

            # 構建搜索查詢
            query = symbol
            if company_name:
                query = f'{company_name} OR {symbol}'

            # 獲取新聞
            response = self.newsapi.get_everything(
                q=query,
                from_param=from_date.strftime('%Y-%m-%d'),
                to=to_date.strftime('%Y-%m-%d'),
                language=language,
                sort_by='relevancy',
                page_size=100  # 最多100條
            )

            articles = response.get('articles', [])
            print(f"✅ 獲取到 {len(articles)} 條 {symbol} 相關新聞")

            return articles

        except Exception as e:
            print(f"❌ 獲取新聞失敗: {e}")
            return []

    def analyze_sentiment(self, text: str) -> Dict:
        """
        分析文本情緒

        參數:
            text: 要分析的文本

        返回:
            情緒評分字典
        """
        if not text:
            return {'compound': 0, 'pos': 0, 'neu': 1, 'neg': 0}

        if self.vader:
            # 使用VADER分析
            scores = self.vader.polarity_scores(text)
            return scores
        else:
            # 簡化版：基於關鍵詞
            positive_keywords = [
                'bullish', 'rally', 'surge', 'gain', 'rise', 'up', 'high',
                'profit', 'growth', 'strong', 'beat', 'positive', 'good',
                'excellent', 'outperform', 'upgrade', 'buy'
            ]
            negative_keywords = [
                'bearish', 'fall', 'drop', 'loss', 'decline', 'down', 'low',
                'weak', 'miss', 'negative', 'bad', 'poor', 'underperform',
                'downgrade', 'sell', 'crash', 'plunge'
            ]

            text_lower = text.lower()
            pos_count = sum(1 for kw in positive_keywords if kw in text_lower)
            neg_count = sum(1 for kw in negative_keywords if kw in text_lower)

            total = pos_count + neg_count
            if total == 0:
                return {'compound': 0, 'pos': 0, 'neu': 1, 'neg': 0}

            compound = (pos_count - neg_count) / (total + 1)
            return {
                'compound': compound,
                'pos': pos_count / (total + 1),
                'neg': neg_count / (total + 1),
                'neu': 1 - (pos_count + neg_count) / (total + 1)
            }

    def calculate_news_sentiment_score(self,
                                       articles: List[Dict]) -> Dict:
        """
        計算新聞情緒評分

        參數:
            articles: 新聞列表

        返回:
            情緒評分字典
        """
        scores = {
            'sentiment_score': 0,      # 情緒評分 (0-10)
            'avg_sentiment': 0,        # 平均情緒 (-1 到 1)
            'positive_ratio': 0,       # 正面新聞比例
            'negative_ratio': 0,       # 負面新聞比例
            'neutral_ratio': 0,        # 中性新聞比例
            'news_count': 0,           # 新聞數量
            'hotness_score': 0,        # 熱度評分 (0-10)
            'trend': 'neutral'         # 趨勢
        }

        if not articles:
            return scores

        scores['news_count'] = len(articles)

        # 分析每條新聞的情緒
        sentiments = []
        for article in articles:
            # 合併標題和描述
            text = f"{article.get('title', '')} {article.get('description', '')}"
            sentiment = self.analyze_sentiment(text)
            sentiments.append(sentiment['compound'])

        if not sentiments:
            return scores

        # 計算統計數據
        avg_sentiment = np.mean(sentiments)
        scores['avg_sentiment'] = float(avg_sentiment)

        # 計算正負中性比例
        positive_count = sum(1 for s in sentiments if s > 0.05)
        negative_count = sum(1 for s in sentiments if s < -0.05)
        neutral_count = len(sentiments) - positive_count - negative_count

        total = len(sentiments)
        scores['positive_ratio'] = positive_count / total
        scores['negative_ratio'] = negative_count / total
        scores['neutral_ratio'] = neutral_count / total

        # 計算情緒評分 (0-10)
        # 情緒越正面，分數越高
        if avg_sentiment >= 0.5:
            scores['sentiment_score'] = 10
        elif avg_sentiment >= 0.2:
            scores['sentiment_score'] = 8
        elif avg_sentiment >= 0:
            scores['sentiment_score'] = 6
        elif avg_sentiment >= -0.2:
            scores['sentiment_score'] = 4
        elif avg_sentiment >= -0.5:
            scores['sentiment_score'] = 2
        else:
            scores['sentiment_score'] = 0

        # 正面新聞比例加成
        if scores['positive_ratio'] > 0.6:
            scores['sentiment_score'] = min(10, scores['sentiment_score'] + 1)
        # 負面新聞比例扣分
        if scores['negative_ratio'] > 0.6:
            scores['sentiment_score'] = max(0, scores['sentiment_score'] - 1)

        # 計算熱度評分 (基於新聞數量)
        if total >= 50:
            scores['hotness_score'] = 10
        elif total >= 30:
            scores['hotness_score'] = 8
        elif total >= 20:
            scores['hotness_score'] = 7
        elif total >= 10:
            scores['hotness_score'] = 5
        elif total >= 5:
            scores['hotness_score'] = 3
        else:
            scores['hotness_score'] = 1

        # 判斷趨勢
        if avg_sentiment > 0.2:
            scores['trend'] = 'positive'
        elif avg_sentiment < -0.2:
            scores['trend'] = 'negative'
        else:
            scores['trend'] = 'neutral'

        return scores

    def calculate_sentiment_score(self,
                                  symbol: str,
                                  company_name: str = None,
                                  days_back: int = 7) -> Dict:
        """
        計算綜合輿情評分

        參數:
            symbol: 股票代碼
            company_name: 公司名稱
            days_back: 回溯天數

        返回:
            綜合輿情評分（滿分10分）
        """
        print(f"\n📰 開始分析 {symbol} 的輿情...")

        # 獲取新聞
        articles = self.get_stock_news(symbol, company_name, days_back)

        # 分析情緒
        sentiment_result = self.calculate_news_sentiment_score(articles)

        # 綜合評分（情緒70% + 熱度30%）
        combined_score = (
            sentiment_result['sentiment_score'] * 0.7 +
            sentiment_result['hotness_score'] * 0.3
        )

        # 判斷輿情環境
        if combined_score >= 8:
            environment = '非常正面'
            recommendation = '輿情強勁看多，市場關注度高'
        elif combined_score >= 6:
            environment = '正面'
            recommendation = '輿情偏多，有利股價表現'
        elif combined_score >= 4:
            environment = '中性'
            recommendation = '輿情中性，關注度一般'
        elif combined_score >= 2:
            environment = '負面'
            recommendation = '輿情偏空，需注意風險'
        else:
            environment = '非常負面'
            recommendation = '輿情極度負面，建議迴避'

        result = {
            **sentiment_result,
            'combined_score': combined_score,
            'environment': environment,
            'recommendation': recommendation,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 打印摘要
        print(f"\n✅ 輿情分析完成")
        print(f"   綜合評分: {combined_score:.1f}/10")
        print(f"   輿情環境: {environment}")
        print(f"   新聞數量: {sentiment_result['news_count']}")
        print(f"   平均情緒: {sentiment_result['avg_sentiment']:.3f}")
        print(f"   正面比例: {sentiment_result['positive_ratio']:.1%}")

        return result

    def generate_sentiment_report(self, sentiment_score: Dict) -> List[str]:
        """
        生成輿情分析報告（關鍵要點）

        參數:
            sentiment_score: 輿情評分

        返回:
            關鍵要點列表
        """
        points = []

        # 新聞數量
        news_count = sentiment_score.get('news_count', 0)
        hotness = sentiment_score.get('hotness_score', 0)

        if news_count > 0:
            if hotness >= 8:
                points.append(f"🔹 新聞數量 {news_count} 條，市場關注度極高")
            elif hotness >= 5:
                points.append(f"🔹 新聞數量 {news_count} 條，市場有一定關注")
            else:
                points.append(f"🔹 新聞數量 {news_count} 條，市場關注度較低")
        else:
            points.append("🔹 近期無相關新聞，市場冷淡")

        # 情緒分析
        avg_sentiment = sentiment_score.get('avg_sentiment', 0)
        positive_ratio = sentiment_score.get('positive_ratio', 0)
        negative_ratio = sentiment_score.get('negative_ratio', 0)

        if avg_sentiment > 0.2:
            points.append(
                f"🔹 新聞情緒正面（平均{avg_sentiment:.2f}），"
                f"{positive_ratio:.0%}為正面報導"
            )
        elif avg_sentiment < -0.2:
            points.append(
                f"🔹 新聞情緒負面（平均{avg_sentiment:.2f}），"
                f"{negative_ratio:.0%}為負面報導"
            )
        else:
            points.append(
                f"🔹 新聞情緒中性（平均{avg_sentiment:.2f}），"
                "報導較為客觀"
            )

        # 綜合評估
        environment = sentiment_score.get('environment', 'unknown')
        combined = sentiment_score.get('combined_score', 0)
        points.append(
            f"🔹 輿情環境評估：{environment} ({combined:.1f}/10分)"
        )

        return points


# ========== 使用示例 ==========

def example_sentiment_analysis():
    """示例：輿情分析"""
    print("\n" + "="*80)
    print("示例：股票輿情分析")
    print("="*80)

    # 初始化分析器（需要NewsAPI密鑰）
    # 免費註冊：https://newsapi.org
    analyzer = SentimentAnalyzer(newsapi_key=None)  # 替換為你的API密鑰

    # 測試：分析AAPL的輿情
    symbol = 'AAPL'
    company_name = 'Apple'

    if analyzer.newsapi:
        sentiment_result = analyzer.calculate_sentiment_score(
            symbol=symbol,
            company_name=company_name,
            days_back=7
        )

        # 生成報告
        print(f"\n📋 {symbol} 輿情分析報告")
        print("="*80)

        report_points = analyzer.generate_sentiment_report(sentiment_result)
        for point in report_points:
            print(f"  {point}")

        print(f"\n💡 投資建議: {sentiment_result['recommendation']}")
    else:
        print("\n⚠️ 請配置NewsAPI密鑰以使用輿情分析功能")
        print("   1. 前往 https://newsapi.org 免費註冊")
        print("   2. 獲取API密鑰")
        print("   3. 在初始化時傳入: SentimentAnalyzer(newsapi_key='你的密鑰')")

    print("\n" + "="*80)


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║          AI輿情分析器 - Sentiment Analyzer                    ║
    ║              整合新聞情緒與市場熱度分析                         ║
    ╚════════════════════════════════════════════════════════════════╝

    功能:
    1. 📰 新聞獲取 - 自動抓取股票相關新聞
    2. 🤖 AI情緒分析 - VADER情緒分析引擎
    3. 📊 熱度評分 - 基於新聞數量的關注度
    4. 🎯 綜合評分 - 情緒+熱度雙維度

    數據來源: NewsAPI (免費)
    情緒引擎: VADER Sentiment Analysis
    """)

    example_sentiment_analysis()
