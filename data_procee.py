#!/usr/bin/env python3
import argparse
import csv
import os
import sys
from collections import defaultdict


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Build per-user metadata CSVs for a benchmarks subset (e.g., Project_CodeNet_C++1000) "
            "by joining against original Project_CodeNet/metadata."
        )
    )
    parser.add_argument(
        "dataset_dir",
        help=(
            "Path to benchmark dataset root, e.g. /data2/liyu/KT/OKT/DataCode/Project_CodeNet_C++1000"
        ),
    )
    parser.add_argument(
        "--codenet_root",
        default="/data2/liyu/KT/OKT/Project_CodeNet",
        help=(
            "Path to Project_CodeNet root that contains metadata/p*.csv (default: %(default)s)"
        ),
    )
    return parser.parse_args()


def iter_benchmark_submissions(dataset_dir: str):
    """
    Yield tuples (problem_id, submission_id) discovered in the benchmark dataset tree.
    Supports layouts:
    - <dataset_dir>/pXXXXX/sXXXXXXXXX.<ext>
    - <dataset_dir>/pXXXXX/<lang>/sXXXXXXXXX.<ext>
    """
    with os.scandir(dataset_dir) as it:
        for entry in it:
            if not entry.is_dir():
                continue
            name = entry.name
            if not (len(name) == 6 and name.startswith("p") and name[1:].isdigit()):
                continue
            problem_id = name
            problem_dir = entry.path

            # Case 1: files directly under problem_dir
            for direct_entry in os.scandir(problem_dir):
                if direct_entry.is_file():
                    fname = direct_entry.name
                    if fname.startswith("s") and "." in fname:
                        submission_id = fname.split(".", 1)[0]
                        if len(submission_id) == 10 and submission_id[1:].isdigit():
                            yield (problem_id, submission_id)

            # Case 2: language subfolders
            for lang_entry in os.scandir(problem_dir):
                if not lang_entry.is_dir():
                    continue
                for file_entry in os.scandir(lang_entry.path):
                    if not file_entry.is_file():
                        continue
                    fname = file_entry.name
                    if not (fname.startswith("s") and "." in fname):
                        continue
                    submission_id = fname.split(".", 1)[0]
                    if len(submission_id) == 10 and submission_id[1:].isdigit():
                        yield (problem_id, submission_id)


def load_problem_metadata_rows(codenet_root: str, problem_id: str, needed_submission_ids: set):
    """
    Load rows from Project_CodeNet/metadata/<problem_id>.csv for the subset of submission_ids.
    Returns (header, rows) where rows is a list of parsed lists.
    """
    meta_csv = os.path.join(codenet_root, "metadata", f"{problem_id}.csv")
    if not os.path.exists(meta_csv):
        return None, []
    header = None
    rows = []
    with open(meta_csv, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0:
                header = row
                continue
            if not row:
                continue
            if row[0] in needed_submission_ids:
                rows.append(row)
    return header, rows


def main():
    args = parse_args()
    dataset_dir = os.path.abspath(args.dataset_dir)
    codenet_root = os.path.abspath(args.codenet_root)

    if not os.path.isdir(dataset_dir):
        print(f"Dataset directory not found: {dataset_dir}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(os.path.join(codenet_root, "metadata")):
        print(f"Invalid Project_CodeNet root (missing metadata): {codenet_root}", file=sys.stderr)
        sys.exit(1)

    # Collect all (problem_id -> set(submission_id)) present in benchmark dataset
    problem_to_submissions = defaultdict(set)
    count = 0
    for problem_id, submission_id in iter_benchmark_submissions(dataset_dir):
        problem_to_submissions[problem_id].add(submission_id)
        count += 1

    if count == 0:
        print("No submissions found in dataset directory. Nothing to do.")
        return

    # Prepare output dir <dataset_dir>/metadata
    out_dir = os.path.join(dataset_dir, "metadata")
    os.makedirs(out_dir, exist_ok=True)

    # Group rows by user_id
    header_ref = None
    user_to_rows = defaultdict(list)

    for problem_id, submission_ids in problem_to_submissions.items():
        header, rows = load_problem_metadata_rows(codenet_root, problem_id, submission_ids)
        if header is None:
            print(f"Warning: missing metadata for {problem_id}; skipping.", file=sys.stderr)
            continue
        if header_ref is None:
            header_ref = header
        # Expect standard columns; user_id at index 2, date at index 3
        for row in rows:
            user_id = row[2]
            user_to_rows[user_id].append(row)

    if header_ref is None:
        print("No metadata rows resolved from Project_CodeNet. Aborting.", file=sys.stderr)
        sys.exit(1)

    # Sort and write per-user CSV
    # Column indices based on README: 0=submission_id, 3=date
    for user_id, rows in user_to_rows.items():
        try:
            rows.sort(key=lambda r: (int(r[3]), r[0]))
        except ValueError:
            rows.sort(key=lambda r: (r[3], r[0]))
        out_csv = os.path.join(out_dir, f"{user_id}.csv")
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header_ref)
            writer.writerows(rows)

    print(
        f"Wrote {len(user_to_rows)} per-user CSV files to {out_dir}. Total submissions processed: {count}."
    )


if __name__ == "__main__":
    main()


