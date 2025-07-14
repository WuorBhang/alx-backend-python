# Unittests and Integration Tests

This project focuses on writing unit and integration tests for a GitHub organization client module using Python's `unittest` framework. The goal is to test various components including nested dictionary access, HTTP JSON retrieval, memoization, and GitHub organization repository handling.

## 📁 Project Structure

alx-backend-python/
└── 0x03-Unittests_and_integration_tests/
├── client.py # GithubOrgClient class
├── utils.py # Utility functions (access_nested_map, get_json, memoize)
├── fixtures.py # Test fixtures for mocking
├── test_utils.py # Unit tests for utils.py
└── test_client.py # Unit and integration tests for client.py

## 🧪 Included Tests

- **Unit Tests**
  - `test_access_nested_map`: Tests accessing values in nested dictionaries.
  - `test_access_nested_map_exception`: Tests that `KeyError` is raised for invalid paths.
  - `test_get_json`: Mocks HTTP requests and verifies correct JSON return values.
  - `test_memoize`: Ensures methods decorated with `@memoize` are only called once.
  - `test_org`: Verifies the `GithubOrgClient.org` property makes correct API calls.
  - `test_public_repos_url`: Tests the internal `_public_repos_url` property.
  - `test_public_repos`: Validates filtering of public repos by license.
  - `test_has_license`: Checks if a repo has a specific license.
  
- **Integration Tests**
  - `test_public_repos_integration`: Uses real fixtures to test `public_repos()` end-to-end.

## 🛠️ Requirements

- Python 3.7 or higher
- Libraries:
  - `unittest`
  - `parameterized`
  - `requests`
  - `mock` (for patching)

Install dependencies:

```bash
pip install requests parameterized
