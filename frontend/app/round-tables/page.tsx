"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { MultiSelect } from '@/components/ui/multi-select';
import { Textarea } from '@/components/ui/textarea';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui/dialog';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { api } from '@/lib/api';
import { Agent, RoundTable } from '@/lib/api-types';

type SortOption = 'recent' | 'status' | 'alphabetical' | 'participants';
type StatusFilter = 'all' | 'pending' | 'in_progress' | 'completed';

export default function RoundTablesPage() {
    console.log('Component rendering');
    const router = useRouter();
    const [roundTables, setRoundTables] = useState<RoundTable[]>([]);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [sortBy, setSortBy] = useState<SortOption>('recent');
    const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
    const [formData, setFormData] = useState({
        title: '',
        context: '',
    });
    const [selectedAgents, setSelectedAgents] = useState<string[]>([]);

    const loadRoundTables = async () => {
        console.log('Loading round tables...');
        try {
            const data = await api.getRoundTables();
            console.log('Round tables data received:', data);
            setRoundTables(data || []);
        } catch (error) {
            console.error('Failed to load round tables:', error);
            setRoundTables([]);
        } finally {
            setIsLoading(false);
        }
    };

    const loadAgents = async () => {
        console.log('Loading agents...');
        try {
            const data = await api.getAgents();
            console.log('Agents data received:', data);
            setAgents(data || []);
        } catch (error) {
            console.error('Failed to load agents:', error);
            setAgents([]);
        }
    };

    useEffect(() => {
        console.log('useEffect triggered');
        setIsLoading(true);
        Promise.all([loadRoundTables(), loadAgents()]).finally(() => {
            console.log('All data loaded');
            setIsLoading(false);
        });
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.createRoundTable({
                title: formData.title,
                context: formData.context,
                participant_ids: selectedAgents,
            });
            setIsOpen(false);
            loadRoundTables();
            setFormData({
                title: '',
                context: '',
            });
            setSelectedAgents([]);
        } catch (error) {
            console.error('Failed to create round table:', error);
        }
    };

    const sortRoundTables = (tables: RoundTable[]) => {
        console.log('Sorting tables:', { tables, sortBy });
        if (!tables || !Array.isArray(tables)) return [];
        return [...tables].sort((a, b) => {
            switch (sortBy) {
                case 'alphabetical':
                    return (a.title || '').localeCompare(b.title || '');
                case 'status':
                    return (a.status || '').localeCompare(b.status || '');
                case 'participants':
                    return ((b.messages?.length || 0) - (a.messages?.length || 0));
                case 'recent':
                default:
                    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
            }
        });
    };

    const filterRoundTables = (tables: RoundTable[]) => {
        console.log('Filtering tables:', { tables, statusFilter });
        if (!tables || !Array.isArray(tables)) return [];
        return tables.filter(table => {
            if (!table) return false;
            const matchesStatus = statusFilter === 'all' || table.status === statusFilter;
            return matchesStatus;
        });
    };

    const displayedRoundTables = sortRoundTables(filterRoundTables(roundTables));

    console.log('Before rendering, state:', { 
        isLoading, 
        error, 
        agentsLength: agents?.length,
        roundTablesLength: roundTables?.length,
        selectedAgentsLength: selectedAgents?.length
    });

    if (isLoading) {
        console.log('Rendering loading state');
        return (
            <div className="container mx-auto py-8">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-3xl font-bold">Round Tables</h1>
                </div>
                <div className="flex items-center justify-center min-h-[200px]">
                    <div>Loading round tables...</div>
                </div>
            </div>
        );
    }

    if (error) {
        console.log('Rendering error state');
        return (
            <div className="container mx-auto py-8">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-3xl font-bold">Round Tables</h1>
                </div>
                <div className="flex items-center justify-center min-h-[200px]">
                    <div className="text-red-500">Error: {error}</div>
                </div>
            </div>
        );
    }

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
                                <Label htmlFor="agents">Participants</Label>
                                <MultiSelect
                                    options={(agents || []).map(agent => {
                                        console.log('Mapping agent:', agent);
                                        return {
                                            value: agent.id,
                                            label: agent.name,
                                        };
                                    })}
                                    defaultValue={selectedAgents}
                                    onValueChange={(value) => {
                                        console.log('MultiSelect value changed:', value);
                                        setSelectedAgents(value);
                                    }}
                                    placeholder="Select participants..."
                                />
                            </div>
                            <Button type="submit">Create</Button>
                        </form>
                    </DialogContent>
                </Dialog>
            </div>

            <div className="mb-6 flex flex-wrap gap-4">
                <div className="flex-1 min-w-[200px]">
                    <Label>Sort by</Label>
                    <Select value={sortBy} onValueChange={(value) => setSortBy(value as SortOption)}>
                        <SelectTrigger>
                            <SelectValue placeholder="Sort by..." />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="recent">Most Recent</SelectItem>
                            <SelectItem value="status">Status</SelectItem>
                            <SelectItem value="alphabetical">Alphabetical</SelectItem>
                            <SelectItem value="participants">Number of Participants</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
                <div className="flex-1 min-w-[200px]">
                    <Label>Filter by Status</Label>
                    <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as StatusFilter)}>
                        <SelectTrigger>
                            <SelectValue placeholder="Filter by status..." />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Status</SelectItem>
                            <SelectItem value="pending">Pending</SelectItem>
                            <SelectItem value="in_progress">In Progress</SelectItem>
                            <SelectItem value="completed">Completed</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {displayedRoundTables.map((table) => (
                    <div
                        key={table.id}
                        className="bg-card text-card-foreground rounded-lg shadow-sm p-6 cursor-pointer hover:shadow-md transition-shadow"
                        onClick={() => router.push(`/round-tables/${table.id}`)}
                    >
                        <h2 className="text-xl font-semibold mb-2">{table.title}</h2>
                        <p className="text-sm text-muted-foreground mb-4">{table.context}</p>
                        <div className="flex justify-between items-center">
                            <span className={`px-2 py-1 rounded-full text-sm ${
                                table.status === 'completed' ? 'bg-green-100 text-green-800' :
                                table.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                                'bg-gray-100 text-gray-800'
                            }`}>
                                {table.status}
                            </span>
                            <span className="text-sm text-muted-foreground">
                                {table.messages?.length || 0} messages
                            </span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
