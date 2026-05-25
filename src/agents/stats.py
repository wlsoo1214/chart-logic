# src/core/stats.py
import sqlite3
import json
import time
from pathlib import Path
from dataclasses import dataclass

DB_PATH = Path(__file__).parent.parent.parent / "data" / "traces.db"

@dataclass
class UsageMetrics:
    prompt_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0

class TokenStats:
    RATE_IN = 0.075 / 1_000_000
    RATE_OUT = 0.30 / 1_000_000

    def __init__(self, ticker: str = "UNKNOWN"):
        self.ticker = ticker
        self.metrics = UsageMetrics()
        self.start_time = time.time()
        self.tool_used = "None"
        DB_PATH.parent.mkdir(exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(str(DB_PATH)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ticker TEXT,
                    tool_used TEXT,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    total_tokens INTEGER,
                    cost_usd REAL,
                    latency_sec REAL,
                    raw_output TEXT
                )
            """)

    def update(self, metadata):
        if not metadata: return
        p_count = metadata.prompt_token_count
        o_count = metadata.candidates_token_count
        self.metrics.prompt_tokens += p_count
        self.metrics.output_tokens += o_count
        self.metrics.total_tokens += (p_count + o_count)
        self.metrics.estimated_cost_usd += (p_count * self.RATE_IN) + (o_count * self.RATE_OUT)

    def save_trace(self, raw_output: str):
        latency = time.time() - self.start_time
        with sqlite3.connect(str(DB_PATH)) as conn:
            conn.execute("""
                INSERT INTO executions (ticker, tool_used, input_tokens, output_tokens, total_tokens, cost_usd, latency_sec, raw_output)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.ticker, self.tool_used, self.metrics.prompt_tokens, 
                self.metrics.output_tokens, self.metrics.total_tokens, 
                self.metrics.estimated_cost_usd, round(latency, 2), raw_output
            ))

    def get_summary(self):
        return {
            "input": self.metrics.prompt_tokens,
            "output": self.metrics.output_tokens,
            "total": self.metrics.total_tokens,
            "cost": f"${self.metrics.estimated_cost_usd:.6f}"
        }