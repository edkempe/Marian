import sqlite3
import datetime
import json
import os
import argparse
from anthropic import Anthropic
from librarian_constants import CATALOG_CONFIG, TABLE_CONFIG, CREATE_CATALOG_TABLE, CREATE_TAGS_TABLE, CREATE_CATALOG_TAGS_TABLE, CREATE_CHAT_HISTORY_TABLE, CREATE_RELATIONSHIPS_TABLE, ERRORS
from marian_lib.anthropic_helper import get_anthropic_client, test_anthropic_connection

class CatalogChat:
    def __init__(self, interactive=False):
        self.interactive = interactive
        self.chat_log_file = CATALOG_CONFIG['CHAT_LOG_FILE']
        self.db_path = CATALOG_CONFIG['CATALOG_DB_FILE']
        self.client = get_anthropic_client()
        self.setup_database()
        
    def setup_database(self):
        """Initialize the catalog database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create all tables using schema from migrations
        cursor.execute(CREATE_CATALOG_TABLE)
        cursor.execute(CREATE_TAGS_TABLE)
        cursor.execute(CREATE_CATALOG_TAGS_TABLE)
        cursor.execute(CREATE_CHAT_HISTORY_TABLE)
        cursor.execute(CREATE_RELATIONSHIPS_TABLE)
        
        conn.commit()
        conn.close()
        
    def run_integration_tests(self):
        """Run a series of integration tests on the database and initialize with useful data"""
        print("Running integration tests and initializing database...")
        tests_passed = 0
        total_tests = 0
        
        def run_test(name, test_func):
            nonlocal tests_passed, total_tests
            total_tests += 1
            try:
                test_func()
                print(f"✓ {name}")
                tests_passed += 1
            except Exception as e:
                print(f"✗ {name}")
                print(f"  Error: {str(e)}")
        
        # Test database connection and schema
        def test_db_setup():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            assert len(tables) >= 5, "Not all tables were created"
        
        # Initialize catalog with core items
        def init_catalog_items():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Add core documentation items
            items = [
                ("Marian User Guide", "Main documentation for using the Marian system", "Complete guide for using Marian's features and capabilities"),
                ("Email Analysis Guide", "Documentation for email processing features", "Details about email analysis, classification, and storage"),
                ("Catalog System Guide", "Guide for the catalog and information management", "Documentation about organizing and retrieving information"),
            ]
            
            for title, desc, content in items:
                cursor.execute(
                    f"INSERT OR IGNORE INTO {TABLE_CONFIG['CATALOG_TABLE']} (title, description, content) VALUES (?, ?, ?)",
                    (title, desc, content)
                )
            
            conn.commit()
            conn.close()
            
        # Initialize tag system
        def init_tag_system():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Add core organizational tags
            core_tags = [
                "documentation",
                "guide",
                "email",
                "catalog",
                "system",
                "user",
                "analysis",
                "core"
            ]
            
            for tag in core_tags:
                cursor.execute(
                    f"INSERT OR IGNORE INTO {TABLE_CONFIG['TAGS_TABLE']} (name) VALUES (?)",
                    (tag,)
                )
            
            # Link tags to items
            cursor.execute(f"SELECT id FROM {TABLE_CONFIG['CATALOG_TABLE']} WHERE title = ?", ("Marian User Guide",))
            guide_id = cursor.fetchone()[0]
            
            cursor.execute(f"SELECT id FROM {TABLE_CONFIG['TAGS_TABLE']} WHERE name IN ('documentation', 'guide', 'user', 'core')")
            tag_ids = cursor.fetchall()
            
            for tag_id in tag_ids:
                cursor.execute(
                    f"INSERT OR IGNORE INTO {TABLE_CONFIG['CATALOG_TAGS_TABLE']} (catalog_id, tag_id) VALUES (?, ?)",
                    (guide_id, tag_id[0])
                )
            
            conn.commit()
            conn.close()
        
        # Test relationships
        def test_relationships():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get our core documentation items
            cursor.execute(f"SELECT id FROM {TABLE_CONFIG['CATALOG_TABLE']} WHERE title LIKE '%Guide%'")
            guide_ids = cursor.fetchall()
            
            if len(guide_ids) >= 2:
                # Create relationships between guides
                cursor.execute(
                    f"INSERT OR IGNORE INTO {TABLE_CONFIG['RELATIONSHIPS_TABLE']} (source_id, target_id, relationship_type) VALUES (?, ?, ?)",
                    (guide_ids[0][0], guide_ids[1][0], 'related_to')
                )
            
            conn.commit()
            conn.close()
            
        # Test complete lifecycle of catalog items and tags
        def test_full_lifecycle():
            """Test complete lifecycle of catalog items and tags"""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            print("\nRunning full lifecycle test:")
            
            # 1. Create test tag
            print("  Creating test tag...")
            test_tag_name = f"test_tag_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            cursor.execute(
                f"INSERT INTO {TABLE_CONFIG['TAGS_TABLE']} (name) VALUES (?)",
                (test_tag_name,)
            )
            cursor.execute(f"SELECT id FROM {TABLE_CONFIG['TAGS_TABLE']} WHERE name = ?", (test_tag_name,))
            test_tag_id = cursor.fetchone()[0]
            
            # 2. Add test content with existing and new tags
            print("  Adding test content...")
            cursor.execute(
                f"INSERT INTO {TABLE_CONFIG['CATALOG_TABLE']} (title, description, content) VALUES (?, ?, ?)",
                ("Test Item", "Test Description", "Test Content")
            )
            test_item_id = cursor.lastrowid
            
            # Get an existing tag (documentation)
            cursor.execute(f"SELECT id FROM {TABLE_CONFIG['TAGS_TABLE']} WHERE name = ?", ("documentation",))
            doc_tag_id = cursor.fetchone()[0]
            
            # Apply both tags
            print("  Applying tags...")
            cursor.execute(
                f"INSERT INTO {TABLE_CONFIG['CATALOG_TAGS_TABLE']} (catalog_id, tag_id) VALUES (?, ?)",
                (test_item_id, test_tag_id)
            )
            cursor.execute(
                f"INSERT INTO {TABLE_CONFIG['CATALOG_TAGS_TABLE']} (catalog_id, tag_id) VALUES (?, ?)",
                (test_item_id, doc_tag_id)
            )
            
            # 3. Query by tag and verify
            print("  Verifying tag query...")
            cursor.execute(f"""
                SELECT DISTINCT c.title, c.description 
                FROM {TABLE_CONFIG['CATALOG_TABLE']} c
                JOIN {TABLE_CONFIG['CATALOG_TAGS_TABLE']} ct ON c.id = ct.catalog_id
                JOIN {TABLE_CONFIG['TAGS_TABLE']} t ON ct.tag_id = t.id
                WHERE t.name = ?
            """, (test_tag_name,))
            result = cursor.fetchall()
            assert len(result) == 1, "Item not found by tag"
            assert result[0][0] == "Test Item", "Wrong item found by tag"
            
            # 4. Query by title and verify tags
            print("  Verifying content query...")
            cursor.execute(f"""
                SELECT t.name 
                FROM {TABLE_CONFIG['TAGS_TABLE']} t
                JOIN {TABLE_CONFIG['CATALOG_TAGS_TABLE']} ct ON t.id = ct.tag_id
                JOIN {TABLE_CONFIG['CATALOG_TABLE']} c ON ct.catalog_id = c.id
                WHERE c.title = ?
            """, ("Test Item",))
            tags = cursor.fetchall()
            assert len(tags) == 2, "Wrong number of tags found"
            tag_names = set(tag[0] for tag in tags)
            assert test_tag_name in tag_names, "Test tag not found"
            assert "documentation" in tag_names, "Documentation tag not found"
            
            # 5. Update content and verify
            print("  Testing content update...")
            cursor.execute(
                f"UPDATE {TABLE_CONFIG['CATALOG_TABLE']} SET description = ? WHERE id = ?",
                ("Updated Description", test_item_id)
            )
            cursor.execute(
                f"SELECT description FROM {TABLE_CONFIG['CATALOG_TABLE']} WHERE id = ?",
                (test_item_id,)
            )
            assert cursor.fetchone()[0] == "Updated Description", "Update failed"
            
            # 6. Remove one tag and verify
            print("  Testing tag removal...")
            cursor.execute(
                f"DELETE FROM {TABLE_CONFIG['CATALOG_TAGS_TABLE']} WHERE catalog_id = ? AND tag_id = ?",
                (test_item_id, doc_tag_id)
            )
            cursor.execute(f"""
                SELECT COUNT(*) FROM {TABLE_CONFIG['CATALOG_TAGS_TABLE']} WHERE catalog_id = ?
            """, (test_item_id,))
            assert cursor.fetchone()[0] == 1, "Wrong number of tags after removal"
            
            # 7. Clean up test data and verify
            print("  Cleaning up test data...")
            cursor.execute(
                f"DELETE FROM {TABLE_CONFIG['CATALOG_TAGS_TABLE']} WHERE catalog_id = ?",
                (test_item_id,)
            )
            cursor.execute(
                f"DELETE FROM {TABLE_CONFIG['CATALOG_TABLE']} WHERE id = ?",
                (test_item_id,)
            )
            cursor.execute(
                f"DELETE FROM {TABLE_CONFIG['TAGS_TABLE']} WHERE id = ?",
                (test_tag_id,)
            )
            
            # Verify cleanup
            cursor.execute(f"SELECT COUNT(*) FROM {TABLE_CONFIG['CATALOG_TABLE']} WHERE id = ?", (test_item_id,))
            assert cursor.fetchone()[0] == 0, "Item not properly deleted"
            cursor.execute(f"SELECT COUNT(*) FROM {TABLE_CONFIG['TAGS_TABLE']} WHERE id = ?", (test_tag_id,))
            assert cursor.fetchone()[0] == 0, "Tag not properly deleted"
            
            conn.commit()
            conn.close()
            print("  Full lifecycle test completed successfully")

        # Test Anthropic API connection
        def test_anthropic_api():
            """Test Anthropic API connection"""
            print("  Testing Anthropic API connection...")
            assert test_anthropic_connection(self.client), "Failed to connect to Anthropic API"
            
        # Run all tests
        run_test("Database Setup", test_db_setup)
        run_test("Initialize Core Items", init_catalog_items)
        run_test("Initialize Tag System", init_tag_system)
        run_test("Setup Relationships", test_relationships)
        run_test("Full Lifecycle Test", test_full_lifecycle)
        run_test("Anthropic API Test", test_anthropic_api)
        
        print(f"\nTests completed: {tests_passed}/{total_tests} passed")
        return tests_passed == total_tests

    def log_interaction(self, role, content):
        """Log chat interactions to database and JSONL file"""
        # Log to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            f"INSERT INTO {TABLE_CONFIG['CHAT_HISTORY_TABLE']} (session_id, role, content, metadata) VALUES (?, ?, ?, ?)",
            (
                str(datetime.datetime.now().date()),
                role,
                content,
                json.dumps({"mode": "interactive" if self.interactive else "cli"})
            )
        )
        
        conn.commit()
        conn.close()

        # Also log to file for backup
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "role": role,
            "content": content,
            "mode": "interactive" if self.interactive else "cli"
        }
        
        with open(self.chat_log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def show_help(self):
        """Display available commands"""
        return """
