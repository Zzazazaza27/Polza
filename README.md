# Polza Agency — Тестовое задание «Технический специалист»

## Структура проекта

```
├── schema.sql                # Схема БД PostgreSQL
├── queries.sql               # 3 аналитических SQL-запроса
├── ANOMALIES.md              # Отчёт об аномалиях в review.csv
├── docker-compose.yml        # Docker для PostgreSQL
├── .env.example              # Пример переменных окружения
├── scripts/
│   ├── load_pages.py         # Загрузка JSON → Postgres
│   └── load_review.py        # Загрузка review.csv → Postgres (с обнаружением аномалий)
├── data/                     # Исходные данные (page_001..020.json, review.csv)
└── web/                      # Next.js приложение (Task 2)
    └── src/
        ├── lib/db.ts         # Подключение к PostgreSQL
        └── app/
            ├── layout.tsx
            ├── page.tsx
            └── companies/
                ├── page.tsx      # Серверный компонент — таблица компаний
                └── companies.css
```

---

## Быстрый запуск

### Требования
- Python 3.8+
- PostgreSQL 14+ (локальный или Docker)
- Node.js 18+
- `psycopg2-binary` (`pip install psycopg2-binary`)

### 1. Поднять базу данных

**Вариант A — Docker:**
```bash
docker compose up -d
```

**Вариант B — Локальный PostgreSQL:**
```bash
createdb polza_companies
psql -d polza_companies -f schema.sql
```

### 2. Загрузить данные (Task 1)

```bash
export DATABASE_URL="postgresql://localhost:5432/polza_companies"

# Загрузка JSON (1000 компаний, дедупликация → 994 уникальных)
python3 scripts/load_pages.py

# Загрузка review.csv (207 строк, аномалии выводятся в консоль)
python3 scripts/load_review.py
```

### 3. Выполнить SQL-запросы (Task 1)

```bash
psql -d polza_companies -f queries.sql
```

### 4. Запустить веб-приложение (Task 2)

```bash
cd web
cp .env.local.example .env.local  # или создать вручную: DATABASE_URL=postgresql://localhost:5432/polza_companies
npm install
npm run dev
```

Открыть http://localhost:3000/companies

---

## Задача 1: Результаты SQL-запросов

### Топ-5 категорий по числу компаний
| Категория | Число компаний |
|-----------|---------------|
| IT-интегратор | 112 |
| Оптовая торговля | 93 |
| Рекламное агентство | 90 |
| Строительная компания | 88 |
| Юридические услуги | 72 |

### Средний рейтинг по городам (компании с 10+ отзывами)
Лидеры: Пермь (4.43), Омск (4.43), Тюмень (4.36), Сочи (4.36), Воронеж (4.32).

### Доля компаний с сайтом
Лидеры: Ресторан (85.4%), Клининг (85.0%), Производство мебели (82.7%).
Аутсайдеры: Типография (62.5%), Строительная компания (67.0%).

---

## Задача 2: Доказательство работы

### Как проверял

1. **Загрузка данных** — запустил `load_pages.py`, убедился что 994 уникальных записи загрузились (6 дублей удалено). Проверил через `psql -c "SELECT COUNT(*) FROM companies"`.
2. **Страница /companies** — открыл http://localhost:3000/companies, увидел таблицу со всеми компаниями, карточки статистики (1189 компаний, средний рейтинг, 23 города).
3. **Поиск** — ввёл "Прайм" в поле поиска, нажал "Найти" — отфильтровались компании с "Прайм" в названии.
4. **Фильтр по городу** — выбрал "Казань" в dropdown, нажал "Найти" — показались только казанские компании.
5. **Пустой результат** — ввёл "zzzzz" — появилось сообщение "Ничего не найдено".

### Что ломалось
- `rating.toFixed is not a function` — рейтинг приходил из PostgreSQL как строка (`NUMERIC`), а не как `number`. Исправил через `parseFloat(String(c.rating))`.
- Python 3.8 не поддерживает `list[dict]` синтаксис — добавил `from __future__ import annotations`.

---

## Задача 3: Аномалии в review.csv

Подробный отчёт: [ANOMALIES.md](ANOMALIES.md)

**Ключевые находки:**
- Файл назван `review.csv`, но содержит **профили компаний**, а не отзывы
- 2 города с битой кодировкой (Mojibake: UTF-8 → Windows-1251)
- Опечатки в городах ("Санкат-Петербург", "москва", "Moscow")
- Сдвиг колонок (адрес в поле города)
- Рейтинги вне диапазона: `-3`, `7.2`, `N/A`, `4,5` (запятая)
- Число отзывов: `-10`, `45.5`, `"много"`
- Подозрительные ID серии `c_900xxx`
- Пустые строки в конце файла

---

## Задача 4

См. файл `TASK4_ANSWERS.txt` (заполняется вручную).
