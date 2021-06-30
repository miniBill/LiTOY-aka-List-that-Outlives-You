#!/usr/bin/env python3.9

###############################################################################
# Summary of each section
# 0. Banner and license
# 1. User defined settings
# 2. fonctions etc
# 3. Main routine

###############################################################################
# 0. Banner and license

###################################################################
#     __    _ ____________  __                                    #
#    / /   (_)_  __/ __ \ \/ /                                    #
#   / /   / / / / / / / /\  /                                     #
#  / /___/ / / / / /_/ / / /                                      #
# /_____/_/ /_/  \____/ /_/                                       #
#   ________            __    _      __     ________          __  #
#  /_  __/ /_  ___     / /   (_)____/ /_   /_  __/ /_  ____ _/ /_ #
#   / / / __ \/ _ \   / /   / / ___/ __/    / / / __ \/ __ `/ __/ #
#  / / / / / /  __/  / /___/ (__  ) /_     / / / / / / /_/ / /_   #
# /_/ /_/ /_/\___/  /_____/_/____/\__/    /_/ /_/ /_/\__,_/\__/   #
#    ____        __  ___                    __  __                #
#   / __ \__  __/ /_/ (_)   _____  _____    \ \/ /___  __  __     #
#  / / / / / / / __/ / / | / / _ \/ ___/     \  / __ \/ / / /     #
# / /_/ / /_/ / /_/ / /| |/ /  __(__  )      / / /_/ / /_/ /      #
# \____/\__,_/\__/_/_/ |___/\___/____/      /_/\____/\__,_(_)     #
#                                                                 #
###################################################################

###############################################################################
# Released under the GNU Lesser General Public License v2.                    #
# Copyright (C) - 2021 - user "thiswillbeyourgithub" of the website "github". #
# This file is part of LiTOY : a tool to help organiser various goals over    #
# time.                                                                       #
#                                                                             #
# LiTOY is free software: you can redistribute it and/or modify               #
# it under the terms of the GNU Lesser General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# LiTOY is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU Lesser General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the GNU Lesser General Public License    #
# along with LiTOY.  If not, see <https://www.gnu.org/licenses/>.             #
#                                                                             #
# for more information or to get the latest version go to :                   #
# https://github.com/thiswillbeyourgithub/LiTOY                               #
###############################################################################


###############################################################################
# 1. User defined settings

# lifebar arguments :
disable_lifebar     = "no"
useless_first_years = 13
user_age            = 24
user_life_expected  = 90
useless_last_years  = 20


# for reading time estimation :
wpm = 200
average_word_length = 6

# used when comparing
questions = {
        "importance": "What steps will make you likely to achieve your goals?\
\n* Which is more important?\n* If you had one hour to spend,\
which would bring you more in your life?",
        "time": "Which task takes the less time to complete?",
        }

shortcuts = {
        "skip_review"                 :  ["s","-"],
        "answer_level"               :  ["1","2","3","4","5","a","z","e","r","r","t"],
        "editLeft"                   :  ["e"],
        "editRight"                  :  ["E"],
        "undo"                       :  ["u"],
        "show_more_fields"           :  ["M"],
        "starLeft"                   :  ["x"],
        "starRight"                  :  ["X"],
        "disableLeft"                :  ["d"],
        "disableRight"               :  ["U"],
        "open_mediaLeft"             :  ["o"],
        "open_mediaRight"            :  ["O"],
        "show_help"                  :  ["h","?"],
        "quit"                       :  ["q"]
        }

# ELO :
K_values           =  [100, 50, 25, 15, 10]  # default [100, 50, 25, 15, 10]
default_score      =  1000  # default 1000
global_weights     =  (2, 1)  # global score is 1st number*iELO + 2nd*tELO

headers = {"User-Agent": "Mozilla/5.0"}  # to avoid getting flagged for abusive web scraping


###############################################################################
# 2. Initialization, definitions etc

# imports
import argparse
import pandas as pd
import logging as lg
from logging.handlers import RotatingFileHandler
import argparse
import random
import requests
from pathlib import Path
from pprint import pprint
from tqdm import tqdm
from Levenshtein import distance as lev
import pdftotext
from itertools import chain
import youtube_dl
import time
from bs4 import BeautifulSoup
import math
import json
import pdb
import get_wayback_machine
from contextlib import suppress


