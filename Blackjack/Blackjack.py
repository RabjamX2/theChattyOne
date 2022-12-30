from deck_maker import deck_maker

# Make a new deck
dealer_shoe = deck_maker(number_of_decks=1)
burn_card = dealer_shoe.pop(0)

blackjack_table = []

# Normally seven total betting boxes
class betting_boxes:
    def __init__(self, betting_box : str, player : str, bet_amount : int) -> None:
        self.betting_box = betting_box
        self.player = player
        self.bet_amount = bet_amount
        self.cards_in_hand = []
        self.insurance = False
        self.stood = False
        self.soft_hand = False
    
    def __str__(self) -> str:
        return f"Betting Box: {self.betting_box} Player: {self.player} Bet: {self.bet_amount} Hand: {[str(card) for card in self.cards_in_hand]} Hand value: {self.hand_value} Busted: {self.busted}"

    @property
    def hand_value(self):
        return sum(card.blackjack_value for card in self.cards_in_hand)

    @property
    def busted(self):
        if self.hand_value > 21:
            if self.hard_hand:
                return True
            elif (self.hand_value - 10) > 21 and self.soft_hand == False:
                return True
            else:
                self.soft_hand = True
                for card in self.cards_in_hand:
                    if card.rank == 1:
                        card.blackjack_value = 1
                return False     
    
    @property
    def blackjack(self):
        return True if self.hand_value == 21 and len(self.cards_in_hand) == 2 else False
    
    @property
    def hard_hand(self):
        for card in self.cards_in_hand:
            if card.rank == 1:
                return False
        return True

dealer = betting_boxes(betting_box = 100, player = 'dealer', bet_amount = 0)



test_bet1 = betting_boxes(betting_box = 1, player = 'Teeony', bet_amount = 10)
test_bet2 = betting_boxes(betting_box = 6, player = 'RabjamX2', bet_amount = 10)
test_bet3 = betting_boxes(betting_box = 3, player = 'Rudy', bet_amount = 10)
blackjack_table.extend([test_bet1,test_bet2,test_bet3,dealer])


def sort_by_betting_box(e):
  return e.betting_box

blackjack_table.sort(key=sort_by_betting_box)

def hit(betting_box):
    (betting_box.cards_in_hand).append(dealer_shoe.pop(0))
    if betting_box.busted:
        return "Busted"
        #collect Money
    else:
        return "Safe"

def stand(betting_box) -> None:
    betting_box.stood = True

def split(betting_box):
    if len(betting_box.cards_in_hand) == 2 and betting_box.cards_in_hand[0].rank == betting_box.cards_in_hand[0].rank:
        pass
    else:
        return f"Can't split a {betting_box.cards_in_hand[0]} and a {betting_box.cards_in_hand[1]}!"

def double_down(betting_box):
    if len(betting_box.cards_in_hand) == 2:
        (betting_box.cards_in_hand).append(dealer_shoe.pop(0))
        betting_box.stood = True

def deal_blackjack(table):
    # Initial Deal
    for second_step in [0,1]:
        for hands in table:
            each_hand = hands
            if each_hand.player == "dealer" and second_step:
                hole_card = dealer_shoe.pop(0)
            else:
                (each_hand.cards_in_hand).append(dealer_shoe.pop(0))

    #Minigames like match the dealer

    # Insurance
    if dealer.hand_value == 1:
        #Ask if want insurance
        if hole_card.blackjack_value == 10:
            pass # End game early 

    for hand in table:
        if hand.player != "dealer":
            if hand.busted == False:
                pass
                # Give em options
            




deal_blackjack(blackjack_table)