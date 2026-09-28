# FreeWili OG release format (schema 1)

This format follows the versioned-release layout used by FREE-WILi2, with an
OG-specific product identity and one combined MAIN UF2. It is not a FREE-WILi2
updater package. Install the extracted UF2 with FreeWili OG App Explorer.

## Identity and channels

The folder `releases/<release>/`, GitHub tag, manifest `release`, and archive
`FREE-WILi-OG-<release>.zip` share one identity, such as `v023-preview.1`.
Names start with `v` and a digit and contain only ASCII letters, digits,
periods and hyphens (at most 80 characters). Component versions are separate
three-digit strings read from the image's CRC-protected `FWGOINFO` records.

Preview means GitHub `prerelease: true`; Stable means `prerelease: false`.
Drafts are not published releases. Channel is release metadata, so a tested
Preview can be promoted without changing its tag or bytes. Corrections require
a new release identity; published files and tags must not be replaced.

## Files and manifest

The release folder and ZIP contain exactly `README.md`, `manifest.json` and
`firmware/ogfw_main-<main-version>.uf2`. All ZIP paths are relative, with no
wrapping directory, symlinks or unlisted files. ZIP uses DEFLATE with fixed
timestamps and permissions so packaging the same inputs is reproducible.

The UTF-8 manifest has `schema: 1`, `product: "FREE-WILi-OG"`, `release`,
`title`, and `files`. `files` contains exactly one record:

| Field | Meaning |
| --- | --- |
| `component` | `main` |
| `version` | Three-digit MAIN version, e.g. `023` |
| `file` | `firmware/ogfw_main-023.uf2` |
| `size` | UF2 file size in bytes |
| `sha256` | Lowercase SHA-256 of the complete UF2 |
| `embedded_display.version` | Three-digit DISPLAY version, e.g. `019` |
| `embedded_display.offset` | Byte offset in the reconstructed MAIN flash payload |
| `embedded_display.size` | Embedded DISPLAY binary length, without UF2 padding |
| `embedded_display.sha256` | SHA-256 of those embedded DISPLAY bytes |

Optional `source` provenance describes the build. A working-tree build must
be marked `dirty: true`; its base revision alone does not reproduce it.
See [the initial manifest](releases/v023-preview.1/manifest.json).

## Validation and installation

`scripts/package_release.py` checks every UF2 block: magic, 256-byte payload,
RP2040 family `0xe48bff56`, family-ID-only flags, unique complete block indices,
and contiguous addresses from `0x10000000` ending at or below `0x10c00000`.
This keeps the UF2 writes below the filesystem. MAIN and embedded DISPLAY must
each have exactly one valid application record named `ogfw`; their versions
must match the manifest. DISPLAY's record must fall inside the declared
embedded image, and its build fields must be empty as required by OG apps.
Manifest sizes, hashes, paths and release-file completeness are checked too.

These checks validate packaging and image identity, not full device behavior.
Release notes must identify the tests actually run and remaining limitations.

Release assets are the ZIP, `<zip>.sha256`, the standalone MAIN UF2, and
`checksums-<release>.txt` containing both download hashes. The standalone UF2
is byte-identical to its ZIP member. Use App Explorer to install it on MAIN;
MAIN transfers DISPLAY's application over the link. The OG display bootloader
is a prerequisite and is installed separately by App Explorer. Never install
this MAIN image directly on DISPLAY.
