from pathlib import Path
import sys
import unittest
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))

import update_profile as profile  # pyright: ignore[reportMissingImports]


class RepositoryScopeTests(unittest.TestCase):
    def test_repository_query_fetches_forks_and_requests_fork_metadata(self):
        self.assertNotIn(
            "isFork: false",
            profile.REPOSITORIES_QUERY,
        )
        self.assertIn(
            "\n                isFork\n",
            profile.REPOSITORIES_QUERY,
        )

    def test_project_scope_excludes_forks_but_activity_scope_keeps_them(self):
        repositories = [
            {
                "name": "project",
                "isArchived": False,
                "isFork": False,
            },
            {
                "name": "forked-project",
                "isArchived": False,
                "isFork": True,
            },
            {
                "name": "archived-project",
                "isArchived": True,
                "isFork": False,
            },
            {
                "name": "Placeholder",
                "isArchived": False,
                "isFork": False,
            },
        ]

        project_names = [
            repository["name"]
            for repository in profile.project_repositories(
                repositories
            )
        ]
        activity_names = [
            repository["name"]
            for repository in profile.activity_repositories(
                repositories
            )
        ]
        snapshot_names = [
            repository["name"]
            for repository in profile.snapshot_repositories(
                repositories
            )
        ]

        self.assertEqual(
            project_names,
            ["project"],
        )
        self.assertEqual(
            activity_names,
            ["project", "forked-project"],
        )
        self.assertEqual(
            snapshot_names,
            [
                "project",
                "archived-project",
                "Placeholder",
            ],
        )

    def test_building_now_uses_activity_repository_scope(self):
        fork_repository = {
            "name": "forked-project",
            "pushedAt": "2026-09-04T16:32:43Z",
            "createdAt": "2026-08-31T11:17:05Z",
        }
        activity = {
            "commits_7d": 4,
            "commits_14d": 4,
            "commits_30d": 4,
            "active_days_14d": 2,
            "latest_commit_age": 0,
            "created_age": 4,
            "latest_release_age": None,
        }

        with (
            patch.object(
                profile,
                "activity_repositories",
                return_value=[fork_repository],
            ) as activity_scope,
            patch.object(
                profile,
                "repository_activity",
                return_value=activity,
            ),
            patch.object(
                profile,
                "qualifies_for_building_now",
                return_value=True,
            ),
            patch.object(
                profile,
                "building_activity_score",
                return_value=10.0,
            ),
        ):
            items = profile.collect_building_now([])

        activity_scope.assert_called_once_with([])
        self.assertEqual(len(items), 1)
        self.assertIs(
            items[0]["repository"],
            fork_repository,
        )

    def test_snapshot_totals_exclude_forks_in_both_renderer_modes(self):
        profile_data = {
            "repositories": [
                {
                    "name": "project",
                    "isArchived": False,
                    "isFork": False,
                    "stargazerCount": 3,
                    "releases": {
                        "totalCount": 2,
                    },
                },
                {
                    "name": "forked-project",
                    "isArchived": False,
                    "isFork": True,
                    "stargazerCount": 100,
                    "releases": {
                        "totalCount": 100,
                    },
                },
                {
                    "name": "archived-project",
                    "isArchived": True,
                    "isFork": False,
                    "stargazerCount": 5,
                    "releases": {
                        "totalCount": 4,
                    },
                },
            ],
        }

        full_svg = profile.render_snapshot_svg(
            profile_data,
            [],
        )

        snapshot_profile = profile.build_snapshot_profile(
            profile_data
        )
        hybrid = profile.render_snapshot_readme(
            snapshot_profile,
            [],
            "native_table_hybrid",
        )

        self.assertIn(
            'text-anchor="middle">8</text>',
            full_svg,
        )
        self.assertIn(
            'text-anchor="middle">6</text>',
            full_svg,
        )
        self.assertNotIn(
            'text-anchor="middle">103</text>',
            full_svg,
        )
        self.assertNotIn(
            'text-anchor="middle">102</text>',
            full_svg,
        )

        self.assertIn("<h2>8</h2>", hybrid)
        self.assertIn("<h2>6</h2>", hybrid)
        self.assertNotIn("<h2>103</h2>", hybrid)
        self.assertNotIn("<h2>102</h2>", hybrid)

    def test_recent_releases_exclude_fork_releases(self):
        repositories = [
            {
                "name": "project",
                "url": "https://github.com/Yusseter/project",
                "isArchived": False,
                "isFork": False,
                "releases": {
                    "nodes": [
                        {
                            "name": "Project release",
                            "tagName": "v1.0.0",
                            "url": (
                                "https://github.com/Yusseter/project/"
                                "releases/tag/v1.0.0"
                            ),
                            "publishedAt": "2026-09-01T12:00:00Z",
                            "isDraft": False,
                            "isPrerelease": False,
                            "isLatest": True,
                        }
                    ]
                },
            },
            {
                "name": "forked-project",
                "url": (
                    "https://github.com/Yusseter/"
                    "forked-project"
                ),
                "isArchived": False,
                "isFork": True,
                "releases": {
                    "nodes": [
                        {
                            "name": "Fork release",
                            "tagName": "fork-v2.0.0",
                            "url": (
                                "https://github.com/Yusseter/"
                                "forked-project/releases/tag/"
                                "fork-v2.0.0"
                            ),
                            "publishedAt": "2026-09-02T12:00:00Z",
                            "isDraft": False,
                            "isPrerelease": False,
                            "isLatest": True,
                        }
                    ]
                },
            },
        ]

        releases = profile.collect_recent_releases(
            repositories
        )

        self.assertEqual(
            [release["tagName"] for release in releases],
            ["v1.0.0"],
        )


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
    def test_owned_fork_commits_require_matching_author(self):
        repository = {
            "name": "project",
            "url": "https://github.com/Yusseter/project",
            "isFork": True,
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
