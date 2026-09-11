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
  <sub><blockquote>Updated <relative-time datetime="2026-09-05T19:13:30Z">Sep 5, 2026</relative-time> · <a href="https://github.com/Yusseter?tab=repositories&amp;language=java"><picture><source media="(max-width: 600px)" srcset="./assets/profile/languages/java-mobile.svg"><img src="./assets/profile/languages/java.svg" alt="" height="20" align="texttop"></picture>Java</a></blockquote></sub>
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — Yusseter's Profile repository.<br>
  <sub><blockquote>Updated <relative-time datetime="2026-09-11T04:46:53Z">Sep 11, 2026</relative-time> · <a href="https://github.com/Yusseter?tab=repositories&amp;language=python"><picture><source media="(max-width: 600px)" srcset="./assets/profile/languages/python-mobile.svg"><img src="./assets/profile/languages/python.svg" alt="" height="20" align="texttop"></picture>Python</a></blockquote></sub>
<!-- building_now:end -->

## Recent commits

<!-- recent_commits:start -->
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Merge branch &#x27;main&#x27; of https://github.com/Yusseter/Yusseter](https://github.com/Yusseter/Yusseter/commit/81e6c47953020085e8c32dc0f33f1a7032cdc6db)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-09-07T22:25:06Z">Sep 7, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 81e6c47](https://github.com/Yusseter/Yusseter/commit/81e6c47953020085e8c32dc0f33f1a7032cdc6db)</blockquote></sub>
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Retry commit search and preserve feed on incomplete results](https://github.com/Yusseter/Yusseter/commit/73dec10c96d4e495a14245f064a7397788984936)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-09-07T22:24:18Z">Sep 7, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 73dec10](https://github.com/Yusseter/Yusseter/commit/73dec10c96d4e495a14245f064a7397788984936)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Add retry logic for GitHub commit search when `incomplete_results` is returned, using short delays between attempts. If the search remains incomplete after all retries, log a warning and preserve the existing Recent commits block in the README instead of overwriting it with partial data. Update status output accordingly and add tests covering successful retry, persistent incomplete results, and README preservation.</p>
  </details>
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Link language metadata to repo filter](https://github.com/Yusseter/Yusseter/commit/75a534ca1f731918234a7774869e94114284c7a0)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-09-07T20:15:34Z">Sep 7, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 75a534c](https://github.com/Yusseter/Yusseter/commit/75a534ca1f731918234a7774869e94114284c7a0)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Wrap language metadata (icon + name) in an anchor to the user&#x27;s GitHub repositories page with `tab=repositories` and a `language` query. Use `urllib.parse.urlencode` and `escape(..., quote=True)` to safely encode values such as `C++` as `c%2B%2B`. Add a unit test confirming the encoded `href` and language icon URL resolution.</p>
  </details>
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
