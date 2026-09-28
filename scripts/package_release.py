#!/usr/bin/env python3
"""Validate and package a versioned FreeWili OG combined MAIN/DISPLAY release."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import zipfile
import zlib


FLASH_START = 0x10000000
FILESYSTEM_START = 0x10C00000
INFO = struct.Struct('<8sHBBHH32s128s32sII')


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def uf2_payload(data):
    if not data or len(data) % 512 or len(data) > 24 * 1024 * 1024:
        raise ValueError('Invalid UF2 length')
    count = len(data) // 512
    blocks = {}
    for pos in range(0, len(data), 512):
        block = data[pos:pos + 512]
        magic0, magic1, flags, address, size, index, total, family = struct.unpack_from('<8I', block)
        if (magic0, magic1, struct.unpack_from('<I', block, 508)[0]) != (0x0A324655, 0x9E5D5157, 0x0AB16F30):
            raise ValueError('Invalid UF2 magic')
        if flags != 0x2000 or family != 0xE48BFF56 or size != 256:
            raise ValueError('Expected RP2040 flash UF2 with 256-byte payloads')
        if total != count or index >= count or index in blocks:
            raise ValueError('Incomplete or duplicate UF2 blocks')
        if address != FLASH_START + index * 256 or address + size > FILESYSTEM_START:
            raise ValueError('UF2 must be contiguous MAIN flash below the filesystem')
        blocks[index] = block[32:288]
    return b''.join(blocks[i] for i in range(count))


def image_records(payload):
    records = {}
    start = 0
    while True:
        offset = payload.find(b'FWGOINFO', start)
        if offset < 0:
            break
        start = offset + 1
        raw = payload[offset:offset + INFO.size]
        if len(raw) != INFO.size:
            raise ValueError('Truncated OG identity record')
        magic, schema, cpu, kind, version, reserved, name, desc, build, timestamp, crc = INFO.unpack(raw)
        if zlib.crc32(raw[:-4]) & 0xFFFFFFFF != crc:
            raise ValueError('OG identity CRC mismatch')
        if schema != 1 or cpu not in (0, 1) or kind != 0 or reserved or version > 999:
            raise ValueError('Invalid OG application identity')
        strings = []
        for field in (name, desc, build):
            if b'\0' not in field:
                raise ValueError('Unterminated OG identity string')
            strings.append(field.split(b'\0', 1)[0].decode('ascii'))
        if strings[0] != 'ogfw' or not strings[1] or cpu in records:
            raise ValueError('Wrong or duplicate OG application identity')
        if cpu == 0 and (strings[2] or timestamp):
            raise ValueError('DISPLAY application must have empty build fields')
        records[cpu] = {'version': f'{version:03d}', 'offset': offset}
    return records


def validate(folder):
    if folder.is_symlink() or any(p.is_symlink() for p in folder.rglob('*')):
        raise ValueError('Symlinks are not release files')
    manifest_data = (folder / 'manifest.json').read_bytes()
    notes = (folder / 'README.md').read_bytes()
    if not notes.strip() or len(notes) > 65536 or len(manifest_data) > 65536:
        raise ValueError('Missing notes or oversized release metadata')
    notes.decode('utf-8')
    manifest = json.loads(manifest_data.decode('utf-8'))
    release = manifest['release']
    if not re.fullmatch(r'v[0-9][A-Za-z0-9.-]{0,78}', release) or release != folder.name:
        raise ValueError('Release name must match its folder')
    if type(manifest['schema']) is not int or manifest['schema'] != 1 or manifest['product'] != 'FREE-WILi-OG':
        raise ValueError('Unsupported release manifest')
    if not isinstance(manifest['title'], str) or not manifest['title'].strip():
        raise ValueError('Release title is required')
    if len(manifest['files']) != 1:
        raise ValueError('Release needs exactly one combined MAIN UF2')
    entry = manifest['files'][0]
    version = entry['version']
    if entry['component'] != 'main' or not re.fullmatch(r'[0-9]{3}', version):
        raise ValueError('Expected MAIN with a three-digit version')
    name = f'firmware/ogfw_main-{version}.uf2'
    if entry['file'] != name:
        raise ValueError('UF2 filename does not match MAIN version')
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
    if actual != {'manifest.json', 'README.md', name}:
        raise ValueError('Missing or unlisted release files')
    data = (folder / name).read_bytes()
    if type(entry['size']) is not int or len(data) != entry['size'] or sha256(data) != entry['sha256']:
        raise ValueError('MAIN size or SHA-256 mismatch')
    payload = uf2_payload(data)
    records = image_records(payload)
    if set(records) != {0, 1} or records[1]['version'] != version:
        raise ValueError('Expected matching MAIN and embedded DISPLAY identities')
    display = entry['embedded_display']
    if records[0]['version'] != display['version']:
        raise ValueError('Embedded DISPLAY version mismatch')
    offset, size = display['offset'], display['size']
    if type(offset) is not int or type(size) is not int or offset < 0 or size <= 0 or offset + size > len(payload):
        raise ValueError('Embedded DISPLAY range is invalid')
    embedded = payload[offset:offset + size]
    if sha256(embedded) != display['sha256']:
        raise ValueError('Embedded DISPLAY SHA-256 mismatch')
    embedded_records = image_records(embedded)
    if set(embedded_records) != {0} or embedded_records[0]['offset'] + offset != records[0]['offset']:
        raise ValueError('Embedded DISPLAY range does not contain its application identity')
    return manifest, {'manifest.json': manifest_data, 'README.md': notes, name: data}


def package(folder, output):
    manifest, files = validate(folder)
    output.mkdir(parents=True, exist_ok=True)
    release = manifest['release']
    archive = output / f'FREE-WILi-OG-{release}.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=False) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data, compresslevel=9)
    checksum = sha256(archive.read_bytes())
    checksum_line = f'{checksum}  {archive.name}\n'
    archive.with_suffix('.zip.sha256').write_bytes(checksum_line.encode('ascii'))
    entry = manifest['files'][0]
    uf2_line = f"{entry['sha256']}  {Path(entry['file']).name}\n"
    (output / f'checksums-{release}.txt').write_bytes((checksum_line + uf2_line).encode('ascii'))
    print(f'{archive}: {archive.stat().st_size} bytes, SHA-256 {checksum}')
    return archive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('release', help='Release folder, e.g. releases/v023-preview.1')
    parser.add_argument('--output', default='dist')
    args = parser.parse_args()
    try:
        package(Path(args.release), Path(args.output))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f'Invalid release: {error}\n')