global cols
cols = ["ID", "date", "content", "metacontent", "tags",
               "starred", "iELO", "tELO", "DiELO", "DtELO", "gELO",
               "compar_time", "n_comparison", "K", "disabled"]
# iELO stands for "importance ELO", DiELO for "delta iELO",
# gELO for "global ELO", etc


# used to make the whole script interruptible using ctrl+c
# you can then resume using 'c'
def debug_signal_handler(signal, frame):
    import pdb
    pdb.set_trace()
import signal
signal.signal(signal.SIGINT, debug_signal_handler)


# misc functions
def log_(string, onlyLogging=True):
    "appends string to the logging file and sometimes also print it"
    lg.info(f"{time.asctime()}: {string}")
    if onlyLogging is False:  # TODO remove this as it was used for debugging
    #if onlyLogging is False or 1==1:  # TODO remove this as it was used for debugging
        #pprint(string)  # TODO, might change this later
        tqdm.write(string)


def checkIfFileAndDB(path):
    "checks if the file and database already exists, if not create the file"
    db_location = Path(path)
    if db_location.exists():
        log_(f"Database file found at {path}", False)
        try:
            return True
        except ValueError as e:
            log_(f"Litoy database not found in file at {path} : {e}", False)
            return None
    else:
        answer = input(f"No database file found at {path}, do you want me to create it?\ny/n?")
        if answer in "yes":
            db_location.touch()
            return None
        else:
            print("Exiting")
            raise SystemExit()


def importFromFile(path):
    "checks if text file exists then import it into LiTOY"
    import_file = Path(path)
    if not import_file.exists():
        log_(f"Import file not found at {path}, exiting", False)
        raise SystemExit()
    log_(f"Importing from file {path}", False)
    with import_file.open() as f:
        lines = f.readlines()
    random.shuffle(lines)  # TODO remove when you're done
    for line in tqdm(lines, desc="Processing each line", unit="Line",
                     ascii=False, dynamic_ncols=True, mininterval=1):
        line.strip()
        line = line.replace("\n", "")
        if not litoy.checksIfEntryExists(litoy.df, line):
            new_df = add_new_entry(litoy.df, line)
            litoy.save_to_file(new_df)
        else:
            log_(f"Line already exists in the litoy database : {line}", False)


def wrong_arguments_(args):
    "used to exit while printing arguments"
    print("Exiting because called with wrong arguments :")
    pprint(args)
    raise SystemExit()


def add_new_entry(df, content):
    "add a new entry to the pandas dataframe"
    tags = get_tags_from_content(content)
    metacontent = get_meta_from_content(content)

    with suppress(KeyError):  # in case metacontent doesn't contain those keys
        # if url not working, reload it after 5 seconds
        if "forbidden" in str(metacontent['title'].lower()) or \
                "404" in str(metacontent['title'].lower()) or\
                "403" in str(metacontent['title'].lower()):
            log_(f"Waiting 5 seconds because apparent webpage loading limit was reached while inspecting line : {content}", False)
            time.sleep(5)
            metacontent = get_meta_from_content(content)
        # if wayback machine was used : mention it in the tags
        if metacontent['wayback_used'] == "1":
            tags.append("wayback_machine")
        elif metacontent['wayback_machine'] == "wayback url not found":
            tags.append("url_not_found")
        metacontent.pop("wayback_used")

    try:
        newID = max(df['ID'])+1
    except ValueError:  # first card
        newID = 1
    df2 = df.append({
            "ID": newID,
            "date": str(time.time()),
            "content": content,
            "metacontent": json.dumps(metacontent),
            "tags": json.dumps(sorted(tags)),
            "iELO": default_score,
            "tELO": default_score,
            "DiELO": default_score,
            "DtELO": default_score,
            "gELO": compute_global_score(default_score, default_score),
            "compar_time": 0,
            "K": sorted(K_values)[-1],
            "starred": "No",
            "disabled": 0,
            }, ignore_index=True)
    return df2


