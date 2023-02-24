from discord.ext.commands import Bot
from discord.ext.tasks import loop

import discord

from dotenv import load_dotenv
import os
from settings import *
from asyncio import *
from helpers import *

import boto3
import discord
import random
import math
import time
import asyncio


intents = discord.Intents.all()

start_time = 0

data_base = {}



bot: Bot = Bot(command_prefix=COMMAND_SYMBOL, case_insensitive=True, intents=intents)


@loop(seconds=DANGER_LENGTH_SECONDS, count=None)
async def time_keeping_task():
    global  start_time
    global saved_data_base

    if(start_time != 0):
        # dataBase, dynamo = getDb(returnDynamo=True)


        # Update dangered people
        idx = 0
        for guild in saved_data_base:
            
            if len(guild['current']) >= DANGER_PLAYER_MIN:
              dangeredid = guild['danger']

              
              textChannel= getGuildTextChannel(int(guild['GuildID']))

              
              players = guild['current'].copy()
              del players[str(dangeredid)]
              new_danger_player = random.choice(list(players))

              setDangerLocal(new_danger_player, idx)

              if(textChannel):
                  await textChannel.send(f"TIMES UP!\n{at_user(dangeredid)} has lost everything. At least they are not dangerous anymore.\n{at_user(new_danger_player)} is now dangerous!")
              
              dynamo, _ = setUserCoins(guild['GuildID'], dangeredid, 0, returnDynamodb=True)
              
              setDanger(guild['GuildID'], new_danger_player, dynamo)

            idx +=1 





    start_time = time.time()

    # print(f"New start: {start_time}")

@bot.event
async def on_ready():
    print(f"{bot.user} is logged in!")
    time_keeping_task.start()

    global saved_data_base

    saved_data_base = getDb()

    # print(saved_data_base)


    # bot.loop.create_task(time_keeping_task())
    

# @bot.event
# async def on_message(ctx):
#     print("Hiiiiii")

@bot.command(name="hi", help=f"Speaks to {NET_NAME}")
async def on_message(ctx):
    await ctx.channel.send("Hello!")


@bot.command(name="join", help="Joins the danger dollar club")
async def on_message(ctx):
    await ctx.channel.send(init_user(ctx))

@bot.command(name='level', help="View your danger levels")
async def on_message(context):
  await context.channel.send(get_balance(context))

@bot.command(name="danger", help="Causes danger")
async def on_message(ctx):
    await ctx.channel.send(is_danger(ctx))

@bot.command(name="pass", help="Pass the danger")
async def on_message(ctx):
    await ctx.channel.send(pass_danger(ctx))


@bot.command(name="table", help="See all the danger")
async def on_message(ctx):
    await ctx.channel.send(embed=await get_table(ctx))

@bot.command(name="time", help="See how close the danger is")
async def on_message(ctx):
    await ctx.channel.send(view_time(ctx))


def view_time(ctx):
    username = ctx.author
    userid = username.id
    guildid = ctx.guild.id

    dynamoDB, userDb = getUserFromDb(guildid, userid, None,True)

    if userDb:
        global  start_time

        cur_time = time.time()

        left_time = DANGER_LENGTH_SECONDS - (cur_time - start_time)

        # print(left_time)

        secs =left_time

        mins = left_time/60
        hours = math.floor(mins/24)

        mins = math.floor(mins - hours*24)

        secs = secs - mins*60 - hours*24*60

        if(hours != 0):
            return f"{hours} h {mins} min {int(secs)} s is left."
        
        if(mins != 0):
           return f"{mins} min {int(secs)} s is left."
        
        return f"{secs:.4} s is left."
            

    else: 
       return f"The danger time does not matter to you. Get dangerous. {COMMAND_SYMBOL}join to play."
def init_user(ctx):
    username = ctx.author
    userid = username.id
    guildid = ctx.guild.id

    userDb, dynamoDB = getUserFromDb(guildid, userid, None,True)

    if userDb:
        return f"{at_user(userid)}, you are already on {NET_NAME}. Stop scamming the danger."
    else: 
        # Add user
        set_user(guildid, userid, STARTING_COINS, dynamoDB)

        new_db = getDb(guildid, dynamoDB)

        guild, idx = findGuild(new_db, guildid)

        global saved_data_base
        saved_data_base[idx] = new_db[idx]

        return f"Welcome to {NET_NAME} {at_user(userid)}, may the danger find you."
    
def get_balance(context):
  username = context.author
  usernameId = username.id
  guildId = context.guild.id

  userDb = getUserFromDb(guildId, usernameId)

  if userDb:
    return get_name(username) + "'s danger level is " + str(getCoinsFromUser(userDb))
  else:
    return f"Hey {at_user(usernameId)}, you are not dangerour yet. {COMMAND_SYMBOL}join to partake in the danger."
  

# def is_danger(context):
#   username = context.author
#   usernameId = username.id
#   guildId = context.guild.id

#   userDb = getUserFromDb(guildId, usernameId)

#   if userDb:
#     guild = getGuildFromDb(guildId)


#     player_count = len(guild['current'])

#     if(player_count < DANGER_PLAYER_MIN):
#        return f"You need {DANGER_PLAYER_MIN} players to start the danger."
    
