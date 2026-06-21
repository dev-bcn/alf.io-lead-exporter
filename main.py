#!/usr/bin/env python3
"""
leads_processor.py

Reads an Excel lead sheet, extracts key columns, groups by 'description'
(i.e., sponsor/booth), and writes one Excel file per sponsor:
   sponsor_devbcn-25-leads.xlsx
"""

import argparse
import logging
import os
from typing import Dict, Iterable

import pandas as pd
import polars as pl

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class LeadLoader:
    """load Excel into a Polars DataFrame."""

    def __init__(self, path: str):
        self.path = path

    def load(self) -> pl.DataFrame:
        try:
            pdf = pd.read_excel(self.path)
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Input file not found: {self.path}") from exc
        except ValueError as exc:
            raise ValueError(f"Unable to read Excel file '{self.path}': {exc}") from exc
        except Exception as exc:
            raise RuntimeError(f"Failed to load Excel file '{self.path}': {exc}") from exc
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

    COLUMN_ALIASES = {
        'Job Title': ['Job Title', 'jobTitle', 'job title'],
    }

    @staticmethod
    def _resolve_column(df_columns: Iterable[str], canonical_name: str) -> str:
        aliases = LeadTransformer.COLUMN_ALIASES.get(canonical_name, [canonical_name])
        for candidate in aliases:
            if candidate in df_columns:
                return candidate
        available = ', '.join(sorted(df_columns))
        expected = ', '.join(aliases)
        raise ValueError(
            f"Missing required column '{canonical_name}'. "
            f"Expected one of: {expected}. "
            f"Available columns: {available or 'none'}."
        )

    @staticmethod
    def extract(df: pl.DataFrame) -> pl.DataFrame:
        rename_map = {}
        for canonical in LeadTransformer.REQUIRED_COLS:
            resolved = LeadTransformer._resolve_column(df.columns, canonical)
            if resolved != canonical:
                rename_map[resolved] = canonical

        normalized = df.rename(rename_map) if rename_map else df
        return normalized.select(LeadTransformer.REQUIRED_COLS)

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
    parser = argparse.ArgumentParser(
        description="Reads a lead sheet and splits it into separate Excel files per sponsor."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="sheets/devbcn-2025-sponsor-scan.xlsx",
        help="Path to the input Excel lead sheet (e.g., 'sheets/devbcn-2025-sponsor-scan.xlsx')."
    )
    args = parser.parse_args()
    logging.info("Loading input file: %s", args.input_file)
    loader = LeadLoader(args.input_file)
    transformer = LeadTransformer()
    exporter = LeadExporter("output")

    try:
        df_all = loader.load()
        df_clean = transformer.extract(df_all)
        grouped = transformer.group(df_clean)
        exporter.export(grouped)
    except Exception as exc:
        logging.error(str(exc))
        raise SystemExit(1) from exc

    logging.info("Generated files:")
    for filename in sorted(os.listdir("output")):
        logging.info(f" - {filename}")


def _test_grouping_logic():
    sample = pl.DataFrame({
        'Full name': ['A', 'B', 'C'],
        'jobTitle': ['X', 'Y', 'Z'],
        'tech stack': ['1', '2', '3'],
        'years of experience': [1, 2, 3],
        'country': ['ES', 'US', 'FR'],
        'city': ['BCN', 'NY', 'PA'],
        'company': ['Co', 'Co', 'Co'],
        'Lead status': ['n', 'c', 'n'],
        'Sponsor notes': ['a', 'b', 'c'],
        'Description': ['One', 'Two', 'One']
    })
    grouped = LeadTransformer.group(LeadTransformer.extract(sample))
    assert set(grouped.keys()) == {'One', 'Two'}
    assert grouped['One'].shape == (2, 9)
    assert grouped['Two'].shape == (1, 9)
    logging.info("✔ grouping logic test passed.")


if __name__ == "__main__":
    main()
