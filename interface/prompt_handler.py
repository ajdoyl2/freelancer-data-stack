"""
Prompt Handler

Processes natural language prompts and determines appropriate agent routing
and task classification for the AI agent system.
"""

import logging
import re
from enum import Enum
from typing import Any

from agents.base_agent import AgentRole, WorkflowPriority, WorkflowRequest


class TaskComplexity(str, Enum):
    """Task complexity levels."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    MULTI_AGENT = "multi_agent"


class IntentType(str, Enum):
    """Types of user intents."""

    DEPLOYMENT = "deployment"
    DATA_PIPELINE = "data_pipeline"
    ANALYTICS = "analytics"
    MACHINE_LEARNING = "machine_learning"
    REPORTING = "reporting"
    MONITORING = "monitoring"
    TROUBLESHOOTING = "troubleshooting"
    GENERAL_INQUIRY = "general_inquiry"


class PromptHandler:
    """
    Handles natural language prompt processing and agent routing.

    Analyzes user prompts to:
    - Classify intent and complexity
    - Determine required agents
    - Extract context and parameters
    - Route to appropriate workflow execution
    """

    def __init__(self):
        """Initialize the prompt handler."""
        self.logger = logging.getLogger(__name__)

        # Keywords for intent classification
        self.intent_keywords = {
            IntentType.DEPLOYMENT: [
                "deploy",
                "deployment",
                "docker",
                "container",
                "infrastructure",
                "terraform",
                "aws",
                "cloud",
                "server",
                "service",
                "start",
                "stop",
            ],
            IntentType.DATA_PIPELINE: [
                "pipeline",
                "etl",
                "elt",
                "ingestion",
                "extract",
                "load",
                "meltano",
                "airflow",
                "data flow",
                "integration",
                "sync",
            ],
            IntentType.ANALYTICS: [
                "transform",
                "transformation",
                "dbt",
                "model",
                "mart",
                "dimension",
                "fact",
                "sql",
                "query",
                "aggregate",
            ],
            IntentType.MACHINE_LEARNING: [
                "ml",
                "machine learning",
                "model",
                "train",
                "predict",
                "feature",
                "experiment",
                "algorithm",
                "classification",
                "regression",
            ],
            IntentType.REPORTING: [
                "report",
                "dashboard",
                "visualization",
                "chart",
                "graph",
                "metabase",
                "evidence",
                "insight",
                "analytics",
                "kpi",
            ],
            IntentType.MONITORING: [
                "monitor",
                "monitoring",
                "alert",
                "health",
                "performance",
                "metrics",
                "logs",
                "status",
                "check",
                "observe",
            ],
            IntentType.TROUBLESHOOTING: [
                "error",
                "issue",
                "problem",
                "debug",
                "fix",
                "broken",
                "failing",
                "troubleshoot",
                "investigate",
                "help",
            ],
        }

        # Agent role mappings for different intents
        self.intent_agent_mapping = {
            IntentType.DEPLOYMENT: [AgentRole.DATA_PLATFORM_ENGINEER],
            IntentType.DATA_PIPELINE: [
                AgentRole.DATA_ENGINEER,
                AgentRole.DATA_PLATFORM_ENGINEER,
            ],
            IntentType.ANALYTICS: [AgentRole.ANALYTICS_ENGINEER],
            IntentType.MACHINE_LEARNING: [AgentRole.DATA_SCIENTIST],
            IntentType.REPORTING: [AgentRole.DATA_ANALYST],
            IntentType.MONITORING: [
                AgentRole.DATA_PLATFORM_ENGINEER,
                AgentRole.DATA_ENGINEER,
            ],
            IntentType.TROUBLESHOOTING: [AgentRole.DATA_PLATFORM_ENGINEER],
            IntentType.GENERAL_INQUIRY: [],  # Will be determined by content analysis
        }

        # Multi-agent workflow indicators
        self.multi_agent_indicators = [
            "end-to-end",
            "complete",
            "full",
            "entire",
            "comprehensive",
            "pipeline to dashboard",
            "data to insights",
            "ingestion to reporting",
            "infrastructure to visualization",
            "setup everything",
        ]

    async def analyze_prompt(
        self, user_prompt: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Analyze a user prompt to determine intent, complexity, and routing.

        Args:
            user_prompt: The natural language prompt from the user
            context: Additional context information

        Returns:
            Dict[str, Any]: Analysis results including intent, agents, and complexity
        """
        self.logger.info(f"Analyzing prompt: {user_prompt[:100]}...")

        # Clean and normalize the prompt
        normalized_prompt = self._normalize_prompt(user_prompt)

        # Classify intent
        intent = self._classify_intent(normalized_prompt)

        # Determine complexity
        complexity = self._assess_complexity(normalized_prompt)

        # Determine required agents
        required_agents = self._determine_agents(intent, normalized_prompt, complexity)

        # Extract entities and parameters
        entities = self._extract_entities(normalized_prompt)

        # Determine priority
        priority = self._determine_priority(normalized_prompt, context)

        # Check for multi-agent workflow
        is_multi_agent = (
            complexity == TaskComplexity.MULTI_AGENT or len(required_agents) > 1
        )

        analysis_result = {
            "original_prompt": user_prompt,
            "normalized_prompt": normalized_prompt,
            "intent": intent,
            "complexity": complexity,
            "required_agents": required_agents,
            "is_multi_agent": is_multi_agent,
            "entities": entities,
            "priority": priority,
            "confidence": self._calculate_confidence(intent, required_agents, entities),
            "suggested_workflow": self._suggest_workflow_type(
                intent, complexity, required_agents
            ),
        }

        return analysis_result

    def _normalize_prompt(self, prompt: str) -> str:
        """Normalize the prompt for analysis."""
        # Convert to lowercase
        normalized = prompt.lower()

        # Remove extra whitespace
        normalized = re.sub(r"\s+", " ", normalized).strip()

        # Remove common filler words that don't add meaning
        filler_words = {
            "please",
            "can you",
            "could you",
            "would you",
            "i want",
            "i need",
            "help me",
        }
        words = normalized.split()
        filtered_words = [word for word in words if word not in filler_words]

        return " ".join(filtered_words)

    def _classify_intent(self, prompt: str) -> IntentType:
        """Classify the user's intent based on keywords."""
        intent_scores = {}

        for intent_type, keywords in self.intent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in prompt:
                    # Weight longer, more specific keywords higher
                    score += len(keyword.split())

            if score > 0:
                intent_scores[intent_type] = score

        if intent_scores:
            # Return the intent with the highest score
            return max(intent_scores, key=intent_scores.get)
        else:
            return IntentType.GENERAL_INQUIRY

    def _assess_complexity(self, prompt: str) -> TaskComplexity:
        """Assess the complexity of the requested task."""
        # Check for multi-agent indicators
        for indicator in self.multi_agent_indicators:
            if indicator in prompt:
                return TaskComplexity.MULTI_AGENT

        # Complex task indicators
        complex_indicators = [
            "setup",
            "configure",
            "implement",
            "create",
            "build",
            "develop",
            "integrate",
            "optimize",
            "automate",
            "orchestrate",
        ]

        # Simple task indicators
        simple_indicators = [
            "show",
            "list",
            "get",
            "check",
            "status",
            "view",
            "display",
        ]

        complex_count = sum(
            1 for indicator in complex_indicators if indicator in prompt
        )
        simple_count = sum(1 for indicator in simple_indicators if indicator in prompt)

        # Count the number of different technologies/tools mentioned
        tech_keywords = [
            "docker",
            "meltano",
            "dbt",
            "airflow",
            "metabase",
            "evidence",
            "datahub",
            "great expectations",
            "postgres",
            "snowflake",
            "duckdb",
        ]
        tech_count = sum(1 for tech in tech_keywords if tech in prompt)

        # Determine complexity based on indicators and tech count
        if complex_count > simple_count and tech_count >= 3:
            return TaskComplexity.COMPLEX
        elif complex_count > simple_count or tech_count >= 2:
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.SIMPLE

    def _determine_agents(
        self, intent: IntentType, prompt: str, complexity: TaskComplexity
    ) -> list[AgentRole]:
        """Determine which agents are needed for the task."""
        # Start with agents mapped to the intent
        agents = self.intent_agent_mapping.get(intent, []).copy()

        # For multi-agent or complex tasks, check for additional agent needs
        if complexity in [TaskComplexity.COMPLEX, TaskComplexity.MULTI_AGENT]:
            # Check for specific agent indicators in the prompt
            agent_indicators = {
                AgentRole.DATA_PLATFORM_ENGINEER: [
                    "docker",
                    "deployment",
                    "infrastructure",
                    "server",
                    "container",
                ],
                AgentRole.DATA_ENGINEER: [
                    "pipeline",
                    "meltano",
                    "ingestion",
                    "etl",
                    "airflow",
                    "data flow",
                ],
                AgentRole.ANALYTICS_ENGINEER: [
                    "dbt",
                    "transformation",
                    "model",
                    "sql",
                    "mart",
                    "dimension",
                ],
                AgentRole.DATA_SCIENTIST: [
                    "ml",
                    "model",
                    "prediction",
                    "feature",
                    "experiment",
                    "algorithm",
                ],
                AgentRole.DATA_ANALYST: [
                    "dashboard",
                    "report",
                    "visualization",
                    "insight",
                    "metabase",
                    "chart",
                ],
            }

            for agent_role, indicators in agent_indicators.items():
                if agent_role not in agents:
                    for indicator in indicators:
                        if indicator in prompt:
                            agents.append(agent_role)
                            break

        # Remove duplicates while preserving order
        seen = set()
        unique_agents = []
        for agent in agents:
            if agent not in seen:
                seen.add(agent)
                unique_agents.append(agent)

        return unique_agents

    def _extract_entities(self, prompt: str) -> dict[str, list[str]]:
        """Extract entities and parameters from the prompt."""
        entities = {
            "technologies": [],
            "data_sources": [],
            "actions": [],
            "metrics": [],
            "file_formats": [],
        }

        # Technology entities
        tech_patterns = {
            "docker",
            "meltano",
            "dbt",
            "airflow",
            "metabase",
            "evidence",
            "datahub",
            "great expectations",
            "postgres",
            "snowflake",
            "duckdb",
            "terraform",
            "aws",
            "jupyter",
            "streamlit",
        }

        # Data source entities
        data_source_patterns = {
            "csv",
            "json",
            "api",
            "database",
            "warehouse",
            "lake",
            "s3",
            "postgres",
            "mysql",
            "sqlite",
            "snowflake",
        }

        # Action entities
        action_patterns = {
            "create",
            "build",
            "deploy",
            "run",
            "test",
            "monitor",
            "analyze",
            "transform",
            "load",
            "extract",
            "visualize",
            "optimize",
        }

        # Extract entities based on patterns
        words = prompt.split()
        for word in words:
            clean_word = re.sub(r"[^\w]", "", word)

            if clean_word in tech_patterns:
                entities["technologies"].append(clean_word)
            elif clean_word in data_source_patterns:
                entities["data_sources"].append(clean_word)
            elif clean_word in action_patterns:
                entities["actions"].append(clean_word)

        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))

        return entities

    def _determine_priority(
        self, prompt: str, context: dict[str, Any] | None = None
    ) -> WorkflowPriority:
        """Determine the priority of the request."""
        # Check for urgency indicators
        urgent_indicators = ["urgent", "asap", "immediately", "critical", "emergency"]
        high_indicators = ["important", "priority", "soon", "quickly"]
        low_indicators = ["when possible", "eventually", "low priority"]

        for indicator in urgent_indicators:
            if indicator in prompt:
                return WorkflowPriority.URGENT

        for indicator in high_indicators:
            if indicator in prompt:
                return WorkflowPriority.HIGH

        for indicator in low_indicators:
            if indicator in prompt:
                return WorkflowPriority.LOW

        # Check context for priority hints
        if context and "priority" in context:
            context_priority = context["priority"].lower()
            if context_priority in ["urgent", "high", "medium", "low"]:
                return WorkflowPriority(context_priority.upper())

        return WorkflowPriority.MEDIUM

    def _calculate_confidence(
        self,
        intent: IntentType,
        agents: list[AgentRole],
        entities: dict[str, list[str]],
    ) -> float:
        """Calculate confidence in the analysis."""
        confidence = 0.5  # Base confidence

        # Increase confidence if we found a clear intent
        if intent != IntentType.GENERAL_INQUIRY:
            confidence += 0.2

        # Increase confidence if we identified specific agents
        if agents:
            confidence += 0.2

        # Increase confidence based on entity extraction
        total_entities = sum(len(entity_list) for entity_list in entities.values())
        confidence += min(total_entities * 0.05, 0.3)

        return min(confidence, 1.0)

    def _suggest_workflow_type(
        self, intent: IntentType, complexity: TaskComplexity, agents: list[AgentRole]
    ) -> str:
        """Suggest the type of workflow needed."""
        if complexity == TaskComplexity.MULTI_AGENT or len(agents) > 1:
            return "orchestrated_multi_agent"
        elif complexity == TaskComplexity.COMPLEX:
            return "complex_single_agent"
        elif complexity == TaskComplexity.MODERATE:
            return "standard_single_agent"
        else:
            return "simple_single_agent"

    async def create_workflow_request(
        self, user_prompt: str, context: dict[str, Any] | None = None
    ) -> WorkflowRequest:
        """
        Create a WorkflowRequest from a user prompt.

        Args:
            user_prompt: The natural language prompt
            context: Additional context information

        Returns:
            WorkflowRequest: Structured workflow request
        """
        analysis = await self.analyze_prompt(user_prompt, context)

        # Merge analysis results into context
        enriched_context = {
            **(context or {}),
            "analysis": analysis,
            "entities": analysis["entities"],
            "confidence": analysis["confidence"],
            "workflow_type": analysis["suggested_workflow"],
        }

        return WorkflowRequest(
            user_prompt=user_prompt,
            context=enriched_context,
            priority=analysis["priority"],
            agents_involved=analysis["required_agents"],
        )
