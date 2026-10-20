"""Generate figures from the included processed data."""

import argparse
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("names", nargs="*")
    args = parser.parse_args()
    names = args.names or [path.stem for path in sorted((ROOT / "plots").glob("f*.py"))]
    failures = []
    for name in names:
        try:
            importlib.import_module("plots." + name).main()
            print("ok", name, flush=True)
        except Exception as error:
            failures.append(name)
            print("failed", name, str(error), flush=True)
        finally:
            import matplotlib.pyplot as plt

            plt.close("all")
    if failures:
        raise SystemExit("Failed figures: " + ", ".join(failures))


if __name__ == "__main__":
    main()
