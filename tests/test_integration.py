import os
import shutil
import tempfile
import unittest

import pandas as pd

from main import main


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.original_output_dir = "output"
        
        self.test_output_dir = tempfile.mkdtemp()
        
        if os.path.exists(self.original_output_dir):
            self.original_output_dir_exists = True
            self.original_output_dir_backup = tempfile.mkdtemp()
            for item in os.listdir(self.original_output_dir):
                src = os.path.join(self.original_output_dir, item)
                dst = os.path.join(self.original_output_dir_backup, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            shutil.rmtree(self.original_output_dir)
        else:
            self.original_output_dir_exists = False
        
        os.makedirs(self.original_output_dir)

    def tearDown(self):
        shutil.rmtree(self.test_output_dir)
        
        shutil.rmtree(self.original_output_dir)
        if self.original_output_dir_exists:
            os.makedirs(self.original_output_dir)
            for item in os.listdir(self.original_output_dir_backup):
                src = os.path.join(self.original_output_dir_backup, item)
                dst = os.path.join(self.original_output_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            shutil.rmtree(self.original_output_dir_backup)

    def test_main_function(self):
        """Test the end-to-end functionality of the main function."""
        main()
        
        self.assertTrue(os.path.exists(self.original_output_dir))
        output_files = os.listdir(self.original_output_dir)
        self.assertGreater(len(output_files), 0, "No output files were created")
        
        for filename in output_files:
            if filename.endswith('.xlsx'):
                file_path = os.path.join(self.original_output_dir, filename)
                try:
                    df = pd.read_excel(file_path)
                    expected_columns = [
                        'Full name', 'Job Title', 'Email', 'tech stack', 
                        'Years of Experience', 'country', 'city', 'company', 
                        'Lead Status', 'Sponsor notes'
                    ]
                    for col in expected_columns:
                        self.assertIn(col, df.columns)
                except Exception as e:
                    self.fail(f"Failed to read Excel file {filename}: {e}")

if __name__ == '__main__':
    unittest.main()