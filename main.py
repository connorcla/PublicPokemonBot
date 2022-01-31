# bot.py
import asyncio
import os
import random
import time
from dotenv import load_dotenv

from googleapiclient.discovery import build
from google.oauth2 import service_account

from discord.ext import tasks
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='-')

trainer_list = []
trainer_num = 0
pokemon_list = [[]]
poke_num = []
catch_limit = []
currentPoke = ""
trainer1 = ""
trainer2 = ""
x = 0

# Set up google sheet connection
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'
creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
SAMPLE_SPREADSHEET_ID = '1c2sexI1t8v_MZN7NDBPORvkvAR0-cUatAf2p1QQMaEk'

service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()
# Done with connection

names = []
sprites = []
types = []
hp = []
atk = []
defense = []
speed = []
new_names = []
tic = 0
toc = 0
battle = False


def erase_extra_chars(s):
    s = s.replace('[', '')
    s = s.replace(']', '')
    s = s.replace('\'', '')
    return s


def update_values():
    global names
    global sprites
    global types
    global hp
    global atk
    global defense
    global speed
    global new_names
    global trainer_num
    global trainer_list
    global poke_num
    global pokemon_list
    global catch_limit
    request = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet1!c2:c899").execute()
    request2 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet1!b2:b899").execute()
    request3 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet1!e2:e899").execute()
    request4 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet1!f2:f899").execute()
    request5 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet1!g2:g899").execute()
    request6 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet1!h2:h899").execute()
    request7 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet1!i2:i899").execute()
    request8 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet2!a2").execute()
    names = request.get('values', [])
    sprites = request2.get('values', [])
    types = request3.get('values', [])
    hp = request4.get('values', [])
    atk = request5.get('values', [])
    defense = request6.get('values', [])
    speed = request7.get('values', [])
    temp = request8.get('values', [])
    trainer_num = erase_extra_chars(str(temp[0]))
    trainer_num = int(trainer_num)
    if trainer_num > 0:
        loc = chr(ord('c')+trainer_num)
        request9 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet2!c1:"+loc+"1").execute()
        temp = request9.get('values', [])
        trainer_list = []
        for i in range(len(temp[0])):
            trainer_list.append(erase_extra_chars(str(temp[0][i])))
        poke_num = []
        for i in range(trainer_num):
            loc = chr(ord('c') + i)
            request10 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet2!"+loc+"2").execute()
            temp = request10.get('values', [])
            temp2 = int(erase_extra_chars(str(temp[0])))
            poke_num.append(temp2)
            catch_limit.append(0)
        pokemon_list = []
        for i in range(trainer_num):
            loc = chr(ord('c') + i)
            pokemon_list.append([])
            for j in range(poke_num[i]):
                request11 = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                               range="Sheet2!" + loc + str(j+3)).execute()
                temp = request11.get('values', [])
                temp2 = str(erase_extra_chars(str(temp[0])))
                pokemon_list[i].append(temp2)
    print(trainer_list)
    print(pokemon_list)
    new_names = []
    for i in range(len(names)):
        new_names.append(str(names[i]))


update_values()
t = random.choice(range(20, 40))


def get_pokemon():
    global x
    global t
    x = random.choice(range(0, 802))
    t = random.choice(range(20, 40))
    poke = str(names[x])
    poke = erase_extra_chars(poke)
    poke2 = str(sprites[x])
    poke2 = erase_extra_chars(poke2)
    for p in range(len(catch_limit)):
        catch_limit[p] = 0
    return poke, poke2


def display_battle(team1, team2, idx1, idx2):
    poke1 = team1[idx1]
    num = new_names.index("[\'" + poke1 + "\']")
    display1 = erase_extra_chars(str(sprites[num]))
    poke2 = team2[idx2]
    num = new_names.index("[\'" + poke2 + "\']")
    display2 = erase_extra_chars(str(sprites[num]))
    return display1, poke1, display2, poke2


