"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Agent, RoundTable, CreateRoundTableRequest } from '@/lib/api-types';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { MultiSelect } from '@/components/ui/multi-select';

export default function RoundTablesPage() {
    const [roundTables, setRoundTables] = useState<RoundTable[]>([]);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const [isDiscussOpen, setIsDiscussOpen] = useState(false);
    const [selectedRoundTable, setSelectedRoundTable] = useState<RoundTable | null>(null);
    const [discussionPrompt, setDiscussionPrompt] = useState('');
    const [formData, setFormData] = useState<CreateRoundTableRequest>({
        title: '',
        context: '',
        participant_ids: [],
    });

    useEffect(() => {
        loadRoundTables();
        loadAgents();
    }, []);

    const loadRoundTables = async () => {
        try {
            const data = await api.getRoundTables();
            setRoundTables(data);
        } catch (error) {
            console.error('Failed to load round tables:', error);
        }
    };

    const loadAgents = async () => {
        try {
            const data = await api.getAgents();
            setAgents(data);
        } catch (error) {
            console.error('Failed to load agents:', error);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.createRoundTable(formData);
            setIsOpen(false);
            loadRoundTables();
            setFormData({
                title: '',
                context: '',
                participant_ids: [],
            });
        } catch (error) {
            console.error('Failed to create round table:', error);
        }
    };

    const handleStartDiscussion = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedRoundTable) return;

        try {
            const result = await api.startDiscussion(
                selectedRoundTable.id,
                discussionPrompt
            );
            setIsDiscussOpen(false);
            loadRoundTables();
            setDiscussionPrompt('');
            setSelectedRoundTable(null);
        } catch (error) {
            console.error('Failed to start discussion:', error);
        }
    };

    return (
        <div className="container mx-auto py-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Round Tables</h1>
                <Dialog open={isOpen} onOpenChange={setIsOpen}>
                    <DialogTrigger asChild>
                        <Button>Create Round Table</Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Create New Round Table</DialogTitle>
                        </DialogHeader>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <Label htmlFor="title">Title</Label>
                                <Input
                                    id="title"
                                    value={formData.title}
                                    onChange={(e) =>
                                        setFormData({ ...formData, title: e.target.value })
                                    }
                                    required
                                />
                            </div>
                            <div>
                                <Label htmlFor="context">Context</Label>
                                <Textarea
                                    id="context"
                                    value={formData.context}
                                    onChange={(e) =>
                                        setFormData({
                                            ...formData,
                                            context: e.target.value,
                                        })
                                    }
                                    required
                                />
                            </div>
                            <div>
                                <Label>Participants</Label>
                                <MultiSelect
                                    options={agents.map((agent) => ({
                                        value: agent.id,
                                        label: agent.name,
                                    }))}
                                    value={formData.participant_ids}
                                    onChange={(values: string[]) =>
                                        setFormData({
                                            ...formData,
                                            participant_ids: values,
                                        })
                                    }
                                />
                            </div>
                            <Button type="submit">Create</Button>
                        </form>
                    </DialogContent>
                </Dialog>
            </div>

            <Dialog open={isDiscussOpen} onOpenChange={setIsDiscussOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Start Discussion</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleStartDiscussion} className="space-y-4">
                        <div>
                            <Label htmlFor="prompt">Discussion Prompt</Label>
                            <Textarea
                                id="prompt"
                                value={discussionPrompt}
                                onChange={(e) => setDiscussionPrompt(e.target.value)}
                                required
                            />
                        </div>
                        <Button type="submit">Start</Button>
                    </form>
                </DialogContent>
            </Dialog>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {roundTables.map((roundTable) => (
                    <Card key={roundTable.id}>
                        <CardHeader>
                            <CardTitle>{roundTable.title}</CardTitle>
                            <div className="text-sm text-gray-500">
                                Status: {roundTable.status}
                            </div>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm">{roundTable.context}</p>
                            {roundTable.messages && (
                                <div className="mt-2 text-sm text-gray-500">
                                    {roundTable.messages.length} messages
                                </div>
                            )}
                        </CardContent>
                        <CardFooter>
                            {roundTable.status === 'pending' && (
                                <Button
                                    onClick={() => {
                                        setSelectedRoundTable(roundTable);
                                        setIsDiscussOpen(true);
                                    }}
                                >
                                    Start Discussion
                                </Button>
                            )}
                            {roundTable.status === 'completed' && (
                                <Link href={`/round-tables/${roundTable.id}`}>
                                    <Button variant="outline">View Discussion</Button>
                                </Link>
                            )}
                        </CardFooter>
                    </Card>
                ))}
            </div>
        </div>
    );
}
