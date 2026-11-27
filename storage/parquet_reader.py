import os
import pandas as pd
import pyarrow.parquet as pq


def list_parquet_partitions(base_dir):
    # cari daftar partisi event_date sama category yg udah kebentuk di folder parquet
    dates = set()
    categories = set()
    if not os.path.isdir(base_dir):
        return [], []
    for root, dirs, files in os.walk(base_dir):
        rel = os.path.relpath(root, base_dir)
        if rel == ".":
            continue
        for part in rel.split(os.sep):
            if part.startswith("event_date="):
                dates.add(part.split("=", 1)[1])
            elif part.startswith("category="):
                categories.add(part.split("=", 1)[1])
    return sorted(dates), sorted(categories)


def read_partitioned_parquet(base_dir, event_date=None, category=None, max_rows=500):
    # baca file parquet yg cocok sama filter partisi
    if not os.path.isdir(base_dir):
        return pd.DataFrame(), 0
    frames = []
    for root, _, files in os.walk(base_dir):
        rel = os.path.relpath(root, base_dir)
        if rel == ".":
            continue
        parts = dict(p.split("=", 1) for p in rel.split(os.sep) if "=" in p)
        f_date, f_cat = parts.get("event_date"), parts.get("category")
        if event_date and event_date != "Semua" and f_date != event_date:
            continue
        if category and category != "Semua" and f_cat != category:
            continue
        for fname in files:
            if fname.endswith(".parquet") and not fname.startswith("."):
                part_df = pq.read_table(os.path.join(root, fname)).to_pandas()
                part_df["event_date"] = f_date
                part_df["category"] = f_cat
                frames.append(part_df)
    if not frames:
        return pd.DataFrame(), 0
    df = pd.concat(frames, ignore_index=True)
    return df.head(max_rows), len(frames)
