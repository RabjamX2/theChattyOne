import discord
from discord.ui import Button, View
from discord import app_commands
import pickle
from deck_maker import deck_maker
from config import discordBotToken, channelIDs

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

discord_id_dict = {"RabjamX2#1936":181262275569647616,"Teeony#8274":342421820021932042,"Don Pack#4076":171084724234616842}
discord_id_name = {"RabjamX2#1936":'Rabjam', "Teeony#8274":'Tony', "Don Pack#4076":"Rudy"}

with open('player_balances.bin', 'rb') as file:
    player_balances = pickle.load(file)

class the_players:
    def __init__(self, player : str) -> None:
        self.player = player
        self.name = discord_id_name[self.player]
        self.balance = player_balances[self.player]
        self.discord_ID = discord_id_dict[self.player]


# Make a new deck
dealer_shoe = deck_maker(number_of_decks=1)
burn_card = dealer_shoe.pop(0)

the_Table = {1:False,2:False,3:False,4:False,100:False}

# Normally seven total betting boxes
class betting_boxes:
    def __init__(self, betting_box : str, player : str, bet_amount : int) -> None:
        self.betting_box = betting_box
        self.player = player
        self.bet_amount = bet_amount
        self.cards_in_hand = []
        self.insurance = False
        self.doubled_down = False
        self.stood = False

        self.payed = False
        the_Table[betting_box] = self
    
    def __str__(self) -> str:
        return f"Player: {self.player} Bet: {self.bet_amount} \nHand: {[str(card) for card in self.cards_in_hand]} = {self.hand_value} Busted: {bool(self.busted)} Splittable: {self.splittable}"

    @property
    def hand_value(self):
        hand_sum = sum(card.blackjack_value for card in self.cards_in_hand)
        if self.hard_hand or hand_sum <= 21:
            return hand_sum
        else:
            for card in self.cards_in_hand:
                if card.rank == 1 and card.blackjack_value != 1:
                    card.blackjack_value = 1
                if sum(card.blackjack_value for card in self.cards_in_hand) <= 21:
                    return sum(card.blackjack_value for card in self.cards_in_hand)
            return sum(card.blackjack_value for card in self.cards_in_hand)

    @property
    def busted(self):
        if self.hand_value > 21:
            return True
        else:
            return False 
    
    @property
    def blackjack(self):
        if self.betting_box != 100:
            if self.hand_value == 21 and len(self.cards_in_hand) == 2:
                self.stood = True
                return True
            else:
                return False

    @property
    def amount_of_aces(self):
        count = 0
        for card in self.cards_in_hand:
            if card.type == 'ace':
                count += 1
        return count

    @property
    def hard_hand(self):
        for card in self.cards_in_hand:
            if card.type == 'ace':
                return False
        return True
    
    @property
    def splittable(self):
        if len(self.cards_in_hand) == 2 and self.cards_in_hand[0].rank == self.cards_in_hand[1].rank:
            return True
        else:
            return False

def hit(hand) -> None:
    (hand.cards_in_hand).append(dealer_shoe.pop(0))

def stand(hand) -> None:
    hand.stood = True

def split(hand):
    if hand.splittable:
        if hand.cards_in_hand[0].type == "ace" and hand.cards_in_hand[1].type == "ace":
            pass
        else:
            new_betting_box_id = hand.betting_box + 1
            betting_boxes(betting_box = new_betting_box_id, player = hand.player, bet_amount = hand.bet_amount)
            the_Table[new_betting_box_id].cards_in_hand = [hand.cards_in_hand[1]]
            hand.cards_in_hand = [hand.cards_in_hand[0]]

            hit(hand)
            hit(the_Table[new_betting_box_id])
    else:
        return (f"Can't split a {hand.cards_in_hand[0]} and a {hand.cards_in_hand[1]}!")

def double_down(hand):
    if len(hand.cards_in_hand) == 2:
        hand.doubled_down = True
        (hand.cards_in_hand).append(dealer_shoe.pop(0))
        hand.stood = True
    else:
        return (f"Can't split a {hand.cards_in_hand[0]} and a {hand.cards_in_hand[1]}!")

