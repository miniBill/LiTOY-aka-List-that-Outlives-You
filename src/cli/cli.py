#!/usr/bin/env python3.9
import re
import pandas as pd
import random
from pprint import pprint
import json
from prettytable import PrettyTable
from statistics import mean, stdev, median, StatisticsError
import sys
sys.path.append("../../")
sys.path.append("../")
from ..backend.log import log_
from user_settings import useless_last_years, useless_first_years, user_life_expected, user_age, disable_lifebar, col_red, col_gre, col_yel, col_rst, col_mgt_fg, col_blink, col_bold, col_uline, spacer, col_blu
from .get_terminal_size import get_terminal_size

def print_memento_mori():
    """
    Print a reminder to the user that life is short and times
    is always passing by faster as time goes on
    """
    if disable_lifebar is False:
        seg1 = useless_first_years
        seg2 = user_age - useless_first_years
        seg3 = user_life_expected - user_age - useless_last_years
        seg4 = useless_last_years
        resize = 1/user_life_expected*(sizex-17)
        if random.random() > 0.99:
            string = "REMEMBER THAT TIME IS RUNNING OUT"
            for i in range(5):
                color_set = [col_red, col_yel]*3
                random.shuffle(color_set)
                col_rdm = (col for col in color_set)
                print(f"{col_mgt_fg}{col_blink}{col_bold}{col_uline}", end="")
                print(f"{next(col_rdm)}{string}", end=spacer*2)
                print(f"{next(col_rdm)}{string}", end=spacer*2)
                print(f"{next(col_rdm)}{string}", end="")
                print(col_rst, end="\n")
        print("Your life (" + col_red + str(int((seg2)/(seg2 + seg3)*100)) +
              "%" + col_rst + ") : " + col_red + "x"*int(seg1*resize) +
              col_red + "X"*(int(seg2*resize)) + col_gre +
              "-"*(int(seg3*resize)) + col_yel + "_"*int(seg4*resize) +
              col_rst)


def side_by_side(rowname, a, b, space=2, col=""):
    """
    from https://stackoverflow.com/questions/53401383/how-to-print-two-strings-large-text-side-by-side-in-python
    """
    rowname = rowname.ljust(15)
    a = str(a)
    b = str(b)
    col_width = int((int(sizex)-len(rowname))/2-int(space)*2)
    inc = 0
    while a or b:
        inc += 1
        if inc == 1:
            print(str(col) + str(rowname) + " "*space + "|" +
                  a[:col_width].ljust(col_width) + " "*space +
                  "|" + b[:col_width] + col_rst)
        else:
            print(str(col) + " "*(len(rowname)+space) + "|" +
                  a[:col_width].ljust(col_width) + " "*space +
                  "|" + b[:col_width] + col_rst)
        a = a[col_width:]
        b = b[col_width:]


def format_length(to_format, reverse=False):
    "displays 120 minutes as 2h0m etc"
    if reverse is False:
        minutes = to_format
        if minutes == "X":
            return "X"
        minutes = float(minutes)
        hours = minutes // 60
        days = hours // 24
        if days == 0:
            days = ""
        else:
            hours = hours-days*24
            days = str(int(days))+"d"
        if hours == 0 :
            hours = ""
        else:
            minutes = minutes-hours*60
            hours = str(int(hours))+"h"
        minutes = str(int(minutes))+"min"
        length = days+hours+minutes
        return length
    else:
        length = 0
        days = re.findall("\d+[jd]", to_format)
        hours = re.findall("\d+h", to_format)
        minutes = re.findall("\d+m", to_format)
        if days:
            length += 1440*int(days[0][:-1])
        if hours:
            length += 60*int(hours[0][:-1])
        if minutes:
            length += int(minutes[0][:-1])
        return str(length)


def show_podium(df):
    "Show the highest ranked things to do in LiTOY "
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', sizex)
    pd.set_option('display.max_colwidth', int(sizex/2.6))
    if args["verbose"] is True:  # print all fields
        pprint(df.sort_values(by="gELO", ascending=False)[0:10])
    else:
        dfp = df.loc[:, ["content", "gELO", "iELO", "tELO",
                         "tags", "disabled", "metacontent"]
                     ][df["disabled"] == 0]
        dfp["media_title"] = [(lambda x: json.loads(x)["title"]
                               if "title" in json.loads(x).keys()
                               else "")(x)
                              for x in dfp.loc[:, "metacontent"]]
        pprint(dfp.loc[:,
                       ["media_title", "content",
                        "gELO", "iELO", "tELO", "tags"]
                       ].sort_values(by="gELO", ascending=False)[0:10])


