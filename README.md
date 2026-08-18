<!-- markdownlint-disable MD013 MD033 MD041 -->

<p align="center">
  <img src="./assets/profile/header.svg" width="760" alt="Yusseter profile header">
</p>

## Building now

<!-- building_now:start -->
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — Windhawk mod for locking Windows 11 notification-area icon order, with supporting analyzers and research.<br>
  <sub><blockquote>Updated 20 minutes ago · <picture><source media="(max-width: 600px)" srcset="./assets/profile/languages/cpp-mobile.svg"><img src="./assets/profile/languages/cpp.svg" alt="" height="20" align="texttop"></picture>C++</blockquote></sub>
- [**ck3-workshop-history**](https://github.com/Yusseter/ck3-workshop-history) — *No description.*<br>
  <sub><blockquote>Updated 2 days ago · <picture><source media="(max-width: 600px)" srcset="./assets/profile/languages/powershell-mobile.svg"><img src="./assets/profile/languages/powershell.svg" alt="" height="20" align="texttop"></picture>PowerShell</blockquote></sub>
<!-- building_now:end -->

## Recent commits

<!-- recent_commits:start -->
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Search authored commits across public repositories](https://github.com/Yusseter/Yusseter/commit/066bfff66a5e421ea383c3788c06516b5b9da92e)<br>
  <sub><blockquote>Committed 15 minutes ago · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 066bfff](https://github.com/Yusseter/Yusseter/commit/066bfff66a5e421ea383c3788c06516b5b9da92e)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Replace the owned-repository commit scan with GitHub&#x27;s global commit search so Recent commits can include commits authored by Yusseter in public repositories regardless of ownership. Sort results by author date, verify the matched GitHub author, preserve owner/repository names for external repositories, and keep the five-commit display limit.</p>
  </details>
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — [Persist manually learned tray order across Explorer restarts](https://github.com/Yusseter/tray-order-lock/commit/80a2dd0a9c915f117cfaba6d94be66a17d855a5a)<br>
  <sub><blockquote>Committed 20 minutes ago · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 80a2dd0](https://github.com/Yusseter/tray-order-lock/commit/80a2dd0a9c915f117cfaba6d94be66a17d855a5a)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>- Extend the Tray Order Lock 0.2.0 development line with configurable ordering behavior.<br>- Add Lock all reordering and Preserve order, allow manual changes modes.<br>- Preserve the existing move-suppression behavior in Lock all reordering mode.<br>- Allow manual tray moves to execute normally in Preserve order mode.<br>- Capture UIOrderList before and after an allowed move and identify the moved Windows tray identity.<br>- Convert supported tray identities to canonical logical keys using IconGuid or version-normalized executable path plus UID.<br>- Learn the moved icon&#x27;s nearest reliable logical predecessor and follower.<br>- Persist the updated canonical order in Windhawk mod local storage.<br>- Reload and merge the persisted canonical order when settings change or Explorer starts again.<br>- Confirm that a manual Discord move is learned and persisted with both logical neighbors resolved.<br>- Confirm that Lock all reordering still blocks subsequent move requests.<br>- Confirm that the persisted canonical order reloads successfully after a full Explorer process restart.<br>- Keep automatic replacement restoration disabled until the production live-identity mapping layer is added.</p>
  </details>
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — [Document invalid alternate tray move-path experiment](https://github.com/Yusseter/tray-order-lock/commit/08eb0528c5f12a3aa58a959631f29aab58f62e22)<br>
  <sub><blockquote>Committed 21 minutes ago · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 08eb052](https://github.com/Yusseter/tray-order-lock/commit/08eb0528c5f12a3aa58a959631f29aab58f62e22)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>- Update Tray Add Path Analyzer to version 0.30.0.<br>- Instrument ITaskbarModel5::MoveNotificationAreaIcon and NotificationAreaIconManager2::MoveIcon to correlate their call paths.<br>- Record that the tested move followed the normal taskbar-model-to-manager path with parentTaskbarMove=1.<br>- Record that no manager move without a taskbar-model parent was observed in the run.<br>- Correct the experiment documentation to state that the assumed separate context-menu move path was based on a mistaken interpretation of the manual test.<br>- Preserve the result as a research-history checkpoint without claiming that an alternate move path exists or does not exist.</p>
  </details>
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Replace recent repositories with recent commits](https://github.com/Yusseter/Yusseter/commit/6350721c7cbd3939c5b54825de565c04d8357a98)<br>
  <sub><blockquote>Committed 39 minutes ago · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 6350721](https://github.com/Yusseter/Yusseter/commit/6350721c7cbd3939c5b54825de565c04d8357a98)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Replace the recently updated repositories section with a Recent commits feed that collects the latest five commits authored by Yusseter across public repositories. Include repository and commit links, relative commit timestamps, short SHAs, and optional commit descriptions, and clean up related Markdown lint issues.</p>
  </details>
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — [Harden Tray Order Lock initialization across Explorer restarts](https://github.com/Yusseter/tray-order-lock/commit/c200eaa26fe4e661adcc3cda08527bbc04c922e5)<br>
  <sub><blockquote>Committed 1 hour ago · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> c200eaa](https://github.com/Yusseter/tray-order-lock/commit/c200eaa26fe4e661adcc3cda08527bbc04c922e5)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>- Start the Tray Order Lock 0.2.0 development line while preserving the existing lock-all-reordering behavior.<br>- Replace the previous taskbar module-load bootstrap with Shell_TrayWnd-aware initialization.<br>- Detect an already running primary taskbar and register taskbar hooks during normal mod initialization.<br>- Defer taskbar hook setup when Explorer starts before its primary shell window exists.<br>- Detect creation of Shell_TrayWnd and apply the deferred taskbar hooks immediately.<br>- Preserve the existing MoveNotificationAreaIcon suppression behavior without writing tray order data.<br>- Confirm that tray move requests remain blocked before and after a complete Explorer process restart.</p>
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
