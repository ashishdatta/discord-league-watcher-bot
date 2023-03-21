from riotwatcher import LolWatcher, ApiError
from timeloop import Timeloop
import pandas as pd
import os
from dotenv import load_dotenv
import nextcord
from nextcord.ext import commands
import time
from datetime import timedelta
import nextcord
from nextcord.ext import commands, tasks


import pprint 
pp = pprint.PrettyPrinter(indent=4)

tl = Timeloop()
load_dotenv()
RIOT_KEY=os.getenv("RIOT_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEV_GUILD_ID = int(os.getenv("DEV_GUILD_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
SUMMONER= os.getenv("SUMMONER")
intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True


# golbal variables
api_key = RIOT_KEY
watcher = LolWatcher(api_key)
my_region = 'na1'
last_time_check = int(time.time())

class Bot(commands.Bot):
    def __init__(self, summoner, last_time_checked):#*args, **kwargs):
        super().__init__()#*args, **kwargs)

        # start the task to run in the background
        self.my_background_task.start()
        self.summoner = summoner
        self.my_region = "na1"
        self.summoner_obj = watcher.summoner.by_name("na1", summoner)
        self.last_time_checked = last_time_checked

    @tasks.loop(seconds=60)  # task runs every 60 seconds
    async def my_background_task(self):
        channel = self.get_channel(CHANNEL_ID)  # channel ID goes here
        games = watcher.match.matchlist_by_puuid(self.my_region, self.summoner_obj['puuid'])
        match = watcher.match.by_id(my_region, games[0])
        ts = int(match['info']['gameEndTimestamp'] / 1000)
        if self.last_time_checked < ts:
            for p in match['info']['participants']:
                if p['summonerName'] == self.summoner:
                    result = p["win"]
                    champ_used = p['championName']
                    dmg_dealt = p['totalDamageDealtToChampions']
                    kills = p['kills']
                    deaths = p['deaths']
                    assists = p['assists']
                    if result is True:
                        await channel.send(f"Nice! {self.summoner} just went {kills}/{deaths}/{assists} and won as {champ_used} and dealt {dmg_dealt} to champions")
                    else:
                        await channel.send(f"Oof {self.summoner} went {kills}/{deaths}/{assists} and lost as {champ_used}")
                    self.last_time_checked = int(time.time())
                else:
                    continue

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in

bot = Bot(summoner=SUMMONER, last_time_checked=int(time.time()))
bot.run(DISCORD_TOKEN)
