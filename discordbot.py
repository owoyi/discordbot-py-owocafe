import discord
from discord.ext import tasks, commands
from discord.commands import Option
import os
import re
import datetime

client = discord.Bot(intents=discord.Intents.all())

OWNER_ID          = 524980170554212363
GUILD_ID          = 965933309911760947
DATA_CHANNEL_ID   = 999671948818784266
LOG_CHANNEL       = 1007933511644217426
LISTENING_ROLE_ID = 1011819296151847012
PLAYING_ROLE_ID   = 989163525127684157
STREAMING_ROLE_ID = 973457073515929620
IGNORE_ROLE_ID    = 975012732824866836
NOMIC_ROLE_ID     = 972652704314851329

APPLICATION_DETAILS = {}
APPLICATION_ROLE = {}
APPLICATION_ROLES = []

COLOR_SELECT = {
    "🌈 기본색":None,
    "🔴 빨간색":985709645513510922,
    "🧡 렌지색":989859648037351465,
    "💛 노란색":973465086867939359,
    "💚 초록색":1000038601586917387,
    "🍀 연두색":1000039581183381566,
    "💙 파란색":973111526842069022,
    "💧 하늘색":985710045339717652,
    "💗 핑크색":966310462109122591,
    "💜 연보라":973111512250077184,
    "🤎 초코색":1000039052784975972,
    "🤍 하얀색":1000038172220207144,
    "🖤 검은색":1000038359558803557
}

@client.event
async def on_ready():
    print("----------------------------------------")
    print("Bot is ready!")
    print(f"{client.user} ({client.user.id})")
    print("----------------------------------------")
    
    if await updateData() == False: return
    userGameRoleUpdate.start()

@tasks.loop(seconds=1)
async def userGameRoleUpdate():
    for member in client.get_guild(GUILD_ID).members:
        if member.bot: continue
        if member in client.get_guild(GUILD_ID).get_role(IGNORE_ROLE_ID).members: continue
        
        try:
            games = []
            for activity in member.activities:
                if activity.type == discord.ActivityType.streaming:
                    games.append(STREAMING_ROLE_ID)
                if activity.type == discord.ActivityType.listening:
                    games.append(LISTENING_ROLE_ID)
                if activity.type == discord.ActivityType.playing:
                    games.append(PLAYING_ROLE_ID)
                    try:
                        check = APPLICATION_ROLE.get(activity.application_id)
                        if check != None: games.append(check)
                        detail_check = APPLICATION_DETAILS.get(activity.details)
                        if detail_check != None: games.append(detail_check)
                    except:
                        check = APPLICATION_ROLE.get(activity.name.lower().strip())
                        if check != None:
                            games.append(check)

            for role_id in games:
                role = client.get_guild(GUILD_ID).get_role(role_id)
                if member not in role.members:
                    print(f"[{datetime.datetime.now()}] + {member.name} | {role.name}")
                    await member.add_roles(role)
                
            for role_id in APPLICATION_ROLES:
                role = client.get_guild(GUILD_ID).get_role(role_id)
                if member in role.members:
                    if role.id not in games:
                        print(f"[{datetime.datetime.now()}] - {member.name} | {role.name}")
                        await member.remove_roles(role)
        except: pass
                        
    active_count = len(client.get_guild(GUILD_ID).get_role(PLAYING_ROLE_ID).members)
    active_count = active_count + len(client.get_guild(GUILD_ID).get_role(STREAMING_ROLE_ID).members)
    active_count = active_count + len(client.get_guild(GUILD_ID).get_role(LISTENING_ROLE_ID).members)
    await client.change_presence(activity=discord.Game(name=f"떱카페에서 {active_count}명이 활동"))

async def updateData():
    print("Reading data contents from server...")
    try:
        messages = await client.get_channel(DATA_CHANNEL_ID).history(limit=100).flatten()
        messages.reverse()
        
        datas = ""
        for message in messages:
            _content = message.content
            _content = re.sub("```[a-z]*", "", _content)
            datas += f"{_content}\n"
            
        exec(datas, globals())
        print("Successfully updated data!\n")
        return datas
        
    except:
        print("Failed to update data :(")
        return False

def is_owner(ctx):
    return ctx.author.id == OWNER_ID
    
data_command = discord.SlashCommandGroup("data", "Data commands")
    
@data_command.command(description="활동 역할 데이터를 업데이트합니다.")
@commands.check(is_owner)
async def update(ctx):
    print(f"Member {ctx.author.name}#{ctx.author.discriminator} trying to update data...")
    _result = await updateData()
    if _result == False:
        await ctx.send_response(":x: 데이터를 업데이트하는데 실패했습니다.", ephemeral=True)
    else:
        with open("temp\\data_update.txt", "w", encoding="utf-8") as file:
            file.write(_result)
        with open("temp\\data_update.txt", "rb") as file:
            await ctx.send_response(":white_check_mark: 데이터를 업데이트하는데 성공했습니다.", 
                file=discord.File(file, "result.py"), ephemeral=True)
        os.remove("temp\\data_update.txt")

