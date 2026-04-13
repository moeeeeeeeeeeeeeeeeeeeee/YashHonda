from __future__ import annotations

import argparse

from app.seed_reference import run_seed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed vehicle variants and sample interchangeable accessories."
    )
    parser.parse_args()
    run_seed()


if __name__ == "__main__":
    main()
