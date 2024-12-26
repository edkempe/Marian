"""Integration tests for the catalog functionality.

This test suite uses real integration testing instead of mocks:
- All API calls to Claude are real calls
- All database operations use a real SQLite database (in-memory)
- No mock objects or responses are used

This ensures our tests reflect real-world behavior and catch actual integration issues.
Test data is cleaned up after each test using test markers for isolation.

Key Integration Points Tested:
- Claude API semantic analysis
- SQLite database operations
- Full catalog item lifecycle
"""

import pytest
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import Session, sessionmaker
import os
import sys
from datetime import datetime
import json

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.catalog import CatalogItem, Tag, CatalogTag
from models.base import Base
from constants import CATALOG_CONFIG
from shared_lib.logging_util import setup_logging
from app_catalog import CatalogChat

class TestCatalog:
    """Test cases for the catalog functionality"""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment"""
        # Use in-memory SQLite for testing
        cls.engine = create_engine('sqlite:///:memory:')
        cls.Session = sessionmaker(bind=cls.engine)
        Base.metadata.create_all(cls.engine)
        
        # Set up logging
        cls.test_logger = setup_logging('test_catalog')
        
        # Initialize CatalogChat
        cls.chat = CatalogChat(db_path=':memory:', mode='test')
    
    def setup_method(self):
        """Set up test case"""
        self.session = self.Session()
        self.test_marker = f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def teardown_method(self):
        """Clean up after test case"""
        self.session.close()
    
    def cleanup_test_data(self, test_marker="TEST"):
        """Clean up test data from database"""
        try:
            # Rollback any pending transactions
            self.session.rollback()
            
            # Delete test catalog items
            self.session.query(CatalogItem).filter(
                or_(
                    CatalogItem.title.ilike(f"%{test_marker}%"),
                    CatalogItem.content.ilike(f"%{test_marker}%")
                )
            ).delete(synchronize_session=False)
            
            # Delete test tags
            self.session.query(Tag).filter(
                Tag.name.ilike(f"%{test_marker}%")
            ).delete(synchronize_session=False)
            
            self.session.commit()
            
        except Exception as e:
            self.session.rollback()
            self.test_logger.error(f"Error cleaning up test data: {str(e)}")
            raise

    def test_duplicate_handling(self):
        """Test handling of duplicate items and tags"""
        test_marker = "DUP_TEST_" + datetime.now().isoformat()
        test_title = f"{test_marker}_item"
        test_content = "Test content"
        test_tag = f"{test_marker}_tag"
        
        try:
            # Clean up any leftover test data
            self.cleanup_test_data(test_marker)
            
            # Test duplicate item titles
            # Add initial item
            item = CatalogItem(title=test_title, content=test_content)
            self.session.add(item)
            self.session.commit()
            assert self.session.query(CatalogItem).filter(CatalogItem.title == test_title).first()
            
            # Try adding duplicate item
            with pytest.raises(ValueError) as cm:
                item2 = CatalogItem(title=test_title, content="Different content")
                self.session.add(item2)
                self.session.commit()
            assert "case-insensitive" in str(cm.value)
            self.session.rollback()
            
            # Try adding case-variant duplicate
            with pytest.raises(ValueError) as cm:
                item3 = CatalogItem(title=test_title.upper(), content="Different content")
                self.session.add(item3)
                self.session.commit()
            assert "case-insensitive" in str(cm.value)
            self.session.rollback()
            
            # Test duplicate tags
            # Add initial tag
            tag = Tag(name=test_tag)
            self.session.add(tag)
            self.session.commit()
            assert self.session.query(Tag).filter(Tag.name == test_tag).first()
            
            # Try adding duplicate tag
            with pytest.raises(ValueError) as cm:
                tag2 = Tag(name=test_tag)
                self.session.add(tag2)
                self.session.commit()
            assert "case-insensitive" in str(cm.value)
            self.session.rollback()
            
            # Try adding case-variant duplicate tag
            with pytest.raises(ValueError) as cm:
                tag3 = Tag(name=test_tag.upper())
                self.session.add(tag3)
                self.session.commit()
            assert "case-insensitive" in str(cm.value)
            self.session.rollback()
            
        finally:
            self.cleanup_test_data(test_marker)

    def test_archived_item_handling(self):
        """Test handling of archived items and tags"""
        test_marker = "ARCHIVED_TEST_" + datetime.now().isoformat()
        test_title = f"{test_marker}_item"
        test_content = "Test content"
        test_tag = f"{test_marker}_tag"
        new_item_title = f"{test_marker}_another_item"
        
        try:
            # Clean up any leftover test data
            self.cleanup_test_data(test_marker)
            
            # Add and tag item
            item = CatalogItem(title=test_title, content=test_content)
            self.session.add(item)
            self.session.commit()
            
            tag = Tag(name=test_tag)
            self.session.add(tag)
            self.session.commit()
            
            if not self.session.query(CatalogTag).filter_by(catalog_id=item.id, tag_id=tag.id).first():
                catalog_tag = CatalogTag(catalog_id=item.id, tag_id=tag.id)
                self.session.add(catalog_tag)
                self.session.commit()
            
            # Archive item
            item.deleted = True
            self.session.commit()
            assert item.deleted
            
            # Try to tag archived item
            with pytest.raises(ValueError) as cm:
                CatalogTag.create(self.session, item.id, tag.id)
            assert "Cannot tag an archived item" in str(cm.value)
            self.session.rollback()
            
            # Archive tag
            tag.deleted = True
            self.session.commit()
            assert tag.deleted
            
            # Try to use archived tag on new item
            new_item = CatalogItem(title=new_item_title, content="Some content")
            self.session.add(new_item)
            self.session.commit()
            
            with pytest.raises(ValueError) as cm:
                CatalogTag.create(self.session, new_item.id, tag.id)
            assert "Cannot use an archived tag" in str(cm.value)
            self.session.rollback()
            
        finally:
            self.cleanup_test_data(test_marker)

    def test_full_lifecycle(self):
        """Test complete lifecycle of catalog items and tags"""
        test_marker = "LIFECYCLE_TEST_" + datetime.now().isoformat()
        self.test_logger.info(f"Starting lifecycle test {test_marker}")
        
        try:
            # Clean up any leftover test data
            self.cleanup_test_data(test_marker)
            
            # 1. Create test tags
            test_tags = []
            for i in range(3):
                tag_name = f"{test_marker}_tag_{i}"
                tag = Tag(name=tag_name)
                self.session.add(tag)
                self.session.commit()
                test_tags.append(tag)
            
            # 2. Add test content
            test_title = f"{test_marker}_item"
            item = CatalogItem(title=test_title, content="Test Content")
            self.session.add(item)
            self.session.commit()
            
            # Apply tags
            for tag in test_tags:
                if not self.session.query(CatalogTag).filter_by(catalog_id=item.id, tag_id=tag.id).first():
                    catalog_tag = CatalogTag(catalog_id=item.id, tag_id=tag.id)
                    self.session.add(catalog_tag)
                    self.session.commit()
                    
                    # Verify the tag was actually added
                    assert self.session.query(CatalogTag).filter_by(catalog_id=item.id, tag_id=tag.id).first()
            
            # Verify findable by each tag
            for tag in test_tags:
                result = self.session.query(CatalogItem).join(CatalogTag).join(Tag).filter(
                    Tag.name == tag.name,
                    CatalogItem.deleted == False
                ).first()
                
                assert result and result.title == test_title
                
            # Query by title and verify all tags present
            tags = self.session.query(Tag).join(CatalogTag).join(CatalogItem).filter(
                CatalogItem.title == test_title
            ).all()
            assert len(tags) == len(test_tags)
            
            tag_names = set(tag.name for tag in tags)
            for tag in test_tags:
                assert tag.name in tag_names
                
            # Update content and verify tags remain
            new_description = f"Updated Description {test_marker}"
            item.description = new_description
            self.session.commit()
            assert item.description == new_description
            
            # Test tag renaming
            test_tag = test_tags[0]
            updated_tag_name = f"{test_tag.name}_updated"
            test_tag.name = updated_tag_name
            self.session.commit()
            
            # Verify item findable by new tag name
            result = self.session.query(CatalogItem).join(CatalogTag).join(Tag).filter(
                Tag.name == updated_tag_name
            ).first()
            assert result and result.title == test_title
            
            # Test tag soft deletion
            test_tag.deleted = True
            self.session.commit()
            
            # Verify tag exists in archive
            result = self.session.query(Tag).filter(Tag.id == test_tag.id).first()
            assert result.deleted
            
            # Verify tag not visible in active tags list
            tags = self.session.query(Tag).filter(Tag.deleted == False).all()
            assert updated_tag_name not in [t.name for t in tags]
            
            # Test tag restoration
            test_tag.deleted = False
            self.session.commit()
            
            # Test item soft deletion
            item.deleted = True
            self.session.commit()
            
            # Verify item not visible in active items list
            items = self.session.query(CatalogItem).filter(CatalogItem.deleted == False).all()
            assert test_title not in [i.title for i in items]
            
            # Verify item exists in archive
            result = self.session.query(CatalogItem).filter(CatalogItem.id == item.id).first()
            assert result.deleted
            
            # Verify item not visible when viewing tags
            items = self.session.query(CatalogItem).join(CatalogTag).join(Tag).filter(
                Tag.name == updated_tag_name,
                CatalogItem.deleted == False
            ).all()
            assert test_title not in [i.title for i in items]
            
        finally:
            self.cleanup_test_data(test_marker)

    def test_semantic_matching(self):
        """Test semantic matching using real Claude API calls.
        
        This test performs real semantic analysis through the Claude API
        to validate our semantic matching functionality. No mocks are used
        to ensure we catch any API integration issues.
        """
        # Create test items
        title = f"{self.test_marker}_Python Programming Guide"
        similar_title = f"{self.test_marker}_Guide to Python Programming"  # Very similar
        related_title = f"{self.test_marker}_Programming Basics"  # Related but not duplicate
        
        # Add first item
        self.chat.add_item(title)
        
        # Adding very similar item should raise duplicate error
        with pytest.raises(ValueError) as cm:
            self.chat.add_item(similar_title)
        assert "Similar item already exists" in str(cm.value)
        
        # Adding related item should raise potential match warning
        with pytest.raises(ValueError) as cm:
            self.chat.add_item(related_title)
        assert "Found potentially similar items" in str(cm.value)
        
        # Force add the related item
        self.chat.add_item(related_title, force=True)
        
    def test_semantic_duplicates(self):
        """Test semantic duplicate detection using real Claude API calls.
        
        This test validates our duplicate detection by making real API calls
        to Claude for semantic analysis. We test both similar and dissimilar
        items to ensure accurate semantic matching in real-world scenarios.
        """
        try:
            # Add test items directly to database
            item1 = CatalogItem(
                title=f"{self.test_marker}_Python Guide",
                content="A guide to Python programming language"
            )
            item2 = CatalogItem(
                title=f"{self.test_marker}_JavaScript Guide",
                content="A guide to JavaScript programming language"
            )
            item3 = CatalogItem(
                title=f"{self.test_marker}_Programming Intro",
                content="Introduction to programming concepts"
            )
            self.session.add_all([item1, item2, item3])
            self.session.commit()
            
            # Get all items
            all_items = self.session.query(CatalogItem).filter(
                CatalogItem.title.like(f"{self.test_marker}%")
            ).all()
            
            # Test exact duplicate detection
            has_dups, duplicates, potential_matches = self.chat.check_semantic_duplicates(
                self.session,
                "Python Programming Tutorial",  # Very similar to Python Guide
                all_items
            )
            assert has_dups
            assert len(duplicates) > 0
            assert duplicates[0][0].title == item1.title
            assert duplicates[0][1] >= CATALOG_CONFIG['MATCH_THRESHOLD']
            
            # Test potential match detection
            has_dups, duplicates, potential_matches = self.chat.check_semantic_duplicates(
                self.session,
                "Introduction to Software Development",  # Related to Programming Intro
                all_items
            )
            assert not has_dups  # Not a direct duplicate
            assert len(potential_matches) > 0  # But should be flagged as potential match
            assert any(item3.title == match[0].title for match in potential_matches)
            assert all(score >= CATALOG_CONFIG['POTENTIAL_MATCH_THRESHOLD'] for _, score, _ in potential_matches)
            
            # Test non-duplicate
            has_dups, duplicates, potential_matches = self.chat.check_semantic_duplicates(
                self.session,
                "Database Design Patterns",  # Unrelated to any item
                all_items
            )
            assert not has_dups
            assert len(duplicates) == 0
            assert len(potential_matches) == 0
            
        finally:
            self.cleanup_test_data(self.test_marker)

if __name__ == '__main__':
    pytest.main()
