#! /usr/bin/env python3

from bs4 import BeautifulSoup
import os
import argparse
from glob import glob
import re
# from time import gmtime, strftime

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


def write(outp, ext):
    # TODO: a korpusz mappa alatt legyen az összes
    for outpf in outp:
        corpora_dir = outpf[3]
        parent_dir = ''.join(outpf[1])
        child_dir = outpf[2]
        # os.makedirs(parent_dir, exist_ok=True)
        annot_folder = outpf[0]['annot_folder']
        os.makedirs(os.path.join(corpora_dir, parent_dir, child_dir, annot_folder), exist_ok=True)
        # os.makedirs(child_dir, exist_ok=True)
        with open(os.path.join(corpora_dir, parent_dir, child_dir, annot_folder, os.path.splitext(outpf[0]['xmlname'])[0] + ext),
                  "w", encoding="utf-8", newline="\n") as f:
            f.write(outpf[0]['xml'].prettify())


def read(files):
    for fl in files:
        # with open(fl, encoding="utf8") as f:
        with open(fl, encoding="latin2") as f:
            yield os.path.basename(fl), f.read()


def gen_header_xml():
    soup = BeautifulSoup(
        '<?xml-model href="span.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>',
        features='xml')
    return soup


def gen_data_xml(data, docid_one, docid_two):
    soup = BeautifulSoup(
        '<?xml-model href="span.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>',
        features='xml')
    txt = soup.new_tag('text')
    txt.string = data
    meta = soup.new_tag('metadata', file='metadata.xml')
    raw_text = soup.new_tag('raw_text',
                            attrs={'docid': '{}.{}'.format(docid_one, docid_two),
                                   'xmlns': 'http://ids-mannheim.de/ns/KorAP'})
    raw_text.append(meta)
    raw_text.append(txt)
    soup.append(raw_text)
    return soup


