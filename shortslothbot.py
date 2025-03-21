import discord
# from discord.ext import commands
import requests
import json
import csv
import pandas as pd
import time
import random



class MyClient(discord.Client):
    
    async def on_ready(self):
        print('{0} is online!'.format(self.user))
        # Add on when added to more channels
        for channel in self.CHANNELS.keys(): 
            channel_response = client.get_channel(self.CHANNELS[channel])
            if channel_response != None:
                await channel_response.send("Short Sloth's Bot is online!")
            else:
                print("Channel not found!")
        
    # async def on_disconnect(self):
    #     print('{0} is logging off!'.format(self.user))
        
    # Helper Functions for Chat Commands ------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def generate_meme(self, msg):
        subreddit = msg.content.lower()
        if subreddit == "quit":
            return "Meme request cancelled!"
        elif subreddit == "random":
            subreddit = ''
        try:
            r = requests.get('https://meme-api.com/gimme/' + subreddit)
            json_data = json.loads(r.text)
            return json_data['url']
        
        except requests.ConnectionError:
            return "Connection error detected!"
        except KeyError:
            return "Invalid Subreddit!"
    

    def deathroll(self, max):
        new_max = random.randint(1, max)
        return new_max
    
    # Scan for Bot Command keywords ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        # Meme Generator with Reddit API 
        if message.content.startswith('$meme'):
            await message.channel.send('Which subreddit do you want to retrieve a meme from? (Type "random" for a random Subreddit, or "quit" to cancel!)')
            msg = await client.wait_for('message')
            await message.channel.send(self.generate_meme(msg))    
            
            
        # Dice Rolling Game with Discord API Functions 
            first_player = message.author.id
            
            # Attempt to play against bot
            if len(message.mentions) == 1 and message.mentions[0].id == client.user.id:
                await message.channel.send("You can't play against me, you bozo!")
                
            # Attempt to use command without user parameters
            elif len(message.mentions) == 0 :
                await message.channel.send("You must @ the one user you want to Death Roll against!")
                
            # Attempt to play against yourself
            elif message.mentions[0].id == first_player:
                await message.channel.send("You cannot Death Roll against yourself! What are you, a gambling addict?!")
                
            # Successful challenge query, will prompt challenged user to react with emoji to accept game
            elif len(message.mentions) == 1 and message.mentions[0].id != first_player:
                second_player = message.mentions[0].id
                game_msg = await message.channel.send("<@" + str(first_player) + "> has challenged <@" + str(second_player) + "> to a Death Roll! Do you accept?")
                await game_msg.add_reaction('✅')
                time.sleep(5)
                game_msg = await game_msg.channel.fetch_message(game_msg.id) # Update message object to include new reactions
                reactors = []
                for reaction in game_msg.reactions:
                    if str(reaction) == "✅":
                        async for user in reaction.users():
                            reactors.append(user.id)
                            
                # Challenged user did not respond in time
                if second_player not in reactors:
                    await message.channel.send("The Death Roll Request was not accepted.")
                    
                # Game commences
                else:
                    await message.channel.send("The Death Roll will commence!")
                    time.sleep(1)
                    
                    # Challenger must give initial rolled value as an integer, will repeat question until valid answer is given
                    await message.channel.send("<@" + str(first_player) + ">, what is your starting roll?")
                    waiting = True
                    while waiting:
                        first_roll = await client.wait_for('message')
                        if first_roll.author.id == first_player:
                            try:
                                roll_value = int(first_roll.content)
                                waiting = False
                            except ValueError:
                                await message.channel.send("<@" + str(first_player) + ">, please type a valid number!")
                    curr_player = first_player
                    
                    #
                    while roll_value >= 1:
                        await message.channel.send("Rolling from 1-" + str(roll_value) + "...")
                        time.sleep(2)
                        roll_value = self.deathroll(roll_value)
                        await message.channel.send("<@" + str(curr_player) + "> rolled a " + str(roll_value) + "!")
                        
                        if roll_value == 1:
                            break # On exit, current player is the loser
                        
                        if curr_player == first_player:
                            curr_player = second_player
                        else:
                            curr_player = first_player
                            
                    if curr_player == first_player:
                        winner = second_player
                    else:
                        winner = first_player
                    await message.channel.send("<@" + str(curr_player) + "> lost the Death Roll! The winner is <@" + str(winner) + ">!")
                    
            # Default error message        
            else:
                await message.channel.send("Correct use of this command is: '$deathroll @[user you want to challenge]'!")
            
        
        # elif message.content.startswith('$weather'):
            
        
        # Brainrot Checker: Uses CSV file to keep track of number of brainrot vocabulary usage
        msg_content = message.content.lower()
        with open('brainrot.csv', 'r') as brainrot:
            words = csv.reader(brainrot, delimiter=',')
            for word in words:
                for field in word:
                    if field in msg_content:
                        await message.channel.send(str(message.author.display_name).capitalize() + "'s brainrot levels are increasing!")
                        df = pd.read_csv('brainrot_stats.csv', delimiter=',')
                        users = df['id'].tolist()
                        # Update CSV if user already tracked
                        if message.author.id in users:
                            old_brainrot_count = df.loc[df['id'] == message.author.id, 'count'].values[0]
                            # print(old_brainrot_count)
                            old_brainrot_level = df.loc[df['id'] == message.author.id, 'level'].values[0]
                            # print(old_brainrot_level)
                            df.loc[df['id'] == message.author.id, 'count'] += 1
                            new_brainrot_level = ((old_brainrot_count + 1) // 10) + 1
                            if old_brainrot_level != new_brainrot_level:
                                await message.channel.send("<@" + str(message.author.id) + ">'s brainrot level has reached " + str(new_brainrot_level)+ "!")
                                df.loc[df['id'] == message.author.id, 'level'] += 1
                            
                        else:
                        # Append new 
                            new_user = {'id': str(message.author.id), 'count': 1, 'level': 1}
                            df.loc[len(df)] = new_user
                            
                        df.to_csv('brainrot_stats.csv', mode='w', index=False, header=True)    
                        break
        
        
            
        
intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run('[Token Here]')
