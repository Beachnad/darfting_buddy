"http://games.espn.com/ffl/tools/projections?&startIndex=00"

import requests
from bs4 import BeautifulSoup
import re
import json

data = {

}

TEAM_ABBR = {
    '49ers': 'SF',
    'Jets': 'NYJ',
    'Giants': 'NYG',
    'Colts': 'IND',
    'Seahawks':"SEA",
    'Bengals': 'CIN',
    'Raiders': 'OAK',
    'Jaguars': 'JAX',
    'Eagles': 'PHI',
    'Ravens': 'BAL',
    'Rams': 'LAR',
    'Patriots': 'NE',
    'Vikings': 'MIN',
    'Titans':'TEN',
    'Texans': 'HOU',
    'Broncos':'DEN',
    'Cardinals': 'ARI',
    'Chargers': 'LAC',
    'Panthers': 'CAR',
    'Lions': 'DET',
    'Steelers': 'PIT',
    'Bears': 'CHI',
    'Redskins': 'WSH',
    'Packers': 'GB',
    'Dolphins': 'MIA',
    'Bills': 'BUF',
    'Saints': 'NO',
    'Buccaneers': 'TB',
    'Cowboys': 'DAL',
    'Falcons': 'ATL',
    'Chiefs': 'KC',
    'Browns': 'CLE',
    'Free Agent': 'FA'
}

indices = [x*40 for x in range(12)]
for ind in indices:
    url = "http://games.espn.com/ffl/tools/projections?&startIndex={}".format(ind)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, parser='html.parser')

    rows = soup.find_all('tr', {'class': 'pncPlayerRow'})
    for row in rows:
        vals = [c.text for c in row]
        if 'D/ST' in vals[1]:
            list_name = re.search('^([49A-Z-a-z ]*)\sD/ST\sD/ST', vals[1]).group(1)
            pos = 'D/ST'
            team = TEAM_ABBR[list_name]
            q = None
        else:
            split = vals[1].split(', ')
            list_name = split[0]
            info = split[1].split('\xa0')
            team, pos = info[0:2]
            if len(info)==4:
                q = info[3]
            else:
                q = None

        team = team.upper()
        assert team in TEAM_ABBR.values()

        info = {
            'list_name': list_name,
            'pos': pos,
            'q': q,
            'team': team,
            'fp': vals[12]
        }
        data['{}::{}'.format(list_name, team)] = info

vs = {}
for wk in range(1, 18):
    vs[wk] = {}
    url = "http://www.espn.com/nfl/schedule/_/week/{}".format(wk)
    result = requests.get(url)
    soup = BeautifulSoup(result.content, perser='html.parser')

    rows = soup.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 2:
            away = re.search('\w{2,3}$',cells[0].text).group(0)
            home = re.search('\w{2,3}$',cells[1].text).group(0)

            assert away in TEAM_ABBR.values()
            assert home in TEAM_ABBR.values()

            vs[wk][home] = away
            vs[wk][away] = home

with open('player_data.json', 'w') as outfile:
    json.dump(data, outfile)

with open('vs.json', 'w') as outfile:
    json.dump(vs, outfile)
