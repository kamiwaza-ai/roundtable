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
