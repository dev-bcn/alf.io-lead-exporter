#!/usr/bin/env python3
"""
leads_processor.py

Reads an Excel lead sheet, extracts key columns, groups by 'description'
(i.e., sponsor/booth), and writes one Excel file per sponsor:
   sponsor_devbcn-25-leads.xlsx
"""

import os
from typing import Dict

import pandas as pd
import polars as pl


class LeadLoader:
    """load Excel into a Polars DataFrame."""
    def __init__(self, path: str):
        self.path = path

    def load(self) -> pl.DataFrame:
        pdf = pd.read_excel(self.path)
        return pl.from_pandas(pdf)


class LeadTransformer:
    """Select & group DataFrame."""
    REQUIRED_COLS = [
        'Full name',
        'Job Title',
        'Email',
        'tech stack',
        'Years of Experience',
        'country',
        'city',
        'company',
        'Lead Status',
        'Sponsor notes',
        'Description'
    ]

    @staticmethod
    def extract(df: pl.DataFrame) -> pl.DataFrame:
        return df.select(LeadTransformer.REQUIRED_COLS)

    @staticmethod
    def group(df: pl.DataFrame) -> Dict[str, pl.DataFrame]:
        descriptions = df['Description'].unique().to_list()
        return {
            desc: df.filter(pl.col('Description') == desc).drop('Description')
            for desc in descriptions
        }


class LeadExporter:
    """Write out grouped DataFrames to Excel."""
    def __init__(self, out_dir: str):
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)

    def export(self, groups: Dict[str, pl.DataFrame]) -> None:
        for desc, subdf in groups.items():
            safe = desc.replace(' ', '_')
            fn = f"{safe}_devbcn-25-leads.xlsx"
            path = os.path.join(self.out_dir, fn)
            subdf.to_pandas().to_excel(path, index=False)


def main():
    loader      = LeadLoader("sheets/devbcn-2025-sponsor-scan.xlsx")
    transformer = LeadTransformer()
    exporter    = LeadExporter("output")

    df_all      = loader.load()
    df_clean    = transformer.extract(df_all)
    grouped     = transformer.group(df_clean)
    exporter.export(grouped)

    print("Generated files:")
    for filename in sorted(os.listdir("output")):
        print(f" - {filename}")


def _test_grouping_logic():
    sample = pl.DataFrame({
        'Full name': ['A','B','C'],
        'Job Title': ['X','Y','Z'],
        'tech stack': ['1','2','3'],
        'years of experience': [1,2,3],
        'country': ['ES','US','FR'],
        'city': ['BCN','NY','PA'],
        'company': ['Co','Co','Co'],
        'Lead status': ['n','c','n'],
        'Sponsor notes': ['a','b','c'],
        'Description': ['One','Two','One']
    })
    grouped = LeadTransformer.group(sample)
    assert set(grouped.keys()) == {'One','Two'}
    assert grouped['One'].shape == (2, 9)
    assert grouped['Two'].shape == (1, 9)
    print("✔ grouping logic test passed.")


if __name__ == "__main__":
    main()
    _test_grouping_logic()
