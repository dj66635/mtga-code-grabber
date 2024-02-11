# MTGA Code Grabber

## Intro

I was browsing Reddit a little bit...

!(https://github.com/dj66635/mtga-code-grabber/robophobia.png)
!(https://github.com/dj66635/mtga-code-grabber/robophobia2.png)
!(https://github.com/dj66635/mtga-code-grabber/robophobia3.png)

Robo-phobia is running rampant. F*ck these fools, I say.

!(https://github.com/dj66635/mtga-code-grabber/touching.png)

Oh, that's so touching.

!(https://github.com/dj66635/mtga-code-grabber/lmao_no.png)

No?

## Setup

### 1. Install Tesseract

This project leverages Google's open source OCR Tesseract for text recognition. Follow [its repository](https://github.com/tesseract-ocr/tesseract) instructions to install it. Depeding on your OS it may be a pain the ass. For your reference, this project have been developed using Tesseract 5.3.3 in Windows 10.

### 2. Fill in the configuration file

MTGA Code Grabber :tm: connects to Reddit and Discord to get its inputs, and to Wizards website to claim the codes. Which means you need to create a `config.ini` file in the root folder of the project and set your credentials in it. Luckyly, I provide a sample for you [`example.config.ini`](https://github.com/dj66635/mtga-code-grabber/example.config.ini). Let's go over it quickly.

```
[Reddit]
client_id = *** 
client_secret = ***
subreddit_names = magicarena,mtg

[Discord]
auth_token = ***
channel_ids = 1038882144132550888,425270263416881152,1156189206553559121,517355406365032480
limit = 5
delay = 10

[Tesseract]
tesseract_cmd = C:\msys64\mingw64\bin\tesseract.exe

[MTGA]
user_username = ***
user_password = ***
```
Reddit's `client_id` and `client_secret` are your Reddit API credentials. If you have no clue how to get an API key, look at [the official instructions](https://www.reddit.com/wiki/api/).

`subreddit_names` is a comma-separated list of the subreddits you want to monitor. Don't you dare put a whitespace in this field.

Discord's `auth_token` is your Discord's authorization token. Pretty straightforward, huh?. If you don't know how to do a Google search, don't worry, [I've got you covered](https://www.androidauthority.com/get-discord-token-3149920/).

`channel_ids` is a comma-separated list of the channels you wish to monitor. You need to have Developer mode enabled to see this information. You'll figure it out.

`limit` is the maximum amount of new messages that will be fetched from every channel every time the bot polls Discord. `delay` is the time between each poll. Basically, I didn't want to have it querying the API constantly to make sure I didn't go over the rate limit. You may want to tweak the default values depending on the frequency of messages in your channels.

`tesseract_cmd` is the path to your Tesseract binary. If you dont know it, you can most likely find it running `which tesseract` or `where tesseract` on a terminal, depending on your platform.

`user_username` `user_password` are your Wizards of the Coast account credentials. You'll have to trust (or verify) that the code is not sending them to some fishy russian server.

### 4. Run it

Install the required packages
```
pip install requirements.txt
```

You're ready. Run the program on a terminal. Fingers crossed.
```
python main.py
```

### 5. ???

### 6. Profit

## Hard mode
You may want to play with the parameters of image processing and preprocessing. With the not-totally-accurate [architecture diagram](https://github.com/dj66635/mtga-code-grabber/docs/architecture.png) and the convoluted comments in the code you may even understand what's going on. 
There are some (tests)[https://github.com/dj66635/mtga-code-grabber/tests/tests.py] with sample inputs that I've been using to determine the image preprocessing and most appropriate set of parameters. But hey, I'm no expert at image analysis, most likely you can improve it.
Feel free to modify this tool. You better share any upgrades with me, thought.