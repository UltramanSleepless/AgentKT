#!/usr/bin/env python3
import argparse
import csv
import glob
import os
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Merge all Project_CodeNet problem-level metadata CSVs into one file, "
            "sorted by user_id."
        )
    )
    parser.add_argument(
        "metadata_dir",
        nargs="?",
        default="/data2/liyu/KT/OKT/Project_CodeNet/metadata",
        help=(
            "Path to Project_CodeNet/metadata directory (default: %(default)s)"
        ),
    )
    parser.add_argument(
        "--output",
        "-o",
        default="/data2/liyu/KT/OKT/Project_CodeNet/metadata_merged.csv",
        help="Output CSV file path (default: %(default)s)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    metadata_dir = os.path.abspath(args.metadata_dir)
    out_csv = os.path.abspath(args.output)

    if not os.path.isdir(metadata_dir):
        print(f"Metadata directory not found: {metadata_dir}", file=sys.stderr)
        sys.exit(1)

    csv_paths = sorted(
        [p for p in glob.glob(os.path.join(metadata_dir, "p*.csv")) if os.path.isfile(p)]
    )
    if not csv_paths:
        print("No problem-level CSVs found to merge.")
        return

    header = None
    rows = []
    for path in csv_paths:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i == 0:
                    if header is None:
                        header = row
                    else:
                        # Basic header consistency check
                        if row != header:
                            print(
                                f"Warning: header mismatch in {path}; proceeding with first header.",
                                file=sys.stderr,
                            )
                    continue
                if row:
                    rows.append(row)

    if header is None:
        print("No header found; aborting.", file=sys.stderr)
        sys.exit(1)

    # Sort by user_id (column index 2), secondary by submission_id to stabilize
    try:
        rows.sort(key=lambda r: (r[2], r[0]))
    except IndexError:
        print("Unexpected row format; cannot sort.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print(
        f"Merged {len(csv_paths)} CSVs into {out_csv} with {len(rows)} rows, sorted by user_id."
    )


if __name__ == "__main__":
    main()


