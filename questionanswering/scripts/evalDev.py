"""Evaulate a parser.

Usage:
  eval.py -i <file>
  eval.py -h | --help

Options:
  -i <file>     Parsing model file.
  -h --help     Show this screen.
"""
from docopt import docopt
import pickle
import sys

def getQuestAnKey(quest):
    idiomas = quest["question"]
    st_keywords = ""
    st_question = ""
    for idiom in idiomas:
        if idiom["language"] == "es":
            st_question = idiom["string"]
            st_keywords = idiom["keywords"]
            break
    return st_question,st_keywords

def progress(msg, width=None):
    """Ouput the progress of something on the same line."""
    if not width:
        width = len(msg)
    print('\b' * width + msg, end='')
    sys.stdout.flush()


if __name__ == '__main__':
    opts = docopt(__doc__)

    print('Loading model...')
    filename = opts['-i']
    f = open(filename, 'rb')
    model = pickle.load(f)
    f.close()

    print('Loading corpus...')
    with open('EvalData.json', 'r') as data_file:
      data = json.load(data_file)
    questionsSample = data["questions"]

    print('Parsing...')
    hits, total_gold, total_model = 0, 0, 0
    n = len(parsed_sents)
    format_str = '{:3.1f}% ({}/{}) (P={:2.2f}%, R={:2.2f}%, F1={:2.2f}%)'

    get_answer_type
    progress(format_str.format(0.0, 0, n, 0.0, 0.0, 0.0))

    for quest in questionsSample:
        tagged_sent = gold_parsed_sent.pos()

        # parse
        model_parsed_sent = model.parse(tagged_sent)


        hits += len(gold_spans & model_spans)
        total_gold += len(gold_spans)
        total_model += len(model_spans)

        # compute labeled partial results
        prec = float(hits) / total_model * 100
        rec = float(hits) / total_gold * 100
        f1 = 2 * prec * rec / (prec + rec)

        progress(format_str.format(float(i+1) * 100 / n, i+1, n, prec, rec, f1))

    print('')
    print('Parsed {} sentences'.format(n))
    print('Labeled')
    print('  Precision: {:2.2f}% '.format(prec))
    print('  Recall: {:2.2f}% '.format(rec))
    print('  F1: {:2.2f}% '.format(f1))
