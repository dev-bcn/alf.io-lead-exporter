import unittest

import polars as pl

from main import LeadTransformer


class TestLeadTransformer(unittest.TestCase):
    def setUp(self):
        self.sample_data = pl.DataFrame({
            'Full name': ['A', 'B', 'C'],
            'Job Title': ['X', 'Y', 'Z'],
            'Email': ['a@example.com', 'b@example.com', 'c@example.com'],
            'tech stack': ['1', '2', '3'],
            'Years of Experience': [1, 2, 3],
            'country': ['ES', 'US', 'FR'],
            'city': ['BCN', 'NY', 'PA'],
            'company': ['Co', 'Co', 'Co'],
            'Lead Status': ['n', 'c', 'n'],
            'Sponsor notes': ['a', 'b', 'c'],
            'Description': ['One', 'Two', 'One'],
            'Extra Column': ['extra1', 'extra2', 'extra3']  # Column that should be filtered out
        })

    def test_extract(self):
        """Test that the extract method correctly selects only the required columns."""
        transformer = LeadTransformer()
        result = transformer.extract(self.sample_data)
        
        self.assertEqual(set(result.columns), set(LeadTransformer.REQUIRED_COLS))
        
        for col in LeadTransformer.REQUIRED_COLS:
            self.assertIn(col, result.columns)
        
        self.assertNotIn('Extra Column', result.columns)
        
        self.assertEqual(result.shape[0], 3)

    def test_group(self):
        """Test that group method correctly groups data by Description."""
        transformer = LeadTransformer()
        extracted = transformer.extract(self.sample_data)
        grouped = transformer.group(extracted)
        
        self.assertEqual(set(grouped.keys()), {'One', 'Two'})
        self.assertEqual(grouped['One'].shape[0], 2)
        self.assertEqual(grouped['Two'].shape[0], 1)
        
        for group_df in grouped.values():
            self.assertNotIn('Description', group_df.columns)
        
        one_group = grouped['One']
        self.assertEqual(one_group.filter(pl.col('Full name') == 'A').shape[0], 1)
        self.assertEqual(one_group.filter(pl.col('Full name') == 'C').shape[0], 1)

if __name__ == '__main__':
    unittest.main()