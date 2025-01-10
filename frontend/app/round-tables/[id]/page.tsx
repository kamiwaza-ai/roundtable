"use client";

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { RoundTable, Message, Agent } from '@/lib/api-types';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { Loader2 } from 'lucide-react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { formatDistanceStrict } from 'date-fns';

const POLLING_INTERVAL = 1000; // Poll every second

export default function RoundTableDetailPage() {
    const params = useParams();
    const { toast } = useToast();
    const [roundTable, setRoundTable] = useState<RoundTable | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [prompt, setPrompt] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isPolling, setIsPolling] = useState(false);

    const loadRoundTable = async () => {
        try {
            const tables = await api.getRoundTables();
            const table = tables.find(t => t.id === params.id);
            if (table) {
                setRoundTable(table);
                // Start polling if discussion is in progress
                setIsPolling(table.status === 'in_progress');
            }
        } catch (error) {
            console.error('Failed to load round table:', error);
            toast({
                title: "Error",
                description: "Failed to load round table",
                variant: "destructive"
            });
        }
    };

    const loadMessages = useCallback(async () => {
        try {
            const data = await api.getRoundTableMessages(params.id as string);
            setMessages(data);
        } catch (error) {
            console.error('Failed to load messages:', error);
            // Don't show error toast for no messages
            setMessages([]);
        }
    }, [params.id]);

    const loadAgents = useCallback(async () => {
        try {
            const data = await api.getAgents();
            setAgents(data);
        } catch (error) {
            console.error('Failed to load agents:', error);
            toast({
                title: "Error",
                description: "Failed to load agents",
                variant: "destructive"
            });
        }
    }, [toast]);

    // Initial load
    useEffect(() => {
        loadRoundTable();
        loadMessages();
        loadAgents();
    }, [loadMessages, loadAgents]);

    // Polling effect
    useEffect(() => {
        if (!isPolling) return;

        const pollData = async () => {
            await loadMessages();
            await loadRoundTable(); // Also check if status has changed
        };

        // Poll immediately
        pollData();

        // Set up polling interval
        const interval = setInterval(pollData, POLLING_INTERVAL);

        return () => clearInterval(interval);
    }, [isPolling, loadMessages]);

    const handleStartDiscussion = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!prompt || !roundTable) return;

        setIsLoading(true);
        try {
            // Fire and forget - don't await the response
            api.startDiscussion(roundTable.id, prompt);
            setPrompt('');
            setIsPolling(true); // Start polling immediately
        } catch (error) {
            console.error('Failed to start discussion:', error);
            toast({
                title: "Error",
                description: error instanceof Error ? error.message : "Failed to start discussion",
                variant: "destructive"
            });
        } finally {
            setIsLoading(false);
        }
    };

    const getDurationDisplay = () => {
        if (!roundTable) return '--';
        
        const start = new Date(roundTable.created_at);
        const end = roundTable.completed_at 
            ? new Date(roundTable.completed_at)
            : new Date();
            
        return formatDistanceStrict(start, end, { addSuffix: false });
    };

    if (!roundTable) {
        return <div>Loading...</div>;
    }

    return (
        <div className="container mx-auto py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">{roundTable.title}</h1>
                <p className="text-gray-600 mb-4">{roundTable.context}</p>
                <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded-full text-sm ${
                        roundTable.status === 'completed' ? 'bg-green-100 text-green-800' :
                        roundTable.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                        roundTable.status === 'paused' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                    }`}>
                        {roundTable.status}
                    </span>
                    {isPolling && (
                        <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                    )}
                </div>
            </div>

            <div className="flex gap-8 h-[calc(100vh-12rem)]">
                {/* Left Panel - Chat */}
                <div className="flex-1 max-w-[60%] overflow-y-auto pr-4">
                    {roundTable.status === 'pending' && (
                        <form onSubmit={handleStartDiscussion} className="mb-8">
                            <div className="space-y-4">
                                <div>
                                    <Label htmlFor="prompt">Discussion Prompt</Label>
                                    <Input
                                        id="prompt"
                                        value={prompt}
                                        onChange={(e) => setPrompt(e.target.value)}
                                        placeholder="Enter the discussion prompt..."
                                        required
                                    />
                                </div>
                                <Button type="submit" disabled={isLoading}>
                                    {isLoading ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                            Starting...
                                        </>
                                    ) : (
                                        'Start Discussion'
                                    )}
                                </Button>
                            </div>
                        </form>
                    )}

                    <div className="space-y-4">
                        {messages.length === 0 && isPolling && (
                            <div className="flex items-center justify-center p-8 text-gray-500">
                                <Loader2 className="mr-2 h-6 w-6 animate-spin" />
                                <span>Waiting for messages...</span>
                            </div>
                        )}
                        
                        <div className="space-y-4">
                            {messages.map((message) => {
                                const agent = agents.find(a => a.id === message.agent_id);
                                if (!agent || message.message_type === 'introduction') return null;
                                
                                return (
                                    <div key={message.id} className="flex items-start gap-4">
                                        <Avatar>
                                            <AvatarFallback className="bg-primary text-primary-foreground">
                                                {agent.name.charAt(0)}
                                            </AvatarFallback>
                                        </Avatar>
                                        <div className="flex-1">
                                            <div className="mb-1">
                                                <span className="font-semibold">{agent.name}</span>
                                                <span className="text-sm text-gray-500 ml-2">{agent.title}</span>
                                            </div>
                                            <Card>
                                                <CardContent className="p-4">
                                                    <p className="text-gray-700">{message.content}</p>
                                                </CardContent>
                                            </Card>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>

                {/* Right Panel - Human Controls */}
                <div className="w-[35%] space-y-6 sticky top-8">
                    <Card>
                        <CardContent className="p-6">
                            <h2 className="text-xl font-semibold mb-4">Human Controls</h2>
                            
                            {/* Discussion Controls */}
                            <div className="space-y-4">
                                <div>
                                    <h3 className="text-sm font-medium mb-2">Discussion Controls</h3>
                                    <div className="flex gap-2">
                                        <Button 
                                            variant={roundTable.status === 'paused' ? 'default' : 'secondary'}
                                            className="w-full"
                                        >
                                            {roundTable.status === 'paused' ? 'Resume Discussion' : 'Pause Discussion'}
                                        </Button>
                                    </div>
                                </div>

                                {/* Interjection */}
                                <div>
                                    <h3 className="text-sm font-medium mb-2">Interjection</h3>
                                    <div className="space-y-2">
                                        <Input
                                            placeholder="Type your message..."
                                            className="w-full"
                                        />
                                        <Button className="w-full">
                                            Send Message
                                        </Button>
                                    </div>
                                </div>

                                {/* Discussion Stats */}
                                <div className="pt-4 border-t">
                                    <h3 className="text-sm font-medium mb-2">Discussion Stats</h3>
                                    <div className="space-y-1 text-sm">
                                        <div className="flex justify-between">
                                            <span className="text-gray-500">Messages</span>
                                            <span className="font-medium">{messages.length}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-500">Status</span>
                                            <span className="font-medium capitalize">{roundTable.status}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-500">Duration</span>
                                            <span className="font-medium">{getDurationDisplay()}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
