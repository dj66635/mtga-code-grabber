import requests
import json
import time
from constants import DISCORD, IMG, TXT, DISCORD_URL, CHANNELS_ENDPOINT, GUILDS_ENDPOINT, MESSAGES_ENDPOINT, LIMIT_QUERY, AFTER_QUERY
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

channels = config['Discord']['channel_ids'].split(',')
limit = config['Discord']['limit']
delay = int(config['Discord']['delay'])
headers = {'Authorization': config['Discord']['auth_token']}

def listenToDiscord(postsQueue):
    print('Listening to Discord...')
    lastMsgId = dict.fromkeys(channels, 0)
    readeableName = dict.fromkeys(channels, '')
    for channelId in channels: # load human-readeable name for logging and find last message id
        url = DISCORD_URL + CHANNELS_ENDPOINT + channelId
        response = requests.get(url, headers=headers)
        j = json.loads(response.content)
        lastMsgId[channelId] = j['last_message_id']
        channelName = j['name']
        
        url = DISCORD_URL + GUILDS_ENDPOINT + j['guild_id']
        response = requests.get(url, headers=headers)
        j = json.loads(response.content)
        guildName = j['name']
        readeableName[channelId] = f'# {channelName} @ {guildName}'
        
    while True:
        # After delay time, grab limit messages only after the last seen
        time.sleep(delay)
        for channelId in channels:
            lastMsgIdChannel = pollChannel(channelId, readeableName[channelId], lastMsgId[channelId], postsQueue)
            lastMsgId[channelId] = lastMsgIdChannel
                        
                        
def pollChannel(channelId, channelName, lastMsgId, postsQueue):
    descriptiveName = DISCORD + ' (' + channelName + ')'
    url = DISCORD_URL + CHANNELS_ENDPOINT + channelId + MESSAGES_ENDPOINT + LIMIT_QUERY + limit + AFTER_QUERY + lastMsgId
    
    newLastMsgId = lastMsgId    
    r = requests.get(url, headers=headers)
    messages = json.loads(r.content)	
        
    if len(messages) > 0:
        for i in range(len(messages)):
            msg = messages[i]
            if i == 0:
                newLastMsgId = msg['id']
            content = msg['content']  # will use it as title as well
            postsQueue.put((descriptiveName, content, content, TXT)) 
                
            if len(msg['attachments']) > 0:
                for att in msg['attachments']:
                    att_url = att['url']
                    response = requests.get(att_url)
                    postsQueue.put((descriptiveName, content, response.content, IMG))
                    
    return newLastMsgId
                    
                    