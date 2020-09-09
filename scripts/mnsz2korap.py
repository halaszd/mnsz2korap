#! /usr/bin/env python3

from bs4 import BeautifulSoup
import os
import argparse
from glob import iglob
import re

# 11 oszlop van. (TSV)
#
# 1 word        szóalak
# 2 lemma       szótő
# 3 msd         morfoszintaktikai leírás
# 4 ctag        (figyelmen kívül hagyandó)
# 5 ana         részletes morfológiai elemzés
# 6 word_cv     szóalak CV-váza
# 7 word_syll   szóalak szótagszáma
# 8 lemma_cv    szótő CV-váza
# 9 lemma_syll  szótő szótagszáma
# 10 word_phon   szóalak fonetikai reprezentációja
# 11 lemma_phon  szótő fonetikai reprezentációja


ANNOTATION_TYPES_ORDERED = (
    'word',
    'lemma',
    'pos',
    'ctag',
    'ana',
    'word_cv',
    'word_syll',
    'lemma_cv',
    'lemma_syll',
    'word_phon',
    'lemma_phon')

OPTS = (
    'header',
    'data',
    'sentences',
    'paragraphs',
    'word',
    'lemma',
    'pos',
    'ana',
    'word_cv',
    'word_syll',
    'lemma_cv',
    'lemma_syll',
    'word_phon',
    'lemma_phon')

OPT_DICT = {'header': (None, 'header', ''),
            'data': (None, 'data', ''),
            'sentences': (None, 'sentences', 'base'),
            'paragraphs': (None, 'paragraphs', 'base'),
            'word': (None, 'tokens', 'noske'),
            'lemma': (('lemma',), 'lemmas', 'noske'),
            'pos': (('word', 'lemma', 'pos'), 'part-of-speech', 'noske'),
            'ana': (('lemma', 'pos', 'ana'), 'morpho', 'noske'),
            'word_cv': (('word', 'word_cv'), 'word_cv', 'noske'),
            'word_syll': (('word', 'word_syll'), 'word_syll', 'noske'),
            'lemma_cv': (('lemma', 'lemma_cv'), 'lemma_cv', 'noske'),
            'lemma_syll': (('lemma', 'lemma_syll'), 'lemma_syll', 'noske'),
            'word_phon': (('word', 'word_phon'), 'word_phon', 'noske'),
            'lemma_phon': (('lemma', 'lemma_phon'), 'lemma_phon', 'noske')}

PAT_CUT_SPACE = re.compile(r' ?NoSpace ?')

STOPS = ('SSTOP', 'PSTOP')

BASE = ('paragraphs', 'sentences', 'header', 'data')

FS_ATTRS = {'type': 'lex', 'xmlns': 'http://www.tei-c.org/ns/1.0'}

F2_ATTRS = {'name': 'lex'}

F4_ATTRS = {'name': ''}

ANNOT_SPAN_ATTRS = {'id': '',
                    'from': '',
                    'to': ''}

BASE_SPAN_ATTRS = {'from': '', 'to': ''}

LAYER_ATTRS = {'docid': '',
               'xmlns': 'http://ids-mannheim.de/ns/KorAP',
               'version': 'KorAP-0.4'}

RAW_TEXT_ATTRS = {'docid': '',
                  'xmlns': 'http://ids-mannheim.de/ns/KorAP'}

PAT_CES_HEADER = re.compile(r'<cesHeader.+?(</cesHeader>)', re.DOTALL | re.MULTILINE)


def read(files):
    for fl in files:
        with open(fl, encoding="iso-8859-2") as f:
            yield os.path.basename(fl), f.read()


