"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";

interface RoundTable {
  id: string;
  title: string;
  context: string;
  status: string;
}

export default function RoundTablesPage() {
  const [tables, setTables] = useState<RoundTable[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchTables() {
      try {
        const res = await fetch("http://localhost:8000/api/v1/round-tables/");
        if (!res.ok) {
          throw new Error("Failed to fetch round tables.");
        }
        const data = await res.json();
        setTables(data);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    }
    fetchTables();
  }, []);

  if (loading) {
    return <div>Loading Round Tables...</div>;
  }

  if (error) {
    return <div className="text-red-500">Error: {error}</div>;
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Round Tables</h1>
      <Link
        href="/round-tables/new"
        className="inline-block bg-primary text-primary-foreground px-4 py-2 rounded hover:opacity-90"
      >
        Create New Round Table
      </Link>

      <ul className="mt-4 space-y-2">
        {tables.map((table) => (
          <li
            key={table.id}
            className="p-2 border border-border rounded hover:bg-muted"
          >
            <Link href={`/round-tables/${table.id}`} className="hover:underline">
              <strong>{table.title}</strong> – {table.status}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
