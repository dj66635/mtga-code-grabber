# MTGA Code Grabber

## Intro

As a new Magic player looking to fight my way through the aggresive economy of MTGA, I was browsing Reddit a little bit...

![](https://github.com/dj66635/mtga-code-grabber/blob/main/readme-pics/robophobia.PNG)

![](https://github.com/dj66635/mtga-code-grabber/blob/main/readme-pics/robophobia2.PNG)

![](https://github.com/dj66635/mtga-code-grabber/blob/main/readme-pics/robophobia3.PNG)

Robo-phobia is running rampant. F*ck these fools, I say.

![](https://github.com/dj66635/mtga-code-grabber/blob/main/readme-pics/touching.PNG)

Oh, that's so touching. ❤️

![](https://github.com/dj66635/mtga-code-grabber/blob/main/readme-pics/lmao_no.PNG)

No?

## Setup

### 1. Install Tesseract

This project leverages Google's open source OCR Tesseract for text recognition. Follow [its repository](https://github.com/tesseract-ocr/tesseract) instructions to install it. Depeding on your OS it may be a pain in the ass. For your reference, this project has been developed using Tesseract 5.3.3 and Python 3.7.1 in Windows 10.

### 2. Fill in the configuration file

MTGA Code Grabber :tm: connects to Reddit and Discord to get its inputs, and to Wizards website to claim the codes. Which means you need to create a `config.ini` file in the root folder of the project and set your credentials in it. Luckyly, I provide a sample for you [`example.config.ini`](https://github.com/dj66635/mtga-code-grabber/blob/main/example.config.ini). Let's go over it quickly.

```
[Reddit]
client_id = *** 
client_secret = ***
subreddit_names = magicarena,mtg

[Discord]
auth_token = ***
channel_ids = 1038882144132550888,425270263416881152,517355406365032480
limit = 5
delay = 10

[PreProcessing]
optimistic = False

[Tesseract]
tesseract_cmd = C:\msys64\mingw64\bin\tesseract.exe
workers = 2

[MTGA]
user_username = ***
user_password = ***
```
Reddit's `client_id` and `client_secret` are your Reddit API credentials. If you have no clue how to get an API key, look at [the official instructions](https://www.reddit.com/wiki/api/).

`subreddit_names` is a comma-separated list of the subreddits you want to monitor. Don't you dare put a whitespace in this field.

Discord's `auth_token` is your Discord's authorization token. Pretty straightforward, huh? If you don't know how to do a Google search, don't worry, [I've got you covered](https://www.androidauthority.com/get-discord-token-3149920/).

`channel_ids` is a comma-separated list of the channels you wish to monitor. You need to have Developer mode enabled to see this information. You'll figure it out.

`limit` is the maximum amount of new messages that will be fetched from every channel every time the bot polls Discord. `delay` is the time between each poll. Basically, I didn't want to have it querying the API constantly to make sure I didn't go over the rate limit. You may want to tweak the default values depending on the frequency of messages in your channels.

Setting `optimistic` to True will skip some stages of the preprocessing phase in order to almost halve the execution time at the expense of some accuracy. Probably not needed unless you're facing other world-class bots.

`tesseract_cmd` is the path to your Tesseract binary. If you dont know it, you can most likely find it running `which tesseract` or `where tesseract` on a terminal, depending on your platform.

`workers` is the number of threads that will be spawned to handle the Tesseract processing. Going beyond 2 or 3 is not worth it, and you might want to lower it to 1 if running this on a toaster.

`user_username` `user_password` are your Wizards of the Coast account credentials. You'll have to trust (or verify) that the code is not sending them to some fishy russian server.

### 4. Run it

Install the required packages.
```
pip install -r requirements.txt
```

You're ready. Run the program on a terminal. 🤞
```
python main.py
```

### 5. ???

![](https://github.com/dj66635/mtga-code-grabber/blob/main/readme-pics/header.PNG)

### 6. Profit

![](https://github.com/dj66635/mtga-code-grabber/blob/main/readme-pics/redeemed.PNG)

## Hard mode
You may want to play with the parameters of image processing and preprocessing. With the not-totally-accurate [architecture diagram](https://github.com/dj66635/mtga-code-grabber/blob/main/docs/architecture.png) and the convoluted comments in the code you may even understand what's going on. 
There are some [tests](https://github.com/dj66635/mtga-code-grabber/blob/main/tests/test.py) with sample inputs that I've been using to determine the image preprocessing techniques and the most appropriate set of parameters. But hey, I'm no expert at image analysis, you can most likely improve it.
Feel free to modify this tool. You better share any updates with me, thought. :smiling_imp:
