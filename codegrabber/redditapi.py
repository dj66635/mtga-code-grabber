import praw
import requests
from constants import REDDIT, IMG, TXT, PNG, JPG, JPEG
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

reddit = praw.Reddit(client_id = config['Reddit']['client_id'], 
                     client_secret = config['Reddit']['client_secret'], 
                     user_agent = 'totally_regular_chrome')

subreddit_names = config['Reddit']['subreddit_names']

def listenToReddit(postsQueue):
    print('Listening to Reddit...')
    subreddit = reddit.subreddit('+'.join(subreddit_names.split(',')))
    for submission in subreddit.stream.submissions(skip_existing=True):
        responses = readSubmission(submission)
        for response in responses:
            descriptiveName, title, content, contentType = response
            postsQueue.put((descriptiveName, title, content, contentType))

        
def readSubmission(submission):
    descriptiveName = REDDIT + ' (r/' + submission.subreddit.display_name + ')'
    if hasattr(submission, 'is_gallery'):
        responses = []
        for i in submission.media_metadata.items():
            image_url = i[1]['p'][0]['u']
            image_url = image_url.split('?')[0].replace('preview', 'i')
            response = requests.get(image_url)
            responses += [(descriptiveName, submission.title, response.content, IMG)]
        return responses
            
    elif submission.url.endswith((PNG, JPG, JPEG)): 
        image_url = submission.url
        response = requests.get(image_url)
        return [(descriptiveName, submission.title, response.content, IMG)]
    
    else:
        return [(descriptiveName, submission.title, submission.selftext, TXT)]
