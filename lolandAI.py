from riotwatcher import LolWatcher, TftWatcher, ApiError
import openai
import discord
import pickle, filecmp #,urlopen, PIL TODO: using profile icon number from api call, make client.user avatar match LOL avatar 'http://ddragon.leagueoflegends.com/cdn/10.18.1/img/profileicon/[ICON ID].png'
import time, threading, datetime
from config import openAIToken, discordBotToken, channelIDs , lolKey, list_players, name_and_id, the_snitch_webhook_url

#from playerdatabase import clean_player_data as old_clean_player_data

# Set up the OpenAI API key
openai.api_key = openAIToken

# Create a new Discord client
# https://discordpy.readthedocs.io/en/stable/api.html
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

the_snitch = discord.SyncWebhook.from_url(the_snitch_webhook_url)

# https://riot-watcher.readthedocs.io/en/latest/index.html
# https://riot-api-libraries.readthedocs.io/en/latest/
# GET KEY FROM https://developer.riotgames.com/
lol_watcher = LolWatcher(lolKey)
tft_watcher = TftWatcher(lolKey)

my_region = 'na1'

imageTrigger = "image of "
closeTrigger = "bye bot"

LeaderBoard = ["Solo/Duo", "Flex", "TFT", "Double Up"]

ranked_dict = {
    "rank" : {
        "IV" : 000,
        "III" : 250,
        "II" : 500,
        "I" : 750
    },
    "tier" : {
        "IRON" : 0000,
        "BRONZE" : 1000,
        "SILVER" : 2000,
        "GOLD" : 3000,
        "PLATINUM" : 4000,
        "DIAMOND" : 5000,
        "MASTER" : 6000,
        "GRANDMASTER" : 8000,
        "CHALLENGER" : 9000
    },
    "queue" : {
        "RANKED_SOLO_5x5" : "Solo/Duo",
        "RANKED_FLEX_SR" : "Flex",
        "RANKED_TFT" : "TFT",
        "RANKED_TFT_DOUBLE_UP" : "Double Up"
    }
}

def get_clean_player_data():

    list_player_data = {}
    try:
        with open("newplayerdatabase.bin", "rb") as newfile: # "rb" because we want to read in binary mode
            becoming_old_data = pickle.load(newfile)

        with open('oldplayerdatabase.bin' , 'wb') as file:
            pickle.dump(becoming_old_data, file)

        #print("Timing started")
        #last_time = time.time()

        for player_name, player_id in name_and_id.items():
            player_data_dict = {}

            #temp_player = (lol_watcher.summoner.by_name(my_region, player_name))  # Not needed since using name_and_id (this loop takes about 13 seconds but after pregenerated ids takes 9 seconds)
            player_ranked_lol_stats = lol_watcher.league.by_summoner(my_region, player_id)
            
            ranked_lol_data = list(player_ranked_lol_stats)

            for i in range(0, len(ranked_lol_data)):
                if ranked_lol_data[i]:
                    player_data_dict[ranked_lol_data[i]["queueType"]] = ranked_lol_data[i]
            
            tft_data = tft_watcher.league.by_summoner(my_region, player_id)

            for i in range(0, len(tft_data)):
                if tft_data:
                    player_data_dict[tft_data[i]["queueType"]] = tft_data[0]

            list_player_data[player_name] = player_data_dict

        #print("time spent 'for player_name in list_players:' ", time.time() - last_time)
        #last_time = time.time()

        clean_player_data = {}
        for player in list_player_data:
            temp_queue = {}
            for queue_type in list_player_data[player]:
                temp_queue_data = {}

                player_wins = list_player_data[player][queue_type]["wins"]
                temp_queue_data["wins"] = player_wins

                player_loses = list_player_data[player][queue_type]["wins"]
                temp_queue_data["loses"] = player_loses
            
                player_tier = list_player_data[player][queue_type]["tier"]
                temp_queue_data["Tier"] = player_tier.capitalize()

                player_rank = list_player_data[player][queue_type]["rank"]
                temp_queue_data["Rank"] = player_rank

                player_LP = list_player_data[player][queue_type]["leaguePoints"]
                temp_queue_data["LP"] = player_LP

                # Make sure elo is added last to temp_queue_data 
                player_elo = ranked_dict["tier"][player_tier] + ranked_dict["rank"][player_rank] + (player_LP*2.5)
                temp_queue_data["elo"] = player_elo

                temp_queue[ranked_dict["queue"][queue_type]] = temp_queue_data
            clean_player_data[player] = temp_queue
            
        with open('newplayerdatabase.bin' , 'wb') as file:
            pickle.dump(clean_player_data, file)

    except ApiError as err:
        if err.response.status_code == 429:
            print('TOOOOOO MANY RIOTWATCHER API REQUESTS   @', datetime.datetime.now)
        elif err.response.status_code == 404:
            print('Summoner with that ridiculous name not found.   @', datetime.datetime.now)
        else:
            print('Something went terribly wrong!!   @', datetime.datetime.now)

