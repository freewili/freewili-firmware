# v023 - FreeWili OG firmware release

September 28, 2026 Stable release for **FreeWili 1-OG (RP2040)**.

| Component | Embedded version | Delivery |
| --- | --- | --- |
| MAIN | 023 | `firmware/ogfw_main-023.uf2` |
| DISPLAY | 019 | Embedded in the MAIN UF2; installed through the OG display bootloader |

This is the current release, superseding the deprecated legacy `release_v73`.
Its MAIN and embedded DISPLAY firmware bytes are identical to `v023-preview.1`;
this Stable promotion changes release identity and documentation only.

## Changes

- Update OG integration with the current shared menu implementation.
  Commands requiring unsupported hardware or protocols report unsupported;
  existing raw USB CDC file transfers and top-level GUI button reads remain
  the supported paths.
- Reduce DISPLAY screenshot scratch memory by 1024 bytes while retaining
  the same complete screenshot output.
- Reduce MAIN's script/capture pool from 82 to 76 KiB to accommodate growth
  in shared menu and scripting state. The script portion is now **69,376
  bytes**; logic-analyzer capture retains 8 KiB. Larger scripts may need to
  be shortened to fit.
- Introduce versioned release bundles, manifests, SHA-256 downloads, and
  explicit Preview/Stable publishing, following the FreeWili 2 repository.

This is the exact image tested on September 28, packaged without rebuilding
or changing its bytes. It was built from a development working tree based on
revision `9a4f0f992c0e7420dfbe9c7e09568f5727bd618a`, including uncommitted
integration changes. Its embedded build is
`n-2026-09-04-24-g9a4f0f99-dirty`; the base revision alone is not a reproducible
source snapshot. This public repository distributes firmware binaries.

## Install

1. Download `ogfw_main-023.uf2` from this release, or extract
   `firmware/ogfw_main-023.uf2` from `FREE-WILi-OG-v023.zip`.
2. Use [FreeWili OG App Explorer](https://github.com/freewili/fwOGAppExplorer/releases/latest).
   A board new to OG apps first needs **OG Bootloader Installer > Install
   FreeWili OG Bootloader**. That one-time conversion erases MAIN first;
   back up files before converting from deprecated firmware.
3. Put the UF2 in App Explorer's local `catalog/` folder, select it in the
   **App Explorer** tab, verify MAIN **023** and DISPLAY **019**, then
   **Flash** the intended board. Keep USB power connected until MAIN boots
   and the display update finishes.

Alternatively, inspect with `fwogcli info ogfw_main-023.uf2`, list boards
with `fwogcli list`, then use
`fwogcli flash ogfw_main-023.uf2 --cpu main --device <chip-id>`.

This file targets MAIN; it already contains DISPLAY's application. The
normal app update does not write the filesystem region. The separate
bootloader conversion above has different erase behavior. This is not
FreeWili 2 firmware, and no bootloader image is included in this release.

MAIN UF2 SHA-256:
`4788cb39640c42b0af483b20d57df4ff51f1e2e5b801027c1838b71615ed3f20`.
The ZIP manifest records image sizes and hashes; release checksum files
also cover the downloadable ZIP and UF2.

## Validation and limitations

Recorded hardware checks for these exact image bytes:

- All **108/108** MAIN flash CRC chunks matched the built image; MAIN booted,
  mounted the existing filesystem, and reported DISPLAY's application updated.
- USB identified MAIN **023** and DISPLAY **019**. DISPLAY reported a working
  link, IO expander and LCD, no dropped events, and all **240** screenshot rows.
  The captured home screen was visually inspected.
- **Eight of eight** button/LED checks passed, including held/released button
  state, valid LED indices, flash mode, and invalid-index rejection.
- **21 menu settings probes** passed. Another 15 probes were for branches
  excluded from OG; the unfiltered FreeWili 2-oriented sweep exited with a
  failure and is not evidence of a complete passing OG regression suite.

Build-time image identity checks passed for both CPUs. Release packaging
checks every UF2 block, both embedded identities, the embedded DISPLAY bytes,
manifest hashes and reproducible archive output. The MAIN image has 20,906
RP2040 UF2 blocks below the filesystem boundary.

Large-script capacity was not hardware-tested; the 6 KiB pool reduction is a
real capacity change. No broad peripheral or radio-transmission test was
performed. These limitations also apply to this Stable release.
