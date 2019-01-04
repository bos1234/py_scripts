# straight flush, jack high :                 <8, 11>
# four aces and a queen kicker :              <7, 14, 12>
# full-house eights over kings :              <6, 8, 13>
# flush 10-8 :                                <5, [10, 8, 7, 5, 3]>
# straight jack high :                        <4, 11>
# three sevens :                              <3, 7, [7, 7, 7, 5, 2]>
# two pair, jacks and threes :                <2, 11, 3,[13,11,11,3,3]>
# pair of twos,  jack high :                  <1, 2, [11, 6, 3, 2, 2]>
# nothing :                                   <0, 7, 5, 4, 3, 2>

import itertools


def poker(hands):
    # Return a list of winning hands: poker([hand,...]) => [hand,...]
    return allmax(hands, key=hand_rank) #give me the maximum according to the function hand_rank


def allmax(iterable, key=None):
    # Return a list of all items equal to the max of the iterable
    result, maxval = [], None
    key = key or (lambda x: x)
    for x in iterable:
        xval = key(x)
        if not result or xval > maxval:
            result, maxval = [x], xval
        elif xval == maxval:
            result.append(x)
    return result


def hand_rank(hand):
    # Return a value indicating the ranking of a hand
    ranks = card_ranks(hand) # extract the ranks with card_ranks function
    if straight(ranks) and flush(hand):
        return (8, max(ranks))  # 2 3 4 5 6 (8, 6) vs 6 7 8 9 T (8, 10)
    elif kind(4, ranks):  # if you have 4 of a kind at all, then do this
        return (7, kind(4, ranks), kind(1, ranks))  # 9 9 9 3 (7, 9 3)
    elif kind(3, ranks) and kind(2, ranks):
        return (6, kind(3, ranks), kind(2, ranks))
    elif flush(hand):
        return (5, ranks)
    elif straight(ranks):
        return (4, max(ranks))
    elif kind(3, ranks):
        return (3, kind(3, ranks), ranks)
    elif two_pair(ranks):
        return (2, two_pair(ranks), ranks)
    elif kind(2, ranks):
        return (1, kind(2, ranks), ranks)
    else:
        return (0, ranks)


def card_ranks(hand):
    # Return a list of the ranks, sorted with higher first
    ranks = ['--23456789TJQKA'.index(r) for r, s in hand]
    ranks.sort(reverse=True)
    return [5, 4, 3, 2, 1] if (ranks == [14, 5, 4, 3, 2]) else ranks


def straight(ranks):
    # Return True if the ordered ranks for a 5-card straight
    return (max(ranks) - min(ranks) == 4) and len(set(ranks)) == 5


def flush(hand):
    # Return True if all the cards have the same suit
    suits = [s for r, s in hand]
    return len(set(suits)) == 1


def kind(n, ranks):
    # Return the first rank that this hand has exactly n of.
    # Return None if there is no n-of-a-kind in the hand
    for r in ranks:
        if ranks.count(r) == n: return r
    return None


def two_pair(ranks):
    # Return the first rank that this hand has exactly n of
    pair = kind(2, ranks)
    lowpair = kind(2, list(reversed(ranks)))
    if pair and lowpair != pair:
        return (pair, lowpair)
    else:
        return None

# initiate the 52 dec of cards and deduct the flop
flop = input('flop: ')
flop = flop.split()

deck = [r + s for r in '23456789TJQKA' for s in 'SHDC']
for card in flop:
    deck.remove(card)

combinations = itertools.combinations(deck, 2)

a = itertools.combinations(deck, 2)


five_cards = [[] for x in range(50)]

for index, c in enumerate(a):
    c = list(c)
    five_cards[index] = flop + c

hands = five_cards
print(poker(hands))
