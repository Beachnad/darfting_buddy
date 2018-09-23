#from get_data import data, vs
from nltk.metrics.distance import edit_distance
import json

# LOAD DATA
with open('player_data.json') as f:
    data = json.load(f)

with open('vs.json') as f:
    vs = json.load(f)

NAME_TO_ID = {p: data[p]['list_name'] for p in data.keys()}

defenses = {}
for k, v in data.items():
    if v['pos'] == 'D/ST':
        defenses[v['team']] = float(v['fp'])


def_avg = sum(defenses.values())/32
def_min = 68.6
def_max = 122.3

def_scale = {}
for team, fp in defenses.items():
    adj = (fp - def_min) / (def_max - def_min)
    adj = (adj * 2) - 1
    def_scale[team] = adj

pass

DEF_ADJ = 0.15

weekly_projections = {}
player_ranks = {}
for player_id, info in data.items():
    weekly_projections[player_id] = {}
    for wk in range(1, 18):
        def_team = vs[str(wk)].get(info['team'], None)
        def_strength = def_scale[def_team] if def_team else None
        fp = float(info['fp']) / 16
        if def_team:
            if info['pos'] != 'D/ST':
                def_adj_fp = fp + (fp * -def_strength * DEF_ADJ)
            else:
                def_adj_fp = fp
        weekly_projections[player_id][wk] = def_adj_fp if def_team else 0

pass
players = [
    'p1',
    'p2',
    'p3',
    'p4',
    'p5',
    'p6',
    'p7',
    'p8',
    'p9',
    'p10'
]

def draft_order():
    max_i = len(players)
    forward = [i for i in range(len(players))]
    reverse = sorted(forward, reverse=True)
    direction = 'f'
    i = 0
    while True:
        if direction == 'f':
            yield players[forward[i]]
        else:
            yield players[reverse[i]]
        if i == max_i-1:
            direction = 'r' if direction == 'f' else 'f'
            i = 0
        else:
            i += 1

snake = iter(draft_order())




player_preds = {p: {'fp':[None]*17, 'pos': [], 'picks': []} for p in players}


def mock():
    i = 0
    for player in draft_order():
        i += 1
        if i > 100:
            break


def pos_default(pos, depth):
    pos = pos if pos != 'FLEX' else ['RB', 'WR', 'TE']
    preds = sorted([float(data[p]['fp'])/16 for p in data.keys()if data[p]['pos'] in [pos]], reverse=True)
    d = 8
    return sum(preds[0:d*depth])/(d*depth)

pos_starters = {
    'QB': 1,
    'RB': 2,
    'WR': 3,
    'TE': 1,
    'FLEX': 1,
    'K': 1,
    'D/ST': 1
}


class Player:
    @property
    def player_id(self):
        return "{}::{}".format(self.list_name, self.team)

    def __init__(self, list_name, team):
        self.list_name = list_name
        self.team = team


class Roster(list):
    def __init__(self,iterable=[]):
        list.__init__(self, iterable)



class Draftee:
    def __init__(self, name):
        self.picks = []
        self.name = name
        self.preds = self.weekly_projections()

    def weekly_projections(self):
        wk_preds = [None for _ in range(17)]
        for wk in range(1, 18):
            total = 0
            for position, pos_depth in pos_starters.items():
                pos_tot = 0
                if position == "FLEX":
                    pred = [weekly_projections[p][wk] for p in self.picks if data[p]['pos']in("RB", "WR", "TE")]
                    if len(pred) >= 4:
                        total += pred[3]
                    else:
                        total += pos_default(position, depth)
                else:
                    preds = [weekly_projections[p][wk] for p in self.picks if data[p]['pos']==position]
                    depth = 1
                    for i in range(pos_depth):
                        if i < len(preds):
                            pos_tot += preds[i]
                        else:
                            pos_tot += pos_default(position, depth)
                            depth += 1
                    total += pos_tot
            wk_preds[wk-1] = total
        return wk_preds

    def update_projections(self):
        self.preds = self.weekly_projections()


#ME = Draftee()
#Jimmy = Draftee()
##Alan = Draftee()
#Lucas = Draftee()
#Josh = Draftee()
#Jacob = Draftee()
#Zac = Draftee()
#Taran = Draftee()

ME = Draftee("Danny")
MY_SCHEDULE = ["Zac", "Jacob", "Lucas", "Taran", "Alan_normal", "Devin", "Jimmy", "Alan_cornstalks", "Zac", "Jacob", "Josh", "Taran", "Alan_normal", None, None, None, None]
DRAFT_ORDER = ["ME", "Jimmy", "Alan","Lucas","Josh","Jacob","Zac","Taran"]
DRAFT_ORDER = ["Jimmy", "Alan_cornstalks", "Devin", "Lucas", "Josh", "Alan_normal", "Jacob", "Zac", "ME", "Taran"]
DRAFTEES = [Draftee(name=x) for x in DRAFT_ORDER]
DRAFTED_PLAYERS = []

def suggest_pick():
    opponent_projections = []
    for i, opp in enumerate(MY_SCHEDULE):
        if opp is None:
            opponent_projections.append(0)
        else:
            opp_obj = [obj for obj in DRAFTEES if obj.name==opp][0]
            opponent_projections.append(opp_obj.preds[i])
    preds = []
    for player in [p for p in data.keys() if p not in DRAFTED_PLAYERS]:
        ME.picks.append(player)
        ME.update_projections()
        wins, loss, tot = 0, 0, 0
        for i in range(17):
            tot += ME.preds[i]
            if ME.preds[i] > opponent_projections[i]:
                wins += 1
            else:
                loss += 1
        preds.append((player, data[player]['pos'],wins, tot))
        del(ME.picks[-1])
    top_ten = sorted(preds, key=lambda x: (x[2],x[3]), reverse=True)[:10]
    for t in top_ten:
        print(t)


snake_draft = draft_order()
from itertools import cycle


def get_pick():
    while True:
        x = input("who did they pick?")
        first_ten = sorted([(k,v) for k,v in NAME_TO_ID.items()], key=lambda v: edit_distance(x, v[1]))[:10]
        for i, x in enumerate(first_ten):
            print("[{}] {}".format(i, x[0]))
        selection = input("SELECT THE PLAYER")
        if selection.isdigit():
            selection = int(selection)
            if selection in [n for n in range(10)]:
                print("RETURNING")
                return first_ten[int(selection)][0]



selector = cycle([0,1, 2, 3, 4, 5,6, 7, 8, 9, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0])
while True:
    s = next(selector)
    print(s)
    draftee = DRAFTEES[s]
    print(draftee.name)
    if draftee.name == 'ME':
        suggest_pick()
    print(draftee.picks)
    print(draftee.preds)
    print('\n')
    print("{} is drafting now...".format(draftee.name))
    pick = get_pick()
    if draftee.name == 'ME':
        ME.picks.append(pick)
    DRAFTED_PLAYERS.append(pick)
    draftee.picks.append(pick)
    draftee.update_projections()



