from enum import Enum
import csv
import re

class Action():
    HAND = "hand"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    FOLD = "fold"
    START = "start"
    END = "end"
    CASH_IN = "cash_in"
    SMALL_BLIND = "sb"
    BIG_BLIND = "bb"
    CASH_OUT = "cash_out"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    WIN = "win"
    UNCALLED = "uncalled"
    STACK_UPDATE = "stacks"

USER = '"(.*) @ [^ ]*"'
NUMBER = '([0-9]*)'
CARD = '((?:[AKQJ]|[0-9]{1,2})[CDHS])'
hand_regexes = {
    Action.HAND: f'Your hand is {CARD}, {CARD}',
    Action.CHECK: f'{USER} checks',
    Action.CALL: f'{USER} calls {NUMBER}',
    Action.BET: f'{USER} bets {NUMBER}',
    Action.RAISE: f'{USER} raises to {NUMBER}',
    Action.FOLD: f'{USER} folds',
    
    Action.SMALL_BLIND: f'{USER} posts a small blind of {NUMBER}',
    Action.BIG_BLIND: f'{USER} posts a big blind of {NUMBER}',
    # Action.CASH_OUT: "cash_out"
    Action.FLOP: f'flop:  \[{CARD}, {CARD}, {CARD}\]',
    Action.TURN: f'turn: {CARD}, {CARD}, {CARD} \[{CARD}\]',
    Action.RIVER: f'river: {CARD}, {CARD}, {CARD}, {CARD} \[{CARD}\]',
    Action.WIN: f'{USER} collected {NUMBER} from pot',
    Action.UNCALLED: f'Uncalled bet of {NUMBER} returned to {USER}',
    # Action.STACK_UPDATE: f'#{NUMBER} {USER} \({NUMBER}\)',
}
admin_regexes= {
    Action.START: f'-- starting hand #{NUMBER}  \(Texas Hold\'em\) \(dealer: {USER}\) --',
    Action.END: f'-- ending hand #{NUMBER} --',
    Action.CASH_IN: f'The admin approved the player {USER} participation with a stack of {NUMBER}.',
    Action.STACK_UPDATE: f'#{NUMBER} {USER} \({NUMBER}\)'
}


# helper method for read_csv
def read_hand(reader):
    lines = []
    extras = []
    for row in reader:
        entry, at, order = row
        entry = (entry
                 .replace("♣", "C")
                 .replace("♦", "D")
                 .replace("♥", "H")
                 .replace("♠", "S"))
        findall = lambda regex_entry: re.findall(hand_regexes[regex_entry], entry)
        find = re.findall(hand_regexes[Action.HAND], entry)
        afind = re.findall(admin_regexes[Action.CASH_IN], entry)
        if afind:
            name, stack = afind[0]
            extras.append([name, Action.CASH_IN, stack, [], at])
        afind = re.findall(admin_regexes[Action.END], entry)
        if afind:
            hand_number = afind[0]
            lines.append(["", Action.END, 0, [], at])
            break;
        find = findall(Action.CHECK)
        if find:
            name = find[0]
            lines.append([name, Action.CHECK, 0, [], at])
        find = findall(Action.CALL)
        if find:
            name, amount = find[0]
            lines.append([name, Action.CALL, -int(amount), [], at])
        find = findall(Action.BET)
        if find:
            name, amount = find[0]
            lines.append([name, Action.BET, -int(amount), [], at])
        find = findall(Action.RAISE)
        if find:
            name, amount = find[0]
            lines.append([name, Action.RAISE, -int(amount), [], at])
        find = findall(Action.FOLD)
        if find:
            name = find[0]
            lines.append([name, Action.FOLD, 0, [], at])
        find = findall(Action.HAND)
        if find:
            first_card, second_card = find[0]
            lines.append(["user", Action.HAND, 0, [first_card, second_card], at])
        find = findall(Action.SMALL_BLIND)
        if find:
            name, small_blind = find[0]
            lines.append([name, Action.SMALL_BLIND, -int(small_blind), [], at])
        find = findall(Action.BIG_BLIND)
        if find:
            name, big_blind = find[0]
            lines.append([name, Action.BIG_BLIND, -int(big_blind), [], at])
        find = findall(Action.FLOP)
        if find:
            first_card, second_card, third_card = find[0]
            lines.append(["", Action.FLOP, 0, [first_card, second_card, third_card], at])
        find = findall(Action.TURN)
        if find:
            first_card = find[0]
            lines.append(["", Action.TURN, 0, [first_card], at])
        find = findall(Action.RIVER)
        if find:
            first_card = find[0]
            lines.append(["", Action.RIVER, 0, [first_card], at])
        find = findall(Action.WIN)
        if find:
            name, payout = find[0]
            lines.append([name, Action.WIN, int(payout), [], at])
        find = findall(Action.UNCALLED)
        if find:
            payout, name = find[0]
            lines.append([name, Action.UNCALLED, int(payout), [], at])
        # else:
        #     print(row)

        # find = findall(Action.BIG_BLIND)
        # if find:
        #     name, big_blind = find[0]
        #     lines.append([name, Action.CASH_IN, -big_blind, [], at])
    return lines, extras

def read_csv(file):
    reader = csv.reader(file)
    events = []
    afindall = lambda regex_entry: re.findall(admin_regexes[regex_entry], entry)
    reader = reversed(list(reader))
    for row in reader:
        entry, at, order = row
        afind = afindall(Action.CASH_IN)
        if afind:
            name, stack = afind[0]
            events.append([name, Action.CASH_IN, stack, [], at])
        afind = afindall(Action.START)
        if afind:
            hand_number, name = afind[0]
            stacks = {}
            stack_entries, at, order = next(reader)
            for stack_entry in stack_entries.split('|'):
                sfind = re.findall(admin_regexes[Action.STACK_UPDATE], stack_entry)
                player_num, name, amount = sfind[0]
                stacks[name] = amount
            lines, extras = read_hand(reader)
            events.append({'number':hand_number, 'stacks':stacks, 'lines':lines})
            events.extend(extras)
        
    return events
