"""Main application module for the Marian Catalog system."""

import datetime
import json
import os
import argparse
from shared_lib.logging_util import setup_logging
from shared_lib.anthropic_client_lib import get_anthropic_client
from shared_lib.chat_log_util import ChatLogger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.catalog import CatalogItem, Tag, CatalogTag
from constants import CATALOG_CONFIG, API_CONFIG
from typing import List
import sys
import logging
from shared_lib.anthropic_lib import parse_claude_response
import re

class CatalogChat:
    """Interface for managing catalog items and tags with semantic search."""
    
    def __init__(self, db_path=CATALOG_CONFIG['DB_PATH'], mode='cli', 
                 chat_log=CATALOG_CONFIG['CHAT_LOG'], enable_semantic=None):
        """Initialize the catalog chat interface"""
        self.mode = mode
        self.db_path = db_path
        self.chat_log = chat_log
        self.test_logger = setup_logging('test_catalog')
        self.interactive = mode == 'interactive'
        self.client = get_anthropic_client()
        
        # Set semantic checking based on parameter or config
        self.enable_semantic = enable_semantic if enable_semantic is not None else CATALOG_CONFIG['ENABLE_SEMANTIC']
        
        # Initialize chat logger
        try:
            self.chat_logger = ChatLogger(os.path.join('data', chat_log))
        except Exception as e:
            self.test_logger.error(f"Failed to initialize chat logger: {str(e)}")
            raise RuntimeError("Chat logging is required but unavailable")
        
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

    def check_semantic_duplicates(self, session, title: str, existing_items: list) -> tuple:
        """Check if there are semantic duplicates of a title in the catalog.
        
        Args:
            session: Database session
            title: Title to check for duplicates
            existing_items: List of items to check against
            
        Returns:
            Tuple of:
            - has_duplicates: True if any strong matches found
            - duplicates: List of items above MATCH_THRESHOLD
            - potential_matches: List of items between POTENTIAL_MATCH_THRESHOLD and MATCH_THRESHOLD
        """
        try:
            # Get semantic matches using the lower threshold
            matches = self.get_semantic_matches(title, existing_items, threshold=CATALOG_CONFIG['POTENTIAL_MATCH_THRESHOLD'])
            
            # Split matches into duplicates and potential matches
            duplicates = []
            potential_matches = []
            
            for item, score, reason in matches:
                if score >= CATALOG_CONFIG['MATCH_THRESHOLD']:
                    duplicates.append((item, score, reason))
                else:
                    potential_matches.append((item, score, reason))
            
            return bool(duplicates), duplicates, potential_matches
            
        except Exception as e:
            self.test_logger.error(f"Error in semantic duplicate detection: {str(e)}")
            return False, [], []

    def get_semantic_matches(self, text: str, items: list, threshold: float = None) -> list:
        """Get semantically similar items using Claude AI.
        
        Args:
            text: Text to compare against
            items: List of items to check (can be strings, CatalogItems, or Tags)
            threshold: Optional similarity threshold (0-1)
            
        Returns:
            List of tuples (item, score, reasoning)
        """
        if not self.enable_semantic:
            return []
            
        try:
            # Handle empty queries
            text = text.strip()
            if not text:
                return []

            # Adjust threshold based on text length
            if threshold is None:
                if len(text.split()) <= 3:  # Short text like tags
                    threshold = CATALOG_CONFIG['TAG_MATCH_THRESHOLD']
                else:
                    threshold = CATALOG_CONFIG['POTENTIAL_MATCH_THRESHOLD']

            # Convert items to title strings if needed
            item_texts = []
            for item in items:
                if isinstance(item, str):
                    item_texts.append(item)
                else:
                    item_texts.append(item.title)

            # Construct prompt with length-aware instructions
            is_short = len(text.split()) <= 3
            prompt = f"""You are a semantic search expert that prioritizes advanced, comprehensive content over basic tutorials. When comparing items, you always ensure that more advanced guides receive higher scores than beginner-level content covering the same topic.

Compare this query semantically against the items and return matches.

Query: "{text}"

Items:
{json.dumps(item_texts, indent=2)}

Instructions:
1. {"For short queries, prioritize abbreviations and key terms." if is_short else "Focus on conceptual similarity and meaning. Consider synonyms, related concepts, and different ways of expressing the same idea."}
2. For programming topics:
   - Match related programming concepts (e.g. 'class' relates to 'OOP', 'object-oriented')
   - Consider common variations in terminology
   - Match both specific and general terms appropriately
   - When matching tutorials/guides:
     * Score advanced/specific content (e.g. OOP, design patterns) higher than beginner/general content
     * For queries about specific concepts, prefer comprehensive guides over basic tutorials
     * For class-related queries, prioritize OOP guides over basic class tutorials
3. For workflow and best practices:
   - Match both positive patterns (what to do) and negative patterns (what to avoid)
   - Consider common problem scenarios and their solutions
   - Match workflow-related terms across different contexts
4. Return matches in this format:
{{
    "matches": [
        {{
            "index": <index in items list>,
            "score": <0.0-1.0>,
            "reasoning": "<explanation of semantic match>"
        }}
    ]
}}

Scoring guidelines:
- Score 0.95-1.0: Advanced/comprehensive guides
  * OOP guides for class-related queries
  * Design pattern documentation
  * In-depth technical references
- Score 0.8-0.95: Strong matches for basic content
  * Beginner tutorials
  * General guides
  * Basic concept explanations
- Score 0.6-0.8: Moderate relationship
  * Partial topic coverage
  * Related but not directly matching content
- Below 0.6: Weak or tangential relationship

Example: For a query about "python class tutorial":
- "Python OOP Guide" should score 0.95-1.0 as it provides comprehensive coverage
- "Python Beginner's Class" should score 0.8-0.95 as it's more basic"""

            # Get response from Claude
            try:
                response = self.client.messages.create(
                    model=API_CONFIG['MODEL'] if self.mode != 'test' else API_CONFIG['TEST_MODEL'],
                    max_tokens=API_CONFIG['MAX_TOKENS'],
                    temperature=0.2,
                    system=prompt,
                    messages=[{"role": "user", "content": "Find semantic matches"}]
                )
                
                # Parse response
                content = response.content[0].text
                self.test_logger.debug(f"Raw API response: {content}")
                
                # Extract JSON object from response
                json_match = re.search(r'\{[\s\S]*\}', content)
                if not json_match:
                    self.test_logger.error("No JSON found in response")
                    return []
                    
                json_str = json_match.group()
                self.test_logger.debug(f"Extracted JSON: {json_str}")
                
                result = json.loads(json_str)
                matches = []
                
                if "matches" in result and isinstance(result["matches"], list):
                    for match in result["matches"]:
                        idx = match.get("index", -1)
                        score = match.get("score", 0)
                        reasoning = match.get("reasoning", "")
                        
                        if 0 <= idx < len(items) and score >= threshold:
                            matches.append((items[idx], score, reasoning))
                            self.test_logger.debug(f"Added match: item[{idx}] (score: {score})")
                
                return sorted(matches, key=lambda x: x[1], reverse=True)
                
            except json.JSONDecodeError as e:
                self.test_logger.error(f"JSON decode error: {str(e)}")
                self.test_logger.error(f"Failed JSON: {json_str}")
                return []
            except Exception as e:
                self.test_logger.error(f"Semantic matching error: {str(e)}")
                return []
            
        except Exception as e:
            self.test_logger.error(f"Error in semantic matching: {str(e)}")
            return []

    def add_item(self, title: str, content: str = "", description: str = "", tags: List[str] = None, force: bool = False) -> CatalogItem:
        """Add a new item to the catalog.
        
        Args:
            title: Title of the item
            content: Content of the item
            description: Description of the item
            tags: List of tag names to apply
            force: If True, bypass semantic duplicate checks
            
        Returns:
            CatalogItem: The newly created catalog item
            
        Raises:
            ValueError: If item with similar title exists or validation fails
        """
        session = self.get_session()
        try:
            # Check for semantic duplicates
            existing_items = session.query(CatalogItem).filter(
                CatalogItem.deleted == False
            ).all()
            
            if not force:
                has_dups, duplicates, potential_matches = self.check_semantic_duplicates(session, title, existing_items)
                
                if has_dups:
                    raise ValueError(
                        CATALOG_CONFIG['ERROR_MESSAGES']['DUPLICATE_ERROR'].format(
                            title=duplicates[0][0].title
                        )
                    )
                
                if potential_matches:
                    # Format potential matches for display
                    match_info = "\n".join([
                        f"- {item.title} (similarity: {score:.2f}): {reason}"
                        for item, score, reason in potential_matches
                    ])
                    
                    raise ValueError(
                        CATALOG_CONFIG['ERROR_MESSAGES']['POTENTIAL_MATCH_WARNING'].format(
                            matches=match_info
                        )
                    )
            
            # Create new item
            item = CatalogItem(
                title=title,
                content=content,
                description=description,
                status='draft'
            )
            session.add(item)
            
            # Add tags if provided
            if tags:
                for tag_name in tags:
                    # Get or create tag
                    tag = session.query(Tag).filter(
                        Tag.name.ilike(tag_name),
                        Tag.deleted == False
                    ).first()
                    
                    if not tag:
                        tag = Tag(name=tag_name)
                        session.add(tag)
                    
                    # Create association
                    catalog_tag = CatalogTag(catalog_id=item.id, tag_id=tag.id)
                    session.add(catalog_tag)
            
            session.commit()
            return item
            
        except Exception as e:
            session.rollback()
            if "case-insensitive" in str(e):
                raise ValueError(
                    CATALOG_CONFIG['ERROR_MESSAGES']['DUPLICATE_ERROR'].format(
                        title=title
                    )
                )
            raise
        finally:
            session.close()

    def archive_item(self, session, title: str) -> None:
        """Archive a catalog item.
        
        Args:
            session: Database session
            title: Title of item to archive
            
        Raises:
            ValueError: If item is already archived or not found
        """
        # Get the item
        item = session.query(CatalogItem).filter(
            CatalogItem.title == title,
            CatalogItem.deleted == False
        ).first()
        
        if not item:
            raise ValueError(CATALOG_CONFIG['ERROR_MESSAGES']['ARCHIVE_ERROR'].format(
                error=f"Item not found: {title}"
            ))
        
        # Check if already archived
        if item.status == 'archived':
            raise ValueError(CATALOG_CONFIG['ERROR_MESSAGES']['ARCHIVE_ERROR'].format(
                error=f"Item is already archived: {title}"
            ))
        
        # Archive the item
        item.status = 'archived'
        item.archived_date = int(datetime.utcnow().timestamp())
        session.commit()

    def add_catalog_tag(self, session, catalog_id: int, tag_id: int) -> CatalogTag:
        """Add a tag to a catalog item.
        
        Args:
            session: Database session
            catalog_id: ID of catalog item
            tag_id: ID of tag to add
            
        Returns:
            CatalogTag: The newly created catalog tag
            
        Raises:
            ValueError: If item or tag is archived
        """
        # Check if item is archived
        item = session.query(CatalogItem).filter(CatalogItem.id == catalog_id).first()
        if not item:
            raise ValueError("Item not found")
        if item.deleted:
            raise ValueError("Cannot tag archived item")
            
        # Check if tag is archived
        tag = session.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            raise ValueError("Tag not found")
        if tag.deleted:
            raise ValueError("Cannot use archived tag")
            
        # Add the tag
        catalog_tag = CatalogTag(catalog_id=catalog_id, tag_id=tag_id)
        session.add(catalog_tag)
        session.commit()
        return catalog_tag

    def process_input(self, command: str, args: str) -> str:
        """Process user input and generate response"""
        session = self.get_session()
        try:
            if command == 'archive':
                if not args:
                    return "Please provide item title to archive"
                title = args.strip()
                
                try:
                    self.archive_item(session, title)
                    return f"Archived item: {title}"
                except ValueError as e:
                    raise  # Re-raise to be caught by test
                
            elif command == 'search':
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
                has_duplicates, duplicates, potential_matches = self.check_semantic_duplicates(session, title, all_items)
                if has_duplicates:
                    if self.interactive:
                        print("\nFound semantically similar items:")
                        for item, score in duplicates:
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
                        similar_list = "\n".join(f"- {item[0].title} ({'archived' if item[0].deleted else 'active'})" 
                                               for item in duplicates)
                        return f"Found semantically similar items:\n{similar_list}\nUse --force to add anyway"
                
                if potential_matches:
                    # Format potential matches for display
                    match_info = "\n".join([
                        f"- {item.title} (similarity: {score:.2f}): {reason}"
                        for item, score, reason in potential_matches
                    ])
                    
                    if self.interactive:
                        print("\nFound potentially similar items:")
                        print(match_info)
                        print("\nWould you like to:")
                        print("1. Create new item anyway")
                        print("2. Cancel")
                        choice = input("Enter choice (1-2): ").strip()
                        
                        if choice == "2":
                            return "Operation cancelled"
                    else:
                        return f"Found potentially similar items:\n{match_info}\nUse --force to add anyway"
                
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
                has_duplicates, duplicates, potential_matches = self.check_semantic_duplicates(session, tag_name, all_tags)
                if has_duplicates:
                    if self.interactive:
                        print("\nFound semantically similar tags:")
                        for tag, score in duplicates:
                            status = "(archived)" if tag.deleted else "(active)"
                            print(f"- {tag.name} {status} (similarity: {score:.2f})")
                        print("\nWould you like to:")
                        print("1. Create new tag anyway")
                        print("2. Use existing tag")
                        print("3. Cancel")
                        choice = input("Enter choice (1-3): ").strip()
                        
                        if choice == "2" and duplicates:
                            tag = duplicates[0][0]  # Use the most similar tag
                            if tag.deleted:
                                tag.deleted = False
                                session.commit()
                            tag_name = tag.name
                        elif choice == "3":
                            return "Operation cancelled"
                    else:
                        similar_list = "\n".join(f"- {tag[0].name} ({'archived' if tag[0].deleted else 'active'})" 
                                               for tag in duplicates)
                        return f"Found semantically similar tags:\n{similar_list}\nUse --force to add anyway"
                
                if potential_matches:
                    # Format potential matches for display
                    match_info = "\n".join([
                        f"- {tag.name} (similarity: {score:.2f}): {reason}"
                        for tag, score, reason in potential_matches
                    ])
                    
                    if self.interactive:
                        print("\nFound potentially similar tags:")
                        print(match_info)
                        print("\nWould you like to:")
                        print("1. Create new tag anyway")
                        print("2. Use existing tag")
                        print("3. Cancel")
                        choice = input("Enter choice (1-3): ").strip()
                        
                        if choice == "2" and potential_matches:
                            tag = potential_matches[0][0]  # Use the most similar tag
                            if tag.deleted:
                                tag.deleted = False
                                session.commit()
                            tag_name = tag.name
                        elif choice == "3":
                            return "Operation cancelled"
                    else:
                        return f"Found potentially similar tags:\n{match_info}\nUse --force to add anyway"
                
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
                has_duplicates, duplicates, potential_matches = self.check_semantic_duplicates(session, tag_name, all_tags)
                if has_duplicates:
                    if self.interactive:
                        print("\nFound semantically similar tags:")
                        for tag, score in duplicates:
                            status = "(archived)" if tag.deleted else "(active)"
                            print(f"- {tag.name} {status} (similarity: {score:.2f})")
                        print("\nWould you like to:")
                        print("1. Create new tag anyway")
                        print("2. Use existing tag")
                        print("3. Cancel")
                        choice = input("Enter choice (1-3): ").strip()
                        
                        if choice == "2" and duplicates:
                            tag = duplicates[0][0]  # Use the most similar tag
                            if tag.deleted:
                                tag.deleted = False
                                session.commit()
                            tag_name = tag.name
                        elif choice == "3":
                            return "Operation cancelled"
                    else:
                        similar_list = "\n".join(f"- {tag[0].name} ({'archived' if tag[0].deleted else 'active'})" 
                                               for tag in duplicates)
                        return f"Found semantically similar tags:\n{similar_list}\nUse --force to add anyway"
                
                if potential_matches:
                    # Format potential matches for display
                    match_info = "\n".join([
                        f"- {tag.name} (similarity: {score:.2f}): {reason}"
                        for tag, score, reason in potential_matches
                    ])
                    
                    if self.interactive:
                        print("\nFound potentially similar tags:")
                        print(match_info)
                        print("\nWould you like to:")
                        print("1. Create new tag anyway")
                        print("2. Use existing tag")
                        print("3. Cancel")
                        choice = input("Enter choice (1-3): ").strip()
                        
                        if choice == "2" and potential_matches:
                            tag = potential_matches[0][0]  # Use the most similar tag
                            if tag.deleted:
                                tag.deleted = False
                                session.commit()
                            tag_name = tag.name
                        elif choice == "3":
                            return "Operation cancelled"
                    else:
                        return f"Found potentially similar tags:\n{match_info}\nUse --force to add anyway"
                
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

            elif command == 'semantic_search':
                if not args:
                    return "Please provide a search query"
                query = args.strip()
                items = self.semantic_search(query)
                if not items:
                    return "No matching items found"
                return "\n".join(f"{item.title}: {item.content[:100]}..." for item in items)

            else:
                return f"Unknown command: {command}"
            
        except Exception as e:
            session.rollback()
            return f"Error: {str(e)}"
            
        finally:
            session.close()

    def process_natural_language_query(self, query: str) -> dict:
        """Process a natural language query using Claude AI.
        
        Args:
            query: The natural language query from the user
            
        Returns:
            dict: Processed query with extracted intents and entities
        """
        system_prompt = CATALOG_CONFIG['PROMPTS']['QUERY_ANALYSIS']
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        try:
            response = self.client.messages.create(
                model=API_CONFIG['MODEL'],
                max_tokens=API_CONFIG['MAX_TOKENS'],
                temperature=API_CONFIG['TEMPERATURE'],
                messages=messages
            )
            
            # Parse the structured response
            analysis = json.loads(response.content)
            return {
                'intent': analysis.get('intent'),
                'entities': analysis.get('entities', {}),
                'filters': analysis.get('filters', {}),
                'search_terms': analysis.get('search_terms', [])
            }
        except Exception as e:
            self.test_logger.error(f"Error processing query with Claude: {str(e)}")
            return {
                'intent': 'unknown',
                'entities': {},
                'filters': {},
                'search_terms': []
            }

    def semantic_search(self, query: str) -> List[CatalogItem]:
        """Perform semantic search using Claude AI.
        
        Args:
            query: Natural language search query
            
        Returns:
            List[CatalogItem]: Matching catalog items
        """
        try:
            # Process the query
            analysis = self.process_natural_language_query(query)
            
            session = self.get_session()
            items = []
            
            # Use extracted search terms and filters
            if analysis['search_terms']:
                base_query = session.query(CatalogItem)
                
                # Apply semantic filtering
                for term in analysis['search_terms']:
                    base_query = base_query.filter(
                        CatalogItem.title.ilike(f'%{term}%') |
                        CatalogItem.content.ilike(f'%{term}%') |
                        CatalogItem.description.ilike(f'%{term}%')
                    )
                
                # Apply entity-based filters
                if 'date' in analysis['filters']:
                    date_filter = analysis['filters']['date']
                    if date_filter.get('start'):
                        base_query = base_query.filter(
                            CatalogItem.created_date >= int(datetime.strptime(
                                date_filter['start'], '%Y-%m-%d'
                            ).timestamp())
                        )
                    if date_filter.get('end'):
                        base_query = base_query.filter(
                            CatalogItem.created_date <= int(datetime.strptime(
                                date_filter['end'], '%Y-%m-%d'
                            ).timestamp())
                        )
                
                # Filter out deleted items and respect status
                base_query = base_query.filter(
                    CatalogItem.deleted == False,
                    CatalogItem.status != 'archived'
                )
                
                if 'status' in analysis['filters']:
                    status = analysis['filters']['status']
                    if status in CATALOG_CONFIG['VALID_STATUSES']:
                        base_query = base_query.filter(CatalogItem.status == status)
                
                if 'tags' in analysis['filters']:
                    for tag in analysis['filters']['tags']:
                        base_query = base_query.join(CatalogTag).join(Tag).filter(
                            Tag.name.ilike(f'%{tag}%'),
                            Tag.deleted == False
                        )
                
                # Apply metadata filters if present
                if 'metadata' in analysis['filters']:
                    metadata_filters = analysis['filters']['metadata']
                    for key, value in metadata_filters.items():
                        base_query = base_query.filter(
                            CatalogItem.item_metadata[key].astext == str(value)
                        )
                
                items = base_query.all()
                
                # Sort by relevance if needed
                if items and len(items) > 1:
                    items = self.rank_results_by_relevance(items, query)
            
            session.close()
            return items
            
        except Exception as e:
            self.test_logger.error(f"Error in semantic search: {str(e)}")
            return []

    def rank_results_by_relevance(self, items: list, query: str) -> list:
        """Rank search results by relevance using Claude AI.
        
        Args:
            items: List of catalog items to rank
            query: Original search query
            
        Returns:
            list: Ranked list of items
        """
        try:
            # Prepare items for ranking
            item_texts = [f"Title: {item.title}\nContent: {item.content}" for item in items]
            
            # Get relevance scores using Claude
            system_prompt = CATALOG_CONFIG['PROMPTS']['RELEVANCE_RANKING']
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {query}\nItems: {json.dumps(item_texts)}"}
            ]
            
            response = self.client.messages.create(
                model=API_CONFIG['MODEL'],
                max_tokens=API_CONFIG['MAX_TOKENS'],
                temperature=0.0,  # Use deterministic output for ranking
                messages=messages
            )
            
            # Parse relevance scores
            scores = json.loads(response.content)
            
            # Sort items by relevance score
            ranked_items = sorted(
                zip(items, scores),
                key=lambda x: x[1],
                reverse=True
            )
            
            return [item for item, _ in ranked_items]
            
        except Exception as e:
            self.test_logger.error(f"Error ranking results: {str(e)}")
            return items

    def process_input(self, user_input: str) -> dict:
        """Process user input and return response."""
        session = self.get_session()
        try:
            response = self.client.messages.create(
                model=API_CONFIG['MODEL'],
                max_tokens=API_CONFIG['MAX_TOKENS'],
                temperature=API_CONFIG['TEMPERATURE'],
                messages=[{
                    "role": "user", 
                    "content": user_input
                }]
            )

            # Parse Claude response
            error_context = {
                'error_type': "catalog_chat",
                'user_input': user_input
            }
            result = parse_claude_response(response.content[0].text, error_context)
            
            # Log the interaction
            self.chat_logger.log_interaction(
                user_input=user_input,
                system_response=result or response.content[0].text,
                model=API_CONFIG['MODEL'],
                status="success" if result else "error",
                error_details=None if result else "Failed to parse response",
                metadata={
                    "mode": self.mode,
                    "interactive": self.interactive,
                    "tokens": len(response.content[0].text.split())
                }
            )
            
            # Rotate logs if needed
            self.chat_logger.rotate_logs()
            
            if not result:
                return {
                    'error': "Failed to parse response from Claude",
                    'raw_response': response.content[0].text
                }
            
            return result
            
        except Exception as e:
            # Log the error
            error_msg = str(e)
            try:
                self.chat_logger.log_interaction(
                    user_input=user_input,
                    system_response=error_msg,
                    model=API_CONFIG['MODEL'],
                    status="error",
                    error_details=error_msg
                )
            except Exception as log_error:
                self.test_logger.error(f"Failed to log chat error: {str(log_error)}")
            
            session.rollback()
            return f"Error: {error_msg}"
        finally:
            session.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Marian Catalog System")
    parser.add_argument("--no-tests", action="store_true", help="Skip running integration tests")
    parser.add_argument("--no-semantic", action="store_true", help="Disable semantic checking for duplicates and search")
    args = parser.parse_args()
    
    if not args.no_tests:
        # Run integration tests
        import unittest
        from tests.test_catalog import TestCatalog
        
        # Create test suite
        suite = unittest.TestLoader().loadTestsFromTestCase(TestCatalog)
        
        # Run tests
        test_logger = setup_logging('test_catalog')
        test_logger.info("Running integration tests...")
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if not result.wasSuccessful():
            sys.exit(1)
    else:
        # Normal app initialization
        chat = CatalogChat(enable_semantic=not args.no_semantic)
        test_logger = setup_logging('test_catalog')
        test_logger.info("Database tables created successfully")
        test_logger.info(f"System State: mode=cli, db_path={chat.db_path}, chat_log={chat.chat_log}, semantic_enabled={chat.enable_semantic}")
