"use client";

import React, { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";

interface Agent {
  id: string;
  name: string;
  title: string;
  background: string;
}

export default function AgentDetailsPage() {
  const router = useRouter();
  const path = usePathname(); 
  const agentId = path.split("/").pop();
  
  const [agent, setAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchAgent() {
      if (!agentId) return;
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/agents/${agentId}`);
        if (!res.ok) {
          throw new Error("Failed to fetch the agent.");
        }
        const data = await res.json();
        setAgent(data);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    }
    fetchAgent();
  }, [agentId]);

  async function handleDelete() {
    if (!agentId) return;
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/agents/${agentId}`, {
        method: "DELETE",
      });
      if (!res.ok) {
        throw new Error("Failed to delete the agent.");
      }
      router.push("/agents");
    } catch (err) {
      setError((err as Error).message);
    }
  }

  if (loading) {
    return <div>Loading Agent...</div>;
  }

  if (error) {
    return <div className="text-red-500">Error: {error}</div>;
  }

  if (!agent) {
    return <div>Agent not found.</div>;
  }

  return (
    <div className="p-4 space-y-2">
      <h2 className="text-xl font-semibold">Agent Details</h2>
      <p><strong>ID:</strong> {agent.id}</p>
      <p><strong>Name:</strong> {agent.name}</p>
      <p><strong>Title:</strong> {agent.title}</p>
      <p><strong>Background:</strong> {agent.background}</p>

      <div className="flex gap-4 mt-4">
        <button
          onClick={handleDelete}
          className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
        >
          Delete
        </button>
      </div>
    </div>
  );
}
