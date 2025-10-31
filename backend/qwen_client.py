# backend/qwen_client.py
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

SYSTEM_PROMPT = """
You are AutoInsight, a universal data analyst. The dataset has these columns (name, dtype, sample):
{sample}

Rules:
1. ONLY use: import pandas as pd, import plotly.express as px, import numpy as np
2. NEVER use matplotlib, seaborn, or other libraries.
3. Before comparing or plotting, ensure column types are correct:
   - Convert to numeric: pd.to_numeric(df['col'], errors='coerce')
   - Convert to datetime: pd.to_datetime(df['col'], errors='coerce')
4. Use EXACT column names from the list above.
5. Output ONLY valid JSON:
{{
  "explanation": "Clear insight",
  "code": "Python code that sets 'fig' (plot) or 'result' (value)",
  "type": "plot" or "value"
}}

Example for "rows where duration > 40":
{{
  "explanation": "Found X calls longer than 40 minutes.",
  "code": "col = next((c for c in df.columns if 'duration' in c.lower() or 'minute' in c.lower()), None)\\nif col:\\n    df[col] = pd.to_numeric(df[col], errors='coerce')\\n    result = df[df[col] > 40].index.tolist()\\nelse:\\n    result = 'No duration column found'",
  "type": "value"
}}
"""

def query_qwen(user_query: str, columns: list, sample_str: str) -> dict:
    full_prompt = SYSTEM_PROMPT.format(sample=sample_str)
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "qwen/qwen-max",
                "messages": [
                    {"role": "system", "content": full_prompt},
                    {"role": "user", "content": user_query}
                ],
                "temperature": 0.2
            },
            timeout=20
        )
        raw = response.json()['choices'][0]['message']['content'].strip()
        
        # Extract JSON if wrapped
        if raw.startswith("```json"):
            raw = raw[7:].split("```")[0]
        elif raw.startswith("```"):
            raw = raw[3:].split("```")[0]
        
        return json.loads(raw)
    except Exception as e:
        return {
            "explanation": f"AI error: {str(e)}",
            "code": "",
            "type": "value"
        }