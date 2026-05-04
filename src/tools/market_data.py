# src/tools/market_data.py

import yfinance as yf
import json
import pandas as pd 
from datetime import datetime

def get_price_history(ticker: str, days: int = 30) -> str:
    """
    Args:
        ticker: Stock ticker (e.g., "AAPL").
        days: Number of days of history to fetch.
    
    Returns:
        Minified JSON string of last N days OHLCV data.
    """
    try:
        # Fetch data
        stock = yf.Ticker(ticker)
        hist = stock.history(period=f"{days}d")

        # --- Error Handling ---
        if hist.empty:
            return json.dumps({"error": f"No data found for {ticker}. Try another ticker."})
        
        # --- Processing ---
        # Convert index to string for JSON serialization
        hist.index = hist.index.strftime('%Y-%m-%d')
        data = []

        for date, row in hist.iterrows():
            data.append({
                "date": date,
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"])
            })
        
        # Add metadata
        meta = {
            "ticker": ticker,
            "days": days,
            "last_updated": datetime.now().isoformat()
        }

        # Return after the for loop
        # Return JSON string for LLM 
        return json.dumps({
            "ticker": ticker.upper(),
            "records_returned": len(data),
            "metadata": meta,
            "data": data
        })
    except Exception as e:
        return json.dumps({"error": f"API Tool execution failed: {ticker.upper()} error: {str(e)}"})

if __name__ == "__main__":
    test_ticker = "AAPL"
    test_days = 5
    
    print(f"Fetching {test_ticker} data for the past {test_days} days...")
    result = get_price_history(test_ticker, test_days)
    print(result)  