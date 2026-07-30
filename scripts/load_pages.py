#!/usr/bin/env python3
from __future__ import annotations
"""
load_pages.py — Загрузка данных из page_001.json..page_020.json в PostgreSQL.
Дедупликация по id (UPSERT), валидация полей.
"""

import json
import glob
import os
import sys
import psycopg2
from psycopg2.extras import execute_values

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://localhost:5432/polza_companies"
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def parse_all_pages(data_dir: str) -> list[dict]:
    """Прочитать все page_NNN.json и собрать items в один список."""
    pattern = os.path.join(data_dir, "page_*.json")
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"[ERROR] JSON файлы не найдены в {data_dir}")
        sys.exit(1)

    all_items = []
    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            items = data.get("items", [])
            all_items.extend(items)
            print(f"  {os.path.basename(filepath)}: {len(items)} записей")

    return all_items


def deduplicate(items: list[dict]) -> list[dict]:
    """Убрать полные дубликаты по id (оставляем первое вхождение)."""
    seen = set()
    unique = []
    dupes = 0
    for item in items:
        item_id = item["id"]
        if item_id in seen:
            dupes += 1
            continue
        seen.add(item_id)
        unique.append(item)
    if dupes:
        print(f"  Удалено дубликатов: {dupes}")
    return unique


def clean_item(item: dict) -> tuple:
    """Привести запись к кортежу для INSERT."""
    return (
        item["id"],
        (item.get("name") or "").strip(),
        (item.get("category") or "").strip(),
        (item.get("city") or "").strip(),
        (item.get("address") or "").strip(),
        item.get("rating"),         # может быть None
        item.get("reviews_count", 0) or 0,
        item.get("site") or None,   # null → None
        item.get("phone") or None,
        "json",
    )


def load_to_postgres(items: list[dict], db_url: str):
    """Загрузить записи в таблицу companies с UPSERT."""
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    rows = [clean_item(item) for item in items]

    sql = """
        INSERT INTO companies (id, name, category, city, address,
                               rating, reviews_count, site, phone, source)
        VALUES %s
        ON CONFLICT (id) DO UPDATE SET
            name          = EXCLUDED.name,
            category      = EXCLUDED.category,
            city          = EXCLUDED.city,
            address       = EXCLUDED.address,
            rating        = EXCLUDED.rating,
            reviews_count = EXCLUDED.reviews_count,
            site          = EXCLUDED.site,
            phone         = EXCLUDED.phone,
            source        = EXCLUDED.source
    """

    execute_values(cur, sql, rows, page_size=200)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM companies WHERE source = 'json'")
    count = cur.fetchone()[0]
    print(f"  Записей в таблице (source=json): {count}")

    cur.close()
    conn.close()


def main():
    print("=" * 60)
    print("Загрузка JSON → PostgreSQL")
    print("=" * 60)

    print(f"\n[1/3] Чтение JSON файлов из {DATA_DIR}")
    items = parse_all_pages(DATA_DIR)
    print(f"  Всего записей: {len(items)}")

    print("\n[2/3] Дедупликация")
    items = deduplicate(items)
    print(f"  Уникальных записей: {len(items)}")

    print(f"\n[3/3] Загрузка в PostgreSQL ({DATABASE_URL})")
    load_to_postgres(items, DATABASE_URL)

    print("\n✅ Загрузка JSON завершена успешно!")


if __name__ == "__main__":
    main()