@data_command.command(description="활동 역할 데이터를 읽어옵니다.")
@commands.check(is_owner)
async def show(ctx):
    _roles = "APPLICATION_ROLE = {\n"
    
    for k, v in APPLICATION_ROLE.items():
        _key = f'"{k}"' if type(k) == str else k
        try: _description = f" # {client.get_guild(GUILD_ID).get_role(v).name}"
        except: _description = ""
        _roles += f"\t{_key}:{v},{_description}\n"
        
    _roles += "}\n\nAPPLICATION_DETAILS = {\n"
    
    for k, v in APPLICATION_DETAILS.items():
        _key = f'"{k}"' if type(k) == str else k
        try: _description = f" # {client.get_guild(GUILD_ID).get_role(v).name}"
        except: _description = ""
        _roles += f"\t{_key}:{v},{_description}\n"
        
    _roles += "}\n\nAPPLICATION_ROLES = ["
    
    for v in APPLICATION_ROLES:
        _roles += f"{v},"
    _roles += "]\n"
    
    with open("temp\\data_show.txt", "w", encoding="utf-8") as file:
        file.write(_roles)
    with open("temp\\data_show.txt", "rb") as file:
        await ctx.send_response(file=discord.File(file, "result.py"), ephemeral=True)
    os.remove("temp\\data_show.txt")
    
client.add_application_command(data_command)

@client.command(description="닉네임의 색상을 바꿔줍니다.")
async def namecolor(ctx, color: Option(str, name="색상", choices=COLOR_SELECT, required=True)):
    await client.get_channel(LOG_CHANNEL).send(f"{ctx.author.mention} 님이 /color {color} 명령어를 사용했습니다.")
    try:
        _role = client.get_guild(GUILD_ID).get_role(COLOR_SELECT.get(color))
        for k, v in COLOR_SELECT.items():
            if v == None: continue
            _r = client.get_guild(GUILD_ID).get_role(v)
            if _r == _role:
                if not ctx.author in _r.members:
                    await ctx.author.add_roles(_role)
            else:
                if ctx.author in _r.members:
                    await ctx.author.remove_roles(_r)
        if _role == None:
            await ctx.send_response(f":white_check_mark: 닉네임 색이 초기화 되었습니다!", ephemeral=True)
        else:
            await ctx.send_response(f":white_check_mark: {_role.mention} 역할 지급이 완료되었습니다!", ephemeral=True)
    except:
        await ctx.send_response(f":x: 알 수 없는 이유로 명령어 사용에 실패했습니다.", ephemeral=True)
    
@client.command(description="[DEBUG] 선택한 멤버의 활동을 확인합니다.")
async def usergame(ctx, member: discord.Member):
    await client.get_channel(LOG_CHANNEL).send(f"{ctx.author.mention} 님이 /usergame 명령어를 사용해 {member.mention} 의 활동을 확인합니다.")
    index = -1
    result = f"{member.mention} 님의 활동: \n"
    for activity in member.activities:
        index += 1
        result = f"{result}[{index}] {activity}\n"
    if index > -1:
        if len(result) > 2000:
            with open("temp\\user_game.txt", "w", encoding='utf-8') as file:
                file.write(result)
            with open("temp\\user_game.txt", "rb") as file:
                await ctx.send_response(file=discord.File(file, "result.txt"), ephemeral=True)
            os.remove("temp\\user_game.txt")
        else:
            print(result)
            await ctx.send_response(result, ephemeral=True)
    else:
        print(f"{member.mention} 님은 활동 중이지 않습니다.")
        await ctx.send_response(f"{member.mention} 님은 활동 중이지 않습니다.", ephemeral=True)
        
@client.command(description="[DEBUG] 멤버들의 활동을 확인합니다.")
async def usergames(ctx):
    await client.get_channel(LOG_CHANNEL).send(f"{ctx.author.mention} 님이 /usergames 명령어를 사용했습니다.")
    result = ""
    for member in client.get_guild(GUILD_ID).members:
        index = 0
        if len(member.activities) > 0 and not member.bot:
            result = f"{result}{member.mention}({member.display_name}) 님의 활동: \n"
            for activity in member.activities:
                result = f"{result}[{index}] {activity}\n"
                index += 1
            result = f"{result}\n"
    if result == "":
        await ctx.send_response("활동하는 멤버가 없습니다.", ephemeral=True)
    else:
        if len(result) > 2000:
            with open("temp\\user_games.txt", "w", encoding='utf-8') as file:
                file.write(result)
            with open("temp\\user_games.txt", "rb") as file:
                await ctx.send_response(file=discord.File(file, "result.txt"), ephemeral=True)
            os.remove("temp\\user_games.txt")
        else:
            await ctx.send_response(result, ephemeral=True)



def read_token():
    with open("token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()

try: BOT_TOKEN = os.environ['TOKEN']
except: BOT_TOKEN = read_token()

client.run(BOT_TOKEN)
