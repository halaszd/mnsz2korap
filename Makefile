PYTHON3 := .venv/bin/python3
INPUT_FOLDER_NOSKE := /store/corpora/mnsz2_20180606-source/sources
INPUT_CLEAN_XMLS := /store/share/projects/mnsz2/xml_clean/\**/\*.xml

# ----- create_venv: .venv könyvtár létrehozása
create_venv:
	rm -rf .venv
	python3 -m venv .venv
	./.venv/bin/pip3 install -r requirements.txt
PHONY: create_venv

# ----- mnsz2korap: Az MNSZ2 NoSkE formátumban lévő XML-jeit átalakítja KorAP formátumra a test input alapján
test:
	$(PYTHON3) scripts/mnsz2korapxml.py inputs/noske_test/*.mxml -m inputs/xml_clean_test/\**/\*.xml -d test_MNSZ_KorAP -c
PHONY: test

# ----- mnsz2korap: Az MNSZ2 NoSkE formátumban lévő XML-jeit átalakítja KorAP formátumra --> éles futtatás az oliphant-on.
mnsz2korapxml:
	$(PYTHON3) scripts/mnsz2korapxml.py $(INPUT_FOLDER_NOSKE)/* -m $(INPUT_CLEAN_XMLS)  -d MNSZ_KorAP -c
PHONY: mnsz2korapxml

# ----- Az MNSZ2 átkonvertálása alkorpusz fajtánként. A -c kapcsoló nélkül, mert egymásra épülnek a futtatások.
mnsz2korapxml_lit:
	$(PYTHON3) scripts/mnsz2korapxml.py $(INPUT_FOLDER_NOSKE)/source.lit_*.mxml -m $(INPUT_CLEAN_XMLS)  -d MNSZ_KorAP
PHONY: mnsz2korapxml_lit

mnsz2korapxml_off:
	$(PYTHON3) scripts/mnsz2korapxml.py $(INPUT_FOLDER_NOSKE)/source.off_*.mxml -m $(INPUT_CLEAN_XMLS)  -d MNSZ_KorAP
PHONY: mnsz2korapxml_off

mnsz2korapxml_pers:
	$(PYTHON3) scripts/mnsz2korapxml.py $(INPUT_FOLDER_NOSKE)/source.pers_*.mxml -m $(INPUT_CLEAN_XMLS)  -d MNSZ_KorAP
PHONY: mnsz2korapxml_pers

mnsz2korapxml_press:
	$(PYTHON3) scripts/mnsz2korapxml.py $(INPUT_FOLDER_NOSKE)/source.press_*.mxml -m $(INPUT_CLEAN_XMLS)  -d MNSZ_KorAP
PHONY: mnsz2korapxml_press

mnsz2korapxml_sci:
	$(PYTHON3) scripts/mnsz2korapxml.py $(INPUT_FOLDER_NOSKE)/source.sci_*.mxml -m $(INPUT_CLEAN_XMLS)  -d MNSZ_KorAP
PHONY: mnsz2korapxml_sci

mnsz2korapxml_spok:
	$(PYTHON3) scripts/mnsz2korapxml.py $(INPUT_FOLDER_NOSKE)/source.spok_*.mxml -m $(INPUT_CLEAN_XMLS)  -d MNSZ_KorAP
PHONY: mnsz2korapxml_spok
