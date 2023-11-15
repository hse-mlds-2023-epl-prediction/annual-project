import time
from random import randint
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
from dotenv import dotenv_values
import re
import humps
import pandas as pd

config = dotenv_values(".env")
proxy_url = f"socks5://{config.get('PROXY_AUTH_LOGIN')}:{config.get('PROXY_AUTH_PASSWORD')}@185.105.46.128:8000";
proxy_with_auth = {
    'http': proxy_url,
    'https': proxy_url,
}
print(proxy_url)
ua = UserAgent()
headers = {'User-Agent': ua.random}

list_url = 'https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures'
base_host = 'https://fbref.com/'


def make_request(url, proxies, headers):
    try:
        response = requests.get(url=url, proxies=proxies, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Ошибка: получен статус-код {response.status_code}")
            return None
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None


def get_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    season = soup.select_one('h1').get_text().split(' ')[0].strip()
    stats_table = soup.select_one('table.stats_table')
    rows = stats_table.select('tr:not(.spacer)')
    links = []

    for row in rows:
        link = row.select_one('[data-stat=score] a')
        if link:
            full_link = base_host + link.get('href')
            links.append({'url': full_link, 'season': season})

    return links


data = make_request(list_url, proxy_with_auth, headers)
links = get_links(data)


def get_team_scorebox_info(scorebox_team):
    team_name = scorebox_team.select_one('strong a').get_text()
    team_score = scorebox_team.select_one('.scores .score').get_text()
    team_manager = scorebox_team.select('.datapoint')[0].get_text().split(':')[1].strip().replace('\xa0', ' ')

    team_captain_element_fbref_id = None
    team_captain_name = None

    try:
        team_captain_element = scorebox_team.select('.datapoint')[1]
        team_captain_element_link = team_captain_element.select_one('a')
        team_captain_element_fbref_id = team_captain_element_link.attrs['href'].split('/')[-2]
        team_captain_name = team_captain_element.get_text().split(':')[1].strip().replace('\xa0', ' ')
    except IndexError:
        pass

    return {
        'team_name': team_name,
        'team_score': int(team_score.strip() or 0),
        'team_manager': team_manager,
        'team_captain_fbref_id': team_captain_element_fbref_id,
        'team_captain_name': team_captain_name
    }


def get_team_stats_info(stats, is_home_team=True):
    index = 0 if is_home_team else 1
    table = stats.select_one('table')
    rows = list(filter(lambda el: el != '\n', list(table.children)))

    possession_title = stats.find('th', string=re.compile('Possession'))
    possession_percent = ''
    if possession_title:
        possession_row = possession_title.parent.find_next_sibling('tr')
        possession_percent = possession_row.select('td')[index].select_one('div div').get_text().replace('%',
                                                                                                         '').replace(
            '\n', '')

    passing_title = stats.find('th', string=re.compile('Passing Accuracy'))
    passing_accuracy_percent = ''
    passing_accuracy_count = ''
    passing_total_count = ''

    if passing_title:
        passing_row = passing_title.parent.find_next_sibling('tr')
        passing_cell = passing_row.select('td')[index]
        passing_accuracy_percent = passing_cell.select_one('strong').get_text().replace('%', '')
        passing_info = passing_cell.get_text().split('—')[index].split('of')
        passing_accuracy_count = passing_info[0].strip()
        passing_total_count = passing_info[1].strip();

    shots_title = stats.find('th', string=re.compile('Shots on Target'))
    shots_on_target_percent = ''
    shots_on_target_count = ''
    shots_total_count = ''

    if shots_title:
        shots_row = shots_title.parent.find_next_sibling('tr')
        shots_cell = shots_row.select('td')[index]
        shots_on_target_percent = shots_cell.select_one('strong').get_text().replace('%', '')
        shots_info = shots_cell.get_text().split('—')[index].split('of')
        shots_on_target_count = shots_info[0].strip()
        shots_total_count = shots_info[1].strip();

    saves_title = stats.find('th', string=re.compile('Saves'))
    saves_percent = ''
    saves_count = ''
    saves_attempt = ''

    if saves_title:
        shots_row = saves_title.parent.find_next_sibling('tr')
        saves_cell = shots_row.select('td')[index]
        saves_percent = saves_cell.select_one('strong').get_text().replace('%', '')
        saves_info = saves_cell.get_text().split('—')[index].split('of')
        saves_count = saves_info[0].strip()
        saves_attempt = saves_info[1].strip();

    cards_title = stats.find('th', string=re.compile('Cards'))
    yellow_cards_count = None
    red_cards_count = None

    if cards_title:
        cards_row = cards_title.parent.find_next_sibling('tr')
        card_cell = cards_row.select('td')[index]
        yellow_cards_count = len(card_cell.select('.yellow_card'))
        red_cards_count = len(card_cell.select('.red_card'))

    print(possession_percent if int(possession_percent.strip() or 0) else None)

    return {
        'possession_percent': int(possession_percent.strip() or 0) if possession_percent else None,
        'passing_total_count': int(passing_total_count.strip() or 0) if passing_total_count else None,
        'passing_accuracy_count': int(passing_accuracy_count.strip() or 0) if passing_accuracy_count else None,
        'passing_accuracy_percent': int(passing_accuracy_percent.strip() or 0) if passing_accuracy_percent else None,
        'shots_on_target_percent': int(shots_on_target_percent.strip() or 0) if shots_on_target_percent else None,
        'shots_on_target_count': int(shots_on_target_count.strip() or 0) if shots_on_target_count else None,
        'shots_total_count': int(shots_total_count.strip() or 0) if shots_total_count else None,
        'saves_percent': int(saves_percent.strip() or 0) if saves_percent else None,
        'saves_count': int(saves_count.strip() or 0) if saves_count else None,
        'saves_attempt': int(saves_attempt.strip() or 0) if saves_attempt else None,
        'yellow_cards_count': yellow_cards_count,
        'red_cards_count': red_cards_count
    }


def get_team_extra_stats_info(extra_stats, is_home_team=True):
    method = 'previous_sibling' if is_home_team else 'next_sibling'
    extra_stats_names = ['Fouls', 'Corners', 'Crosses', 'Touches', 'Interceptions', 'Aerials Won', 'Offsides',
                         'Goal Kicks', 'Throw Ins', 'Long Balls']
    extra_stats_dict = {}
    for name in extra_stats_names:
        key = humps.decamelize(name)
        name_title = extra_stats.find('div', string=re.compile(name))
        if name_title:
            value = getattr(name_title, method).get_text()
            extra_stats_dict[key] = int(value)
        else:
            extra_stats_dict[key] = None

    return extra_stats_dict


def get_match_common_info(html, url, season):
    soup = BeautifulSoup(html, 'html.parser')

    scorebox = soup.select_one('.scorebox')
    scorebox_children = list(filter(lambda el: el != '\n', list(scorebox.children)))
    home_team_scorebox_info = get_team_scorebox_info(scorebox_children[0])
    away_team_scorebox_info = get_team_scorebox_info(scorebox_children[1])
    scorebox_meta = scorebox.select_one('.scorebox_meta')
    scorebox_meta_venuetime = scorebox_meta.select_one('.venuetime')
    match_date = scorebox_meta_venuetime.attrs['data-venue-date']
    match_time = scorebox_meta_venuetime.attrs['data-venue-time']

    premier_league_link = scorebox_meta.find('a', string=re.compile('Premier League'))
    match_week = premier_league_link.next_sibling.strip().split(' ')[1].replace(')', '')

    attendance = scorebox_meta.find('small', string=re.compile('Attendance'))

    if attendance:
        attendance = attendance.parent.next_sibling.next_sibling.get_text()

    venue_data = scorebox_meta.find('small', string=re.compile('Venue'))

    if venue_data:
        venue_data = venue_data.parent.next_sibling.next_sibling.get_text().split(',')
        venue_data = list(map(lambda venue_str: venue_str.strip(), venue_data))
    else:
        venue_data = [None, None]

    referee = scorebox_meta.find('small', string=re.compile('Officials'))

    if referee:
        referee = referee.parent.next_sibling.next_sibling.select_one('span').get_text().replace('\xa0', ' ')

    team_stats = soup.select_one('#team_stats')
    home_team_stats_info = get_team_stats_info(team_stats)
    away_team_stats_info = get_team_stats_info(team_stats, False)

    team_stats_extra = soup.select_one('#team_stats_extra')
    home_team_extra_stats_info = get_team_extra_stats_info(team_stats_extra)
    away_team_extra_stats_info = get_team_extra_stats_info(team_stats_extra, False)

    fbref_id = url.split('/')[-2]

    # Match result (h:home team win, a:away team win, d:draw)
    home_team_score = home_team_scorebox_info['team_score']
    away_team_score = away_team_scorebox_info['team_score'];

    match_result = None

    if home_team_score > away_team_score:
        match_result = 'H'
    elif away_team_score > home_team_score:
        match_result = 'A'
    else:
        match_result = 'D'

    data = {
        'fbref_match_id': fbref_id,
        'season': season,
        'match_week': int(match_week.strip()),
        'match_date': match_date,
        'match_time': match_time,
        'home_team_name': home_team_scorebox_info['team_name'],
        'away_team_name': away_team_scorebox_info['team_name'],
        'score': f"{str(home_team_scorebox_info['team_score'])}:{str(away_team_scorebox_info['team_score'])}",
        'match_result': match_result,
        'home_team_score': home_team_score,
        'away_team_score': away_team_score,
        'venue': venue_data[0],
        'venue_city': venue_data[1],
        'attendance': attendance,
        'referee': referee,
        'home_team_manager': home_team_scorebox_info['team_manager'],
        'away_team_manager': away_team_scorebox_info['team_manager'],
        'home_team_captain_name': home_team_scorebox_info['team_captain_name'],
        'away_team_captain_name': away_team_scorebox_info['team_captain_name'],
        'home_team_captain_fbref_id': home_team_scorebox_info['team_captain_fbref_id'],
        'away_team_captain_fbref_id': away_team_scorebox_info['team_captain_fbref_id'],
        'home_team_possession_percent': home_team_stats_info['possession_percent'],
        'away_team_possession_percent': away_team_stats_info['possession_percent'],
        'home_team_passing_total_count': home_team_stats_info['passing_total_count'],
        'away_team_passing_total_count': away_team_stats_info['passing_total_count'],
        'home_team_passing_accuracy_count': home_team_stats_info['passing_accuracy_count'],
        'away_team_passing_accuracy_count': away_team_stats_info['passing_accuracy_count'],
        'home_team_passing_accuracy_percent': home_team_stats_info['passing_accuracy_percent'],
        'away_team_passing_accuracy_percent': away_team_stats_info['passing_accuracy_percent'],
        'home_team_shots_on_target_percent': home_team_stats_info['shots_on_target_percent'],
        'away_team_shots_on_target_percent': away_team_stats_info['shots_on_target_percent'],
        'home_team_shots_on_target_count': home_team_stats_info['shots_on_target_count'],
        'away_team_shots_on_target_count': away_team_stats_info['shots_on_target_count'],
        'home_team_shots_total_count': home_team_stats_info['shots_total_count'],
        'away_team_shots_total_count': away_team_stats_info['shots_total_count'],
        'home_team_saves_percent': home_team_stats_info['saves_percent'],
        'away_team_saves_percent': away_team_stats_info['saves_percent'],
        'home_team_saves_count': home_team_stats_info['saves_count'],
        'away_team_saves_count': away_team_stats_info['saves_count'],
        'home_team_saves_attempt': home_team_stats_info['saves_attempt'],
        'away_team_saves_attempt': away_team_stats_info['saves_attempt'],
        'home_team_yellow_cards_count': home_team_stats_info['yellow_cards_count'],
        'away_team_yellow_cards_count': away_team_stats_info['yellow_cards_count'],
        'home_team_red_cards_count': home_team_stats_info['red_cards_count'],
        'away_team_red_cards_count': away_team_stats_info['red_cards_count'],
    }

    for key in home_team_extra_stats_info.keys():
        data[f"home_team_{key}"] = home_team_extra_stats_info[key]

    for key in away_team_extra_stats_info.keys():
        data[f"away_team_{key}"] = home_team_extra_stats_info[key]

    return data


data = []

for link in links:
    print(link)
    html = make_request(link['url'], proxy_with_auth, headers)
    info = get_match_common_info(html, link['url'], link['season'])
    data.append(info)
    time.sleep(randint(1, 2))


df = pd.DataFrame(data)

df.to_csv('matches.csv', index=False)