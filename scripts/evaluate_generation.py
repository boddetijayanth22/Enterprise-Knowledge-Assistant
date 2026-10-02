import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1]),
)

import argparse
import json

from app.evaluation.generation_dataset import BENCHMARK
from app.evaluation.generation_evaluator import evaluate_dataset
from app.services.query_service import ask


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the generation evaluation benchmark."
    )

    parser.add_argument(
        "--owner-id",
        type=int,
        required=True,
        help="Owner ID whose documents will be evaluated.",
    )

    parser.add_argument(
        "--document",
        default="Python Programming Handbook.pdf",
        help="Document to evaluate.",
    )

    parser.add_argument(
        "--mode",
        default="hybrid_reranker",
        choices=[
            "semantic",
            "bm25",
            "hybrid",
            "hybrid_reranker",
        ],
        help="Retrieval mode.",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    result = evaluate_dataset(
        dataset=BENCHMARK,
        ask_fn=ask,
        owner_id=args.owner_id,
        documents=[args.document],
        mode=args.mode,
    )

    print("\n=== Generation Evaluation ===")
    print(f"Mode: {result['mode']}")
    print(f"Queries: {result['queries']}")
    print(f"Successful Queries: {result['successful_queries']}")
    print(f"Provider Failures: {result['provider_failures']}")
    print(
        "Evidence Coverage (successful): "
        f"{result['evidence_coverage']:.4f}"
    )
    print(
        "Source Coverage (successful): "
        f"{result['source_coverage']:.4f}"
    )

    print("\n=== Query Results ===")

    for index, item in enumerate(result["results"], start=1):
        print(f"\n[{index}] {item['question']}")
        print(f"Status: {item['status']}")

        if item["status"] == "SUCCESS":
            print(
                f"Evidence Coverage: "
                f"{item['evidence_coverage']:.4f}"
            )
            print(
                f"Source Coverage: "
                f"{item['source_coverage']:.4f}"
            )
        else:
            print("Evidence Coverage: N/A")
            print("Source Coverage: N/A")
            print(f"Sources: {item['sources']}")

    print("\n=== JSON Result ===")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()