def gen_header_xml(header_type, corpora_dir=None, parent_dir=None, clean_xml=None, div=None, docid=None):
    """

    :param docid:
    :param div:
    :param parent_dir:
    :param corpora_dir:
    :param clean_xml:
    :param header_type:

    options: 1. 'corpus_header'
             2. '2nd_level_header': header of a complete XML
             3. '3rd_level_header': header of part of the XML
    :return:
    """
    if header_type == '2nd_level_header':
        ces_header = PAT_CES_HEADER.search(clean_xml)
        os.makedirs(os.path.join(corpora_dir, parent_dir), exist_ok=True)

        with open(os.path.join(corpora_dir, parent_dir, 'header.xml'), 'w', encoding='utf-8') as outpf:
            print('<?xml version="1.0" encoding="UTF-8"?>',
                  '<?xml-model href="header.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>',
                  '<!DOCTYPE idsCorpus PUBLIC "-//IDS//DTD IDS-XCES 1.0//EN" "http://corpora.ids-mannheim.de/idsxces1/DTD/ids.xcesdoc.dtd">',
                  ces_header.group().replace('cesHeader', 'idsHeader'), sep='\n', file=outpf)
        return

    soup = BeautifulSoup(
        '<?xml-model href="header.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>'
        '<!DOCTYPE idsCorpus PUBLIC "-//IDS//DTD IDS-XCES 1.0//EN" "http://corpora.ids-mannheim.de/idsxces1/DTD/ids.xcesdoc.dtd">',
        features='lxml')

    if header_type == '3rd_level_header':
        ids_header = soup.new_tag('idsHeader', attrs={'type': 'text'})  # parent: soup
        soup.append(ids_header)
        file_desc = soup.new_tag('fileDesc')  # parent: ids_header
        ids_header.append(file_desc)
        title_stmt = soup.new_tag('titleStmt')  # parent: file_desc
        file_desc.append(title_stmt)
        text_sigle = soup.new_tag('textSigle')  # parent: title_stmt, string = DOC00001.00001
        title_stmt.append(text_sigle)
        text_sigle.string = docid
        t_title = soup.new_tag('t.title')  # parent: title_stmt, string = title
        title_stmt.append(t_title)

        content = div.find('head')
        if content:
            t_title.string = content.text

        publication_stmt = soup.new_tag('publicationStmt')  # parent: file_desc
        file_desc.append(publication_stmt)
        source_desc = soup.new_tag('sourceDesc')  # parent: file_desc
        file_desc.append(source_desc)
        bibl_struct = soup.new_tag('biblStruct')  # parent: source_desc
        source_desc.append(bibl_struct)
        analytic = soup.new_tag('analytic')  # parent: bibl_struct
        bibl_struct.append(analytic)
        h_author = soup.new_tag('h.author')  # parent: analytic, string = author
        analytic.append(h_author)

        # <docAuthor>Addbot</docAuthor>
        content = div.find('docauthor')
        if content:
            h_author.string = content.text

        encoding_desc = soup.new_tag('encodingDesc')  # parent: idsHeader
        ids_header.append(encoding_desc)
        profile_desc = soup.new_tag('profilDesc')  # parent: idsHeader
        ids_header.append(profile_desc)
        creation = soup.new_tag('creation')  # parent: profileDesc
        profile_desc.append(creation)
        creat_date = soup.new_tag('creatDate')  # parent: creation, string = date
        creation.append(creat_date)

        # <date ISO8601="2013-03-02T14:36:02Z"></date>
        content = div.find('date')
        if content:
            creat_date.string = content['iso8601']

    return soup


def gen_data_xml(data, parent_id, child_id):
    soup = BeautifulSoup(
        '<?xml-model href="span.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>',
        features='lxml')
    txt = soup.new_tag('text')
    txt.string = data
    meta = soup.new_tag('metadata', file='metadata.xml')
    RAW_TEXT_ATTRS['docid'] = f'{parent_id}.{child_id}'
    raw_text = soup.new_tag('raw_text', attrs=RAW_TEXT_ATTRS)
    raw_text.append(meta)
    raw_text.append(txt)
    soup.append(raw_text)
    return soup


def gen_annotated_xml(annot_types, fname, annotations_per_line, opt):
    soup = BeautifulSoup(
        '<?xml-model href="span.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>',
        features='lxml')
    from_index_sp = 0
    from_index = 0
    to_index = 0
    iden = 0
    LAYER_ATTRS['docid'] = fname
    soup.append(soup.new_tag('layer', attrs=LAYER_ATTRS))
    span_list = soup.new_tag('spanList')

    for i, (is_space, word) in enumerate(annotations_per_line):

        if i != 0 and annotations_per_line[i - 1][1] not in STOPS and not is_space:
            from_index -= 1

        if word == 'SSTOP' or word == 'PSTOP':
            if (word == 'SSTOP' and opt == 'sentences') or (word == 'PSTOP' and opt == 'paragraphs'):
                BASE_SPAN_ATTRS['from'] = f'{from_index_sp}'
                BASE_SPAN_ATTRS['to'] = f'{to_index}'
                span = soup.new_tag('span', attrs=BASE_SPAN_ATTRS)
                span_list.append(span)
                from_index_sp = to_index + 1
            continue

        to_index = from_index + len(word['word'])

        # tag+number --> lowest the number the higher in hierarchy it is.
        if opt not in BASE:
            ANNOT_SPAN_ATTRS['id'] = f's{iden}'
            ANNOT_SPAN_ATTRS['from'] = f'{from_index}'
            ANNOT_SPAN_ATTRS['to'] = f'{to_index}'
            span = soup.new_tag('span', attrs=ANNOT_SPAN_ATTRS)

            if annot_types:
                # 1. szint
                fs1 = soup.new_tag('fs', attrs=FS_ATTRS)
                # 2. szint
                f2 = soup.new_tag('f', attrs=F2_ATTRS)
                # 3. szint
                fs3 = soup.new_tag('fs')

                for annot in annot_types:
                    # 4.szint: bármennyi következhet egymásután
                    F4_ATTRS['name'] = annot
                    f4 = soup.new_tag('f', attrs=F4_ATTRS)
                    f4.string = word[annot]
                    fs3.append(f4)

                span.append(fs1)
                fs1.append(f2)
                f2.append(fs3)
            span_list.append(span)

        from_index = to_index + 1
        iden += 1
    soup.layer.append(span_list)

    return soup


