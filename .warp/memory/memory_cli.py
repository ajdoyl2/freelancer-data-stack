#!/usr/bin/env python3
"""
Memory CLI Tool

Command-line interface for managing AI agent memory system.
Provides commands for viewing, searching, and managing memory data.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agent_integration import get_warp_memory
from memory_manager import AgentMemoryManager


def format_memory_fragment(fragment: dict) -> str:
    """Format memory fragment for display"""
    content = fragment["content"]
    if len(content) > 100:
        content = content[:97] + "..."

    return f"""
  [{fragment['fragment_type'].upper()}] {content}
  Importance: {fragment['importance_score']:.2f} | Confidence: {fragment['confidence_score']:.2f}
  Accessed: {fragment['access_count']} times | Last: {fragment['last_accessed']}
  Tags: {', '.join(fragment['tags']) if fragment['tags'] else 'None'}
"""


def format_conversation(convo: dict) -> str:
    """Format conversation for display"""
    start_time = convo["start_time"]
    end_time = convo["end_time"] or "Ongoing"
    summary = convo["context_summary"] or "No summary"

    return f"""
  Session: {convo['session_id']} | Agent: {convo['agent_name']}
  Started: {start_time} | Ended: {end_time}
  Summary: {summary}
  Tags: {', '.join(convo['tags']) if convo['tags'] else 'None'}
