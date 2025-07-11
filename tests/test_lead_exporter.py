import os
import shutil
import tempfile
import unittest

import pandas as pd
import polars as pl

from main import LeadExporter


class TestLeadExporter(unittest.TestCase):
    def setUp(self):
        self.test_output_dir = tempfile.mkdtemp()
        
        self.sample_groups = {
            'Test Sponsor': pl.DataFrame({
                'Full name': ['A', 'B'],
                'Job Title': ['X', 'Y'],
                'Email': ['a@example.com', 'b@example.com'],
                'tech stack': ['1', '2'],
                'Years of Experience': [1, 2],
                'country': ['ES', 'US'],
                'city': ['BCN', 'NY'],
                'company': ['Co1', 'Co2'],
                'Lead Status': ['n', 'c'],
                'Sponsor notes': ['note1', 'note2']
            }),
            'Another Sponsor': pl.DataFrame({
                'Full name': ['C'],
                'Job Title': ['Z'],
                'Email': ['c@example.com'],
                'tech stack': ['3'],
                'Years of Experience': [3],
                'country': ['FR'],
                'city': ['PA'],
                'company': ['Co3'],
                'Lead Status': ['n'],
                'Sponsor notes': ['note3']
            })
        }
        
        self.exporter = LeadExporter(self.test_output_dir)

    def tearDown(self):
        shutil.rmtree(self.test_output_dir)

    def test_export(self):
        """Test that the exporter correctly creates Excel files for each group."""
        self.exporter.export(self.sample_groups)
        
        expected_files = [
            'Test_Sponsor_devbcn-25-leads.xlsx',
            'Another_Sponsor_devbcn-25-leads.xlsx'
        ]
        
        for filename in expected_files:
            file_path = os.path.join(self.test_output_dir, filename)
            self.assertTrue(os.path.exists(file_path), f"Expected file {filename} was not created")
            
            try:
                df = pd.read_excel(file_path)
                if 'Test_Sponsor' in filename:
                    self.assertEqual(len(df), 2)
                else:
                    self.assertEqual(len(df), 1)
                
                expected_columns = [
                    'Full name', 'Job Title', 'Email', 'tech stack', 
                    'Years of Experience', 'country', 'city', 'company', 
                    'Lead Status', 'Sponsor notes'
                ]
                for col in expected_columns:
                    self.assertIn(col, df.columns)
                
            except Exception as e:
                self.fail(f"Failed to read Excel file {filename}: {e}")

    def test_export_empty_groups(self):
        """Test that the exporter handles empty groups correctly."""
        self.exporter.export({})
        
        self.assertEqual(len(os.listdir(self.test_output_dir)), 0)

if __name__ == '__main__':
    unittest.main()