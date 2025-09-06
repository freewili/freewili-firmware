Follow update instructions here:  https://docs.freewili.com/freewili-firmware-update/



Updating checksum file:
```bash
cd firmware
find . -name "*.uf2" -type f -exec sha256sum {} \; > checksums.txt
```
