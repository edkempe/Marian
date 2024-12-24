#!/usr/bin/env python3

"""Interactive interface for the Marian Catalog System."""

import argparse
import readline
import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import readchar
from app_catalog import CatalogChat

def get_input(prompt: str) -> str:
    """Get input from user, supporting ESC to exit."""
    print(prompt, end='', flush=True)
    chars = []
    while True:
        char = readchar.readchar()
        if char == readchar.key.ESC:
            print("\nExiting...")
            sys.exit(0)
        elif char == readchar.key.ENTER:
            print()  # Move to next line
            return ''.join(chars)
        elif char == readchar.key.BACKSPACE:
            if chars:
                chars.pop()
                # Move cursor back, print space, move cursor back again
                print('\b \b', end='', flush=True)
        elif ord(char) >= 32:  # Printable characters
            chars.append(char)
            print(char, end='', flush=True)

MENU_OPTIONS = {
    1: {'name': 'Catalog item search', 'help': 'Search catalog items by title or content'},
    2: {'name': 'Catalog search by tag', 'help': 'Search catalog items by tag name'},
    3: {'name': 'List tags', 'help': 'Show all available tags'},
    4: {'name': 'List recent items', 'help': 'Show recently added or modified items'},
    5: {'name': 'Add catalog item', 'help': 'Add a new item to the catalog'},
    6: {'name': 'Create new tag', 'help': 'Create a new tag'},
    7: {'name': 'Tag item', 'help': 'Apply a tag to an item'},
    8: {'name': 'Chat mode', 'help': 'Drop to command-line interface'},
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
    'menu': {
        'format': 'menu',
        'help': 'Return to main menu',
        'example': 'menu'
    },
    'exit': {
        'format': 'exit',
        'help': 'Exit the program',
        'example': 'exit'
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
        self.setup_readline()
        
    def setup_readline(self):
        """Set up readline with command history and tab completion."""
        # Set up command history
        histfile = os.path.join(os.path.expanduser("~"), ".marian_history")
        try:
            readline.read_history_file(histfile)
            readline.set_history_length(1000)
        except FileNotFoundError:
            pass
        
        # Enable tab completion
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.complete)
        readline.set_completer_delims(' \t\n;')
    
    def complete(self, text: str, state: int) -> Optional[str]:
        """Handle tab completion for commands and arguments."""
        buffer = readline.get_line_buffer()
        if not buffer.strip():
            matches = [cmd + ' ' for cmd in COMMANDS.keys() if cmd.startswith(text)]
        else:
            cmd = buffer.split()[0].lower()
            if cmd in COMMANDS:
                matches = []  # Add command-specific completion here
        return matches[state] if state < len(matches) else None
    
    def show_menu(self):
        """Display the main menu."""
        print("\nMarian Catalog System")
        print("===================")
        for num, option in MENU_OPTIONS.items():
            print(f"{num}) {option['name']:<20} - {option['help']}")
    
    def handle_menu_option(self, option: int) -> bool:
        """Handle a menu selection. Returns True if should exit."""
        if option == 1:  # Catalog item search
            query = get_input("\nEnter search terms: ").strip()
            if query:
                response = self.chat.process_input('search', query)
                print(response)
            return False
        
        elif option == 2:  # Catalog search by tag
            tag = get_input("\nEnter tag name: ").strip()
            if tag:
                response = self.chat.process_input('search_by_tag', tag)
                print(response)
            return False
        
        elif option == 3:  # List tags
            include_archived = get_input("\nInclude archived tags? (y/n) [n]: ").strip().lower() == 'y'
            response = self.chat.process_input('list_tags', 'archived' if include_archived else '')
            print(response)
            return False
        
        elif option == 4:  # List recent items
            days = get_input("\nShow items from last N days [7]: ").strip()
            days = int(days) if days.isdigit() else 7
            response = self.chat.process_input('list_recent', str(days))
            print(response)
            return False
        
        elif option == 5:  # Add catalog item
            title = get_input("\nEnter title: ").strip()
            if title:
                print("Enter content (Ctrl+D or empty line to finish):")
                content_lines = []
                while True:
                    try:
                        line = get_input("")
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
            tag_name = get_input("\nEnter new tag name: ").strip()
            if tag_name:
                response = self.chat.process_input('create_tag', tag_name)
                print(response)
            return False
        
        elif option == 7:  # Tag item
            title = get_input("\nEnter item title: ").strip()
            tag = get_input("Enter tag name: ").strip()
            if title and tag:
                response = self.chat.process_input('tag', f"{title} {tag}")
                print(response)
            return False
        
        elif option == 8:  # Chat mode
            print("\nEntering command-line mode. Type 'menu' to return to menu, 'help' or '?' for commands.")
            self.run_command_mode()
            return False  # Continue to menu after chat mode
        
        elif option == 9:  # Exit
            return True
        
        return False
    
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
            for cmd, info in COMMANDS.items():
                print(f"  {info['format']:<25} : {info['help']}")
            print("\nType 'help <command>' or '? <command>' for more details about a specific command")
    
    def run_command_mode(self):
        """Run the command-line interface."""
        while True:
            try:
                command = get_input("\n> ")
                
                if not command:
                    continue
                
                parts = command.split(maxsplit=1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                if cmd in ('exit', 'q', 'quit'):
                    break
                elif cmd == 'menu':
                    return
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
                print("\nUse 'exit', 'quit', or 'q' to quit, 'menu' to return to menu, or press ESC")
                print("Type 'help' or '?' for available commands")
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def run(self):
        """Run the interactive interface."""
        print("\nWelcome to the Marian Catalog System")
        print("Type Ctrl+C to cancel current operation, ESC to exit")
        
        while True:
            try:
                self.show_menu()
                choice = get_input("\nSelect an option [1-9] or 'q'/'quit' to quit: ")
                choice = choice.lower()
                
                if choice in ('q', 'quit'):
                    break
                
                if not choice.isdigit() or int(choice) not in MENU_OPTIONS:
                    print("Please enter a number between 1 and 9 or 'q'/'quit' to quit (ESC to exit)")
                    continue
                
                if self.handle_menu_option(int(choice)):
                    break
                
                if int(choice) != 8:  # Don't pause after chat mode
                    get_input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\nOperation cancelled")
                continue
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                get_input("\nPress Enter to continue...")
        
        # Save command history
        histfile = os.path.join(os.path.expanduser("~"), ".marian_history")
        try:
            readline.write_history_file(histfile)
        except Exception as e:
            print(f"Warning: Could not save command history: {e}")
        
        print("\nGoodbye!")

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
