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
import { useRouter } from 'next/navigation';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Badge } from '@/components/ui/badge';
import { CalendarIcon, CheckCircleIcon, ClockIcon, PlayIcon } from 'lucide-react';
import { cn } from "@/lib/utils";

type SortOption = 'recent' | 'status' | 'alphabetical' | 'participants';
type StatusFilter = 'all' | 'pending' | 'in_progress' | 'completed';

export default function RoundTablesPage() {
    const router = useRouter();
    const [roundTables, setRoundTables] = useState<RoundTable[]>([]);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const [isDiscussOpen, setIsDiscussOpen] = useState(false);
    const [selectedRoundTable, setSelectedRoundTable] = useState<RoundTable | null>(null);
    const [discussionPrompt, setDiscussionPrompt] = useState('');
    const [sortBy, setSortBy] = useState<SortOption>('recent');
    const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
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
            api.startDiscussion(selectedRoundTable.id, discussionPrompt);
            
            setIsDiscussOpen(false);
            setDiscussionPrompt('');
            setSelectedRoundTable(null);
            
            router.push(`/round-tables/${selectedRoundTable.id}`);
        } catch (error) {
            console.error('Failed to start discussion:', error);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'pending':
                return 'bg-yellow-100 text-yellow-800';
            case 'in_progress':
                return 'bg-blue-100 text-blue-800';
            case 'completed':
                return 'bg-green-100 text-green-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'pending':
                return <ClockIcon className="h-4 w-4" />;
            case 'in_progress':
                return <PlayIcon className="h-4 w-4" />;
            case 'completed':
                return <CheckCircleIcon className="h-4 w-4" />;
            default:
                return null;
        }
    };

    const sortRoundTables = (tables: RoundTable[]) => {
        return [...tables].sort((a, b) => {
            switch (sortBy) {
                case 'recent':
                    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
                case 'status':
                    const statusOrder = { in_progress: 0, pending: 1, completed: 2 };
                    return (statusOrder[a.status as keyof typeof statusOrder] || 0) - 
                           (statusOrder[b.status as keyof typeof statusOrder] || 0);
                case 'alphabetical':
                    return a.title.localeCompare(b.title);
                case 'participants':
                    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
                default:
                    return 0;
            }
        });
    };

    const filterRoundTables = (tables: RoundTable[]) => {
        return tables.filter(table => {
            const matchesStatus = statusFilter === 'all' || table.status === statusFilter;
            return matchesStatus;
        });
    };

    const displayedRoundTables = sortRoundTables(filterRoundTables(roundTables));

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
                                    value={formData.participant_ids || []}
                                    onChange={(values) =>
                                        setFormData({
                                            ...formData,
                                            participant_ids: values || [],
                                        })
                                    }
                                    className="w-full"
                                    popoverContentProps={{
                                        className: "max-h-[200px] overflow-y-auto"
                                    }}
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
                {displayedRoundTables.map((roundTable) => (
                    <Card key={roundTable.id} className="flex flex-col">
                        <CardHeader>
                            <div className="flex justify-between items-start">
                                <CardTitle className="flex-1">{roundTable.title}</CardTitle>
                                <Badge 
                                    className={`ml-2 flex items-center gap-1 ${getStatusColor(roundTable.status)}`}
                                >
                                    {getStatusIcon(roundTable.status)}
                                    {roundTable.status}
                                </Badge>
                            </div>
                        </CardHeader>
                        <CardContent className="flex-1">
                            <p className="text-sm">{roundTable.context}</p>
                            <div className="mt-4 space-y-2">
                                <div className="flex items-center gap-2 text-sm text-gray-500">
                                    <CalendarIcon className="h-4 w-4" />
                                    {new Date(roundTable.created_at).toLocaleDateString()}
                                </div>
                                {roundTable.messages && (
                                    <div className="text-sm text-gray-500">
                                        {roundTable.messages.length} messages
                                    </div>
                                )}
                            </div>
                        </CardContent>
                        <CardFooter className="mt-auto">
                            {roundTable.status === 'pending' && (
                                <Button
                                    onClick={() => {
                                        setSelectedRoundTable(roundTable);
                                        setIsDiscussOpen(true);
                                    }}
                                    className="w-full"
                                >
                                    Start Discussion
                                </Button>
                            )}
                            {roundTable.status !== 'pending' && (
                                <Link href={`/round-tables/${roundTable.id}`} className="w-full">
                                    <Button variant="outline" className="w-full">
                                        View Discussion
                                    </Button>
                                </Link>
                            )}
                        </CardFooter>
                    </Card>
                ))}
            </div>
        </div>
    );
}