Available commands:
- help: Show this help message
- add [title] [description]: Add new item to catalog
- search [query]: Search catalog
- tag [item_id] [tag]: Add tag to item
- list: List recent items
- exit: Exit the program
"""

    def process_command(self, command, args=None):
        """Process a single command with optional arguments"""
        if command == 'help':
            return self.show_help()
        elif command == 'exit':
            return None
        
        # Log command
        self.log_interaction("user", f"{command} {args if args else ''}")
        
        # Process the command and get response
        response = self.process_input(command, args)
        
        # Log response
        self.log_interaction("assistant", response)
        
        return response

    def process_input(self, command, args):
        """Process user input and generate response"""
        # TODO: Implement command processing
        return f"Processing command: {command} with args: {args}"

    def chat_loop(self):
        """Main chat loop for interacting with the catalog"""
        if self.interactive:
            print("\nWelcome to Marian Catalog!")
            print("Type 'help' for available commands or 'exit' to quit.")
            print("----------------------------------------")
        
        while True:
            try:
                if self.interactive:
                    print("\nMarian>", end=" ")
                    user_input = input().strip()
                    
                    if not user_input:
                        continue
                        
                    command = user_input.split()[0].lower()
                    args = ' '.join(user_input.split()[1:]) if len(user_input.split()) > 1 else None
                else:
                    # Non-interactive mode for testing
                    break

                response = self.process_command(command, args)
                if response is None:  # exit command
                    if self.interactive:
                        print("\nGoodbye! Thank you for using Marian Catalog.")
                    break
                    
                if self.interactive:
                    print("\nResponse:", response)
                    print("\nWhat would you like to do next?")
                    
            except KeyboardInterrupt:
                if self.interactive:
                    print("\n\nExiting on user interrupt...")
                break
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                self.log_interaction("error", error_msg)
                if self.interactive:
                    print(f"\nError: {str(e)}")
                    print("Type 'help' for available commands.")

def main():
    parser = argparse.ArgumentParser(description='Marian Catalog Chat Interface')
    parser.add_argument('--interactive', '-i', action='store_true', help='Start in interactive mode')
    args = parser.parse_args()
    
    chat = CatalogChat(interactive=args.interactive)
    
    if args.interactive:
        print("Starting interactive session...")
        chat.chat_loop()
    else:
        # Run integration tests by default
        success = chat.run_integration_tests()
        exit(0 if success else 1)

if __name__ == "__main__":
    main()
