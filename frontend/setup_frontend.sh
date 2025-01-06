#!/usr/bin/env bash

# ==============================================================================
# update_frontend.sh
#
# This script creates the basic directories, pages, and components needed
# to interface with your backend at http://localhost:8000.
# ==============================================================================
set -euo pipefail

echo "Creating directories for Agents and Round Tables..."

mkdir -p app/agents
mkdir -p app/agents/new
mkdir -p app/agents/[id]

mkdir -p app/round-tables
mkdir -p app/round-tables/new
mkdir -p app/round-tables/[id]

mkdir -p components/agents
mkdir -p components/round-tables

echo "Creating Agents listing page (app/agents/page.tsx)..."
cat << 'EOF' > app/agents/page.tsx
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
EOF

echo "Creating New Agent page (app/agents/new/page.tsx)..."
cat << 'EOF' > app/agents/new/page.tsx
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
EOF

echo "Creating Single Agent page (app/agents/[id]/page.tsx)..."
cat << 'EOF' > app/agents/[id]/page.tsx
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
        const res = await fetch(\`http://localhost:8000/api/v1/agents/\${agentId}\`);
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
      const res = await fetch(\`http://localhost:8000/api/v1/agents/\${agentId}\`, {
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
EOF

echo "Creating Round Tables listing page (app/round-tables/page.tsx)..."
cat << 'EOF' > app/round-tables/page.tsx
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
EOF

echo "Creating New Round Table page (app/round-tables/new/page.tsx)..."
cat << 'EOF' > app/round-tables/new/page.tsx
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
EOF

echo "Creating Single Round Table page (app/round-tables/[id]/page.tsx)..."
cat << 'EOF' > app/round-tables/[id]/page.tsx
"use client";

import React, { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

interface DiscussionResult {
  chat_history: string[];
  summary?: string;
}

export default function RoundTablePage() {
  const path = usePathname();
  const roundTableId = path.split("/").pop();

  const [title, setTitle] = useState("");
  const [context, setContext] = useState("");
  const [status, setStatus] = useState("");
  const [discussionPrompt, setDiscussionPrompt] = useState("");
  const [chatHistory, setChatHistory] = useState<string[]>([]);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Fetch the round table info
  useEffect(() => {
    async function fetchTable() {
      if (!roundTableId) return;
      try {
        const res = await fetch(\`http://localhost:8000/api/v1/round-tables/\`);
        if (!res.ok) {
          throw new Error("Failed to fetch round tables list.");
        }
        const data = await res.json();
        // find the matching table
        const table = data.find((rt: any) => rt.id === roundTableId);
        if (!table) {
          setError("Round table not found.");
          return;
        }
        setTitle(table.title);
        setContext(table.context);
        setStatus(table.status);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    }
    fetchTable();
  }, [roundTableId]);

  async function handleDiscuss() {
    if (!roundTableId || !discussionPrompt) return;
    setError("");
    try {
      const params = new URLSearchParams({
        discussion_prompt: discussionPrompt,
      });
      const res = await fetch(\`http://localhost:8000/api/v1/round-tables/\${roundTableId}/discuss?\${params}\`, {
        method: "POST",
      });
      if (!res.ok) {
        throw new Error("Failed to start discussion.");
      }
      const data: DiscussionResult = await res.json();
      setChatHistory(data.chat_history || []);
      setSummary(data.summary || "");
    } catch (err) {
      setError((err as Error).message);
    }
  }

  if (loading) {
    return <div>Loading Round Table...</div>;
  }

  if (error) {
    return <div className="text-red-500">Error: {error}</div>;
  }

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold">Round Table: {title}</h2>
      <p><strong>Context:</strong> {context}</p>
      <p><strong>Status:</strong> {status}</p>

      <div>
        <label className="block mb-1 font-semibold" htmlFor="discussion-prompt">
          Discussion Prompt
        </label>
        <textarea
          id="discussion-prompt"
          className="w-full border border-border rounded px-2 py-1"
          rows={3}
          value={discussionPrompt}
          onChange={(e) => setDiscussionPrompt(e.target.value)}
          placeholder="Enter your discussion prompt..."
        />
        <button
          onClick={handleDiscuss}
          className="mt-2 bg-primary text-primary-foreground px-4 py-2 rounded hover:opacity-90"
        >
          Start Discussion
        </button>
      </div>

      {chatHistory.length > 0 && (
        <div className="border-t pt-4 space-y-2">
          <h3 className="text-lg font-semibold">Chat History</h3>
          {chatHistory.map((entry, idx) => (
            <div key={idx} className="border-b border-border py-2">
              {entry}
            </div>
          ))}
          {summary && (
            <div className="bg-muted p-2 rounded">
              <strong>Summary:</strong> {summary}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
EOF

echo "Done creating base pages and components."

echo
echo "======================================================================="
echo "At this point, you can also add any ShadCN UI components you’d like."
echo
echo "For example, to add the 'chart' component from ShadCN, run:"
echo
echo "  npx shadcn@latest add chart"
echo
echo "Feel free to explore other ShadCN components by running:"
echo
echo "  npx shadcn@latest add --help"
echo
echo "======================================================================="
echo "Script complete!"
