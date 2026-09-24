from pathlib import Path
import io
import sys
import tempfile
import unittest
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))

import update_profile as profile  # pyright: ignore[reportMissingImports]



class GitHubRequestTests(unittest.TestCase):
    def test_graphql_retries_transient_502(self):
        error = profile.urllib.error.HTTPError(
            profile.GRAPHQL_URL,
            502,
            "Bad Gateway",
            {},
            io.BytesIO(b"bad gateway"),
        )

        success = io.BytesIO(
            b'{"data":{"viewer":"ok"}}'
        )

        with (
            patch.object(
                profile,
                "GITHUB_TOKEN",
                "test-token",
            ),
            patch.object(
                profile.urllib.request,
                "urlopen",
                side_effect=[
                    error,
                    success,
                ],
            ) as urlopen_mock,
            patch.object(
                profile.time,
                "sleep",
            ) as sleep_mock,
            patch("builtins.print"),
        ):
            data = profile.graphql_request(
                "query Test { viewer { login } }",
                {},
            )

        self.assertEqual(
            data,
            {"viewer": "ok"},
        )
        self.assertEqual(
            urlopen_mock.call_count,
            2,
        )
        sleep_mock.assert_called_once_with(1)

    def test_rest_retries_transient_502(self):
        error = profile.urllib.error.HTTPError(
            "https://api.github.com/test",
            502,
            "Bad Gateway",
            {},
            io.BytesIO(b"bad gateway"),
        )

        success = io.BytesIO(
            b'{"ok":true}'
        )

        with (
            patch.object(
                profile,
                "GITHUB_TOKEN",
                "test-token",
            ),
            patch.object(
                profile.urllib.request,
                "urlopen",
                side_effect=[
                    error,
                    success,
                ],
            ) as urlopen_mock,
            patch.object(
                profile.time,
                "sleep",
            ) as sleep_mock,
            patch("builtins.print"),
        ):
            data = profile.rest_json_request(
                "https://api.github.com/test"
            )

        self.assertEqual(
            data,
            {"ok": True},
        )
        self.assertEqual(
            urlopen_mock.call_count,
            2,
        )
        sleep_mock.assert_called_once_with(1)


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
                / "profile_config.json"
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

        self.assertIn(
            "./assets/profile/generated/snapshot/"
            "native_table_hybrid/dot-1.svg",
            hybrid,
        )
        self.assertNotIn(
            "./assets/profile/native_table_hybrid/",
            hybrid,
        )

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

    def test_building_activity_ignores_bot_commit_for_updated_time(self):
        repository = self.repository("Yusseter")

        repository["defaultBranchRef"] = {
            "target": {
                "history": {
                    "nodes": [
                        {
                            "committedDate": (
                                "2026-09-10T10:00:00Z"
                            ),
                            "author": {
                                "user": {
                                    "login": (
                                        "github-actions[bot]"
                                    )
                                }
                            },
                            "committer": {
                                "user": {
                                    "login": (
                                        "github-actions[bot]"
                                    )
                                }
                            },
                        },
                        {
                            "committedDate": (
                                "2026-09-09T20:00:00Z"
                            ),
                            "author": {
                                "user": {
                                    "login": "Yusseter"
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
        }

        with patch.object(
            profile,
            "USERNAME",
            "Yusseter",
        ):
            activity = profile.repository_activity(
                repository,
                profile.parse_github_date(
                    "2026-09-10T12:00:00Z"
                ),
            )

        self.assertEqual(
            activity["latest_commit_at"],
            "2026-09-09T20:00:00Z",
        )
        self.assertEqual(
            activity["commits_7d"],
            1,
        )

    def test_building_now_selects_by_score_then_orders_by_latest_commit(self):
        repositories = [
            self.repository("a"),
            self.repository("b"),
            self.repository("c"),
            self.repository("d"),
            self.repository("e"),
        ]

        activity_by_name = {
            "a": {
                "latest_commit_at": (
                    "2026-09-01T12:00:00Z"
                ),
                "_score": 100,
            },
            "b": {
                "latest_commit_at": (
                    "2026-09-05T12:00:00Z"
                ),
                "_score": 90,
            },
            "c": {
                "latest_commit_at": (
                    "2026-09-03T12:00:00Z"
                ),
                "_score": 80,
            },
            "d": {
                "latest_commit_at": (
                    "2026-09-04T12:00:00Z"
                ),
                "_score": 70,
            },
            "e": {
                "latest_commit_at": (
                    "2026-09-06T12:00:00Z"
                ),
                "_score": 60,
            },
        }

        with (
            patch.object(
                profile,
                "activity_repositories",
                return_value=repositories,
            ),
            patch.object(
                profile,
                "repository_activity",
                side_effect=lambda repo, now: (
                    activity_by_name[repo["name"]]
                ),
            ),
            patch.object(
                profile,
                "qualifies_for_building_now",
                return_value=True,
            ),
            patch.object(
                profile,
                "building_activity_score",
                side_effect=lambda activity: (
                    activity["_score"]
                ),
            ),
        ):
            items = profile.collect_building_now([])

        self.assertEqual(
            [
                item["repository"]["name"]
                for item in items
            ],
            ["b", "d", "c", "a"],
        )

    def test_building_renderer_uses_user_activity_time_not_branch_head(self):
        repository = self.repository(
            "Yusseter",
            languages=[],
        )

        repository["description"] = (
            "Yusseter's Profile repository."
        )
        repository["defaultBranchRef"] = {
            "target": {
                "committedDate": (
                    "2026-09-10T10:00:00Z"
                )
            }
        }

        rendered = profile.render_building_now(
            [
                {
                    "repository": repository,
                    "activity": {
                        "latest_commit_at": (
                            "2026-09-09T20:00:00Z"
                        )
                    },
                    "score": 10.0,
                }
            ]
        )

        self.assertIn(
            'datetime="2026-09-09T20:00:00Z"',
            rendered,
        )
        self.assertNotIn(
            "2026-09-10T10:00:00Z",
            rendered,
        )


class SetiLanguageIconTests(unittest.TestCase):
    def test_light_color_matches_vscode_seti_transform(self):
        self.assertEqual(
            profile.darken_seti_color("#CC3E44"),
            "#b8383d",
        )
        self.assertEqual(
            profile.darken_seti_color("#356EA1"),
            "#306391",
        )

    def test_language_asset_paths_use_variant_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            language_dir = Path(temp_dir)

            with patch.object(
                profile,
                "LANGUAGE_ASSETS_DIR",
                language_dir,
            ):
                self.assertEqual(
                    (
                        profile
                        .seti_language_icon_asset_path(
                            "C++"
                        )
                        .relative_to(language_dir)
                        .as_posix()
                    ),
                    "dark/desktop/cpp.svg",
                )

                self.assertEqual(
                    (
                        profile
                        .seti_language_icon_asset_path(
                            "C++",
                            mobile=True,
                            light=True,
                        )
                        .relative_to(language_dir)
                        .as_posix()
                    ),
                    "light/mobile/cpp.svg",
                )

    def test_writer_creates_dark_and_light_desktop_mobile_assets(self):
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'viewBox="0 0 32 32">'
            '<path fill="#CC3E44" d="M0 0h1v1z"/>'
            '</svg>'
        )

        class Response:
            def __enter__(self):
                return self

            def __exit__(
                self,
                exc_type,
                exc_value,
                traceback,
            ):
                return False

            def read(self):
                return svg.encode("utf-8")

        item = {
            "repository": {
                "languages": {
                    "edges": [
                        {
                            "node": {
                                "name": "Java"
                            }
                        }
                    ]
                }
            }
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            language_dir = Path(temp_dir)

            with (
                patch.object(
                    profile,
                    "LANGUAGE_ASSETS_DIR",
                    language_dir,
                ),
                patch.object(
                    profile,
                    "seti_language_icon_url",
                    return_value=(
                        "https://example.invalid/java.svg"
                    ),
                ),
                patch.object(
                    profile.urllib.request,
                    "urlopen",
                    return_value=Response(),
                ),
            ):
                profile.write_seti_language_assets(
                    [item]
                )

                dark_desktop = (
                    profile
                    .seti_language_icon_asset_path(
                        "Java"
                    )
                )
                light_desktop = (
                    profile
                    .seti_language_icon_asset_path(
                        "Java",
                        light=True,
                    )
                )

            expected_paths = {
                "dark/desktop/java.svg",
                "dark/mobile/java.svg",
                "light/desktop/java.svg",
                "light/mobile/java.svg",
            }

            self.assertEqual(
                {
                    path
                    .relative_to(language_dir)
                    .as_posix()
                    for path in language_dir.rglob(
                        "*.svg"
                    )
                },
                expected_paths,
            )

            self.assertIn(
                "#CC3E44",
                dark_desktop.read_text(
                    encoding="utf-8"
                ),
            )

            self.assertIn(
                "#b8383d",
                light_desktop.read_text(
                    encoding="utf-8"
                ),
            )

    def test_metadata_uses_theme_and_viewport_sources(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            language_dir = Path(temp_dir)

            with patch.object(
                profile,
                "LANGUAGE_ASSETS_DIR",
                language_dir,
            ):
                for mobile, light in (
                    (False, False),
                    (True, False),
                    (False, True),
                    (True, True),
                ):
                    path = (
                        profile
                        .seti_language_icon_asset_path(
                            "C++",
                            mobile=mobile,
                            light=light,
                        )
                    )

                    path.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    path.write_text(
                        "<svg/>",
                        encoding="utf-8",
                    )

                rendered = (
                    profile.render_language_metadata(
                        "C++"
                    )
                )

        self.assertIn(
            (
                'media="(prefers-color-scheme: light) '
                'and (max-width: 600px)" '
                'srcset="./assets/profile/generated/'
                'languages/light/mobile/cpp.svg"'
            ),
            rendered,
        )

        self.assertIn(
            (
                'media="(prefers-color-scheme: dark) '
                'and (max-width: 600px)" '
                'srcset="./assets/profile/generated/'
                'languages/dark/mobile/cpp.svg"'
            ),
            rendered,
        )

        self.assertIn(
            (
                'media="(prefers-color-scheme: light)" '
                'srcset="./assets/profile/generated/'
                'languages/light/desktop/cpp.svg"'
            ),
            rendered,
        )

        self.assertIn(
            (
                'media="(prefers-color-scheme: dark)" '
                'srcset="./assets/profile/generated/'
                'languages/dark/desktop/cpp.svg"'
            ),
            rendered,
        )

        self.assertIn(
            (
                '?tab=repositories&amp;'
                'language=c%2B%2B'
            ),
            rendered,
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

    def test_empty_release_feed_keeps_italic_message(self):
        self.assertEqual(
            profile.render_recent_releases([]),
            "*No published releases yet.*",
        )



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


    def test_building_language_metadata_links_to_repository_filter(self):
        with (
            patch.object(
                profile,
                "seti_language_icon_asset_path",
                return_value=None,
            ),
            patch.object(
                profile,
                "seti_language_icon_url",
                return_value="https://example.invalid/cpp.svg",
            ) as icon_url_mock,
        ):
            rendered = profile.render_language_metadata("C++")

        self.assertIn(
            (
                'href="https://github.com/Yusseter'
                '?tab=repositories&amp;language=c%2B%2B"'
            ),
            rendered,
        )
        self.assertIn(">C++</a>", rendered)
        icon_url_mock.assert_called_once_with("C++")

    def test_search_retries_incomplete_results(self):
        incomplete = {
            "incomplete_results": True,
            "items": [],
        }
        complete = {
            "incomplete_results": False,
            "items": [],
        }

        with (
            patch.object(
                profile,
                "rest_json_request",
                side_effect=[
                    incomplete,
                    incomplete,
                    complete,
                ],
            ) as request_mock,
            patch.object(
                profile.time,
                "sleep",
            ) as sleep_mock,
        ):
            commits = profile.fetch_searched_recent_commits()

        self.assertEqual(commits, [])
        self.assertEqual(request_mock.call_count, 3)
        self.assertEqual(
            [call.args[0] for call in sleep_mock.call_args_list],
            [1, 3],
        )

    def test_persistent_incomplete_search_returns_none(self):
        incomplete = {
            "incomplete_results": True,
            "items": [],
        }

        with (
            patch.object(
                profile,
                "rest_json_request",
                return_value=incomplete,
            ) as request_mock,
            patch.object(
                profile.time,
                "sleep",
            ),
            patch("builtins.print") as print_mock,
        ):
            commits = profile.fetch_searched_recent_commits()

        self.assertIsNone(commits)
        self.assertEqual(request_mock.call_count, 3)
        print_mock.assert_called_once()
        self.assertIn(
            "preserving Recent commits",
            print_mock.call_args.args[0],
        )

    def test_readme_preserves_commits_when_search_is_incomplete(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            readme_path = Path(temp_dir) / "README.md"

            readme_path.write_text(
                """<!-- snapshot:start -->
old snapshot
<!-- snapshot:end -->
<!-- building_now:start -->
old building
<!-- building_now:end -->
<!-- recent_releases:start -->
old releases
<!-- recent_releases:end -->
<!-- recent_commits:start -->
KEEP THIS COMMIT FEED
<!-- recent_commits:end -->
""",
                encoding="utf-8",
            )

            with patch.object(
                profile,
                "README_PATH",
                readme_path,
            ):
                profile.update_readme(
                    {"repositories": []},
                    {"repositories": []},
                    [],
                    [],
                    None,
                    "full_svg",
                )

            result = readme_path.read_text(
                encoding="utf-8"
            )

        self.assertIn(
            "KEEP THIS COMMIT FEED",
            result,
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

    def test_recent_commit_render_omits_message_body(self):
        rendered = profile.render_recent_commits(
            [
                {
                    "repositoryName": "project",
                    "repositoryUrl": (
                        "https://github.com/Yusseter/project"
                    ),
                    "oid": "abcdef1234567890",
                    "url": (
                        "https://github.com/Yusseter/project/"
                        "commit/abcdef1234567890"
                    ),
                    "messageHeadline": "Example commit",
                    "messageBody": "BODY SENTINEL",
                    "committedDate": "2026-09-24T12:00:00Z",
                }
            ]
        )

        self.assertIn(
            "Example commit",
            rendered,
        )
        self.assertIn(
            "abcdef1",
            rendered,
        )
        self.assertNotIn(
            "BODY SENTINEL",
            rendered,
        )
        self.assertNotIn(
            "<details>",
            rendered,
        )
        self.assertNotIn(
            "<summary>Details</summary>",
            rendered,
        )



class ResponsiveInlineRenderingTests(unittest.TestCase):
    def test_release_title_and_badge_share_one_link(self):
        cases = (
            ("latest.svg", True, False),
            ("prerelease.svg", False, True),
        )

        release_url = (
            "https://github.com/Yusseter/test/"
            "releases/tag/v0.2.0"
        )

        for badge, is_latest, is_prerelease in cases:
            with self.subTest(badge=badge):
                rendered = profile.render_recent_releases(
                    [
                        {
                            "name": (
                                "CK3 Workshop Auto Updater v0.2.0"
                            ),
                            "url": release_url,
                            "repositoryUrl": (
                                "https://github.com/Yusseter/test"
                            ),
                            "tagName": "v0.2.0",
                            "publishedAt": (
                                "2026-08-05T11:08:17Z"
                            ),
                            "isLatest": is_latest,
                            "isPrerelease": is_prerelease,
                        }
                    ]
                )

                headline, metadata = rendered.split(
                    "<br>\n",
                    1,
                )

                self.assertIn(
                    (
                        "**CK3 Workshop Auto Updater v0.2.0**"
                        "&nbsp;<img src="
                        '"./assets/profile/icons/releases/'
                        f'{badge}"'
                    ),
                    headline,
                )

                self.assertEqual(
                    headline.count(release_url),
                    1,
                )

                self.assertNotIn(
                    "&nbsp;[<img",
                    headline,
                )

                self.assertIn(
                    (
                        'tag.svg" alt="" height="18" '
                        'align="texttop">&nbsp;v0.2.0'
                    ),
                    metadata,
                )


    def test_commit_icon_and_sha_are_nonbreaking_unit(self):
        rendered = profile.render_recent_commits(
            [
                {
                    "repositoryName": "project",
                    "repositoryUrl": (
                        "https://github.com/Yusseter/project"
                    ),
                    "oid": "abcdef1234567890",
                    "url": (
                        "https://github.com/Yusseter/project/"
                        "commit/abcdef1234567890"
                    ),
                    "messageHeadline": "Example commit",
                    "messageBody": "",
                    "committedDate": "2026-09-24T12:00:00Z",
                }
            ]
        )

        self.assertIn(
            (
                'commit.svg" alt="" height="18" '
                'align="texttop">&nbsp;abcdef1'
            ),
            rendered,
        )


if __name__ == "__main__":
    unittest.main()
