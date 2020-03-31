#! /usr/bin/env python3

from bs4 import BeautifulSoup
import os
import argparse
from glob import glob
import re
# from time import gmtime, strftime

"""
    11 oszlop van. (TSV)

      1 word        szóalak
      2 lemma       szótő
      3 msd         morfoszintaktikai leírás
      4 ctag        (figyelmen kívül hagyandó)
      5 ana         részletes morfológiai elemzés
      6 word_cv     szóalak CV-váza
      7 word_syll   szóalak szótagszáma
      8 lemma_cv    szótő CV-váza
      9 lemma_syll  szótő szótagszáma
     10 word_phon   szóalak fonetikai reprezentációja
     11 lemma_phon  szótő fonetikai reprezentációja

    BEMENET: no_ske-t használom bemenetként.
    <doc file ="file" style="style", region="region">
        <div type="type">
            <head rend="rend">
                <p> ??
                   <byline rend="rend"> ??
                        <s>
                            word->lemma->msd->ctag->ana->word_cv->word_syll->lemma_cv->lemma_syll->word_phon->lemma_phon
                            ..
                            ..
                            </g>
                        </s>
                    </byline>
                </p>
            </head>
        </div>
    </doc>

    KIMENET (morpho.xml):
    <span id="s89" from="657" to="668" l="4">
      <fs type="lex" xmlns="http://www.tei-c.org/ns/1.0">
        <f name="lex">
          <fs>
            <f name="lemma">módosítható</f>
            <f name="pos">MN.NOM</f>
            <f name="msd">compound=n;;hyphenated=n;;stem=mód::FN;;morphemes=ít::_FAK ZERO::NOM os::_SKEP ható::_HATO;;mboundary=mód+os+ít+ható</f>
          </fs>
        </f>
      </fs>
    </span>
    """


def write(outp, ext):
    # {'anl':soup, 'xmlname':xmlname}, parent_doc_nampts, child_docname
    for outpf in outp:
        parent_dir = ''.join(outpf[1])
        child_dir = outpf[2]
        # os.makedirs(parent_dir, exist_ok=True)
        anl_folder = outpf[0]['anl_folder']
        os.makedirs(os.path.join(parent_dir, child_dir, anl_folder), exist_ok=True)
        # os.makedirs(child_dir, exist_ok=True)
        with open(os.path.join(parent_dir, child_dir, anl_folder, os.path.splitext(outpf[0]['xmlname'])[0] + ext),
                  "w", encoding="utf-8", newline="\n") as f:
            f.write(outpf[0]['anl'].prettify())


def read(files):
    for fl in files:
        # with open(fl, encoding="utf8") as f:
        with open(fl, encoding="latin2") as f:
            yield os.path.basename(fl), f.read()


