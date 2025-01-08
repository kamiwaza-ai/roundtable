import { Agent, CreateAgentRequest, CreateRoundTableRequest, RoundTable, Message, KamiwazaModel } from './api-types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function fetchApi<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'An error occurred');
    }

    return response.json();
}

export const api = {
    // Agent endpoints
    getAgents: () => fetchApi<Agent[]>('/agents'),
    
    createAgent: (data: CreateAgentRequest) =>
        fetchApi<Agent>('/agents', {
            method: 'POST',
            body: JSON.stringify(data),
        }),

    // Round Table endpoints
    getRoundTables: () => fetchApi<RoundTable[]>('/round-tables'),
    
    createRoundTable: (data: CreateRoundTableRequest) =>
        fetchApi<RoundTable>('/round-tables', {
            method: 'POST',
            body: JSON.stringify(data),
        }),
    
    startDiscussion: (roundTableId: string, prompt: string) =>
        fetchApi<{ chat_history: any[], summary: string | null }>(
            `/round-tables/${roundTableId}/discuss`,
            {
                method: 'POST',
                body: JSON.stringify({ discussion_prompt: prompt })
            }
        ),
    
    pauseDiscussion: (roundTableId: string) =>
        fetchApi<{ status: string, round_table_id: string, message_count: number }>(
            `/round-tables/${roundTableId}/pause`,
            {
                method: 'POST'
            }
        ),
    
    resumeDiscussion: (roundTableId: string) =>
        fetchApi<{ status: string, round_table_id: string, chat_history: any[] }>(
            `/round-tables/${roundTableId}/resume`,
            {
                method: 'POST'
            }
        ),
    
    getRoundTableMessages: (roundTableId: string) =>
        fetchApi<Message[]>(`/messages/round-table/${roundTableId}`),

    getKamiwazaModels: async (): Promise<KamiwazaModel[]> => {
        const response = await fetch(`${API_BASE}/kamiwaza/models`);
        if (!response.ok) {
            throw new Error("Failed to fetch Kamiwaza models");
        }
        return response.json();
    },
}; 