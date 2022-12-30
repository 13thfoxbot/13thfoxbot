import os
from twitchio.ext import commands, routines
import twitchio
from dotenv import load_dotenv
import datetime
import csv

with open('whitelist.txt', 'r') as f:
    reader = csv.reader(f)
    wl=list(reader)

print(wl[0])

load_dotenv()
#set up enviornment
TMI_TOKEN = os.environ.get('TMI_TOKEN')
CLIENT_ID = os.environ.get('CLIENT_ID')
BOT_NICK = os.environ.get('BOT_NICK')
BOT_PREFIX = os.environ.get('BOT_PREFIX')
CHANNEL = os.environ.get('CHANNEL')

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=TMI_TOKEN, prefix="?", initial_channels=[CHANNEL])

        # white list channels to shoutout
        self.whitelist = wl[0]
        print(self.whitelist)
        #list of channels to shout out and channels that have been shouted out
        self.shoutoutList = []
        self.shoutedoutList = []

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")
        self.send_reminder.start()

    async def event_message(self, message: twitchio.Message):
        #ignore bot message
        if message.echo:
            return
        #log chat for testing
        print(message.content)
        #check messages for users to shout out and add them to the list if needed.
        if message.author.name.lower() in self.whitelist and message.author.name.lower() not in self.shoutedoutList:
            self.shoutoutList.append(message.author.name.lower())
            print(f'message shoutout {self.shoutoutList}')
            print(f'message shoutedout {self.shoutedoutList}')
            await self.handle_commands(message)

        #forward message content to commands
        await self.handle_commands(message)

    @commands.command()
    async def add(self, ctx, *, name):
        # add twitch user to shoutout list
        # e.g ?add 13thfox
        #ensure moderator
        if(ctx.author.is_mod):
            name = name.lower()
            if name in self.whitelist:
                await ctx.send(f'{name} already on whitelist')
                print(f'current whitelist {self.whitelist}')
            elif name not in self.whitelist:
                self.whitelist.append(name)
                print(f'user {name} added to whitelist')
                print(self.whitelist)
                # send confirmation
                await ctx.send(f'added {name} to whitelist')
                f = open('whitelist.txt', 'a')
                f.write(f",{name}")
                f.close()
                f = open('whitelist.txt', 'r')
                print(f.read())



    @commands.command()
    async def remove(self, ctx, *, name):
        if (ctx.author.is_mod):
            # remove twitch user from shoutout list
            # e.g ?remove 13thfox
            name = name.lower()
            while True:
                try:
                    self.whitelist.remove(name)
                    # send confirmation
                    await ctx.send(f'removed {name} from whitelist')
                    print(f'removed {name} from list')
                    f = open('whitelist.txt', 'r')
                    data = f.read()
                    print(data)
                    data=data.replace(name, '')
                    print(data)


                    with open('whitelist.txt', 'w') as file:
                        file.write(data)

                    break
                except ValueError:
                    await ctx.send (f'Not able to remove {name} from list')
                    print('could not remove user from list')
                    break

            print(self.whitelist)

    @commands.command()
    async def reset(self, ctx: commands.Context):
        if (ctx.author.is_mod):
            # resets the shoutout and shoutedout list so shoutouts will happen if a user on the whitelist chats
            self.shoutoutList = []
            self.shoutedoutList = []
            print('shoutouts reset')
            print(self.shoutoutList)
            print(self.shoutedoutList)
            await ctx.send(f'shoutouts reset')

    @routines.routine(time=datetime.datetime(year=2022, month=12, day=18, hour=5, minute=0))
    async def resetrout(self):
        # resets the shoutout list once a day
        print('shoutout list reset')
        self.shoutoutList=[]

    @resetrout.before_routine
    async def before_resetrout(self):
        await self.wait_for_ready()

    @commands.command()
    async def help(self, ctx: commands.Context):
        if (ctx.author.is_mod):
            # list of 13thfox bots commands
            await ctx.send (f'13thfoxbot will shoutout users on the whitelist when they chat for the first time each day. '
                            f' ?add adds users to whitelist.  ?remove removes users from whitelist.')

    @routines.routine(seconds=5)
    async def send_reminder(self):
        chan = self.get_channel(CHANNEL)
        if self.shoutoutList:
            await chan.send(f'!so {self.shoutoutList[0]}')
            self.shoutedoutList.append(self.shoutoutList[0])
            self.shoutoutList = self.shoutoutList[1:]
            print(f'routine shoutout {self.shoutoutList}')
            print(f'routine shoutedout {self.shoutedoutList}')

    @send_reminder.before_routine
    async def before_send_reminder(self):
        await self.wait_for_ready()

bot = Bot()
bot.run()