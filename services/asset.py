import pandas as pd
import yfinance as yf
import ta
from datetime import datetime, timedelta

class Asset:
    def __init__(self, asset: str, start_date: str = None, end_date: str = None):
        """
        Initialize the Asset analyzer with a specific asset ticker and optional date range.
        
        Args:
            asset (str): Asset ticker symbol
            start_date (str, optional): Start date in 'YYYY-MM-DD' format. Defaults to 1 year ago.
            end_date (str, optional): End date in 'YYYY-MM-DD' format. Defaults to today.
        """
        print(f"\nInitializing analyzer for {asset}...")
        self.asset = asset
        self.ticker = yf.Ticker(asset)
        self.sector = self.ticker.info.get('sector', 'N/A')
        
        # Set default date range if not provided
        self.end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        self.start_date = start_date or (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

    # ==========================
    # Fundamentals Section
    # ==========================
    
    def get_fundamentals(self) -> dict:
        """Fetch fundamental data for the asset."""
        print(f"Fetching fundamentals...")
        fundamentals = {
            'Trailing P/E Ratio': self.ticker.info.get('trailingPE', 'N/A'),
            'Forward P/E Ratio': self.ticker.info.get('forwardPE', 'N/A'),
            'Market Cap': self.ticker.info.get('marketCap', 'N/A'),
            'Revenue': self.ticker.info.get('totalRevenue', 'N/A'),
            'Gross Profit': self.ticker.info.get('grossProfits', 'N/A'),
            'Net Income': self.ticker.info.get('netIncomeToCommon', 'N/A'),
            'EPS': self.ticker.info.get('trailingEps', 'N/A'),
            'Dividend Yield': self.ticker.info.get('dividendYield', 'N/A'),
        }
        print("Successfully fetched fundamentals.")
        return fundamentals

    # ==========================
    # Earnings Section
    # ==========================
    
    def get_earnings(self, frequency: str = 'quarterly') -> pd.DataFrame:
        """Fetch earnings reports with specified frequency ('quarterly' or 'yearly')."""
        print(f"Fetching {frequency} earnings...")
        earnings = self.ticker.get_income_stmt(freq=frequency)
        
        if earnings.empty:
            raise ValueError(f"No earnings data available for {self.asset}.")
        
        extracted_data = {
            'Total Revenue': earnings.loc['TotalRevenue'],
            'Net Income': earnings.loc['NetIncome'],
            'Earnings Per Share (EPS)': earnings.loc['DilutedEPS'],
            'Gross Profit': earnings.loc['GrossProfit'],
            'Operating Income': earnings.loc['OperatingIncome']
        }
        return pd.DataFrame(extracted_data).reset_index()

    def get_cash_flow(self) -> pd.DataFrame:
        """Fetch cash flow statements."""
        print("Fetching cash flow...")
        cash_flow = self.ticker.cashflow
        if cash_flow.empty:
            raise ValueError(f"No cash flow data available for {self.asset}.")
        return cash_flow.reset_index()

    # ==========================
    # Quant Section
    # ==========================
    
    def get_market_data(self, interval: str = '1d', start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Fetch market data with specified interval and date range.
        
        Args:
            interval (str): Data interval (e.g., '1d', '1h')
            start_date (str, optional): Override default start date
            end_date (str, optional): Override default end date
        """
        print("Fetching market data...")
        # Use provided dates or fall back to instance defaults
        start = start_date or self.start_date
        end = end_date or self.end_date
        
        data = yf.download(
            tickers=self.asset, 
            interval=interval, 
            start=start, 
            end=end, 
            progress=False
        )
        if data.empty:
            raise ValueError(f"No data available for {self.asset}.")
        
        data = data.reset_index()
        data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        return data

    def add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to market data."""
        print("Calculating technical indicators...")
        data['rsi'] = ta.momentum.RSIIndicator(data['Close']).rsi()
        data['ema_20'] = ta.trend.EMAIndicator(data['Close'], window=20).ema_indicator()
        data['ema_50'] = ta.trend.EMAIndicator(data['Close'], window=50).ema_indicator()
        data['volatility'] = ta.volatility.AverageTrueRange(
            data['High'], data['Low'], data['Close']
        ).average_true_range()
        return data

    def get_market_data_with_indicators(
        self, 
        interval: str = '1d',
        start_date: str = None,
        end_date: str = None
    ) -> pd.DataFrame:
        """
        Fetch market data and calculate indicators in one call.
        
        Args:
            interval (str): Data interval (e.g., '1d', '1h')
            start_date (str, optional): Override default start date
            end_date (str, optional): Override default end date
        """
        data = self.get_market_data(interval, start_date, end_date)
        return self.add_technical_indicators(data)


if __name__ == "__main__":
    # Example usage
    
    # Create asset analyzer with default 1-year range
    # Or specify custom date range
    asset = Asset(
        "AAPL",
        start_date='2023-01-01',
        end_date='2024-01-01'
    )
    
    # Get fundamentals
    fundamentals = asset.get_fundamentals()
    print("\nFundamentals:", fundamentals)
    
    # Get quarterly earnings
    quarterly_earnings = asset.get_earnings('quarterly')
    print("\nQuarterly Earnings:", quarterly_earnings)
    
    # Get market data with indicators using instance date range
    market_data = asset.get_market_data_with_indicators()
    print("\nMarket Data Shape:", market_data.shape)
    
    # Or get market data for a specific date range
    custom_market_data = asset.get_market_data_with_indicators()
    print("\nCustom Period Market Data Shape:", custom_market_data.shape)