def gen_analyzed_xml(meta_dict, opt):
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
                'word': (None, 'tokens', 'to_be_named'),
                'lemma': (('lemma',), 'lemmas', 'to_be_named'),
                'pos': (('word', 'lemma', 'pos'), 'part-of-speech', 'noske'),
                'ana': (('lemma', 'pos', 'ana'), 'morpho', 'noske'),
                'word_cv': (('word', 'word_cv'), 'word_cv', 'noske'),
                'word_syll': (('word', 'word_syll'), 'word_syll', 'noske'),
                'lemma_cv': (('lemma', 'lemma_cv'), 'lemma_cv', 'noske'),
                'lemma_syll': (('lemma', 'lemma_syll'), 'lemma_syll', 'noske'),
                'word_phon': (('word', 'word_phon'), 'word_phon', 'noske'),
                'lemma_phon': (('lemma', 'lemma_phon'), 'lemma_phon', 'noske')}

    soup = BeautifulSoup(
        '<?xml-model href="span.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>',
        features='xml')

    anl_types = opt_dict[opt][0]
    xmlname = opt_dict[opt][1]
    anl_folder = opt_dict[opt][2]
    from_index = 0
    to_index = 0
    iden = 0
    sents_or_pgraphs = meta_dict['sents' if opt != 'paragraphs' else 'pgraphs']

    # TODO: külön függvénybe a header, data, sentences és paragraphs, 10 elemzés legenerálását
    # TODO: header nincs megoldva, csak továbbadja őket írásra. a header-hez kelleni fog az mxml, sajnos!
    # TODO: metaadatok a headerhez: oliphant.nytud.hu:/store/share/projects/mnsz2/xml_clean/
    if opt == 'header':
        return {'anl': soup, 'xmlname': xmlname, 'anl_folder': anl_folder}
    if opt == 'data':
        txt = soup.new_tag('text')
        txt.string = meta_dict['data']
        meta = soup.new_tag('metadata', file='metadata.xml')
        raw_text = soup.new_tag('raw_text',
                                attrs={'docid': '{}.{}'.format(''.join(meta_dict['parent_doc_nampts']), meta_dict['child_docname']),
                                'xmlns': 'http://ids-mannheim.de/ns/KorAP'})
        raw_text.append(meta)
        raw_text.append(txt)
        soup.append(raw_text)
        return {'anl': soup, 'xmlname': xmlname, 'anl_folder': anl_folder}

    soup.append(soup.new_tag('layer', attrs={'docid': meta_dict['fname'],
                                             'xmlns': 'http://ids-mannheim.de/ns/KorAP',
                                             'version': 'KorAP-0.4'}))
    span_list = soup.new_tag('spanList')
    for i, s_or_p in enumerate(sents_or_pgraphs):
        diff = -1

        for j, word in enumerate(s_or_p):
            # TODO sentences.xml és a paragraphs.xml végindexe nem mindig egyezik.
            if j != 0 and word[0] is True:
                from_index -= 1
                diff -= 1
            to_index = from_index + len(word[1]['word'])
            diff += len(word[1]['word'])+1

            # tag+number --> lowest the number the higher in hierarchy it is.
            if opt not in ('paragraphs', 'sentences', 'header', 'data'):
                span = soup.new_tag('span', attrs={'id': 's{}'.format(iden),
                                                   'from': str(from_index),
                                                   'to': str(to_index)})
                if anl_types is not None:
                    # 1. szint
                    fs1 = soup.new_tag('fs', attrs={'type': 'lex',
                                                    'xmlns': 'http://www.tei-c.org/ns/1.0'})
                    # 2. szint
                    f2 = soup.new_tag('f', attrs={'name': 'lex'})
                    # 3. szint
                    fs3 = soup.new_tag('fs')
                    for anl in anl_types:
                        # 4.szint: bármennyi következhet egymásután
                        f4 = soup.new_tag('f', attrs={'name': anl})
                        f4.string = word[1][anl]
                        fs3.append(f4)

                    span.append(fs1)
                    fs1.append(f2)
                    f2.append(fs3)
                span_list.append(span)

            from_index = to_index + 1
            iden += 1

        if opt == 'paragraphs' or opt == 'sentences':
            span = soup.new_tag('span', attrs={'from': str(to_index - diff),
                                               'to': str(to_index)})
            span_list.append(span)
    soup.layer.append(span_list)
    return {'anl': soup, 'xmlname': xmlname, 'anl_folder': anl_folder}


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
    # print(data)
    return pat_cut_space.sub('', ' '.join(data))


def process(inps):
    # észrevett hiba no-ske-val kapcs-ban: néha nincsen annyi tab -1, amennyi hely az elemzésfajtákhoz kell:
    anls_ordered = (
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
        soup = BeautifulSoup(inp[1], 'xml')
        doc = soup.find('doc')
        divs = doc.find_all({'div'})
        fname = doc['file']
        genre = doc['style']
        region = doc['region']
        nospace = False
        # ha vége van egy divnek --> yield kimenet --> kimenet kiírása külön mappába, amiben külön mappában az elemzések
        for j, div in enumerate(divs):  # a teszt miatt divs[-1], mert egyelőre nem yield-et használok
            child_docname = gen_docname(child_docname, j)
            sents = []
            pgraphs = []
            # szöveg típus
            txt_type = div['type']
            # cím
            txt_title = " ".join([ln.split('\t')[0] for ln in div.find('head').text.split('\n')])
            data = get_data(div)
            for p_tag in div.find_all('p'):
                pgraph = []
                for s_tag in p_tag.find_all('s'):
                    sent = []
                    s_tag = s_tag.text.split('\n')
                    for line in s_tag:
                        line = line.strip()
                        if line != '':
                            # [word, lemma, msd, ctag, ana, word_cv, word_syll, lemma_cv, lemma_syll, word_phon, lemma_phon]
                            anls = {}
                            k_count = 0
                            for k, anl in enumerate(line.split('\t')):
                                k_count = k
                                anls[anls_ordered[k]] = anl
                            if k_count < 10:
                                start = 11 - (10 - k_count)
                                for l in range(start, len(anls_ordered)):
                                    anls[anls_ordered[l]] = '__NA__'
                            sent.append((nospace, anls))
                            pgraph.append((nospace, anls))
                            if nospace:
                                nospace = False
                        else:
                            nospace = True

                    sents.append(sent)
                pgraphs.append(pgraph)

            meta_dict = {'fname': fname, 'genre': genre, 'region': region, 'txt_type': txt_type,
                         'txt_title': txt_title, 'pgraphs': pgraphs, 'sents': sents, 'data': data,
                         'parent_doc_nampts': parent_doc_nampts, 'child_docname': child_docname}
            # print(meta_dict['sents'])

            for opt in opts:
                if opt:  # header és data: még nincsen írva rájuk script, de kellenek
                    yield gen_analyzed_xml(meta_dict, opt), meta_dict['parent_doc_nampts'], meta_dict['child_docname']


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
