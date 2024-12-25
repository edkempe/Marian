#!/usr/bin/env python3

"""Interactive interface for the Marian Catalog System."""

import argparse
import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion, WordCompleter, NestedCompleter
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory

from app_catalog import CatalogChat
from models.catalog import CatalogItem, Tag

# Style for syntax highlighting
style = Style.from_dict({
    'command': '#00aa00 bold',  # Green for commands
    'arg': '#0000aa',          # Blue for arguments
    'error': '#aa0000',        # Red for errors
    'help': '#00aaaa',         # Cyan for help text
})

MENU_OPTIONS = {
    1: {'name': 'Catalog item search', 'help': 'Search catalog items by title or content'},
    2: {'name': 'Catalog search by tag', 'help': 'Search catalog items by tag name'},
    3: {'name': 'List tags', 'help': 'Show all available tags'},
    4: {'name': 'List recent items', 'help': 'Show recently added or modified items'},
    5: {'name': 'Add catalog item', 'help': 'Add a new item to the catalog'},
    6: {'name': 'Create new tag', 'help': 'Create a new tag'},
    7: {'name': 'Tag item', 'help': 'Apply a tag to an item'},
    8: {'name': 'CLI mode', 'help': 'Switch to command-line interface'},
    9: {'name': 'Chat mode', 'help': 'Have a natural conversation with the catalog'}
}

# Command definitions for command-line mode
COMMANDS = {
    'add': {
        'format': 'add <title> - <content>',
        'help': 'Add a new catalog item',
        'example': 'add My Book - This is a great book about...'
    },
    'tag': {
        'format': 'tag <title> <tag>',
        'help': 'Add a tag to an item',
        'example': 'tag "My Book" fiction'
    },
    'list': {
        'format': 'list [archived]',
        'help': 'List all active items',
        'example': 'list'
    },
    'list_tags': {
        'format': 'list_tags [archived]',
        'help': 'List all tags (optionally including archived)',
        'example': 'list_tags'
    },
    'search': {
        'format': 'search <query>',
        'help': 'Search items by title or content',
        'example': 'search "programming"'
    },
    'info': {
        'format': 'info <title>',
        'help': 'Show detailed information about an item',
        'example': 'info "My Book"'
    },
    'archive': {
        'format': 'archive <title>',
        'help': 'Archive a catalog item',
        'example': 'archive "My Book"'
    },
    'archive_tag': {
        'format': 'archive_tag <tag_name>',
        'help': 'Archive a tag',
        'example': 'archive_tag fiction'
    },
    'restore': {
        'format': 'restore <title>',
        'help': 'Restore an archived item',
        'example': 'restore "My Book"'
    },
    'restore_tag': {
        'format': 'restore_tag <tag_name>',
        'help': 'Restore an archived tag',
        'example': 'restore_tag fiction'
    },
    'help': {
        'format': 'help [command]',
        'help': 'Show help for all commands or a specific command',
        'example': 'help tag'
    },
    '?': {
        'format': '? [command]',
        'help': 'Show help for all commands or a specific command',
        'example': '? tag'
    },
    'menu': {
        'format': 'menu',
        'help': 'Switch to menu-driven interface',
        'example': 'menu'
    },
    'clear': {
        'format': 'clear',
        'help': 'Clear the screen',
        'example': 'clear'
    },
    'exit': {
        'format': 'exit',
        'help': 'Exit the program',
        'example': 'exit'
    },
    'quit': {
        'format': 'quit',
        'help': 'Exit the program',
        'example': 'quit'
    },
    'q': {
        'format': 'q',
        'help': 'Exit the program',
        'example': 'q'
    },
    'create_tag': {
        'format': 'create_tag <tag_name>',
        'help': 'Create a new tag',
        'example': 'create_tag fiction'
    }
}

class CommandCompleter(Completer):
    """Custom completer that adds spaces after commands."""
    
    def __init__(self, commands):
        self.commands = commands
    
    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        
        for command in self.commands:
            if command.startswith(word):
                yield Completion(
                    command,
                    start_position=-len(word),
                    display=command,
                    display_meta='command',
                    text=command + ' '  # Add space after command
                )

