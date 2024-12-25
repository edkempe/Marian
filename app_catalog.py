"""Main application module for the Marian Catalog system."""

import datetime
import json
import os
import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.catalog import CatalogItem, Tag, CatalogTag
from utils.logger import setup_logger
from utils.anthropic import get_anthropic_client
from catalog_constants import CATALOG_CONFIG

class CatalogChat:
    """Interface for managing catalog items and tags with semantic search."""
    
    def __init__(self, db_path=CATALOG_CONFIG['database']['file'], mode='cli', 
                 chat_log=CATALOG_CONFIG['logging']['chat_log']):
        """Initialize the catalog chat interface"""
        self.mode = mode
        self.db_path = db_path
        self.chat_log = chat_log
        self.test_logger = setup_logger('test_catalog')
        self.interactive = mode == 'interactive'
        self.client = get_anthropic_client()
        
        # Initialize database
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(self.engine)
        self.test_logger.info("Database tables created successfully")
        self.test_logger.info(f"System State: mode={mode}, db_path={db_path}, chat_log={chat_log}")

    def get_session(self):
        """Get a new database session"""
        return self.Session()

    def check_semantic_duplicates(self, session: sessionmaker, title: str, existing_items: list) -> tuple:
        """Check for semantic duplicates of a title."""
        try:
            # For items, use title attribute
            items = [item.title for item in existing_items]
            if not items:
                return False, []
                
            matches = self.get_semantic_matches(title, items, threshold=CATALOG_CONFIG['semantic']['threshold'])
            if not matches:
                return False, []
                
            return True, matches
            
        except Exception as e:
            error_msg = CATALOG_CONFIG['error_messages']['semantic_error'].format(error=str(e))
            self.test_logger.error(error_msg)
            return False, []

    def get_semantic_matches(self, text: str, items: list, threshold: float = CATALOG_CONFIG['semantic']['threshold']) -> list:
        """Find semantically similar items using Claude."""
        if not items:
            return []
            
        try:
            # Format items list
            items_str = "\n".join(f"- {item}" for item in items)
            
            # Send request to Claude
            response = self.client.messages.create(
                model=CATALOG_CONFIG['semantic']['model'] if self.mode != 'test' else CATALOG_CONFIG['test']['model'],
                max_tokens=CATALOG_CONFIG['semantic']['max_tokens'],
                temperature=CATALOG_CONFIG['semantic']['temperature'],
                messages=[{
                    "role": "user",
                    "content": CATALOG_CONFIG['semantic']['prompt'].format(
                        text=text,
                        items=items_str,
                        threshold=threshold
                    )
                }]
            )
            
            # Parse response
            matches_str = response.content[0].text.strip()
            try:
                matches = eval(matches_str)  # Safe since we control the input and format
                if not isinstance(matches, list):
                    return []
                return matches
            except:
                # If parsing fails, try to extract tuples from the text
                import re
                pattern = r'\("([^"]+)",\s*(0\.\d+)\)'
                matches = re.findall(pattern, matches_str)
                return [(m[0], float(m[1])) for m in matches]
            
        except Exception as e:
            error_msg = CATALOG_CONFIG['error_messages']['semantic_error'].format(error=str(e))
            self.test_logger.error(error_msg)
            return []

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
                    CatalogItem.title.ilike(title)
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
    args = parser.parse_args()
    
    chat = CatalogChat()
