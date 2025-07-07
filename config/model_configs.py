"""
Model Configuration Management

Provides configuration for different LLM models and providers including
OpenAI, Anthropic, and other supported model providers.
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ModelProvider(str, Enum):
    """Supported model providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"
    XAI = "xai"


@dataclass
class ModelConfig:
    """Configuration for a specific model."""

    name: str
    provider: ModelProvider
    max_tokens: int
    temperature: float = 0.1
    supports_streaming: bool = True
    supports_function_calling: bool = True
    cost_per_1k_input_tokens: float = 0.0
    cost_per_1k_output_tokens: float = 0.0
    rate_limit_rpm: int = 60
    rate_limit_tpm: int = 50000
    context_window: int = 128000
    recommended_for: list[str] = None

    def __post_init__(self):
        if self.recommended_for is None:
            self.recommended_for = []


class ModelConfigs:
    """
    Manages configuration for all supported LLM models.

    Provides model-specific settings, cost information, and recommendations
    for different types of tasks and agents.
    """

    def __init__(self):
        """Initialize model configurations."""
        self.logger = logging.getLogger(__name__)
        self.models: dict[str, ModelConfig] = {}

        # Load model configurations
        self._load_model_configs()

    def _load_model_configs(self):
        """Load configurations for all supported models."""

        # OpenAI Models
        self.models["openai:gpt-4"] = ModelConfig(
            name="gpt-4",
            provider=ModelProvider.OPENAI,
            max_tokens=4096,
            temperature=0.1,
            cost_per_1k_input_tokens=0.03,
            cost_per_1k_output_tokens=0.06,
            rate_limit_rpm=500,
            rate_limit_tpm=150000,
            context_window=128000,
            recommended_for=["complex_reasoning", "code_generation", "analysis"],
        )

        self.models["openai:gpt-4-turbo"] = ModelConfig(
            name="gpt-4-turbo",
            provider=ModelProvider.OPENAI,
            max_tokens=4096,
            temperature=0.1,
            cost_per_1k_input_tokens=0.01,
            cost_per_1k_output_tokens=0.03,
            rate_limit_rpm=500,
            rate_limit_tpm=150000,
            context_window=128000,
            recommended_for=["general_purpose", "fast_response", "cost_effective"],
        )

        self.models["openai:gpt-3.5-turbo"] = ModelConfig(
            name="gpt-3.5-turbo",
            provider=ModelProvider.OPENAI,
            max_tokens=4096,
            temperature=0.1,
            cost_per_1k_input_tokens=0.0005,
            cost_per_1k_output_tokens=0.0015,
            rate_limit_rpm=3500,
            rate_limit_tpm=90000,
            context_window=16385,
            recommended_for=["simple_tasks", "high_volume", "budget_conscious"],
        )

        # Anthropic Models
        self.models["anthropic:claude-3-5-sonnet-20241022"] = ModelConfig(
            name="claude-3-5-sonnet-20241022",
            provider=ModelProvider.ANTHROPIC,
            max_tokens=4096,
            temperature=0.1,
            cost_per_1k_input_tokens=0.003,
            cost_per_1k_output_tokens=0.015,
            rate_limit_rpm=50,
            rate_limit_tpm=40000,
            context_window=200000,
            recommended_for=["complex_reasoning", "long_context", "safety_critical"],
        )

        self.models["anthropic:claude-3-haiku-20240307"] = ModelConfig(
            name="claude-3-haiku-20240307",
            provider=ModelProvider.ANTHROPIC,
            max_tokens=4096,
            temperature=0.1,
            cost_per_1k_input_tokens=0.00025,
            cost_per_1k_output_tokens=0.00125,
            rate_limit_rpm=50,
            rate_limit_tpm=40000,
            context_window=200000,
            recommended_for=["fast_response", "simple_tasks", "cost_effective"],
        )

        # Google Models
        self.models["google:gemini-1.5-pro"] = ModelConfig(
            name="gemini-1.5-pro",
            provider=ModelProvider.GOOGLE,
            max_tokens=8192,
            temperature=0.1,
            cost_per_1k_input_tokens=0.00125,
            cost_per_1k_output_tokens=0.00375,
            rate_limit_rpm=360,
            rate_limit_tpm=30000,
            context_window=2000000,  # 2M tokens
            recommended_for=["very_long_context", "multimodal", "cost_effective"],
        )

        # Groq Models (fast inference)
        self.models["groq:llama-3.1-70b-versatile"] = ModelConfig(
            name="llama-3.1-70b-versatile",
            provider=ModelProvider.GROQ,
            max_tokens=8000,
            temperature=0.1,
            cost_per_1k_input_tokens=0.00059,
            cost_per_1k_output_tokens=0.00079,
            rate_limit_rpm=30,
            rate_limit_tpm=14400,
            context_window=131072,
            recommended_for=["fast_inference", "real_time", "cost_effective"],
        )

        # xAI Models (Grok)
        self.models["xai:grok-beta"] = ModelConfig(
            name="grok-beta",
            provider=ModelProvider.XAI,
            max_tokens=4096,
            temperature=0.1,
            cost_per_1k_input_tokens=0.005,
            cost_per_1k_output_tokens=0.015,
            rate_limit_rpm=60,
            rate_limit_tpm=50000,
            context_window=128000,
            recommended_for=["general_purpose", "real_time", "conversational"],
        )

    def get_model_config(self, model_name: str) -> ModelConfig:
        """Get configuration for a specific model."""
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")

        return self.models[model_name]

    def get_models_by_provider(self, provider: ModelProvider) -> list[ModelConfig]:
        """Get all models for a specific provider."""
        return [
            config for config in self.models.values() if config.provider == provider
        ]

    def get_recommended_models(self, use_case: str) -> list[ModelConfig]:
        """Get models recommended for a specific use case."""
        return [
            config
            for config in self.models.values()
            if use_case in config.recommended_for
        ]

    def get_cost_estimate(
        self, model_name: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Estimate cost for a model with given token usage."""
        config = self.get_model_config(model_name)

        input_cost = (input_tokens / 1000) * config.cost_per_1k_input_tokens
        output_cost = (output_tokens / 1000) * config.cost_per_1k_output_tokens

        return input_cost + output_cost

    def compare_models_by_cost(
        self, input_tokens: int, output_tokens: int
    ) -> list[dict[str, Any]]:
        """Compare all models by cost for given token usage."""
        comparisons = []

        for model_name, config in self.models.items():
            cost = self.get_cost_estimate(model_name, input_tokens, output_tokens)

            comparisons.append(
                {
                    "model": model_name,
                    "provider": config.provider.value,
                    "cost": cost,
                    "context_window": config.context_window,
                    "recommended_for": config.recommended_for,
                }
            )

        # Sort by cost
        return sorted(comparisons, key=lambda x: x["cost"])

    def get_fastest_models(self, limit: int = 5) -> list[str]:
        """Get models with highest rate limits (fastest)."""
        models_by_speed = sorted(
            self.models.items(), key=lambda x: x[1].rate_limit_tpm, reverse=True
        )

        return [model_name for model_name, _ in models_by_speed[:limit]]

    def get_most_cost_effective(self, limit: int = 5) -> list[str]:
        """Get most cost-effective models (lowest cost per token)."""
        models_by_cost = sorted(
            self.models.items(),
            key=lambda x: x[1].cost_per_1k_input_tokens
            + x[1].cost_per_1k_output_tokens,
        )

        return [model_name for model_name, _ in models_by_cost[:limit]]

    def get_largest_context_models(self, limit: int = 5) -> list[str]:
        """Get models with largest context windows."""
        models_by_context = sorted(
            self.models.items(), key=lambda x: x[1].context_window, reverse=True
        )

        return [model_name for model_name, _ in models_by_context[:limit]]

    def validate_model_selection(
        self, model_name: str, requirements: dict[str, Any]
    ) -> list[str]:
        """Validate if a model meets specific requirements."""
        issues = []

        try:
            config = self.get_model_config(model_name)
        except ValueError as e:
            return [str(e)]

        # Check context window requirement
        if "min_context_window" in requirements:
            if config.context_window < requirements["min_context_window"]:
                issues.append(
                    f"Context window {config.context_window} < required {requirements['min_context_window']}"
                )

        # Check cost requirements
        if "max_cost_per_1k_tokens" in requirements:
            total_cost = (
                config.cost_per_1k_input_tokens + config.cost_per_1k_output_tokens
            )
            if total_cost > requirements["max_cost_per_1k_tokens"]:
                issues.append(
                    f"Cost per 1k tokens {total_cost:.4f} > max allowed {requirements['max_cost_per_1k_tokens']}"
                )

        # Check rate limit requirements
        if "min_rate_limit_rpm" in requirements:
            if config.rate_limit_rpm < requirements["min_rate_limit_rpm"]:
                issues.append(
                    f"Rate limit {config.rate_limit_rpm} RPM < required {requirements['min_rate_limit_rpm']}"
                )

        # Check feature requirements
        if (
            requirements.get("requires_streaming", False)
            and not config.supports_streaming
        ):
            issues.append("Model does not support streaming")

        if (
            requirements.get("requires_function_calling", False)
            and not config.supports_function_calling
        ):
            issues.append("Model does not support function calling")

        return issues

    def recommend_model_for_agent(
        self, agent_role: str, requirements: dict[str, Any] | None = None
    ) -> str:
        """Recommend the best model for a specific agent role."""
        requirements = requirements or {}

        # Agent-specific recommendations
        agent_preferences = {
            "data_platform_engineer": {
                "preferred_providers": [ModelProvider.OPENAI, ModelProvider.ANTHROPIC],
                "min_context_window": 32000,
                "use_cases": ["complex_reasoning", "code_generation"],
            },
            "data_engineer": {
                "preferred_providers": [ModelProvider.OPENAI, ModelProvider.ANTHROPIC],
                "min_context_window": 16000,
                "use_cases": ["code_generation", "analysis"],
            },
            "analytics_engineer": {
                "preferred_providers": [ModelProvider.OPENAI, ModelProvider.ANTHROPIC],
                "min_context_window": 32000,
                "use_cases": ["code_generation", "complex_reasoning"],
            },
            "data_scientist": {
                "preferred_providers": [ModelProvider.OPENAI, ModelProvider.ANTHROPIC],
                "min_context_window": 64000,
                "use_cases": ["complex_reasoning", "analysis"],
            },
            "data_analyst": {
                "preferred_providers": [ModelProvider.OPENAI, ModelProvider.GOOGLE],
                "min_context_window": 16000,
                "use_cases": ["general_purpose", "fast_response"],
            },
        }

        preferences = agent_preferences.get(agent_role, {})

        # Filter models by preferences and requirements
        candidate_models = []

        for model_name, config in self.models.items():
            # Check provider preference
            if (
                preferences.get("preferred_providers")
                and config.provider not in preferences["preferred_providers"]
            ):
                continue

            # Check context window
            min_context = max(
                preferences.get("min_context_window", 0),
                requirements.get("min_context_window", 0),
            )
            if config.context_window < min_context:
                continue

            # Check use cases
            preferred_use_cases = preferences.get("use_cases", [])
            if preferred_use_cases and not any(
                use_case in config.recommended_for for use_case in preferred_use_cases
            ):
                continue

            # Validate against requirements
            issues = self.validate_model_selection(model_name, requirements)
            if issues:
                continue

            candidate_models.append((model_name, config))

        if not candidate_models:
            # Fallback to default model
            return "openai:gpt-4"

        # Sort by preference score (cost-effectiveness and capabilities)
        def score_model(model_tuple):
            model_name, config = model_tuple

            # Lower cost is better
            cost_score = 1.0 / (
                config.cost_per_1k_input_tokens
                + config.cost_per_1k_output_tokens
                + 0.001
            )

            # Higher context window is better
            context_score = config.context_window / 200000

            # Higher rate limit is better
            rate_score = config.rate_limit_rpm / 1000

            return cost_score + context_score + rate_score

        best_model = max(candidate_models, key=score_model)
        return best_model[0]

    def get_provider_summary(self) -> dict[str, dict[str, Any]]:
        """Get summary of all providers and their models."""
        summary = {}

        for provider in ModelProvider:
            models = self.get_models_by_provider(provider)

            if models:
                summary[provider.value] = {
                    "model_count": len(models),
                    "models": [model.name for model in models],
                    "avg_cost_per_1k": sum(
                        model.cost_per_1k_input_tokens + model.cost_per_1k_output_tokens
                        for model in models
                    )
                    / len(models),
                    "max_context_window": max(model.context_window for model in models),
                    "total_rate_limit_rpm": sum(
                        model.rate_limit_rpm for model in models
                    ),
                }

        return summary

    def load_from_env_vars(self):
        """Load model configuration overrides from environment variables."""

        # Check for API keys and validate they're set
        api_key_mapping = {
            ModelProvider.OPENAI: "OPENAI_API_KEY",
            ModelProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
            ModelProvider.GOOGLE: "GOOGLE_API_KEY",
            ModelProvider.GROQ: "GROQ_API_KEY",
            ModelProvider.XAI: "XAI_API_KEY",
        }

        available_providers = []
        for provider, env_var in api_key_mapping.items():
            if os.getenv(env_var):
                available_providers.append(provider)
                self.logger.info(f"API key found for {provider.value}")
            else:
                self.logger.warning(
                    f"No API key found for {provider.value} ({env_var})"
                )

        # Remove models for providers without API keys
        models_to_remove = []
        for model_name, config in self.models.items():
            if config.provider not in available_providers:
                models_to_remove.append(model_name)

        for model_name in models_to_remove:
            provider = (
                self.models[model_name].provider
                if model_name in self.models
                else "unknown"
            )
            del self.models[model_name]
            self.logger.info(f"Removed {model_name} (no API key for {provider})")

        return available_providers
