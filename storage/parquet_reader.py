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