#     if(is_dangerous(guild, usernameId)):
#        return f"{at_user(usernameId)} is dangerous!"

#     return f"You are not dangerous. {at_user(usernameId)} is!"
  
#   else:
#     return f"Hey {at_user(usernameId)}, you are not dangerour yet. {COMMAND_SYMBOL}join to partake in the danger."

def is_danger(context):
  username = context.author
  usernameId = username.id
  guildId = context.guild.id

#   userDb = getUserFromDb(guildId, usernameId)

  global saved_data_base


  guild, idx = findGuild(saved_data_base, guildId)

  if str(usernameId) in guild['current']:
    # guild = getGuildFromDb(guildId)

    player_count = len(guild['current'])

    if(player_count < DANGER_PLAYER_MIN):
       return f"You need {DANGER_PLAYER_MIN} players to start the danger."
    
    if(is_dangerous(guild, usernameId)):
       return f"{at_user(usernameId)} is dangerous!"

    return f"You are not dangerous. {at_user(usernameId)} is!"
  
  else:
    return f"Hey {at_user(usernameId)}, you are not dangerour yet. {COMMAND_SYMBOL}join to partake in the danger."


def pass_danger(context):
  username = context.author
  usernameId = username.id
  guildId = context.guild.id

#   userDb, dynamo = getUserFromDb(guildId, usernameId, returnDynamodb=True)
  global saved_data_base


  guild_data, idx = findGuild(saved_data_base, guildId)

  # print(guild_data['current'])
  if str(usernameId) in guild_data['current']:
    # guild = getGuildFromDb(guildId, dynamo)


    player_count = len(guild_data['current'])

    if(player_count < DANGER_PLAYER_MIN):
       return f"You need {DANGER_PLAYER_MIN} players to start the danger."
    if(is_dangerous(guild_data, usernameId)):
       
       players = guild_data['current'].copy()
       del players[str(usernameId)]


       new_danger_player = random.choice(list(players))

      #  print(saved_data_base)
       setDangerLocal(new_danger_player, idx)
      #  print(saved_data_base)


       return f"{at_user(new_danger_player)} is now dangerous!"
       
    
    return f"Can't pass something you don't have."
  else:
    return f"Hey {at_user(usernameId)}, you are not dangerous yet. {COMMAND_SYMBOL}join to partake in the danger."
  
# def pass_danger(context):
#   username = context.author
#   usernameId = username.id
#   guildId = context.guild.id

#   userDb, dynamo = getUserFromDb(guildId, usernameId, returnDynamodb=True)

#   if userDb:
#     guild = getGuildFromDb(guildId, dynamo)


#     player_count = len(guild['current'])

#     if(player_count < DANGER_PLAYER_MIN):
#        return f"You need {DANGER_PLAYER_MIN} players to start the danger."
    
#     if(is_dangerous(guild, usernameId)):
       
#        players = guild['current'].copy()
#        del players[str(usernameId)]


#        new_danger_player = random.choice(list(players))

#        setDanger(guildId, new_danger_player, dynamo)

#        return f"{at_user(new_danger_player)} is now dangerous!"
       
    
#     return f"Can't pass something you don't have."
#   else:
#     return f"Hey {at_user(usernameId)}, you are not dangerour yet. {COMMAND_SYMBOL}join to partake in the danger."


async def get_table(context):
  username = context.author
  usernameId = username.id
  guildId = context.guild.id
  guildName = context.guild.name

  userDb, dynamo = getUserFromDb(guildId, usernameId, returnDynamodb=True)

  if userDb:
    guild = getGuildFromDb(guildId, dynamo)
    sorted_dict = dict(sorted(guild["current"].items(), key=lambda item: item[1], reverse=True))
    pos = 1
    msg=""
    for userID in sorted_dict:
      user = await bot.fetch_user(int(userID))

      if(is_dangerous(guild, userID)):
         msg = msg + "\n{0} - {1} DD {2} (*DANGEROUS*)".format(pos, sorted_dict[userID], user.name)
      else:
         msg = msg + "\n{0} - {1} DD {2}".format(pos, sorted_dict[userID], user.name)

      
      pos = pos + 1
    embed=discord.Embed(title=f" *** {NET_NAME} Danger List ***", color=0xFF0000, description=msg)
  else:
    embed=discord.Embed(title=GUILD_NOT_ON_NET(guildName), color=0xFF0000)
  return embed



def is_dangerous(guild, id):
   return int(guild['danger']) == int(id)

def GUILD_NOT_ON_NET(guildName):
  return f"{guildName} is not DANGEROUS! Start making DangerDollars, be the first to join! Use {COMMAND_SYMBOL}join to get started."


def getGuildTextChannel(guildId):

  guild = bot.get_guild(guildId)
  textChannelList = guild.text_channels

  txtChannel = None

  for item in textChannelList:
    if(item.name.lower() == TEXT_CHANNEL):
      txtChannel = item
      break
    
  return txtChannel

def setDangerLocal(new_id, idx):
   global saved_data_base

   saved_data_base[idx]['danger'] = str(new_id)
   
def findGuild(listOfDb, guildId):
   idx = 0
   for dict in listOfDb:
      if dict['GuildID'] == guildId:
        return dict, idx
      idx+=1

bot.run(BOT_TOKEN)