def find_the_change():
    with open("newplayerdatabase.bin", "rb") as n_f:
        new_file = pickle.load(n_f)
        with open("oldplayerdatabase.bin" , "rb") as o_f:
            old_file = pickle.load(o_f)
            for (new_name, new_data), (old_name, old_data) in zip(new_file.items(), old_file.items()):
                if new_name == old_name and new_data != old_data:
                    player_name = new_name
                    for (new_queue_type, new_stats), (old_queue_type, old_stats) in zip(new_data.items(), old_data.items()):
                        if new_queue_type == old_queue_type and new_stats != old_stats:
                            response = f"{player_name} has "
                            queue_type = new_queue_type
                            if new_stats['wins'] != old_stats['wins']:
                                response += f"won {new_stats['wins'] - old_stats['wins']} "
                            if new_stats['wins'] != old_stats['wins'] and new_stats['loses'] != old_stats['loses']:
                                response += 'and '
                            if new_stats['loses'] != old_stats['loses']:
                                response += f"lost {new_stats['loses'] - old_stats['loses']} "
                            response += f"{queue_type} games resulting in a "
                            if new_stats['Tier'] != old_stats['Tier']:
                                if ranked_dict['tier'][new_stats['Tier'].upper()] > ranked_dict['tier'][old_stats['Tier'].upper()]:
                                    response += "Tier promotion!!! :partying_face: <@&938057479907078185> rejoice!! \n"
                                    response += f"{player_name} is now {new_stats['Tier']} {new_stats['Rank']} at {new_stats['LP']} LP"
                                elif ranked_dict['tier'][new_stats['Tier'].upper()] < ranked_dict['tier'][old_stats['Tier'].upper()]:
                                    response += "tier demotion... :sob: \n"
                                    response += f"{player_name} is now {new_stats['Tier']} {new_stats['Rank']} at {new_stats['LP']} LP"
                            elif new_stats['Rank'] != old_stats['Rank']:
                                if ranked_dict['rank'][new_stats['Rank'].upper()] > ranked_dict['rank'][old_stats['Rank'].upper()]:
                                    response += "Rank up!!! :partying_face: \n"
                                    response += f"{player_name} is now {new_stats['Tier']} {new_stats['Rank']} at {new_stats['LP']} LP"
                                elif ranked_dict['rank'][new_stats['Rank'].upper()] < ranked_dict['rank'][old_stats['Rank'].upper()]:
                                    response += "Rank down... :sob: \n"
                                    response += f"{player_name} is now {new_stats['Tier']} {new_stats['Rank']} at {new_stats['LP']} LP"
                            elif new_stats['LP'] != old_stats['LP']:
                                if new_stats['LP'] > old_stats['LP']:
                                    response += f"{new_stats['LP'] - old_stats['LP']} gain!"
                                elif new_stats['LP'] < old_stats['LP']:
                                    response += f"{old_stats['LP'] - new_stats['LP']} loss. :sob:"
                            
                            the_snitch.send(response)

def run_get_clean_player_data():
    while True:
        get_clean_player_data()
        filecmp.clear_cache()
        are_the_files_same = filecmp.cmp("newplayerdatabase.bin", "oldplayerdatabase.bin", shallow=False)
        if are_the_files_same == False:
            find_the_change()

        # Sleep for 30 minutes (1800 seconds)
        time.sleep(1800)

# Used when sorting by elo for leaderboard
def get_word(item):
    return item[-1]

