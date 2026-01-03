"""Unit tests for configuration module."""
import unittest
from pathlib import Path
from src.utils.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for Config."""

    def test_base_directories_exist(self):
        """Test that base directories are properly set."""
        self.assertIsInstance(Config.BASE_DIR, Path)
        self.assertIsInstance(Config.TEMP_DIR, Path)
        self.assertIsInstance(Config.DATA_DIR, Path)

        # Directories should exist after initialization
        self.assertTrue(Config.TEMP_DIR.exists())
        self.assertTrue(Config.DATA_DIR.exists())

    def test_file_paths_are_paths(self):
        """Test that file paths are Path objects."""
        self.assertIsInstance(Config.PARA_FILE, Path)
        self.assertIsInstance(Config.IMP_INFO_FILE, Path)
        self.assertIsInstance(Config.IMP_SENTENCES_FILE, Path)

    def test_get_temp_file_path(self):
        """Test getting temp file paths."""
        test_file = Config.get_temp_file_path("test.txt")
        self.assertIsInstance(test_file, Path)
        self.assertEqual(test_file.parent, Config.TEMP_DIR)
        self.assertEqual(test_file.name, "test.txt")

    def test_get_data_file_path(self):
        """Test getting data file paths."""
        test_file = Config.get_data_file_path("test_data.txt")
        self.assertIsInstance(test_file, Path)
        self.assertEqual(test_file.parent, Config.DATA_DIR)
        self.assertEqual(test_file.name, "test_data.txt")

    def test_cleanup_temp_files(self):
        """Test cleanup of temporary files."""
        # Create temporary test files
        test_files = [
            Config.PARA_FILE,
            Config.IMP_INFO_FILE,
            Config.IMP_SENTENCES_FILE
        ]

        for file_path in test_files:
            file_path.touch()
            self.assertTrue(file_path.exists())

        # Cleanup
        Config.cleanup_temp_files()

        # Files should be removed
        for file_path in test_files:
            self.assertFalse(file_path.exists())

    def test_default_values(self):
        """Test default configuration values."""
        self.assertEqual(Config.MAX_SEARCH_RESULTS, 10)
        self.assertEqual(Config.TOP_PARAGRAPHS, 4)
        self.assertGreater(Config.REQUEST_TIMEOUT, 0)


if __name__ == '__main__':
    unittest.main()