@tasks.loop(minutes=t)
async def send():
    global tic
    if not battle:
        tic = time.perf_counter()
        channel = bot.get_channel(684500984114053253)
        response = get_pokemon()
        global currentPoke
        currentPoke = response[0]
        await channel.send(response[1])
        await channel.send("A wild " + response[0] + " has appeared!")


@send.before_loop
async def before():
    await bot.wait_until_ready()
send.start()


@bot.command(name='Update', help='Updates values from spreadsheet.')
async def upd(ctx):
    update_values()
    await ctx.send("Values have been updated.")


@bot.command(name='Register', help='Registers Discord name with the trainer list. '
                                   'Allows for trainer to catch and battle pokemon.')
async def regis(ctx):
    global trainer_num
    global trainer_list
    if ctx.author.name not in trainer_list:
        trainer_list.append(ctx.author.name)
        catch_limit.append(0)
        pokemon_list.append([])
        poke_num.append(0)
        loc = chr(ord('c')+trainer_num)
        sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet2!" + loc + "1",
                              valueInputOption="USER_ENTERED", body={'values': [[ctx.author.name]]}).execute()
        trainer_num = trainer_num + 1
        sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet2!a2",
                              valueInputOption="USER_ENTERED", body={'values': [[str(trainer_num)]]}).execute()
        sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet2!" + loc + "2",
                              valueInputOption="USER_ENTERED", body={'values': [['0']]}).execute()
        await ctx.send(f"{ctx.author.name} has been registered!")
        print(trainer_list)
    else:
        await ctx.send(f"{ctx.author.name} is already a registered trainer.")


@bot.command(name='ListTrainers', help="Shows the list of registered trainers.")
async def show_list(ctx):
    t_list = str(trainer_list[:])
    t_list = erase_extra_chars(t_list)
    await ctx.send(t_list)


@bot.command(name='Catch', help="Attempt to catch the most recent shown Pokemon. "
                                "Will result in a catch, a failure, or the Pokemon will flee.")
async def catch(ctx):
    global currentPoke
    global x
    global tic
    global toc
    toc = time.perf_counter()
    index = trainer_list.index(ctx.author.name)
    if ctx.author.name in trainer_list and catch_limit[index] < 3 and len(pokemon_list[index]) < 31 and (toc-tic) < 300\
            and currentPoke not in pokemon_list[index]:
        chance = random.choice(range(1, 10))
        if chance in range(1, 7):
            if x == 145 or 146 or 147 or 151 or 152 or range(250, 252) or range(378, 387) or range(481, 495) or range(
                    639, 650) or range(717, 722) or range(786, 810) or range(889, 899):
                if random.choice(range(1, 100)) < 60:
                    pokemon_list[index].append(currentPoke)
                    poke_num[index] = poke_num[index]+1
                    catch_limit[index] = 4
                    loc = chr(ord('c')+index)
                    sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                          range="Sheet2!" + loc + str(len(pokemon_list[index])+2),
                                          valueInputOption="USER_ENTERED",
                                          body={'values': [[currentPoke]]}).execute()
                    sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                          range="Sheet2!" + loc + "2",
                                          valueInputOption="USER_ENTERED",
                                          body={'values': [[poke_num[index]]]}).execute()
                    await ctx.send(f"{ctx.author.name}: Gotcha! {currentPoke} was caught!")
            else:
                pokemon_list[index].append(currentPoke)
                poke_num[index] = poke_num[index] + 1
                catch_limit[index] = 4
                loc = chr(ord('c') + index)
                sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                      range="Sheet2!" + loc + str(len(pokemon_list[index]) + 2),
                                      valueInputOption="USER_ENTERED",
                                      body={'values': [[currentPoke]]}).execute()
                sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                      range="Sheet2!" + loc + "2",
                                      valueInputOption="USER_ENTERED",
                                      body={'values': [[poke_num[index]]]}).execute()
                await ctx.send(f"{ctx.author.name}: Gotcha! {currentPoke} was caught!")
        else:
            catch_limit[index] = catch_limit[index] + 1
            message = [f"{ctx.author.name}: Oh no! The pokemon broke free!",
                       f"{ctx.author.name}: Aww! It appeared to be caught",
                       f"{ctx.author.name}: Argh! Almost had it!",
                       f"{ctx.author.name}: Shoot, it was so close too!"]
            response = random.choice(message)
            await ctx.send(response)
    elif ctx.author.name in trainer_list and currentPoke in pokemon_list[index]:
        await ctx.send(f"{ctx.author.name}, you have already caught this pokemon.")
    elif ctx.author.name in trainer_list and catch_limit[index] >= 3 or (toc-tic) > 20:
        await ctx.send(f"Sorry, {ctx.author.name}, {currentPoke} already fled.")
    elif ctx.author.name in trainer_list and len(pokemon_list[index]) > 30:
        await ctx.send(f"{ctx.author.name}, you already have 30 Pokemon. "
                       f"Please release one if you wish to catch a new one.")
    else:
        await ctx.send(f"{ctx.author.name}, you are not a registered trainer. Please register with '!Register'")


