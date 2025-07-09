"""
LLM Gateway for code generation and data Q&A using LangChain
"""

import logging
from datetime import datetime
from typing import Any

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from config import settings

logger = logging.getLogger(__name__)


class LLMGateway:
    """LLM Gateway for code generation and data Q&A"""

    def __init__(self):
        self.llm = None
        self.chat_model = None
        self.memory = ConversationBufferMemory()
        self.code_gen_chain = None
        self.qa_chain = None

    async def initialize(self):
        """Initialize LLM models and chains"""
        try:
            if settings.openai_api_key:
                # Initialize OpenAI models
                self.llm = OpenAI(
                    openai_api_key=settings.openai_api_key,
                    model_name=settings.openai_model,
                    temperature=0.1,
                )

                self.chat_model = ChatOpenAI(
                    openai_api_key=settings.openai_api_key,
                    model_name=settings.openai_model,
                    temperature=0.1,
                )

                # Initialize chains
                self._setup_chains()

                logger.info("LLM Gateway initialized successfully")
            else:
                logger.warning("OpenAI API key not configured")

        except Exception as e:
            logger.error(f"Failed to initialize LLM Gateway: {e}")
            raise

    def _setup_chains(self):
        """Setup LangChain chains for different tasks"""

        # Code generation chain
        code_gen_template = """
        You are a expert data engineer and programmer. Generate {language} code based on the following requirements:

        Requirements: {prompt}

        Context: {context}

        Please provide clean, well-documented, and production-ready code.
        Include error handling and best practices.

        Code:
        """

        code_gen_prompt = PromptTemplate(
            template=code_gen_template,
            input_variables=["language", "prompt", "context"],
        )

        self.code_gen_chain = LLMChain(
            llm=self.llm, prompt=code_gen_prompt, memory=self.memory
        )

        # Q&A chain
        qa_template = """
        You are a data analyst and expert in data systems. Answer the following question about data:

        Question: {question}

        Context: {context}

        Available Data Sources:
        - Snowflake data warehouse
        - DuckDB local database
        - dbt transformation models
        - Dagster pipeline data
        - DataHub metadata

        Please provide a comprehensive answer with specific recommendations and insights.
        If data analysis is needed, suggest specific queries or approaches.

        Answer:
        """

        qa_prompt = PromptTemplate(
            template=qa_template, input_variables=["question", "context"]
        )

        self.qa_chain = LLMChain(llm=self.llm, prompt=qa_prompt, memory=self.memory)

    async def generate_code(self, request: dict[str, Any]) -> dict[str, Any]:
        """Generate code using LLM"""
        try:
            if not self.code_gen_chain:
                await self.initialize()

            prompt = request.get("prompt", "")
            language = request.get("language", "python")
            context = request.get("context", "")

            # Generate code
            result = await self.code_gen_chain.arun(
                prompt=prompt, language=language, context=context
            )

            return {
                "content": result,
                "model": settings.openai_model,
                "tokens_used": self._estimate_tokens(prompt + result),
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return {
                "content": f"Error generating code: {str(e)}",
                "model": settings.openai_model,
                "tokens_used": 0,
                "generated_at": datetime.now().isoformat(),
            }

    async def answer_question(self, request: dict[str, Any]) -> dict[str, Any]:
        """Answer data questions using LLM"""
        try:
            if not self.qa_chain:
                await self.initialize()

            question = request.get("question", "")
            context = request.get("context", "")
            include_data = request.get("include_data", False)

            # Enhance context with data if requested
            if include_data:
                context = await self._enhance_context_with_data(context)

            # Generate answer
            result = await self.qa_chain.arun(question=question, context=context)

            return {
                "content": result,
                "model": settings.openai_model,
                "tokens_used": self._estimate_tokens(question + result),
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                "content": f"Error answering question: {str(e)}",
                "model": settings.openai_model,
                "tokens_used": 0,
                "generated_at": datetime.now().isoformat(),
            }

    async def _enhance_context_with_data(self, context: str) -> str:
        """Enhance context with data from adapters"""
        try:
            # Import here to avoid circular imports
            from main import adapters

            enhanced_context = context + "\n\nAvailable Data Sources:\n"

            # Add Dagster jobs info
            try:
                jobs = await adapters["dagster"].get_jobs()
                enhanced_context += f"\nDagster Jobs ({len(jobs)} jobs):\n"
                for job in jobs[:5]:  # Limit to first 5
                    enhanced_context += f"- {job['name']}: {job['status']}\n"
            except:
                pass

            # Add dbt models info
            try:
                models = await adapters["dbt"].get_models()
                enhanced_context += f"\ndbt Models ({len(models)} models):\n"
                for model in models[:5]:  # Limit to first 5
                    enhanced_context += f"- {model['name']}: {model['description']}\n"
            except:
                pass

            # Add DuckDB tables info
            try:
                tables = await adapters["duckdb"].get_tables()
                enhanced_context += f"\nDuckDB Tables ({len(tables)} tables):\n"
                for table in tables[:5]:  # Limit to first 5
                    enhanced_context += f"- {table['schema']}.{table['name']}: {table.get('row_count', 'N/A')} rows\n"
            except:
                pass

            # Add DataHub datasets info
            try:
                datasets = await adapters["datahub"].get_datasets()
                enhanced_context += f"\nDataHub Datasets ({len(datasets)} datasets):\n"
                for dataset in datasets[:5]:  # Limit to first 5
                    enhanced_context += f"- {dataset['name']} ({dataset['platform']}): {dataset.get('description', 'N/A')}\n"
            except:
                pass

            return enhanced_context

        except Exception as e:
            logger.error(f"Error enhancing context: {e}")
            return context

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Rough estimation: 1 token per 4 characters
        return len(text) // 4

    async def generate_sql_query(self, request: dict[str, Any]) -> dict[str, Any]:
        """Generate SQL queries based on natural language"""
        try:
            if not self.chat_model:
                await self.initialize()

            question = request.get("question", "")
            schema_info = request.get("schema_info", "")
            database_type = request.get("database_type", "snowflake")

            system_message = SystemMessage(
                content=f"""
            You are an expert SQL developer specializing in {database_type}.
            Generate SQL queries based on natural language questions.

            Schema Information:
            {schema_info}

            Guidelines:
            - Use proper {database_type} syntax
            - Include appropriate WHERE clauses
            - Use JOINs when necessary
            - Optimize for performance
            - Include comments explaining complex logic
            """
            )

            human_message = HumanMessage(
                content=f"Generate a SQL query for: {question}"
            )

            response = await self.chat_model.agenerate(
                [[system_message, human_message]]
            )
            sql_query = response.generations[0][0].text

            return {
                "sql_query": sql_query,
                "database_type": database_type,
                "model": settings.openai_model,
                "tokens_used": self._estimate_tokens(question + sql_query),
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error generating SQL query: {e}")
            return {
                "sql_query": f"-- Error generating SQL: {str(e)}",
                "database_type": database_type,
                "model": settings.openai_model,
                "tokens_used": 0,
                "generated_at": datetime.now().isoformat(),
            }

    async def explain_data_lineage(self, request: dict[str, Any]) -> dict[str, Any]:
        """Explain data lineage and dependencies"""
        try:
            dataset_name = request.get("dataset_name", "")
            lineage_info = request.get("lineage_info", {})

            if not self.chat_model:
                await self.initialize()

            system_message = SystemMessage(
                content="""
            You are a data lineage expert. Explain data lineage and dependencies
            in a clear, understandable way. Include:
            - Data sources and origins
            - Transformation steps
            - Dependencies between datasets
            - Impact analysis
            - Data quality considerations
            """
            )

            human_message = HumanMessage(
                content=f"""
            Explain the data lineage for dataset: {dataset_name}

            Lineage Information:
            {lineage_info}
            """
            )

            response = await self.chat_model.agenerate(
                [[system_message, human_message]]
            )
            explanation = response.generations[0][0].text

            return {
                "explanation": explanation,
                "dataset_name": dataset_name,
                "model": settings.openai_model,
                "tokens_used": self._estimate_tokens(str(lineage_info) + explanation),
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error explaining data lineage: {e}")
            return {
                "explanation": f"Error explaining data lineage: {str(e)}",
                "dataset_name": dataset_name,
                "model": settings.openai_model,
                "tokens_used": 0,
                "generated_at": datetime.now().isoformat(),
            }
