from typing import Dict, List
from datetime import datetime, timedelta
from asset import Asset
import pandas as pd

class Market:
    def __init__(self, start_date: str = None, end_date: str = None):
        """
        Initialize the Market analyzer.
        
        Args:
            start_date (str, optional): Start date in 'YYYY-MM-DD' format. Defaults to 1 year ago.
            end_date (str, optional): End date in 'YYYY-MM-DD' format. Defaults to today.
        """
        print("\nInitializing Market analyzer...")
        
        # Set default date range if not provided
        self.end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        self.start_date = start_date or (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # Major indices and ETFs to track
        self.market_indicators = {
            'indices': {
                'S&P 500': '^GSPC',
                'Nasdaq 100': '^NDX',
                'Dow Jones': '^DJI'
            },
            'etfs': {
                'SPY': 'SPY',    # S&P 500 ETF
                'QQQ': 'QQQ',    # Nasdaq 100 ETF
                'DIA': 'DIA',    # Dow Jones ETF
                'VIX': '^VIX',   # Volatility Index
                'TLT': 'TLT'     # 20+ Year Treasury Bond ETF
            },
            'bonds': {
                '13-Week Treasury': '^IRX',
                '5-Year Treasury': '^FVX',
                '10-Year Treasury': '^TNX',
                '30-Year Treasury': '^TYX'
            }
        }

    def get_market_trends(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Analyze trends for major indices and ETFs.
        Returns performance metrics and technical indicators as a DataFrame.
        
        Args:
            start_date (str, optional): Override default start date
            end_date (str, optional): Override default end date
        """
        # Use provided dates or fall back to instance defaults
        start = start_date or self.start_date
        end = end_date or self.end_date
        
        # Create list to store data for DataFrame
        market_data = []
        
        # Combine all symbols to analyze
        all_symbols = {
            **self.market_indicators['indices'],
            **self.market_indicators['etfs']
        }
        
        for name, symbol in all_symbols.items():
            try:
                asset = Asset(symbol)
                data = asset.get_market_data_with_indicators(
                    interval='1d',
                    start_date=start,
                    end_date=end
                )
                
                if not data.empty:
                    current_price = data['Close'].iloc[-1]
                    start_price = data['Close'].iloc[0]
                    
                    market_data.append({
                        'name': name,
                        'symbol': symbol,
                        'current_price': current_price,
                        'period_return': ((current_price - start_price) / start_price) * 100,
                        'rsi': data['rsi'].iloc[-1],
                        'ema_20': data['ema_20'].iloc[-1],
                        'ema_50': data['ema_50'].iloc[-1],
                        'volatility': data['volatility'].iloc[-1],
                        'volume': data['Volume'].iloc[-1],
                        'above_20_ema': current_price > data['ema_20'].iloc[-1],
                        'above_50_ema': current_price > data['ema_50'].iloc[-1],
                        'trend': self._determine_trend(
                            current_price, 
                            data['ema_20'].iloc[-1], 
                            data['ema_50'].iloc[-1]
                        )
                    })
            except Exception as e:
                print(f"Error analyzing {name}: {str(e)}")
        
        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(market_data)
        
        # Set name as index
        df.set_index('name', inplace=True)
        
        # Sort by period return
        df = df.sort_values('period_return', ascending=False)
        
        return df

    def get_rates_analysis(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Analyze bond yields and interest rates.
        Returns current rates and their recent trends as a DataFrame.
        
        Args:
            start_date (str, optional): Override default start date
            end_date (str, optional): Override default end date
        """
        # Use provided dates or fall back to instance defaults
        start = start_date or self.start_date
        end = end_date or self.end_date
        
        # Create list to store data for DataFrame
        rates_data = []
        
        for name, symbol in self.market_indicators['bonds'].items():
            try:
                asset = Asset(symbol)
                data = asset.get_market_data_with_indicators(
                    interval='1d',
                    start_date=start,
                    end_date=end
                )
                
                if not data.empty:
                    current_rate = data['Close'].iloc[-1]
                    week_ago_rate = data['Close'].iloc[-5] if len(data) >= 5 else data['Close'].iloc[0]
                    month_ago_rate = data['Close'].iloc[0]
                    
                    rates_data.append({
                        'name': name,
                        'symbol': symbol,
                        'current_rate': current_rate,
                        'weekly_change': current_rate - week_ago_rate,
                        'monthly_change': current_rate - month_ago_rate,
                        'trend': 'Rising' if current_rate > week_ago_rate else 'Falling',
                        'rsi': data['rsi'].iloc[-1],
                        'volatility': data['volatility'].iloc[-1]
                    })
            except Exception as e:
                print(f"Error analyzing {name}: {str(e)}")
        
        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(rates_data)
        
        # Set name as index
        df.set_index('name', inplace=True)
        
        # Sort by current rate
        df = df.sort_values('current_rate', ascending=False)
        
        return df

    def _determine_trend(self, price: float, ema20: float, ema50: float) -> str:
        """Determine trend based on price and EMAs."""
        if price > ema20 > ema50:
            return "Strong Uptrend"
        elif price > ema20:
            return "Uptrend"
        elif price < ema20 < ema50:
            return "Strong Downtrend"
        else:
            return "Downtrend"

    def get_yield_curve(self) -> Dict:
        """
        Analyze the yield curve and check for inversions.
        Returns the current yield curve and inversion status.
        """
        yields = {}
        try:
            # Get current yields using Asset class
            yields = {
                '13W': Asset('^IRX').get_market_data_with_indicators(
                    interval='1d',
                    start_date=datetime.now().strftime('%Y-%m-%d'),
                    end_date=datetime.now().strftime('%Y-%m-%d')
                )['Close'].iloc[-1],
                '5Y': Asset('^FVX').get_market_data_with_indicators(
                    interval='1d',
                    start_date=datetime.now().strftime('%Y-%m-%d'),
                    end_date=datetime.now().strftime('%Y-%m-%d')
                )['Close'].iloc[-1],
                '10Y': Asset('^TNX').get_market_data_with_indicators(
                    interval='1d',
                    start_date=datetime.now().strftime('%Y-%m-%d'),
                    end_date=datetime.now().strftime('%Y-%m-%d')
                )['Close'].iloc[-1],
                '30Y': Asset('^TYX').get_market_data_with_indicators(
                    interval='1d',
                    start_date=datetime.now().strftime('%Y-%m-%d'),
                    end_date=datetime.now().strftime('%Y-%m-%d')
                )['Close'].iloc[-1]
            }
            
            # Check for inversions
            inversions = {
                '10Y-2Y': yields['10Y'] - yields['5Y'],
                '30Y-10Y': yields['30Y'] - yields['10Y']
            }
            
            return {
                'yields': yields,
                'inversions': inversions,
                'is_inverted': any(spread < 0 for spread in inversions.values())
            }
        except Exception as e:
            print(f"Error analyzing yield curve: {str(e)}")
            return {}


if __name__ == "__main__":

    # Create market analyzer with default 1-year range
    # Or specify custom date range
    market = Market(
        start_date='2023-01-01',
        end_date='2024-12-30'
    )
    
    # Get market trends using instance date range
    trends = market.get_market_trends()
    print("\nMarket Trends:")
    print(trends)
        
    # Get rates analysis
    rates = market.get_rates_analysis()
    print("\nRates Analysis:")
    print(rates)
