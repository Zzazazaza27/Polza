import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export interface Company {
  id: string;
  name: string;
  category: string;
  city: string;
  address: string;
  rating: number | null;
  reviews_count: number;
  site: string | null;
  phone: string | null;
}

export async function getCompanies(
  search?: string,
  city?: string
): Promise<Company[]> {
  const conditions: string[] = [];
  const params: string[] = [];
  let idx = 1;

  if (search && search.trim()) {
    conditions.push(`name ILIKE $${idx}`);
    params.push(`%${search.trim()}%`);
    idx++;
  }

  if (city && city.trim()) {
    conditions.push(`city = $${idx}`);
    params.push(city.trim());
    idx++;
  }

  const where = conditions.length
    ? `WHERE ${conditions.join(" AND ")}`
    : "";

  const query = `
    SELECT id, name, category, city, address, rating, reviews_count, site, phone
    FROM companies
    ${where}
    ORDER BY name ASC
    LIMIT 100
  `;

  const result = await pool.query(query, params);
  return result.rows;
}

export async function getCities(): Promise<string[]> {
  const result = await pool.query(
    `SELECT DISTINCT city FROM companies ORDER BY city`
  );
  return result.rows.map((r: { city: string }) => r.city);
}

export async function getStats(): Promise<{
  total: number;
  avgRating: number;
  citiesCount: number;
}> {
  const result = await pool.query(`
    SELECT
      COUNT(*)::int AS total,
      ROUND(AVG(rating), 2) AS avg_rating,
      COUNT(DISTINCT city)::int AS cities_count
    FROM companies
  `);
  const row = result.rows[0];
  return {
    total: row.total,
    avgRating: parseFloat(row.avg_rating) || 0,
    citiesCount: row.cities_count,
  };
}

export default pool;
