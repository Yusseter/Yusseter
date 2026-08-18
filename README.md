<!-- markdownlint-disable MD013 MD033 MD041 -->

<p align="center">
  <img src="./assets/profile/header.svg" width="760" alt="Yusseter profile header">
</p>

## Building now

<!-- building_now:start -->
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — Windhawk mod for locking Windows 11 notification-area icon order, with supporting analyzers and research.<br>
  <sub><blockquote>Updated <relative-time datetime="2026-08-18T22:10:40Z">Aug 18, 2026</relative-time> · <picture><source media="(max-width: 600px)" srcset="./assets/profile/languages/cpp-mobile.svg"><img src="./assets/profile/languages/cpp.svg" alt="" height="20" align="texttop"></picture>C++</blockquote></sub>
- [**ck3-workshop-history**](https://github.com/Yusseter/ck3-workshop-history) — *No description.*<br>
  <sub><blockquote>Updated <relative-time datetime="2026-08-16T22:47:58Z">Aug 16, 2026</relative-time> · <picture><source media="(max-width: 600px)" srcset="./assets/profile/languages/powershell-mobile.svg"><img src="./assets/profile/languages/powershell.svg" alt="" height="20" align="texttop"></picture>PowerShell</blockquote></sub>
<!-- building_now:end -->

## Recent commits

<!-- recent_commits:start -->
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Use native relative times in profile metadata](https://github.com/Yusseter/Yusseter/commit/40a0aed846be8e49b2ff6bf6a5af04fed7309f7b)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-08-18T22:16:58Z">Aug 18, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 40a0aed](https://github.com/Yusseter/Yusseter/commit/40a0aed846be8e49b2ff6bf6a5af04fed7309f7b)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Replace static GitHub-style time labels with GitHub&#x27;s native &lt;relative-time&gt; element for Building now updates, recent commits, and releases so displayed times update client-side without regenerating the README. Remove the custom relative-time formatter and fix release metadata wording from &quot;Released this ...&quot; to &quot;Released ...&quot;.</p>
  </details>
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — [Validate live tray identity bridge](https://github.com/Yusseter/tray-order-lock/commit/4b80c492f4596ae0b7624ba8374c7039e056b8ae)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-08-18T22:10:40Z">Aug 18, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 4b80c49](https://github.com/Yusseter/tray-order-lock/commit/4b80c492f4596ae0b7624ba8374c7039e056b8ae)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>- Update Tray Add Path Analyzer to version 0.34.0.<br>- Hook NotificationAreaIcon2 construction and copy the 64-bit value from its NotifyIconSettings pair.<br>- Convert each constructed NotificationAreaIcon2 object to its INotificationAreaIcon ABI pointer through the previously validated QueryInterface path.<br>- Confirm that the copied settings identity is present in UIOrderList.<br>- Correlate the Discord tray icon&#x27;s live implementation, ABI pointer and 64-bit Windows tray identity.<br>- Confirm that MoveNotificationAreaIcon receives the same mapped ABI pointer and settings identity during a real manual drag.<br>- Confirm that NotifyIconSettingsDatabase::MoveIcon receives the same active settings identity as its first 64-bit identity argument.<br>- Validate the complete live ABI-to-NotifyIconSettings identity bridge without blocking moves, performing automatic moves or writing registry state.</p>
  </details>
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — [Audit NotifyIconSettings identity bridge](https://github.com/Yusseter/tray-order-lock/commit/0578496eef7da6104967587c46ac366887c03a59)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-08-18T22:03:27Z">Aug 18, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 0578496](https://github.com/Yusseter/tray-order-lock/commit/0578496eef7da6104967587c46ac366887c03a59)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>- Update Tray Add Path Analyzer to version 0.33.0.<br>- Audit the 64-bit settings identity bridge used to construct NotificationAreaIcon2 objects.<br>- Confirm that CreateDefaultSettingsForNewIcon returns a pair containing an unsigned 64-bit value and a shared registry HKEY.<br>- Confirm that TryGetSettingsForExistingIcon returns an optional value containing the same pair type.<br>- Confirm that NotificationAreaIcon2 construction consumes that settings pair.<br>- Confirm that NotifyIconSettingsDatabase::GetUIOrderForIcon accepts a 64-bit identity.<br>- Discover NotifyIconSettingsDatabase::MoveIcon with two 64-bit identity arguments and a relative-position argument.<br>- Scan 27,966 taskbar.dll symbols and record ten bridge-related matches.<br>- Keep the audit read-only without invoking private functions or modifying tray state.</p>
  </details>
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Keep recent commits fresh after pushes](https://github.com/Yusseter/Yusseter/commit/8757486ec9a4b442b23fdaafd617173e6e469992)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-08-18T22:00:11Z">Aug 18, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 8757486](https://github.com/Yusseter/Yusseter/commit/8757486ec9a4b442b23fdaafd617173e6e469992)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Combine GitHub Commit Search with fresh default-branch commit data from owned public repositories so Recent commits does not depend on search indexing immediately after a push. Merge both sources by commit SHA, prefer the fresh GraphQL data for owned repositories, sort by author date, and keep the latest five authored commits.</p>
  </details>
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — [Audit NotificationAreaIconIdentity bridge symbols](https://github.com/Yusseter/tray-order-lock/commit/231af690c33ef08e5352cdd1b7183c35cfee271e)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-08-18T21:57:44Z">Aug 18, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 231af69](https://github.com/Yusseter/tray-order-lock/commit/231af690c33ef08e5352cdd1b7183c35cfee271e)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>- Update Tray Add Path Analyzer to version 0.32.0.<br>- Enumerate every taskbar.dll symbol that references NotificationAreaIconIdentity.<br>- Emit long undecorated and decorated PDB symbol names in complete log chunks.<br>- Confirm that NotificationAreaIconIdentity can be constructed directly from _TRAYNOTIFYDATAW.<br>- Confirm that NotificationAreaIcon2::Identity() returns NotificationAreaIconIdentity by value.<br>- Discover that NotificationAreaIcon2 construction receives both NotificationAreaIconIdentity and a pair containing an unsigned 64-bit value plus a shared registry HKEY.<br>- Identify equality and collection-search operations that use NotificationAreaIconIdentity.<br>- Scan 27,966 symbols and record 36 identity-related matches, including 16 bridge candidates.<br>- Keep the audit read-only without invoking identity functions or modifying tray state.</p>
  </details>
<!-- recent_commits:end -->

## Recent releases

<!-- recent_releases:start -->
- [**CK3 Workshop Auto Updater v0.3.0**](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.3.0) [<img src="./assets/profile/release-latest.svg" alt="Latest" height="24" align="absmiddle">](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.3.0)<br>
  <sub><blockquote>Released <relative-time datetime="2026-08-07T09:23:12Z">Aug 7, 2026</relative-time> · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> v0.3.0](https://github.com/Yusseter/ck3-workshop-auto-updater/tree/v0.3.0)</blockquote></sub>
- [**Tray Order Lock 0.1.0**](https://github.com/Yusseter/tray-order-lock/releases/tag/tray-order-lock-v0.1.0) [<img src="./assets/profile/release-latest.svg" alt="Latest" height="24" align="absmiddle">](https://github.com/Yusseter/tray-order-lock/releases/tag/tray-order-lock-v0.1.0)<br>
  <sub><blockquote>Released <relative-time datetime="2026-08-05T19:40:24Z">Aug 5, 2026</relative-time> · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> tray-order-lock-v0.1.0](https://github.com/Yusseter/tray-order-lock/tree/tray-order-lock-v0.1.0)</blockquote></sub>
- [**CK3 Workshop Auto Updater v0.2.0**](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.2.0) [<img src="./assets/profile/release-prerelease.svg" alt="Pre-release" height="24" align="absmiddle">](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.2.0)<br>
  <sub><blockquote>Released <relative-time datetime="2026-08-05T11:08:17Z">Aug 5, 2026</relative-time> · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> v0.2.0](https://github.com/Yusseter/ck3-workshop-auto-updater/tree/v0.2.0)</blockquote></sub>

<details>
<summary>More releases</summary>

- [**CK3 Workshop Auto Updater v0.1.1**](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.1.1) [<img src="./assets/profile/release-prerelease.svg" alt="Pre-release" height="24" align="absmiddle">](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.1.1)<br>
  <sub><blockquote>Released <relative-time datetime="2026-08-05T10:06:18Z">Aug 5, 2026</relative-time> · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> v0.1.1](https://github.com/Yusseter/ck3-workshop-auto-updater/tree/v0.1.1)</blockquote></sub>
- [**CK3 Workshop Auto Updater v0.1.0**](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.1.0) [<img src="./assets/profile/release-prerelease.svg" alt="Pre-release" height="24" align="absmiddle">](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.1.0)<br>
  <sub><blockquote>Released <relative-time datetime="2026-08-03T12:43:57Z">Aug 3, 2026</relative-time> · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> v0.1.0](https://github.com/Yusseter/ck3-workshop-auto-updater/tree/v0.1.0)</blockquote></sub>
- [**1.2.2 for 1.19 (Released: 2026-04-20)**](https://github.com/Yusseter/yb_map/releases/tag/1.2.2) [<img src="./assets/profile/release-latest.svg" alt="Latest" height="24" align="absmiddle">](https://github.com/Yusseter/yb_map/releases/tag/1.2.2)<br>
  <sub><blockquote>Released <relative-time datetime="2026-04-20T17:44:05Z">Apr 20, 2026</relative-time> · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> 1.2.2](https://github.com/Yusseter/yb_map/tree/1.2.2)</blockquote></sub>
- [**1.2.1 for 1.18 (Released: 2026-03-13)**](https://github.com/Yusseter/yb_map/releases/tag/1.2.1)<br>
  <sub><blockquote>Released <relative-time datetime="2026-03-13T17:55:13Z">Mar 13, 2026</relative-time> · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> 1.2.1](https://github.com/Yusseter/yb_map/tree/1.2.1)</blockquote></sub>

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
