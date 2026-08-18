<!-- markdownlint-disable MD013 MD033 MD041 -->

<p align="center">
  <img src="./assets/profile/header.svg" width="760" alt="Yusseter profile header">
</p>

## Building now

<!-- building_now:start -->
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — Windhawk mod for locking Windows 11 notification-area icon order, with supporting analyzers and research.<br>
  <sub><blockquote>Updated 2 minutes ago · <picture><source media="(max-width: 600px)" srcset="./assets/profile/languages/cpp-mobile.svg"><img src="./assets/profile/languages/cpp.svg" alt="" height="20" align="texttop"></picture>C++</blockquote></sub>
- [**ck3-workshop-history**](https://github.com/Yusseter/ck3-workshop-history) — *No description.*<br>
  <sub><blockquote>Updated 2 days ago · <picture><source media="(max-width: 600px)" srcset="./assets/profile/languages/powershell-mobile.svg"><img src="./assets/profile/languages/powershell.svg" alt="" height="20" align="texttop"></picture>PowerShell</blockquote></sub>
<!-- building_now:end -->

## Recent commits

<!-- recent_commits:start -->
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Keep recent commits fresh after pushes](https://github.com/Yusseter/Yusseter/commit/8757486ec9a4b442b23fdaafd617173e6e469992)<br>
  <sub><blockquote>Committed 25 seconds ago · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 8757486](https://github.com/Yusseter/Yusseter/commit/8757486ec9a4b442b23fdaafd617173e6e469992)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Combine GitHub Commit Search with fresh default-branch commit data from owned public repositories so Recent commits does not depend on search indexing immediately after a push. Merge both sources by commit SHA, prefer the fresh GraphQL data for owned repositories, sort by author date, and keep the latest five authored commits.</p>
  </details>
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — [Audit NotificationAreaIconIdentity bridge symbols](https://github.com/Yusseter/tray-order-lock/commit/231af690c33ef08e5352cdd1b7183c35cfee271e)<br>
  <sub><blockquote>Committed 2 minutes ago · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 231af69](https://github.com/Yusseter/tray-order-lock/commit/231af690c33ef08e5352cdd1b7183c35cfee271e)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>- Update Tray Add Path Analyzer to version 0.32.0.<br>- Enumerate every taskbar.dll symbol that references NotificationAreaIconIdentity.<br>- Emit long undecorated and decorated PDB symbol names in complete log chunks.<br>- Confirm that NotificationAreaIconIdentity can be constructed directly from _TRAYNOTIFYDATAW.<br>- Confirm that NotificationAreaIcon2::Identity() returns NotificationAreaIconIdentity by value.<br>- Discover that NotificationAreaIcon2 construction receives both NotificationAreaIconIdentity and a pair containing an unsigned 64-bit value plus a shared registry HKEY.<br>- Identify equality and collection-search operations that use NotificationAreaIconIdentity.<br>- Scan 27,966 symbols and record 36 identity-related matches, including 16 bridge candidates.<br>- Keep the audit read-only without invoking identity functions or modifying tray state.</p>
  </details>
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — [Audit NotificationAreaIcon2 identity signature](https://github.com/Yusseter/tray-order-lock/commit/a53fb2ec8109531369223df065a1e3ce16af6aa5)<br>
  <sub><blockquote>Committed 6 minutes ago · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> a53fb2e](https://github.com/Yusseter/tray-order-lock/commit/a53fb2ec8109531369223df065a1e3ce16af6aa5)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>- Update Tray Add Path Analyzer to version 0.31.0.<br>- Enumerate taskbar.dll symbols without installing taskbar function hooks.<br>- Locate the exact NotificationAreaIcon2::Identity() PDB signature.<br>- Confirm that Identity() returns NotificationAreaIconIdentity by value rather than a primitive Windows tray identity.<br>- Record both the undecorated and decorated identity symbol names.<br>- Scan 27,966 taskbar.dll symbols and observe eight related identity matches.<br>- Keep the experiment read-only without invoking Identity(), moving tray icons or modifying tray state.</p>
  </details>
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Polish recent commit metadata](https://github.com/Yusseter/Yusseter/commit/1ef05719d955cadc74f9726e9385cce6544b2f71)<br>
  <sub><blockquote>Committed 14 minutes ago · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 1ef0571](https://github.com/Yusseter/Yusseter/commit/1ef05719d955cadc74f9726e9385cce6544b2f71)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Add the official GitHub Primer git-commit icon before short commit SHAs to better balance Recent commits metadata with the surrounding profile sections. Also shorten expandable commit body labels from &quot;Commit description&quot; to &quot;Details&quot; for a cleaner layout.</p>
  </details>
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Search authored commits across public repositories](https://github.com/Yusseter/Yusseter/commit/066bfff66a5e421ea383c3788c06516b5b9da92e)<br>
  <sub><blockquote>Committed 29 minutes ago · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 066bfff](https://github.com/Yusseter/Yusseter/commit/066bfff66a5e421ea383c3788c06516b5b9da92e)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Replace the owned-repository commit scan with GitHub&#x27;s global commit search so Recent commits can include commits authored by Yusseter in public repositories regardless of ownership. Sort results by author date, verify the matched GitHub author, preserve owner/repository names for external repositories, and keep the five-commit display limit.</p>
  </details>
<!-- recent_commits:end -->

## Recent releases

<!-- recent_releases:start -->
- [**CK3 Workshop Auto Updater v0.3.0**](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.3.0) [<img src="./assets/profile/release-latest.svg" alt="Latest" height="24" align="absmiddle">](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.3.0)<br>
  <sub><blockquote>Released this 2 weeks ago · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> v0.3.0](https://github.com/Yusseter/ck3-workshop-auto-updater/tree/v0.3.0)</blockquote></sub>
- [**Tray Order Lock 0.1.0**](https://github.com/Yusseter/tray-order-lock/releases/tag/tray-order-lock-v0.1.0) [<img src="./assets/profile/release-latest.svg" alt="Latest" height="24" align="absmiddle">](https://github.com/Yusseter/tray-order-lock/releases/tag/tray-order-lock-v0.1.0)<br>
  <sub><blockquote>Released this 2 weeks ago · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> tray-order-lock-v0.1.0](https://github.com/Yusseter/tray-order-lock/tree/tray-order-lock-v0.1.0)</blockquote></sub>
- [**CK3 Workshop Auto Updater v0.2.0**](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.2.0) [<img src="./assets/profile/release-prerelease.svg" alt="Pre-release" height="24" align="absmiddle">](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.2.0)<br>
  <sub><blockquote>Released this 2 weeks ago · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> v0.2.0](https://github.com/Yusseter/ck3-workshop-auto-updater/tree/v0.2.0)</blockquote></sub>

<details>
<summary>More releases</summary>

- [**CK3 Workshop Auto Updater v0.1.1**](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.1.1) [<img src="./assets/profile/release-prerelease.svg" alt="Pre-release" height="24" align="absmiddle">](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.1.1)<br>
  <sub><blockquote>Released this 2 weeks ago · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> v0.1.1](https://github.com/Yusseter/ck3-workshop-auto-updater/tree/v0.1.1)</blockquote></sub>
- [**CK3 Workshop Auto Updater v0.1.0**](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.1.0) [<img src="./assets/profile/release-prerelease.svg" alt="Pre-release" height="24" align="absmiddle">](https://github.com/Yusseter/ck3-workshop-auto-updater/releases/tag/v0.1.0)<br>
  <sub><blockquote>Released this 2 weeks ago · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> v0.1.0](https://github.com/Yusseter/ck3-workshop-auto-updater/tree/v0.1.0)</blockquote></sub>
- [**1.2.2 for 1.19 (Released: 2026-04-20)**](https://github.com/Yusseter/yb_map/releases/tag/1.2.2) [<img src="./assets/profile/release-latest.svg" alt="Latest" height="24" align="absmiddle">](https://github.com/Yusseter/yb_map/releases/tag/1.2.2)<br>
  <sub><blockquote>Released this Apr 20 · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> 1.2.2](https://github.com/Yusseter/yb_map/tree/1.2.2)</blockquote></sub>
- [**1.2.1 for 1.18 (Released: 2026-03-13)**](https://github.com/Yusseter/yb_map/releases/tag/1.2.1)<br>
  <sub><blockquote>Released this Mar 13 · [<img src="./assets/profile/release-tag.svg" alt="" height="18" align="texttop"> 1.2.1](https://github.com/Yusseter/yb_map/tree/1.2.1)</blockquote></sub>

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
