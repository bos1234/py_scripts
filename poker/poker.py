def flop_evaluator(new_deck, flop_on_board):
    hand_one = []
    for card_one in new_deck:
        flop_on_board.append(card_one)
        new_deck.remove(card_one)
        for card_two in new_deck:
            flop_on_board.append(card_two)
            hand_one = flop_on_board
            flop_on_board(flop_on_board)
            print(hand_one)

def flop_evaluator(flop_on_board):
            # remove the last element

flop = input('flop: ')
flop = flop.split()

# iniate the 52 dec of cards and deduct the flop
deck = [r + s for r in '23456789TJQKA' for s in 'SHDC']
for card in flop:
    deck.remove(card)
    
flop_evaluator(deck, flop)
