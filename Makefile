# ----- mnsz2korap: Az MNSZ2 NoSkE formátumban lévő XML-jeit átalakítja KorAP formátumra a test input alapján
test:
	cd scripts; python3 mnsz2korapxml.py ../inputs/noske_test/*.mxml -m ../inputs/xml_clean_test/\**/\*.xml -d ../MNSZ -c

# ----- mnsz2korap: Az MNSZ2 NoSkE formátumban lévő XML-jeit átalakítja KorAP formátumra --> éles futtatás az oliphant-on.
mnsz2korapxml:
	cd scripts; python3 mnsz2korapxml.py /store/corpora/mnsz2_20180606-source/sources/* -m /store/share/projects/mnsz2/xml_clean/\**/\*.xml -c
