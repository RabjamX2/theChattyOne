from riotwatcher import LolWatcher, TftWatcher, ApiError
import discord
from config import discordBotToken, channelIDs , lolKey


# Create a new Discord client
# https://discordpy.readthedocs.io/en/stable/api.html
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

closeTrigger = "bye bot"

# https://riot-watcher.readthedocs.io/en/latest/index.html
# https://riot-api-libraries.readthedocs.io/en/latest/
lol_watcher = LolWatcher(lolKey)
tft_watcher = TftWatcher(lolKey)

my_region = 'na1'

list_players = ['RabjamX2',"kaı guy", "Teeony", "namfro", "Exurp", "Suitheism", "You Are A BK", "Airplane Legs", "Pickerel Prince", "Chives123", "Linkindorf"]


list_player_data = {}
try:
    for player_name in list_players:
        player_data_dict = {}

        temp_player = (lol_watcher.summoner.by_name(my_region, player_name))
        player_ranked_lol_stats = lol_watcher.league.by_summoner(my_region, temp_player['id'])
        
        ranked_lol_data = list(player_ranked_lol_stats)

        for i in range(0, len(ranked_lol_data)):
            if ranked_lol_data[i]:
                player_data_dict[ranked_lol_data[i]["queueType"]] = ranked_lol_data[i]
        
        tft_data = tft_watcher.league.by_summoner(my_region, temp_player['id'])

        for i in range(0, len(tft_data)):
            if tft_data:
                player_data_dict[tft_data[i]["queueType"]] = tft_data[0]

        list_player_data[player_name] = player_data_dict
    #print(list_player_data)

except ApiError as err:
    if err.response.status_code == 429:
        print('We should retry in {} seconds.'.format(err.response.headers['Retry-After']))
        print('this retry-after is handled by default by the RiotWatcher library')
        print('future requests wait until the retry-after time passes')
    elif err.response.status_code == 404:
        print('Summoner with that ridiculous name not found.')
    else:
        print('Something went terribly wrong!!')

ranked_dict = {
    "rank" : {
        "IV" : 000,
        "III" : 100,
        "II" : 200,
        "I" : 300
    },
    "tier" : {
        "IRON" : 0000,
        "BRONZE" : 1000,
        "SILVER" : 2000,
        "GOLD" : 3000,
        "PLATINUM" : 4000,
        "DIAMOND" : 5000,
        "MASTER" : 6000,
        "GRANDMASTER" : 7000,
        "CHALLENGER" : 8000
    },
    "queue" : {
        "RANKED_SOLO_5x5" : "Solo/Duo",
        "RANKED_FLEX_SR" : "Flex",
        "RANKED_TFT" : "TFT",
        "RANKED_TFT_DOUBLE_UP" : "Double Up"
    }
}

list_to_show = []
clean_player_data = {}
for player in list_player_data:
    temp_queue = {}
    for queue_type in list_player_data[player]:
        temp_queue_data = {}
       
        player_tier = list_player_data[player][queue_type]["tier"]
        temp_queue_data["Tier"] = player_tier.capitalize()

        player_rank = list_player_data[player][queue_type]["rank"]
        temp_queue_data["Rank"] = player_rank

        player_LP = list_player_data[player][queue_type]["leaguePoints"]
        temp_queue_data["LP"] = player_LP

        player_elo = ranked_dict["tier"][player_tier] + ranked_dict["rank"][player_rank] + player_LP
        temp_queue_data["elo"] = player_elo

        temp_queue[ranked_dict["queue"][queue_type]] = temp_queue_data
    clean_player_data[player] = temp_queue

#print(clean_player_data)

def get_word(item):
    return item[-1]

# Handle messages received in the target Discord channel
@client.event
async def on_message(message):
    # To ignore itself
    if message.author == client.user:
        return
    
    # To close bot
    if message.channel.id in channelIDs:
        if message.author == "RabjamX2#1936": 
            if message.content == closeTrigger:
                await client.close()

    # Bring up leader board and update  
    # TO DO: make then update a function and call it on every command 
    if message.content == ("elo update") or message.content == ("elo leaderboard"):
        LeaderBoard = ["Solo/Duo", "Flex", "TFT", "Double Up"]

        output={}
        for queue_stat in LeaderBoard:
            queue_list = []
            for name in clean_player_data:
                holder_list = []
                for queue in clean_player_data[name]:
                    if queue == queue_stat:
                        stats = [name,clean_player_data[name][queue]["Tier"], clean_player_data[name][queue]["Rank"], str(clean_player_data[name][queue]["LP"])]
                        if stats:
                            holder_list.append(stats)
                            holder_list.append(clean_player_data[name][queue]["elo"])
                            stats = ""
                if holder_list:
                    queue_list.append(holder_list)
            queue_list.sort(reverse=True,key=get_word)
            output[queue_stat] = queue_list

        
        for i , x in output.items():
            response = ""
            response += '{:<17} \n'.format(i)
            for j in x:
                for k in j[0]:
                    response += '{:<15}'.format(k)
                response += "\n"
            response += "\n"
            await message.channel.send(response)

"""
    elif message.content.startswith("elof "):
        elof_player = (message.content[len("elof "):]).strip()
        if elof_player in list_players:
            for queue,data in clean_player_data[elof_player].items():
                await message.channel.send(queue + " Elo = " + str(data["elo"]))
    elif message.content == ("test"):
        async def menutest(message):
            await message.reply
class view_menu(discord.ui.View):
    def __init__(self):
        self.value = None
    @discord.ui.button(label="test", style=discord.ButtonStyle.primary)
    async def test1(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("pressed")
            
"""

# Run the Discord client
client.run(discordBotToken)

{'RabjamX2': {'Double Up': {'Tier': 'Bronze',
   'Rank': 'I',
   'LP': 41,
   'elo': 1341},
  'Solo/Duo': {'Tier': 'Silver', 'Rank': 'III', 'LP': 18, 'elo': 2118},
  'Flex': {'Tier': 'Silver', 'Rank': 'II', 'LP': 0, 'elo': 2200}},
 'kaı guy': {'Solo/Duo': {'Tier': 'Platinum',
   'Rank': 'IV',
   'LP': 78,
   'elo': 4078},
  'Flex': {'Tier': 'Platinum', 'Rank': 'IV', 'LP': 81, 'elo': 4081},
  'TFT': {'Tier': 'Platinum', 'Rank': 'III', 'LP': 95, 'elo': 4195}},
 'Teeony': {'Solo/Duo': {'Tier': 'Platinum',
   'Rank': 'IV',
   'LP': 4,
   'elo': 4004},
  'Double Up': {'Tier': 'Gold', 'Rank': 'III', 'LP': 4, 'elo': 3104},
  'Flex': {'Tier': 'Gold', 'Rank': 'II', 'LP': 42, 'elo': 3242},
  'TFT': {'Tier': 'Platinum', 'Rank': 'II', 'LP': 59, 'elo': 4259}}}
  