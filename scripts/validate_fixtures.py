#!/usr/bin/env python3
import json
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
api_dir = root_dir / "apps" / "api"
sys.path.insert(0, str(api_dir))

from app.schemas import (
    AnalysisResult,
    ReportResponse,
    CompareResult,
    ChatResponse,
)

def validate_all():
    fixtures_dir = root_dir / "contracts" / "fixtures"
    
    # 1. analysis_cafe_medium.json
    f1 = fixtures_dir / "analysis_cafe_medium.json"
    with open(f1, "r", encoding="utf-8") as f:
        data = json.load(f)
    AnalysisResult.model_validate(data)
    print(f"✓ Validated {f1.name} against AnalysisResult")

    # 2. report_blr_loc1.json
    f2 = fixtures_dir / "report_blr_loc1.json"
    with open(f2, "r", encoding="utf-8") as f:
        data = json.load(f)
    ReportResponse.model_validate(data)
    print(f"✓ Validated {f2.name} against ReportResponse")

    # 3. compare_sample.json
    f3 = fixtures_dir / "compare_sample.json"
    with open(f3, "r", encoding="utf-8") as f:
        data = json.load(f)
    CompareResult.model_validate(data)
    print(f"✓ Validated {f3.name} against CompareResult")

    # 4. chat_verified.json
    f4 = fixtures_dir / "chat_verified.json"
    with open(f4, "r", encoding="utf-8") as f:
        data = json.load(f)
    ChatResponse.model_validate(data)
    print(f"✓ Validated {f4.name} against ChatResponse")

    # 5. chat_partially_verified.json
    f5 = fixtures_dir / "chat_partially_verified.json"
    with open(f5, "r", encoding="utf-8") as f:
        data = json.load(f)
    ChatResponse.model_validate(data)
    print(f"✓ Validated {f5.name} against ChatResponse")

    # 6. chat_fallback.json
    f6 = fixtures_dir / "chat_fallback.json"
    with open(f6, "r", encoding="utf-8") as f:
        data = json.load(f)
    ChatResponse.model_validate(data)
    print(f"✓ Validated {f6.name} against ChatResponse")

    # 7. chat_refusal.json
    f7 = fixtures_dir / "chat_refusal.json"
    with open(f7, "r", encoding="utf-8") as f:
        data = json.load(f)
    ChatResponse.model_validate(data)
    print(f"✓ Validated {f7.name} against ChatResponse")

    print("\nAll fixtures validated successfully against schemas!")

if __name__ == "__main__":
    validate_all()
