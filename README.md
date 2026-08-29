<!-- markdownlint-disable MD013 MD033 MD041 -->

<p align="center">
  <picture>
    <source media="(max-width: 600px)" srcset="./assets/profile/header-mobile.svg">
    <img src="./assets/profile/header.svg" width="100%" alt="Yusseter profile header">
  </picture>
</p>

## Building now

<!-- building_now:start -->
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — Windhawk mod for preserving Windows 11 notification-area icon order while allowing user-controlled reordering.<br>
  <sub><blockquote>Updated <relative-time datetime="2026-08-28T12:31:30Z">Aug 28, 2026</relative-time> · <picture><source media="(max-width: 600px)" srcset="./assets/profile/languages/cpp-mobile.svg"><img src="./assets/profile/languages/cpp.svg" alt="" height="20" align="texttop"></picture>C++</blockquote></sub>
<!-- building_now:end -->

## Recent commits

<!-- recent_commits:start -->
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Polish profile header SVG layout and styling](https://github.com/Yusseter/Yusseter/commit/5aa0fffdb434823c4aee071c6d06a288d50a7ae8)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-08-29T16:45:04Z">Aug 29, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 5aa0fff](https://github.com/Yusseter/Yusseter/commit/5aa0fffdb434823c4aee071c6d06a288d50a7ae8)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Updated the README header image to use full-width rendering and refreshed both profile header SVGs with a rounded frame, theme-aware border stroke, and gold gradient accent rules. Also adjusted rule positions and artwork transforms to improve visual balance and consistency across desktop and mobile variants.</p>
  </details>
- [**Yusseter**](https://github.com/Yusseter/Yusseter) — [Add responsive profile header SVGs](https://github.com/Yusseter/Yusseter/commit/67469a04af440341ba12fe71a98b9c422f2134cd)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-08-29T08:43:44Z">Aug 29, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 67469a0](https://github.com/Yusseter/Yusseter/commit/67469a04af440341ba12fe71a98b9c422f2134cd)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Use a `&lt;picture&gt;` block in README to serve a dedicated mobile header on small screens while keeping the desktop SVG as the default. Refine both header variants with improved proportions, geometric precision rendering, stronger rule strokes, and adjusted emblem positioning for cleaner scaling and alignment.</p>
  </details>
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — [Document 0.2.0 and reorganize research](https://github.com/Yusseter/tray-order-lock/commit/2e167faf4752085bacae5f42c61308a4e247014f)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-08-28T12:31:30Z">Aug 28, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 2e167fa](https://github.com/Yusseter/tray-order-lock/commit/2e167faf4752085bacae5f42c61308a4e247014f)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>This update refreshes the project docs for the 0.2.0 release, including the new Preserve order mode, installation settings, validation notes, and repository layout. It also moves the analyzer and experiment sources under research/ to clarify the production mod versus historical research work, and updates the project homepage URLs to the repo&#x27;s current name.</p>
  </details>
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — [Document 0.2.0 tray ordering features](https://github.com/Yusseter/tray-order-lock/commit/22536d765b5f466753e68d2ec4ad9cf996dbe77e)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-08-28T11:24:17Z">Aug 28, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 22536d7](https://github.com/Yusseter/tray-order-lock/commit/22536d765b5f466753e68d2ec4ad9cf996dbe77e)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Update the project banner text to reflect the completed 0.2.0 release notes. This change describes the new persistent manual ordering support and automatic restoration of known tray icons, while keeping the original lock-all-reordering behavior from 0.1.0.</p>
  </details>
- [**tray-order-lock**](https://github.com/Yusseter/tray-order-lock) — [Add new icon placement option](https://github.com/Yusseter/tray-order-lock/commit/73b2e32227358c1bf2e1645edf9eb396a90dbf3e)<br>
  <sub><blockquote>Committed <relative-time datetime="2026-08-28T11:09:09Z">Aug 28, 2026</relative-time> · [<img src="./assets/profile/git-commit.svg" alt="" height="18" align="texttop"> 73b2e32](https://github.com/Yusseter/tray-order-lock/commit/73b2e32227358c1bf2e1645edf9eb396a90dbf3e)</blockquote></sub>
  <details>
  <summary>Details</summary>
  <p>Introduce a new setting &#x27;newIconBehavior&#x27; with options &#x27;windowsDefault&#x27; and &#x27;placeAtEnd&#x27;. Add the NewIconBehavior enum and g_newIconBehavior storage, and implement handling for newly discovered tray icons through AppendNewCanonicalKeyAtEnd, AdoptNewIconAtWindowsDefault, AdoptNewIconFromUiOrder and HandleNewIcon. When configured for place-at-end, the mod moves the new icon to the end of the overflow, verifies the resulting position and persists it in the canonical order; otherwise it adopts Windows&#x27; current placement, using UIOrder state as a fallback when live overflow neighbors are unavailable. LoadSettings now reads and logs the new setting, and RestoreCanonicalRelation delegates new-icon handling to HandleNewIcon.</p>
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
