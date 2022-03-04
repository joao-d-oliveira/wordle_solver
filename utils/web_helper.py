import time

import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from wordleSolver import filter_words


def get_words_with_pattern_url_aux(pattern):
    from selenium import webdriver
    from bs4 import BeautifulSoup

    # Making a GET request
    url = f'https://wordsolver.net/solve#!q={pattern.upper().replace("?", "%3F")}'
    url += "&f=&ftype=f_none&dic=d_twl&type=st_anagram&ml=5"

    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-dev-sh-usage')

    driver = webdriver.Chrome('../chromedriver', options=option)
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    html_txt = soup.text

    return html_txt


def get_words_with_pattern_url(pattern, okletters='', notokletters='', okpattern='', nokpattern=[], letters='', verbose=False):
    html_txt = ''
    words = []
    loop = 0
    while '5 letter words' not in html_txt or len(words) == 0:
        if pattern.count('?') < 3: html_txt = get_words_with_pattern_url_aux(pattern)
        else:
            pattern = okletters + letters[loop + 1:5 + 1 + loop - len(okletters)]
            loop += 1

        inx = pattern.find('?')
        if inx == -1: pattern = pattern[:-1] + '?'
        else: pattern = pattern[:inx - 1] + '?' * (5 - inx + 1)

        if '5 letter words' in html_txt:
            if '4 letter words' not in html_txt or html_txt.find('3 letter words') < html_txt.find('4 letter words'):
                next_lett = '3'
            else:
                next_lett = '4'

            words = html_txt[html_txt.find('5 letter words') + len('5 letter words'):html_txt.find(f'{next_lett} letter words')]
            words = words.replace('\n', '').replace('.', '')
            words = [w.strip() for w in words.split(',')]
            words = filter_words(words, okletters, notokletters, okpattern, nokpattern, verbose)

    return words


def get_words_with_pattern_local(corpus, okletters='', notokletters='', nokpattern=[], letters='', pattern_ori=''):
    words = []
    loop, n_letters = 0, 5 - len(okletters)

    corpus_l = list(corpus.keys()) if type(corpus) == dict else corpus
    corpus_filtered = filter_words(words=corpus_l, okletters=okletters, notokletters=notokletters, nokpattern=nokpattern, okpattern=pattern_ori)
    okletters_ = ''

    while len(words) == 0:
        if okletters_ == okletters:
            loop += 1
            n_letters = 5 - len(okletters)

        okletters_ = okletters + letters[loop:loop + n_letters]

        n_letters -= 1

        words = filter_words(words=corpus_filtered, okletters=okletters_, notokletters=notokletters, okpattern=pattern_ori, nokpattern=nokpattern)

    return words


def get_initial_driver():
    from selenium import webdriver

    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-dev-sh-usage')

    driver = webdriver.Chrome('../chromedriver', options=option)

    return driver


def get_initial_page(driver, url):
    driver.get(url)

    try:
        body = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'board'))  # This is a dummy element
        )
    finally:
        body = None

    body = driver.find_element(by=By.TAG_NAME, value='body')

    return body


def send_try(body_elem, trial, enter=True):
    from selenium.webdriver.common.keys import Keys

    body_elem.send_keys(trial)
    if enter: body_elem.send_keys(Keys.ENTER)


def process_results(driver, row):
    dict_res = {'wrong': -1, 'misplaced': 0, 'correct': 1}

    def find(driver):
        rows = driver.find_elements(by=By.CLASS_NAME, value='row-index')
        if len(rows) <= row: return False

        letters = rows[row].find_elements(by=By.CLASS_NAME, value='letter-box')

        return not all([l.get_dom_attribute('class') == 'letter-box' for l in letters])

    try:
        elem = WebDriverWait(driver, 10).until(find)
    except selenium.common.exceptions.TimeoutException:
        return -1
    finally:
        elem = None

    rows = driver.find_elements(by=By.CLASS_NAME, value='row-index')

    if len(rows) < row: Exception(f'Error: couldnt find row yet... some problem. ({row})')
    letters = rows[row].find_elements(by=By.CLASS_NAME, value='letter-box')

    if all([l.get_dom_attribute('class') == 'letter-box' for l in letters]):
        time.sleep(5)
        letters = rows[row].find_elements(by=By.CLASS_NAME, value='letter-box')

    results = [dict_res[l.get_dom_attribute('class').split(' ')[1]] for l in letters]

    return results


def debug_print_page(driver, filename='examp0.html'):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    print(soup, file=open('examp0.html', 'w+'))


