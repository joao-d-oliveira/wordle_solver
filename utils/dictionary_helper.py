match_pattern = lambda w, p: all([(w[i] == p[i] or p[i] == '?') for i in range(5)])
doesnmatch_pattern = lambda w, p: all([(w[i] != p[i] or p[i] == '?') for i in range(5)])


def filter_words_without_known(words, forbiddenletters, okletters, verbose=False):
    from collections import Counter

    common_lett = list(set(okletters).intersection(set(forbiddenletters)))

    words = [w for w in words if len([l2 for l2 in [l for l in forbiddenletters if l in w] if l2 not in okletters]) == 0]

    final_words = []
    for w in words:
        c = Counter(list(w))
        if not any([c[l] > 1 for l in common_lett]): final_words.append(w)

    if verbose: print(f'After removing forbidden letters:\t{len(final_words)}')

    return words


def filter_words_with_known(words, okletters, nokletters, verbose=False):
    from collections import Counter
    words = [w for w in words if len([w for l in okletters if l in w]) == len(okletters)]
    common_lett = list(set(okletters).intersection(set(nokletters)))

    final_words = []
    for w in words:
        c = Counter(list(w))
        if not any([c[l] > 1 for l in common_lett]): final_words.append(w)

    if verbose: print(f'After removing words with no known letters:\t{len(final_words)}')

    return final_words


def filter_words_known_pattern(words, knownpattern, verbose=False):
    words = [w for w in words if match_pattern(w, knownpattern)]
    if verbose: print(f"After removing words that don't fit known pattern:\t{len(words)}")

    return words


def filter_words_forbidden_pattern(words, forbiddenpattern, verbose=False):
    words = [w for w in words if all([doesnmatch_pattern(w, p) for p in forbiddenpattern])]
    if verbose: print(f'After removing forbidden patterns:\t{len(words)}')

    return words


def letter_score(letter=None, verbose=False, return_letter=True):
    scores = {'A': 8000, 'B': 1600, 'C': 3000, 'D': 4400, 'E': 12000, 'F': 2500, 'G': 1700, 'H': 6400, 'I': 8000, 'J': 400,
            'K': 800, 'L': 4000, 'M': 3000, 'N': 8000, 'O': 8000, 'P': 1700, 'Q': 500, 'R': 6200, 'S': 8000, 'T': 9000,
            'U': 3400, 'V': 1200, 'W': 2000, 'X': 400, 'Y': 2000, 'Z': 200, }

    if letter is None:
        if verbose: print(*sorted(scores.items(), key=lambda x:x[1], reverse=True), sep='\n')
        return [l for l, v in sorted(scores.items(), key=lambda x:x[1], reverse=True)]
    else:
        if verbose: print(letter.upper(), ':',scores[letter.upper()])
        if return_letter: return  letter.upper()
        else: return scores[letter]


def filter_words(words, okletters='', notokletters='', okpattern='', nokpattern=[], verbose=False):
    if okletters != '':
        okletters = okletters.upper()
        words = filter_words_with_known(words, okletters, notokletters)

    if notokletters != '':
        notokletters = notokletters.upper()
        words = filter_words_without_known(words, notokletters, okletters)

    if okpattern != '':
        okpattern = okpattern.upper()
        words = filter_words_known_pattern(words, okpattern)

    if nokpattern is not []:
        words = filter_words_forbidden_pattern(words, nokpattern)

    return words


def get_corpus(filter_ngrams=None, filename='~/Documents/Python/wordleSolver/corpus/ngram_freq.csv', validater=None):
    import pandas as pd

    full_corpus = pd.read_csv(filename)
    full_corpus.word = full_corpus.word.str.upper()

    if filter_ngrams is not None:
        full_corpus['n_gram'] = full_corpus.word.str.len()
        full_corpus = full_corpus.loc[full_corpus.n_gram == filter_ngrams, ['word', 'count']]

    if validater is not None:
        dictionary = open(validater, 'r', encoding='ascii', errors='ignore').read()
        dictionary = dictionary.upper().split('\n')
        if filter_ngrams is not None:
            dictionary = [w for w in dictionary if len(w) == filter_ngrams]

        full_corpus = full_corpus.loc[full_corpus.word.isin(dictionary)]

    return full_corpus.set_index('word').to_dict()['count']

