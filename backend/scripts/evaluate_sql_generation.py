from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.application.rag.evaluation import (  # noqa: E402
    evaluate_sql_generation,
    load_sql_evaluation_cases,
    sql_evaluation_summary_to_dict,
)
from app.core.container import Container  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate generated RAG SQL against expected SQL cases.",
    )
    parser.add_argument(
        "--cases",
        default=str(BACKEND_ROOT / "evaluation" / "sql_cases.json"),
        help="Path to a JSON file with SQL evaluation cases.",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write the JSON evaluation report.",
    )
    return parser.parse_args()


async def main() -> int:
    args = parse_args()
    container = Container()
    cases = load_sql_evaluation_cases(args.cases)
    rag_service = container.rag_service()
    sql_executor = container.sql_executor()

    try:
        summary = await evaluate_sql_generation(
            cases=cases,
            rag_service=rag_service,
            sql_executor=sql_executor,
        )
    finally:
        await container.rag_engine().dispose()

    report = sql_evaluation_summary_to_dict(summary)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(f"{rendered}\n", encoding="utf-8")
    print(rendered)
    return 0 if summary.success else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