def pick_entries(df):
    """
    picks entries before a comparison : the left one is chosen randomly
    among those with the highest K factor, then 10 other entries are selected
    at random
    """
    highest_K = max(df['K'])

    picked = []
    picked.append(df.loc[ (df['K'] == highest_K) & (df['disabled'] == 0)].sample(1)["ID"].loc[0])
    picked.extend(df.loc[ (df['disabled'] == 0) ].sample(min(10, len(df.index)-1))["ID"])

    while picked[0].iloc[0] in list(picked[1:]):
        log_("Picking entries one more time")
        picked = pick_entries(df)
    return picked


def print_2_entries(id_left, id_right, all_fields=False):
    """
    shows the two entries that are to be compared
    """
    print(id_left)
    print(id_right)
    breakpoint()
    for i in [id_left, id_right]:
        entry = litoy.df["ID" == i]
        pprint(entry[["ID", "content", "tags", "starred", "iELO", "tELO"]])
        d = entry['metacontent'].to_dict()
        pprint(d)
        print("###########################################")


def show_podium(df):
    """
    shows the highest ranked things to do in LiTOY
    """
    df2 = df.sort_values(by="gELO")[0:5]
    pprint(df2)


def show_stats(df):
    "shows statistics on the litoy database"
    log_("Printing statistics", False)
    df = litoy.df
    df_not_disabled = df[ df['disabled'] == 0 ]
    pprint(f"Number of entries in LiTOY : {len(df)}, non disabled entries only : {len(df_not_disabled)}")
    pprint(f"Average importance score : {df_not_disabled['iELO'].mean()}, time score : {df_not_disabled['tELO'].mean()}") 
    pprint(f"Average global score : {df_not_disabled['gELO'].mean()}") 
    pprint(f"Average K value : {df_not_disabled['K'].mean()}")
    pprint(f"Time spent comparing : {df_not_disabled['compar_time'].sum()}")
    pprint(f"Number of comparison : {df_not_disabled['n_comparison'].sum}, average : {df_not_disabled['n_comparison'].mean()}")


def print_syntax_examples():
    "shows the user usage example of LiTOY"
    # TODO
    log_("Printing syntax example", False)


def rlinput(prompt, prefill=''): 
    "prompt the user using prefilled text"
    # https://stackoverflow.com/questions/2533120/show-default-value-for-editing-on-python-input-possible
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    readline.parse_and_bind("tab: complete")
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()

def shortcut_and_action(entries): 
    """
    makes the link between keypresses and actions
    shortcuts are stored at the top of the file
    """
    def get_action(input):   # get action from the keypress pressed
        found = ""
        for action, keypress in shortcuts.items():
            if str(input) in keypress:
                if found != "":
                    log_("Several corresponding shortcuts found! Quitting.", False)
                    raise SystemExit()
                found = action
        if action == "":
            log_(f"No {str(input)} shortcut found", False)
            action = "show_help"
        return found

    action = ""
    while True:
        start_time = time.time()  # to get time elapsed

        if action == "exit_outerloop":  # not a shortcut, but used as a way
            # to exit the while loop
            # not to be confused with "quit"
            break
        action = ""

        log_(f"Shortcut : asking question, mode = {str(mode)}", False)
        print(f"{questions[mode]} (h or ? for help)")
        keypress = input()
        log_(f"Shortcut : User typed : {keypress}", False)

        if keypress not in list(chain.from_iterable(shortcuts.values())):
            log_(f"Shortcut Error : keypress not found : {keypress}")
            action = "show_help"
        else :
            action = str(get_action(keypress))
            log_(f"Shortcut : Action={action}", False)

        if action == "answer_level" : # where the actual comparison takes place
            if keypress=="a": keypress="1"
            if keypress=="z": keypress="2"
            if keypress=="e": keypress="3"
            if keypress=="r": keypress="4"
            if keypress=="t": keypress="5"

            # TODO


        if action == "skip_review":
            log_("Shortcut : Skipped review")
            break

        if action == "show_more_fields":  # display all the fields from a card
            log_("Shortcut : displaying the entries in full", False)
            print("\n"*10)
            print_2_entries(entries, mode, "all") 
            continue

        if action == "editLeft":  # edit field of the left card
            #TODO
            pass

        if action == "editRight":  # edit field of the right card
            #TODO
            pass

        if action == "undo":
            # TODO
            pass

        if action == "open_mediaLeft":
            # TODO
            pass

        if action == "open_mediaRight":
            # TODO
            pass

        if action == "starLeft":  # useful to get back to it to edit etc after a review
            # TODO
            pass

        if action == "starRight":  # useful to get back to it to edit etc after a review
            # TODO
            pass

        if action == "disable":  # disable an entry
            # TODO
            pass

        if action == "show_help":
            log_("Shortcut : showing help", False)
            pprint(shortcuts)
            continue

        if action == "quit":
            log_("Shortcut : quitting")
            print("Quitting.")
            raise SystemExit()
        break