@bot.command(name='MyPokemon', help="Shows list of your current Pokemon.")
async def list_poke(ctx):
    if ctx.author.name in trainer_list:
        index = trainer_list.index(ctx.author.name)
        p_list = str(pokemon_list[index])
        p_list = erase_extra_chars(p_list)
        await ctx.send(f"Here are {ctx.author.name}'s pokemon: " + p_list)
    else:
        await ctx.send(f"{ctx.author.name}, you are not a registered trainer. Please register with '!Register'")


@bot.command(name='PokeStats', help="Shows the list of all your Pokemon in your box.")
async def stats(ctx):
    index = trainer_list.index(ctx.author.name)
    j = 0
    while j < len(pokemon_list[index]):
        num = new_names.index("[\'" + str(pokemon_list[index][j]) + "\']")
        name = erase_extra_chars(str(names[num]))
        typ = erase_extra_chars(str(types[num]))
        health = erase_extra_chars(str(hp[num]))
        attack = erase_extra_chars(str(atk[num]))
        defend = erase_extra_chars(str(defense[num]))
        spd = erase_extra_chars(str(speed[num]))
        await ctx.send(name + " is a " + typ + " type, has " + health + " HP, " + attack + " attack, " + defend +
                       " defense, and " + spd + " speed.")
        j = j + 1


@bot.command(name='Release', help="You can release one of the Pokemon in your box. "
                                  "You are only allowed 30 Pokemon in your box at a time.")
async def release(ctx):
    index = trainer_list.index(ctx.author.name)
    await ctx.send(f"Which Pokemon do you want to release, {ctx.author.name}?")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    msg = await bot.wait_for("message", check=check)

    if msg.content in pokemon_list[index]:
        pokemon_list[index].remove(msg.content)
        poke_num[index] = poke_num[index] - 1
        loc = chr(ord('c') + index)
        sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                              range="Sheet2!" + loc + "2",
                              valueInputOption="USER_ENTERED",
                              body={'values': [[poke_num[index]]]}).execute()
        for i in range(len(pokemon_list[index])):
            sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                  range="Sheet2!" + loc + str(i+3),
                                  valueInputOption="USER_ENTERED",
                                  body={'values': [[pokemon_list[index][i]]]}).execute()
        sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                              range="Sheet2!" + loc + str(poke_num[index]+3),
                              valueInputOption="USER_ENTERED",
                              body={'values': [[""]]}).execute()
        await ctx.send(f"You released {msg.content}")
    else:
        await ctx.send("You do not have that Pokemon.")


@bot.command(name='Battle', help="Starts a battle between two players. "
                                 "Follow the instructions during the battle to play.")
