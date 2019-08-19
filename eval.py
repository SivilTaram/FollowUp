from string import punctuation
from nltk.translate.bleu_score import sentence_bleu
import nltk
from typing import List
import re
import statistics
from nltk.corpus import stopwords

stop_words = list(set(stopwords.words('english') + [
    "of",
    "what",
    "name",
    "is",
    "in",
    "how",
    "which",
    "than",
    "has",
    "and",
    "about",
    "show",
    "for",
    "to",
    "was",
    "all",
    "by",
    "are",
    "from",
    "with",
    "that",
    "when",
    "have",
    "who",
    "it",
    "list",
    "did",
    "if",
    "on",
    "other",
    "does",
    "compare",
    "their",
    "just",
    "those",
    "were",
    "each",
    "there",
    "as",
    "total",
    "only",
    "whose",
    "got",
    "me",
    "had",
    "or",
    "its",
    "also",
    "grouped",
    "one",
    "where",
    "same",
    "listed",
    "display",
    "use",
    "they",
    "any",
    "at",
    "i",
    "he",
    "group",
    "please",
    "his",
    "limit",
    "using",
    "every",
    "according",
    "here",
    "then",
    "see",
    "this",
    "held",
    "him",
    "over",
    "among",
    "get",
    "created",
    "ever",
    "set",
    "scope",
    "come",
    "earned",
    "against",
    "being",
    "value",
    "based",
    "tell",
    "received",
    "named",
    "times",
    "calculate",
    "been",
    "give",
    "appear",
    "involved",
    "but",
    "gained",
    "let",
    "find",
    "into",
    "chart",
    "made",
    "keep",
    "statistics",
    "until",
    "do",
    "happen",
    "s",
    "between",
    "gap",
    "did",
    "do",
    "does",
    "doing",
    "done",
    "due",
    "during",
    "was",
    "the",
    "groups",
    "split",
    "take",
    "already",
    "receive",
    "order",
    "could",
    "may",
    "compared",
    "chart",
    "table",
    "like",
    "inducted",
    "occur",
    "joined",
    "join",
    "meet",
    "add",
    "remove",
    "produced",
    "reaching",
    "grouping",
    "appears",
    "limited",
    "finally",
    "exactly",
    "belong",
    "next",
    "attended",
    "attend"
]))

stop_words.sort(key=lambda s: len(s), reverse=True)

try:
    import spacy

    nlp = spacy.load('en_core_web_sm', disable=["tagger", "parser", "ner"])
except ImportError:
    print("WARNING: you should install `spacy` to for accurate BLEU and Sym Acc.")
    nlp = None

symbol_words = [
    "more", "largest", "less", "sum", "count", "mean", "average", "middle",
    "many", "much",
    "lowest", "least", "most", "max", "min", "first", "last", "earliest", "oldest",
    "top", "max", "min", "latest", "highest", "lowest",
    "biggest", "maximum", "best", "minimum", "amount", "smallest", "greatest", "worst", "descending", "ascending",
    "early", "late", "small", "large",
    "more", "less", "before", "after", "over", "higher", "larger", "longer", "shorter",
    "greater", "lower", "equal", "more", "smaller", "under", "above", "later", "after", "equals",
    "not", "no"
]

symbol_words = [re.sub('\\s+', '', sym) for sym in symbol_words]
symbol_words.sort(key=lambda s: len(s), reverse=True)


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


def evaluate_sym_acc(predict_restate: str, ground_restate_sym: List[str], ground_restate_query: str = None):
    # compress the space of all tokens in predict_restate,
    # then check if the every symbol word in ground_restate_sym
    # is the substring in predict_restate
    default_ret = 1.0

    # remove punctuation
    predict_restate = re.sub("\\s+", ' ', predict_restate)
    predict_restate = [re.sub(r'[^\w\s]', '', word.lower())
                       for word in tokenize_sentence(predict_restate) if word not in punctuation]

    ground_restate_sym = [re.sub(r'[^\w\s]', '', word.lower())
                          for word in ground_restate_sym if word not in punctuation]

    ground_restate_sym.sort(key=lambda s: len(s), reverse=True)

    # check all ground in predict
    for key_sym in ground_restate_sym:
        if key_sym in predict_restate:
            sym_index = predict_restate.index(key_sym)
            del predict_restate[sym_index]
        else:
            return 0.0

    # check symbol_words not in predict
    for key_sym in symbol_words:
        if key_sym in predict_restate:
            return 0.0

    specific_unused_words = []
    if ground_restate_query is not None:
        ground_restate_query = [re.sub(r'[^\w\s]', '', word.lower())
                                for word in tokenize_sentence(ground_restate_query)]
        specific_unused_words = list(set([word for word in ground_restate_query if word not in ground_restate_sym]))

    # use ground_restate_query to build extra stop words
    for word in specific_unused_words + stop_words:
        while word in predict_restate:
            start_pos = predict_restate.index(word)
            del predict_restate[start_pos]

    # remaining chars should be equal to 0, but here we keep some space
    # for possible stopwords which are not covered by our evaluation script.
    if len(predict_restate) > 0:
        default_ret = 0.0

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
            sym_acc = evaluate_sym_acc(predict_example, test_sym, test_example)

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
