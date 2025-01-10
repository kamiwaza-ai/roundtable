"use client";

import { useState, useEffect } from 'react';
import { Agent, CreateAgentRequest, KamiwazaModel, KamiwazaLLMConfig, AzureLLMConfig } from '@/lib/api-types';
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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const AZURE_MODELS = ["gpt-4o", "gpt-4o-mini"];

export default function AgentsPage() {
    const [agents, setAgents] = useState<Agent[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const [kamiwazaModels, setKamiwazaModels] = useState<KamiwazaModel[]>([]);
    const [formData, setFormData] = useState<CreateAgentRequest>({
        name: '',
        title: '',
        background: '',
        agent_type: 'standard',
        llm_config: {
            api_type: "azure" as const,
            model: 'gpt-4o-mini',
            api_key: process.env.NEXT_PUBLIC_AZURE_OPENAI_API_KEY || "",
            azure_endpoint: process.env.NEXT_PUBLIC_AZURE_OPENAI_ENDPOINT || "",
            temperature: 0.7,
        },
    });

    useEffect(() => {
        loadAgents();
        loadKamiwazaModels();
    }, []);

    const loadAgents = async () => {
        try {
            const data = await api.getAgents();
            setAgents(data);
        } catch (error) {
            console.error('Failed to load agents:', error);
        }
    };

    const loadKamiwazaModels = async () => {
        try {
            const models = await api.getKamiwazaModels();
            setKamiwazaModels(models);
        } catch (error) {
            console.error('Failed to load Kamiwaza models:', error);
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
                    api_type: "azure" as const,
                    model: 'gpt-4o-mini',
                    api_key: process.env.NEXT_PUBLIC_AZURE_OPENAI_API_KEY || "",
                    azure_endpoint: process.env.NEXT_PUBLIC_AZURE_OPENAI_ENDPOINT || "",
                    temperature: 0.7,
                },
            });
        } catch (error) {
            console.error('Failed to create agent:', error);
        }
    };

    const handleModelTypeChange = (type: "azure" | "kamiwaza") => {
        console.log("Changing model type to:", type);
        if (type === "azure") {
            setFormData({
                ...formData,
                llm_config: {
                    api_type: "azure" as const,
                    model: 'gpt-4o-mini',
                    api_key: process.env.NEXT_PUBLIC_AZURE_OPENAI_API_KEY || "",
                    azure_endpoint: process.env.NEXT_PUBLIC_AZURE_OPENAI_ENDPOINT || "",
                    temperature: 0.7,
                }
            });
        } else {
            const firstModel = kamiwazaModels[0];
            console.log("First Kamiwaza model:", firstModel);
            if (firstModel && firstModel.instances.length > 0) {
                const instance = firstModel.instances[0];
                setFormData({
                    ...formData,
                    llm_config: {
                        provider: "kamiwaza" as const,
                        model_name: firstModel.model_name,
                        host_name: instance.host_name,
                        port: instance.port,
                        temperature: 0.7,
                    }
                });
            }
        }
        console.log("Updated form data:", formData);
    };

    const isKamiwazaConfig = (config: AzureLLMConfig | KamiwazaLLMConfig): config is KamiwazaLLMConfig => {
        return (config as KamiwazaLLMConfig).provider === "kamiwaza";
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
                            <div>
                                <Label>Model Type</Label>
                                <Select
                                    defaultValue="azure"
                                    onValueChange={handleModelTypeChange}
                                >
                                    <SelectTrigger>
                                        <SelectValue>
                                            {isKamiwazaConfig(formData.llm_config) ? "Kamiwaza" : "Azure OpenAI"}
                                        </SelectValue>
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="azure">Azure OpenAI</SelectItem>
                                        <SelectItem value="kamiwaza">Kamiwaza</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            {!isKamiwazaConfig(formData.llm_config) ? (
                                <div>
                                    <Label>Azure Model</Label>
                                    <Select
                                        defaultValue="gpt-4o-mini"
                                        onValueChange={(value) =>
                                            setFormData({
                                                ...formData,
                                                llm_config: {
                                                    ...formData.llm_config as AzureLLMConfig,
                                                    model: value,
                                                },
                                            })
                                        }
                                    >
                                        <SelectTrigger>
                                            <SelectValue>
                                                {(formData.llm_config as AzureLLMConfig).model}
                                            </SelectValue>
                                        </SelectTrigger>
                                        <SelectContent>
                                            {AZURE_MODELS.map((model) => (
                                                <SelectItem key={model} value={model}>
                                                    {model}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                            ) : (
                                <div>
                                    <Label>Kamiwaza Model</Label>
                                    <Select
                                        defaultValue={kamiwazaModels[0]?.model_name}
                                        onValueChange={(value) => {
                                            console.log("Selected Kamiwaza model:", value);
                                            const model = kamiwazaModels.find(
                                                (m) => m.model_name === value
                                            );
                                            if (model) {
                                                setFormData({
                                                    ...formData,
                                                    llm_config: {
                                                        ...(formData.llm_config as KamiwazaLLMConfig),
                                                        model_name: value,
                                                        port: model.instances[0]?.port || 0,
                                                    },
                                                });
                                            }
                                        }}
                                    >
                                        <SelectTrigger>
                                            <SelectValue>
                                                {isKamiwazaConfig(formData.llm_config) 
                                                    ? formData.llm_config.model_name 
                                                    : kamiwazaModels[0]?.model_name}
                                            </SelectValue>
                                        </SelectTrigger>
                                        <SelectContent>
                                            {kamiwazaModels.map((model) => (
                                                <SelectItem key={model.model_name} value={model.model_name}>
                                                    {model.model_name}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                            )}

                            <div>
                                <Label>Temperature</Label>
                                <Input
                                    type="number"
                                    step="0.1"
                                    min="0"
                                    max="2"
                                    value={formData.llm_config.temperature}
                                    onChange={(e) =>
                                        setFormData({
                                            ...formData,
                                            llm_config: {
                                                ...formData.llm_config,
                                                temperature: Number(e.target.value),
                                            },
                                        })
                                    }
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
                                <div>Type: {agent.agent_type}</div>
                                <div>Model: {
                                    isKamiwazaConfig(agent.llm_config) 
                                        ? agent.llm_config.model_name 
                                        : agent.llm_config.model
                                }</div>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}
