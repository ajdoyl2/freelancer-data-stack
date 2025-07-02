-- AI Agent Memory System Schema
-- Uses DuckDB for high-performance analytics on memory data

-- Conversations table - tracks agent sessions
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid(),
    session_id VARCHAR NOT NULL,
    agent_name VARCHAR NOT NULL,
    user_id VARCHAR DEFAULT 'default_user',
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    context_summary TEXT,
    tags VARCHAR[],
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages table - individual conversation messages
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid(),
    conversation_id UUID NOT NULL,
    role VARCHAR NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tokens_used INTEGER,
    reasoning_trace TEXT,
    tool_calls JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- Memory fragments - extracted knowledge and patterns
CREATE TABLE IF NOT EXISTS memory_fragments (
    id UUID PRIMARY KEY DEFAULT uuid(),
    fragment_type VARCHAR NOT NULL CHECK (fragment_type IN ('fact', 'pattern', 'preference', 'rule', 'context')),
    content TEXT NOT NULL,
    source_conversation_id UUID,
    source_message_id UUID,
    confidence_score FLOAT DEFAULT 0.5,
    importance_score FLOAT DEFAULT 0.5,
    tags VARCHAR[],
    embeddings FLOAT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    metadata JSON,
    FOREIGN KEY (source_conversation_id) REFERENCES conversations(id),
    FOREIGN KEY (source_message_id) REFERENCES messages(id)
);

-- Agent states - persistent agent knowledge
CREATE TABLE IF NOT EXISTS agent_states (
    id UUID PRIMARY KEY DEFAULT uuid(),
    agent_name VARCHAR NOT NULL,
    state_key VARCHAR NOT NULL,
    state_value JSON NOT NULL,
    expiry_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent_name, state_key)
);

-- Reasoning traces - detailed thought processes
CREATE TABLE IF NOT EXISTS reasoning_traces (
    id UUID PRIMARY KEY DEFAULT uuid(),
    conversation_id UUID NOT NULL,
    message_id UUID,
    step_number INTEGER NOT NULL,
    reasoning_type VARCHAR NOT NULL CHECK (reasoning_type IN ('analysis', 'planning', 'execution', 'reflection')),
    thought TEXT NOT NULL,
    action_taken TEXT,
    outcome TEXT,
    confidence FLOAT DEFAULT 0.5,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id),
    FOREIGN KEY (message_id) REFERENCES messages(id)
);

-- User preferences and context
CREATE TABLE IF NOT EXISTS user_context (
    id UUID PRIMARY KEY DEFAULT uuid(),
    user_id VARCHAR NOT NULL,
    context_type VARCHAR NOT NULL CHECK (context_type IN ('preference', 'skill', 'project', 'goal', 'constraint')),
    context_key VARCHAR NOT NULL,
    context_value JSON NOT NULL,
    priority INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, context_type, context_key)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_agent ON conversations(agent_name);
CREATE INDEX IF NOT EXISTS idx_conversations_time ON conversations(start_time);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);

CREATE INDEX IF NOT EXISTS idx_memory_fragments_type ON memory_fragments(fragment_type);
CREATE INDEX IF NOT EXISTS idx_memory_fragments_conversation ON memory_fragments(source_conversation_id);
CREATE INDEX IF NOT EXISTS idx_memory_fragments_importance ON memory_fragments(importance_score);
CREATE INDEX IF NOT EXISTS idx_memory_fragments_accessed ON memory_fragments(last_accessed);

CREATE INDEX IF NOT EXISTS idx_agent_states_name ON agent_states(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_states_key ON agent_states(state_key);

CREATE INDEX IF NOT EXISTS idx_reasoning_conversation ON reasoning_traces(conversation_id);
CREATE INDEX IF NOT EXISTS idx_reasoning_type ON reasoning_traces(reasoning_type);

CREATE INDEX IF NOT EXISTS idx_user_context_user ON user_context(user_id);
CREATE INDEX IF NOT EXISTS idx_user_context_type ON user_context(context_type);
