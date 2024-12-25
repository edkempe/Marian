import datetime
import unittest
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

from app_catalog import CatalogChat
from models.catalog import Base, CatalogItem, Tag, CatalogTag
from marian_lib.logger import setup_logger

class TestCatalog(unittest.TestCase):
    """Test cases for the catalog functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Use in-memory SQLite for testing
        cls.engine = create_engine('sqlite:///:memory:')
        cls.Session = sessionmaker(bind=cls.engine)
        Base.metadata.create_all(cls.engine)
        
        # Set up logging
        cls.test_logger = setup_logger('test_catalog')
        
        # Initialize CatalogChat
        cls.chat = CatalogChat(db_path=':memory:', mode='test')
    
    def setUp(self):
        """Set up test case"""
        self.session = self.Session()
    
    def tearDown(self):
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
        test_marker = "DUP_TEST_" + datetime.datetime.now().isoformat()
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
            self.assertTrue(
                self.session.query(CatalogItem).filter(CatalogItem.title == test_title).first(),
                "Failed to add initial item"
            )
            
            # Try adding duplicate item
            with self.assertRaises(ValueError) as cm:
                item2 = CatalogItem(title=test_title, content="Different content")
                self.session.add(item2)
                self.session.commit()
            self.assertIn("case-insensitive", str(cm.exception))
            self.session.rollback()
            
            # Try adding case-variant duplicate
            with self.assertRaises(ValueError) as cm:
                item3 = CatalogItem(title=test_title.upper(), content="Different content")
                self.session.add(item3)
                self.session.commit()
            self.assertIn("case-insensitive", str(cm.exception))
            self.session.rollback()
            
            # Test duplicate tags
            # Add initial tag
            tag = Tag(name=test_tag)
            self.session.add(tag)
            self.session.commit()
            self.assertTrue(
                self.session.query(Tag).filter(Tag.name == test_tag).first(),
                "Failed to add initial tag"
            )
            
            # Try adding duplicate tag
            with self.assertRaises(ValueError) as cm:
                tag2 = Tag(name=test_tag)
                self.session.add(tag2)
                self.session.commit()
            self.assertIn("case-insensitive", str(cm.exception))
            self.session.rollback()
            
            # Try adding case-variant duplicate tag
            with self.assertRaises(ValueError) as cm:
                tag3 = Tag(name=test_tag.upper())
                self.session.add(tag3)
                self.session.commit()
            self.assertIn("case-insensitive", str(cm.exception))
            self.session.rollback()
            
        finally:
            self.cleanup_test_data(test_marker)

    def test_archived_item_handling(self):
        """Test handling of archived items and tags"""
        test_marker = "ARCHIVED_TEST_" + datetime.datetime.now().isoformat()
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
            self.assertTrue(item.deleted, "Failed to archive item")
            
            # Try to tag archived item
            with self.assertRaises(Exception) as cm:
                new_tag = Tag(name=f"{test_marker}_new_tag")
                self.session.add(new_tag)
                self.session.commit()
                
                catalog_tag = CatalogTag(catalog_id=item.id, tag_id=new_tag.id)
                self.session.add(catalog_tag)
                self.session.commit()
            self.assertIn("archived", str(cm.exception).lower())
            self.session.rollback()
            
            # Archive tag
            tag.deleted = True
            self.session.commit()
            self.assertTrue(tag.deleted, "Failed to archive tag")
            
            # Try to use archived tag on new item
            new_item = CatalogItem(title=new_item_title, content="Some content")
            self.session.add(new_item)
            self.session.commit()
            
            with self.assertRaises(Exception) as cm:
                catalog_tag = CatalogTag(catalog_id=new_item.id, tag_id=tag.id)
                self.session.add(catalog_tag)
                self.session.commit()
            self.assertIn("archived", str(cm.exception).lower())
            self.session.rollback()
            
        finally:
            self.cleanup_test_data(test_marker)

    def test_full_lifecycle(self):
        """Test complete lifecycle of catalog items and tags"""
        test_marker = "LIFECYCLE_TEST_" + datetime.datetime.now().isoformat()
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
                    self.assertTrue(
                        self.session.query(CatalogTag).filter_by(catalog_id=item.id, tag_id=tag.id).first(),
                        f"Failed to add tag {tag.name}"
                    )
            
            # Verify findable by each tag
            for tag in test_tags:
                result = self.session.query(CatalogItem).join(CatalogTag).join(Tag).filter(
                    Tag.name == tag.name,
                    CatalogItem.deleted == False
                ).first()
                
                self.assertTrue(result and result.title == test_title, f"Item not found by tag {tag.name}")
            
            # Query by title and verify all tags present
            tags = self.session.query(Tag).join(CatalogTag).join(CatalogItem).filter(
                CatalogItem.title == test_title
            ).all()
            self.assertEqual(len(tags), len(test_tags), "Wrong number of tags found")
            
            tag_names = set(tag.name for tag in tags)
            for tag in test_tags:
                self.assertIn(tag.name, tag_names, f"Tag {tag.name} not found")
            
            # Update content and verify tags remain
            new_description = f"Updated Description {test_marker}"
            item.description = new_description
            self.session.commit()
            self.assertEqual(item.description, new_description, "Update failed")
            
            # Test tag renaming
            test_tag = test_tags[0]
            updated_tag_name = f"{test_tag.name}_updated"
            test_tag.name = updated_tag_name
            self.session.commit()
            
            # Verify item findable by new tag name
            result = self.session.query(CatalogItem).join(CatalogTag).join(Tag).filter(
                Tag.name == updated_tag_name
            ).first()
            self.assertTrue(result and result.title == test_title, "Item not found by updated tag name")
            
            # Test tag soft deletion
            test_tag.deleted = True
            self.session.commit()
            
            # Verify tag exists in archive
            result = self.session.query(Tag).filter(Tag.id == test_tag.id).first()
            self.assertTrue(result.deleted, "Tag not marked as deleted")
            
            # Verify tag not visible in active tags list
            tags = self.session.query(Tag).filter(Tag.deleted == False).all()
            self.assertNotIn(updated_tag_name, [t.name for t in tags], "Deleted tag still visible in active tags")
            
            # Test tag restoration
            test_tag.deleted = False
            self.session.commit()
            
            # Test item soft deletion
            item.deleted = True
            self.session.commit()
            
            # Verify item not visible in active items list
            items = self.session.query(CatalogItem).filter(CatalogItem.deleted == False).all()
            self.assertNotIn(test_title, [i.title for i in items], "Deleted item still visible in active items")
            
            # Verify item exists in archive
            result = self.session.query(CatalogItem).filter(CatalogItem.id == item.id).first()
            self.assertTrue(result.deleted, "Item not marked as deleted")
            
            # Verify item not visible when viewing tags
            items = self.session.query(CatalogItem).join(CatalogTag).join(Tag).filter(
                Tag.name == updated_tag_name,
                CatalogItem.deleted == False
            ).all()
            self.assertNotIn(test_title, [i.title for i in items], "Deleted item still visible on tag")
            
        finally:
            self.cleanup_test_data(test_marker)

    def test_semantic_matching(self):
        """Test semantic matching functionality"""
        test_marker = "SEMANTIC_TEST_" + datetime.datetime.now().isoformat()
        
        try:
            # Clean up any leftover test data
            self.cleanup_test_data(test_marker)
            
            # Add test item directly to database
            item = CatalogItem(
                title=f"{test_marker}_Python Guide",
                content="A comprehensive guide to Python programming"
            )
            self.session.add(item)
            self.session.commit()
            
            # Test semantic similarity detection
            similar_items = self.chat.get_semantic_matches(
                "Python Tutorial",
                [item.title],
                threshold=0.7
            )
            self.assertTrue(len(similar_items) > 0, "Should detect semantic similarity")
            self.assertEqual(similar_items[0][0], item.title)
            self.assertGreaterEqual(similar_items[0][1], 0.7)
            
            # Test different meanings
            different_items = self.chat.get_semantic_matches(
                "Python Snake",
                [item.title],
                threshold=0.7
            )
            self.assertEqual(len(different_items), 0, "Should not detect similarity for different concepts")
            
            # Add test tag directly to database
            tag = Tag(name=f"{test_marker}_programming")
            self.session.add(tag)
            self.session.commit()
            
            # Test tag similarity
            similar_tags = self.chat.get_semantic_matches(
                "coding",
                [tag.name],
                threshold=0.7
            )
            self.assertTrue(len(similar_tags) > 0, "Should detect similar tags")
            self.assertEqual(similar_tags[0][0], tag.name)
            self.assertGreaterEqual(similar_tags[0][1], 0.7)
            
            # Test archived items
            item.deleted = True
            self.session.commit()
            
            # Test empty database handling
            empty_matches = self.chat.get_semantic_matches("test", [], threshold=0.7)
            self.assertEqual(len(empty_matches), 0, "Should handle empty item list")
            
            # Add test item with special chars
            special_item = CatalogItem(
                title=f"{test_marker}_Python (Programming)",
                content="Guide to Python"
            )
            self.session.add(special_item)
            self.session.commit()
            
            special_matches = self.chat.get_semantic_matches(
                "Python [Code]",
                [special_item.title],
                threshold=0.7
            )
            self.assertTrue(len(special_matches) > 0, "Should handle special characters")
            
        finally:
            self.cleanup_test_data(test_marker)

    def test_semantic_duplicates(self):
        """Test semantic duplicate detection"""
        test_marker = "SEMANTIC_DUP_TEST_" + datetime.datetime.now().isoformat()
        
        try:
            # Clean up any leftover test data
            self.cleanup_test_data(test_marker)
            
            # Add test items directly to database
            item1 = CatalogItem(
                title=f"{test_marker}_Python Guide",
                content="A guide to Python"
            )
            item2 = CatalogItem(
                title=f"{test_marker}_JavaScript Guide",
                content="A guide to JavaScript"
            )
            self.session.add_all([item1, item2])
            self.session.commit()
            
            # Get all items
            all_items = self.session.query(CatalogItem).filter(
                CatalogItem.title.like(f"{test_marker}%")
            ).all()
            
            # Test duplicate detection
            has_dups, similar = self.chat.check_semantic_duplicates(
                self.session,
                "Python Tutorial",
                all_items
            )
            self.assertTrue(has_dups, "Should detect similar item")
            self.assertTrue(len(similar) > 0)
            self.assertEqual(similar[0][0].title, item1.title)
            
            # Test non-duplicate
            has_dups, similar = self.chat.check_semantic_duplicates(
                self.session,
                "Ruby Guide",
                all_items
            )
            self.assertFalse(has_dups, "Should not detect similarity")
            self.assertEqual(len(similar), 0)
            
            # Add test tag directly to database
            tag = Tag(name=f"{test_marker}_programming")
            self.session.add(tag)
            self.session.commit()
            
            # Test tag duplicates
            all_tags = self.session.query(Tag).filter(
                Tag.name.like(f"{test_marker}%")
            ).all()
            
            has_dups, similar = self.chat.check_semantic_duplicates(
                self.session,
                "coding",
                all_tags
            )
            self.assertTrue(has_dups, "Should detect similar tag")
            self.assertTrue(len(similar) > 0)
            self.assertEqual(similar[0][0].name, tag.name)
            
        finally:
            self.cleanup_test_data(test_marker)

if __name__ == '__main__':
    unittest.main()
