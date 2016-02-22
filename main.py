#!/usr/bin/env python2
# coding: utf-8

import sys, os

for lib in os.listdir('./lib'):
    sys.path.insert(1, './lib/' + lib)

import re
import xuxian

parser = xuxian.get_parser()
parser.add_argument('--task-id', required=True, help='execution id')
parser.add_argument('--wiki-file', required=True,
        help='the /path/to/name of the wiki file to process')
parser.add_argument('--nlp-server', default='127.0.0.1')
parser.add_argument('--nlp-port', default=9000)

parser.add_argument('--entity-wiki-file', required=True,
        help='freebase node and wikipedia map file, first column is '
        'freebase node and second collumn is wikipedia links.'
        )

parser.add_argument('--entity-sentence-output-file', required=True,
        help='output file each line with an entity and the sentence where it appears')

from wiki_doc import wikiobj_to_doc
from utils import charset_wrapper, init_corenlp
from entity_wikilink import build_entity_wikilink_map, href_to_wikilink
from entity_mentions import get_plain_text, get_plain_text_mention_info

def main(args):
    recovery_state = xuxian.recall(args.task_id)

    docs = wikiobj_to_doc(charset_wrapper(open(args.wiki_file)))
    nlp = init_corenlp(args.nlp_server, args.nlp_port)
    wikilink_to_entity, entity_to_wikilink = build_entity_wikilink_map(
            charset_wrapper(open(args.entity_wiki_file)))

    entity_sentence_outfile = xuxian.apply_dump_file('entity-sentence',
            args.entity_sentence_output_file)

    for doc in docs:
        for (lineno, line) in enumerate(doc['text']):
            # every line is a paragraph in wikipedia
            plaintext = get_plain_text(line)
            mentions = get_plain_text_mention_info(line)

            # at the correct time point, clear the recovery state
            if recovery_state == doc['id'] + str(lineno):
                recovery_state = None

            if recovery_state is not None:
                continue

            for (mstart, mend, href, _) in mentions:
                wikilink = href_to_wikilink(href)
                if wikilink not in wikilink_to_entity:
                    # TODO: print error
                    continue

                entity_sentence_outfile.info(u"{0}\t{1}\t{2}\t{3}".format(
                        wikilink_to_entity[href_to_wikilink(href)],
                        mstart, mend, plaintext))


            xuxian.remember(args.task_id, doc['id'] + str(lineno))

        break


if __name__ == "__main__":
    xuxian.parse_args()
    xuxian.run(main)

