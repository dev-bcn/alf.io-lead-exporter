import os
import unittest

import polars as pl

from main import LeadLoader


class TestLeadLoader(unittest.TestCase):
    def setUp(self):
        self.test_file_path = "sheets/template.xlsx"
        
        self.assertTrue(os.path.exists(self.test_file_path),
                        f"Test file {self.test_file_path} does not exist")

    def test_load(self):
        """Test that the loader can load an Excel file into a Polars DataFrame."""
        loader = LeadLoader(self.test_file_path)
        df = loader.load()
        
        self.assertIsInstance(df, pl.DataFrame)
        
        self.assertGreater(df.shape[0], 0)
        self.assertGreater(df.shape[1], 0)
        
        self.assertGreater(len(df.columns), 0)

    def test_nonexistent_file(self):
        """Test that the loader raises an appropriate error for nonexistent files."""
        loader = LeadLoader("nonexistent_file.xlsx")
        
        with self.assertRaises(Exception):
            loader.load()

if __name__ == '__main__':
    unittest.main()