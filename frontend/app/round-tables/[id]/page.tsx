"use client";

import React, { useEffect, useState, useCallback } from "react";
import { usePathname } from "next/navigation";
import { RoundTable, Message } from "@/lib/api-types";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Loader2 } from "lucide-react";

const POLLING_INTERVAL = 2000; // 2 seconds

export default function RoundTablePage() {
    const path = usePathname();
    const roundTableId = path.split("/").pop();

    const [roundTable, setRoundTable] = useState<RoundTable | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [discussionPrompt, setDiscussionPrompt] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [isPolling, setIsPolling] = useState(false);

    const loadRoundTable = async () => {
        if (!roundTableId) return;
        try {
            const tables = await api.getRoundTables();
            const table = tables.find((rt) => rt.id === roundTableId);
            if (!table) {
                throw new Error("Round table not found");
            }
            setRoundTable(table);
            
            // Start polling if the discussion is in progress
            if (table.status !== "completed") {
                setIsPolling(true);
            }
        } catch (error) {
            setError(error instanceof Error ? error.message : "Failed to load round table");
        } finally {
            setLoading(false);
        }
    };

    const loadMessages = useCallback(async () => {
        if (!roundTableId) return;
        try {
            const data = await api.getRoundTableMessages(roundTableId);
            setMessages(data);

            // If we have a roundTable and it's completed, stop polling
            if (roundTable?.status === "completed") {
                setIsPolling(false);
            }
        } catch (error) {
            console.error("Failed to load messages:", error);
        }
    }, [roundTableId, roundTable?.status]);

    // Initial load
    useEffect(() => {
        loadRoundTable();
    }, [roundTableId]);

    // Polling effect
    useEffect(() => {
        if (!isPolling) return;

        loadMessages();
        const interval = setInterval(async () => {
            await loadMessages();
            // Refresh round table to check status
            await loadRoundTable();
        }, POLLING_INTERVAL);

        return () => clearInterval(interval);
    }, [isPolling, loadMessages]);

    const handleStartDiscussion = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!roundTableId || !discussionPrompt) return;

        try {
            // Start the discussion
            await api.startDiscussion(roundTableId, discussionPrompt);
            setDiscussionPrompt("");
            setIsPolling(true);
        } catch (error) {
            setError(error instanceof Error ? error.message : "Failed to start discussion");
        }
    };

    if (loading) {
        return <div className="p-4">Loading Round Table...</div>;
    }

    if (error) {
        return <div className="p-4 text-red-500">Error: {error}</div>;
    }

    if (!roundTable) {
        return <div className="p-4">Round table not found</div>;
    }

    return (
        <div className="container mx-auto py-8 space-y-6">
            <div>
                <h1 className="text-3xl font-bold mb-2">{roundTable.title}</h1>
                <p className="text-gray-600 mb-4">{roundTable.context}</p>
                <div className="text-sm text-gray-500 flex items-center gap-2">
                    Status: {roundTable.status}
                    {isPolling && (
                        <Loader2 className="h-4 w-4 animate-spin" />
                    )}
                </div>
            </div>

            {roundTable.status === "pending" && (
                <div className="space-y-4">
                    <h2 className="text-xl font-semibold">Start Discussion</h2>
                    <form onSubmit={handleStartDiscussion} className="space-y-4">
                        <div>
                            <Textarea
                                value={discussionPrompt}
                                onChange={(e) => setDiscussionPrompt(e.target.value)}
                                placeholder="Enter your discussion prompt..."
                                className="min-h-[100px]"
                                required
                            />
                        </div>
                        <Button type="submit">Start Discussion</Button>
                    </form>
                </div>
            )}

            {messages.length > 0 && (
                <div className="space-y-4">
                    <h2 className="text-xl font-semibold">Discussion</h2>
                    <div className="space-y-4">
                        {messages.map((message) => (
                            <Card key={message.id}>
                                <CardContent className="pt-6">
                                    <div className="text-sm text-gray-500 mb-2">
                                        {new Date(message.created_at).toLocaleString()}
                                    </div>
                                    <div className="prose max-w-none">
                                        {message.content}
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>
            )}

            {isPolling && messages.length === 0 && (
                <div className="flex items-center justify-center p-8 text-gray-500">
                    <Loader2 className="h-6 w-6 animate-spin mr-2" />
                    <span>Starting discussion...</span>
                </div>
            )}
        </div>
    );
}
