import asyncio

from services.asset_data import AssetDataProcessor
from services.asset_fundamentals import FundamentalsFetcher

from agents.analyst import AnalystAgent
from agents.manager import ManagerAgent

async def analyze_stock(asset: str, start_date: str, end_date: str) -> None:
    """Main function to analyze a stock."""
    try:
        # Fetch and prepare data
        df_with_indicators = AssetDataProcessor.fetch_and_prepare_data(asset, "1d", start_date, end_date)

        # Fetch fundamentals
        fundamentals = FundamentalsFetcher.fetch_fundamentals(asset)

        # Prepare analysis requests
        technical_request = f"""
        Please analyze the following technical data for {asset}:
        
        Technical Indicators:
        - RSI: {df_with_indicators['rsi'].iloc[-1]:.2f}
        - EMA20: ${df_with_indicators['ema_20'].iloc[-1]:.2f}
        - EMA50: ${df_with_indicators['ema_50'].iloc[-1]:.2f}
        - Volatility (ATR): {df_with_indicators['volatility'].iloc[-1]:.2f}
        
        Provide a summary of the technical analysis.
        """

        # Fundamental request
        fundamentals_summary = "\n".join([f"{key}: {value}" for key, value in fundamentals.items()])
        fundamental_request = f"""
        Please analyze the following fundamental data for {asset}:
        
        Fundamentals:
        {fundamentals_summary}
        
        Provide a summary of the fundamental analysis.
        """

        # Create analyst agents
        technical_analyst = AnalystAgent(name="Technical Analyst", focus="technical data")
        fundamental_analyst = AnalystAgent(name="Fundamental Analyst", focus="fundamental data")

        # Analyze data
        technical_summary =  await technical_analyst.analyze(technical_request)
        fundamental_summary =  await fundamental_analyst.analyze(fundamental_request)

        # Create a manager to make a decision based on the analysts' outputs
        manager = ManagerAgent(name="Market Manager")
        await manager.make_decision([technical_summary, fundamental_summary])

    except Exception as e:
        print(f"Error during analysis: {str(e)}")

async def main():
    await analyze_stock(
        asset="NVDA",
        start_date="2024-07-01",
        end_date="2024-12-27"
    )

if __name__ == "__main__":
    asyncio.run(main())