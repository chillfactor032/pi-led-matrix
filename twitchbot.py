import argparse
import os
import json
from twitchio.ext import commands

class Bot(commands.Bot):

    def __init__(self, config):
        self.token = config.get("token", None)
        self.channel = config.get("channel", None)
        super().__init__(token=self.token, prefix='!', initial_channels=[self.channel])

    async def event_ready(self):
        print("=== TwitchBot Ready ===")
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        # Ignore messages from the bot itself
        if message.echo: return
        await self.handle_commands(message)

    @commands.command()
    async def mode(self, ctx: commands.Context):
        if not self.is_priv(ctx.author):
            # User is not Mod/Broadcaster
            return
        await ctx.send(f'Hello {ctx.author.name}!')

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

    parser.add_argument("config",
                        required=True,
                        help="Path to a config file. See the config_template.json for the format.")

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
