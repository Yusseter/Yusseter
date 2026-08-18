<!-- markdownlint-disable MD013 MD033 MD041 -->

<p align="center">
  <img src="./assets/profile/header.svg" width="760" alt="Yusseter profile header">
</p>

## Building now

<!-- building_now:start -->
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — Windhawk mod for locking Windows 11 notification-area icon order, with supporting analyzers and research.<br>
  <sub><blockquote>Updated 21 minutes ago · <picture><source media="(max-width: 600px)" srcset="./assets/profile/languages/cpp-mobile.svg"><img src="./assets/profile/languages/cpp.svg" alt="" height="20" align="texttop"></picture>C++</blockquote></sub>
- [**ck3-workshop-history**](https://github.com/Yusseter/ck3-workshop-history) — *No description.*<br>
  <sub><blockquote>Updated 2 days ago · <picture><source media="(max-width: 600px)" srcset="./assets/profile/languages/powershell-mobile.svg"><img src="./assets/profile/languages/powershell.svg" alt="" height="20" align="texttop"></picture>PowerShell</blockquote></sub>
<!-- building_now:end -->

## Recent commits

<!-- recent_commits:start -->
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Replace recent repositories with recent commits](https://github.com/Yusseter/Yusseter/commit/6350721c7cbd3939c5b54825de565c04d8357a98)<br>
  <sub><blockquote>Committed 54 seconds ago · [6350721](https://github.com/Yusseter/Yusseter/commit/6350721c7cbd3939c5b54825de565c04d8357a98)</blockquote></sub>
  <details>
  <summary>Commit description</summary>
  <p>Replace the recently updated repositories section with a Recent commits feed that collects the latest five commits authored by Yusseter across public repositories. Include repository and commit links, relative commit timestamps, short SHAs, and optional commit descriptions, and clean up related Markdown lint issues.</p>
  </details>
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — [Harden Tray Order Lock initialization across Explorer restarts](https://github.com/Yusseter/tray-order-lock/commit/c200eaa26fe4e661adcc3cda08527bbc04c922e5)<br>
  <sub><blockquote>Committed 21 minutes ago · [c200eaa](https://github.com/Yusseter/tray-order-lock/commit/c200eaa26fe4e661adcc3cda08527bbc04c922e5)</blockquote></sub>
  <details>
  <summary>Commit description</summary>
  <p>- Start the Tray Order Lock 0.2.0 development line while preserving the existing lock-all-reordering behavior.<br>- Replace the previous taskbar module-load bootstrap with Shell_TrayWnd-aware initialization.<br>- Detect an already running primary taskbar and register taskbar hooks during normal mod initialization.<br>- Defer taskbar hook setup when Explorer starts before its primary shell window exists.<br>- Detect creation of Shell_TrayWnd and apply the deferred taskbar hooks immediately.<br>- Preserve the existing MoveNotificationAreaIcon suppression behavior without writing tray order data.<br>- Confirm that tray move requests remain blocked before and after a complete Explorer process restart.</p>
  </details>
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — [Validate persisted logical tray identity restoration](https://github.com/Yusseter/tray-order-lock/commit/58e0e49fa7b1d91e031933574da1307bbf694ccd)<br>
  <sub><blockquote>Committed 48 minutes ago · [58e0e49](https://github.com/Yusseter/tray-order-lock/commit/58e0e49fa7b1d91e031933574da1307bbf694ccd)</blockquote></sub>
  <details>
  <summary>Commit description</summary>
  <p>- Update Tray Add Path Analyzer to version 0.29.0.<br>- Replace historical Windows tray identity matching with persisted normalized path and UID logical identity matching.<br>- Persist the target UID together with the normalized logical path and manually learned canonical relation.<br>- Reload the persisted logical identity after a complete Explorer process restart.<br>- Confirm that the phase-1 Windows tray identity is absent from NotifyIconSettings in the replacement Explorer session.<br>- Match the replacement target directly from its current normalized path and UID without requiring the historical Windows identity.<br>- Recreate fresh canonical anchors and add helper icons to change the live overflow collection geometry.<br>- Confirm that the previously saved numeric target index is invalid after the collection changes.<br>- Resolve the persisted predecessor and follower from their current live positions.<br>- Restore the replacement target between the persisted canonical neighbors with exactly one second-session analyzer move.<br>- Confirm logical identity matching and canonical relation restoration across a full Explorer restart.<br>- Complete the end-to-end persisted logical identity validation successfully.</p>
  </details>
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Add responsive language icon alignment](https://github.com/Yusseter/Yusseter/commit/0a7ca46a640a98bfc7d2e3f84c2ffcc142fb2ff8)<br>
  <sub><blockquote>Committed 2 hours ago · [0a7ca46](https://github.com/Yusseter/Yusseter/commit/0a7ca46a640a98bfc7d2e3f84c2ffcc142fb2ff8)</blockquote></sub>
  <details>
  <summary>Commit description</summary>
  <p>Use separate normalized Seti language icon variants for desktop and mobile profile rendering, applying a 3px vertical shift on desktop while preserving the existing 2px shift on mobile.</p>
  </details>
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Add fallback language icon](https://github.com/Yusseter/Yusseter/commit/386b84d8c83acd818c42cf3da6489177f5199d27)<br>
  <sub><blockquote>Committed yesterday · [386b84d](https://github.com/Yusseter/Yusseter/commit/386b84d8c83acd818c42cf3da6489177f5199d27)</blockquote></sub>
  <details>
  <summary>Commit description</summary>
  <p>Add a theme-aware VS Code Seti default icon fallback for Building now language metadata when a matching Seti language icon is unavailable, while preserving the existing 20px sizing, text-top alignment, and 2.0px optical shift for supported language icons.</p>
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
