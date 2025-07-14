#!/usr/bin/env python3
"""Unit tests for client.py
"""

import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, Mock, PropertyMock
from typing import Dict

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test GithubOrgClient class"""

    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, mock_get_json: Mock) -> None:
        """Test that GithubOrgClient.org returns the correct value"""
        client = GithubOrgClient(org_name)
        expected_url = f"https://api.github.com/orgs/{org_name}"
        client.org
        mock_get_json.assert_called_once_with(expected_url)

    def test_public_repos_url(self) -> None:
        """Test _public_repos_url property"""
        expected = "https://api.github.com/orgs/google/repos"
        with patch.object(
            GithubOrgClient,
            'org',
            new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = {"repos_url": expected}
            client = GithubOrgClient("google")
            self.assertEqual(client._public_repos_url, expected)

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """Test public_repos method"""
        mock_get_json.return_value = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3"}
        ]
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = "https://api.github.com/orgs/google/repos"
            client = GithubOrgClient("google")
            self.assertEqual(
                client.public_repos(), ["repo1", "repo2", "repo3"]
            )
            self.assertEqual(client.public_repos("mit"), ["repo1"])
            self.assertEqual(client.public_repos("apache-2.0"), ["repo2"])
            mock_get_json.assert_called_once_with(
                "https://api.github.com/orgs/google/repos"
            )
            mock_url.assert_called()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license method"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.has_license(repo, license_key), expected
        )


@parameterized_class([
    {
        "org_payload": test_case[0],
        "repos_payload": test_case[1],
        "expected_repos": test_case[2],
        "apache2_repos": test_case[3]
    } for test_case in TEST_PAYLOAD
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test for GithubOrgClient.public_repos"""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up mock for requests.get"""
        cls.get_patcher = patch('requests.get')

        def side_effect(url):
            mock = Mock()
            if url == cls.org_payload["repos_url"]:
                mock.json.return_value = cls.repos_payload
            else:
                mock.json.return_value = cls.org_payload
            return mock

        cls.get_patcher.start().side_effect = side_effect

    @classmethod
    def tearDownClass(cls) -> None:
        """Stop patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """Test integration: public_repos returns correct list"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == '__main__':
    unittest.main()
