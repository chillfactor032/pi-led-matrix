import argparse
import os
import json
import random
import threading
import requests
from twitchio.ext import commands, routines
from matrix import LedMatrix

class Bot(commands.Bot):

    def __init__(self, config):
        self.token = config.get("token", None)
        self.channel = config.get("channel", None)
        super().__init__(token=self.token, prefix='!', initial_channels=[self.channel])
        self.matrix = LedMatrix(32, 32, brightness=0.03)
        self.emote_cdn = "https://static-cdn.jtvnw.net/emoticons/v2/<id>/default/dark/4.0"
        self.emote_buffer_max_size = 10
        self.emote_buffer = []
        self.emote_cache_dir = config.get("emote_cache_dir", "/tmp")

    async def event_ready(self):
        print("=== TwitchBot Ready ===")
        print(f"Logged in as | {self.nick}")
        print(f"Connected Channel: {self.channel}")
        self.emote_timer.start()

    async def event_message(self, message):
        # Ignore messages from the bot itself
        if message.echo: return
        emotes = self.emotes_from_message(message)
        for emote in emotes:
            x = threading.Thread(target=self.download_emote, args=(emote,))
            x.start()

    @routines.routine(seconds=7.0)
    async def emote_timer(self):
        print("Emote Size: "+str(len(self.emote_buffer)))
        if len(self.emote_buffer) > 0:
            emote_id = random.choice(self.emote_buffer)
            path = os.path.join(self.emote_cache_dir, emote_id)
            #url = f"https://static-cdn.jtvnw.net/emoticons/v2/{emote_id}/default/dark/4.0"
            self.matrix.show_img(path)

    def emote_buffer_add(self, emote_list: list):
        """ Add a list of emotes to the emote buffer. 
            Remove duplicates and remove the oldest to stay under max.
            emote_buffer is sorted oldest (head) to most recent (tail).
        """
        self.emote_buffer = [x for x in self.emote_buffer if x not in emote_list]
        for emote in emote_list:
            self.emote_buffer.append(emote)
        while len(self.emote_buffer) > self.emote_buffer_max_size:
            self.emote_buffer.pop(0)

    def emotes_from_message(self, message):
        """ Return a list of emotes from the message """
        emotes_in_msg = []
        emotes_str = message.tags.get("emotes", None)
        if not emotes_str:
            return []
        emotes = emotes_str.split("/")
        for emote in emotes:
            emotes_in_msg.append(emote.split(":")[0])
        return emotes_in_msg
    
    def download_emote(self, emote_id):
        url = self.emote_cdn.replace("<id>", emote_id)
        path = os.path.join(self.emote_cache_dir, emote_id)
        if os.path.exists(path):
            return
        resp = requests.get(url)
        if resp.status_code >= 300:
            return None
        try:
            with open(path, "wb") as f:
                f.write(resp.content)
        except Exception as e:
            print("Error downloading emote")
            print(e)
        self.emote_buffer_add([emote_id])


    def is_priv(self, user):
        """ Get the level of the user: tier/mod/broadcaster"""
        if user is None:
            return False
        if(user.is_mod):
            return True
        if(user.badges == None):
            return False
        if(user.badges.get('broadcaster', '0') == '1'):
            return True
        return False

def main():
    parser = argparse.ArgumentParser(
                            prog='PiLedWallBot',
                            description='A simple Twitch chatbot to demonstrate led matrix integration',
                            epilog='by ChillFacToR032')

    parser.add_argument("config", help="Path to a config file. See the config_template.json for the format.")

    args = parser.parse_args()
    if not os.path.isfile(args.config):
        print("Error: config file does not exists. Create one using config_template.json")
        return
    try:
        config = None
        with open(args.config) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print("Error decoding config as JSON")
        print(e)
        return
    try:
        bot = Bot(config)
        bot.run()
    except KeyboardInterrupt:
        print("=== TwitchBot Stopped ===")

if __name__ == '__main__':
    main()
