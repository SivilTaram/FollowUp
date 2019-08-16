from string import punctuation
from nltk.translate.bleu_score import sentence_bleu
import nltk
from typing import List
import re
import statistics

try:
    import spacy

    nlp = spacy.load('en_core_web_sm', disable=["tagger", "parser", "ner"])
except ImportError:
    print("WARNING: you should install `spacy` to bettter tokenized results for accuracte BLEU.")
    nlp = None


def tokenize_sentence(sentence):
    if nlp is not None:
        tokens = nlp(sentence)
        tokens = [token.text.lower() for token in tokens]
    else:
        tokens = [token.lower() for token in sentence.split(" ")]
    return tokens


def evaluate_bleu_score(predict_restate: str, ground_restate: str):
    predict = [ele for ele in tokenize_sentence(predict_restate) if ele not in punctuation]
    target = [ele for ele in tokenize_sentence(ground_restate) if ele not in punctuation]

    bleu_score = sentence_bleu([target], predict,
                               smoothing_function=nltk.translate.bleu_score.SmoothingFunction().method2)
    return bleu_score


def evaluate_sym_acc(predict_restate: str, ground_restate_sym: List[str]):
    # compress the space of all tokens in predict_restate,
    # then check if the every symbol word in ground_restate_sym
    # is the substring in predict_restate
    default_ret = 1.0
    predict = re.sub('\\s+', '', predict_restate)
    target_key_syms = [re.sub('\\s+', '', sym) for sym in ground_restate_sym]
    # check all key words
    for key_sym in target_key_syms:
        if key_sym in predict:
            start_pos = predict.index(key_sym)
            predict = list(predict)
            # remove the checked substring
            del predict[start_pos: len(key_sym)]
            predict = ''.join(predict)
        else:
            default_ret = 0.0
            break
    return default_ret


def check_on_all_examples(predict_file, test_tsv_file, test_sym_file):
    with open(predict_file, 'r', encoding='utf8') as predict_f, \
            open(test_tsv_file, 'r', encoding='utf8') as test_f, \
            open(test_sym_file, 'r', encoding='utf8') as sym_f:
        try:
            from tqdm import tqdm
            iter_eval = tqdm(list(zip(predict_f, test_f, sym_f)))
        except ImportError:
            print("You could install tqdm to see the evaluation progress.")
            iter_eval = list(zip(predict_f, test_f, sym_f))

        all_bleu_scores = []
        all_sym_acc = []

        for predict_example, test_example, test_sym in iter_eval:
            predict_example = predict_example.strip()
            test_example = test_example.strip().split('\t')[-2]
            test_sym = test_sym.strip().split(' ')
            # check bleu
            bleu_score = evaluate_bleu_score(predict_example, test_example)
            sym_acc = evaluate_sym_acc(predict_example, test_sym)

            all_bleu_scores.append(bleu_score)
            all_sym_acc.append(sym_acc)

        avg_bleu_score = 100 * statistics.mean(all_bleu_scores)
        avg_sym_acc = 100 * statistics.mean(all_sym_acc)

        print("=" * 80)
        print(" " * 20 + " FollowUp Dataset Evaluation Result")
        print("=" * 80)
        print("BLEU Score:  {:.2f} (%)".format(avg_bleu_score))
        print("Symbol Acc:  {:.2f} (%)".format(avg_sym_acc))


if __name__ == '__main__':
    check_on_all_examples('predict.example',
                          'test.tsv',
                          'test.sym')
