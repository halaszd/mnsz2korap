PYTHON3 := .venv/bin/python3

# ----- create_venv: .venv könyvtár létrehozása
create_venv:
	rm -rf .venv
	python3 -m venv .venv
	./venv/bin/pip3 install -r requirements.txt
PHONY: create_venv

# ----- mnsz2korap: Az MNSZ2 NoSkE formátumban lévő XML-jeit átalakítja KorAP formátumra a test input alapján
test:
	$(PYTHON3) scripts/mnsz2korapxml.py inputs/noske_test/*.mxml -m inputs/xml_clean_test/\**/\*.xml -d MNSZ -c
PHONY: test

# ----- mnsz2korap: Az MNSZ2 NoSkE formátumban lévő XML-jeit átalakítja KorAP formátumra --> éles futtatás az oliphant-on.
mnsz2korapxml:
	$(PYTHON3) scripts/mnsz2korapxml.py /store/corpora/mnsz2_20180606-source/sources/* -m /store/share/projects/mnsz2/xml_clean/\**/\*.xml  -d /store/share/resources/corpora/MNSZ_korap -c
PHONY: mnsz2korapxml