async def start_b(ctx):
    global battle
    global trainer1
    global trainer2
    if not battle:
        index = trainer_list.index(ctx.author.name)
        trainer1 = str(ctx.author.name)
        trainer2 = ""
        team1 = []
        team2 = []
        good = False
        battle = True

        def check1(ms):
            return ms.author == ctx.author and ms.channel == ctx.channel

        def check2(ms):
            return ms.author.name == trainer2 and ms.channel == ctx.channel

        def check3(ms):
            return ms.author != ctx.author and ms.author.name in trainer_list and ms.channel == ctx.channel \
                   and ms.content in ["Me!"]

        await ctx.send(f"Who wants to battle {trainer1}? Reply with \"Me!\"")
        try:
            msg = await bot.wait_for("message", check=check3, timeout=120)
            trainer2 = msg.author.name
        except asyncio.TimeoutError:
            await ctx.send("Message not sent in time. Battle has been stopped.")
            battle = False
            return

        if battle:
            await ctx.send(f"{trainer1} vs {trainer2}!")
        index2 = trainer_list.index(trainer2)

        if battle:
            await ctx.send(f"{trainer1}, choose your team of six Pokemon. or type 'Done' to finish "
                           f"The order you pick them will be the order they battle in.")
        try:
            poke1 = await bot.wait_for("message", check=check1, timeout=120)
        except asyncio.TimeoutError:
            await ctx.send("Message not sent in time. Battle has been stopped.")
            battle = False
            return
        while battle and len(team1) < 6 and (poke1.content != "Done" or len(team1) == 0):
            if poke1.content in pokemon_list[index]:
                team1.append(poke1.content)
                await ctx.send(f"{poke1.content} has been selected.")
            else:
                await ctx.send("You do not have that Pokemon.")
            if len(team1) < 6:
                try:
                    poke1 = await bot.wait_for("message", check=check1, timeout=120)
                except asyncio.TimeoutError:
                    await ctx.send("Message not sent in time. Battle has been stopped.")
                    battle = False
                    return
        if battle:
            await ctx.send(f"{trainer2}, choose your team of six Pokemon or type 'Done' to finish "
                           f"(The order you pick them will be the order they battle in.")
        try:
            poke2 = await bot.wait_for("message", check=check2, timeout=120)
        except asyncio.TimeoutError:
            await ctx.send("Message not sent in time. Battle has been stopped.")
            battle = False
            return
        while battle and len(team2) < 6 and (poke2.content != "Done" or len(team2) == 0):
            if poke2.content in pokemon_list[index2]:
                team2.append(poke2.content)
                await ctx.send(f"{poke2.content} has been selected.")
            else:
                await ctx.send("You do not have that Pokemon.")
            if len(team2) < 6:
                try:
                    poke2 = await bot.wait_for("message", check=check2, timeout=120)
                except asyncio.TimeoutError:
                    await ctx.send("Message not sent in time. Battle has been stopped.")
                    battle = False
                    return

        p_num1 = 0
        p_num2 = 0
        new1 = True
        new2 = True
        charge1 = 0
        charge2 = 0
        hp1 = 0
        hp2 = 0
        while battle:
            num1 = new_names.index("[\'" + team1[0] + "\']")
            num2 = new_names.index("[\'" + team2[0] + "\']")
            if new1:
                hp1 = int(erase_extra_chars(str(hp[num1])))
                new1 = False
            if new2:
                hp2 = int(erase_extra_chars(str(hp[num2])))
                new2 = False
            atk1 = int(erase_extra_chars(str(atk[num1])))
            atk2 = int(erase_extra_chars(str(atk[num1])))
            def1 = int(erase_extra_chars(str(defense[num1])))
            def2 = int(erase_extra_chars(str(defense[num2])))
            spd1 = int(erase_extra_chars(str(speed[num1])))
            spd2 = int(erase_extra_chars(str(speed[num2])))

            display = display_battle(team1, team2, 0, 0)
            await ctx.send(display[0])
            await ctx.send(f"{display[1]}      HP: {hp1}/{erase_extra_chars(str(hp[num1]))}    Charge: {charge1}/5")
            await ctx.send(display[2])
            await ctx.send(f"{display[3]}      HP: {hp2}/{erase_extra_chars(str(hp[num2]))}    Charge: {charge2}/5")