def payout(hand) -> str:
    if hand.betting_box != 100:
        if hand.payed:
            return ("Already payed betting box " + str(hand.betting_box))
        else:
            hand.payed = True
            multiplier = 2 if hand.doubled_down else 1

            if hand.busted:
                player_balances[hand.player] -= hand.bet_amount*multiplier
                return (f"{hand.player} busted and lost {hand.bet_amount*multiplier}")    
            elif hand.blackjack:
                if the_Table[100].blackjack:
                    return (f"Dealer and {hand.player} hit Blackjack! Hand results in a push")
                else:
                    player_balances[hand.player] += hand.bet_amount*1.5
                    return (f"{hand.player} hit Blackjack and won {hand.bet_amount*1.5}")
            elif the_Table[100].busted:
                    if hand.busted == False:
                        player_balances[hand.player] += hand.bet_amount*multiplier
                        return (f"Dealer busted. {hand.player} has won {hand.bet_amount*multiplier}")
            else:
                if hand.busted == False and hand.stood == True:
                    if hand.hand_value > the_Table[100].hand_value:
                        player_balances[hand.player] += hand.bet_amount*multiplier
                        return (f"{hand.player} has won {hand.bet_amount*multiplier}")
                    elif hand.hand_value == the_Table[100].hand_value:
                        return (f"{hand.player} has pushed")
                    elif hand.hand_value < the_Table[100].hand_value:
                        player_balances[hand.player] -= hand.bet_amount*multiplier
                        return (f"{hand.player} has lost {hand.bet_amount*multiplier}")
                    else:
                        return ("Error occured")
                else:
                    return("error else")
    
def ascii_card(*cards):
    # we will use this to prints the appropriate icons for each card
    suits_name = ['spade', 'diamond', 'heart', 'club']
    suits_symbols = ['♠', '♦', '♥', '♣']

    # create an empty list of list, each sublist is a line
    lines = [[] for i in range(5)]

    for index, card in enumerate(cards):
        # "King" should be "K" and "10" should still be "10"
        if card.rank == 10:  # ten is the only one who's rank is 2 char long
            rank = card.rank
            space = ''  # if we write "10" on the card that line will be 1 char to long
        elif card.type == "number":
            rank = card.rank  # some have a rank of 'King' this changes that to a simple 'K' ("King" doesn't fit)
            space = ' '  # no "10", we use a blank space to will the void
        else:
            rank = card.name[0]  # some have a rank of 'King' this changes that to a simple 'K' ("King" doesn't fit)
            space = ' '  # no "10", we use a blank space to will the void
    
        # get the cards suit in two steps
        suit = suits_name.index(card.suit)
        suit = suits_symbols[suit]

        # add the individual card on a line by line basis
        lines[0].append('┌─────┐')
        lines[1].append('│{}{}   │'.format(rank, space))  # use two {} one for char, one for space or char
        lines[2].append('│  {}  │'.format(suit))
        lines[3].append('│   {}{}│'.format(space, rank))
        lines[4].append('└─────┘')

    result = []
    for index, line in enumerate(lines):
        result.append(''.join(lines[index]))

    return '\n'.join(result)



class aClient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents = discord.Intents.default())
        self.synced = True
    
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild = discord.Object(id=746246368473120798))
            self.synced = True

client = aClient()
tree = app_commands.CommandTree(client)

