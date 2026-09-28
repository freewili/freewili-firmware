# v024 - FreeWili OG audio playback fix

September 28, 2026 Stable release for **FreeWili 1-OG (RP2040)**.

| Component | Embedded version | Delivery |
| --- | --- | --- |
| MAIN | 024 | `firmware/ogfw_main-024.uf2` |
| DISPLAY | 020 | Embedded in the MAIN UF2; installed through the OG display bootloader |

## Changes

- Fix choppy playback of built-in audio assets and generated tones when
  display rendering delays the main loop. These sounds now refill their
  audio buffers from DMA completion interrupts.
- Keep microphone capture on its separate DMA interrupt and preserve audio
  buffer capacity, volume controls, and tone behavior.

This release includes the integration and memory changes shipped in
[v023](https://github.com/freewili/freewili-firmware/releases/tag/v023).

This is the exact image tested on September 28, packaged without rebuilding
or changing its bytes. It was built from a development working tree based on
revision `9a4f0f992c0e7420dfbe9c7e09568f5727bd618a`, with uncommitted integration
and audio changes, plus a modified BSP based on
`061000e3427d2b16cc1756e9e130dfbf5d40f839`. The base revisions alone are not
a reproducible source snapshot. This public repository distributes firmware
binaries; the manifest records the embedded build identity and image hashes.

## Install

1. Download `ogfw_main-024.uf2` from this release, or extract
   `firmware/ogfw_main-024.uf2` from `FREE-WILi-OG-v024.zip`.
2. Use [FreeWili OG App Explorer](https://github.com/freewili/fwOGAppExplorer/releases/latest).
   A board new to OG apps first needs **OG Bootloader Installer > Install
   FreeWili OG Bootloader**. That one-time conversion erases MAIN first;
   back up files before converting from deprecated firmware.
3. Put the UF2 in App Explorer's local `catalog/` folder, select it in the
   **App Explorer** tab, verify MAIN **024** and DISPLAY **020**, then
   **Flash** the intended board. Keep USB power connected until MAIN boots
   and the display update finishes.

Alternatively, inspect with `fwogcli info ogfw_main-024.uf2`, list boards
with `fwogcli list`, then use
`fwogcli flash ogfw_main-024.uf2 --cpu main --device <chip-id>`.

This file targets MAIN; it already contains DISPLAY's application. The
normal app update does not write the filesystem region. The separate
bootloader conversion above has different erase behavior. This is not
FreeWili 2 firmware, and no bootloader image is included in this release.

MAIN UF2 SHA-256:
`48c3174b73fb392397325aa81f25d40ba5e662d308a86c1dd2664593f7378eb9`.
The ZIP manifest records image sizes and hashes; release checksum files
also cover the downloadable ZIP and UF2.

## Validation and limitations

Recorded checks for these exact image bytes:

- MAIN **024** and DISPLAY **020** installed and booted on an OG board.
  All **108/108** reported MAIN flash CRC chunks matched the built image.
  MAIN reported DISPLAY's application updated; DISPLAY reported a working
  link, IO expander and LCD.
- **30 different short audio assets** played at three-second start intervals.
  All 30 commands succeeded and all 30 sounds completed. The listening tester
  confirmed the audio was good and approved this release.
- **4/4 microphone/tone smoke checks passed**, including microphone capture
  while playing an 880 Hz tone, and a clean stream stop.
- Both host audio test suites passed. The DMA regression reproduces the old
  failure without foreground polling and verifies correct sample order and
  completion with this fix. It also covers tone callbacks, file callback
  context, buffer tails, stop, and restart.
- Build-time identity checks passed for both CPUs. Release packaging checks
  every UF2 block, both embedded identities, embedded DISPLAY bytes, and
  manifest hashes. The MAIN image has **20,908 RP2040 UF2 blocks** below the
  filesystem boundary.

File-backed audio still requires regular foreground servicing. Interrupts
must not remain masked for longer than an audio buffer period. Sustained
playback during navigation and a broad peripheral regression were not tested.
The v023 script/capture pool reduction remains: the script portion is
**69,376 bytes**, with 8 KiB retained for logic-analyzer capture.
