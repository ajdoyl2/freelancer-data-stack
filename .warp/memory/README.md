# 🧠 AI Agent Memory System

A sophisticated memory management system for AI agents that provides persistent memory capabilities using DuckDB. The system stores conversations, reasoning traces, memory fragments, and user context to enable agents to learn and adapt over time.

## 🚀 Features

- **Persistent Memory**: Store and retrieve facts, patterns, preferences, rules, and context
- **Conversation Tracking**: Record full conversation histories with reasoning traces
- **User Preferences**: Persistent user preferences and context management
- **Agent State**: Stateful agent behavior across sessions
- **Search & Recall**: Semantic search and importance-based memory retrieval
- **Memory Cleanup**: Automated cleanup of old or low-importance memories
- **Export/Import**: Full data export capabilities

## 📦 Architecture

### Database Schema
- **conversations**: Agent conversation sessions
- **messages**: Individual conversation messages
- **memory_fragments**: Extracted knowledge and patterns
- **reasoning_traces**: Step-by-step agent reasoning
- **agent_states**: Persistent agent state
- **user_context**: User preferences and context

### Components
1. **AgentMemoryManager**: Core memory operations
2. **WarpAgentMemory**: Specialized Warp terminal integration
3. **CLI Tools**: Command-line memory management
4. **Shell Integration**: Easy-to-use shell functions

## 🛠 Installation

The memory system is automatically installed when you source the agent functions:

```bash
source .warp/agent_functions.sh
```

This creates the database at `~/.warp/memory/agent_memory.duckdb` and sets up all CLI functions.

## 📖 Usage

### Quick Commands

| Command | Alias | Description |
|---------|--------|-------------|
| `mem_stats` | `ms` | Show memory statistics |
| `mem_remember` | `mr` | Store a memory fragment |
| `mem_recall` | `mrc` | Search and recall memories |
| `mem_context` | `mx` | Show conversation context |
| `mem_prefs` | `mp` | Manage user preferences |

### Examples

#### Remember Information
```bash
# Remember a fact
mr fact "User prefers concise explanations" 0.8

# Remember a pattern
mr pattern "User frequently works with Python data pipelines" 0.9

# Remember a preference
mr preference "Terminal: Warp, Shell: zsh" 0.6

# Remember a rule
mr rule "Always use Poetry for Python dependency management" 0.9
```

#### Recall Information
```bash
# Search for memories about Python
mrc "Python"

# Search with limit
mrc "data pipelines" 3

# Search by type
mem_search --type pattern "workflow"
```

#### Manage Preferences
```bash
# View all preferences
mp

# Set a preference
mp coding_style "pythonic and clean"
mp verbosity "concise"
```

#### View Context
```bash
# Show current conversation context
mx

# View memory statistics
ms
```

### Advanced Usage

#### Direct CLI Access
```bash
# Full CLI with all options
python3 ~/.warp/memory/memory_cli.py --help

# Search with filters
python3 ~/.warp/memory/memory_cli.py search "python" --type fact --limit 5

# Export data
python3 ~/.warp/memory/memory_cli.py export --output backup.json

# Cleanup old data
python3 ~/.warp/memory/memory_cli.py cleanup --days 7
```

#### Python Integration
```python
from memory_manager import AgentMemoryManager
from agent_integration import WarpAgentMemory

# Basic usage
memory = WarpAgentMemory()
memory.remember("fact", "Important information", importance=0.8)
results = memory.recall("important")

# Full conversation tracking
conv_id = memory.start_conversation("Testing memory system")
memory.add_user_message("How do I remember things?")
memory.add_assistant_message("You can use the memory system...")
memory.end_conversation("Successfully demonstrated memory usage")
```

## 🎯 Memory Fragment Types

### 1. **Fact**
Concrete, factual information that doesn't change frequently.
```bash
mr fact "User's working directory is /Users/ajdoyle/data-stack"
```

### 2. **Pattern** 
Behavioral patterns and workflows observed over time.
```bash
mr pattern "User typically runs tests after making code changes"
```

### 3. **Preference**
User preferences and configuration choices.
```bash
mr preference "Prefers JSON output format over XML"
```

### 4. **Rule**
Explicit rules and constraints that should always be followed.
```bash
mr rule "Never commit directly to main branch"
```

### 5. **Context**
Situational context that might be temporarily relevant.
```bash
mr context "Currently working on memory system implementation"
```

## 🔧 Configuration

### Memory Retention
- **High Importance (0.8-1.0)**: Kept indefinitely
- **Medium Importance (0.5-0.7)**: Kept for 90 days
- **Low Importance (0.0-0.4)**: Kept for 30 days

### Default Preferences
The system automatically sets up default preferences:
- `shell`: Current shell (from $SHELL)
- `terminal`: "warp"
- `work_directory`: Current working directory
- `coding_style`: "pythonic"
- `verbosity`: "concise"

## 📊 Memory Analytics

View detailed statistics about your memory system:

```bash
ms  # Quick stats
```

Sample output:
```
🧠 AI Agent Memory Statistics
========================================
📊 Total Conversations: 15
💬 Total Messages: 127
🔥 Recent Activity (7 days): 8

📚 Memory Fragments by Type:
  Fact: 23
  Pattern: 15
  Preference: 8
  Rule: 12
  Context: 5

🔍 Total Memory Fragments: 63
```

## 🧹 Maintenance

### Cleanup Old Data
```bash
# Clean data older than 30 days (default)
mem_cleanup

# Clean data older than 7 days
mem_cleanup 7
```

### Backup and Export
```bash
# Export all memory data
mem_export

# Export to specific file
mem_export --output "backup_$(date +%Y%m%d).json"
```

## 🚨 Troubleshooting

### Common Issues

1. **Database not found**
   ```bash
   # Reload agent functions to recreate database
   source .warp/agent_functions.sh
   ```

2. **Permission errors**
   ```bash
   # Fix permissions
   chmod +x ~/.warp/memory/memory_cli.py
   ```

3. **Import errors**
   ```bash
   # Ensure Python dependencies are available
   pip install duckdb
   ```

### Debug Mode
```bash
# Enable debug output
DEBUG=1 mem_stats
```

## 🔮 Advanced Features

### Conversation Context Injection
The memory system can provide context for AI prompts:

```python
from agent_integration import get_context_for_prompt

context = get_context_for_prompt()
prompt = f"""
{context}

User Question: How do I optimize this code?
"""
```

### Command Success/Failure Tracking
```python
memory = WarpAgentMemory()

# Track successful commands
memory.remember_command_success(
    command="pytest tests/",
    output="5 passed, 0 failed",
    context="Running unit tests"
)

# Track failures for learning
memory.remember_command_failure(
    command="npm install",
    error="Package not found",
    context="Setting up JS project"
)
```

### Workflow Pattern Recognition
```python
# Store workflow patterns
memory.remember_user_workflow(
    workflow_name="Feature Development",
    steps=[
        "Create feature branch",
        "Write tests",
        "Implement feature",
        "Run test suite",
        "Create PR"
    ],
    context="Standard development workflow"
)
```

## 📚 API Reference

See the Python docstrings in `memory_manager.py` and `agent_integration.py` for complete API documentation.

## 🤝 Contributing

To extend the memory system:

1. Add new fragment types in the schema
2. Extend the CLI with new commands
3. Add shell function wrappers
4. Update this documentation

## 📄 License

This memory system is part of the AI Agent enhancement stack and follows the same license as the parent project.

---

*Generated by AI Agent Memory System v1.0 - Never forget, always learn!* 🧠✨
