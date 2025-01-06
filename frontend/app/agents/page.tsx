"use client";

import { useState, useEffect } from 'react';
import { Agent, CreateAgentRequest } from '@/lib/api-types';
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
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function AgentsPage() {
    const [agents, setAgents] = useState<Agent[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const [formData, setFormData] = useState<CreateAgentRequest>({
        name: '',
        title: '',
        background: '',
        agent_type: 'standard',
        llm_config: {
            temperature: 0.7,
            model: 'gpt-4',
        },
    });

    useEffect(() => {
        loadAgents();
    }, []);

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
            await api.createAgent(formData);
            setIsOpen(false);
            loadAgents();
            setFormData({
                name: '',
                title: '',
                background: '',
                agent_type: 'standard',
                llm_config: {
                    temperature: 0.7,
                    model: 'gpt-4',
                },
            });
        } catch (error) {
            console.error('Failed to create agent:', error);
        }
    };

    return (
        <div className="container mx-auto py-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Agents</h1>
                <Dialog open={isOpen} onOpenChange={setIsOpen}>
                    <DialogTrigger asChild>
                        <Button>Create Agent</Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Create New Agent</DialogTitle>
                        </DialogHeader>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <Label htmlFor="name">Name</Label>
                                <Input
                                    id="name"
                                    value={formData.name}
                                    onChange={(e) =>
                                        setFormData({ ...formData, name: e.target.value })
                                    }
                                    required
                                />
                            </div>
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
                                <Label htmlFor="background">Background</Label>
                                <Textarea
                                    id="background"
                                    value={formData.background}
                                    onChange={(e) =>
                                        setFormData({
                                            ...formData,
                                            background: e.target.value,
                                        })
                                    }
                                    required
                                />
                            </div>
                            <Button type="submit">Create</Button>
                        </form>
                    </DialogContent>
                </Dialog>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {agents.map((agent) => (
                    <Card key={agent.id}>
                        <CardHeader>
                            <CardTitle>{agent.name}</CardTitle>
                            <div className="text-sm text-gray-500">{agent.title}</div>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm">{agent.background}</p>
                            <div className="mt-4 text-sm text-gray-500">
                                Type: {agent.agent_type}
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}
