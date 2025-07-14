#!/usr/bin/env python3
"""Unit tests for utils.py
"""

import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock
from typing import Dict, Any, Tuple

from client import GithubOrgClient
from utils import access_nested_map, get_json, memoize
from fixtures import TEST_PAYLOAD


class TestAccessNestedMap(unittest.TestCase):
    """Test access_nested_map function"""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2)
    ])
    def test_access_nested_map(
        self,
        nested_map: Dict[str, Any],
        path: Tuple[str, ...],
        expected: Any
    ) -> None:
        """Test that access_nested_map returns the expected result"""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b"))
    ])
    def test_access_nested_map_exception(
        self,
        nested_map: Dict[str, Any],
        path: Tuple[str, ...]
    ) -> None:
        """Test that access_nested_map raises KeyError for invalid paths"""
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)

        exception_msg = str(cm.exception)
        if len(path) > 0:
            self.assertIn(path[-1], exception_msg)


class TestGetJson(unittest.TestCase):
    """Test get_json function"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False})
    ])
    def test_get_json(
        self,
        test_url: str,
        test_payload: Dict[str, bool]
    ) -> None:
        """Test that get_json returns the expected result"""
        mock_response = Mock()
        mock_response.json.return_value = test_payload

        with patch('requests.get') as mock_get:
            mock_get.return_value = mock_response
            result = get_json(test_url)
            mock_get.assert_called_once_with(test_url)
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test memoize decorator"""

    def test_memoize(self) -> None:
        """Test that a_property is computed only once"""

        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        test_instance = TestClass()

        with patch.object(
            TestClass, 'a_method', return_value=42
        ) as mock_a_method:
            result1 = test_instance.a_property
            result2 = test_instance.a_property
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            mock_a_method.assert_called_once()


if __name__ == '__main__':
    unittest.main()
