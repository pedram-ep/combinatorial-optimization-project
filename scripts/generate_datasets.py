"""
Dataset generation script for the optimization problem.

Generates two JSON instances:
  - small:   n=10, m=5,  scores 0–20,  quota_factor=1
  - medium:  n=50, m=20, scores 0–50,  quota_factor=2
  - large:   n=1000, m=20, scores 0–50,  quota_factor=2

All parameters are configurable via command‑line arguments.
Output files are saved to a specified directory (default: data/generated/).
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generator import generate_instance, save_instance


def main():
    ## Command-line argument parsing (Added with aid of AI)
    parser = argparse.ArgumentParser(
        description="Generate optimization problem instances (small and medium)."
    )
    # Parameters for the small instance
    parser.add_argument(
        "--small-n", type=int, default=10,
        help="Number of applicants for the small instance."
    )
    parser.add_argument(
        "--small-m", type=int, default=5,
        help="Number of universities for the small instance."
    )
    parser.add_argument(
        "--small-score-min", type=int, default=0,
        help="Minimum score for the small instance."
    )
    parser.add_argument(
        "--small-score-max", type=int, default=20,
        help="Maximum score for the small instance."
    )
    parser.add_argument(
        "--small-quota-factor", type=float, default=1.0,
        help="Quota factor for the small instance."
    )

    # Parameters for the medium instance
    parser.add_argument(
        "--medium-n", type=int, default=50,
        help="Number of applicants for the medium instance."
    )
    parser.add_argument(
        "--medium-m", type=int, default=20,
        help="Number of universities for the medium instance."
    )
    parser.add_argument(
        "--medium-score-min", type=int, default=0,
        help="Minimum score for the medium instance."
    )
    parser.add_argument(
        "--medium-score-max", type=int, default=50,
        help="Maximum score for the medium instance."
    )
    parser.add_argument(
        "--medium-quota-factor", type=float, default=2.0,
        help="Quota factor for the medium instance."
    )

    # Parameters for the large instance
    parser.add_argument(
        "--large-n", type=int, default=1000,
        help="Number of applicants for the large instance."
    )
    parser.add_argument(
        "--large-m", type=int, default=20,
        help="Number of universities for the large instance."
    )
    parser.add_argument(
        "--large-score-min", type=int, default=0,
        help="Minimum score for the large instance."
    )
    parser.add_argument(
        "--large-score-max", type=int, default=50,
        help="Maximum score for the large instance."
    )
    parser.add_argument(
        "--large-quota-factor", type=float, default=2.0,
        help="Quota factor for the large instance."
    )


    # Common options
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility."
    )
    parser.add_argument(
        "--complete", action="store_true", default=True,
        help="If set, each applicant applies to all universities (default: True)."
    )
    parser.add_argument(
        "--no-complete", dest="complete", action="store_false",
        help="If set, applicants apply to a random subset (~60% of universities)."
    )

    args = parser.parse_args()

    # Set random seed
    random.seed(args.seed)

    # Create output directory if it doesn't exist
    output_dir = Path("data/generated")
    output_dir.mkdir(parents=True, exist_ok=True)

    small_filename = "instance_small.json"
    strict_small_filename = "instance_strict_small.json"

    medium_filename = "instance_medium.json"
    strict_medium_filename = "instance_strict_medium.json"

    large_filename = "instance_large.json"
    strict_large_filename = "instance_strict_large.json"


    # ---- Generate small instance ----
    small_data = generate_instance(
        n=args.small_n,
        m=args.small_m,
        score_range=(args.small_score_min, args.small_score_max),
        quota_factor=args.small_quota_factor,
        complete=args.complete,
        strict=False
    )
    small_path = output_dir / small_filename
    save_instance(small_data, str(small_path))
    print(f"Saved small instance to: {small_path}")

    # ---- Generate medium instance ----
    medium_data = generate_instance(
        n=args.medium_n,
        m=args.medium_m,
        score_range=(args.medium_score_min, args.medium_score_max),
        quota_factor=args.medium_quota_factor,
        complete=args.complete,
        strict=False
    )
    medium_path = output_dir / medium_filename
    save_instance(medium_data, str(medium_path))
    print(f"Saved medium instance to: {medium_path}")

    # ---- Generate large instance ----
    large_data = generate_instance(
        n=args.large_n,
        m=args.large_m,
        score_range=(args.large_score_min, args.large_score_max),
        quota_factor=args.large_quota_factor,
        complete=args.complete,
        strict=False
    )
    large_path = output_dir / large_filename
    save_instance(large_data, str(large_path))
    print(f"Saved large instance to: {large_path}")

    # ---- Generate strict small instance ----
    strict_small_data = generate_instance(
        n=args.small_n,
        m=args.small_m,
        score_range=(args.small_score_min, args.small_score_max),
        quota_factor=args.small_quota_factor,
        complete=args.complete,
        strict=True
    )
    strict_small_path = output_dir / strict_small_filename
    save_instance(strict_small_data, str(strict_small_path))
    print(f"Saved strict small instance to: {strict_small_path}")

    # ---- Generate strict medium instance ----
    medium_strict_data = generate_instance(
        n=args.medium_n,
        m=args.medium_m,
        score_range=(args.medium_score_min, args.medium_score_max),
        quota_factor=args.medium_quota_factor,
        complete=args.complete,
        strict=True
    )
    strict_medium_path = output_dir / strict_medium_filename
    save_instance(medium_strict_data, str(strict_medium_path))
    print(f"Saved strict medium instance to: {strict_medium_path}")

    # ---- Generate strict large instance ----
    large_strict_data = generate_instance(
        n=args.large_n,
        m=args.large_m,
        score_range=(args.large_score_min, args.large_score_max),
        quota_factor=args.large_quota_factor,
        complete=args.complete,
        strict=True
    )
    strict_large_path = output_dir / strict_large_filename
    save_instance(large_strict_data, str(strict_large_path))
    print(f"Saved strict large instance to: {strict_large_path}")


if __name__ == "__main__":
    import random
    main()