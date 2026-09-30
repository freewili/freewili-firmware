# v024-preview.1 - FreeWili OG audio playback fix

September 30, 2026 Preview for **FreeWili 1-OG (RP2040)**.

| Component | Embedded version | Delivery |
| --- | --- | --- |
| MAIN | 024 | `firmware/ogfw_main-024.uf2` |
| DISPLAY | 020 | Embedded in the MAIN UF2; installed through the OG display bootloader |

## Why this Preview exists

The Preview channel lists the newest `prerelease` package. v024 went directly
to Stable, which left Preview on the older `v023-preview.1`. This release
brings Preview up to date. Its MAIN UF2 is **byte-identical** to the Stable
[v024](https://github.com/freewili/freewili-firmware/releases/tag/v024)
image; only the release identity and notes differ.

## Changes

Same as v024:

- Fix choppy playback of built-in audio assets and generated tones when
  display rendering delays the main loop. These sounds now refill their
  audio buffers from DMA completion interrupts.
- Keep microphone capture on its separate DMA interrupt and preserve audio
  buffer capacity, volume controls, and tone behavior.

## Install

1. Download `ogfw_main-024.uf2` from this release, or extract
   `firmware/ogfw_main-024.uf2` from `FREE-WILi-OG-v024-preview.1.zip`.
2. Use [FreeWili OG App Explorer](https://github.com/freewili/fwOGAppExplorer/releases/latest).
   A board new to OG apps first needs **OG Bootloader Installer > Install
   FreeWili OG Bootloader**. That one-time conversion erases MAIN first;
   back up files before converting from deprecated firmware.
3. Put the UF2 in App Explorer's local `catalog/` folder, select it in the
   **App Explorer** tab, verify MAIN **024** and DISPLAY **020**, then
   **Flash** the intended board. Keep USB power connected until MAIN boots
   and the display update finishes.

This file targets MAIN; it already contains DISPLAY's application. This is
not FreeWili 2 firmware, and no bootloader image is included in this release.

MAIN UF2 SHA-256:
`48c3174b73fb392397325aa81f25d40ba5e662d308a86c1dd2664593f7378eb9`
(identical to v024).

## Validation and limitations

The image bytes are the ones validated for v024; see the
[v024 notes](https://github.com/freewili/freewili-firmware/releases/tag/v024)
for the hardware, audio and packaging checks and the known limitations.
Packaging checks were re-run for this release identity.
