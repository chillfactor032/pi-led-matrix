from twitchio.ext import commands

class Bot(commands.Bot):

    def __init__(self, token, channel):
        self.token = token
        self.channel = channel
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


try:
    bot = Bot()
    bot.run()
except KeyboardInterrupt:
    print("=== TwitchBot Stopped ===")
