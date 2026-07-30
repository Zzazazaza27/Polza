import Link from "next/link";

export default function Home() {
  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      minHeight: "100vh",
      gap: "24px",
      padding: "40px",
    }}>
      <h1 style={{
        fontSize: "2.5rem",
        fontWeight: 700,
        background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
        WebkitBackgroundClip: "text",
        WebkitTextFillColor: "transparent",
      }}>
        Polza Companies
      </h1>
      <p style={{ color: "#8b8b9e", fontSize: "1.1rem" }}>
        Каталог компаний из внутренней базы
      </p>
      <Link href="/companies" style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "8px",
        padding: "14px 32px",
        background: "linear-gradient(135deg, #6366f1, #7c3aed)",
        color: "#fff",
        borderRadius: "12px",
        fontSize: "1rem",
        fontWeight: 600,
        transition: "transform 0.2s, box-shadow 0.2s",
        boxShadow: "0 4px 20px rgba(99, 102, 241, 0.3)",
      }}>
        Открыть каталог →
      </Link>
    </div>
  );
}