# functions related to one entry
def get_tags_from_content(string):
    "extracts tags from a line in the import file"
    splitted = string.split(" ")
    result = []
    for word in splitted:
        if word.startswith("tags:"):
            result.append(word[5:])
    return list(set(result))


def get_meta_from_content(string):
    """
    extracts all metadata from a line in the import file
    this does not include tags, which are indicated using tags:sometag in the
    line. Instead it's for example the length of a youtube video which link
    appears in the content.
    If several links are supplied, only the first one will be used
    """
    with suppress(UnboundLocalError):
        since = time.time() - last
        last = time.time()
        if since < 2:
            tqdm.write("Sleeping 2 seconds")
            time.sleep(2-since)

    splitted = string.split(" ")
    for word in splitted:
        if word == "type:video":  # this forces to analyse as a video
            for word in splitted:
                if word.startswith("http") or word.startswith("www."):
                    log_(f"Extracting info from video {word}")
                    return extract_youtube(word)

        if word.startswith("http") or word.startswith("www."):
            if "ytb" in word or "youtube" in word:
                log_(f"Extracting info from video {word}")
                return extract_youtube(word)

            if word.endswith(".pdf"):
                log_(f"Extracting pdf from {word}")
                return extract_pdf_url(word)

            # if here then is probably just an html and should be treated as text
            log_(f"Extracting text from webpage {word}")
            return extract_webpage(word)

        elif "/" in word:  # might be a link to a file
            if word.endswith(".pdf"):
                log_(f"Extracting pdf from {word}")
                return extract_pdf_local(word)

            if word.endswith(".md") or word.endswith(".txt"):
                log_(f"Extracting data from {word}")
                return extract_txt(word)
        else:
            log_(f"No metadata were extracted for {word}")
            res_dic = {"type": "not found", "url": word}
            return res_dic


def extract_youtube(url):
    "extracts video duration in minutes from youtube link, title etc"
    with youtube_dl.YoutubeDL({"quiet": True}) as ydl:
        video = ydl.extract_info(url, download=False)
    try:
        res = {"type": "video",
               "length": str(round(video['duration']/60, 1)),
               "title": video['title'],
               "url": url}

    # I had to used this because the exception was never caught
    except KeyError as e:
        log_(f"Video link skipped because : error during information extraction from {url} : {e}", False)
        res.update({"type": "video not found", "url": url})
    except youtube_dl.utils.DownloadError as e:
        log_(f"Video link skipped because : error during information extraction from {url} : {e}", False)
        res.update({"type": "video not found", "url": url})
    except youtube_dl.utils.ExtractorError as e:
        log_(f"Video link skipped because : error during information extraction from {url} : {e}", False)
        res.update({"type": "video not found", "url": url})
    return res


def extract_pdf_url(url):
    "extracts reading time from an online pdf"
    downloaded = requests.get(url, headers=headers)
    open("./.temporary.pdf", "wb").write(downloaded.content)
    temp_dic = extract_pdf_local("./.temporary.pdf")
    temp_dic["type"] = "online pdf"
    Path("./.temporary.pdf").unlink()
    return temp_dic

def extract_pdf_local(path):
    "extracts reading time from a local pdf file"
    try:
        with open(path, "rb") as f:
            text_content = pdftotext.PDF(f)
            text_content = " ".join(text_content).replace("\n", " ")
    except FileNotFoundError:
        log_(f"Cannot find {path}, I thought it was a PDF", False)
        return {"type": "pdf not found",
                "url": path}

    total_words = len(text_content)/average_word_length
    estimatedReadingTime = str(round(total_words/wpm,1))

    title = path.split(sep="/")[-1]
    res = {"type": "local pdf",
            "length": estimatedReadingTime,
            "title": title,
            "url": path}
    return res


