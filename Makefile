# ----- mnsz2korap: Az MNSZ2 NoSkE formátumban lévő XML-jeit átalakítja KorAP formátumra
mnsz2korap_test:
	cd scripts; python3 mnsz2korap.py ../inputs/noske_test/*.mxml -m ../inputs/xml_clean_test/\**/\*.xml -d ../MNSZ

mnsz2korap:
	cd scripts; python3 mnsz2korap.py ../inputs/noske/*.mxml -m ../inputs/xml_clean/\**/\*.xml -d ../MNSZ