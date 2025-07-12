# Alf.io Lead Exporter

[![Python build](https://github.com/dev-bcn/alf.io-lead-exporter/actions/workflows/python-package.yml/badge.svg)](https://github.com/dev-bcn/alf.io-lead-exporter/actions/workflows/python-package.yml)

A Python script that processes Excel lead sheets from events, extracts key columns, groups by sponsor/booth, and generates individual Excel files for each sponsor.

## Usage

Run the script with [UV](https://github.com/astral-sh/uv):

### Install uv:

```shell
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```
### Run the app
```bash
uv run main.py
```

This will:
1. Read the lead sheet from `sheets/devbcn-2025-sponsor-scan.xlsx` (you can optionally pass another file path)
2. Extract and process the data
3. Generate one Excel file per sponsor in the `output` directory

## Testing

The project includes comprehensive tests to verify all functionality. The tests are organized as follows:

### Unit Tests

- **LeadTransformer Tests**: Tests for the data transformation logic, including column extraction and grouping by description.
- **LeadLoader Tests**: Tests for loading Excel files into [Polars](https://github.com/pola-rs/polars) DataFrames.
- **LeadExporter Tests**: Tests for exporting grouped data to Excel files.

### Integration Tests

- **End-to-End Test**: Tests the complete workflow from loading the input file to generating the output files.

### Running Tests

Run all tests with:

```bash
uv run run_tests.py
```

Or run individual test files with:

```bash
uv run -m unittest tests/test_lead_transformer.py
uv run -m unittest tests/test_lead_loader.py
uv run -m unittest tests/test_lead_exporter.py
uv run -m unittest tests/test_integration.py
```

## Test Coverage

The tests cover the following use cases:

1. **Data Loading**:
   - Loading valid Excel files
   - Handling non-existent files

2. **Data Transformation**:
   - Extracting required columns
   - Grouping data by description
   - Handling edge cases (empty data, missing columns)

3. **Data Export**:
   - Creating Excel files for each group
   - Handling empty groups
   - Verifying file content

4. **End-to-End Workflow**:
   - Complete process from input to output
   - Verifying output file structure and content

## Dependencies

- **polars**: For data processing
- **pandas**: For Excel file handling
- **openpyxl**: For Excel file support
- **pyarrow**: For data conversion
