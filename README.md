# mnsz2korap

## About mnsz2korap

- It is a script which converts MNSZ NoSkE (for annotation) and clean (for metadata) XML files into [KorAP XML files](https://github.com/KorAP/KorAP-XML-Krill#about-korap-xml)

***

## Usage

```bash
python3 mnsz2korap.py <input NoSkE filepath> -m <XML clean root folder/\**/\*.xml> -d <output folder> -b <backup filepath> -c <start a new conversion>
```

- Example:
```bash
python3 mnsz2korap.py ../inputs/noske/*.mxml -m ../inputs/xml_clean/\**/\*.xml -d ../MNSZ -b ./backup.txt -c
```