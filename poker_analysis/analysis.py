import io
from poker_analysis import library
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

def get_players(data):
    players = set()
    for event in data:
        if type(event) is dict:
            for key in event['stacks']:
                players.add(key)
    return players

def get_stacks(data):
    stacks = {}
    players = get_players(data)
    for player in players:
        stacks[player] = []
    for event in data:
        if type(event) is dict:
            for player in players:
                if player in event['stacks']:
                    stacks[player].append(int(event['stacks'][player]))
                else:
                    stacks[player].append(0)
    return stacks

yes_vpip = {library.Action.CALL, library.Action.BET, library.Action.RAISE}
no_vpip = {library.Action.CHECK, library.Action.FOLD}
def get_vpip(data):
    vpip = {}
    players = get_players(data)
    for player in players:
        vpip[player] = {'count':0, 'total':0}
    for event in data:
        if type(event) is dict:
            active_players = set(event['stacks'].keys())
            for line in event['lines']:
                if len(active_players) == 0:
                    break
                player = line[0]
                action = line[1]
                if player in active_players:
                    if action in yes_vpip:
                        vpip[player]['count'] += 1
                        vpip[player]['total'] += 1
                        active_players.remove(player)
                    if action in no_vpip:
                        vpip[player]['total'] += 1
                        active_players.remove(player)
    return vpip

def get_betsize(data):
    sizes = {}
    players = get_players(data)
    for player in players:
        sizes[player] = {'count':0, 'total':0}
    for event in data:
        if type(event) is dict:
            active_players = set(event['stacks'].keys())
            for line in event['lines']:
                if len(active_players) == 0:
                    break
                player = line[0]
                action = line[1]
                if player in active_players:
                    if action in yes_vpip:
                        sizes[player]['count'] += (-1 * line[2])
                        sizes[player]['total'] += 1
                        active_players.remove(player)
    return sizes

# # Analysis
# datas = [data1, data2, data3]
# players = []
# stacks = []
# vpips = []
# for data in datas:
#     players.append(get_players(data))
#     stacks.append(get_stacks(data))
#     vpips.append(get_vpip(data))

def plot_stack_counts(data):
    fig = Figure(figsize=(8,4))
    axis = fig.add_subplot()
    stacks = get_stacks(data)
    players = get_players(data)
    x=list(range(len(stacks['joe mama'])))
    for player in players:
        axis.plot(x, stacks[player], label=player)
    axis.legend()

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return output

def get_statistics(data):
    vpips = get_vpip(data)
    sizes = get_betsize(data)
    output = []
    for player in vpips:
        output.append(player+": "+'{:.1%}'.format(vpips[player]['count']/vpips[player]['total']) + f" over {vpips[player]['total']} hands. Average bet size is " + str(sizes[player]['count'] / sizes[player]['total']))
    return "<br>".join(output)
