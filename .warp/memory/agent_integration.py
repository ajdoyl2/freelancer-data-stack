#!/usr/bin/env python3
"""
Agent Integration for Memory System

Provides easy-to-use wrappers for AI agents to integrate with the memory system.
Handles session management, context injection, and memory extraction.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from memory_manager import AgentMemoryManager, MemoryFragment, ReasoningStep


class MemoryEnabledAgent:
    """Base class for AI agents with memory capabilities"""
    
    def __init__(self, agent_name: str, user_id: str = "default_user"):
        self.agent_name = agent_name
        self.user_id = user_id
        self.memory_manager = AgentMemoryManager()
        self.current_conversation_id = None
        self.session_id = self._generate_session_id()
        
        # Load user context and agent state
        self.user_context = self.memory_manager.get_user_context(user_id)
        self.agent_state = self.memory_manager.get_agent_state(agent_name)
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        content = f"{self.agent_name}_{self.user_id}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def start_conversation(self, context_summary: str = None, 
                          tags: List[str] = None) -> str:
        """Start a new conversation session"""
        self.current_conversation_id = self.memory_manager.start_conversation(
            session_id=self.session_id,
            agent_name=self.agent_name,
            user_id=self.user_id,
            context_summary=context_summary,
            tags=tags or []
        )
        return self.current_conversation_id
    
    def end_conversation(self, summary: str = None):
        """End current conversation"""
        if self.current_conversation_id:
            self.memory_manager.end_conversation(
                self.current_conversation_id, 
                context_summary=summary
            )
            self.current_conversation_id = None
    
    def add_user_message(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Add user message to conversation"""
        if not self.current_conversation_id:
            self.start_conversation()
        
        return self.memory_manager.add_message(
            conversation_id=self.current_conversation_id,
            role="user",
            content=content,
            metadata=metadata or {}
        )
    
    def add_assistant_message(self, content: str, reasoning_trace: str = None,
                            tool_calls: List[Dict] = None, 
                            tokens_used: int = None,
                            metadata: Dict[str, Any] = None) -> str:
        """Add assistant response to conversation"""
        if not self.current_conversation_id:
            self.start_conversation()
        
        return self.memory_manager.add_message(
            conversation_id=self.current_conversation_id,
            role="assistant",
            content=content,
            reasoning_trace=reasoning_trace,
            tool_calls=tool_calls,
            tokens_used=tokens_used,
            metadata=metadata or {}
        )
    
    def remember(self, fragment_type: str, content: str, 
                importance: float = 0.5, confidence: float = 0.5,
                tags: List[str] = None, metadata: Dict[str, Any] = None):
        """Store a memory fragment"""
        fragment = MemoryFragment(
            fragment_type=fragment_type,
            content=content,
            importance_score=importance,
            confidence_score=confidence,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        return self.memory_manager.add_memory_fragment(
            fragment=fragment,
            source_conversation_id=self.current_conversation_id
        )
    
    def recall(self, query: str = None, fragment_type: str = None,
              tags: List[str] = None, limit: int = 5,
              min_importance: float = 0.3) -> List[Dict[str, Any]]:
        """Retrieve relevant memory fragments"""
        return self.memory_manager.search_memory_fragments(
            query=query,
            fragment_type=fragment_type,
            tags=tags,
            limit=limit,
            min_importance=min_importance
        )
    
    def add_reasoning(self, reasoning_steps: List[ReasoningStep],
                     message_id: str = None):
        """Add reasoning trace to conversation"""
        if self.current_conversation_id:
            self.memory_manager.add_reasoning_trace(
                conversation_id=self.current_conversation_id,
                steps=reasoning_steps,
                message_id=message_id
            )
    
    def set_preference(self, key: str, value: Any, priority: int = 5):
        """Set user preference"""
        self.memory_manager.set_user_context(
            user_id=self.user_id,
            context_type="preference",
            context_key=key,
            context_value=value,
            priority=priority
        )
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences"""
        context = self.memory_manager.get_user_context(self.user_id, "preference")
        return context or {}
    
    def save_state(self, key: str, value: Any, expiry: datetime = None):
        """Save agent state"""
        self.memory_manager.set_agent_state(
            agent_name=self.agent_name,
            state_key=key,
            state_value=value,
            expiry_time=expiry
        )
        self.agent_state[key] = value
    
    def load_state(self, key: str = None) -> Any:
        """Load agent state"""
        if key:
            return self.memory_manager.get_agent_state(self.agent_name, key)
        else:
            return self.memory_manager.get_agent_state(self.agent_name)
    
    def get_conversation_context(self, limit: int = 3) -> str:
        """Get formatted conversation context for prompt injection"""
        # Get recent conversations
        recent_convos = self.memory_manager.get_conversation_history(
            agent_name=self.agent_name,
            user_id=self.user_id,
            limit=limit
        )
        
        # Get relevant memory fragments
        relevant_memories = self.recall(limit=5, min_importance=0.5)
        
        # Format context
        context_parts = []
        
        if recent_convos:
            context_parts.append("## Recent Conversations:")
            for convo in recent_convos:
                if convo.get('context_summary'):
                    context_parts.append(f"- {convo['context_summary']}")
        
        if relevant_memories:
            context_parts.append("\n## Relevant Memories:")
            for memory in relevant_memories:
                context_parts.append(f"- [{memory['fragment_type']}] {memory['content']}")
        
        # Add user preferences
        prefs = self.get_preferences()
        if prefs:
            context_parts.append("\n## User Preferences:")
            for key, value in prefs.items():
                context_parts.append(f"- {key}: {value}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def extract_insights(self, conversation_content: str) -> List[MemoryFragment]:
        """Extract insights from conversation content (placeholder for AI analysis)"""
        # This is a placeholder - in a real implementation, you'd use
        # an LLM to analyze the conversation and extract insights
        insights = []
        
        # Simple keyword-based extraction for now
        if "prefer" in conversation_content.lower():
            insights.append(MemoryFragment(
                fragment_type="preference",
                content=f"User mentioned preferences in: {conversation_content[:100]}...",
                importance_score=0.6
            ))
        
        if "always" in conversation_content.lower() or "never" in conversation_content.lower():
            insights.append(MemoryFragment(
                fragment_type="rule",
                content=f"User stated rule: {conversation_content[:100]}...",
                importance_score=0.8
            ))
        
        if "remember" in conversation_content.lower():
            insights.append(MemoryFragment(
                fragment_type="fact",
                content=f"Important fact: {conversation_content[:100]}...",
                importance_score=0.7
            ))
        
        return insights


class WarpAgentMemory(MemoryEnabledAgent):
    """Specialized memory integration for Warp terminal agents"""
    
    def __init__(self):
        super().__init__(agent_name="warp_agent", user_id=os.getenv("USER", "default_user"))
        
        # Load Warp-specific context
        self._load_warp_context()
    
    def _load_warp_context(self):
        """Load Warp-specific user context and preferences"""
        # Set default preferences for terminal work
        default_prefs = {
            "shell": os.getenv("SHELL", "zsh"),
            "terminal": "warp",
            "work_directory": os.getcwd(),
            "coding_style": "pythonic",
            "verbosity": "concise"
        }
        
        for key, value in default_prefs.items():
            existing = self.memory_manager.get_user_context(self.user_id, "preference")
            if not existing or key not in existing:
                self.set_preference(key, value)
    
    def remember_command_success(self, command: str, output: str, context: str = ""):
        """Remember successful command execution"""
        self.remember(
            fragment_type="pattern",
            content=f"Successful command: {command}\nContext: {context}\nOutput: {output[:200]}...",
            importance_score=0.6,
            tags=["command", "success"]
        )
    
    def remember_command_failure(self, command: str, error: str, context: str = ""):
        """Remember failed command execution"""
        self.remember(
            fragment_type="pattern",
            content=f"Failed command: {command}\nContext: {context}\nError: {error[:200]}...",
            importance_score=0.8,
            tags=["command", "failure", "error"]
        )
    
    def remember_user_workflow(self, workflow_name: str, steps: List[str], context: str = ""):
        """Remember user workflow patterns"""
        workflow_content = f"Workflow: {workflow_name}\nSteps:\n" + "\n".join(f"  {i+1}. {step}" for i, step in enumerate(steps))
        if context:
            workflow_content += f"\nContext: {context}"
        
        self.remember(
            fragment_type="pattern",
            content=workflow_content,
            importance_score=0.9,
            tags=["workflow", workflow_name.lower().replace(" ", "_")]
        )
    
    def get_command_suggestions(self, current_context: str) -> List[str]:
        """Get command suggestions based on memory"""
        # Search for relevant command patterns
        command_memories = self.recall(
            query=current_context,
            fragment_type="pattern",
            tags=["command", "success"],
            limit=3
        )
        
        suggestions = []
        for memory in command_memories:
            # Extract command from memory content
            content = memory['content']
            if "Successful command:" in content:
                cmd_line = content.split("Successful command:")[1].split("\n")[0].strip()
                suggestions.append(cmd_line)
        
        return suggestions
    
    def get_workflow_suggestions(self, task_description: str) -> List[Dict[str, Any]]:
        """Get workflow suggestions based on task description"""
        workflow_memories = self.recall(
            query=task_description,
            fragment_type="pattern",
            tags=["workflow"],
            limit=3
        )
        
        workflows = []
        for memory in workflow_memories:
            workflows.append({
                "content": memory['content'],
                "importance": memory['importance_score'],
                "last_used": memory['last_accessed']
            })
        
        return workflows


# Convenience functions for easy integration
def get_warp_memory() -> WarpAgentMemory:
    """Get singleton Warp memory instance"""
    if not hasattr(get_warp_memory, '_instance'):
        get_warp_memory._instance = WarpAgentMemory()
    return get_warp_memory._instance


def remember_this(content: str, fragment_type: str = "fact", importance: float = 0.7):
    """Quick function to remember something"""
    memory = get_warp_memory()
    return memory.remember(fragment_type, content, importance)


def recall_about(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Quick function to recall information"""
    memory = get_warp_memory()
    return memory.recall(query=query, limit=limit)


def get_context_for_prompt() -> str:
    """Get memory context to inject into prompts"""
    memory = get_warp_memory()
    return memory.get_conversation_context()


if __name__ == "__main__":
    # Demo usage
    memory = WarpAgentMemory()
    
    # Start conversation
    conv_id = memory.start_conversation("Testing memory system")
    
    # Add some interactions
    memory.add_user_message("How do I list files in Python?")
    memory.add_assistant_message(
        "You can use `os.listdir()` or `pathlib.Path().iterdir()`",
        reasoning_trace="User wants to list files, providing Python solutions"
    )
    
    # Remember something
    memory.remember_command_success(
        command="ls -la",
        output="total 48\ndrwxr-xr-x...",
        context="User wanted to see detailed file listing"
    )
    
    # End conversation
    memory.end_conversation("Helped user with file listing in Python")
    
    # Search memory
    results = memory.recall("file listing")
    print(f"Found {len(results)} relevant memories")
    
    # Get context
    context = memory.get_conversation_context()
    print(f"Context length: {len(context)} characters")
