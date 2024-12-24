#!/usr/bin/env python3

"""Interactive interface for the Marian Catalog System."""

import argparse
import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter, NestedCompleter
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style

from app_catalog import CatalogChat

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
    8: {'name': 'Menu mode', 'help': 'Switch to menu-driven interface'},
    9: {'name': 'Exit', 'help': 'Exit the program'}
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

class CatalogInteractive:
    """Interactive interface for the Marian Catalog System."""
    
    def __init__(self):
        """Initialize the interactive interface."""
        self.chat = CatalogChat(interactive=True)
        self.setup_prompt()
    
    def setup_prompt(self):
        """Set up prompt toolkit session with completions and key bindings."""
        # Create nested completer for commands and their arguments
        command_completer = self.create_command_completer()
        
        # Create key bindings
        kb = KeyBindings()
        
        @kb.add(Keys.Escape)
        def _(event):
            """Handle ESC key."""
            print("\nExiting...")
            sys.exit(0)
        
        # Create prompt session
        self.session = PromptSession(
            completer=command_completer,
            style=style,
            key_bindings=kb,
            complete_while_typing=True,
            enable_history_search=True,
            history=self.load_history()
        )
    
    def create_command_completer(self) -> NestedCompleter:
        """Create a nested completer for commands and their arguments."""
        # Filter out alias commands for completion
        main_commands = {cmd: None for cmd in COMMANDS.keys() 
                        if cmd not in ('q', '?', 'quit')}
        
        # Add special completions for specific commands
        main_commands['help'] = WordCompleter(list(COMMANDS.keys()))
        main_commands['?'] = WordCompleter(list(COMMANDS.keys()))
        
        # TODO: Add completions for item titles and tag names
        return NestedCompleter.from_nested_dict(main_commands)
    
    def load_history(self):
        """Load command history from file."""
        from prompt_toolkit.history import FileHistory
        histfile = os.path.join(os.path.expanduser("~"), ".marian_history")
        return FileHistory(histfile)
    
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
        while True:
            try:
                # Get command with prompt_toolkit
                command = self.session.prompt("\n> ")
                
                if not command:
                    continue
                
                parts = command.split(maxsplit=1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
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
                elif cmd not in COMMANDS:
                    print(f"Unknown command: {cmd}")
                    print("Type 'help' or '?' for available commands")
                    continue
                
                response = self.chat.process_input(cmd, args)
                print(response)
                
            except KeyboardInterrupt:
                print("\nUse 'exit', 'quit', or 'q' to quit, 'menu' for menu mode, or press ESC")
                print("Type 'help' or '?' for available commands")
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def run(self):
        """Run the interactive interface."""
        print("\nWelcome to the Marian Catalog System")
        print("Type Ctrl+C to cancel current operation, ESC to exit")
        print("Type 'help' or '?' for available commands, 'menu' for menu mode")
        
        while True:
            try:
                # Start in command-line mode
                if self.run_command_mode():
                    # Switch to menu mode
                    self.run_menu_mode()
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                self.session.prompt("\nPress Enter to continue...")
        
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
        print("-------------------")
        for num, option in MENU_OPTIONS.items():
            print(f"{num}. {option['name']:<20} : {option['help']}")
    
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
        
        elif option == 8:  # Return to chat mode
            return False
        
        elif option == 9:  # Exit
            return True
        
        return False

def main():
    """Run the catalog system in interactive mode."""
    try:
        interface = CatalogInteractive()
        interface.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
