"""Test configuration."""

import os
import pytest

# Ensure we're using test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
