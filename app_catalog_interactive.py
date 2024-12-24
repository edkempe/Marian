#!/usr/bin/env python3

import argparse
from app_catalog import CatalogChat

def main():
    """Run the catalog system in interactive mode"""
    chat = CatalogChat(interactive=True)
    
    print("\nMarian Catalog System - Interactive Mode")
    print("----------------------------------------")
    
    while True:
        try:
            command = input("\nEnter command (or 'help' for commands, 'exit' to quit): ").strip()
            if command.lower() == 'exit':
                break
            elif command.lower() == 'help':
                print("\nAvailable commands:")
                print("  add <title> - <content>  : Add a new catalog item")
                print("  tag <title> <tag>        : Add a tag to an item")
                print("  list                     : List all items")
                print("  list_tags                : List all tags")
                print("  search <query>           : Search items")
                print("  archive <title>          : Archive an item")
                print("  archive_tag <name>       : Archive a tag")
                print("  restore <title>          : Restore an archived item")
                print("  restore_tag <name>       : Restore an archived tag")
                print("  delete <title>           : Permanently delete an item")
                print("  delete_tag <name>        : Permanently delete a tag")
                print("  exit                     : Exit the program")
                continue
            
            parts = command.split(maxsplit=1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            response = chat.process_input(cmd, args)
            print(response)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
