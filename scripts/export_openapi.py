#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# Add apps/api to sys.path
root_dir = Path(__file__).resolve().parent.parent
api_dir = root_dir / "apps" / "api"
sys.path.insert(0, str(api_dir))

from app.main import app

def export_openapi():
    openapi_schema = app.openapi()
    contracts_dir = root_dir / "contracts"
    contracts_dir.mkdir(parents=True, exist_ok=True)
    out_file = contracts_dir / "openapi.json"
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    
    print(f"Exported OpenAPI spec to {out_file}")

if __name__ == "__main__":
    export_openapi()
