# src/web/app.py
import sqlite3
import json
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from src.agents.analyst import run_analyst

app = FastAPI(title="ChartLogic Dashboard")
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
DB_PATH = BASE_DIR.parent.parent / "data" / "traces.db"

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    # Pull current traces from Database
    traces = []
    if DB_PATH.exists():
        with sqlite3.connect(str(DB_PATH)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM executions ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            for r in rows:
                trace_dict = dict(r)
                # Parse internal output fields safely for template loop usage
                try:
                    trace_dict["parsed_output"] = json.loads(trace_dict["raw_output"])
                except:
                    trace_dict["parsed_output"] = {"trend": "ERROR", "reasoning": trace_dict["raw_output"]}
                traces.append(trace_dict)
                
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"traces": traces})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_stock(request: Request, prompt: str = Form(...)):
    # Run our live structural agent flow
    run_analyst(prompt)
    # Return directly to the main layout to render the refreshed layout state
    return await dashboard(request)