@tree.command(name = "blackjack", guild = discord.Object(id=746246368473120798))
async def self(interaction: discord.Interaction, bet: int):
    main_player = the_players(player = str(interaction.user))
    print(main_player.player)
    if int(bet) > main_player.balance:
        await interaction.response.send_message(content=f"You only have {main_player.balance}, {main_player.name}!", ephemeral=True)
    else:
        betting_boxes(betting_box = 1, player = main_player.player, bet_amount = int(bet))
        betting_boxes(betting_box = 100, player = 'dealer', bet_amount = 0)

        class ViewGame(discord.ui.View):
            def __init__(self, main_interaction):
                super().__init__(timeout=15)
                self.value = None
                self.main_interaction = main_interaction
            
            @discord.ui.button(label="Hit", custom_id="hit_button", style=discord.ButtonStyle.success)
            async def hit_button(self, button_interaction: discord.Interaction, button : discord.ui.Button):
                hit(the_Table[1])
                if the_Table[1].busted:
                    self.clear_items()
                    await update_embed(embed_bj, end=True)
                else:
                    await update_embed(embed_bj)
                await button_interaction.response.defer()

            @discord.ui.button(label="Stand", custom_id="stand_button", style=discord.ButtonStyle.danger)
            async def stand_button(self, button_interaction: discord.Interaction, button : discord.ui.Button):
                stand(the_Table[1])
                self.clear_items()
                await update_embed(embed_bj, end=True)
                await button_interaction.response.defer()

            if len(the_Table[1].cards_in_hand) == 2:
                @discord.ui.button(label="Double Down", custom_id="double_button", style=discord.ButtonStyle.success)
                async def double_button(self, button_interaction: discord.Interaction, button : discord.ui.Button):
                    double_down(the_Table[1])
                    self.clear_items()
                    await update_embed(embed_bj, end=True)
                    await button_interaction.response.defer()
        
            if the_Table[1].splittable:
                @discord.ui.button(label="Split", custom_id="split_button", style=discord.ButtonStyle.danger)
                async def split_button(self, button_interaction: discord.Interaction, button : discord.ui.Button):
                    split(the_Table[1])
                    
            async def interaction_check(self, interaction) -> bool:
                if interaction.user != self.main_interaction.user:
                    return False
                else:
                    return True

        async def update_embed(embeded, message = "", end=False):
            if end:
                await the_end()

            player_hand_str = ""
            for card in the_Table[1].cards_in_hand:
                player_hand_str += "```"
                player_hand_str += ascii_card(card)
                player_hand_str += "```"

            dealer_hand_str = ""
            for card in the_Table[100].cards_in_hand:
                dealer_hand_str += "```"
                dealer_hand_str += ascii_card(card)
                dealer_hand_str += "```"

            embeded.set_field_at(
                index=0,
                name="Dealer Hand",
                value= dealer_hand_str,
                inline=True
            )
            embeded.set_field_at(
                index=1,
                name="Total",
                value= str(the_Table[100].hand_value),
                inline=True
            )
            embeded.set_field_at(
                index=3,
                name="Player Hand",
                value= player_hand_str,
                inline=True
            )
            embeded.set_field_at(
                index=4,
                name="Total",
                value= str(the_Table[1].hand_value),
                inline=True
            )

            if message:
                embeded.set_field_at(
                    index=5,
                    name="Message",
                    value= message,
                    inline=False
                )

            await interaction.followup.send(embed=embed_bj, view=view)

        # Initial Deal
        for second_step in [0,1]:
            for betting_box_id, hand in the_Table.items():
                if hand:
                    if betting_box_id == 100 and second_step:
                        hole_card = dealer_shoe.pop(0)
                    else:
                        (hand.cards_in_hand).append(dealer_shoe.pop(0))
        
        player_hand_str = ""
        for card in the_Table[1].cards_in_hand:
            player_hand_str += "```"
            player_hand_str += ascii_card(card)
            player_hand_str += "```"

        dealer_hand_str = ""
        for card in the_Table[100].cards_in_hand:
            dealer_hand_str += "```"
            dealer_hand_str += ascii_card(card)
            dealer_hand_str += "```"

        embed_bj = discord.Embed(
            title = "Blackjack",
            colour = discord.Colour.green()
        )
        embed_bj.add_field(
            name="Dealer Hand",
            value= dealer_hand_str,
            inline=True
        )
        embed_bj.add_field(
            name="Total",
            value= str(the_Table[100].hand_value),
            inline=True
        )
        embed_bj.add_field(
            name = '\u200B', 
            value = '\u200B',
            inline = False
        )
        embed_bj.add_field(
            name="Player Hand",
            value=player_hand_str,
            inline=True
        )
        embed_bj.add_field(
            name="Total",
            value= str(the_Table[1].hand_value),
            inline=True
        )
        embed_bj.add_field(
            name = '\u200B', 
            value = '\u200B',
            inline = False
        )
        embed_bj.add_field(
            name = '\u200B', 
            value = '\u200B',
            inline = False
        )

        async def the_end():
            if len(the_Table[100].cards_in_hand) == 1:
                the_Table[100].cards_in_hand.append(hole_card)
            while the_Table[100].hand_value <= 16:
                hit(the_Table[100])
                await update_embed(embed_bj)

            embed_bj.set_field_at(
                index=6,
                name="Result",
                value= payout(the_Table[1]),
                inline = False
            )
            embed_bj.add_field(
                name="New Balance",
                value= main_player.balance,
                inline = True
            )

            with open('player_balances.bin', 'wb') as file:
                pickle.dump(player_balances, file)

        view = ViewGame(interaction)
        await interaction.response.send_message(embed=embed_bj, view=view)

        if (the_Table[100].cards_in_hand[0].blackjack_value == 10 and hole_card.type == 'ace') or (the_Table[100].cards_in_hand[0].type == 'ace' and hole_card.blackjack_value == 10):
            if the_Table[1].blackjack:
                await update_embed(embed_bj, message = "Dealer and Player hit BJ", end=True)
            else:
                await update_embed(embed_bj, message = "Dealer hit BJ", end=True)
        elif the_Table[1].blackjack:
            await update_embed(embed_bj, message = "Player hit BJ", end=True)

    


client.run(discordBotToken)