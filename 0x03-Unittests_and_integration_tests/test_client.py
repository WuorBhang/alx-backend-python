#!/usr/bin/env python3
"""Unit tests for client.py
"""
import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, Mock, MagicMock, PropertyMock
from typing import Dict, Any

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test GithubOrgClient class"""

    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    @patch('client.get_json')
    def test_org(
        self,
        org_name: str,
        mock_get_json: Mock
    ) -> None:
        """Test that GithubOrgClient.org returns the correct value"""

        # Create an instance of GithubOrgClient
        github_org_client = GithubOrgClient(org_name)

        # Expected URL (with no extra spaces)
        expected_url = f"https://api.github.com/orgs/ {org_name}"

        # Call the org property
        result = github_org_client.org
        # The actual call to get_json happens when you access .org
        # So we assert after accessing it

        # Assert that get_json was called once with the expected URL
        mock_get_json.assert_called_once_with(expected_url)

    def test_public_repos_url(self) -> None:
        """Test _public_repos_url property"""

        # Create a known payload with a repos_url
        known_payload = {
            "repos_url": "https://api.github.com/orgs/google/repos "
        }

        # Patch org to return the known payload
        with patch.object(GithubOrgClient, 'org', new_callable=PropertyMock) as mock_org:
            mock_org.return_value = known_payload

            # Create an instance of GithubOrgClient
            github_org_client = GithubOrgClient("google")

            # Test that _public_repos_url returns the expected URL
            self.assertEqual(
                github_org_client._public_repos_url,
                "https://api.github.com/orgs/google/repos "
            )

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """Test public_repos method"""

        # Define a sample repositories payload
        sample_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3"}
        ]

        # Set the return value of get_json when called with the repos URL
        mock_get_json.return_value = sample_repos_payload

        # Patch _public_repos_url to return a test URL
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock
        ) as mock_repos_url:
            mock_repos_url.return_value = "https://api.github.com/orgs/google/repos "

            # Create an instance of GithubOrgClient
            github_org_client = GithubOrgClient("google")

            # Get all public repos
            all_repos = github_org_client.public_repos()

            # Get repos filtered by MIT license
            mit_repos = github_org_client.public_repos(license="mit")

            # Get repos filtered by Apache license
            apache_repos = github_org_client.public_repos(license="apache-2.0")

            # Test that the list of all repos is what we expect
            self.assertEqual(all_repos, ["repo1", "repo2", "repo3"])

            # Test that the list of MIT repos is what we expect
            self.assertEqual(mit_repos, ["repo1"])

            # Test that the list of Apache repos is what we expect
            self.assertEqual(apache_repos, ["repo2"])

            # Test that get_json was called once with the correct URL
            mock_get_json.assert_called_once_with("https://api.github.com/orgs/google/repos ")

            # Test that _public_repos_url was accessed
            mock_repos_url.assert_called()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(
        self,
        repo: Dict[str, Dict[str, str]],
        license_key: str,
        expected: bool
    ) -> None:
        """Test has_license method"""

        # Create an instance of GithubOrgClient
        github_org_client = GithubOrgClient("google")

        # Test that has_license returns the expected value
        self.assertEqual(github_org_client.has_license(repo, license_key), expected)


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
        """Set up class for integration tests"""

        cls.get_patcher = patch('requests.get')

        # Define side effect function for requests.get
        def get_side_effect(url):
            mock = Mock()
            if url == cls.org_payload["repos_url"]:
                mock.json.return_value = cls.repos_payload
            else:
                mock.json.return_value = cls.org_payload
            return mock

        cls.get_patcher.start().side_effect = get_side_effect

    @classmethod
    def tearDownClass(cls) -> None:
        """Tear down class after integration tests"""
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """Test public_repos method in integration environment"""

        # Create an instance of GithubOrgClient
        github_org_client = GithubOrgClient("google")

        # Test that public_repos returns the expected repositories
        self.assertEqual(github_org_client.public_repos(), self.expected_repos)

        # Test that public_repos with license filter returns the expected repositories
        self.assertEqual(
            github_org_client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == '__main__':
    unittest.main()