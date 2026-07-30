-- ============================================================
-- schema.sql — Polza Agency: Companies Database Schema
-- ============================================================

DROP TABLE IF EXISTS companies CASCADE;

CREATE TABLE companies (
    id              VARCHAR(20)   PRIMARY KEY,
    name            VARCHAR(255)  NOT NULL,
    category        VARCHAR(100)  NOT NULL,
    city            VARCHAR(100)  NOT NULL,
    address         TEXT          NOT NULL DEFAULT '',
    rating          NUMERIC(3, 1) CHECK (rating >= 0 AND rating <= 5),
    reviews_count   INTEGER       NOT NULL DEFAULT 0 CHECK (reviews_count >= 0),
    site            TEXT,
    phone           VARCHAR(50),
    source          VARCHAR(10)   NOT NULL DEFAULT 'json',   -- 'json' or 'csv'
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ============================================================
-- Indexes for analytical queries and search
-- ============================================================

-- Task 1 Query 1: top categories by company count
CREATE INDEX idx_companies_category ON companies (category);

-- Task 1 Query 2: avg rating by city with reviews >= 10
CREATE INDEX idx_companies_city ON companies (city);
CREATE INDEX idx_companies_reviews_count ON companies (reviews_count);

-- Task 1 Query 3: share of companies with website by category
CREATE INDEX idx_companies_category_site ON companies (category, site);

-- Task 2: search by name (trigram or ILIKE)
CREATE INDEX idx_companies_name ON companies (name);

-- Combined filter for /companies page
CREATE INDEX idx_companies_city_name ON companies (city, name);

COMMENT ON TABLE companies IS 'Company directory from Polza internal API export';
COMMENT ON COLUMN companies.source IS 'Data origin: json (page_NNN.json) or csv (review.csv)';
