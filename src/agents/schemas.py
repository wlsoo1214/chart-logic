# src/agents/schemas.py
# data structure template for AI's Output. 

from pydantic import BaseModel, Field
from typing import List, Literal

class PriceLevel(BaseModel):
    price: float = Field(description="The price level")
    type: Literal["support", "resistance", "box_top", "box_bottom"]

class TradeSignal(BaseModel):
    ticker: str = Field(description="The stock ticker symbol")
    trend: Literal["BULLISH", "BEARISH", "SIDEWAYS"] = Field(description="Overall technical trend")
    confidence: float = Field(description="Confidence score from 0.0 to 1.0")
    key_levels: List[PriceLevel] = Field(description="Important price levels identified")
    reasoning: str = Field(description="A concise 2-sentence explanation of the technical setup")