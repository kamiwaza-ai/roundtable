"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { KamiwazaModel } from "@/lib/api-types";

const AZURE_MODELS = ["gpt-4o", "gpt-4o-mini"];

export default function NewAgentPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [title, setTitle] = useState("");
  const [background, setBackground] = useState("");
  const [modelType, setModelType] = useState<"azure" | "kamiwaza">("azure");
  const [azureModel, setAzureModel] = useState("gpt-4o-mini");
  const [kamiwazaModels, setKamiwazaModels] = useState<KamiwazaModel[]>([]);
  const [selectedKamiwazaModel, setSelectedKamiwazaModel] = useState<KamiwazaModel | null>(null);
  const [temperature, setTemperature] = useState(0.7);
  const [error, setError] = useState("");

  useEffect(() => {
    // Fetch available Kamiwaza models
    async function fetchKamiwazaModels() {
      try {
        const models = await api.getKamiwazaModels();
        setKamiwazaModels(models);
        if (models.length > 0) {
          setSelectedKamiwazaModel(models[0]);
        }
      } catch (err) {
        console.error("Failed to fetch Kamiwaza models:", err);
      }
    }
    fetchKamiwazaModels();
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    const llm_config = modelType === "azure" 
      ? {
          api_type: "azure" as const,
          model: azureModel,
          api_key: process.env.NEXT_PUBLIC_AZURE_OPENAI_API_KEY || "",
          azure_endpoint: process.env.NEXT_PUBLIC_AZURE_OPENAI_ENDPOINT || "",
          temperature,
        }
      : {
          provider: "kamiwaza" as const,
          model_name: selectedKamiwazaModel?.model_name || "",
          port: selectedKamiwazaModel?.instances[0]?.port || 0,
          temperature,
        };

    const agentData = {
      name,
      title,
      background,
      agent_type: "assistant",
      llm_config,
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
          <label className="block mb-1 font-semibold">Model Type</label>
          <select
            className={cn(
              "w-full border border-border rounded px-2 py-1"
            )}
            value={modelType}
            onChange={(e) => setModelType(e.target.value as "azure" | "kamiwaza")}
          >
            <option value="azure">Azure OpenAI</option>
            <option value="kamiwaza">Kamiwaza</option>
          </select>
        </div>

        {modelType === "azure" ? (
          <div>
            <label className="block mb-1 font-semibold">Azure Model</label>
            <select
              className={cn(
                "w-full border border-border rounded px-2 py-1"
              )}
              value={azureModel}
              onChange={(e) => setAzureModel(e.target.value)}
            >
              {AZURE_MODELS.map(model => (
                <option key={model} value={model}>{model}</option>
              ))}
            </select>
          </div>
        ) : (
          <div>
            <label className="block mb-1 font-semibold">Kamiwaza Model</label>
            <select
              className={cn(
                "w-full border border-border rounded px-2 py-1"
              )}
              value={selectedKamiwazaModel?.model_name || ""}
              onChange={(e) => {
                const model = kamiwazaModels.find(m => m.model_name === e.target.value);
                setSelectedKamiwazaModel(model || null);
              }}
            >
              {kamiwazaModels.map(model => (
                <option key={model.model_name} value={model.model_name}>
                  {model.model_name}
                </option>
              ))}
            </select>
          </div>
        )}

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