def extract_txt(path):
    "extracts reading time from a text file"
    try:
        txt_file = Path(path)
        with txt_file.open() as f:
            lines = f.readlines()
        text_content = ' '.join(lines).replace("\n", " ")

        total_words = len(text_content)/average_word_length
        estimatedReadingTime = str(round(total_words/wpm,1))

        title = path.split(sep="/")[-1]
        res = {"type": "text",
                "length": estimatedReadingTime,
                "title": title}
        return res

    except ValueError as e:
        log_(f"Cannot find {path} : {e}", False)
        res = {"type": "txt file not found",
                "url": path} 
        return res

def extract_webpage(url):
    """
    extracts reading time from a webpage, output is a tupple containing 
    estimation of the reading time ; title of the page ; if the wayback
    machine was used
    """
    try :
        wayback_used = 0
        res = requests.get(url, headers=headers)
    except requests.exceptions.ConnectionError:
        # if url is dead : use wayback machine
        tqdm.write(f"Using the wayback machine for {url}")
        wayback_used = 1
        wb = get_wayback_machine.get(url)
        try:  # if url was never saved
            url = wb.links['last memento']['url']
        except (requests.exceptions.ConnectionError, AttributeError) as e:
            log_(f"Url could not be found even using wayback machine : {url} : {e}", False)
            res = {"title": "Not found",
                   "length": "-1",
                   "used_wayback_machine": "wayback url no found"}
            return res
        res = requests.get(url, headers=headers)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    text_content = ' '.join(soup.find_all(text=True)).replace("\n", " ")

    for t in soup.find_all('title'):
        title = t.get_text()

    total_words = len(text_content)/average_word_length
    estimatedReadingTime = str(round(total_words/wpm, 1))
    res = {"title": title,
            "type": "webpage",
            "length": estimatedReadingTime,
            "used_wayback_machine": wayback_used,
            "url": url}
    if res['length'] == "-1":
        res.pop("length")
        res.pop("title")
        res["type"] = "not found"
    return res

# functions related to scores
def expected_elo(elo_A, elo_B, Rp=100):
    '''
    Calculate expected score of A in a best of 3 match against B
    Expected score of B in a best of 3 match against A is given by
    1-expected(A,B,Rp). For each Rp rating points of advantage over the 
    opponent, the expected score is magnified ten times in comparison to
    the opponent's expected score
    '''
    log_(f"Expected : A={str(elo_A)} B={str(elo_B)} Rp={str(Rp)}")
    result = 3 / (1 + 10 ** ((elo_B - elo_A) / Rp))
    log_(f"Expected : result={tr(result)}")
    return int(result)


def update_elo(elo, exp_score, real_score, K):
    "computes the ELO score"
    log_(f"Update_elo : elo={str(elo)} expected={str(exp_score)}\
            real_score={str(real_score)} K={str(K)}")
    result = elo + K*(real_score - exp_score)
    log_(f"Update_elo : result={str(result)}")
    return int(result)

def adjust_K(K0):
    """
    lowers the K factor of the card after at each comparison
    until lowest value is reached
    """
    K0 = int(K0)
    log_(f"Adjust_K : K0={str(K0)}", False)
    if K0 == K_values[-1] :
        log_(f"Adjust_K : K already at last specified value :\
                {str(K0)}={str(K_values[-1])}", False)
        return str(K0)
    for i in range(len(K_values)-1):
        if int(K_values[i]) == int(K0) :
            log_(f"New K_value : {str(K_values[i+1])}", False)
            return K_values[i+1]
    if K0 not in K_values:
        log_(f"error : K not part of K_values : {str(K0)}, reset to\
                {str(K_values[-1])}", False)
        return str(K_values[-1])
    log_("This should never print")
    raise SystemExit()  # should not be encounted

def compute_global_score(iELO, tELO):
    return int(global_weights[0]*int(iELO) +  global_weights[1]*int(tELO))


