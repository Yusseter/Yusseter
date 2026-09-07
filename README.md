<!-- markdownlint-disable MD013 MD033 MD041 -->

<p align="center">
  <picture>
    <source media="(max-width: 600px)" srcset="./assets/profile/header-mobile.svg">
    <img src="./assets/profile/header.svg" width="100%" alt="Yusseter profile header">
  </picture>
</p>

## Building now

<!-- building_now:start -->
- [**OptiFabric**](https://github.com/Yusseter/OptiFabric) — OptiFabric venturing out into the 1.16+ world<br>
  <sub><blockquote>Updated <relative-time datetime="2026-09-05T19:13:30Z">Sep 5, 2026</relative-time> · <picture><source media="(max-width: 600px)" srcset="./assets/profile/languages/java-mobile.svg"><img src="./assets/profile/languages/java.svg" alt="" height="20" align="texttop"></picture>Java</blockquote></sub>
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — *No description.*<br>
  <sub><blockquote>Updated <relative-time datetime="2026-09-07T18:35:19Z">Sep 7, 2026</relative-time> · <picture><source media="(max-width: 600px)" srcset="./assets/profile/languages/python-mobile.svg"><img src="./assets/profile/languages/python.svg" alt="" height="20" align="texttop"></picture>Python</blockquote></sub>
<!-- building_now:end -->

## Recent commits

<!-- recent_commits:start -->
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Add contribution_forks and private repo handling](https://github.com/Yusseter/Yusseter/commit/73e811d9bee84fd70ccfa8c2f8cb58ae25edc697)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-09-07T18:34:57Z">Sep 7, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 73e811d](https://github.com/Yusseter/Yusseter/commit/73e811d9bee84fd70ccfa8c2f8cb58ae25edc697)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Use PROFILE_GITHUB_TOKEN in CI and add support for a contribution_forks list in profile_renderer.json. Introduce load_profile_config with validation and normalization of contribution_forks. Update the GraphQL query to fetch all owned repositories visible to the token, including private repositories, with nameWithOwner and isPrivate metadata. Snapshot languages, stars, and releases now use the same repository scope: all owned repositories are included except forks explicitly listed in contribution_forks. Public activity and release feeds continue to exclude private repositories, and hardcoded Yusseter/Placeholder exclusions were removed. Expand tests to cover contribution fork filtering, private repository handling, snapshot scope consistency, and the new query fields.</p>
  </details>
- [**OptiFabric**](https://github.com/Yusseter/OptiFabric) — [Bridge Fabric world render events in patcher](https://github.com/Yusseter/OptiFabric/commit/44cc62087ce63f25dd0e29eef434d11328576a81)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-09-05T19:13:30Z">Sep 5, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 44cc620](https://github.com/Yusseter/OptiFabric/commit/44cc62087ce63f25dd0e29eef434d11328576a81)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Update `WorldRendererFix` to robustly inject Fabric Rendering V1 hooks into OptiFine&#x27;s main world render path. The patch now detects required anchor instructions, validates expected method and instruction shapes, prepares `WorldRenderContextImpl`, sets the matrix stack, and inserts all main event callbacks (`START_MAIN`, `BEFORE_ENTITIES`, `AFTER_ENTITIES`, `BEFORE_TRANSLUCENT`, `END_MAIN`). It also adds stronger duplicate and partial-bridge detection, clearer constants and helpers, and improved logging and error messages to fail fast when the bytecode structure is unexpected.</p>
  </details>
- [**OptiFabric**](https://github.com/Yusseter/OptiFabric) — [Restore vanilla render methods for Indigo](https://github.com/Yusseter/OptiFabric/commit/47e501ed3b112a5d3113d6296e80dd4bcdf609de)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-09-05T10:46:27Z">Sep 5, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 47e501e](https://github.com/Yusseter/OptiFabric/commit/47e501ed3b112a5d3113d6296e80dd4bcdf609de)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Rework `BlockRenderManagerFix` to replace OptiFine’s transformed `method_23071` and `method_3353` with vanilla copies when Indigo is loaded and no other renderer advertises `fabric-renderer-api-v1:contains_renderer`. Remove the previous dead-anchor injection approach, retain missing-method backfill logic, and fail explicitly when the expected vanilla or OptiFine render methods are unavailable.</p>
  </details>
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Refine fork handling across profile sections](https://github.com/Yusseter/Yusseter/commit/a456908944c89a826aba238e42ca6309f58678b1)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-09-04T23:36:21Z">Sep 4, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> a456908](https://github.com/Yusseter/Yusseter/commit/a456908944c89a826aba238e42ca6309f58678b1)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Adjust repository fetching and filtering so forks are handled per feature instead of globally. The GraphQL query now includes fork metadata, with separate project, activity, and snapshot scopes. Project languages, releases, and snapshot totals exclude forks, while Building now and the owned-repository freshness path for Recent commits can include them. Tests were expanded to cover query shape, scope behavior, snapshot totals, building-now selection, recent release filtering, and owned fork commit author matching.</p>
  </details>
- [**OptiFabric**](https://github.com/Yusseter/OptiFabric) — [Patch Bedrockify tooltip draw in OptiFine HUD](https://github.com/Yusseter/OptiFabric/commit/d12b9303ef75964fd06c03483b2aeb35cdd50b43)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-09-04T16:32:38Z">Sep 4, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> d12b930](https://github.com/Yusseter/OptiFabric/commit/d12b9303ef75964fd06c03483b2aeb35cdd50b43)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Reworks the InGameHud fix to preserve OptiFine’s selected-item rendering path instead of replacing its wrapper with the vanilla method. Adds a dead draw anchor for Bedrockify’s redirect and routes OptiFine’s real selected-item text draw through a new external bridge that invokes Bedrockify held-item tooltips via cached reflection when enabled, while preserving OptiFine’s normal draw behavior as fallback.</p>
  </details>
<!-- recent_commits:end -->

## Recent releases

<!-- recent_releases:start -->
- [**Tray Order Lock 0.2.0**](https://github.com/Yusseter/tray-order-lock/releases/tag/tray-order-lock-v0.2.0) [<img src="./assets/profile/release-latest.svg" alt="Latest" height="24" align="absmiddle">](https://github.com/Yusseter/tray-order-lock/releases/tag/tray-order-lock-v0.2.0)<br>
  <sub><blockquote>Released <relative-time datetime="2026-08-28T11:31:20Z">Aug 28, 2026</relative-time> · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> tray-order-lock-v0.2.0](https://github.com/Yusseter/tray-order-lock/tree/tray-order-lock-v0.2.0)</blockquote></sub>
- [**test**](https://github.com/Yusseter/Minecraft-Yusseter-s-Vanilla-Resource-Pack/releases/tag/test) [<img src="./assets/profile/release-latest.svg" alt="Latest" height="24" align="absmiddle">](https://github.com/Yusseter/Minecraft-Yusseter-s-Vanilla-Resource-Pack/releases/tag/test)<br>
  <sub><blockquote>Released <relative-time datetime="2026-08-20T14:03:25Z">Aug 20, 2026</relative-time> · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> test](https://github.com/Yusseter/Minecraft-Yusseter-s-Vanilla-Resource-Pack/tree/test)</blockquote></sub>
- [**CK3 Workshop Auto Updater v0.3.1**](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.3.1) [<img src="./assets/profile/release-latest.svg" alt="Latest" height="24" align="absmiddle">](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.3.1)<br>
  <sub><blockquote>Released <relative-time datetime="2026-08-19T15:55:31Z">Aug 19, 2026</relative-time> · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> v0.3.1](https://github.com/Yusseter/ck3-workshop-auto-updater/tree/v0.3.1)</blockquote></sub>

<details>
<summary>More releases</summary>

- [**CK3 Workshop Auto Updater v0.3.0**](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.3.0)<br>
  <sub><blockquote>Released <relative-time datetime="2026-08-07T09:23:12Z">Aug 7, 2026</relative-time> · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> v0.3.0](https://github.com/Yusseter/ck3-workshop-auto-updater/tree/v0.3.0)</blockquote></sub>
- [**Tray Order Lock 0.1.0**](https://github.com/Yusseter/tray-order-lock/releases/tag/tray-order-lock-v0.1.0)<br>
  <sub><blockquote>Released <relative-time datetime="2026-08-05T19:40:24Z">Aug 5, 2026</relative-time> · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> tray-order-lock-v0.1.0](https://github.com/Yusseter/tray-order-lock/tree/tray-order-lock-v0.1.0)</blockquote></sub>
- [**CK3 Workshop Auto Updater v0.2.0**](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.2.0) [<img src="./assets/profile/release-prerelease.svg" alt="Pre-release" height="24" align="absmiddle">](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.2.0)<br>
  <sub><blockquote>Released <relative-time datetime="2026-08-05T11:08:17Z">Aug 5, 2026</relative-time> · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> v0.2.0](https://github.com/Yusseter/ck3-workshop-auto-updater/tree/v0.2.0)</blockquote></sub>
- [**CK3 Workshop Auto Updater v0.1.1**](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.1.1) [<img src="./assets/profile/release-prerelease.svg" alt="Pre-release" height="24" align="absmiddle">](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.1.1)<br>
  <sub><blockquote>Released <relative-time datetime="2026-08-05T10:06:18Z">Aug 5, 2026</relative-time> · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> v0.1.1](https://github.com/Yusseter/ck3-workshop-auto-updater/tree/v0.1.1)</blockquote></sub>
- [**CK3 Workshop Auto Updater v0.1.0**](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.1.0) [<img src="./assets/profile/release-prerelease.svg" alt="Pre-release" height="24" align="absmiddle">](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.1.0)<br>
  <sub><blockquote>Released <relative-time datetime="2026-08-03T12:43:57Z">Aug 3, 2026</relative-time> · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> v0.1.0](https://github.com/Yusseter/ck3-workshop-auto-updater/tree/v0.1.0)</blockquote></sub>

</details>
<!-- recent_releases:end -->

## GitHub snapshot

<!-- snapshot:start -->
<p align="center">
  <picture>
    <source media="(max-width: 600px)" srcset="./assets/profile/snapshot-mobile.svg">
    <img src="./assets/profile/snapshot.svg" width="100%" alt="GitHub overview and languages">
  </picture>
</p>
<!-- snapshot:end -->
