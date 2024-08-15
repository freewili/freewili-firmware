Follow update instructions here:  https://docs.freewili.com/freewili-firmware-update/



Updating checksum file:
```bash
cd firmware
find . -type f -exec sha256sum {} > checksums.txt \;
```
