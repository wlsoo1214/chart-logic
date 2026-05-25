# src/agents/analyst.py
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

from src.loader import load_prompt
from src.tools.market_data import get_price_history
from src.agents.schemas import TradeSignal
from src.agents.stats import TokenStats

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_ID = "gemini-3.5-flash"

def run_analyst(user_query: str) -> str:
    # Crude ticker extraction for telemetry labeling
    ticker = user_query.split()[-1].upper().replace("?","") if user_query else "UNKNOWN"
    stats = TokenStats(ticker=ticker)
    system_prompt = load_prompt(version="v1")
    
    tools = [types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="get_price_history",
            description="Fetch historical stock price data for technical analysis.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "ticker": {"type": "STRING", "description": "Stock ticker"},
                    "days": {"type": "INTEGER", "description": "Days of history"}
                },
                required=["ticker"]
            )
        )
    ])]

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=tools,
        temperature=0.1,
        response_mime_type="application/json",
        response_schema=TradeSignal,
    )

    chat = client.chats.create(model=MODEL_ID, config=config)
    response = chat.send_message(user_query)
    stats.update(response.usage_metadata)
    
    parts = response.candidates[0].content.parts
    for part in parts:
        if part.function_call:
            fn = part.function_call
            stats.tool_used = fn.name
            
            try:
                observation = get_price_history(fn.args["ticker"], int(fn.args.get("days", 15)))
            except Exception as e:
                observation = json.dumps({"error": str(e)})
            
            final_response = chat.send_message(
                types.Part.from_function_response(name=fn.name, response={"result": observation})
            )
            stats.update(final_response.usage_metadata)
            
            output_text = final_response.text
            stats.save_trace(output_text) # Save Trace to SQLite DB
            return output_text

    stats.save_trace(response.text)
    return response.text