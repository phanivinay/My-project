# utils/safe_executor.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def execute_code(code: str, df: pd.DataFrame):
    local_vars = {
        "df": df.copy(),
        "pd": pd,
        "px": px,
        "go": go,
        "np": np,
        "fig": None,
        "result": None
    }

    restricted_globals = {
        "__builtins__": {
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "range": range,
            "enumerate": enumerate,
            "zip": zip,
            "ValueError": ValueError,
            "TypeError": TypeError,
        }
    }

    try:
        exec(code, restricted_globals, local_vars)
        
        if local_vars.get("fig") is not None:
            return local_vars["fig"], "plot"
        
        result = local_vars.get("result")
        if result is not None:
            # If result is a list of dicts → tabular
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                return pd.DataFrame(result), "table"
            else:
                return result, "value"
        else:
            return "Code ran but produced no output.", "value"
            
    except TypeError as e:
        if "'>' not supported between" in str(e):
            return "⚠️ Type error: Column appears to be text. Ensure it's numeric (e.g., 'Call Duration (Minutes)').", "value"
        else:
            return f"Type error: {str(e)}", "value"
    except Exception as e:
        return f"Execution failed: {type(e).__name__}: {str(e)}", "value"