# Handle messages received in the target Discord channel
@client.event
async def on_message(message):
    # To ignore itself
    if message.author == client.user:
        return
    
    # To close bot
    if message.channel.id in channelIDs and message.author == "RabjamX2#1936" and message.content == closeTrigger:
        await client.close()

    # Bring up leader board and update  
    # TODO: make then update a function and call it on every command 

    elif message.content.lower() == ("elo update"):
        get_clean_player_data()

        await message.delete()
        
    elif message.content.lower() == ("elo leaderboard"):
        output={}
        with open("newplayerdatabase.bin", "rb") as f: # "rb" because we want to read in binary mode
            clean_player_data = pickle.load(f)

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

        
        tonys_list = []
        for i , x in output.items():
            place = 1
            response = ""
            response += f'__**{i}**__ \n'
            response += "```"
            for j in x:
                rank_place = str(place) + "."
                response += '{:<4}'.format(rank_place)
                place += 1
                for k in j[0]:
                    if len(k) <= 3:
                        response += '{:<5}'.format(k)
                    else:
                        response += '{:<17}'.format(k)
                response += "\n"
            response += "\n"
            response += "```"

            tonys_list.append(response)

            
        response = '__**Average ELO**__  ```'
        elo_holder = []
        for player , player_elo_data in clean_player_data.items():
            player_total_elo = 0
            elo_count = 0

            for j , elodata in player_elo_data.items():
                elo_count += 1
                player_total_elo += elodata["elo"]

            if elo_count:
                elo_holder.append([player, player_total_elo / elo_count])
            else:
                elo_holder.append([player, player_total_elo])
        elo_holder.sort(reverse=True, key=get_word)

        place = 0
        for name in elo_holder:
            place += 1
            rank_place = str(place) + "."
            response += '{:<4}'.format(rank_place)
            
            last_tier = "IRON"
            for i, x in ranked_dict["tier"].items():
                if x >= name[1]:
                    elo_minus_tier = name[1] - (ranked_dict["tier"][last_tier])
                    break
                last_tier = i

            last_rank = "IV"
            for i, x, in ranked_dict["rank"].items():
                if x >= elo_minus_tier:
                    elo_minus_rank = elo_minus_tier - (ranked_dict["rank"][last_rank])
                    break
                last_rank = i
            response += '{:<17} {:<11} {:<5}'.format(name[0], last_tier, last_rank)
            response += '{:3.0f}   '.format(elo_minus_rank/2.5)
            response += '{:.2f} \n'.format(name[1])

        response += "```"
        tonys_list.append(response)

        for i in tonys_list:
            await message.channel.send(i)


    elif message.content.startswith("elof "):
        with open("newplayerdatabase.bin", "rb") as f: # "rb" because we want to read in binary mode
            clean_player_data = pickle.load(f)

        list_of_elos = []
        elof_player = (message.content[len("elof "):]).strip()
        if elof_player in list_players:
            for queue,data in clean_player_data[elof_player].items():
                list_of_elos.append("`" + elof_player + "'s " + queue + " elo is " + str(data["elo"]) + "`")

        class ViewMenu(discord.ui.View):
            def __init__(self, timeout):
                super().__init__()
                self.value = None
                self.timeout = timeout
            @discord.ui.button(label="Solo/Duo", style=discord.ButtonStyle.primary)
            async def solo_duo_button(self, interaction, button):
                if message.author == interaction.user:                  
                    await interaction.response.edit_message(content=list_of_elos[0], view=None)
                    discord.ui.View.stop(self)
            @discord.ui.button(label="Double Up", style=discord.ButtonStyle.secondary)
            async def double_up_button(self, interaction, button):
                if message.author == interaction.user:
                    await interaction.response.edit_message(content=list_of_elos[1], view=None)
                    discord.ui.View.stop(self)
            @discord.ui.button(label="Flex", style=discord.ButtonStyle.success)
            async def flex_button(self, interaction, button):
                if message.author == interaction.user:
                    await interaction.response.edit_message(content=list_of_elos[2], view=None)
                    discord.ui.View.stop(self)
            @discord.ui.button(label="TFT", style=discord.ButtonStyle.danger)
            async def tft_button(self, interaction, button):
                if message.author == interaction.user:
                    await interaction.response.edit_message(content=list_of_elos[3], view=None)
                    discord.ui.View.stop(self)
            
            async def on_error(self, interaction, error, item):
                await interaction.response.edit_message(content="`" + elof_player + " has 0 elo in that category`" + item, view=None)

            async def on_timeout(self):
                self.value = "Timeout"
        
        await message.channel.send(view=ViewMenu(15))
        await ViewMenu.wait()
        if ViewMenu.value == "Timeout":
            message.delete

    elif message.content.lower() == ("test"):
        pass


    else:
        try:
            # Check if the message content is flagged by the moderation model
            flagged = openai.Moderation.create(
                input=message.content
            ).results[0]

            # If the message is flagged, do not generate a response
            if flagged["flagged"]:
                if message.channel.id == channelIDs or message.channel.id == 1052391367449522296:
                    for flag in flagged["categories"]:
                        if flagged["categories"][flag]:
                            if flag == "sexual":
                                await message.channel.send(f"Yo {message.author.mention} , stop being horny... You down bad man")
                            else:
                                await message.channel.send(f"Yo {message.author.mention} , stop it with the talks of {flag}")
            else:
                if message.content.startswith(imageTrigger):
                    response = openai.Image.create(
                        prompt=message.content[len(imageTrigger):],
                        n=1,
                        size="1024x1024"
                    ).data[0].url

                    await message.channel.send(response)
                else:
                    if message.channel.id == channelIDs or message.channel.id == 1052391367449522296:
                        # Generate a response using the chatGPT model
                        response = openai.Completion.create(
                            engine="text-davinci-003",
                            prompt=message.content,
                            max_tokens=3024,
                            n=1,
                            #Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer.
                            temperature=0.9
                        ).choices[0].text

                        # Send the response to the Discord channel
                        await message.channel.send(response)
        except Exception as e:
            # Send a message to the Discord channel with the error message and the user who caused the error
            await message.channel.send(f"{message.author.mention}, you got me fucked up. Error: {e}")


thread = threading.Thread(target=run_get_clean_player_data)
# Start the thread
thread.start()

# Run the Discord client
client.run(discordBotToken)

