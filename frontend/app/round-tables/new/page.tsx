"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface Agent {
  id: string;
  name: string;
  title: string;
}

export default function NewRoundTablePage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [context, setContext] = useState("");
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    // fetch agents to select from
    async function fetchAgents() {
      try {
        const res = await fetch("http://localhost:8000/api/v1/agents/");
        if (!res.ok) {
          throw new Error("Failed to fetch agents.");
        }
        const data = await res.json();
        setAgents(data);
      } catch (err) {
        console.error(err);
      }
    }
    fetchAgents();
  }, []);

  function toggleAgent(agentId: string) {
    setSelectedAgents((prev) => {
      if (prev.includes(agentId)) {
        return prev.filter((id) => id !== agentId);
      } else {
        return [...prev, agentId];
      }
    });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    const roundTableData = {
      title,
      context,
      participant_ids: selectedAgents,
      settings: {
        max_rounds: 10,
        speaker_selection_method: "auto",
        allow_repeat_speaker: true,
        send_introductions: true,
      },
    };

    try {
      const res = await fetch("http://localhost:8000/api/v1/round-tables/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(roundTableData),
      });
      if (!res.ok) {
        throw new Error("Failed to create round table.");
      }
      await res.json();
      router.push("/round-tables");
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-2">Create a New Round Table</h2>
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <form onSubmit={handleSubmit} className="space-y-4 max-w-md">
        <div>
          <label className="block mb-1 font-semibold" htmlFor="round-title">
            Title
          </label>
          <input
            id="round-title"
            className="w-full border border-border rounded px-2 py-1"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Market Entry Discussion"
            required
          />
        </div>

        <div>
          <label className="block mb-1 font-semibold" htmlFor="round-context">
            Context
          </label>
          <textarea
            id="round-context"
            className="w-full border border-border rounded px-2 py-1"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Describe the topic..."
            rows={3}
            required
          />
        </div>

        <div>
          <p className="mb-1 font-semibold">Select Participants</p>
          <div className="flex flex-col space-y-1">
            {agents.map((agent) => (
              <label key={agent.id} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  value={agent.id}
                  checked={selectedAgents.includes(agent.id)}
                  onChange={() => toggleAgent(agent.id)}
                />
                <span>{agent.name} – {agent.title}</span>
              </label>
            ))}
          </div>
        </div>

        <button
          type="submit"
          className="bg-primary text-primary-foreground px-4 py-2 rounded hover:opacity-90"
        >
          Create Round Table
        </button>
      </form>
    </div>
  );
}