def show_stats(df, printing=True):
    """
    shows statistics on the litoy database, but is also used to write at each
    launch the state of the database for later analysis
    """
    df = df.copy()
    df_nd = df[df['disabled'] == 0]
    df_virg = df[df['n_review'] == 0]
    df_nvirg = df[df['n_review'] != 0]
    try:
        table = PrettyTable()
        table.field_names = ["", "value"]
        table.align[""] = "l"
        table.align["value"] = "r"
        table.add_row(["Number of entries in LiTOY:", len(df)])
        table.add_row(["Number of non disabled entries in LiTOY:", len(df_nd)])
        table.add_row(["Number of entries that have never been reviewed:",
                       len(df_virg)])
        table.add_row(["Total number of review:",
                       round(df_nd.n_review.sum(), 1)])
        table.add_row(["Average number of review:",
                       round(df_nd['n_review'].mean(), 2)])

        table2 = PrettyTable()
        table2.field_names = ["", "average", "sd", "median"]
        table2.align[""] = "l"
        table2.align["average"] = "r"
        table2.align["sd"] = "r"
        table2.align["median"] = "r"
        table2.add_row(["Importance score:",
                       round(df_nd.iELO.mean(), 1),
                       round(df_nd.iELO.std(), 2),
                       round(median(df_nd.iELO), 2)])
        table2.add_row(["Time score:", round(df_nd.tELO.mean(), 1),
                       round(df_nd.tELO.std(), 2),
                       round(median(df_nd.tELO), 2)])
        table2.add_row(["Global score:", round(df_nvirg.gELO.mean(), 1),
                       round(df_nvirg.gELO.std(), 2),
                       round(median(df_nvirg.gELO), 2)])

        pooled = list(df_nd.DiELO + df_nd.DtELO)
        table2.add_row(["Delta scores:", round(mean(pooled), 1),
                       round(stdev(pooled), 2), round(median(pooled), 2)])
        table2.add_row(["K value:", round(df_nd.K.mean(), 1),
                       round(df_nd.K.std(), 2), round(df_nd.K.median())])
        table2.add_row(["Time spent reviewing:",
                        round(df_nd.review_time.sum(), 1),
                        round(df_nd.review_time.std(), 2),
                        round(median(df_nd.review_time), 2)])

        completion_score = round(mean([
                                       mean(pooled),
                                       median(pooled)
                                      ]
                                      ) / len(df_nd.index), 4)
        if printing is True:
            print(table)
            print("")
            print(table2)
            print(f"Progress score: {round(completion_score, 3):>20}")
            print("(lower is better)")
        else:
            table.border = False
            table2.border = False
            log_(str(table))
            log_(str(table2))
            log_(f"Progress score: {round(completion_score, 3):>20}")
    except StatisticsError as e:
        log_(f"Not enough data points! {e}", False)
        raise SystemExit()


def print_2_entries(id_left, id_right, mode, litoy, all_fields="no"):
    "Show the two entries to review side by side"
    global sizex, sizey
    (sizex, sizey) = get_terminal_size()  # dynamic sizing
    print(col_blu + "#"*sizex + col_rst)
    print_memento_mori()
    print(col_blu + "#"*sizex + col_rst)

    entry_left = litoy.df.loc[id_left, :].copy()
    entry_right = litoy.df.loc[id_right, :].copy()

    if all_fields != "all":
        side_by_side("ID", id_left, id_right)
        print("."*sizex)

        if "".join(entry_left.tags + entry_right.tags) != "":
            tag_left = ', '.join(json.loads(entry_left.tags))
            tag_right = ', '.join(json.loads(entry_right.tags))
            side_by_side("Tags", tag_left, tag_right)
            print("."*sizex)
        if int(entry_left.starred) + int(entry_right.starred) != 0:
            side_by_side("Starred", entry_left.starred, entry_right.starred,
                         col=col_yel)
            print("."*sizex)

        side_by_side("Entry", entry_left.content, entry_right.content)
        print("."*sizex)
        if mode == "importance":
            side_by_side("iELO", entry_left.iELO, entry_right.iELO)
            print("."*sizex)
        else:
            side_by_side("tELO",
                         entry_left.tELO, entry_right.tELO)
            print("."*sizex)
        side_by_side("K factor", entry_left.K, entry_right.K)

    # print all fields, useful for debugging
    if all_fields == "all":
        for c in litoy.df.columns:
            side_by_side(str(c), str(entry_left[c]), str(entry_right[c]))

    # metadata :
    js = []
    js.append(json.loads(entry_left.metacontent))
    js.append(json.loads(entry_right.metacontent))
    for x in [0, 1]:
        for y in ["length", "title", "url", "type", "channel"]:
            if y not in js[x].keys():
                js[x][y] = "X"
    if (js[0]["length"] + js[1]["length"]) != "XX":
        side_by_side("Length",
                     format_length(js[0]["length"]),
                     format_length(js[1]["length"]))
    if (js[0]["title"] + js[1]["title"]) != "XX":
        side_by_side("Title", js[0]["title"], js[1]["title"])
        print("."*sizex)
    if (js[0]["url"] + js[1]["url"]) != "XX":
        side_by_side("Location", js[0]["url"], js[1]["url"])
    if (js[0]["channel"] + js[1]["channel"]) != "XX":
        side_by_side("Channel", js[0]["channel"], js[1]["channel"])
    if (js[0]["type"] + js[1]["type"]) != "XX":
        side_by_side("Media type", js[0]["type"], js[1]["type"])

    print(col_blu + "#"*sizex + col_rst)
