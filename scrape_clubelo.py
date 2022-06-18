from turtle import home
from bs4 import BeautifulSoup
import requests
from pprint import pprint
import functools

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
}
response = requests.get("http://clubelo.com/2002-06-16/CRO/Games", headers=headers)

cols = {
    "HOME_FLAG": 0,
    "DATE": 10,
    "HOME_TEAM": 20,
    "HOME_ELO": 180,
    "AWAY_FLAG": 215,
    "AWAY_TEAM": 235,
    "AWAY_ELO": 395,
    "HOME_ODDS": 520,
    "DRAW_ODDS": 550,
    "AWAY_ODDS": 580,
    "HOME_GOALS": 615,
    "AWAY_GOALS": 625,
    "HOME_IMPROV": 675,
}

soup = BeautifulSoup(response.text, "lxml")

# Sort data into corresponding columns

svg = soup.find_all("svg")[1]
x_ax = []
x_ax_dict = {}
for child in svg.children:
    if 'x="' in str(child):
        newc = str(child).split('x="')[1].split('"')[0]
        x_ax.append(int(newc))
        if int(newc) not in x_ax_dict.keys():
            x_ax_dict[int(newc)] = []
        y = str(child).split('y="')[1].split('"')[0]
        x_ax_dict[int(newc)].append((int(float(y)), child))

# Declare column variables

home_team = x_ax_dict[cols["HOME_TEAM"]]
away_team = x_ax_dict[cols["AWAY_TEAM"]]
home_flag = x_ax_dict[cols["HOME_FLAG"]]
away_flag = x_ax_dict[cols["AWAY_FLAG"]]
home_elo = [(elem[0], int(elem[1].string)) for elem in x_ax_dict[cols["HOME_ELO"]]]
away_elo = [(elem[0], int(elem[1].string)) for elem in x_ax_dict[cols["AWAY_ELO"]]]
home_odds = [
    (elem[0], int(elem[1].string.strip("%"))) for elem in x_ax_dict[cols["HOME_ODDS"]]
]
away_odds = [
    (elem[0], int(elem[1].string.strip("%"))) for elem in x_ax_dict[cols["AWAY_ODDS"]]
]
draw_odds = [
    (elem[0], int(elem[1].string.strip("%"))) for elem in x_ax_dict[cols["DRAW_ODDS"]]
]
home_goals = [(elem[0], int(elem[1].string)) for elem in x_ax_dict[cols["HOME_GOALS"]]]
away_goals = [(elem[0], int(elem[1].string)) for elem in x_ax_dict[cols["AWAY_GOALS"]]]
date = [(elem[0], elem[1].string) for elem in x_ax_dict[cols["DATE"]]]

# Sort columns


def sort_this(first, second):
    return first[0] - second[0]


for (i, flag) in enumerate(home_flag):
    home_flag[i] = (flag[0], str(flag[1]).split('href="')[1].split('"')[0])

for (i, flag) in enumerate(away_flag):
    away_flag[i] = (flag[0], str(flag[1]).split('href="')[1].split('"')[0])

home_team.sort(key=functools.cmp_to_key(sort_this))
away_team.sort(key=functools.cmp_to_key(sort_this))
home_flag.sort(key=functools.cmp_to_key(sort_this))
away_flag.sort(key=functools.cmp_to_key(sort_this))
home_elo.sort(key=functools.cmp_to_key(sort_this))
away_elo.sort(key=functools.cmp_to_key(sort_this))
home_odds.sort(key=functools.cmp_to_key(sort_this))
draw_odds.sort(key=functools.cmp_to_key(sort_this))
away_odds.sort(key=functools.cmp_to_key(sort_this))
home_goals.sort(key=functools.cmp_to_key(sort_this))
away_goals.sort(key=functools.cmp_to_key(sort_this))
date.sort(key=functools.cmp_to_key(sort_this))

# Data binding

pairs = []

for elem in home_team:
    for elem2 in away_team:
        if elem[0] == elem2[0]:
            pairs.append((elem[0], elem[1].string, elem2[1].string))
            break
j_date = 1
for i in range(100):
    y = pairs[i][0]
    while j_date < len(date) and y > date[j_date][0]:
        j_date += 1
    pairs[i] = (pairs[i][0], date[j_date - 1][1], pairs[i][1], pairs[i][2])

for (i, ((_, home), (__, away))) in enumerate(zip(home_goals, away_goals)):
    pairs[i] = pairs[i] + (home, away)

for (i, ((_, home), (__, away))) in enumerate(zip(home_elo, away_elo)):
    pairs[i] = pairs[i] + (home, away)

to_erase = []
for flag1, flag2 in zip(home_flag, away_flag):
    if flag1[1] != flag2[1]:
        to_erase.append(flag1[0] + 9)


for pair in pairs:
    if pair[0] in to_erase:
        pairs.remove(pair)

odds = []

for (i, ((y, home), (__, draw), (___, away))) in enumerate(
    zip(home_odds, draw_odds, away_odds)
):
    if y not in to_erase:
        n = home + draw + away
        odds.append((home / n, draw / n, away / n))

for (i, pair) in enumerate(pairs):
    pairs[i] = pair + odds[i]

# Data writing

f = open("file.csv", "a")
for line in pairs:
    f.write(str(line[1:]) + "\n")
f.close()
