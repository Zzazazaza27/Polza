#!/usr/bin/env python3
from __future__ import annotations
"""
load_review.py — Загрузка review.csv в PostgreSQL.
Обнаруживает и логирует аномалии, пропускает невалидные строки.
"""

import csv
import os
import sys
import re
import psycopg2
from psycopg2.extras import execute_values

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://localhost:5432/polza_companies"
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CSV_PATH = os.path.join(DATA_DIR, "review.csv")


def normalize_city(city: str) -> str | None:
    """Попытка нормализовать город."""
    city = city.strip()

    # Mojibake — двойная кодировка UTF-8 → Windows-1251
    # РњРѕСЃРєРІР° → Москва, РЎР°РЅРєС‚-РџРµС‚РµСЂР±СѓСЂРі → Санкт-Петербург
    try:
        decoded = city.encode('latin-1').decode('utf-8')
        if decoded and not any(c in decoded for c in ['Р', 'С']):
            return decoded
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass

    # Типичные исправления
    fixes = {
        "Санкат-Петербург": "Санкт-Петербург",
        "москва": "Москва",
        "Moscow": "Москва",
        "Москва ": "Москва",
    }
    if city in fixes:
        return fixes[city]

    return city if city else None


def parse_rating(value: str) -> float | None:
    """Парсинг рейтинга с обработкой аномалий."""
    if not value or value.strip().upper() == "N/A":
        return None
    value = value.strip().replace(",", ".")
    try:
        rating = float(value)
        if rating < 0 or rating > 5:
            return None  # вне допустимого диапазона
        return rating
    except ValueError:
        return None


def parse_reviews_count(value: str) -> int | None:
    """Парсинг числа отзывов с обработкой аномалий."""
    if not value:
        return 0
    value = value.strip()
    try:
        count = int(float(value))
        if count < 0:
            return None  # отрицательное — аномалия
        return count
    except ValueError:
        return None  # текстовое значение ("много")


def load_csv(csv_path: str):
    """Прочитать CSV и вернуть (валидные_строки, аномалии)."""
    anomalies = []
    valid_rows = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    print(f"  Всего строк в CSV: {len(reader)}")

    for idx, row in enumerate(reader, start=2):
        row_id = row.get("id", "").strip()
        row_anomalies = []

        # Пустая строка
        if not row_id:
            anomalies.append(f"Строка {idx}: полностью пустая строка")
            continue

        # Проверка города
        raw_city = row.get("city", "").strip()
        city = normalize_city(raw_city)
        if raw_city != city and city:
            row_anomalies.append(f"город исправлен: '{raw_city}' → '{city}'")
        if not city or "ул." in raw_city:
            row_anomalies.append(f"невалидный город: '{raw_city}' (возможен сдвиг колонок)")
            anomalies.append(f"Строка {idx} ({row_id}): {'; '.join(row_anomalies)}")
            continue

        # Проверка рейтинга
        raw_rating = row.get("rating", "").strip()
        rating = parse_rating(raw_rating)
        if raw_rating and raw_rating.upper() != "N/A" and rating is None:
            try:
                val = float(raw_rating.replace(",", "."))
                row_anomalies.append(f"рейтинг вне диапазона [0, 5]: '{raw_rating}' ({val})")
            except ValueError:
                row_anomalies.append(f"невалидный рейтинг: '{raw_rating}'")
        if "," in raw_rating:
            row_anomalies.append(f"запятая вместо точки в рейтинге: '{raw_rating}'")

        # Проверка числа отзывов
        raw_reviews = row.get("reviews_count", "").strip()
        reviews = parse_reviews_count(raw_reviews)
        if reviews is None:
            row_anomalies.append(f"невалидное число отзывов: '{raw_reviews}'")
            reviews = 0

        # ID серии c_900xxx — подозрительные
        if row_id.startswith("c_900"):
            row_anomalies.append(f"нетипичный ID из серии c_900xxx")

        if row_anomalies:
            anomalies.append(f"Строка {idx} ({row_id}): {'; '.join(row_anomalies)}")

        valid_rows.append((
            row_id,
            (row.get("name") or "").strip(),
            (row.get("category") or "").strip(),
            city,
            (row.get("address") or "").strip(),
            rating,
            reviews,
            row.get("site", "").strip() or None,
            row.get("phone", "").strip() or None,
            "csv",
        ))

    return valid_rows, anomalies


def load_to_postgres(rows: list[tuple], db_url: str):
    """UPSERT CSV-записей в companies."""
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

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

    cur.execute("SELECT COUNT(*) FROM companies")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM companies WHERE source = 'csv'")
    csv_count = cur.fetchone()[0]
    print(f"  Записей из CSV: {csv_count}")
    print(f"  Всего в таблице: {total}")

    cur.close()
    conn.close()


def main():
    print("=" * 60)
    print("Загрузка review.csv → PostgreSQL")
    print("=" * 60)

    print(f"\n[1/3] Чтение и валидация {CSV_PATH}")
    valid_rows, anomalies = load_csv(CSV_PATH)
    print(f"  Валидных записей: {len(valid_rows)}")
    print(f"  Обнаружено аномалий: {len(anomalies)}")

    if anomalies:
        print("\n--- Обнаруженные аномалии ---")
        for a in anomalies:
            print(f"  ⚠️  {a}")

    print(f"\n[2/3] Загрузка валидных записей в PostgreSQL")
    load_to_postgres(valid_rows, DATABASE_URL)

    print(f"\n[3/3] Отчёт")
    print(f"  Всего строк в CSV: {len(valid_rows) + len([a for a in anomalies if 'пустая' in a or 'сдвиг' in a])}")
    print(f"  Загружено: {len(valid_rows)}")
    print(f"  Пропущено: {len(anomalies)}")

    print("\n✅ Загрузка CSV завершена!")


if __name__ == "__main__":
    main()
