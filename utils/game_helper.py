import wordle_algo
from dictionary_helper import *
from web_helper import *
from util_helper import *


def best_guessing_words(dict_global, n=1, corpus='web', words=[], okletters='', notokletters='', okpattern='', nokpattern=[],
                        verbose=False, evaluation='word'):
    import random

    def sum_letter_weight(words_):
        return [sum([letter_score(l, return_letter=False) for l in w]) for w in words_]

    def word_freq_weight(words_):
        return [dict_global[w] if w in dict_global else 1 for w in words_]

    words = filter_words(words, okletters, notokletters, okpattern, nokpattern, verbose)

    if len(words) == 0:
        letters = letter_score()
        letters = "".join([l for l in letters if l not in notokletters and l not in okletters])

        if corpus == 'web':
            words = get_words_with_pattern_url(okletters + letters[:5 - len(okletters)], okletters, notokletters,
                                               okpattern, nokpattern, letters, verbose)
        elif corpus == 'local':
            words = get_words_with_pattern_local(dict_global, okletters=okletters, letters=letters,
                                                 notokletters=notokletters, nokpattern=nokpattern)

    weights_ = word_freq_weight(words) if evaluation == 'word' else sum_letter_weight(words)
    word = random.choices(words, k=n, weights=weights_)
    if verbose: print(*word, sep='\n')

    return word


def analyse_results(word, results, okletters, nokletters, pattern, nokpatterns):
    sokl, snokl = [], []
    pattern_, new_nok_pat = list(pattern), list('?????')
    nokpatterns_ = [] + nokpatterns

    for i, (w, r) in enumerate(zip(word, results)):
        if r == -1:
            snokl.append(w)
        elif r == 0:
            sokl.append(w)
            new_nok_pat[i] = w
        elif r == 1:
            sokl.append(w)
            pattern_[i] = w

    nokpatterns_.append("".join(new_nok_pat))

    return "".join(list(set(sokl + list(okletters)))), "".join(list(set(snokl + list(nokletters)))), "".join(
        pattern_), nokpatterns_


def play_page(driver, number, dict_global, type_guess, corpus='web', seq=None, seq_res=None):
    from selenium.webdriver.common.keys import Keys
    import datetime

    if type(number) != int:
        number = (number - datetime.datetime.strptime('06/19/2021', '%m/%d/%Y')).days

    body = get_initial_page(driver, f"https://metzger.media/games/wordle-archive/?day={number}")


    words, okletters, nokletters, pattern, nokpatterns, trial = '', '', '', '?????', [], 0
    erase_word = Keys.BACK_SPACE * 5

    while trial < 6 and pattern.count('?') > 0:
        if type_guess == 'solver':
            date_2_solve = datetime.datetime.strptime('06/19/2021', '%m/%d/%Y') + datetime.timedelta(days=number)
            word_try = wordle_algo.solve_worldle(date_2_solve)
        else:
            word_try = best_guessing_words(dict_global=dict_global,corpus=corpus, words=words, okletters=okletters, notokletters=nokletters,
                                           okpattern=pattern,
                                           nokpattern=nokpatterns)

        if type(word_try) == list: word_try = word_try[0]

        send_try(body, word_try)
        results = process_results(driver, trial)
        if results == -1:
            print("tried non-existing word: ", word_try)
            send_try(body, erase_word, enter=False)
            if word_try in dict_global: dict_global.pop(word_try)
            if word_try in words: words.remove(word_try)
            continue

        if seq is not None:
            if len(seq) > trial:
                word_try = seq[trial]
            else:
                poss = filter_words(words=dict_global, okletters=okletters, notokletters=nokletters,
                                    nokpattern=nokpatterns, okpattern=pattern)
                score_f = [dict_global[w] for w in poss]
                tot = sum(score_f)
                score_p = [s / tot for s in score_f]
                for i, w in enumerate(poss):
                    print(f"{w}: {score_f[i]} ({score_p[i]})", sep='\n')
                import random
                print('choices with freq: ', random.choices(poss, weights=score_f, k=1))
                print('choices with perc: ', random.choices(poss, weights=score_p, k=1))
                return -1

        if seq_res is not None and len(seq_res) > trial:
            results = seq_res[trial]

        print_colored(word_try, results)
        okletters, nokletters, pattern, nokpatterns = analyse_results(word_try, results, okletters, nokletters, pattern,
                                                                      nokpatterns)
        if corpus == 'web' and len(okletters) > 2 and pattern.count('?') > 0:
            words = get_words_with_pattern_url(okletters + '?' * (5 - len(okletters)))
        elif corpus == 'local':
            letters = letter_score()
            letters = "".join([l for l in letters if l not in nokletters and l not in okletters])

            words = get_words_with_pattern_local(dict_global, okletters=okletters,
                                                 letters=letters, notokletters=nokletters, nokpattern=nokpatterns)

        trial += 1

    if pattern.count('?') == 0:
        print(f'\nfound: {pattern}')
        result = trial
    else:
        print(f'\nCouldn found words, found pattern: {pattern}')
        print('possible words: ', end='')
        print(*filter_words(get_words_with_pattern_url(pattern), okletters, nokletters, pattern, nokpatterns), sep=', ')
        result = -1

    print()

    return result

