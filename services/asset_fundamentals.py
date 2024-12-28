import pandas as pd
import yfinance as yf

class FundamentalsFetcher:
    @staticmethod
    def fetch_fundamentals(asset: str) -> dict:
        """Fetch fundamental data for a given stock."""
        print(f"\nFetching fundamentals for {asset}...")
        stock = yf.Ticker(asset)
        fundamentals = {
            'Trailing P/E Ratio': stock.info.get('trailingPE', 'N/A'),
            'Forward P/E Ratio': stock.info.get('forwardPE', 'N/A'),
            'Market Cap': stock.info.get('marketCap', 'N/A'),
            'Revenue': stock.info.get('totalRevenue', 'N/A'),
            'Gross Profit': stock.info.get('grossProfits', 'N/A'),
            'Net Income': stock.info.get('netIncomeToCommon', 'N/A'),
            'EPS': stock.info.get('trailingEps', 'N/A'),
            'Dividend Yield': stock.info.get('dividendYield', 'N/A'),
        }
        print("Successfully fetched fundamentals.")
        return fundamentals