def gen_annotated_xml(annot_types, fname, txt, opt):
    soup = BeautifulSoup(
        '<?xml-model href="span.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>',
        features='xml')
    from_index_sp = 0
    from_index = 0
    to_index = 0
    iden = 0
    soup.append(soup.new_tag('layer', attrs={'docid': fname,
                                             'xmlns': 'http://ids-mannheim.de/ns/KorAP',
                                             'version': 'KorAP-0.4'}))
    span_list = soup.new_tag('spanList')
    for i, word in enumerate(txt):
        if i != 0 and txt[i - 1] not in ['SSTOP', 'PSTOP'] and word[0] is True:
            from_index -= 1
        if word == 'SSTOP' or word == 'PSTOP':
            if (word == 'SSTOP' and opt == 'sentences') or (word == 'PSTOP' and opt == 'paragraphs'):
                span = soup.new_tag('span', attrs={'from': str(from_index_sp),
                                                   'to': str(to_index)})
                span_list.append(span)
                from_index_sp = to_index + 1
            continue

        to_index = from_index + len(word[1]['word'])

        # tag+number --> lowest the number the higher in hierarchy it is.
        if opt not in ('paragraphs', 'sentences', 'header', 'data'):
            span = soup.new_tag('span', attrs={'id': 's{}'.format(iden),
                                               'from': str(from_index),
                                               'to': str(to_index)})
            if annot_types is not None:
                # 1. szint
                fs1 = soup.new_tag('fs', attrs={'type': 'lex', 'xmlns': 'http://www.tei-c.org/ns/1.0'})
                # 2. szint
                f2 = soup.new_tag('f', attrs={'name': 'lex'})
                # 3. szint
                fs3 = soup.new_tag('fs')
                for annot in annot_types:
                    # 4.szint: bármennyi következhet egymásután
                    f4 = soup.new_tag('f', attrs={'name': annot})
                    f4.string = word[1][annot]
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

    opt_dict = {'header': (None, 'header', ''),
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

    xmlname = opt_dict[opt][1]
    annot_folder = opt_dict[opt][2]

    # TODO: header nincs megoldva, csak továbbadja írásra
    # TODO: metaadatok a headerhez: oliphant.nytud.hu:/store/share/projects/mnsz2/xml_clean/
    if opt == 'header':
        xml = gen_header_xml()
    elif opt == 'data':
        xml = gen_data_xml(meta_dict['data'], ''.join(meta_dict['parent_doc_nampts']), meta_dict['child_docname'])
    else:
        xml = gen_annotated_xml(opt_dict[opt][0], meta_dict['fname'], meta_dict['txt'], opt)
    return {'xml': xml, 'xmlname': xmlname, 'annot_folder': annot_folder}


def gen_docname(num_of_doc, i):
    i_str = str(i + 1)
    num_of_doc = num_of_doc[0:-len(i_str)] + i_str
    return num_of_doc


def get_data(div):
    pat_cut_space = re.compile(r' ?NoSpace ?')
    data = []
    for s_tag in div.find_all('s'):
        s_tag = s_tag.text.split('\n')
        for line in s_tag:
            line = line.strip()
            if line != '':
                data.append(line.split('\t')[0])

            elif len(data) > 0 and data[-1] == 'NoSpace':
                del data[-1]
            else:
                data.append('NoSpace')
    return pat_cut_space.sub('', ' '.join(data))


def get_annots(line, annots_ordered):
    # word,lemma,msd,ctag,ana,word_cv,word_syll,lemma_cv,lemma_syll,word_phon,lemma_phon
    annots = {}
    k_count = 0
    for k, anl in enumerate(line.split('\t')):
        k_count = k
        annots[annots_ordered[k]] = anl
    if k_count < 10:
        start = 11 - (10 - k_count)
        for l in range(start, len(annots_ordered)):
            annots[annots_ordered[l]] = '__NA__'
    return annots


def process(inps):
    # észrevett hiba no-ske-val kapcs-ban: néha nincsen annyi tab -1, amennyi hely az elemzésfajtákhoz kell:
    annots_ordered = (
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

    opts = (
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

    parent_doc_nampts = ['DOC', '000000']

    for i, inp in enumerate(inps):
        parent_doc_nampts[1] = gen_docname(parent_doc_nampts[1], i)
        child_docname = '000000'
        # TODO: a header tag s-je (a cím) lemarad az elemzésekből: kijavítani
        # TODO: paragraphus más kezdőindexet kap, mint a sentence
        soup = BeautifulSoup(inp[1], 'xml')
        doc = soup.find('doc')
        divs = doc.find_all({'div'})
        fname = doc['file']
        genre = doc['style']
        region = doc['region']

        for j, div in enumerate(divs):
            child_docname = gen_docname(child_docname, j)
            txt = []
            # szöveg típus
            txt_type = div['type']
            # cím
            txt_title = " ".join([ln.split('\t')[0] for ln in div.find('head').text.split('\n')])
            data = get_data(div)
            for p_tag in div.find_all('p'):
                nospace = False
                for s_tag in p_tag.find_all('s'):
                    s_tag = s_tag.text.split('\n')
                    for line in s_tag:
                        line = line.strip()
                        if line != '':
                            anls = get_annots(line, annots_ordered)
                            txt.append((nospace, anls))
                            if nospace:
                                nospace = False
                        else:
                            nospace = True

                    txt.append("SSTOP")
                txt.append("PSTOP")

            meta_dict = {'fname': fname, 'genre': genre, 'region': region, 'txt_type': txt_type,
                         'txt_title': txt_title, 'txt': txt, 'data': data,
                         'parent_doc_nampts': parent_doc_nampts, 'child_docname': child_docname}
            for opt in opts:
                yield gen_xml(meta_dict, opt), meta_dict['parent_doc_nampts'], meta_dict['child_docname'], "MNSZ"


def get_args(basp):
    """
    :param basp: folder of output
    :return: 1: folder of output, 2: folder of input
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs="+")
    parser.add_argument('-d', '--directory', help='Path of output file(s)', nargs='?')

    args = parser.parse_args()
    files = []

    if args.filepath:
        for p in args.filepath:
            poss_files = glob(p)
            poss_files = [os.path.abspath(x) for x in poss_files]
            files += poss_files

    if args.directory:
        basp = os.path.abspath(args.directory)

    return {'dir': basp, 'files': files}


def main():
    args = get_args('outp')
    inp = read(args['files'])
    outp = process(inp)
    write(outp, '.xml')


if __name__ == '__main__':
    main()
