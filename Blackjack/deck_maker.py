import secrets

def deck_maker(number_of_decks=1, shuffled=True): # Add option for jokers
    # Normal casinos will play with 1-8 52 card decks | Since we are online, we should have max to prevent card counting
    suits = ['spade', 'heart', 'diamond', "club"]
    face_cards_dict = {1: "Ace", 11: 'Jack', 12: 'Queen', 13: 'King'}
    number_words_dict = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
                         7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen"}

    class deck_generator:
        def __init__(self, rank, suit, deck_id):
            self.rank = rank
            self.suit = suit
            self.deck_id = deck_id
            if rank in face_cards_dict:
                self.name = face_cards_dict[rank]
                self.blackjack_value = 11 if rank == 1 else 10
                self.type = 'face' if rank != 1 else 'ace'
            else:
                self.blackjack_value = rank
                self.type = 'number'
                self.name = number_words_dict[rank]
        
        def __str__(self) -> str:
            return f"{face_cards_dict[self.rank].capitalize() if self.rank in face_cards_dict or self.rank == 1 else self.rank} of {self.suit.capitalize()}s"

    # unshuffled_deck = [deck_generator(value, suit) for value in range(1, 14) for suit in suits]
    unshuffled_deck = []
    for deck_id in range(0, number_of_decks):
        for each_suit in suits:
            for rank in range(1, 14):
                unshuffled_deck.append(
                    deck_generator(rank, each_suit, deck_id))

    shuffled_deck = []

    def deck_shuffler(deck):
        while unshuffled_deck:
            picked_card = secrets.choice(deck)
            shuffled_deck.append(picked_card)
            unshuffled_deck.remove(picked_card)
        return shuffled_deck

    if shuffled:
        return deck_shuffler(unshuffled_deck)
    else:
        return unshuffled_deck