"""


def cmd_stats(args):
    """Show memory system statistics"""
    memory = AgentMemoryManager()
    stats = memory.get_memory_stats()

    print("🧠 AI Agent Memory Statistics")
    print("=" * 40)
    print(f"📊 Total Conversations: {stats['total_conversations']}")
    print(f"💬 Total Messages: {stats['total_messages']}")
    print(f"🔥 Recent Activity (7 days): {stats['conversations_last_week']}")

    fragments = stats.get("memory_fragments", {})
    if fragments:
        print("\n📚 Memory Fragments by Type:")
        for frag_type, count in fragments.items():
            print(f"  {frag_type.capitalize()}: {count}")

    total_fragments = sum(fragments.values()) if fragments else 0
    print(f"\n🔍 Total Memory Fragments: {total_fragments}")


def cmd_search(args):
    """Search memory fragments"""
    memory = AgentMemoryManager()

    results = memory.search_memory_fragments(
        query=args.query if hasattr(args, "query") else None,
        fragment_type=args.type if hasattr(args, "type") else None,
        limit=args.limit if hasattr(args, "limit") else 10,
        min_importance=args.min_importance if hasattr(args, "min_importance") else 0.0,
    )

    if not results:
        print("🔍 No memory fragments found matching your criteria.")
        return

    print(f"🔍 Found {len(results)} memory fragments:")
    print("=" * 60)

    for i, fragment in enumerate(results, 1):
        print(f"\n{i}. {format_memory_fragment(fragment)}")


def cmd_conversations(args):
    """Show recent conversations"""
    memory = AgentMemoryManager()

    conversations = memory.get_conversation_history(
        agent_name=args.agent if hasattr(args, "agent") else None,
        user_id=args.user if hasattr(args, "user") else None,
        limit=args.limit if hasattr(args, "limit") else 10,
    )

    if not conversations:
        print("💬 No conversations found.")
        return

    print(f"💬 Recent Conversations ({len(conversations)}):")
    print("=" * 60)

    for i, convo in enumerate(conversations, 1):
        print(f"\n{i}. {format_conversation(convo)}")


def cmd_remember(args):
    """Add a memory fragment"""
    memory = get_warp_memory()

    fragment_id = memory.remember(
        fragment_type=args.type,
        content=args.content,
        importance=args.importance,
        tags=args.tags.split(",") if args.tags else [],
    )

    print(f"✅ Remembered fragment: {fragment_id}")
    print(f"Type: {args.type}")
    print(f"Content: {args.content}")
    print(f"Importance: {args.importance}")


def cmd_recall(args):
    """Recall memory fragments"""
    memory = get_warp_memory()

    results = memory.recall(
        query=args.query,
        fragment_type=args.type if hasattr(args, "type") else None,
        limit=args.limit if hasattr(args, "limit") else 5,
    )

    if not results:
        print(f"🔍 No memories found for: {args.query}")
        return

    print(f"🧠 Recalled {len(results)} memories about '{args.query}':")
    print("=" * 60)

    for i, memory_item in enumerate(results, 1):
        print(f"\n{i}. {format_memory_fragment(memory_item)}")


def cmd_cleanup(args):
    """Clean up old memory data"""
    memory = AgentMemoryManager()

    days = args.days if hasattr(args, "days") else 30

    print(f"🧹 Cleaning up data older than {days} days...")
    memory.cleanup_old_data(days_to_keep=days)
    print("✅ Cleanup completed!")


def cmd_context(args):
    """Get conversation context for agent"""
    memory = get_warp_memory()
    context = memory.get_conversation_context()

    if not context:
        print("📝 No conversation context available.")
        return

    print("📝 Current Conversation Context:")
    print("=" * 50)
    print(context)


def cmd_preferences(args):
    """Manage user preferences"""
    memory = get_warp_memory()

    if hasattr(args, "set_key") and args.set_key:
        # Set preference
        memory.set_preference(args.set_key, args.set_value, args.priority or 5)
        print(f"✅ Set preference: {args.set_key} = {args.set_value}")
    else:
        # Show preferences
        prefs = memory.get_preferences()
        if not prefs:
            print("⚙️ No preferences set.")
            return

        print("⚙️ User Preferences:")
        print("=" * 30)
        for key, value in prefs.items():
            print(f"  {key}: {value}")


def cmd_export(args):
    """Export memory data"""
    memory = AgentMemoryManager()

    # Get all data
    conversations = memory.get_conversation_history(limit=1000)
    fragments = memory.search_memory_fragments(limit=1000)

    export_data = {
        "export_date": datetime.now().isoformat(),
        "conversations": conversations,
        "memory_fragments": fragments,
        "stats": memory.get_memory_stats(),
    }

    filename = (
        args.output
        if hasattr(args, "output")
        else f"agent_memory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    with open(filename, "w") as f:
        json.dump(export_data, f, indent=2, default=str)

    print(f"📤 Exported memory data to: {filename}")
    print(f"   Conversations: {len(conversations)}")
    print(f"   Memory fragments: {len(fragments)}")


def main():
    """Main CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Agent Memory Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  memory stats                    # Show memory statistics
  memory search python            # Search for fragments about python
  memory remember fact "Python uses indentation" --importance 0.8
  memory recall "file operations" # Recall memories about file operations
  memory conversations            # Show recent conversations
  memory cleanup --days 7         # Clean up data older than 7 days
  memory context                  # Show current conversation context
  memory preferences              # Show user preferences
  memory export                   # Export all memory data
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Stats command
    subparsers.add_parser("stats", help="Show memory statistics")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search memory fragments")
    search_parser.add_argument("query", nargs="?", help="Search query")
    search_parser.add_argument("--type", help="Fragment type filter")
    search_parser.add_argument("--limit", type=int, default=10, help="Result limit")
    search_parser.add_argument(
        "--min-importance", type=float, default=0.0, help="Minimum importance score"
    )

    # Conversations command
    conv_parser = subparsers.add_parser(
        "conversations", help="Show recent conversations"
    )
    conv_parser.add_argument("--agent", help="Filter by agent name")
    conv_parser.add_argument("--user", help="Filter by user ID")
    conv_parser.add_argument("--limit", type=int, default=10, help="Result limit")

    # Remember command
    remember_parser = subparsers.add_parser("remember", help="Add a memory fragment")
    remember_parser.add_argument(
        "type",
        choices=["fact", "pattern", "preference", "rule", "context"],
        help="Fragment type",
    )
    remember_parser.add_argument("content", help="Content to remember")
    remember_parser.add_argument(
        "--importance", type=float, default=0.7, help="Importance score (0-1)"
    )
    remember_parser.add_argument("--tags", help="Comma-separated tags")

    # Recall command
    recall_parser = subparsers.add_parser("recall", help="Recall memory fragments")
    recall_parser.add_argument("query", help="What to recall")
    recall_parser.add_argument("--type", help="Fragment type filter")
    recall_parser.add_argument("--limit", type=int, default=5, help="Result limit")

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old data")
    cleanup_parser.add_argument("--days", type=int, default=30, help="Days to keep")

    # Context command
    subparsers.add_parser("context", help="Show conversation context")

    # Preferences command
    pref_parser = subparsers.add_parser("preferences", help="Manage user preferences")
    pref_parser.add_argument("--set-key", help="Preference key to set")
    pref_parser.add_argument("--set-value", help="Preference value to set")
    pref_parser.add_argument("--priority", type=int, help="Preference priority")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export memory data")
    export_parser.add_argument("--output", help="Output filename")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Route to appropriate command function
    command_functions = {
        "stats": cmd_stats,
        "search": cmd_search,
        "conversations": cmd_conversations,
        "remember": cmd_remember,
        "recall": cmd_recall,
        "cleanup": cmd_cleanup,
        "context": cmd_context,
        "preferences": cmd_preferences,
        "export": cmd_export,
    }

    if args.command in command_functions:
        try:
            command_functions[args.command](args)
        except Exception as e:
            print(f"❌ Error: {e}")
            if os.getenv("DEBUG"):
                import traceback

                traceback.print_exc()
    else:
        print(f"❌ Unknown command: {args.command}")
        parser.print_help()


if __name__ == "__main__":
    main()