def gen_xml(meta_dict, opt):
    """
    gen. options:
        - header: metadata XML of analyzed text
        - data: XML of raw text
        -(sentences: XML of boundaries of sentences
        - paragraphs): XML of boundaries of paragraphs
        - word: XML of boundaries of words
        - lemma: XML of lemmas
        - pos: XML of lemmas + pos (msd)
        - ana: XML of lemmas + pos (msd) + ana
        - word_cv: XML of lemmas + word_cv
        - word_syll: XML of lemmas + word_syll
        - lemma_cv: XML of lemmas + lemma_cv
        - lemma_syll: XML of lemmas + lemma_syll
        - word_phon: XML of lemmas + word_phon
        - lemma_phon: XML of lemmas + lemma_phon
    """
    output_xmlname = OPT_DICT[opt][1]
    annot_folder = OPT_DICT[opt][2]

    if opt == 'header':
        output_xml = gen_header_xml(
            '3rd_level_header',
            docid=f'{meta_dict["parent_folder_name"]}.{meta_dict["child_folder_name"]}',
            div=meta_dict['clean_div'])

    elif opt == 'data':
        output_xml = gen_data_xml(meta_dict['data'], meta_dict['parent_folder_name'],
                                  meta_dict['child_folder_name'])

    else:
        output_xml = gen_annotated_xml(OPT_DICT[opt][0], meta_dict['fname_wo_ext'],
                                       meta_dict['annotations_per_line'], opt)

    return {'output_xml': output_xml, 'output_xmlname': output_xmlname, 'annot_folder': annot_folder}


def gen_docname(num_of_doc, i):
    num_of_doc = f'{num_of_doc[0:-len(str(i))]}{i}'
    return num_of_doc


def get_data(div):
    data = []
    txt = div.text
    for line in txt.split('\n'):
        line = line.strip()
        if line != '':
            if line == '###NOSPACE###':
                data.append('NoSpace')
            else:
                data.append(line.split('\t')[0])

    return PAT_CUT_SPACE.sub('', ' '.join(data))


def get_meta_file_path(clean_inps, fname_wo_ext):
    clean_xml = ''

    for meta_file_path, meta_file_fname in clean_inps:
        # NoSkE vs. clean megfeleltetés
        if fname_wo_ext == meta_file_fname[:-4]:
            clean_xml = open(os.path.join(meta_file_path, meta_file_fname), encoding='iso-8859-2').read()
            clean_xml = clean_xml.replace('<poem>', '</div>\n<div>')

    return clean_xml


def teszt_write_out(dirname, fname, txt):
    os.makedirs(dirname, exist_ok=True)
    with open(os.path.join(dirname, f'{fname}.xml'), 'w', encoding='utf-8') as f:
        print(txt.replace(
            '<g/>', '###NOSPACE###').replace(
            '<poem>', '</div>\n<div>').replace('</poem>', '').replace('<div>\n</div>', ''), file=f)


def get_annotations_with_paragraph(tag_to_iterate, annotations_per_line):
    for p_tag in tag_to_iterate.find_all('p'):
        get_annotatons_with_sentence(p_tag, annotations_per_line)


def get_annotatons_with_sentence(tag_to_iterate, annotations_per_line):
    for s_tag in tag_to_iterate.find_all('s'):
        is_space = True
        txt = s_tag.text.strip().split('\n')

        for line in txt:
            line = line.strip()

            if line == '':
                continue

            if line == '###NOSPACE###':
                is_space = False
                continue

            annotations = {}
            annotation_count = 0

            for k, annotation_type in enumerate(line.split('\t')):
                annotation_count = k
                annotations[ANNOTATION_TYPES_ORDERED[k]] = annotation_type

            if annotation_count < 10:
                # No-ske: néha nincsen annyi tabok száma -1, amennyi hely az elemzésfajtákhoz kell:
                start = 11 - (10 - annotation_count)
                for n in range(start, len(ANNOTATION_TYPES_ORDERED)):
                    annotations[ANNOTATION_TYPES_ORDERED[n]] = '__NA__'

            annotations_per_line.append((is_space, annotations))

            if not is_space:
                is_space = True

        annotations_per_line.append((True, 'SSTOP'))
    annotations_per_line.append((True, 'PSTOP'))