# class
class LiTOYClass:
    "Class that interacts with the database using panda etc"
    def __init__(self, db_path):
        if db_path is None:
            db_path = args['litoy_db']
            self.path = db_path
            self.create_database()
        else:
            self.path = db_path
        self.df = pd.read_excel(db_path)

    def reload_df(self):
        self.df = pd.read_excel(self.path)

    def save_to_file(self, df):
        Excelwriter = pd.ExcelWriter(args['litoy_db'] , engine="xlsxwriter")
        df.to_excel(Excelwriter, sheet_name="LiTOY", index=False)
        Excelwriter.save()
        self.reload_df()

    def create_database(self):
        df = pd.DataFrame(columns=cols)
        self.save_to_file(df)
        self.reload_df()

    def checksIfEntryExists(self, df, text):
        for present in df['content']:
            present.strip()
            present = present.replace("\n", "")
            # tries to avoid computing levenshtein distance for nothing
            if abs(len(present)-len(text)) <= 10 and\
                    lev(text, present) <= max(7, 0.1*len(present)):
                tqdm.write("Line already present in database : {text}")
                return True
            else:
                return False

    def get_tags(self, df):
        tag_list = []
        for i in df.index:
            tag_list.append(i['tags'])
        return sorted(list(set(tag_list)))

    def print_all_entries(self, df, pretty=True):
        for i in df.index:
            if pretty is True:
                pprint(df.iloc[i])
            else:
                print(df.iloc[i])


# arguments
parser = argparse.ArgumentParser()
parser.add_argument("--import-from-file", "-i",
        nargs="?",
        metavar = "import_path",
        dest='to_import_loc',
        type = str,
        required=False,
        help = "path of the text file to import to litoy database")
parser.add_argument("--litoy-db", "-l",
        nargs = "?",
        metavar = "litoy_db",
        dest='litoy_db',
        type = str,
        required=False,
        help = "path to the litoy database")
parser.add_argument("--add", "-a",
        nargs = "?",
        type = str,
        metavar='new_entry',
        dest='entry_to_add',
        required=False,
        help = "directly add an entry by putting it inside quotation mark\
        like so : python3 ./__main__.py -a \"do this thing tags:DIY, I\
        really need to do it that way\"")
parser.add_argument("--review", "-r",
        dest='review_mode',
        required=False,
        action="store_true",
        help = "use this to enable review mode instead of importation etc")
#parser.add_argument("--mode", "-m",
#        nargs = "?",
#        metavar = "mode",
#        dest='mode',
#        type = str,
#        required=False,
#        help = "comparison mode, can be either \'importance\' or \'time\'")

###############################################################################
# 3. Main routine


if __name__ == "__main__":
    lg.basicConfig(level=lg.INFO,
            filename = 'logs/rotating_log',
            filemode='a',
            format='%(asctime)s: %(message)s')
    #https://stackoverflow.com/questions/24505145/how-to-limit-log-file-size-in-python
    log = lg.getLogger()
    handler = RotatingFileHandler("logs/rotating_log", maxBytes=20*1024*1024, backupCount=20)
    log.addHandler(handler)

    args = parser.parse_args().__dict__

    # checks if the arguments are sane
    if args['litoy_db'] is None:
        wrong_arguments_(args)
    if args['to_import_loc'] is None and args['litoy_db'] is None:
        wrong_arguments_(args)
    if args['review_mode'] is True and args['to_import_loc'] is not None:
        wrong_arguments_(args)

    if checkIfFileAndDB(args['litoy_db']) is None:
        litoy = LiTOYClass(None)
    else:
        litoy = LiTOYClass(args['litoy_db'])

    if args['to_import_loc'] is not None:
        importFromFile(args['to_import_loc'])
        log_("Done importing from file, exiting", False)
        raise SystemExit()

    if args['review_mode'] is not None:
        n = len(litoy.df.index)
        if n < 10:
            log_(f"You only have {n} item in your database, add more to start \
                    using LiTOY!", False)
            raise SystemExit()
        picked = pick_entries(litoy.df)
        for i in picked[1:]:
            print_2_entries(picked[0], i)
            print("?", end="")
            print("done")
            raise SystemExit()
            shortcut_and_action(picked[0], picked[1].loc[i])


# TODOS :
# * respect pep8
# * use type hints from the beginning
# * use docstrings everywhere
# * use mypy
# * store metadata of litoy into the log file : average k and average score
