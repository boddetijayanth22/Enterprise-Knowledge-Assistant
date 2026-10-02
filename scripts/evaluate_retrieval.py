import argparse
import json

from app.evaluation.benchmark_dataset import BENCHMARK
from app.evaluation.retrieval_evaluator import evaluate_dataset


MODES = [
    "semantic",
    "bm25",
    "hybrid",
    "hybrid_reranker",
]


def main():
    parser = argparse.ArgumentParser(
        description="Run retrieval evaluation benchmark."
    )

    parser.add_argument(
        "--owner-id",
        type=int,
        required=True,
        help="Owner ID of the user who uploaded the benchmark document.",
    )

    parser.add_argument(
        "--document",
        default="Python Programming Handbook.pdf",
        help="Benchmark PDF filename.",
    )

    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Top-K retrieval depth.",
    )

    args = parser.parse_args()

    results = []

    for mode in MODES:
        print(f"\nRunning evaluation: {mode}")

        result = evaluate_dataset(
            dataset=BENCHMARK,
            owner_id=args.owner_id,
            documents=[args.document],
            mode=mode,
            k=args.k,
        )

        results.append(result)

        print(
            f"Precision@{args.k}: "
            f"{result['precision_at_k']:.4f}"
        )

        print(
            f"Recall@{args.k}: "
            f"{result['recall_at_k']:.4f}"
        )

        print(
            f"MRR: "
            f"{result['mrr']:.4f}"
        )

    print("\n" + "=" * 60)
    print("RETRIEVAL EVALUATION SUMMARY")
    print("=" * 60)

    print(
        json.dumps(
            results,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()