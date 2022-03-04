import datetime
from utils.game_helper import *
from utils.util_helper import *

INCORRECT = -1
EXISTS = 0
CORRECT = 1
DEFAULT_GAMES = [datetime.datetime.today()]
DEFAULT_TYPE = 'solver'  # 'solver/guessing'
DEFAULT_CORPUS = 'local' # local/web
DEFAULT_CHOICE = 'word'  # letter/word
DEFAULT_WORDS_TRIED = []
DEFAULT_RESULTS_TRIED = []
DEFAULT_EXPORT_RES = True
EXPORT_FILE = 'session_levels.txt'
GLOBAL_DICT = get_corpus(filter_ngrams=5,
                         validater='/Users/joao/Documents/Python/wordleSolver/corpus/wordle_av.txt')


def print_help():
    print(f"usage: python3 {sys.argv[0]} <params - optional>")
    print('params:')
    print("\t--game number/date/range \t 'number', example: 231, plays the game according to 'https://metzger.media/games/wordle-archive/'; ",
          "'date', example: '2022-01-20' (yyyy-mm-dd) only works for now with solver type; ",
          "'range', example: 2-200 in case you want the computer to play range of games ")
    print("\t--type solver/guessing \t 'solver' to use wordle algo and get it right at first trial; 'guessing' to try to guess;")
    print("\t--corpus local/web \t'local' uses local database of words; 'web' does scrapping from wordsolver.net")
    print("\t--eval_choice letter/word \t 'letter' gives preference to most used letters; 'word' gives preference to most used words")
    print("\t--words_tried [words, separated, by, comma] \t example: [TELIA, ORATE] list of words, in case you want to find next available words ")
    print(f"\t--results_tried [results, separated, by, comma] ({INCORRECT}-incorrect, {EXISTS}-exists, {CORRECT}-correct) ",
          " \t example: [[1, 0, 0, 0, 2], [1, 2, 0, 0, 2]] list of results, needs to be used in combination with '--words_tried' ")
    print("\t--export_results True/False \t '1' if you want to export results to a session object so later on it's easier to see computer performance")


def process_game_params():
    args = sys.argv[1:]
    all_args = " " + " ".join(args)
    if '--help' in all_args: print_help()
    games      = process_params('--game', DEFAULT_GAMES, all_args)
    type_guess = process_params('--type', DEFAULT_TYPE, all_args)
    corpus     = process_params('--corpus', DEFAULT_CORPUS, all_args)
    eval       = process_params('--eval_choice', DEFAULT_CHOICE, all_args)
    w_tried    = process_params('--words_tried', DEFAULT_WORDS_TRIED, all_args)
    r_tried    = process_params('--results_tried', DEFAULT_RESULTS_TRIED, all_args)
    exp_res    = process_params('--export_results', DEFAULT_EXPORT_RES, all_args)

    return games, type_guess, corpus, eval, w_tried, r_tried, exp_res


def validation_params(games, type_guess,  w_tried, r_tried):
    assert len(r_tried) == len(w_tried), "in case you want to use already tried words, needs to have same number of results"
    assert (type_guess == 'guessing' and all([type(g) != datetime.datetime for g in games])) or type_guess == 'solver',\
        'can use datetime only with solver type'


if __name__ == '__main__':
    import sys
    from collections import Counter

    final_results, txt = [], ''

    start_time = time.time()

    games, type_guess, corpus, eval, w_tried, r_tried, exp_res = process_game_params()
    validation_params(games, type_guess,  w_tried, r_tried)

    driver = get_initial_driver()

    if w_tried:
        play_page(driver, 246, GLOBAL_DICT, type_guess, corpus=corpus, seq=w_tried, seq_res=r_tried)
    else:
        if exp_res: txt = '{"levels": {'

        for g in games:
            res = play_page(driver, g, GLOBAL_DICT, type_guess, corpus=corpus)

            final_results.append(res)

            if exp_res:
                txt += f'"{str(g)}": '
                if res == -1: txt += '{"tries":6,"cleared":false},'
                else: txt += '{"tries":' + str(res) + ',"cleared":true},'
                print(txt, file=open(EXPORT_FILE, 'w'))

        if exp_res:
            txt = txt[:-1] + '}}'
            print(txt, file=open(EXPORT_FILE, 'w'))

    driver.close()

    print(f'Finished in {print_time(start_time, time.time())}\n')
    print(f'results: {Counter(final_results)}')
