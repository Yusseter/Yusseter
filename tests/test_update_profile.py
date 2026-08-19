from pathlib import Path
import sys
import unittest
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))

import update_profile as profile  # pyright: ignore[reportMissingImports]


class RelativeTimeTests(unittest.TestCase):
    def test_render_relative_time_uses_native_element(self):
        rendered = profile.render_relative_time(
            "2026-08-18T22:16:58Z"
        )

        self.assertEqual(
            rendered,
            (
                '<relative-time '
                'datetime="2026-08-18T22:16:58Z">'
                'Aug 18, 2026'
                '</relative-time>'
            ),
        )


class RecentReleaseTests(unittest.TestCase):
    def test_release_uses_relative_time_without_old_wording(self):
        rendered = profile.render_recent_releases(
            [
                {
                    "name": "Test release",
                    "url": (
                        "https://github.com/Yusseter/test/"
                        "releases/tag/v1.0.0"
                    ),
                    "repositoryUrl": (
                        "https://github.com/Yusseter/test"
                    ),
                    "tagName": "v1.0.0",
                    "publishedAt": "2026-08-07T09:23:12Z",
                    "isLatest": True,
                    "isPrerelease": False,
                }
            ]
        )

        self.assertIn(
            (
                'Released <relative-time '
                'datetime="2026-08-07T09:23:12Z">'
                'Aug 7, 2026'
                '</relative-time>'
            ),
            rendered,
        )
        self.assertNotIn("Released this", rendered)


