from botocore.exceptions import ClientError
import boto3
import json
import random
from settings import *
import discord

def getUserFromDb(guildId, memberId,dynamodb=None, returnDynamodb=False):
  if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ca-central-1', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

  table = dynamodb.Table(AWS_TABLE)

  try:
      response = table.get_item(
          Key={'GuildID': guildId},
          ProjectionExpression="#cur.#id",
          ExpressionAttributeNames={
              '#cur':'current',
              '#id': f'{memberId}'
          })
  except ClientError as e:
      print("e.response['Error']['Message']")
  else:
      if returnDynamodb:
        return response.get('Item'),dynamodb 
      else:
        return response.get('Item')

def getGuildFromDb(guildId,dynamodb=None, returnDynamodb=False):
  if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ca-central-1', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

  table = dynamodb.Table(AWS_TABLE)

  try:
      response = table.get_item(Key={'GuildID': guildId})
  except ClientError as e:
      print("e.response['Error']['Message']")
  else:
      if returnDynamodb:
        return  response.get('Item'), dynamodb
      else:
        return response.get('Item')

def getDb(dynamodb=None, returnDynamo=False):
  if not dynamodb:
       dynamodb = boto3.resource('dynamodb', region_name='ca-central-1', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

  table = dynamodb.Table(AWS_TABLE)
  response = table.scan()
  if returnDynamo:
    return response["Items"], dynamodb
  else:
    return response["Items"]


def setPrevious(guildId, newData, dynamodb=None):

  if not dynamodb:
      dynamodb = boto3.resource('dynamodb', region_name='ca-central-1', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

  table = dynamodb.Table(AWS_TABLE)

  response = table.update_item(
        Key={
            'GuildID': guildId,
        },
        UpdateExpression="set previous=:new",
        ExpressionAttributeValues={
            ':new': newData
        },
        ReturnValues="UPDATED_NEW"
    )
  return response

def setDanger(guildId, newData, dynamodb=None):

  if not dynamodb:
      dynamodb = boto3.resource('dynamodb', region_name='ca-central-1', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

  table = dynamodb.Table(AWS_TABLE)

  response = table.update_item(
        Key={
            'GuildID': guildId,
        },
        UpdateExpression="set danger=:new",
        ExpressionAttributeValues={
            ':new': newData
        },
        ReturnValues="UPDATED_NEW"
    )
  return response



def setGuildWithUser(guildId,userId, coins, dynamodb=None, returnDynamodb=False):
  if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ca-central-1', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

  table = dynamodb.Table(AWS_TABLE)

  response = table.put_item(
       Item={
            'GuildID': guildId,
            'current': {
              f"{userId}" : coins
            },
            'previous': {
              f"{userId}" : coins
            },
            'danger': 0
        }
    )
  if returnDynamodb:
    return dynamodb, response
  else:
    return response

def setUserCoins(guildId, memberId, amount=1, dynamodb=None, returnDynamodb=False, setPrev=False):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ca-central-1', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    table = dynamodb.Table(AWS_TABLE)
    if(not setPrev):
      response = table.update_item(
          Key={
              'GuildID': guildId,
          },
          UpdateExpression="set #cur.#id = :val",
          ExpressionAttributeNames={
              '#cur':'current',
              '#id': f'{memberId}',
          },
          ExpressionAttributeValues={
              ':val': amount
          },
          ReturnValues="UPDATED_NEW"
      )
    else:
      response = table.update_item(
          Key={
              'GuildID': guildId,
          },
          UpdateExpression="set #cur.#id = :val, #prev.#id = :val",
          ExpressionAttributeNames={
              '#cur':'current',
              '#id': f'{memberId}',
              '#prev':'previous'
          },
          ExpressionAttributeValues={
              ':val': amount
          },
          ReturnValues="UPDATED_NEW"
      )

    if returnDynamodb:
      return dynamodb, response
    else:
      return response

def addUserCoins(guildId, memberId, increaseAmount=1, dynamodb=None, returnDynamodb=False ):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ca-central-1')

    table = dynamodb.Table(AWS_TABLE)

    response = table.update_item(
        Key={
            'GuildID': guildId,
        },
        UpdateExpression="set #cur.#id = #cur.#id + :val",
        ExpressionAttributeNames={
            '#cur':'current',
            '#id': f'{memberId}',
        },
        ExpressionAttributeValues={
            ':val': increaseAmount
        },
        ReturnValues="UPDATED_NEW"
    )

    if returnDynamodb:
      return dynamodb, response
    else:
      return response

def getCoinsFromUser(userData):
    return list(userData["current"].values())[0]

def get_name(username):
  if username.nick:
    return username.nick
  else:
    return username.name

def at_user(id):
  return "<@!{0}>".format(id)

def set_user(guildId, id, coins, dynamoDB=None):
  guild = getGuildFromDb(guildId, dynamoDB)
  if(guild):
    setUserCoins(guildId, id, coins, dynamoDB, setPrev=True)
  else:
    setGuildWithUser(guildId, id, coins, dynamoDB)


def get_losing_text():

  with open("words.json", 'r') as f:
    losing_array = json.load(f)["lost"]
  
  return random.choice(losing_array)

def get_random_text(type):

  with open("words.json", 'r') as f:
    array = json.load(f)[type]
  
  return random.choice(array)


def buildUpdateMessage(text):
  embed = discord.Embed(title="==== UPDATE ALERT ====", color=0xa9ce46)
  embed.add_field(name=f"--- {text['title']} ---", value=text['desc'], inline=False)
  #embed.add_field(name=f"Also...", value="CloutNet will be down temporarily", inline=False)

  return embed

"""
def del_cloutnet(context):
  guildId = context.guild.id
  if guild_in_db(guildId):
    del db[guildId]
"""