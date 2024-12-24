"""Main application module for the Marian Catalog system."""

import datetime
import json
import os
import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from anthropic import Anthropic

from librarian_constants import CATALOG_CONFIG, TABLE_CONFIG, ERRORS
from marian_lib.anthropic_helper import get_anthropic_client, test_anthropic_connection
from marian_lib.logger import setup_logger, log_performance, log_system_state, log_security_event
from models.catalog import Base, CatalogItem, Tag, CatalogTag, ItemRelationship

class CatalogChat:
    """Main class for handling catalog operations and chat interactions."""
    
    def __init__(self, interactive=False):
        self.interactive = interactive
        self.chat_log_file = CATALOG_CONFIG['CHAT_LOG_FILE']
        self.db_path = CATALOG_CONFIG['CATALOG_DB_FILE']
        self.client = get_anthropic_client()
        
        # Set up system logger
        self.logger = setup_logger('catalog')
        self.test_logger = setup_logger('catalog', is_test=True)
        self.logger.info("Initializing CatalogChat")
        
        # Initialize database
        start_time = datetime.datetime.now()
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        self.Session = sessionmaker(bind=self.engine)
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
        """Initialize the catalog database with SQLAlchemy models."""
        Base.metadata.create_all(self.engine)
        self.logger.info("Database tables created successfully")
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.Session()
    
    def cleanup_test_data(self, session: Session, test_marker: str = None):
        """Clean up test data from previous test runs."""
        try:
            # Clean up catalog tags first due to foreign key constraints
            if test_marker:
                # Delete catalog tags for items matching the test marker
                session.query(CatalogTag).filter(CatalogTag.catalog_id.in_(
                    session.query(CatalogItem.id).filter(CatalogItem.title.like(f"{test_marker}%"))
                )).delete(synchronize_session=False)
                
                # Delete items matching the test marker
                session.query(CatalogItem).filter(CatalogItem.title.like(f"{test_marker}%")).delete()
                session.query(Tag).filter(Tag.name.like(f"{test_marker}%")).delete()
            else:
                # Delete all test items and tags
                session.query(CatalogTag).filter(CatalogTag.catalog_id.in_(
                    session.query(CatalogItem.id).filter(
                        CatalogItem.title.like("Test%")
                    )
                )).delete(synchronize_session=False)
                
                session.query(CatalogItem).filter(CatalogItem.title.like("Test%")).delete()
                session.query(Tag).filter(Tag.name.like("Test%")).delete()
            
            session.commit()
        except Exception as e:
            session.rollback()
            self.test_logger.error(f"Error cleaning up test data: {str(e)}")
            raise

    def run_integration_tests(self):
        """Run integration tests for the catalog system"""
        print("\nRunning integration tests...")
        
        tests_passed = 0
        total_tests = 0
        
        def run_test(name, test_func):
            nonlocal tests_passed, total_tests
            total_tests += 1
            try:
                test_func()
                tests_passed += 1
                print(f"✓ {name}")
            except Exception as e:
                print(f"✗ {name}: {str(e)}")
                self.test_logger.error(f"Test failed: {name}", exc_info=True)
        
        def test_duplicate_handling():
            """Test handling of duplicate items and tags"""
            test_title = "Test Duplicate Item"
            test_content = "Test content"
            test_tag = "TestDuplicateTag"
            
            session = self.get_session()
            try:
                # Clean up any leftover test data
                self.cleanup_test_data(session)
                
                # Test duplicate item titles
                # Add initial item
                item = CatalogItem(title=test_title, content=test_content)
                session.add(item)
                session.commit()
                assert session.query(CatalogItem).filter(CatalogItem.title == test_title).first(), "Failed to add initial item"
                
                # Try adding duplicate item
                try:
                    item2 = CatalogItem(title=test_title, content="Different content")
                    session.add(item2)
                    session.commit()
                    assert False, "Should not allow duplicate titles"
                except ValueError as e:
                    assert "case-insensitive" in str(e), "Should prevent case-insensitive duplicates"
                    session.rollback()
                
                # Try adding case-variant duplicate
                try:
                    item3 = CatalogItem(title=test_title.upper(), content="Different content")
                    session.add(item3)
                    session.commit()
                    assert False, "Should not allow case-variant duplicates"
                except ValueError as e:
                    assert "case-insensitive" in str(e), "Should prevent case-insensitive duplicates"
                    session.rollback()
                
                # Test duplicate tags
                # Add initial tag
                tag = Tag(name=test_tag)
                session.add(tag)
                session.commit()
                assert session.query(Tag).filter(Tag.name == test_tag).first(), "Failed to add initial tag"
                
                # Try adding duplicate tag
                try:
                    tag2 = Tag(name=test_tag)
                    session.add(tag2)
                    session.commit()
                    assert False, "Should not allow duplicate tags"
                except ValueError as e:
                    assert "case-insensitive" in str(e), "Should prevent case-insensitive duplicates"
                    session.rollback()
                
                # Try adding case-variant duplicate tag
                try:
                    tag3 = Tag(name=test_tag.upper())
                    session.add(tag3)
                    session.commit()
                    assert False, "Should not allow case-variant tag duplicates"
                except ValueError as e:
                    assert "case-insensitive" in str(e), "Should prevent case-insensitive duplicates"
                    session.rollback()
                
                # Test duplicate handling with archived items
                # Archive the item
                item.deleted = True
                session.commit()
                assert item.deleted, "Failed to archive item"
                
                # Try adding item with same title
                try:
                    item4 = CatalogItem(title=test_title, content="New content")
                    session.add(item4)
                    session.commit()
                    assert False, "Should not allow duplicate titles even with archived items"
                except ValueError as e:
                    assert "case-insensitive" in str(e), "Should prevent case-insensitive duplicates"
                    session.rollback()
                
                # Clean up
                self.cleanup_test_data(session)
                
            finally:
                session.close()
        
        def test_archived_item_handling():
            """Test handling of archived items and tags"""
            test_marker = "ARCHIVED_TEST_" + datetime.datetime.now().isoformat()
            test_title = f"{test_marker}_item"
            test_content = "Test content"
            test_tag = f"{test_marker}_tag"
            new_item_title = f"{test_marker}_another_item"
            
            session = self.get_session()
            try:
                # Clean up any leftover test data
                self.cleanup_test_data(session)
                
                # Add and tag item
                item = CatalogItem(title=test_title, content=test_content)
                session.add(item)
                session.commit()
                
                tag = Tag(name=test_tag)
                session.add(tag)
                session.commit()
                
                catalog_tag = CatalogTag(catalog_id=item.id, tag_id=tag.id)
                session.add(catalog_tag)
                session.commit()
                
                # Archive item
                item.deleted = True
                session.commit()
                assert item.deleted, "Failed to archive item"
                
                # Try to tag archived item
                try:
                    new_tag = Tag(name=f"{test_marker}_new_tag")
                    session.add(new_tag)
                    session.commit()
                    
                    catalog_tag = CatalogTag(catalog_id=item.id, tag_id=new_tag.id)
                    session.add(catalog_tag)
                    session.commit()
                    assert False, "Should prevent tagging archived items"
                except Exception as e:
                    session.rollback()
                    assert "archived" in str(e).lower(), "Should prevent tagging archived items"
                
                # Archive tag
                tag.deleted = True
                session.commit()
                assert tag.deleted, "Failed to archive tag"
                
                # Try to use archived tag on new item
                new_item = CatalogItem(title=new_item_title, content="Some content")
                session.add(new_item)
                session.commit()
                
                try:
                    catalog_tag = CatalogTag(catalog_id=new_item.id, tag_id=tag.id)
                    session.add(catalog_tag)
                    session.commit()
                    assert False, "Should prevent using archived tags"
                except Exception as e:
                    session.rollback()
                    assert "archived" in str(e).lower(), "Should prevent using archived tags"
                
                # Clean up
                self.cleanup_test_data(session)
                
            finally:
                session.close()

        def test_full_lifecycle():
            """Test complete lifecycle of catalog items and tags"""
            test_marker = "LIFECYCLE_TEST_" + datetime.datetime.now().isoformat()
            self.test_logger.info(f"Starting lifecycle test {test_marker}")
            
            session = self.get_session()
            try:
                # Clean up any leftover test data
                self.cleanup_test_data(session, test_marker)
                
                # 1. Create test tags
                print("  Creating test tags...")
                test_tags = []
                for i in range(3):
                    tag_name = f"{test_marker}_tag_{i}"
                    tag = Tag(name=tag_name)
                    session.add(tag)
                    session.commit()
                    test_tags.append(tag)
                    self.test_logger.debug(f"Created tag {tag_name}")
                
                # 2. Add test content
                print("  Adding test content...")
                test_title = f"{test_marker}_item"
                item = CatalogItem(title=test_title, content="Test Content")
                session.add(item)
                session.commit()
                self.test_logger.debug(f"Added item {test_title}")
                
                # Apply tags
                print("  Applying tags...")
                for tag in test_tags:
                    catalog_tag = CatalogTag(catalog_id=item.id, tag_id=tag.id)
                    session.add(catalog_tag)
                    session.commit()
                
                tag_names = [tag.name for tag in test_tags]
                self.test_logger.debug(f"Applied tags: {', '.join(tag_names)} to {test_title}")
                
                # Verify findable by each tag
                print("  Verifying tag search...")
                for tag in test_tags:
                    result = session.query(CatalogItem).join(CatalogTag).join(Tag).filter(
                        Tag.name == tag.name,
                        CatalogItem.deleted == False
                    ).first()
                    assert result and result.title == test_title, f"Item not found by tag {tag.name}"
                self.test_logger.debug("Verified item findable by all tags")
                
                # Query by title and verify all tags present
                print("  Verifying content query...")
                tags = session.query(Tag).join(CatalogTag).join(CatalogItem).filter(CatalogItem.title == test_title).all()
                assert len(tags) == len(test_tags), "Wrong number of tags found"
                tag_names = set(tag.name for tag in tags)
                for tag in test_tags:
                    assert tag.name in tag_names, f"Tag {tag.name} not found"
                self.test_logger.debug(f"Verified item has all expected tags")
                
                # Update content and verify tags remain
                print("  Testing content update...")
                new_description = f"Updated Description {test_marker}"
                item.description = new_description
                session.commit()
                assert item.description == new_description, "Update failed"
                self.test_logger.debug(f"Updated item {test_title}")
                
                # Test tag renaming
                print("  Testing tag renaming...")
                test_tag = test_tags[0]
                updated_tag_name = f"{test_tag.name}_updated"
                test_tag.name = updated_tag_name
                session.commit()
                self.test_logger.debug(f"Renamed tag from {test_tag.name} to {updated_tag_name}")
                
                # Verify item findable by new tag name
                result = session.query(CatalogItem).join(CatalogTag).join(Tag).filter(Tag.name == updated_tag_name).first()
                assert result and result.title == test_title, "Item not found by updated tag name"
                self.test_logger.debug("Verified item findable by updated tag name")
                
                # Test tag soft deletion
                print("  Testing tag soft deletion...")
                test_tag.deleted = True
                session.commit()
                self.test_logger.debug(f"Soft deleted tag {updated_tag_name}")
                
                # Verify tag exists in archive
                result = session.query(Tag).filter(Tag.id == test_tag.id).first()
                assert result.deleted, "Tag not marked as deleted"
                self.test_logger.debug("Verified tag exists in archive")
                
                # Verify tag not visible in active tags list
                tags = session.query(Tag).filter(Tag.deleted == False).all()
                assert updated_tag_name not in [t.name for t in tags], "Deleted tag still visible in active tags"
                
                # Test tag restoration
                print("  Testing tag restoration...")
                test_tag.deleted = False
                session.commit()
                self.test_logger.debug(f"Restored tag {updated_tag_name}")
                
                # Test item soft deletion
                print("  Testing item soft deletion...")
                item.deleted = True
                session.commit()
                self.test_logger.debug(f"Soft deleted item {test_title}")
                
                # Verify item not visible in active items list
                items = session.query(CatalogItem).filter(CatalogItem.deleted == False).all()
                assert test_title not in [i.title for i in items], "Deleted item still visible in active items"
                
                # Verify item exists in archive
                result = session.query(CatalogItem).filter(CatalogItem.id == item.id).first()
                assert result.deleted, "Item not marked as deleted"
                self.test_logger.debug("Verified item exists in archive")
                
                # Verify item not visible when viewing tags
                items = session.query(CatalogItem).join(CatalogTag).join(Tag).filter(
                    Tag.name == updated_tag_name,
                    CatalogItem.deleted == False
                ).all()
                assert test_title not in [i.title for i in items], "Deleted item still visible on tag"
                self.test_logger.debug("Verified deleted item not visible in listings")
                
                # Clean up test data
                self.cleanup_test_data(session, test_marker)
                
            except Exception as e:
                self.test_logger.error(f"Lifecycle test failed: {str(e)}", exc_info=True)
                raise
            finally:
                session.close()

        # Run all tests
        run_test("Test duplicate handling", test_duplicate_handling)
        run_test("Test archived item handling", test_archived_item_handling)
        print("\nRunning full lifecycle test:")
        run_test("Test full lifecycle", test_full_lifecycle)
        
        print(f"\nIntegration tests complete: {tests_passed}/{total_tests} passed")

    def get_semantic_matches(self, text: str, items: list, threshold: float = 0.7) -> list:
        """Find semantically similar items using Claude."""
        if not items:
            return []
            
        try:
            # Create prompt for semantic similarity check
            prompt = f"""Compare the following text: "{text}" with these items:
            {[str(item) for item in items]}
            
            Return only the items that are semantically similar (meaning they refer to the same concept or topic), 
            with a similarity score above {threshold}. Format each match as: "item|score".
            Only return the matches, nothing else."""
            
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response into matches
            matches = []
            for line in response.content[0].text.strip().split('\n'):
                if line:
                    item, score = line.split('|')
                    matches.append((item.strip().strip('"'), float(score)))
            return matches
            
        except Exception as e:
            self.logger.error(f"Error in semantic matching: {str(e)}")
            return []

    def check_semantic_duplicates(self, session: Session, title: str, existing_items: list) -> tuple:
        """Check for semantic duplicates of a title."""
        matches = self.get_semantic_matches(title, [item.title for item in existing_items])
        if matches:
            similar_items = []
            for match_title, score in matches:
                item = next((i for i in existing_items if i.title == match_title), None)
                if item:
                    similar_items.append((item, score))
            return True, similar_items
        return False, []

    def process_input(self, command: str, args: str) -> str:
        """Process user input and generate response"""
        session = self.get_session()
        
        try:
            if command == 'search':
                if not args:
                    return "Please provide search terms"
                query = args.strip()
                items = session.query(CatalogItem).filter(
                    CatalogItem.deleted == False,
                    (CatalogItem.title.ilike(f"%{query}%") |
                     CatalogItem.content.ilike(f"%{query}%"))
                ).all()
                if not items:
                    return "No matching items found"
                return "\n".join(f"{item.title}: {item.content[:100]}..." for item in items)
            
            elif command == 'search_by_tag':
                if not args:
                    return "Please provide tag name"
                tag_name = args.strip()
                items = session.query(CatalogItem).join(CatalogTag).join(Tag).filter(
                    CatalogItem.deleted == False,
                    Tag.deleted == False,
                    Tag.name.ilike(f"%{tag_name}%")
                ).all()
                if not items:
                    return "No items found with that tag"
                return "\n".join(f"{item.title}: {item.content[:100]}..." for item in items)
            
            elif command == 'list_recent':
                try:
                    days = int(args) if args else 7
                except ValueError:
                    days = 7
                cutoff = int((datetime.datetime.utcnow() - datetime.timedelta(days=days)).timestamp())
                items = session.query(CatalogItem).filter(
                    CatalogItem.deleted == False,
                    CatalogItem.modified_date >= cutoff
                ).order_by(CatalogItem.modified_date.desc()).all()
                if not items:
                    return f"No items modified in the last {days} days"
                return "\n".join(
                    f"{item.title} (modified: {datetime.datetime.fromtimestamp(item.modified_date).strftime('%Y-%m-%d %H:%M:%S')})"
                    for item in items
                )
            
            elif command == 'list_tags':
                include_archived = args.lower() == 'archived'
                tags = session.query(Tag)
                if not include_archived:
                    tags = tags.filter(Tag.deleted == False)
                tags = tags.order_by(Tag.name).all()
                if not tags:
                    return "No tags found"
                return "\n".join(
                    f"{tag.name} {'(archived)' if tag.deleted else ''}"
                    for tag in tags
                )
            
            elif command == 'list':
                include_archived = args.lower() == 'archived'
                items = session.query(CatalogItem)
                if not include_archived:
                    items = items.filter(CatalogItem.deleted == False)
                items = items.order_by(CatalogItem.modified_date.desc()).all()
                if not items:
                    return "No items found"
                return "\n".join(
                    f"{item.title} {'(archived)' if item.deleted else ''}: {item.content[:100]}..."
                    for item in items
                )
            
            elif command == 'add':
                if not args:
                    return "Please provide title and content for the catalog item"
                parts = args.split(' - ', 1)
                if len(parts) != 2:
                    return "Format: add <title> - <content>"
                title, content = parts
                
                # Get all existing items for semantic check
                all_items = session.query(CatalogItem).all()
                
                # Check for semantic duplicates
                has_duplicates, similar_items = self.check_semantic_duplicates(session, title, all_items)
                if has_duplicates:
                    if self.interactive:
                        print("\nFound semantically similar items:")
                        for item, score in similar_items:
                            status = "(archived)" if item.deleted else "(active)"
                            print(f"- {item.title} {status} (similarity: {score:.2f})")
                        print("\nWould you like to:")
                        print("1. Create new item anyway")
                        print("2. Cancel")
                        if item.deleted:
                            print("3. Restore similar item")
                        choice = input("Enter choice (1-3): ").strip()
                        
                        if choice == "2":
                            return "Operation cancelled"
                        elif choice == "3" and item.deleted:
                            item.deleted = False
                            session.commit()
                            return f"Restored similar item: {item.title}"
                    else:
                        similar_list = "\n".join(f"- {item.title} ({'archived' if item.deleted else 'active'})" 
                                               for item, _ in similar_items)
                        return f"Found semantically similar items:\n{similar_list}\nUse --force to add anyway"
                
                # Check for exact title match
                existing_item = session.query(CatalogItem).filter(
                    CatalogItem.title.ilike(title),
                    CatalogItem.deleted == False
                ).first()
                if existing_item:
                    return f"Error: An item with title '{title}' already exists"
                
                # Check for archived item
                archived_item = session.query(CatalogItem).filter(
                    CatalogItem.title.ilike(title),
                    CatalogItem.deleted == True
                ).first()
                if archived_item:
                    if self.interactive:
                        print(f"\nFound archived item with title '{archived_item.title}'. Would you like to restore it? (y/n): ", end="")
                        if input().strip().lower() == 'y':
                            archived_item.deleted = False
                            session.commit()
                            return f"Restored and updated catalog item: {title}"
                    else:
                        return f"Found archived item '{title}'. Use 'restore <title>' to restore it"
                
                try:
                    item = CatalogItem(title=title, content=content)
                    session.add(item)
                    session.commit()
                    return f"Added catalog item: {title}"
                except Exception as e:
                    session.rollback()
                    return f"Error: {str(e)}"
            
            elif command == 'tag':
                if not args:
                    return "Format: tag <item_title> <tag_name>"
                parts = args.split()
                if len(parts) < 2:
                    return "Please provide both item title and tag name"
                title = parts[0]
                tag_name = parts[1]
                
                # Get item (including archived)
                item = session.query(CatalogItem).filter(
                    CatalogItem.title.ilike(title)
                ).first()
                if not item:
                    return f"Item '{title}' not found"
                if item.deleted:
                    return f"Item '{title}' is archived. Restore it first."
                
                # Get all existing tags for semantic check
                all_tags = session.query(Tag).all()
                
                # Check for semantic duplicates
                has_duplicates, similar_tags = self.check_semantic_duplicates(session, tag_name, all_tags)
                if has_duplicates:
                    if self.interactive:
                        print("\nFound semantically similar tags:")
                        for tag, score in similar_tags:
                            status = "(archived)" if tag.deleted else "(active)"
                            print(f"- {tag.name} {status} (similarity: {score:.2f})")
                        print("\nWould you like to:")
                        print("1. Create new tag anyway")
                        print("2. Use existing tag")
                        print("3. Cancel")
                        choice = input("Enter choice (1-3): ").strip()
                        
                        if choice == "2" and similar_tags:
                            tag = similar_tags[0][0]  # Use the most similar tag
                            if tag.deleted:
                                tag.deleted = False
                                session.commit()
                            tag_name = tag.name
                        elif choice == "3":
                            return "Operation cancelled"
                    else:
                        similar_list = "\n".join(f"- {tag.name} ({'archived' if tag.deleted else 'active'})" 
                                               for tag, _ in similar_tags)
                        return f"Found semantically similar tags:\n{similar_list}\nUse --force to add anyway"
                
                # Check for existing active tag
                existing_tag = session.query(Tag).filter(
                    Tag.name.ilike(tag_name),
                    Tag.deleted == False
                ).first()
                if existing_tag:
                    return f"Error: Tag '{tag_name}' already exists"
                
                # Check for archived tag
                archived_tag = session.query(Tag).filter(
                    Tag.name.ilike(tag_name),
                    Tag.deleted == True
                ).first()
                if archived_tag:
                    if self.interactive:
                        print(f"\nFound archived tag '{archived_tag.name}'. Would you like to restore it? (y/n): ", end="")
                        if input().strip().lower() == 'y':
                            archived_tag.deleted = False
                            session.commit()
                            return f"Restored tag: {archived_tag.name}"
                    return f"Found archived tag '{tag_name}'. Use 'restore_tag <name>' to restore it"
                
                # Create new tag
                try:
                    tag = Tag(name=tag_name)
                    session.add(tag)
                    session.commit()
                    tag_name = tag.name
                except Exception as e:
                    session.rollback()
                    return f"Error creating tag: {str(e)}"
                
                # Check if tag is already applied
                existing_catalog_tag = session.query(CatalogTag).filter(
                    CatalogTag.catalog_id == item.id,
                    CatalogTag.tag_id == tag.id
                ).first()
                if existing_catalog_tag:
                    return f"Tag '{tag_name}' is already applied to '{item.title}'"
                
                # Apply tag
                catalog_tag = CatalogTag(catalog_id=item.id, tag_id=tag.id)
                session.add(catalog_tag)
                session.commit()
                return f"Tagged '{item.title}' with '{tag_name}'"
            
            elif command == 'create_tag':
                if not args:
                    return "Please provide a tag name"
                tag_name = args.strip()
                
                # Get all existing tags for semantic check
                all_tags = session.query(Tag).all()
                
                # Check for semantic duplicates
                has_duplicates, similar_tags = self.check_semantic_duplicates(session, tag_name, all_tags)
                if has_duplicates:
                    if self.interactive:
                        print("\nFound semantically similar tags:")
                        for tag, score in similar_tags:
                            status = "(archived)" if tag.deleted else "(active)"
                            print(f"- {tag.name} {status} (similarity: {score:.2f})")
                        print("\nWould you like to:")
                        print("1. Create new tag anyway")
                        print("2. Use existing tag")
                        print("3. Cancel")
                        choice = input("Enter choice (1-3): ").strip()
                        
                        if choice == "2" and similar_tags:
                            tag = similar_tags[0][0]  # Use the most similar tag
                            if tag.deleted:
                                tag.deleted = False
                                session.commit()
                            return f"Restored tag: {tag.name}"
                        elif choice == "3":
                            return "Operation cancelled"
                    else:
                        similar_list = "\n".join(f"- {tag.name} ({'archived' if tag.deleted else 'active'})" 
                                               for tag, _ in similar_tags)
                        return f"Found semantically similar tags:\n{similar_list}\nUse --force to add anyway"
                
                # Check for existing active tag
                existing_tag = session.query(Tag).filter(
                    Tag.name.ilike(tag_name),
                    Tag.deleted == False
                ).first()
                if existing_tag:
                    return f"Error: Tag '{tag_name}' already exists"
                
                # Check for archived tag
                archived_tag = session.query(Tag).filter(
                    Tag.name.ilike(tag_name),
                    Tag.deleted == True
                ).first()
                if archived_tag:
                    if self.interactive:
                        print(f"\nFound archived tag '{archived_tag.name}'. Would you like to restore it? (y/n): ", end="")
                        if input().strip().lower() == 'y':
                            archived_tag.deleted = False
                            session.commit()
                            return f"Restored tag: {archived_tag.name}"
                    return f"Found archived tag '{tag_name}'. Use 'restore_tag <name>' to restore it"
                
                # Create new tag
                try:
                    tag = Tag(name=tag_name)
                    session.add(tag)
                    session.commit()
                    return f"Created new tag: {tag_name}"
                except Exception as e:
                    session.rollback()
                    return f"Error creating tag: {str(e)}"

            elif command == 'restore' or command == 'restore_tag':
                if not args:
                    return f"Format: {command} <name>"
                name = args.strip()
                
                table = Tag if command == 'restore_tag' else CatalogItem
                name_field = 'name' if command == 'restore_tag' else 'title'
                
                archived_item = session.query(table).filter(
                    getattr(table, name_field).ilike(name),
                    table.deleted == True
                ).first()
                if not archived_item:
                    return f"No archived {'tag' if command == 'restore_tag' else 'item'} found with name '{name}'"
                
                archived_item.deleted = False
                session.commit()
                return f"Restored {'tag' if command == 'restore_tag' else 'item'}: {name}"

            elif command == 'archive' or command == 'archive_tag':
                if not args:
                    return f"Format: {command} <name>"
                name = args.strip()
                
                table = Tag if command == 'archive_tag' else CatalogItem
                name_field = 'name' if command == 'archive_tag' else 'title'
                
                item = session.query(table).filter(
                    getattr(table, name_field).ilike(name),
                    table.deleted == False
                ).first()
                if not item:
                    return f"No active {'tag' if command == 'archive_tag' else 'item'} found with name '{name}'"
                
                item.deleted = True
                session.commit()
                return f"Archived {'tag' if command == 'archive_tag' else 'item'}: {name}"

            elif command == 'archive':
                if not args:
                    return "Please provide the title of the item to archive"
                title = args.strip()
                
                item = session.query(CatalogItem).filter(
                    CatalogItem.title.ilike(title),
                    CatalogItem.deleted == False
                ).first()
                
                if not item:
                    return f"No active item found with title '{title}'"
                
                item.deleted = True
                session.commit()
                return f"Archived item: {title}"

            else:
                return f"Unknown command: {command}"
            
        except Exception as e:
            session.rollback()
            return f"Error: {str(e)}"
            
        finally:
            session.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Marian Catalog System")
    parser.add_argument("--test", action="store_true", help="Run integration tests")
    args = parser.parse_args()
    
    chat = CatalogChat()
    
    if args.test:
        chat.run_integration_tests()
    else:
        print("\nInitializing catalog system and running tests...")
        chat.run_integration_tests()
