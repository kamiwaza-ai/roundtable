"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";

interface Agent {
  id: string;
  name: string;
  title: string;
  background: string;
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchAgents() {
      try {
        const res = await fetch("http://localhost:8000/api/v1/agents/", {
          method: "GET",
        });
        if (!res.ok) {
          throw new Error("Failed to fetch agents.");
        }
        const data = await res.json();
        setAgents(data);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    }

    fetchAgents();
  }, []);

  if (loading) {
    return <div>Loading Agents...</div>;
  }

  if (error) {
    return <div className="text-red-500">Error: {error}</div>;
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Agents</h1>
      <Link
        href="/agents/new"
        className={cn(
          "inline-block bg-primary text-primary-foreground px-4 py-2 rounded hover:opacity-90"
        )}
      >
        Create New Agent
      </Link>

      <ul className="mt-4 space-y-2">
        {agents.map((agent) => (
          <li
            key={agent.id}
            className="p-2 border border-border rounded hover:bg-muted"
          >
            <Link href={`/agents/${agent.id}`} className="hover:underline">
              <strong>{agent.name}</strong> – {agent.title}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
