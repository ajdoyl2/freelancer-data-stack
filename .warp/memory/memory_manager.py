#!/usr/bin/env python3
"""
AI Agent Memory Manager

Provides persistent memory capabilities for AI agents using DuckDB.
Stores conversations, reasoning traces, memory fragments, and user context.
"""

import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import duckdb


@dataclass
class MemoryFragment:
    """Represents a piece of extracted knowledge or pattern"""

    fragment_type: str  # fact, pattern, preference, rule, context
    content: str
    confidence_score: float = 0.5
    importance_score: float = 0.5
    tags: list[str] = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ReasoningStep:
    """Represents a step in the agent's reasoning process"""

    step_number: int
    reasoning_type: str  # analysis, planning, execution, reflection
    thought: str
    action_taken: str | None = None
    outcome: str | None = None
    confidence: float = 0.5
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class AgentMemoryManager:
    """Manages AI agent memory using DuckDB backend"""

    def __init__(self, memory_dir: str = None):
        """Initialize memory manager with DuckDB database"""
        if memory_dir is None:
            memory_dir = os.path.expanduser("~/.warp/memory")

        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.memory_dir / "agent_memory.duckdb"
        self.schema_path = Path(__file__).parent / "schema.sql"

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize DuckDB database with schema"""
        with duckdb.connect(str(self.db_path)) as conn:
            # Load and execute schema
            if self.schema_path.exists():
                schema_sql = self.schema_path.read_text()
                conn.execute(schema_sql)
            else:
                raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

    def start_conversation(
        self,
        session_id: str,
        agent_name: str,
        user_id: str = "default_user",
        context_summary: str = None,
        tags: list[str] = None,
        metadata: dict[str, Any] = None,
    ) -> str:
        """Start a new conversation and return conversation ID"""
        conversation_id = str(uuid.uuid4())

        with duckdb.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                INSERT INTO conversations
                (id, session_id, agent_name, user_id, context_summary, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    conversation_id,
                    session_id,
                    agent_name,
                    user_id,
                    context_summary,
                    tags or [],
                    json.dumps(metadata or {}),
                ],
            )

        return conversation_id

    def end_conversation(self, conversation_id: str, context_summary: str = None):
        """Mark conversation as ended with optional summary"""
        with duckdb.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                UPDATE conversations
                SET end_time = CURRENT_TIMESTAMP,
                    context_summary = COALESCE(?, context_summary),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                [context_summary, conversation_id],
            )

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tokens_used: int = None,
        reasoning_trace: str = None,
        tool_calls: list[dict] = None,
        metadata: dict[str, Any] = None,
    ) -> str:
        """Add a message to the conversation"""
        message_id = str(uuid.uuid4())

        with duckdb.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                INSERT INTO messages
                (id, conversation_id, role, content, tokens_used, reasoning_trace, tool_calls, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    message_id,
                    conversation_id,
                    role,
                    content,
                    tokens_used,
                    reasoning_trace,
                    json.dumps(tool_calls or []),
                    json.dumps(metadata or {}),
                ],
            )

        return message_id

    def add_memory_fragment(
        self,
        fragment: MemoryFragment,
        source_conversation_id: str = None,
        source_message_id: str = None,
    ) -> str:
        """Store a memory fragment"""
        fragment_id = str(uuid.uuid4())

        with duckdb.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                INSERT INTO memory_fragments
                (id, fragment_type, content, source_conversation_id, source_message_id,
                 confidence_score, importance_score, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    fragment_id,
                    fragment.fragment_type,
                    fragment.content,
                    source_conversation_id,
                    source_message_id,
                    fragment.confidence_score,
                    fragment.importance_score,
                    fragment.tags,
                    json.dumps(fragment.metadata),
                ],
            )

        return fragment_id

    def add_reasoning_trace(
        self, conversation_id: str, steps: list[ReasoningStep], message_id: str = None
    ):
        """Add reasoning trace for a conversation"""
        with duckdb.connect(str(self.db_path)) as conn:
            for step in steps:
                conn.execute(
                    """
                    INSERT INTO reasoning_traces
                    (conversation_id, message_id, step_number, reasoning_type,
                     thought, action_taken, outcome, confidence, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    [
                        conversation_id,
                        message_id,
                        step.step_number,
                        step.reasoning_type,
                        step.thought,
                        step.action_taken,
                        step.outcome,
                        step.confidence,
                        json.dumps(step.metadata),
                    ],
                )

    def set_agent_state(
        self,
        agent_name: str,
        state_key: str,
        state_value: Any,
        expiry_time: datetime = None,
    ):
        """Set persistent agent state"""
        with duckdb.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                INSERT INTO agent_states
                (agent_name, state_key, state_value, expiry_time, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (agent_name, state_key) DO UPDATE SET
                    state_value = excluded.state_value,
                    expiry_time = excluded.expiry_time,
                    updated_at = ?
            """,
                [
                    agent_name,
                    state_key,
                    json.dumps(state_value),
                    expiry_time,
                    datetime.now(),
                    datetime.now(),
                ],
            )

    def get_agent_state(self, agent_name: str, state_key: str = None) -> dict[str, Any]:
        """Get agent state(s)"""
        with duckdb.connect(str(self.db_path)) as conn:
            if state_key:
                result = conn.execute(
                    """
                    SELECT state_value FROM agent_states
                    WHERE agent_name = ? AND state_key = ?
                    AND (expiry_time IS NULL OR expiry_time > CURRENT_TIMESTAMP)
                """,
                    [agent_name, state_key],
                ).fetchone()

                return json.loads(result[0]) if result else None
            else:
                results = conn.execute(
                    """
                    SELECT state_key, state_value FROM agent_states
                    WHERE agent_name = ?
                    AND (expiry_time IS NULL OR expiry_time > CURRENT_TIMESTAMP)
                """,
                    [agent_name],
                ).fetchall()

                return {row[0]: json.loads(row[1]) for row in results}

    def search_memory_fragments(
        self,
        query: str = None,
        fragment_type: str = None,
        tags: list[str] = None,
        limit: int = 10,
        min_importance: float = 0.0,
    ) -> list[dict[str, Any]]:
        """Search memory fragments by content, type, or tags"""
        conditions = ["importance_score >= ?"]
        params = [min_importance]

        if fragment_type:
            conditions.append("fragment_type = ?")
            params.append(fragment_type)

        if tags:
            # Use array_contains for tag matching
            tag_conditions = ["array_contains(tags, ?)"] * len(tags)
            conditions.extend(tag_conditions)
            params.extend(tags)

        if query:
            conditions.append("content ILIKE ?")
            params.append(f"%{query}%")

        where_clause = " AND ".join(conditions)

        with duckdb.connect(str(self.db_path)) as conn:
            results = conn.execute(
                f"""
                SELECT id, fragment_type, content, confidence_score, importance_score,
                       tags, created_at, last_accessed, access_count, metadata
                FROM memory_fragments
                WHERE {where_clause}
                ORDER BY importance_score DESC, last_accessed DESC
                LIMIT ?
            """,
                params + [limit],
            ).fetchall()

            # Update access count for retrieved fragments
            if results:
                fragment_ids = [row[0] for row in results]
                placeholders = ",".join(["?"] * len(fragment_ids))
                conn.execute(
                    f"""
                    UPDATE memory_fragments
                    SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                    WHERE id IN ({placeholders})
                """,
                    fragment_ids,
                )

            return [
                {
                    "id": row[0],
                    "fragment_type": row[1],
                    "content": row[2],
                    "confidence_score": row[3],
                    "importance_score": row[4],
                    "tags": row[5],
                    "created_at": row[6],
                    "last_accessed": row[7],
                    "access_count": row[8],
                    "metadata": json.loads(row[9] or "{}"),
                }
                for row in results
            ]

    def get_conversation_history(
        self, agent_name: str = None, user_id: str = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get recent conversation history"""
        conditions = []
        params = []

        if agent_name:
            conditions.append("agent_name = ?")
            params.append(agent_name)

        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        with duckdb.connect(str(self.db_path)) as conn:
            results = conn.execute(
                f"""
                SELECT id, session_id, agent_name, user_id, start_time, end_time,
                       context_summary, tags, metadata
                FROM conversations
                WHERE {where_clause}
                ORDER BY start_time DESC
                LIMIT ?
            """,
                params + [limit],
            ).fetchall()

            return [
                {
                    "id": row[0],
                    "session_id": row[1],
                    "agent_name": row[2],
                    "user_id": row[3],
                    "start_time": row[4],
                    "end_time": row[5],
                    "context_summary": row[6],
                    "tags": row[7],
                    "metadata": json.loads(row[8] or "{}"),
                }
                for row in results
            ]

    def get_reasoning_traces(self, conversation_id: str) -> list[dict[str, Any]]:
        """Get reasoning traces for a conversation"""
        with duckdb.connect(str(self.db_path)) as conn:
            results = conn.execute(
                """
                SELECT step_number, reasoning_type, thought, action_taken, outcome,
                       confidence, timestamp, metadata
                FROM reasoning_traces
                WHERE conversation_id = ?
                ORDER BY step_number ASC
            """,
                [conversation_id],
            ).fetchall()

            return [
                {
                    "step_number": row[0],
                    "reasoning_type": row[1],
                    "thought": row[2],
                    "action_taken": row[3],
                    "outcome": row[4],
                    "confidence": row[5],
                    "timestamp": row[6],
                    "metadata": json.loads(row[7] or "{}"),
                }
                for row in results
            ]

    def set_user_context(
        self,
        user_id: str,
        context_type: str,
        context_key: str,
        context_value: Any,
        priority: int = 5,
    ):
        """Set user context/preferences"""
        with duckdb.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                INSERT INTO user_context
                (user_id, context_type, context_key, context_value, priority, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (user_id, context_type, context_key) DO UPDATE SET
                    context_value = excluded.context_value,
                    priority = excluded.priority,
                    updated_at = ?
            """,
                [
                    user_id,
                    context_type,
                    context_key,
                    json.dumps(context_value),
                    priority,
                    datetime.now(),
                    datetime.now(),
                ],
            )

    def get_user_context(
        self, user_id: str, context_type: str = None
    ) -> dict[str, Any]:
        """Get user context/preferences"""
        with duckdb.connect(str(self.db_path)) as conn:
            if context_type:
                results = conn.execute(
                    """
                    SELECT context_key, context_value, priority FROM user_context
                    WHERE user_id = ? AND context_type = ?
                    ORDER BY priority DESC
                """,
                    [user_id, context_type],
                ).fetchall()
            else:
                results = conn.execute(
                    """
                    SELECT context_type, context_key, context_value, priority FROM user_context
                    WHERE user_id = ?
                    ORDER BY context_type, priority DESC
                """,
                    [user_id],
                ).fetchall()

            if context_type:
                return {row[0]: json.loads(row[1]) for row in results}
            else:
                context = {}
                for row in results:
                    if row[0] not in context:
                        context[row[0]] = {}
                    context[row[0]][row[1]] = json.loads(row[2])
                return context

    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old conversation data"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        with duckdb.connect(str(self.db_path)) as conn:
            # Clean up old conversations and related data
            conn.execute(
                """
                DELETE FROM reasoning_traces
                WHERE conversation_id IN (
                    SELECT id FROM conversations
                    WHERE start_time < ? AND end_time IS NOT NULL
                )
            """,
                [cutoff_date],
            )

            conn.execute(
                """
                DELETE FROM messages
                WHERE conversation_id IN (
                    SELECT id FROM conversations
                    WHERE start_time < ? AND end_time IS NOT NULL
                )
            """,
                [cutoff_date],
            )

            conn.execute(
                """
                DELETE FROM conversations
                WHERE start_time < ? AND end_time IS NOT NULL
            """,
                [cutoff_date],
            )

            # Clean up unused memory fragments (keep high importance ones)
            conn.execute(
                """
                DELETE FROM memory_fragments
                WHERE created_at < ? AND importance_score < 0.7
            """,
                [cutoff_date],
            )

    def get_memory_stats(self) -> dict[str, Any]:
        """Get memory system statistics"""
        with duckdb.connect(str(self.db_path)) as conn:
            stats = {}

            # Conversation stats
            result = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()
            stats["total_conversations"] = result[0]

            # Message stats
            result = conn.execute("SELECT COUNT(*) FROM messages").fetchone()
            stats["total_messages"] = result[0]

            # Memory fragment stats
            result = conn.execute(
                """
                SELECT fragment_type, COUNT(*) FROM memory_fragments
                GROUP BY fragment_type
            """
            ).fetchall()
            stats["memory_fragments"] = {row[0]: row[1] for row in result}

            # Recent activity
            result = conn.execute(
                """
                SELECT COUNT(*) FROM conversations
                WHERE start_time > CURRENT_TIMESTAMP - INTERVAL 7 DAY
            """
            ).fetchone()
            stats["conversations_last_week"] = result[0]

            return stats


# CLI interface functions
def main():
    """CLI interface for memory manager"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Agent Memory Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Stats command
    subparsers.add_parser("stats", help="Show memory statistics")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search memory fragments")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--type", help="Fragment type filter")
    search_parser.add_argument("--limit", type=int, default=10, help="Result limit")

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old data")
    cleanup_parser.add_argument("--days", type=int, default=30, help="Days to keep")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    memory_manager = AgentMemoryManager()

    if args.command == "stats":
        stats = memory_manager.get_memory_stats()
        print("🧠 Agent Memory Statistics:")
        print(f"  Conversations: {stats['total_conversations']}")
        print(f"  Messages: {stats['total_messages']}")
        print(f"  Recent activity (7 days): {stats['conversations_last_week']}")
        print("\n📚 Memory Fragments:")
        for frag_type, count in stats.get("memory_fragments", {}).items():
            print(f"  {frag_type}: {count}")

    elif args.command == "search":
        results = memory_manager.search_memory_fragments(
            query=args.query, fragment_type=args.type, limit=args.limit
        )
        print(f"🔍 Found {len(results)} memory fragments:")
        for result in results:
            print(f"\n  [{result['fragment_type']}] {result['content'][:100]}...")
            print(
                f"    Importance: {result['importance_score']:.2f}, "
                f"Accessed: {result['access_count']} times"
            )

    elif args.command == "cleanup":
        memory_manager.cleanup_old_data(days_to_keep=args.days)
        print(f"🧹 Cleaned up data older than {args.days} days")


if __name__ == "__main__":
    main()