def process_documents(noske_inps, clean_inps, corpora_dir):
    parent_folder_name = 'DOC'
    parent_folder_number = '000000'

    for i, noske_inp in enumerate(noske_inps):
        get_annotations = get_annotations_with_paragraph

        # inp[0] --> fájlnév, noske_inp[1] szöveg
        parent_folder_number = gen_docname(parent_folder_number, i)
        child_folder_name = '000000'

        # NoSkE soup létrehozása
        noske_soup = BeautifulSoup(noske_inp[1].replace('<g/>', '###NOSPACE###').
                                   replace('<poem>', '</div>\n<div>').
                                   replace('</poem>', '').replace('<div>\n</div>', ''),
                                   'xml')

        # doc tagen belüli fájlnév --> <doc file="lit_er_ambrus_l.s1.clean" ...>
        noske_doc = noske_soup.find('doc')
        fname_wo_ext = noske_doc['file']

        teszt_write_out('teszt_outputs', fname_wo_ext, noske_inp[1])

        # a NoSkE formátumban lévő fájlok clean megfelelője (metaadatokhoz, tehát header-ekhez)
        clean_xml = get_meta_file_path(clean_inps, fname_wo_ext)
        clean_soup = BeautifulSoup(clean_xml, 'html.parser')

        # NoSkE div tag-listájának létrehozása. Egy div egyenlő egy dokumentummal
        noske_divs = noske_soup.find_all('div')
        # clean div tag-listájának létrehozása.
        clean_divs = clean_soup.find_all('div')

        if len(noske_divs[0].find_all('div')) > 1:
            noske_divs = noske_divs[0:1]
            clean_divs = clean_divs[0:1]

        print(fname_wo_ext)

        # Az egész bemeneti XML metaadatának (header-jének) legenerálása és kiírása
        gen_header_xml('2nd_level_header', corpora_dir=corpora_dir,
                       parent_dir=f'{parent_folder_name}{parent_folder_number}', clean_xml=clean_xml)

        child_folder_number = 0

        for j, div in enumerate(noske_divs):

            if div.text.strip() == '':
                continue

            child_folder_number += 1

            clean_div = clean_divs[j]
            child_folder_name = gen_docname(child_folder_name, child_folder_number)
            annotations_per_line = []
            data = get_data(div)
            paragraphs = div.find_all('p')

            # Ha nincsen <p> tag a diven belül, akkor div-re állítódik az értéke, hogy lehessen benne iterálni a s-ket

            if len(paragraphs) == 0:
                get_annotations = get_annotatons_with_sentence

            # A szövegrész elemzésének hozzáadása az annotations listához
            get_annotations(div, annotations_per_line)

            meta_dict = {'fname_wo_ext': fname_wo_ext, 'annotations_per_line': annotations_per_line, 'data': data,
                         'clean_div': clean_div, 'parent_folder_name': f'{parent_folder_name}{parent_folder_number}',
                         'child_folder_name': child_folder_name}

            for opt in OPTS:
                yield gen_xml(meta_dict, opt), meta_dict['parent_folder_name'], meta_dict['child_folder_name']


def get_args():
    """
    :param basp: folder of output
    :return: 1: folder of output, 2: folder of input
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('input_noske_filepath', help='Path to file', nargs="+")
    parser.add_argument('-d', '--output_dir', help='Path to output directory', nargs='?')
    parser.add_argument('-m', '--input_clean_iglob_filepath', help='Path to root folder for iglob module',
                        nargs="?")

    args = parser.parse_args()

    input_clean_files = []

    for input_clean_file in iglob(args.input_clean_iglob_filepath, recursive=True):
        fname = os.path.basename(input_clean_file)
        input_clean_files.append((input_clean_file.replace(fname, ''), fname))

    args.input_clean_iglob_filepath = input_clean_files

    return vars(args)


def main():
    args = get_args()
    corpora_dir = args['output_dir']

    # noske fájlok az annotációk kinyeréséhez
    noske_inp = read(args['input_noske_filepath'])
    # clean fájlok a metaadatok kinyeréséhez (headerek)
    outp = process_documents(noske_inp, args['input_clean_iglob_filepath'], corpora_dir)

    for outpf in outp:
        parent_dir = ''.join(outpf[1])
        child_dir = outpf[2]
        annot_folder = outpf[0]['annot_folder']
        os.makedirs(os.path.join(corpora_dir, parent_dir, child_dir, annot_folder), exist_ok=True)
        # print(os.path.join(corpora_dir, parent_dir, child_dir, annot_folder))
        with open(os.path.join(corpora_dir, parent_dir, child_dir,
                               annot_folder, os.path.splitext(outpf[0]['output_xmlname'])[0] + '.xml'),
                  "w", encoding="utf-8", newline="\n") as f:
            f.write(outpf[0]['output_xml'].prettify())


if __name__ == '__main__':
    main()
