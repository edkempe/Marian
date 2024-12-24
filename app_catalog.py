import sqlite3
import datetime
import json
import os
import argparse
import random
from anthropic import Anthropic
from librarian_constants import CATALOG_CONFIG, TABLE_CONFIG, CREATE_CATALOG_TABLE, CREATE_TAGS_TABLE, CREATE_CATALOG_TAGS_TABLE, CREATE_CHAT_HISTORY_TABLE, CREATE_RELATIONSHIPS_TABLE, ERRORS
from marian_lib.anthropic_helper import get_anthropic_client, test_anthropic_connection
from marian_lib.logger import setup_logger, log_performance, log_system_state, log_security_event

class CatalogChat:
    def __init__(self, interactive=False):
        self.interactive = interactive
        self.chat_log_file = CATALOG_CONFIG['CHAT_LOG_FILE']
        self.db_path = CATALOG_CONFIG['CATALOG_DB_FILE']
        self.client = get_anthropic_client()
        
        # Set up system logger
        self.logger = setup_logger('catalog')
        self.test_logger = setup_logger('catalog', is_test=True)
        self.logger.info("Initializing CatalogChat")
        
        start_time = datetime.datetime.now()
        self.setup_database()
        log_performance(self.logger, "Database setup", start_time)
        
        # Log initial system state
        log_system_state(
            self.logger,
            mode="interactive" if interactive else "cli",
            db_path=self.db_path,
            chat_log=self.chat_log_file
        )
        
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
            print("\nRunning full lifecycle test:")
            
            test_marker = "LIFECYCLE_TEST_" + datetime.datetime.now().isoformat()
            self.test_logger.info(f"Starting lifecycle test {test_marker}")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                # 1. Create test tag
                print("  Creating test tag...")
                test_tag_name = f"{test_marker}_tag"
                cursor.execute(
                    f"INSERT INTO {TABLE_CONFIG['TAGS_TABLE']} (name) VALUES (?)",
                    (test_tag_name,)
                )
                cursor.execute(f"SELECT id FROM {TABLE_CONFIG['TAGS_TABLE']} WHERE name = ?", (test_tag_name,))
                test_tag_id = cursor.fetchone()[0]
                self.test_logger.debug(f"Created tag {test_tag_name}")
                
                # 2. Add test content with both new and existing tags
                print("  Adding test content...")
                test_title = f"{test_marker}_item"
                cursor.execute(
                    f"INSERT INTO {TABLE_CONFIG['CATALOG_TABLE']} (title, description, content) VALUES (?, ?, ?)",
                    (test_title, "Test Description", "Test Content")
                )
                test_item_id = cursor.lastrowid
                self.test_logger.debug(f"Added item {test_title}")
                
                # Get random selection of existing tags
                cursor.execute(f"SELECT id, name FROM {TABLE_CONFIG['TAGS_TABLE']}")
                all_tags = cursor.fetchall()
                num_existing_tags = random.randint(1, len(all_tags) - 1)  # At least 1, less than total
                selected_tags = random.sample(all_tags, num_existing_tags)
                existing_tag_ids = [(tag_id, name) for tag_id, name in selected_tags]
                self.test_logger.debug(f"Selected {num_existing_tags} random existing tags")
                
                # Apply test tag and existing tags
                print("  Applying tags...")
                # Apply new test tag
                cursor.execute(
                    f"INSERT INTO {TABLE_CONFIG['CATALOG_TAGS_TABLE']} (catalog_id, tag_id) VALUES (?, ?)",
                    (test_item_id, test_tag_id)
                )
                
                # Apply existing tags
                for tag_id, tag_name in existing_tag_ids:
                    cursor.execute(
                        f"INSERT INTO {TABLE_CONFIG['CATALOG_TAGS_TABLE']} (catalog_id, tag_id) VALUES (?, ?)",
                        (test_item_id, tag_id)
                    )
                
                tag_names = [name for _, name in existing_tag_ids]
                self.test_logger.debug(f"Applied test tag {test_tag_name} and existing tags: {', '.join(tag_names)} to {test_title}")
                
                # Verify findable by each tag
                print("  Verifying tag queries...")
                for tag_id, tag_name in [(test_tag_id, test_tag_name)] + existing_tag_ids:
                    cursor.execute(f"""
                        SELECT DISTINCT c.title, c.description 
                        FROM {TABLE_CONFIG['CATALOG_TABLE']} c
                        JOIN {TABLE_CONFIG['CATALOG_TAGS_TABLE']} ct ON c.id = ct.catalog_id
                        JOIN {TABLE_CONFIG['TAGS_TABLE']} t ON ct.tag_id = t.id
                        WHERE t.name = ?
                    """, (tag_name,))
                    result = cursor.fetchall()
                    assert any(row[0] == test_title for row in result), f"Item not found by tag {tag_name}"
                self.test_logger.debug("Verified item findable by all {num_existing_tags + 1} tags")
                
                # Query by title and verify all tags present
                print("  Verifying content query...")
                cursor.execute(f"""
                    SELECT t.name 
                    FROM {TABLE_CONFIG['TAGS_TABLE']} t
                    JOIN {TABLE_CONFIG['CATALOG_TAGS_TABLE']} ct ON t.id = ct.tag_id
                    JOIN {TABLE_CONFIG['CATALOG_TABLE']} c ON ct.catalog_id = c.id
                    WHERE c.title = ?
                """, (test_title,))
                tags = cursor.fetchall()
                assert len(tags) == num_existing_tags + 1, "Wrong number of tags found"
                tag_names = set(tag[0] for tag in tags)
                assert test_tag_name in tag_names, "Test tag not found"
                for _, name in existing_tag_ids:
                    assert name in tag_names, f"Tag {name} not found"
                self.test_logger.debug(f"Verified item has all expected tags")
                
                # Update content and verify tags remain
                print("  Testing content update...")
                new_description = f"Updated Description {test_marker}"
                cursor.execute(
                    f"UPDATE {TABLE_CONFIG['CATALOG_TABLE']} SET description = ? WHERE id = ?",
                    (new_description, test_item_id)
                )
                cursor.execute(
                    f"SELECT description FROM {TABLE_CONFIG['CATALOG_TABLE']} WHERE id = ?",
                    (test_item_id,)
                )
                assert cursor.fetchone()[0] == new_description, "Update failed"
                self.test_logger.debug(f"Updated item {test_title}")
                
                # Remove test tag and verify
                print("  Testing tag removal...")
                cursor.execute(
                    f"DELETE FROM {TABLE_CONFIG['CATALOG_TAGS_TABLE']} WHERE catalog_id = ? AND tag_id = ?",
                    (test_item_id, test_tag_id)
                )
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {TABLE_CONFIG['CATALOG_TAGS_TABLE']} WHERE catalog_id = ?
                """, (test_item_id,))
                assert cursor.fetchone()[0] == num_existing_tags, "Wrong number of tags after removal"
                
                # Verify correct tags remain
                cursor.execute(f"""
                    SELECT t.name 
                    FROM {TABLE_CONFIG['TAGS_TABLE']} t
                    JOIN {TABLE_CONFIG['CATALOG_TAGS_TABLE']} ct ON t.id = ct.tag_id
                    JOIN {TABLE_CONFIG['CATALOG_TABLE']} c ON ct.catalog_id = c.id
                    WHERE c.title = ? AND t.deleted = 0
                """, (test_title,))
                remaining_tags = set(tag[0] for tag in cursor.fetchall())
                assert test_tag_name not in remaining_tags, "Test tag still present after removal"
                for _, name in existing_tag_ids:
                    assert name in remaining_tags, f"Existing tag {name} was incorrectly removed"
                self.test_logger.debug(f"Removed test tag {test_tag_name}, verified existing tags remain intact")
                
                # Test tag renaming
                print("  Testing tag renaming...")
                updated_tag_name = f"{test_tag_name}_updated"
                cursor.execute(
                    f"UPDATE {TABLE_CONFIG['TAGS_TABLE']} SET name = ? WHERE id = ?",
                    (updated_tag_name, test_tag_id)
                )
                self.test_logger.debug(f"Renamed tag from {test_tag_name} to {updated_tag_name}")

                # Verify item findable by new tag name
                cursor.execute(f"""
                    SELECT DISTINCT c.title 
                    FROM {TABLE_CONFIG['CATALOG_TABLE']} c
                    JOIN {TABLE_CONFIG['CATALOG_TAGS_TABLE']} ct ON c.id = ct.catalog_id
                    JOIN {TABLE_CONFIG['TAGS_TABLE']} t ON ct.tag_id = t.id
                    WHERE t.name = ?
                """, (updated_tag_name,))
                result = cursor.fetchone()
                assert result and result[0] == test_title, "Item not found by updated tag name"
                self.test_logger.debug("Verified item findable by updated tag name")

                # Soft delete test tag
                print("  Testing tag soft deletion...")
                archive_timestamp = int(datetime.datetime.utcnow().timestamp())
                cursor.execute(
                    f"UPDATE {TABLE_CONFIG['TAGS_TABLE']} SET deleted = 1, archived_date = ? WHERE id = ?",
                    (archive_timestamp, test_tag_id)
                )
                self.test_logger.debug(f"Soft deleted tag {updated_tag_name}")

                # Verify tag exists in archive
                cursor.execute(f"""
                    SELECT deleted, archived_date 
                    FROM {TABLE_CONFIG['TAGS_TABLE']} 
                    WHERE id = ?
                """, (test_tag_id,))
                result = cursor.fetchone()
                assert result[0] == 1, "Tag not marked as deleted"
                assert result[1] == archive_timestamp, "Archive timestamp not set correctly"
                self.test_logger.debug("Verified tag exists in archive")

                # Verify tag not visible in active tags list
                cursor.execute(f"""
                    SELECT name FROM {TABLE_CONFIG['TAGS_TABLE']} 
                    WHERE deleted = 0
                """)
                active_tags = set(tag[0] for tag in cursor.fetchall())
                assert updated_tag_name not in active_tags, "Deleted tag still visible in active tags"

                # Verify tag exists in archive
                cursor.execute(f"""
                    SELECT deleted, archived_date 
                    FROM {TABLE_CONFIG['TAGS_TABLE']} 
                    WHERE id = ?
                """, (test_tag_id,))
                result = cursor.fetchone()
                assert result[0] == 1, "Tag not marked as deleted"
                assert result[1] == archive_timestamp, "Archive timestamp not set correctly"
                self.test_logger.debug("Verified tag exists in archive")

                # Verify tag not visible when viewing item tags
                cursor.execute(f"""
                    SELECT t.name 
                    FROM {TABLE_CONFIG['TAGS_TABLE']} t
                    JOIN {TABLE_CONFIG['CATALOG_TAGS_TABLE']} ct ON t.id = ct.tag_id
                    JOIN {TABLE_CONFIG['CATALOG_TABLE']} c ON ct.catalog_id = c.id
                    WHERE c.title = ? AND t.deleted = 0
                """, (test_title,))
                visible_tags = set(tag[0] for tag in cursor.fetchall())
                assert updated_tag_name not in visible_tags, "Deleted tag still visible on item"
                assert len(visible_tags) == num_existing_tags, "Wrong number of visible tags"
                self.test_logger.debug("Verified deleted tag not visible in listings")

                # Restore test tag
                print("  Testing tag restoration...")
                cursor.execute(
                    f"UPDATE {TABLE_CONFIG['TAGS_TABLE']} SET deleted = 0, archived_date = NULL WHERE id = ?",
                    (test_tag_id,)
                )
                self.test_logger.debug(f"Restored tag {updated_tag_name}")

                # Test item soft deletion
                print("  Testing item soft deletion...")
                archive_timestamp = int(datetime.datetime.utcnow().timestamp())
                cursor.execute(
                    f"UPDATE {TABLE_CONFIG['CATALOG_TABLE']} SET deleted = 1, archived_date = ? WHERE id = ?",
                    (archive_timestamp, test_item_id)
                )
                self.test_logger.debug(f"Soft deleted item {test_title}")

                # Verify item not visible in active items list
                cursor.execute(f"""
                    SELECT title FROM {TABLE_CONFIG['CATALOG_TABLE']} 
                    WHERE deleted = 0
                """)
                active_items = set(item[0] for item in cursor.fetchall())
                assert test_title not in active_items, "Deleted item still visible in active items"

                # Verify item exists in archive
                cursor.execute(f"""
                    SELECT deleted, archived_date 
                    FROM {TABLE_CONFIG['CATALOG_TABLE']} 
                    WHERE id = ?
                """, (test_item_id,))
                result = cursor.fetchone()
                assert result[0] == 1, "Item not marked as deleted"
                assert result[1] == archive_timestamp, "Archive timestamp not set correctly"
                self.test_logger.debug("Verified item exists in archive")

                # Verify item not visible when viewing tags
                cursor.execute(f"""
                    SELECT c.title 
                    FROM {TABLE_CONFIG['CATALOG_TABLE']} c
                    JOIN {TABLE_CONFIG['CATALOG_TAGS_TABLE']} ct ON c.id = ct.catalog_id
                    JOIN {TABLE_CONFIG['TAGS_TABLE']} t ON ct.tag_id = t.id
                    WHERE t.name = ? AND c.deleted = 0
                """, (updated_tag_name,))
                visible_items = set(item[0] for item in cursor.fetchall())
                assert test_title not in visible_items, "Deleted item still visible on tag"
                self.test_logger.debug("Verified deleted item not visible in listings")

            except Exception as e:
                self.test_logger.error(f"Lifecycle test failed: {str(e)}")
                raise

            finally:
                # Clean up test data
                cursor.execute(f"DELETE FROM {TABLE_CONFIG['CATALOG_TABLE']} WHERE title LIKE ?", (f"{test_marker}%",))
                cursor.execute(f"DELETE FROM {TABLE_CONFIG['TAGS_TABLE']} WHERE name LIKE ?", (f"{test_marker}%",))
                cursor.execute(f"DELETE FROM {TABLE_CONFIG['CATALOG_TAGS_TABLE']} WHERE catalog_id IN (SELECT id FROM {TABLE_CONFIG['CATALOG_TABLE']} WHERE title LIKE ?)", (f"{test_marker}%",))
                conn.commit()
                conn.close()
                
        run_test("Database setup", test_db_setup)
        run_test("Initialize catalog items", init_catalog_items)
        run_test("Initialize tag system", init_tag_system)
        run_test("Test relationships", test_relationships)
        run_test("Test full lifecycle", test_full_lifecycle)
        
        print(f"\nIntegration tests complete: {tests_passed}/{total_tests} passed")

    def process_input(self, command, args):
        """Process user input and generate response"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if command == 'add':
                if not args:
                    return "Please provide title and content for the catalog item"
                # Split args into title and content
                parts = args.split(' - ', 1)
                if len(parts) != 2:
                    return "Format: add <title> - <content>"
                title, content = parts
                
                # Check for existing active item
                cursor.execute(
                    f"SELECT title FROM {TABLE_CONFIG['CATALOG_TABLE']} WHERE title = ? COLLATE NOCASE AND deleted = 0",
                    (title,)
                )
                if cursor.fetchone():
                    return f"Error: An item with title '{title}' already exists"
                
                # Check for archived item
                cursor.execute(
                    f"SELECT id, title, content FROM {TABLE_CONFIG['CATALOG_TABLE']} WHERE title = ? COLLATE NOCASE AND deleted = 1",
                    (title,)
                )
                archived = cursor.fetchone()
                if archived:
                    if self.interactive:
                        print(f"\nFound archived item with title '{archived[1]}'. Would you like to restore it? (y/n): ", end="")
                        if input().strip().lower() == 'y':
                            cursor.execute(
                                f"UPDATE {TABLE_CONFIG['CATALOG_TABLE']} SET deleted = 0, archived_date = NULL, content = ?, modified_date = ? WHERE id = ?",
                                (content, int(datetime.datetime.utcnow().timestamp()), archived[0])
                            )
                            conn.commit()
                            return f"Restored and updated catalog item: {title}"
                    else:
                        return f"Found archived item '{title}'. Use 'restore <title>' to restore it"
                    
                try:
                    cursor.execute(
                        f"INSERT INTO {TABLE_CONFIG['CATALOG_TABLE']} (title, content) VALUES (?, ?)",
                        (title, content)
                    )
                    conn.commit()
                    return f"Added catalog item: {title}"
                except sqlite3.IntegrityError:
                    return f"Error: An item with title '{title}' already exists"
                    
            elif command == 'tag':
                if not args:
                    return "Format: tag <item_title> <tag_name>"
                parts = args.split()
                if len(parts) < 2:
                    return "Please provide both item title and tag name"
                title = parts[0]
                tag_name = parts[1]
                
                # Check for existing active tag
                cursor.execute(
                    f"SELECT id, name FROM {TABLE_CONFIG['TAGS_TABLE']} WHERE name = ? COLLATE NOCASE AND deleted = 0",
                    (tag_name,)
                )
                result = cursor.fetchone()
                if result:
                    tag_id = result[0]
                    tag_name = result[1]  # Use existing case
                else:
                    # Check for archived tag
                    cursor.execute(
                        f"SELECT id, name FROM {TABLE_CONFIG['TAGS_TABLE']} WHERE name = ? COLLATE NOCASE AND deleted = 1",
                        (tag_name,)
                    )
                    archived = cursor.fetchone()
                    if archived:
                        if self.interactive:
                            print(f"\nFound archived tag '{archived[1]}'. Would you like to restore it? (y/n): ", end="")
                            if input().strip().lower() == 'y':
                                cursor.execute(
                                    f"UPDATE {TABLE_CONFIG['TAGS_TABLE']} SET deleted = 0, archived_date = NULL, modified_date = ? WHERE id = ?",
                                    (int(datetime.datetime.utcnow().timestamp()), archived[0])
                                )
                                conn.commit()
                                tag_id = archived[0]
                                tag_name = archived[1]
                            else:
                                try:
                                    cursor.execute(
                                        f"INSERT INTO {TABLE_CONFIG['TAGS_TABLE']} (name) VALUES (?)",
                                        (tag_name,)
                                    )
                                    tag_id = cursor.lastrowid
                                except sqlite3.IntegrityError:
                                    return f"Error: Tag '{tag_name}' already exists with different case"
                        else:
                            return f"Found archived tag '{tag_name}'. Use 'restore_tag <name>' to restore it"
                    else:
                        try:
                            cursor.execute(
                                f"INSERT INTO {TABLE_CONFIG['TAGS_TABLE']} (name) VALUES (?)",
                                (tag_name,)
                            )
                            tag_id = cursor.lastrowid
                        except sqlite3.IntegrityError:
                            return f"Error: Tag '{tag_name}' already exists with different case"
                
                # Get item id (including archived)
                cursor.execute(
                    f"SELECT id, title, deleted FROM {TABLE_CONFIG['CATALOG_TABLE']} WHERE title = ? COLLATE NOCASE",
                    (title,)
                )
                result = cursor.fetchone()
                if not result:
                    return f"Item '{title}' not found"
                
                item_id, item_title, is_deleted = result
                if is_deleted:
                    if self.interactive:
                        print(f"\nItem '{item_title}' is archived. Would you like to restore it? (y/n): ", end="")
                        if input().strip().lower() == 'y':
                            cursor.execute(
                                f"UPDATE {TABLE_CONFIG['CATALOG_TABLE']} SET deleted = 0, archived_date = NULL, modified_date = ? WHERE id = ?",
                                (int(datetime.datetime.utcnow().timestamp()), item_id)
                            )
                            conn.commit()
                        else:
                            return f"Cannot tag archived item '{item_title}'. Restore it first"
                    else:
                        return f"Item '{item_title}' is archived. Use 'restore <title>' to restore it"
                
                # Check if tag is already applied
                cursor.execute(
                    f"SELECT 1 FROM {TABLE_CONFIG['CATALOG_TAGS_TABLE']} WHERE catalog_id = ? AND tag_id = ?",
                    (item_id, tag_id)
                )
                if cursor.fetchone():
                    return f"Tag '{tag_name}' is already applied to '{item_title}'"
                
                # Apply tag
                cursor.execute(
                    f"INSERT INTO {TABLE_CONFIG['CATALOG_TAGS_TABLE']} (catalog_id, tag_id) VALUES (?, ?)",
                    (item_id, tag_id)
                )
                conn.commit()
                return f"Tagged '{item_title}' with '{tag_name}'"
            
            elif command == 'restore' or command == 'restore_tag':
                if not args:
                    return f"Format: {command} <name>"
                name = args
                
                table = TABLE_CONFIG['TAGS_TABLE'] if command == 'restore_tag' else TABLE_CONFIG['CATALOG_TABLE']
                name_field = 'name' if command == 'restore_tag' else 'title'
                
                cursor.execute(
                    f"SELECT id, {name_field} FROM {table} WHERE {name_field} = ? COLLATE NOCASE AND deleted = 1",
                    (name,)
                )
                result = cursor.fetchone()
                if not result:
                    return f"No archived {'tag' if command == 'restore_tag' else 'item'} found with name '{name}'"
                
                cursor.execute(
                    f"UPDATE {table} SET deleted = 0, archived_date = NULL, modified_date = ? WHERE id = ?",
                    (int(datetime.datetime.utcnow().timestamp()), result[0])
                )
                conn.commit()
                return f"Restored {'tag' if command == 'restore_tag' else 'item'}: {result[1]}"
                
        except Exception as e:
            return f"Error: {str(e)}"
            
        finally:
            conn.close()
