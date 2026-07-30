import Link from "next/link";
import { getCompanies, getCities, getStats } from "@/lib/db";
import "./companies.css";

export const dynamic = "force-dynamic";

interface PageProps {
  searchParams: Promise<{ search?: string; city?: string }>;
}

export default async function CompaniesPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const search = params.search || "";
  const city = params.city || "";

  const [companies, cities, stats] = await Promise.all([
    getCompanies(search, city),
    getCities(),
    getStats(),
  ]);

  return (
    <div className="container">
      <Link href="/" className="back-link">
        ← На главную
      </Link>

      <div className="header">
        <h1>Каталог компаний</h1>
        <p>Поиск по названию и фильтр по городу</p>
      </div>

      {/* Stats */}
      <div className="stats">
        <div className="stat-card">
          <div className="label">Всего компаний</div>
          <div className="value">{stats.total}</div>
        </div>
        <div className="stat-card">
          <div className="label">Средний рейтинг</div>
          <div className="value">⭐ {stats.avgRating}</div>
        </div>
        <div className="stat-card">
          <div className="label">Городов</div>
          <div className="value">{stats.citiesCount}</div>
        </div>
      </div>

      {/* Filters */}
      <form method="GET" action="/companies">
        <div className="filters">
          <input
            type="text"
            name="search"
            className="search-input"
            placeholder="🔍 Поиск по названию компании..."
            defaultValue={search}
            id="search-input"
          />
          <select name="city" className="city-select" defaultValue={city} id="city-select">
            <option value="">Все города</option>
            {cities.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <button type="submit" className="search-btn" id="search-btn">
            Найти
          </button>
        </div>
      </form>

      {/* Results */}
      <div className="results-count">
        Найдено: {companies.length} {companies.length >= 100 ? "(показаны первые 100)" : ""}
      </div>

      <div className="table-wrapper">
        {companies.length === 0 ? (
          <div className="empty">
            <div className="empty-icon">📭</div>
            <p>Ничего не найдено. Попробуйте изменить параметры поиска.</p>
          </div>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Название</th>
                  <th>Категория</th>
                  <th>Город</th>
                  <th>Рейтинг</th>
                  <th>Отзывы</th>
                  <th>Сайт</th>
                  <th>Телефон</th>
                </tr>
              </thead>
              <tbody>
                {companies.map((c) => {
                  const ratingNum = c.rating !== null ? parseFloat(String(c.rating)) : null;
                  const ratingClass = ratingNum === null || isNaN(ratingNum)
                    ? "none"
                    : ratingNum >= 4.5
                    ? "high"
                    : ratingNum >= 3.5
                    ? "mid"
                    : "low";

                  return (
                    <tr key={c.id}>
                      <td className="company-name">{c.name}</td>
                      <td><span className="badge">{c.category}</span></td>
                      <td>{c.city}</td>
                      <td>
                        <span className={`rating ${ratingClass}`}>
                          {ratingNum !== null && !isNaN(ratingNum) ? ratingNum.toFixed(1) : "—"}
                        </span>
                      </td>
                      <td>{c.reviews_count}</td>
                      <td>
                        {c.site ? (
                          <a
                            href={c.site}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="site-link"
                          >
                            {c.site.replace(/^https?:\/\//, "")}
                          </a>
                        ) : (
                          <span className="no-data">—</span>
                        )}
                      </td>
                      <td>{c.phone || <span className="no-data">—</span>}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
