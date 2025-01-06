export interface Agent {
    id: string;
    name: string;
    title: string;
    background: string;
    agent_type: string;
    llm_config: any;
    tool_config?: any;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface RoundTableSettings {
    max_rounds?: number;
    speaker_selection_method?: string;
    allow_repeat_speaker?: boolean;
    send_introductions?: boolean;
    allowed_speaker_transitions?: Record<string, string[]>;
}

export interface RoundTable {
    id: string;
    title: string;
    context: string;
    status: string;
    settings: RoundTableSettings;
    created_at: string;
    completed_at?: string;
    messages?: Message[];
}

export interface Message {
    id: string;
    content: string;
    message_type: string;
    agent_id: string;
    round_table_id: string;
    created_at: string;
}

export interface CreateAgentRequest {
    name: string;
    title: string;
    background: string;
    agent_type: string;
    llm_config: any;
    tool_config?: any;
}

export interface CreateRoundTableRequest {
    title: string;
    context: string;
    participant_ids: string[];
    settings?: RoundTableSettings;
} 