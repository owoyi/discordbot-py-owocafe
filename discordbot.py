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
    "π κΈ°λ³Έμ":None,
    "π΄ λΉ¨κ°μ":985709645513510922,
    "π§‘ λ μ§μ":989859648037351465,
    "π λΈλμ":973465086867939359,
    "π μ΄λ‘μ":1000038601586917387,
    "π μ°λμ":1000039581183381566,
    "π νλμ":973111526842069022,
    "π§ νλμ":985710045339717652,
    "π νν¬μ":966310462109122591,
    "π μ°λ³΄λΌ":973111512250077184,
    "π€ μ΄μ½μ":1000039052784975972,
    "π€ νμμ":1000038172220207144,
    "π€ κ²μμ":1000038359558803557
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
    await client.change_presence(activity=discord.Game(name=f"λ±μΉ΄νμμ {active_count}λͺμ΄ νλ"))

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
    
@data_command.command(description="νλ μ­ν  λ°μ΄ν°λ₯Ό μλ°μ΄νΈν©λλ€.")
@commands.check(is_owner)
async def update(ctx):
    print(f"Member {ctx.author.name}#{ctx.author.discriminator} trying to update data...")
    _result = await updateData()
    if _result == False:
        await ctx.send_response(":x: λ°μ΄ν°λ₯Ό μλ°μ΄νΈνλλ° μ€ν¨νμ΅λλ€.", ephemeral=True)
    else:
        with open("temp\\data_update.txt", "w", encoding="utf-8") as file:
            file.write(_result)
        with open("temp\\data_update.txt", "rb") as file:
            await ctx.send_response(":white_check_mark: λ°μ΄ν°λ₯Ό μλ°μ΄νΈνλλ° μ±κ³΅νμ΅λλ€.", 
                file=discord.File(file, "result.py"), ephemeral=True)
        os.remove("temp\\data_update.txt")

@data_command.command(description="νλ μ­ν  λ°μ΄ν°λ₯Ό μ½μ΄μ΅λλ€.")
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

@client.command(description="λλ€μμ μμμ λ°κΏμ€λλ€.")
async def namecolor(ctx, color: Option(str, name="μμ", choices=COLOR_SELECT, required=True)):
    await client.get_channel(LOG_CHANNEL).send(f"{ctx.author.mention} λμ΄ /color {color} λͺλ Ήμ΄λ₯Ό μ¬μ©νμ΅λλ€.")
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
            await ctx.send_response(f":white_check_mark: λλ€μ μμ΄ μ΄κΈ°ν λμμ΅λλ€!", ephemeral=True)
        else:
            await ctx.send_response(f":white_check_mark: {_role.mention} μ­ν  μ§κΈμ΄ μλ£λμμ΅λλ€!", ephemeral=True)
    except:
        await ctx.send_response(f":x: μ μ μλ μ΄μ λ‘ λͺλ Ήμ΄ μ¬μ©μ μ€ν¨νμ΅λλ€.", ephemeral=True)
    
@client.command(description="[DEBUG] μ νν λ©€λ²μ νλμ νμΈν©λλ€.")
async def usergame(ctx, member: discord.Member):
    await client.get_channel(LOG_CHANNEL).send(f"{ctx.author.mention} λμ΄ /usergame λͺλ Ήμ΄λ₯Ό μ¬μ©ν΄ {member.mention} μ νλμ νμΈν©λλ€.")
    index = -1
    result = f"{member.mention} λμ νλ: \n"
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
            await ctx.send_response(result, ephemeral=True)
    else:
        await ctx.send_response(f"{member.mention} λμ νλ μ€μ΄μ§ μμ΅λλ€.", ephemeral=True)
        
@client.command(description="[DEBUG] λ©€λ²λ€μ νλμ νμΈν©λλ€.")
async def usergames(ctx):
    await client.get_channel(LOG_CHANNEL).send(f"{ctx.author.mention} λμ΄ /usergames λͺλ Ήμ΄λ₯Ό μ¬μ©νμ΅λλ€.")
    result = ""
    for member in client.get_guild(GUILD_ID).members:
        index = 0
        if len(member.activities) > 0 and not member.bot:
            result = f"{result}{member.mention}({member.display_name}) λμ νλ: \n"
            for activity in member.activities:
                result = f"{result}[{index}] {activity}\n"
                index += 1
            result = f"{result}\n"
    if result == "":
        await ctx.send_response("νλνλ λ©€λ²κ° μμ΅λλ€.", ephemeral=True)
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
