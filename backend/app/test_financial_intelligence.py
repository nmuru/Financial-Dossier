from pathlib import Path
import json

from .financial_intelligence import collect_financial_intelligence


def test_collect_financial_intelligence_selects_annual_10k(tmp_path: Path):
    payload = {
        "entityName": "Example Corp",
        "cik": 123,
        "facts": {
            "us-gaap": {
                "Revenues": {
                    "label": "Revenue",
                    "units": {
                        "USD": [
                            {"fy": 2023, "fp": "FY", "form": "10-K", "frame": "CY2023", "end": "2023-12-31", "filed": "2024-02-01", "val": 100},
                            {"fy": 2023, "fp": "Q3", "form": "10-Q", "end": "2023-09-30", "filed": "2023-11-01", "val": 80},
                            {"fy": 2024, "fp": "FY", "form": "10-K", "frame": "CY2024", "end": "2024-12-31", "filed": "2025-02-01", "val": 110},
                        ]
                    }
                }
            }
        }
    }
    (tmp_path / "companyfacts.json").write_text(json.dumps(payload), encoding="utf-8")
    output = collect_financial_intelligence(tmp_path, years=2)
    assert "Example Corp" in output
    assert '"fy": 2023' in output
    assert '"value": 100' in output
    assert '"value": 80' not in output
