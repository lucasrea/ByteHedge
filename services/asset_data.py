import pandas as pd
import yfinance as yf
import ta

class AssetDataProcessor:
    @staticmethod
    def fetch_market_data(asset: str, interval: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch market data using yfinance."""
        print(f"\nFetching market data for {asset}...")
        data = yf.download(tickers=asset, interval=interval, start=start_date, end=end_date, progress=False)
        if data.empty:
            raise ValueError(f"No data available for {asset}.")
        data = data.reset_index()
        data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        print(f"Successfully fetched {len(data)} rows of data")
        return data

    @staticmethod
    def calculate_quant_indicators(data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators."""
        print("\nCalculating technical indicators...")
        data['rsi'] = ta.momentum.RSIIndicator(data['Close']).rsi()
        data['ema_20'] = ta.trend.EMAIndicator(data['Close'], window=20).ema_indicator()
        data['ema_50'] = ta.trend.EMAIndicator(data['Close'], window=50).ema_indicator()
        data['volatility'] = ta.volatility.AverageTrueRange(data['High'], data['Low'], data['Close']).average_true_range()
        print("Successfully calculated all indicators.")
        return data

    @classmethod
    def fetch_and_prepare_data(cls, asset: str, interval: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch market data and calculate indicators in one call."""
        df = cls.fetch_market_data(asset, interval, start_date, end_date)
        df_with_indicators = cls.calculate_quant_indicators(df)
        return df_with_indicators


if __name__ == "__main__":
    pass