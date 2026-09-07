from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))

import update_profile as profile  # pyright: ignore[reportMissingImports]


class RepositoryScopeTests(unittest.TestCase):
    @staticmethod
    def repository(
        name,
        *,
        fork=False,
        private=False,
        archived=False,
        stars=0,
        release_count=0,
        languages=None,
    ):
        edges = [
            {
                "size": size,
                "node": {
                    "name": language,
                    "color": color,
                },
            }
            for language, size, color in (languages or [])
        ]

        return {
            "name": name,
            "nameWithOwner": f"Yusseter/{name}",
            "url": f"https://github.com/Yusseter/{name}",
            "description": "",
            "isArchived": archived,
            "isFork": fork,
            "isPrivate": private,
            "stargazerCount": stars,
            "pushedAt": "2026-09-04T16:32:43Z",
            "createdAt": "2026-08-01T12:00:00Z",
            "defaultBranchRef": None,
            "languages": {
                "edges": edges,
            },
            "releases": {
                "totalCount": release_count,
                "nodes": [],
            },
        }

    def test_repository_query_fetches_all_owned_visibility_metadata(self):
        self.assertNotIn(
            "privacy: PUBLIC",
            profile.REPOSITORIES_QUERY,
        )

        for field in (
            "nameWithOwner",
            "isFork",
            "isPrivate",
        ):
            self.assertIn(
                f"\n                {field}\n",
                profile.REPOSITORIES_QUERY,
            )

    def test_profile_config_loads_contribution_forks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = (
                Path(temp_dir)
                / "profile_renderer.json"
            )
            config_path.write_text(
                (
                    '{\n'
                    '  "snapshot_mode": "full_svg",\n'
                    '  "contribution_forks": [\n'
                    '    "Yusseter/example",\n'
                    '    "yusseter/EXAMPLE"\n'
                    '  ]\n'
                    '}\n'
                ),
                encoding="utf-8",
            )

            config = profile.load_profile_config(
                temp_dir
            )

        self.assertEqual(
            config["snapshot_mode"],
            "full_svg",
        )
        self.assertEqual(
            config["contribution_forks"],
            ["Yusseter/example"],
        )

    def test_repository_scopes_match_profile_policy(self):
        repositories = [
            self.repository("project"),
            self.repository("archived-project", archived=True),
            self.repository("private-project", private=True),
            self.repository("own-fork", fork=True),
            self.repository("contribution-fork", fork=True),
            self.repository("Yusseter"),
            self.repository("Placeholder"),
        ]

        snapshot_names = [
            repo["name"]
            for repo in profile.snapshot_repositories(
                repositories,
                ["Yusseter/contribution-fork"],
            )
        ]

        activity_names = [
            repo["name"]
            for repo in profile.activity_repositories(
                repositories
            )
        ]

        release_names = [
            repo["name"]
            for repo in profile.release_repositories(
                repositories
            )
        ]

        self.assertEqual(
            snapshot_names,
            [
                "project",
                "archived-project",
                "private-project",
                "own-fork",
                "Yusseter",
                "Placeholder",
            ],
        )

        self.assertEqual(
            activity_names,
            [
                "project",
                "own-fork",
                "contribution-fork",
                "Yusseter",
                "Placeholder",
            ],
        )

        self.assertEqual(
            release_names,
            [
                "project",
                "Yusseter",
                "Placeholder",
            ],
        )

    def test_snapshot_totals_and_languages_share_the_same_scope(self):
        repositories = [
            self.repository(
                "project",
                stars=3,
                release_count=2,
                languages=[
                    ("Python", 30, "#3572A5"),
                ],
            ),
            self.repository(
                "archived-project",
                archived=True,
                stars=5,
                release_count=4,
                languages=[
                    ("PowerShell", 20, "#012456"),
                ],
            ),
            self.repository(
                "private-project",
                private=True,
                stars=7,
                release_count=6,
                languages=[
                    ("C++", 10, "#f34b7d"),
                ],
            ),
            self.repository(
                "own-fork",
                fork=True,
                stars=11,
                release_count=8,
                languages=[
                    ("Java", 40, "#b07219"),
                ],
            ),
            self.repository(
                "contribution-fork",
                fork=True,
                stars=100,
                release_count=100,
                languages=[
                    ("Rust", 999, "#dea584"),
                ],
            ),
            self.repository(
                "Yusseter",
                stars=13,
                release_count=10,
                languages=[
                    ("Python", 10, "#3572A5"),
                ],
            ),
            self.repository(
                "Placeholder",
                stars=17,
                release_count=12,
                languages=[
                    ("CSS", 5, "#663399"),
                ],
            ),
        ]

        snapshot_profile = profile.build_snapshot_profile(
            {
                "repositories": repositories,
            },
            ["Yusseter/contribution-fork"],
        )

        languages = profile.aggregate_languages(
            snapshot_profile["repositories"]
        )

        language_bytes = {
            language["name"]: language["bytes"]
            for language in languages
        }

        self.assertEqual(
            language_bytes,
            {
                "Python": 40,
                "Java": 40,
                "PowerShell": 20,
                "C++": 10,
                "CSS": 5,
            },
        )

        full_svg = profile.render_snapshot_svg(
            snapshot_profile,
            languages,
        )

        hybrid = profile.render_snapshot_readme(
            snapshot_profile,
            languages,
            "native_table_hybrid",
        )

        self.assertIn(
            'text-anchor="middle">56</text>',
            full_svg,
        )
        self.assertIn(
            'text-anchor="middle">42</text>',
            full_svg,
        )
        self.assertIn("<h2>56</h2>", hybrid)
        self.assertIn("<h2>42</h2>", hybrid)

        self.assertNotIn("Rust", full_svg)
        self.assertNotIn("Rust", hybrid)

    def test_building_now_uses_public_activity_scope(self):
        fork_repository = self.repository(
            "forked-project",
            fork=True,
        )

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

    def test_recent_releases_exclude_private_and_fork_repositories(self):
        project = self.repository("project")
        fork = self.repository(
            "forked-project",
            fork=True,
        )
        private = self.repository(
            "private-project",
            private=True,
        )

        def release(name, published_at):
            return {
                "name": name,
                "tagName": "v1.0.0",
                "url": (
                    "https://github.com/Yusseter/"
                    f"{name}/releases/tag/v1.0.0"
                ),
                "publishedAt": published_at,
                "isDraft": False,
                "isPrerelease": False,
                "isLatest": True,
            }

        project["releases"]["nodes"] = [
            release("project", "2026-09-01T12:00:00Z")
        ]
        fork["releases"]["nodes"] = [
            release("forked-project", "2026-09-02T12:00:00Z")
        ]
        private["releases"]["nodes"] = [
            release("private-project", "2026-09-03T12:00:00Z")
        ]

        releases = profile.collect_recent_releases(
            [project, fork, private]
        )

        self.assertEqual(
            [release["name"] for release in releases],
            ["project"],
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

    def test_owned_private_commits_are_not_published(self):
        repository = {
            "name": "private-project",
            "url": (
                "https://github.com/Yusseter/"
                "private-project"
            ),
            "isPrivate": True,
            "defaultBranchRef": {
                "target": {
                    "history": {
                        "nodes": [
                            {
                                "oid": "private111",
                                "url": (
                                    "https://github.com/Yusseter/"
                                    "private-project/commit/"
                                    "private111"
                                ),
                                "messageHeadline": "Private commit",
                                "messageBody": "",
                                "authoredDate": (
                                    "2026-09-04T12:00:00Z"
                                ),
                                "committedDate": (
                                    "2026-09-04T12:00:01Z"
                                ),
                                "author": {
                                    "user": {
                                        "login": "Yusseter"
                                    }
                                },
                            }
                        ]
                    }
                }
            },
        }

        with patch.object(profile, "USERNAME", "Yusseter"):
            commits = profile.collect_owned_recent_commits(
                [repository]
            )

        self.assertEqual(commits, [])

    def test_search_keeps_placeholder_repository(self):
        payload = {
            "incomplete_results": False,
            "items": [
                {
                    "sha": "placeholder111",
                    "html_url": (
                        "https://github.com/Yusseter/"
                        "Placeholder/commit/placeholder111"
                    ),
                    "author": {
                        "login": "Yusseter"
                    },
                    "repository": {
                        "full_name": "Yusseter/Placeholder",
                        "name": "Placeholder",
                        "html_url": (
                            "https://github.com/Yusseter/"
                            "Placeholder"
                        ),
                        "private": False,
                        "owner": {
                            "login": "Yusseter"
                        },
                    },
                    "commit": {
                        "message": "Placeholder commit",
                        "author": {
                            "date": "2026-09-04T13:00:00Z"
                        },
                        "committer": {
                            "date": "2026-09-04T13:00:01Z"
                        },
                    },
                }
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
            "Placeholder",
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
