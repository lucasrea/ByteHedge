import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

from dotenv import load_dotenv
import os

# Import Agents
import yfinance as yf
import pandas as pd
import ta


# Load environment variables from .env file
load_dotenv()

# Define the tool to use the MarketData class
def fetch_market_data(asset: str, interval: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Tool for fetching market data asynchronously using yfinance.
    """
    print(f"\nFetching market data for {asset}...")  # Added logging
    try:
        # Fetch historical market data using yfinance directly
        data = yf.download(
            tickers=asset,
            interval=interval,
            start=start_date,
            end=end_date,
            progress=False
        )
        
        if data.empty:
            raise ValueError(f"No data available for {asset}.")
        
        # Reset index to make date a column
        data = data.reset_index()
   
        # Rename columns to standard names
        data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        
        print(f"Successfully fetched {len(data)} rows of data")  # Added logging
        return data
        
    except Exception as e:
        raise ValueError(f"Error in fetch_market_data: {str(e)}")

def calculate_quant_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Tool for calculating technical indicators asynchronously.

    :param data: Stock data as a pandas DataFrame
    :return: Enhanced data with indicators
    """
    print("\nCalculating technical indicators...")  # Added logging
    try:
        # Print shape and columns for debugging
        print(f"Input DataFrame shape: {data.shape}")
        print(f"Input columns: {data.columns.tolist()}")

        # Calculate technical indicators using the correct column names
        data['rsi'] = ta.momentum.RSIIndicator(data['Close']).rsi()
        print("RSI calculated")  # Progress logging
        
        data['ema_20'] = ta.trend.EMAIndicator(data['Close'], window=20).ema_indicator()
        print("EMA-20 calculated")  # Progress logging
        
        data['ema_50'] = ta.trend.EMAIndicator(data['Close'], window=50).ema_indicator()
        print("EMA-50 calculated")  # Progress logging
        
        data['volatility'] = ta.volatility.AverageTrueRange(
            data['High'], 
            data['Low'], 
            data['Close']
        ).average_true_range()
        print("Volatility calculated")  # Progress logging

        print(f"Successfully calculated all indicators. Final columns: {data.columns.tolist()}")  # Added logging
        return data

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Added error logging
        raise ValueError(f"Error in calculate_quant_indicators: {str(e)}")

async def analyze_stock(asset: str, start_date: str, end_date: str) -> None:
    """Main function to analyze a stock"""
    try:
        # Fetch and prepare data
        df = fetch_market_data(asset, "1d", start_date, end_date)
        df_with_indicators = calculate_quant_indicators(df)
        
        # Convert DataFrame to a format suitable for the agent
        data_summary = {
            'asset': asset,
            'period': f"{start_date} to {end_date}",
            'data_points': len(df),
            'latest_price': df_with_indicators['Close'].iloc[-1],
            'latest_rsi': df_with_indicators['rsi'].iloc[-1],
            'latest_ema20': df_with_indicators['ema_20'].iloc[-1],
            'latest_ema50': df_with_indicators['ema_50'].iloc[-1],
            'latest_volatility': df_with_indicators['volatility'].iloc[-1],
        }
        
        # Create analysis agent
        analyst = AssistantAgent(
            name="market_analyst",
            system_message="""You are an expert financial analyst. Analyze the provided market data and technical indicators.
            Focus on:
            1. Current market position
            2. Technical indicator signals
            3. Potential trend directions
            4. Risk assessment
            
            Provide clear, actionable insights based on the technical analysis.""",
            model_client=OpenAIChatCompletionClient(
                model="gpt-4o-mini-2024-07-18",
                api_key=os.getenv('OPENAI_API_KEY')
            )
        )
        
        # Create the analysis request
        analysis_request = f"""
        Please analyze the following market data for {asset}:
        
        Period: {data_summary['period']}
        Latest Price: ${data_summary['latest_price']:.2f}
        
        Technical Indicators:
        - RSI: {data_summary['latest_rsi']:.2f}
        - EMA20: ${data_summary['latest_ema20']:.2f}
        - EMA50: ${data_summary['latest_ema50']:.2f}
        - Volatility (ATR): {data_summary['latest_volatility']:.2f}
        
        Please provide a breif analysis (less than 200 words) including:
        1. Current market position and trend
        2. Technical signal interpretation
        3. Potential risks and opportunities
        
        End your analysis with TERMINATE
        """
        
        # Run the analysis
        stream = analyst.run_stream(task=analysis_request)
        await Console(stream)

    except Exception as e:
        print(f"Error during analysis: {str(e)}")

async def main():
    # Example usage
    await analyze_stock(
        asset="AAPL",
        start_date="2024-07-01",
        end_date="2024-12-31"
    )

if __name__ == "__main__":
    asyncio.run(main())