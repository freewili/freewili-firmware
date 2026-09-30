# FreeWili OG firmware

Firmware releases for the original **FreeWili 1-OG (RP2040)**. Download from
[Releases](https://github.com/freewili/freewili-firmware/releases).
Each new release includes a versioned ZIP, manifest, release notes, SHA-256
checksums, and a standalone MAIN UF2 for installation with
[FreeWili OG App Explorer](https://github.com/freewili/fwOGAppExplorer).

## Current release: v024

**MAIN 024 / DISPLAY 020**, packaged from the September 28, 2026 tested build.
The single MAIN UF2 includes the matching DISPLAY application. It fixes choppy
playback of built-in audio assets and generated tones. A 30-asset listening
test passed; see the [full notes](releases/v024/README.md) for changes, hardware
checks, and limitations.

[Download the latest release](https://github.com/freewili/freewili-firmware/releases/latest).
**v024 is the current Stable release.** It supersedes v023 and includes its
shared menu integration and memory changes.
The Preview channel's current release, `v024-preview.1`, carries the same
MAIN 024 / DISPLAY 020 bytes.

**`release_v73` is deprecated legacy firmware.** Its version numbering belongs
to the old firmware line; it is not newer than OG 024. Use v024 for current
FreeWili OG installations. Legacy downloads remain available for historical
recovery only.

## Install

1. Download the release's `ogfw_main-024.uf2`, or extract it from the ZIP's
   `firmware/` folder. The ZIP itself is not an installable UF2.
2. Open [FreeWili OG App Explorer](https://github.com/freewili/fwOGAppExplorer/releases/latest).
   If this board has never run OG apps, use **OG Bootloader Installer >
   Install FreeWili OG Bootloader** once. This installation erases MAIN first;
   back up files before converting a board from the deprecated firmware.
3. Place the downloaded UF2 in App Explorer's local `catalog/` folder, select
   it in **App Explorer**, check MAIN **024** / DISPLAY **020**, and press
   **Flash**. Select the intended board if more than one is connected.
4. Keep USB power connected until MAIN restarts and finishes updating DISPLAY.

The included command-line tool can also inspect and install the file:

```text
fwogcli info ogfw_main-024.uf2
fwogcli list
fwogcli flash ogfw_main-024.uf2 --cpu main --device <chip-id>
```

Install this UF2 on **MAIN**. DISPLAY's matching application is embedded in it
and is transferred through the OG display bootloader. App Explorer identifies
the correct CPU. FreeWili 2 uses [separate firmware](https://github.com/freewili/FREE-WILi2-Firmware).

The release channels describe GitHub release metadata. App Explorer installs
the downloaded UF2; this repository change does not add a channel picker or
automatically update its remote app catalog.

## Release layout and publishing

Each immutable `releases/<version>/` folder contains:

```text
manifest.json
README.md
firmware/ogfw_main-024.uf2
```

The ZIP contains those files at its root. The manifest records MAIN's version,
size and SHA-256, plus the version, location, size and hash of the embedded
DISPLAY image. See [RELEASE_FORMAT.md](RELEASE_FORMAT.md) for the full contract.

To publish a new release:

1. Add a new release folder containing a tested combined MAIN image, manifest,
   and release notes. Use the actual embedded versions and a new bundle name.
2. Validate and package it:
   ```sh
   python -m unittest discover -s scripts -p 'test_*.py'
   python scripts/package_release.py releases/v024
   ```
3. Open a pull request and merge after validation passes. Never push directly
   to `main`.
4. Run **Actions > Publish firmware release** on the merged commit, enter the
   folder version, and choose **preview** (default) or **stable**. The workflow
   uploads the ZIP, ZIP checksum, standalone UF2 and checksum list to a draft
   before publishing it. Existing tags/releases are never overwritten.
5. Download the published assets and verify their hashes before installation.
   Record hardware testing before promoting a Preview to Stable.

The root `ogfw_mainV21.uf2`, `Legacy/`, and older releases remain available as
historical downloads. New releases live in their versioned folders and GitHub
Release assets; the old root file is not the current release.
