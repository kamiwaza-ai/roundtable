"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";

export default function NewAgentPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [title, setTitle] = useState("");
  const [background, setBackground] = useState("");
  const [model, setModel] = useState("gpt-4o-mini");
  const [temperature, setTemperature] = useState(0.7);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    const agentData = {
      name,
      title,
      background,
      agent_type: "assistant",
      llm_config: {
        model,
        temperature,
      },
      tool_config: null,
    };

    try {
      const res = await fetch("http://localhost:8000/api/v1/agents/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(agentData),
      });
      if (!res.ok) {
        throw new Error("Error creating agent.");
      }
      await res.json();
      router.push("/agents");
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-2">Create a New Agent</h2>
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 max-w-md">
        <div>
          <label className="block mb-1 font-semibold" htmlFor="agent-name">
            Agent Name
          </label>
          <input
            id="agent-name"
            className={cn(
              "w-full border border-border rounded px-2 py-1"
            )}
            value={name}
            placeholder="e.g. business_analyst"
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block mb-1 font-semibold" htmlFor="agent-title">
            Title
          </label>
          <input
            id="agent-title"
            className={cn(
              "w-full border border-border rounded px-2 py-1"
            )}
            value={title}
            placeholder="e.g. Senior Business Analyst"
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block mb-1 font-semibold" htmlFor="agent-background">
            Background
          </label>
          <textarea
            id="agent-background"
            className={cn(
              "w-full border border-border rounded px-2 py-1"
            )}
            value={background}
            placeholder="Agent's expertise, role, style..."
            onChange={(e) => setBackground(e.target.value)}
            rows={3}
            required
          />
        </div>

        <div>
          <label className="block mb-1 font-semibold">Model</label>
          <input
            className={cn(
              "w-full border border-border rounded px-2 py-1"
            )}
            value={model}
            onChange={(e) => setModel(e.target.value)}
          />
        </div>

        <div>
          <label className="block mb-1 font-semibold">Temperature</label>
          <input
            type="number"
            step="0.1"
            min="0"
            max="2"
            className={cn(
              "w-full border border-border rounded px-2 py-1"
            )}
            value={temperature}
            onChange={(e) => setTemperature(Number(e.target.value))}
          />
        </div>

        <button
          type="submit"
          className={cn(
            "bg-primary text-primary-foreground px-4 py-2 rounded hover:opacity-90"
          )}
        >
          Create Agent
        </button>
      </form>
    </div>
  );
}
