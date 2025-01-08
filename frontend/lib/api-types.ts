export interface KamiwazaModelInstance {
  host_name: string;
  port: number;
  url: string;
}

export interface KamiwazaModel {
  model_name: string;
  status: string;
  instances: KamiwazaModelInstance[];
  capabilities: {
    chat_completion: boolean;
    text_completion: boolean;
    embeddings: boolean;
  };
}

export interface Agent {
  id: string;
  name: string;
  title: string;
  background: string;
  agent_type: string;
  llm_config: AzureLLMConfig | KamiwazaLLMConfig;
  tool_config?: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AzureLLMConfig {
  api_type: "azure";
  model: string;
  api_key: string;
  azure_endpoint: string;
  api_version?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface KamiwazaLLMConfig {
  provider: "kamiwaza";
  model_name: string;
  host_name?: string;
  port: number;
  temperature?: number;
  max_tokens?: number;
}

export interface AgentCreate {
  name: string;
  title: string;
  background: string;
  agent_type?: string;
  llm_config: AzureLLMConfig | KamiwazaLLMConfig;
  tool_config?: Record<string, any>;
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
    status: 'pending' | 'in_progress' | 'paused' | 'completed';
    settings: RoundTableSettings;
    messages_state?: any;
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