class RecentCommitTests(unittest.TestCase):
    def test_owned_commits_require_matching_author(self):
        repository = {
            "name": "project",
            "url": "https://github.com/Yusseter/project",
            "defaultBranchRef": {
                "target": {
                    "history": {
                        "nodes": [
                            {
                                "oid": "owned111",
                                "url": (
                                    "https://github.com/Yusseter/"
                                    "project/commit/owned111"
                                ),
                                "messageHeadline": "Owned commit",
                                "messageBody": "",
                                "authoredDate": (
                                    "2026-08-19T10:00:00Z"
                                ),
                                "committedDate": (
                                    "2026-08-19T10:01:00Z"
                                ),
                                "author": {
                                    "user": {
                                        "login": "Yusseter"
                                    }
                                },
                                "committer": {
                                    "user": {
                                        "login": "someone-else"
                                    }
                                },
                            },
                            {
                                "oid": "skip222",
                                "url": (
                                    "https://github.com/Yusseter/"
                                    "project/commit/skip222"
                                ),
                                "messageHeadline": "Other author",
                                "messageBody": "",
                                "authoredDate": (
                                    "2026-08-19T11:00:00Z"
                                ),
                                "committedDate": (
                                    "2026-08-19T11:01:00Z"
                                ),
                                "author": {
                                    "user": {
                                        "login": "someone-else"
                                    }
                                },
                                "committer": {
                                    "user": {
                                        "login": "Yusseter"
                                    }
                                },
                            },
                        ]
                    }
                }
            },
        }

        with patch.object(profile, "USERNAME", "Yusseter"):
            commits = profile.collect_owned_recent_commits(
                [repository]
            )

        self.assertEqual(
            [commit["oid"] for commit in commits],
            ["owned111"],
        )
        self.assertEqual(
            commits[0]["committedDate"],
            "2026-08-19T10:00:00Z",
        )

    def test_search_keeps_external_owner_in_repository_name(self):
        payload = {
            "incomplete_results": False,
            "items": [
                {
                    "sha": "external111",
                    "html_url": (
                        "https://github.com/other/project/"
                        "commit/external111"
                    ),
                    "author": {
                        "login": "Yusseter"
                    },
                    "repository": {
                        "full_name": "other/project",
                        "name": "project",
                        "html_url": (
                            "https://github.com/other/project"
                        ),
                        "private": False,
                        "owner": {
                            "login": "other"
                        },
                    },
                    "commit": {
                        "message": "External commit\n\nDetails",
                        "author": {
                            "date": "2026-08-19T12:00:00Z"
                        },
                        "committer": {
                            "date": "2026-08-19T12:00:01Z"
                        },
                    },
                },
                {
                    "sha": "skip222",
                    "html_url": (
                        "https://github.com/other/project/"
                        "commit/skip222"
                    ),
                    "author": {
                        "login": "someone-else"
                    },
                    "repository": {
                        "full_name": "other/project",
                        "name": "project",
                        "html_url": (
                            "https://github.com/other/project"
                        ),
                        "private": False,
                        "owner": {
                            "login": "other"
                        },
                    },
                    "commit": {
                        "message": "Wrong author",
                        "author": {
                            "date": "2026-08-19T13:00:00Z"
                        },
                        "committer": {
                            "date": "2026-08-19T13:00:01Z"
                        },
                    },
                },
            ],
        }

        with (
            patch.object(profile, "USERNAME", "Yusseter"),
            patch.object(
                profile,
                "rest_json_request",
                return_value=payload,
            ),
        ):
            commits = profile.fetch_searched_recent_commits()

        self.assertEqual(len(commits), 1)
        self.assertEqual(
            commits[0]["repositoryName"],
            "other/project",
        )
        self.assertEqual(
            commits[0]["messageBody"],
            "Details",
        )

    def test_graphql_commit_overrides_duplicate_search_commit(self):
        searched = [
            {
                "repositoryName": "Yusseter",
                "repositoryUrl": (
                    "https://github.com/Yusseter/Yusseter"
                ),
                "oid": "duplicate111",
                "url": (
                    "https://github.com/Yusseter/Yusseter/"
                    "commit/duplicate111-search"
                ),
                "messageHeadline": "Search copy",
                "messageBody": "",
                "committedDate": "2026-08-19T12:00:00Z",
            },
            {
                "repositoryName": "other/project",
                "repositoryUrl": (
                    "https://github.com/other/project"
                ),
                "oid": "external222",
                "url": (
                    "https://github.com/other/project/"
                    "commit/external222"
                ),
                "messageHeadline": "External commit",
                "messageBody": "",
                "committedDate": "2026-08-19T11:00:00Z",
            },
        ]

        owned = [
            {
                "repositoryName": "Yusseter",
                "repositoryUrl": (
                    "https://github.com/Yusseter/Yusseter"
                ),
                "oid": "duplicate111",
                "url": (
                    "https://github.com/Yusseter/Yusseter/"
                    "commit/duplicate111-fresh"
                ),
                "messageHeadline": "Fresh GraphQL copy",
                "messageBody": "",
                "committedDate": "2026-08-19T12:05:00Z",
            }
        ]

        with (
            patch.object(
                profile,
                "fetch_searched_recent_commits",
                return_value=searched,
            ),
            patch.object(
                profile,
                "collect_owned_recent_commits",
                return_value=owned,
            ),
        ):
            commits = profile.collect_recent_commits([])

        self.assertEqual(
            [commit["oid"] for commit in commits],
            ["duplicate111", "external222"],
        )
        self.assertEqual(
            commits[0]["messageHeadline"],
            "Fresh GraphQL copy",
        )
        self.assertTrue(
            commits[0]["url"].endswith("duplicate111-fresh")
        )

    def test_recent_commit_feed_keeps_latest_five(self):
        searched = []

        for hour in range(1, 7):
            searched.append(
                {
                    "repositoryName": "project",
                    "repositoryUrl": (
                        "https://github.com/Yusseter/project"
                    ),
                    "oid": f"commit{hour}",
                    "url": (
                        "https://github.com/Yusseter/project/"
                        f"commit/commit{hour}"
                    ),
                    "messageHeadline": f"Commit {hour}",
                    "messageBody": "",
                    "committedDate": (
                        f"2026-08-19T{hour:02d}:00:00Z"
                    ),
                }
            )

        with (
            patch.object(
                profile,
                "fetch_searched_recent_commits",
                return_value=searched,
            ),
            patch.object(
                profile,
                "collect_owned_recent_commits",
                return_value=[],
            ),
        ):
            commits = profile.collect_recent_commits([])

        self.assertEqual(
            [commit["oid"] for commit in commits],
            [
                "commit6",
                "commit5",
                "commit4",
                "commit3",
                "commit2",
            ],
        )


if __name__ == "__main__":
    unittest.main()