class MultiCompleter(Completer):
    """Completer that combines multiple completers."""
    
    def __init__(self, completers):
        self.completers = completers
    
    def get_completions(self, document, complete_event):
        for completer in self.completers:
            yield from completer.get_completions(document, complete_event)

class CatalogInteractive:
    """Interactive interface for the Marian Catalog System."""
    
    def __init__(self):
        """Initialize the interactive interface."""
        self.chat = CatalogChat(interactive=True)
        self.setup_prompt()
    
    def setup_prompt(self):
        """Set up prompt toolkit session with completions and key bindings."""
        # Set up key bindings
        kb = KeyBindings()
        
        # Add ESC binding
        @kb.add('escape')
        def _(event):
            """Handle ESC key."""
            sys.exit(0)
        
        # Create completers
        command_completer = CommandCompleter(COMMANDS.keys())
        nested_completer = self.create_command_completer()
        multi_completer = MultiCompleter([command_completer, nested_completer])
        
        # Initialize prompt session
        self.session = PromptSession(
            completer=multi_completer,
            key_bindings=kb,
            style=style,
            history=self.load_history(),
            complete_while_typing=True,
            enable_history_search=True
        )
    
    def create_command_completer(self):
        """Create a nested completer for commands and their arguments."""
        session = self.chat.get_session()
        
        # Get active item titles for completion
        active_items = session.query(CatalogItem.title).filter(
            CatalogItem.deleted == False
        ).all()
        item_titles = [item[0] for item in active_items]
        
        # Get all tags for completion
        tags = session.query(Tag.name).filter(Tag.deleted == False).all()
        tag_names = [tag[0] for tag in tags]
        
        # Create completers for different argument types
        tag_completer = WordCompleter(tag_names, sentence=True)
        item_completer = WordCompleter(item_titles, sentence=True)
        archived_completer = WordCompleter(['archived'], sentence=True)
        
        # Build nested completer dictionary
        completions = {}
        
        # Commands with no arguments
        for cmd in ['exit', 'quit', 'q', 'menu', 'clear']:
            completions[cmd] = None
        
        # Commands with specific completions
        completions['archive'] = item_completer
        completions['search'] = None
        completions['search_by_tag'] = tag_completer
        completions['list'] = archived_completer
        completions['list_tags'] = archived_completer
        completions['list_recent'] = None
        completions['add'] = None
        completions['restore'] = None
        completions['create_tag'] = None
        completions['help'] = WordCompleter(list(COMMANDS.keys()))
        completions['?'] = WordCompleter(list(COMMANDS.keys()))
        
        # Special handling for tag command (item followed by tag)
        tag_dict = {}
        for item in item_titles:
            tag_dict[item] = tag_completer
        completions['tag'] = tag_dict
        
        # Create a custom completer for commands
        command_completer = CommandCompleter(completions.keys())
        
        # Return a completer that first tries command completion, then nested completion
        return NestedCompleter.from_nested_dict(completions)
    
    def load_history(self):
        """Load command history from file."""
        history_file = os.path.expanduser('~/.marian_history')
        return FileHistory(history_file)
    
    def show_help(self, command: Optional[str] = None):
        """Show help for all commands or a specific command."""
        if command and command in COMMANDS:
            cmd_info = COMMANDS[command]
            print(f"\nCommand: {command}")
            print(f"Format:  {cmd_info['format']}")
            print(f"Help:    {cmd_info['help']}")
            print(f"Example: {cmd_info['example']}")
        else:
            print("\nAvailable commands:")
            # Filter out alias commands from the main help display
            main_commands = {cmd: info for cmd, info in COMMANDS.items() 
                           if cmd not in ('q', '?', 'quit')}
            for cmd, info in main_commands.items():
                print(f"  {info['format']:<25} : {info['help']}")
            print("\nType 'help <command>' or '? <command>' for more details about a specific command")
    
    def run_command_mode(self):
        """Run the command-line interface."""
        print("\nEntering CLI mode. Type 'menu' to return to menu, 'help' or '?' for commands")
        while True:
            try:
                # Refresh completer before each command to ensure up-to-date completions
                self.session.completer = self.create_command_completer()
                
                # Get command with prompt_toolkit
                command = self.session.prompt("\n> ")
                
                if not command:
                    continue
                
                parts = command.split(maxsplit=1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                # Handle built-in commands first
                if cmd in ('exit', 'q', 'quit'):
                    sys.exit(0)
                elif cmd == 'menu':
                    return True  # Return to menu mode
                elif cmd == 'clear':
                    clear()
                    continue
                elif cmd in ('help', '?'):
                    self.show_help(args if args else None)
                    continue
                
                # Handle catalog commands
                try:
                    response = self.chat.process_input(cmd, args)
                    print(response)
                except Exception as e:
                    if cmd not in COMMANDS:
                        print(f"Unknown command: {cmd}")
                        print("Type 'help' or '?' for available commands")
                    else:
                        print(f"Error: {str(e)}")
                
            except KeyboardInterrupt:
                print("\nUse 'exit', 'quit', or 'q' to quit, 'menu' for menu mode, or press ESC")
                print("Type 'help' or '?' for available commands")
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                self.session.prompt("\nPress Enter to continue...")
    
    def run_chat_mode(self):
        """Run the natural language chat interface."""
        print("\nEntering chat mode. Type 'exit' to return to menu.")
        print("You can now have a natural conversation with the catalog system.")
        print("Examples:")
        print("- Show me all items about machine learning")
        print("- Find documents tagged with 'python' from last week")
        print("- Add a new item about data structures")
        
        while True:
            try:
                user_input = self.session.prompt('You: ', style=style)
                
                if user_input.lower() in ['exit', 'quit', 'back']:
                    break
                    
                if not user_input.strip():
                    continue
                
                # Process the natural language query
                analysis = self.chat.process_natural_language_query(user_input)
                
                if analysis['intent'] == 'search':
                    # Perform semantic search
                    items = self.chat.semantic_search(user_input)
                    if items:
                        print("\nFound these relevant items:")
                        for i, item in enumerate(items, 1):
                            print(f"\n{i}. {item.title}")
                            print(f"   {item.content[:200]}...")
                            if item.tags:
                                tags = [tag.name for tag in item.tags]
                                print(f"   Tags: {', '.join(tags)}")
                    else:
                        print("\nNo matching items found.")
                        
                elif analysis['intent'] == 'add':
                    # Extract title and content from entities
                    title = analysis['entities'].get('title', '')
                    content = analysis['entities'].get('content', '')
                    tags = analysis['entities'].get('tags', [])
                    
                    if title and content:
                        # Confirm with user
                        print("\nI'll help you add this item:")
                        print(f"Title: {title}")
                        print(f"Content: {content}")
                        if tags:
                            print(f"Tags: {', '.join(tags)}")
                        
                        confirm = self.session.prompt(
                            '\nLook good? (yes/no): ',
                            style=style
                        ).lower()
                        
                        if confirm.startswith('y'):
                            # Add the item
                            self.chat.execute_command(f"add {title} - {content}")
                            # Add tags if present
                            for tag in tags:
                                self.chat.execute_command(f"tag {title} {tag}")
                            print("\nItem added successfully!")
                    else:
                        print("\nI couldn't extract a clear title and content. Please try again with more details.")
                
                elif analysis['intent'] == 'list':
                    # List items with any filters
                    filters = []
                    if 'date' in analysis['filters']:
                        date_filter = analysis['filters']['date']
                        if date_filter.get('start'):
                            filters.append(f"after:{date_filter['start']}")
                        if date_filter.get('end'):
                            filters.append(f"before:{date_filter['end']}")
                    
                    if 'tags' in analysis['filters']:
                        for tag in analysis['filters']['tags']:
                            filters.append(f"tag:{tag}")
                    
                    filter_str = ' '.join(filters) if filters else ''
                    result = self.chat.execute_command(f"list {filter_str}")
                    print(f"\n{result}")
                
                else:
                    print("\nI'm not sure what you want to do. Try rephrasing your request.")
                
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
                continue

    def run(self):
        """Run the interactive interface."""
        print("\nWelcome to the Marian Catalog System")
        print("Type Ctrl+C to cancel current operation, ESC to exit")
        print("Type 'help' or '?' for available commands, 'menu' for menu mode")
        
        try:
            self.run_command_mode()
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Press Enter to continue...")
            input()
        
        print("\nGoodbye!")
    
    def run_menu_mode(self):
        """Run the menu-driven interface."""
        while True:
            try:
                self.show_menu()
                choice = self.session.prompt("\nSelect an option [1-9] or 'q'/'quit' to quit: ")
                choice = choice.lower()
                
                if choice in ('q', 'quit'):
                    sys.exit(0)
                
                if not choice.isdigit() or int(choice) not in MENU_OPTIONS:
                    print("Please enter a number between 1 and 9 or 'q'/'quit' to quit (ESC to exit)")
                    continue
                
                if self.handle_menu_option(int(choice)):
                    sys.exit(0)
                
                if int(choice) != 8:  # Don't pause after returning to chat mode
                    self.session.prompt("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\nOperation cancelled")
                continue
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                self.session.prompt("\nPress Enter to continue...")
    
    def show_menu(self):
        """Display the main menu."""
        print("\nMarian Catalog System")
        print("=" * 20)
        for option_num, option in MENU_OPTIONS.items():
            print(f"{option_num}. {option['name']}")
        print("\nPress ESC to exit")
    
    def handle_menu_option(self, option: int) -> bool:
        """Handle a menu selection. Returns True if should exit."""
        if option == 1:  # Catalog item search
            query = self.session.prompt("\nEnter search terms: ").strip()
            if query:
                response = self.chat.process_input('search', query)
                print(response)
            return False
        
        elif option == 2:  # Catalog search by tag
            tag = self.session.prompt("\nEnter tag name: ").strip()
            if tag:
                response = self.chat.process_input('search_by_tag', tag)
                print(response)
            return False
        
        elif option == 3:  # List tags
            include_archived = self.session.prompt("\nInclude archived tags? (y/n) [n]: ").strip().lower() == 'y'
            response = self.chat.process_input('list_tags', 'archived' if include_archived else '')
            print(response)
            return False
        
        elif option == 4:  # List recent items
            days = self.session.prompt("\nShow items from last N days [7]: ").strip()
            days = int(days) if days.isdigit() else 7
            response = self.chat.process_input('list_recent', str(days))
            print(response)
            return False
        
        elif option == 5:  # Add catalog item
            title = self.session.prompt("\nEnter title: ").strip()
            if title:
                print("Enter content (Ctrl+D or empty line to finish):")
                content_lines = []
                while True:
                    try:
                        line = self.session.prompt("")
                        if not line and content_lines:
                            break
                        content_lines.append(line)
                    except EOFError:
                        break
                content = "\n".join(content_lines)
                if content:
                    response = self.chat.process_input('add', f"{title} - {content}")
                    print(response)
            return False
        
        elif option == 6:  # Create new tag
            tag_name = self.session.prompt("\nEnter new tag name: ").strip()
            if tag_name:
                response = self.chat.process_input('create_tag', tag_name)
                print(response)
            return False
        
        elif option == 7:  # Tag item
            title = self.session.prompt("\nEnter item title: ").strip()
            tag = self.session.prompt("Enter tag name: ").strip()
            if title and tag:
                response = self.chat.process_input('tag', f"{title} {tag}")
                print(response)
            return False
        
        elif option == 8:  # CLI mode
            return self.run_command_mode()
        
        elif option == 9:  # Chat mode
            return self.run_chat_mode()
        
        return False

def main():
    """Run the catalog system in interactive mode."""
    try:
        interactive = CatalogInteractive()
        interactive.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
