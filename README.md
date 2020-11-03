# mnsz2korap

## About mnsz2korap

- It is a script which converts MNSZ NoSkE (for annotation) and clean (for metadata) XML files into [KorAP XML files](https://github.com/KorAP/KorAP-XML-Krill#about-korap-xml)

***
## Installation
1. `git clone https://github.com/halaszd/mnsz2korap.git`
2. `cd mnsz2korap; make create_venv`
## Usage
- Test: `make test`

- General usage 
```bash
./.venv/bin/python3 mnsz2korapxml.py <input NoSkE filepath> -m <XML clean root folder/\**/\*.xml> -d <output folder> -b <backup filepath> -c <start a new conversion>
```
- Example:
```bash
python3 mnsz2korapxml.py ../inputs/noske/*.mxml -m ../inputs/xml_clean/\**/\*.xml -d ../MNSZ -b ./backup.txt -c
```

- On oliphant.nytud: `make mnsz2korapxml`