# Input from trainer1 to attack, defend, or use charge attack
            await ctx.send(f"{trainer1}, type attack, defend, or charge in a spoiler message using ||.")
            go = await bot.wait_for("message", check=check1)
            while not good:
                if go.content.lower() == "||attack||" or go.content.lower() == "||defend||" \
                        or go.content.lower() == "||charge||":
                    good = True
                    if go.content.lower() == "||charge||" and charge1 < 5:
                        good = False
                        await ctx.send("Charge attack is not ready.")
                        await ctx.send(f"{trainer1}, type attack, defend, or charge in a spoiler message using ||.")
                        go = await bot.wait_for("message", check=check1)
                else:
                    await ctx.send(f"{trainer1}, type attack, defend, or charge in a spoiler message using ||.")
                    go = await bot.wait_for("message", check=check1)
            good = False
            if go.content.lower() == "||attack||":
                p_num1 = 1
            elif go.content.lower() == "||defend||":
                p_num1 = 2
            elif go.content.lower() == "||charge||":
                p_num1 = 3

# Input from trainer2 to attack, defend, or use charged attack
            await ctx.send(f"{trainer2}, type attack, defend, or charge in a spoiler message using ||.")
            go = await bot.wait_for("message", check=check2)
            while not good:
                if go.content.lower() == "||attack||" or go.content.lower() == "||defend||" \
                        or go.content.lower() == "||charge||":
                    good = True
                    if go.content.lower() == "||charge||" and charge2 < 5:
                        good = False
                        await ctx.send("Charge attack is not ready.")
                        await ctx.send(f"{trainer2}, type attack, defend, or charge in a spoiler message using ||.")
                        go = await bot.wait_for("message", check=check2)
                else:
                    await ctx.send(f"{trainer2}, type attack, defend, or charge in a spoiler message using ||.")
                    go = await bot.wait_for("message", check=check2)
            good = False
            if go.content.lower() == "||attack||":
                p_num2 = 1
            elif go.content.lower() == "||defend||":
                p_num2 = 2
            elif go.content.lower() == "||charge||":
                p_num2 = 3

            # If poke1 is faster
            if spd1 >= spd2:
                if p_num1 == 1:   # Poke1 attacks
                    if p_num2 == 2:
                        hp2 -= (atk1 // (def2 // 5))
                        await ctx.send(f"{team1[0]} attacked!")
                    else:
                        hp2 -= (atk1 // (def2 // 10))
                        await ctx.send(f"{team1[0]} attacked!")
                elif p_num1 == 3:
                    if p_num2 == 2:
                        hp2 -= (atk1 // (def2 // 5))
                        charge1 = -1
                        await ctx.send(f"{team1[0]} used a charged attack!")
                    else:
                        hp2 -= (atk1 // (def2 // 20))
                        charge1 = -1
                        await ctx.send(f"{team1[0]} used a charged attack!")
                elif p_num1 == 2:
                    await ctx.send(f"{team1[0]} defended!")
                if hp2 < 1:
                    new2 = True
                    charge2 = 0
                    await ctx.send(f"{team2[0]} fainted!")
                    team2.remove(team2[0])
                if not new2:
                    if p_num2 == 1:   # Poke2 attacks
                        if p_num1 == 2:
                            hp1 -= (atk2 // (def1 // 5))
                            await ctx.send(f"{team2[0]} attacked!")
                        else:
                            hp1 -= (atk2 // (def1 // 10))
                            await ctx.send(f"{team2[0]} attacked!")
                    elif p_num2 == 3:
                        if p_num1 == 2:
                            hp1 -= (atk2 // (def1 // 5))
                            charge2 = -1
                            await ctx.send(f"{team2[0]} used a charged attack!")
                        else:
                            hp1 -= (atk2 // (def1 // 20))
                            charge2 = -1
                            await ctx.send(f"{team2[0]} used a charged attack!")
                    elif p_num2 == 2:
                        await ctx.send(f"{team2[0]} defended!")
                    if hp1 < 1:
                        new1 = True
                        charge1 = 0
                        await ctx.send(f"{team1[0]} fainted!")
                        team1.remove(team1[0])
            else:  # If poke2 is faster
                if p_num2 == 1:  # Poke2 attacks
                    if p_num1 == 2:
                        hp1 -= (atk2 // (def1 // 5))
                        await ctx.send(f"{team2[0]} attacked!")
                    else:
                        hp1 -= (atk2 // (def1 // 10))
                        await ctx.send(f"{team2[0]} attacked!")
                elif p_num2 == 3:
                    if p_num1 == 2:
                        hp1 -= (atk2 // (def1 // 5))
                        charge2 = -1
                        await ctx.send(f"{team2[0]} used a charged attack!")
                    else:
                        hp1 -= (atk2 // (def1 // 20))
                        charge2 = -1
                        await ctx.send(f"{team2[0]} used a charged attack!")
                elif p_num2 == 2:
                    await ctx.send(f"{team2[0]} defended!")
                if hp1 < 1:
                    new1 = True
                    charge1 = 0
                    await ctx.send(f"{team1[0]} fainted!")
                    team1.remove(team1[0])
                if not new1:
                    if p_num1 == 1:  # Poke1 attacks
                        if p_num2 == 2:
                            hp2 -= (atk1 // (def2 // 5))
                            await ctx.send(f"{team1[0]} attacked!")
                        else:
                            hp2 -= (atk1 // (def2 // 10))
                            await ctx.send(f"{team1[0]} attacked!")
                    elif p_num1 == 3:
                        if p_num2 == 2:
                            hp2 -= (atk1 // (def2 // 5))
                            charge1 = -1
                            await ctx.send(f"{team1[0]} used a charged attack!")
                        else:
                            hp2 -= (atk1 // (def2 // 20))
                            charge1 = -1
                            await ctx.send(f"{team1[0]} used a charged attack!")
                    elif p_num1 == 2:
                        await ctx.send(f"{team1[0]} defended!")
                    if hp2 < 1:
                        new2 = True
                        charge2 = 0
                        await ctx.send(f"{team2[0]} fainted!")
                        team2.remove(team2[0])

            charge1 += 1
            charge2 += 1

# Determine if battle is over or draw
            if len(team1) < 1 and len(team2) < 1:
                await ctx.send("Wow, it's a draw!!!!!!!")
                battle = False
            elif len(team1) < 1:
                await ctx.send(f"{trainer2} is the winner!!!!!!!")
                trainer1 = ""
                trainer2 = ""
                battle = False
            elif len(team2) < 1:
                await ctx.send(f"{trainer1} is the winner!!!!!!!")
                trainer1 = ""
                trainer2 = ""
                battle = False


@bot.command(name='StopBattle', help="If there is a current battle, "
                                     "the trainers participating in the battle can stop it.")
async def stop(ctx):
    global battle
    global trainer1
    global trainer2
    if ctx.author.name == trainer1 or ctx.author.name == trainer2 and battle:
        battle = False
        await ctx.send("The battle has been stopped.")


@bot.command(name='Version', help="Shows current version of PokemonBot")
async def ver(ctx):
    await ctx.send("PokemonBot: Version 1.1.0")


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    channel = bot.get_channel(684500984114053253)
    await channel.send(f'{bot.user.name} has connected to Discord!')

bot.run(TOKEN)
