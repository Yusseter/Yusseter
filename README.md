<!-- markdownlint-disable MD013 MD033 MD041 -->

<p align="center">
  <img src="./assets/profile/header.svg" width="760" alt="Yusseter profile header">
</p>

## Building now

<!-- building_now:start -->
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — Windhawk mod for locking Windows 11 notification-area icon order, with supporting analyzers and research.<br>
  <sub><blockquote>Updated <relative-time datetime="2026-08-18T22:10:40Z">Aug 18, 2026</relative-time> · <picture><source media="(max-width: 600px)" srcset="./assets/profile/languages/cpp-mobile.svg"><img src="./assets/profile/languages/cpp.svg" alt="" height="20" align="texttop"></picture>C++</blockquote></sub>
- [**ck3-workshop-history**](https://github.com/Yusseter/ck3-workshop-history) — *No description.*<br>
  <sub><blockquote>Updated <relative-time datetime="2026-08-19T13:00:43Z">Aug 19, 2026</relative-time> · <picture><source media="(max-width: 600px)" srcset="./assets/profile/languages/powershell-mobile.svg"><img src="./assets/profile/languages/powershell.svg" alt="" height="20" align="texttop"></picture>PowerShell</blockquote></sub>
- [**ck3-workshop-auto-updater**](https://github.com/Yusseter/ck3-workshop-auto-updater) — A Windows utility that detects and requests missing Crusader Kings III Steam Workshop updates.<br>
  <sub><blockquote>Updated <relative-time datetime="2026-08-19T10:29:24Z">Aug 19, 2026</relative-time> · <picture><source media="(max-width: 600px)" srcset="./assets/profile/languages/powershell-mobile.svg"><img src="./assets/profile/languages/powershell.svg" alt="" height="20" align="texttop"></picture>PowerShell</blockquote></sub>
<!-- building_now:end -->

## Recent commits

<!-- recent_commits:start -->
- [**ck3-workshop-history**](https://github.com/Yusseter/ck3-workshop-history) — [Add first-pass archive verification analysis](https://github.com/Yusseter/ck3-workshop-history/commit/27be09f84e2b67a701fc7131b517660888dd8a7a)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-08-19T13:00:43Z">Aug 19, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 27be09f](https://github.com/Yusseter/ck3-workshop-history/commit/27be09f84e2b67a701fc7131b517660888dd8a7a)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Expand the validated archive-content pilot across all 52 P0 Skymods revisions from Analysis 07. Persist resumable per-revision state, reuse Analysis 08 cache where available, download remaining archives through isolated Chrome/CDP, validate archive provenance and descriptors, inventory archived content, and compare related historical Git candidates using Git-aware projected hashing.<br><br>The completed queue verifies all 52 revisions with zero final errors: 41 resolve to unique projected Git matches, one retains multiple exact projected matches, and 10 have no exact projected Git match. All 52 archives contain exactly one descriptor matching the expected Workshop ID. Include cumulative raw-page provenance, archive and file inventories, comparison and difference matrices, queue and run history, and an unattended run-to-completion helper.</p>
  </details>
- [**ck3-workshop-auto-updater**](https://github.com/Yusseter/ck3-workshop-auto-updater) — [Release 0.3.1](https://github.com/Yusseter/ck3-workshop-auto-updater/commit/321da966e1519b5dc0b4f30303ad670d1a838b76)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-08-19T10:29:24Z">Aug 19, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 321da96](https://github.com/Yusseter/ck3-workshop-auto-updater/commit/321da966e1519b5dc0b4f30303ad670d1a838b76)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Mark version 0.3.1 as released in the changelog and README. This update also finalizes the changelog entry for the Windows installer Open Logs shortcut fix.</p>
  </details>
- [**ck3-workshop-auto-updater**](https://github.com/Yusseter/ck3-workshop-auto-updater) — [Fix Windows installer Open Logs shortcut](https://github.com/Yusseter/ck3-workshop-auto-updater/commit/b5b898349311352ac4565103d377f6a2c3d320c1)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-08-19T10:06:35Z">Aug 19, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> b5b8983](https://github.com/Yusseter/ck3-workshop-auto-updater/commit/b5b898349311352ac4565103d377f6a2c3d320c1)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>The Windows installer now uses the correct Explorer path for the Open Logs shortcut so the logs folder opens reliably. This change also bumps the project version to 0.3.1 and updates the README and changelog for the unreleased fix.</p>
  </details>
- [**ck3-workshop-auto-updater**](https://github.com/Yusseter/ck3-workshop-auto-updater) — [Fix Open Logs shortcut path](https://github.com/Yusseter/ck3-workshop-auto-updater/commit/46998a7c25a33b59b623cc4b705b1b1a6e057afa)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-08-19T09:53:47Z">Aug 19, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 46998a7](https://github.com/Yusseter/ck3-workshop-auto-updater/commit/46998a7c25a33b59b623cc4b705b1b1a6e057afa)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>The installer used the system directory variable for the Open Logs shortcut, which points to System32 instead of the Windows directory. This change uses the Windows directory variable so the shortcut resolves explorer.exe correctly.</p>
  </details>
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Use native relative times in profile metadata](https://github.com/Yusseter/Yusseter/commit/40a0aed846be8e49b2ff6bf6a5af04fed7309f7b)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-08-18T22:16:58Z">Aug 18, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 40a0aed](https://github.com/Yusseter/Yusseter/commit/40a0aed846be8e49b2ff6bf6a5af04fed7309f7b)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Replace static GitHub-style time labels with GitHub&#x27;s native &lt;relative-time&gt; element for Building now updates, recent commits, and releases so displayed times update client-side without regenerating the README. Remove the custom relative-time formatter and fix release metadata wording from &quot;Released this ...&quot; to &quot;Released ...&quot;.</p>
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
