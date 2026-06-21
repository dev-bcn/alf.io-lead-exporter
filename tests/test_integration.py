import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd
import polars as pl

from main import main, LeadTransformer


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.original_output_dir = "output"
        self.test_dir = tempfile.mkdtemp()
        self.test_output_dir = tempfile.mkdtemp()
        self.input_file_path = os.path.join(self.test_dir, "sample_leads.xlsx")
        self.output_dir_path = os.path.join(self.test_dir, "test_output")

        sample_data = {
            'Full name': ['Alice', 'Bob', 'Charlie'],
            'jobTitle': ['Dev', 'Eng', 'PM'],
            'Email': ['alice@a.com', 'bob@b.com', 'charlie@c.com'],
            'tech stack': ['Python', 'Java', 'JS'],
            'Years of Experience': [5, 10, 3],
            'country': ['ES', 'FR', 'UK'],
            'city': ['BCN', 'PAR', 'LON'],
            'company': ['A', 'B', 'C'],
            'Lead Status': ['New', 'Contacted', 'New'],
            'Sponsor notes': ['', '', ''],
            'Description': ['Sponsor One', 'Sponsor Two', 'Sponsor One']
        }
        df = pd.DataFrame(sample_data)
        df.to_excel(self.input_file_path, index=False)

    def tearDown(self):
        """Remove the temporary directory and all its contents after the test."""
        shutil.rmtree(self.test_dir)

    def test_main_function_with_args(self):
        """Test the end-to-end functionality by simulating command-line arguments."""
        test_args = [
            "main.py",
            self.input_file_path,
        ]

        with patch('sys.argv', test_args):
            main()

        self.assertTrue(os.path.exists("output"))
        output_files = os.listdir("output")
        self.assertEqual(len(output_files), 2, "Expected two output files for two sponsors")

        expected_filenames = [
            "Sponsor_One_devbcn-25-leads.xlsx",
            "Sponsor_Two_devbcn-25-leads.xlsx"
        ]
        for fname in expected_filenames:
            self.assertIn(fname, output_files, f"Expected file {fname} was not created")

        sponsor_one_file = os.path.join("output", "Sponsor_One_devbcn-25-leads.xlsx")
        try:
            df = pd.read_excel(sponsor_one_file)
            expected_columns = set(LeadTransformer.REQUIRED_COLS) - {'Description'}

            self.assertEqual(set(df.columns), expected_columns)
            self.assertEqual(len(df), 2, "Sponsor One file should contain 2 leads")
            self.assertEqual(df.iloc[0]['Full name'], 'Alice')
        except Exception as e:
            self.fail(f"Failed to read or validate Excel file {sponsor_one_file}: {e}")

if __name__ == '__main__':
    unittest.main()
