#!/usr/bin/env python3
import argparse
import csv
import glob
import os
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Extract per-user CSVs from Project_CodeNet problem-level metadata files."
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
        "--output_dir",
        "-o",
        default="/data2/liyu/KT/OKT/Project_CodeNet/userdata",
        help="Output directory for per-user CSVs (default: %(default)s)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    metadata_dir = os.path.abspath(args.metadata_dir)
    out_dir = os.path.abspath(args.output_dir)

    if not os.path.isdir(metadata_dir):
        print(f"Metadata directory not found: {metadata_dir}", file=sys.stderr)
        sys.exit(1)

    csv_paths = sorted(
        [p for p in glob.glob(os.path.join(metadata_dir, "p*.csv")) if os.path.isfile(p)]
    )
    if not csv_paths:
        print("No problem-level CSVs found to extract.")
        return

    header = None
    user_to_rows = {}
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
                if not row:
                    continue
                if len(row) < 3:
                    continue
                user_id = row[2]
                user_to_rows.setdefault(user_id, []).append(row)

    if header is None:
        print("No header found; aborting.", file=sys.stderr)
        sys.exit(1)

    # Ensure output directory
    os.makedirs(out_dir, exist_ok=True)

    # For each user, sort rows by date then submission_id and write <user_id>.csv
    written = 0
    for user_id, rows in user_to_rows.items():
        try:
            rows.sort(key=lambda r: (int(r[3]), r[0]))  # date, submission_id
        except Exception:
            rows.sort(key=lambda r: (r[3], r[0]))
        out_path = os.path.join(out_dir, f"{user_id}.csv")
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
        written += 1

    print(
        f"Wrote {written} per-user CSV files to {out_dir} from {len(csv_paths)} problem CSVs."
    )


if __name__ == "__main__":
    main()


