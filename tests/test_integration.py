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
            'Job Title': ['Dev', 'Eng', 'PM'],
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
        df = pl.DataFrame(sample_data)
        df.write_excel(self.input_file_path)

    def tearDown(self):
        """Remove the temporary directory and all its contents after the test."""
        shutil.rmtree(self.test_dir)

def test_main_function_with_args(self):
    """Test the end-to-end functionality by simulating command-line arguments."""
    # 1. Define the arguments to simulate, including the script name
    test_args = [
        "main.py",  # The first element is always the script name
        self.input_file_path,
        "-o",
        self.output_dir_path
    ]

    # 2. Use patch to temporarily replace sys.argv with our test arguments
    with patch('sys.argv', test_args):
        main()

    # 3. Assertions now check the temporary output directory
    self.assertTrue(os.path.exists(self.output_dir_path))
    output_files = os.listdir(self.output_dir_path)
    self.assertEqual(len(output_files), 2, "Expected two output files for two sponsors")

    # Check for expected file names (based on our sample data)
    expected_filenames = [
        "Sponsor_One_devbcn-25-leads.xlsx",
        "Sponsor_Two_devbcn-25-leads.xlsx"
    ]
    for fname in expected_filenames:
        self.assertIn(fname, output_files, f"Expected file {fname} was not created")

    # 4. Verify the content of one of the generated files
    sponsor_one_file = os.path.join(self.output_dir_path, "Sponsor_One_devbcn-25-leads.xlsx")
    try:
        # Read with pandas for easy column checking, as in the original test
        df = pd.read_excel(sponsor_one_file)
        # The transformer should drop the 'Description' column
        expected_columns = set(LeadTransformer.REQUIRED_COLS) - {'Description'}

        self.assertEqual(set(df.columns), expected_columns)
        self.assertEqual(len(df), 2, "Sponsor One file should contain 2 leads")
        self.assertEqual(df.iloc[0]['Full name'], 'Alice')

    except Exception as e:
        self.fail(f"Failed to read or validate Excel file {sponsor_one_file}: {e}")

if __name__ == '__main__':
    unittest.main()