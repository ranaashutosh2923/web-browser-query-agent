"""
Command Line Interface for Web Browser Query Agent
"""

import argparse
import sys
import json
from main import WebBrowserQueryAgent

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Web Browser Query Agent - CLI Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py "Best places to visit in Delhi"
  python cli.py --interactive
  python cli.py --status
        """
    )

    parser.add_argument(
        'query',
        nargs='?',
        help='Query to process'
    )

    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Start interactive mode'
    )

    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='Show system status'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Initialize agent
    try:
        print("🚀 Initializing Web Browser Query Agent...")
        agent = WebBrowserQueryAgent()
        print("✅ Agent initialized successfully!\n")
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        sys.exit(1)

    # Handle different modes
    if args.status:
        show_status(agent)
    elif args.interactive:
        interactive_mode(agent, args.verbose)
    elif args.query:
        process_single_query(agent, args.query, args.verbose)
    else:
        parser.print_help()

def show_status(agent):
    """Show system status"""
    print("🔍 System Status")
    print("=" * 50)

    status = agent.get_system_status()

    print(f"Status: {status['status']}")
    print("\nComponents:")
    for component, status_val in status['components'].items():
        emoji = "✅" if status_val == "online" else "❌"
        print(f"  {emoji} {component}: {status_val}")

    print("\nConfiguration:")
    config = status.get('config', {})
    for key, value in config.items():
        print(f"  • {key}: {value}")

    print("\nCache Statistics:")
    cache_stats = status.get('cache_stats', {})
    if 'error' in cache_stats:
        print(f"  ❌ {cache_stats['error']}")
    else:
        print(f"  • Cached queries: {cache_stats.get('total_cached_queries', 0)}")

def process_single_query(agent, query, verbose=False):
    """Process a single query"""
    print(f"🔍 Processing query: {query}")
    print("=" * 50)

    result = agent.process_query(query)

    # Display result
    if result['type'] == 'invalid_query':
        print(f"❌ Invalid Query")
        print(f"Response: {result['response']}")
        print(f"Reason: {result['reason']}")

    elif result['type'] == 'search_result':
        print(f"✅ Search Result")
        print(f"Answer: {result['answer']}")
        print(f"\nSources ({result['total_sources']}):")
        for i, source in enumerate(result.get('sources', []), 1):
            print(f"  {i}. {source['title']}")
            if verbose:
                print(f"     {source['url']}")

        if result.get('cached'):
            print("\n💾 Result retrieved from cache")

    elif result['type'] == 'no_results':
        print(f"❌ No Results")
        print(f"Response: {result['response']}")

    elif result['type'] == 'error':
        print(f"❌ Error")
        print(f"Response: {result['response']}")

    print(f"\n⏱️  Processing time: {result['processing_time']:.2f} seconds")

def interactive_mode(agent, verbose=False):
    """Interactive mode"""
    print("🤖 Interactive Mode - Web Browser Query Agent")
    print("=" * 50)
    print("Enter your queries below. Type 'quit', 'exit', or press Ctrl+C to exit.")
    print("Commands:")
    print("  - status: Show system status")
    print("  - clear: Clear screen")
    print("  - help: Show this help")
    print()

    while True:
        try:
            query = input("🔍 Query: ").strip()

            if not query:
                continue

            if query.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break

            elif query.lower() == 'status':
                show_status(agent)
                continue

            elif query.lower() == 'clear':
                import os
                os.system('cls' if os.name == 'nt' else 'clear')
                continue

            elif query.lower() == 'help':
                print("Commands:")
                print("  - status: Show system status")
                print("  - clear: Clear screen")
                print("  - help: Show this help")
                print("  - quit/exit: Exit interactive mode")
                continue

            print()
            process_single_query(agent, query, verbose)
            print("\n" + "-" * 50 + "\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
