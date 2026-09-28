"""Exercise damaged/wrong-target images and the actual release packaging."""
import copy
import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
import zipfile

from package_release import image_records, package, sha256, uf2_payload, validate


RELEASE = Path(__file__).resolve().parents[1] / 'releases' / 'v023-preview.1'


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.files = validate(RELEASE)
        cls.name = cls.manifest['files'][0]['file']
        cls.uf2 = cls.files[cls.name]

    def test_real_image_identities(self):
        records = image_records(uf2_payload(self.uf2))
        self.assertEqual(records[1]['version'], '023')
        self.assertEqual(records[0]['version'], '019')

    def test_bad_uf2_blocks(self):
        # Header damage, foreign family, dangerous flags, duplicates, gaps,
        # wrong block totals, writes into the filesystem and partial blocks.
        edits = [(0, 0), (28, 0xE48BFF59), (8, 0x2001), (16, 128),
                 (512 + 20, 0), (12, 0x10000100), (24, 1), (12, 0x10C00000),
                 (508, 0)]
        for offset, value in edits:
            with self.subTest(offset=offset, value=value):
                bad = bytearray(self.uf2)
                struct.pack_into('<I', bad, offset, value)
                with self.assertRaises(ValueError):
                    uf2_payload(bad)
        for bad in (b'', self.uf2[:-1], self.uf2[:-512]):
            with self.assertRaises(ValueError):
                uf2_payload(bad)

    def test_reordered_uf2_blocks(self):
        swapped = self.uf2[512:1024] + self.uf2[:512] + self.uf2[1024:]
        self.assertEqual(uf2_payload(swapped), uf2_payload(self.uf2))

    def test_identity_crc(self):
        bad = bytearray(uf2_payload(self.uf2))
        bad[bad.index(b'FWGOINFO') + 12] ^= 1
        with self.assertRaisesRegex(ValueError, 'CRC'):
            image_records(bad)

    def test_manifest_and_file_failures(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / RELEASE.name
            shutil.copytree(RELEASE, folder)
            original = copy.deepcopy(self.manifest)
            for label in ('main_version', 'display_version', 'display_hash',
                          'display_range', 'main_hash', 'main_size', 'path',
                          'duplicate', 'product'):
                with self.subTest(label=label):
                    m = copy.deepcopy(original)
                    entry = m['files'][0]
                    if label == 'main_version': entry['version'] = '024'
                    if label == 'display_version': entry['embedded_display']['version'] = '020'
                    if label == 'display_hash': entry['embedded_display']['sha256'] = '0' * 64
                    if label == 'display_range': entry['embedded_display']['offset'] = -1
                    if label == 'main_hash': entry['sha256'] = '0' * 64
                    if label == 'main_size': entry['size'] -= 1
                    if label == 'path': entry['file'] = '../../outside.uf2'
                    if label == 'duplicate': m['files'].append(copy.deepcopy(entry))
                    if label == 'product': m['product'] = 'FREE-WILi2'
                    (folder / 'manifest.json').write_text(json.dumps(m), encoding='utf-8')
                    with self.assertRaises(ValueError): validate(folder)
            (folder / 'manifest.json').write_bytes(self.files['manifest.json'])
            (folder / 'extra.uf2').write_bytes(b'extra')
            with self.assertRaisesRegex(ValueError, 'unlisted'): validate(folder)
            (folder / 'extra.uf2').unlink()
            (folder / 'README.md').write_bytes(b'')
            with self.assertRaisesRegex(ValueError, 'notes'): validate(folder)

    def test_archive_is_reproducible_and_preserves_image(self):
        with tempfile.TemporaryDirectory() as temp:
            first = package(RELEASE, Path(temp) / 'first')
            second = package(RELEASE, Path(temp) / 'second')
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                self.assertIsNone(archive.testzip())
                self.assertEqual(set(archive.namelist()), set(self.files))
                self.assertEqual(archive.read(self.name), self.uf2)
            self.assertEqual(first.with_suffix('.zip.sha256').read_text().split()[0], sha256(first.read_bytes()))
            checksums = (first.parent / f'checksums-{RELEASE.name}.txt').read_text()
            self.assertIn(sha256(self.uf2), checksums)


if __name__ == '__main__':
    unittest.main()
