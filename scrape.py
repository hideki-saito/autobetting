import re

import requests
from bs4 import BeautifulSoup

def output_content(text):
    f = open('content.txt', 'w')
    f.write(text)
    f.close()


def get_dates(date_range):

    from dateutil import rrule, parser

    date1 = date_range[0]
    date2 = date_range[1]

    dates = list(rrule.rrule(rrule.DAILY,
                             dtstart=parser.parse(date1),
                             until=parser.parse(date2)))

    return dates

def calculation_score(htmlTag_list):
    score_list = []
    for score_tag  in htmlTag_list:
        score = score_tag.text.strip()
        if score == "":
            pass
        elif len(score) > 1:
            score_list.append(str(score[0]+"^"+str(score[1])))
        else:
            score_list.append(score)

    score = "|".join(score_list)

    return score

def extraData(url):

    r = s.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    surfaceString = soup.findAll('div', attrs={'class':'box boxBasic lGray'})[1].text.strip()
    surface = surfaceString.split(',')[-1]

    nameTags = soup.findAll('th', attrs={'class':'plName'})
    nameList = []
    for nameTag in nameTags:
        nameList.append(nameTag.text.strip())

    Name1 = " / ".join(list(nameList[i] for i in range(0,len(nameList)) if i%2==0 ))
    Name2 = " / ".join(list(nameList[i] for i in range(0,len(nameList)) if i%2==1 ))

    return surface, Name1, Name2

def get_data(url, date):

    day_data = []
    r = s.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    result_rows = soup.find('table', attrs={'class':'result'}).findAll('tr')

    tournament_rowIndex = []
    for index in range(0, len(result_rows)):
        if 'head' in result_rows[index].get('class'):
            tournament_rowIndex.append(index)

    tournament_rowIndex.append(len(result_rows))
    for index_index in range(0, len(tournament_rowIndex)-1):
        tournament = result_rows[tournament_rowIndex[index_index]].td.text.strip()
        print tournament

        try:
            tournament_url = domain + result_rows[tournament_rowIndex[index_index]].td.a.get('href')
        except Exception:
            tournament_url = ''

        single_atp = result_rows[tournament_rowIndex[index_index]].td.findAll('span')[1].get('class')
        if 'women' in single_atp[0]:
            is_atp = 'False'
        else:
            is_atp = 'True'

        if '2' in single_atp[0]:
            is_singles = 'True'
        else:
            is_singles = 'False'

        tournament_data = []
        for row_index in range(tournament_rowIndex[index_index]+1,tournament_rowIndex[index_index+1],2):

            time = result_rows[row_index].td.text.strip()

            player1 = result_rows[row_index].find('td', attrs={'class':"t-name"}).text.strip()
            player1_url = domain + result_rows[row_index].find('td', attrs={'class':"t-name"}).a.get('href')
            score1_tags = result_rows[row_index].findAll('td', attrs={'class':"score"})
            score1 = calculation_score(score1_tags)

            player2 = result_rows[row_index+1].find('td', attrs={'class':"t-name"}).text.strip()
            player2_url = domain + result_rows[row_index+1].find('td', attrs={'class':"t-name"}).a.get('href')
            score2_tags = result_rows[row_index+1].findAll('td', attrs={'class':"score"})
            score2 = calculation_score(score2_tags)

            odds1 = result_rows[row_index].find('td', attrs={'class':"coursew"}).text.strip()
            odds2 = result_rows[row_index].find('td', attrs={'class':"course"}).text.strip()

            match_url = domain + result_rows[row_index].find('a', attrs={'title':'Click for match detail'}).get('href')
            surface, full_name1, full_name2 = extraData(match_url)

            tournament_data.append([date, time, tournament, tournament_url, is_atp, is_singles, player1, player2, player1_url, player2_url, score1, score2, odds1, odds2, match_url, surface, full_name1, full_name2])

        day_data = day_data + tournament_data

    return day_data

def write_csv(fileName, rows):
    # import csv
    import unicodecsv as csv

    with open(fileName, "a") as f:
        writer = csv.writer(f, delimiter=',', lineterminator='\n', )
        writer.writerows(rows)

def main():

    dateList = get_dates(date_range)

    # for item in dateList:
    day_count = 0
    while day_count < len(dateList):
        item = dateList[day_count]
        year = item.date().year
        month = item.date().month
        day = item.date().day
        date = item.date().__str__()

        url = baseUrl + 'year=' + str(year) + '&month=' + str(month) + '&day=' + str(day)

        print date
        print url

        try:
            data = get_data(url, date)
        except requests.exceptions.ConnectionError:
            import time
            print "I am relaxing"
            time.sleep(100)

            continue


        write_csv(outputFile, data)
        day_count = day_count + 1

        print len(data)
        print '\n'

if __name__ == "__main__":

    import sys

    date_range = [sys.argv[1], sys.argv[2]]
    outputFile = sys.argv[3]


    items = [['date', 'time', 'tournament', 'tournament_url', 'is_atp', 'is_singles', 'player1', 'player2','player1_url', 'player2_url', 'scores1', 'scores2', 'odds1', 'odds2', 'match_url', 'surface', 'full_name1', 'full_name2']]
    write_csv(outputFile, items)

    baseUrl = 'http://www.tennisexplorer.com/results/?type=all&'
    domain = 'http://www.tennisexplorer.com'

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/s537.36'}
    s = requests.session()

    main()