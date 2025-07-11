#!/usr/bin/env python3
"""
run_tests.py

Discovers and runs all tests for the alfio-lead-exporter project.
Run with: uv run run_tests.py
"""

import sys
import unittest


def run_tests():
    """Discover and run all tests."""
    test_suite = unittest.defaultTestLoader.discover('tests')
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())