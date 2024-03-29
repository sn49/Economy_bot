# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import random
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import requests
import string
import math
import os.path
import asyncio
import sched
import datetime
import csv
import re
import shutil
import sys
import glob
from reinforce import doforce, sellforce, buyforce
from financial import givemoney, setluckypang, GetSumMoney, GetLuckypang
import reinforce
import financial
import seasonmanage
import time
import datamanage
import json
import datarecord
import traceback

datapath = "data/"
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="$$", intents=intents)

token = ""
version = "V1.4.9"
cancommand = True
canLotto = True
getnotice = False

testint = 1
testmode = False

tokenfile = open("token.json")

token = json.load(tokenfile)

tokenfile.close()

if testint == 0:
    testmode = False
else:
    testmode = True

Lottocool = 0
Lottomax = 3
maxlucky = 0
forceMsg = []
boxMsg = []

if testmode:
    giveMcool = 1
    Lottocool = 1
    version += " TEST"
    maxlucky = 7901
    Lottomax = 10
    token = token["test"]
else:
    giveMcool = 90
    Lottocool = 16
    Lottomax = 3
    token = token["main"]
    maxlucky = 10000000


getPercent = {
    "복권 1개": 35,
    "복권 3개": 26,
    "복권 5개": 16,
    "복권 7개": 10,
    "복권 10개": 6,
    "복권 20개": 3,
    "성공시 4렙업": 1,
    "파괴방지": 1.9,
    "강화비용면제": 1,
    "확정1업": 0.1,
}


seasoncheck = seasonmanage.seasoncheck()
ispreseason = False
ispreseason = seasoncheck["ispreseason"]


if not ispreseason:
    print(f"season{seasoncheck['currentseason']}")
    ispreseason = False
else:
    print(f"preseason{seasoncheck['currentseason']}-{seasoncheck['resetcount']}")
    ispreseason = True

lottoRange = 0


@bot.event
async def on_message(tempmessage):
    global getnotice

    if cancommand:
        await bot.process_commands(tempmessage)
    else:
        if tempmessage.author.id == 382938103435886592:
            await bot.process_commands(tempmessage)
        else:
            if str(tempmessage.content).startswith("$"):
                if not getnotice:
                    channel = bot.get_channel(771203131836989443)
                    await channel.send("현재 일시정지 상태입니다.")
                    getnotice = True
                else:
                    getnotice = False


@bot.event
async def on_ready():
    print("bot login test")
    print(bot.user.name)
    print(bot.user.id)
    print("-----------")
    await bot.change_presence(
        status=discord.Status.online, activity=discord.Game(f"{version} $도움말")
    )
    bot.loop.create_task(job())


async def job():
    iswriting = False
    isgiving = False
    if testmode:
        datapath = "testdata/"
        channel = bot.get_channel(709647685417697372)
    else:
        datapath = "data/"
        channel = bot.get_channel(771203131836989443)

    while True:
        currentTime = datetime.datetime.now()
        hour = currentTime.hour
        minute = currentTime.minute
        second = currentTime.second

        if hour == 1 and second >= 0 and second < 10 and minute == 0:
            forceSale = {}
            with open(f"{datapath}forcestore.json", "r") as forceFile:
                forceSale = json.load(forceFile)

            if forceSale["1"] < 100:
                forceSale["1"] = 100
                with open(f"{datapath}forcestore.json", "w") as forceFile:
                    json.dump(forceSale, forceFile)
                await channel.send("의문의 물건 +1의 남은 개수가 100개가 되었습니다.")

            with open(f"{datapath}advforcestore.json", "r") as forceFile:
                forceSale = json.load(forceFile)

            if forceSale["1"] < 20:
                forceSale["1"] = 20
                with open(f"{datapath}advforcestore.json", "w") as forceFile:
                    json.dump(forceSale, forceFile)
                await channel.send("고오급 의문의 물건 +1의 남은 개수가 20개가 되었습니다.")
        elif (
            (hour % 12 == 5 or hour % 12 == 11)
            and minute == 0
            and second >= 0
            and second < 10
        ):
            if not isgiving:
                userlist = financial.GetInfo(channel)
                minlist = []
                maxlist = []
                minimum = 0
                maximum = 0
                index = 0
                for key, value in userlist.items():
                    if index == 0:
                        minimum = int(value)
                        maximum = int(value)
                        minlist.append([key, value])
                        maxlist.append([key, value])
                    else:
                        if int(value) > maximum:
                            maximum = int(value)
                            maxlist.clear()
                            maxlist.append([key, value])
                        elif int(value) == maximum:
                            maxlist.append([key, value])
                        elif int(value) < minimum:
                            minimum = int(value)
                            minlist.clear()
                            minlist.append([key, value])
                        elif int(value) == minimum:
                            minlist.append([key, value])
                    index += 1

                maxstack = 0
                for user in maxlist:
                    tempstack = -math.floor(user[1] * 0.1)
                    givemoney(channel, user[0], tempstack)
                    maxstack -= tempstack

                remain = len(minlist)

                for user in minlist:
                    print(maxstack)
                    if remain != 1:
                        willgive = math.floor(maxstack / remain)
                        maxstack = willgive
                        givemoney(channel, user[0], willgive)
                    else:
                        givemoney(channel, user[0], maxstack)
                    remain -= 1
                    print(maxstack)
                    if remain == 0:
                        break
                await channel.send("자산 분배가 완료되었습니다.")
            else:
                return

        await asyncio.sleep(10)


@bot.event
async def on_reaction_add(reaction, user):
    global forceMsg
    global boxMsg
    global maxlucky
    global ispreseason
    global advanceForceMsg
    if user.bot:
        return

    if reaction.message.id in boxMsg:
        if user.display_name == reaction.message.content:
            if (
                str(reaction.emoji) == "🎁"
                or str(reaction.emoji) == "❌"
                or str(reaction.emoji) == "👜"
            ):
                await reaction.message.delete()

            if str(reaction.emoji) == "🎁":
                await BuyBox(reaction.message, user)
                boxMsg.remove(reaction.message.id)
            elif str(reaction.emoji) == "❌":
                boxMsg.remove(reaction.message.id)
            elif str(reaction.emoji) == "👜":
                await CheckItem(reaction.message, user)
                boxMsg.remove(reaction.message.id)

    elif reaction.message.id in forceMsg:
        if user.display_name == reaction.message.content:
            if (
                str(reaction.emoji) == "🔥"
                or str(reaction.emoji) == "😀"
                or str(reaction.emoji) == "🔨"
                or str(reaction.emoji) == "🛡️"
                or str(reaction.emoji) == "⏩"
                or str(reaction.emoji) == "⭐"  
            ):
                await reaction.message.delete()

            if str(reaction.emoji) == "🔨":
                await doforce(
                    reaction.message, user, 1, ispreseason, maxlucky, datapath=datapath
                )
                forceMsg.remove(reaction.message.id)
            elif str(reaction.emoji) == "😀":
                checkpre = await sellforce(reaction.message, user)
                forceMsg.remove(reaction.message.id)

                if checkpre:
                    SeasonChange(checkpre, reaction.message.channel)
            elif str(reaction.emoji) == "🔥":
                await doforce(
                    reaction.message, user, 3, ispreseason, maxlucky, datapath=datapath
                )
                forceMsg.remove(reaction.message.id)
            elif str(reaction.emoji) == "🛡️":
                await doforce(
                    reaction.message, user, 2, ispreseason, maxlucky, datapath=datapath
                )
                forceMsg.remove(reaction.message.id)
            elif str(reaction.emoji) == "⏩":
                await doforce(
                    reaction.message, user, 4, ispreseason, maxlucky, datapath=datapath
                )
                forceMsg.remove(reaction.message.id)
            elif str(reaction.emoji) == "⭐":
                await doforce(
                    reaction.message, user, 5, ispreseason, maxlucky, datapath=datapath
                )
                forceMsg.remove(reaction.message.id)

    elif reaction.message.id in advanceForceMsg:
        if user.display_name == reaction.message.content:
            if str(reaction.emoji) == "😀" or str(reaction.emoji) == "🔨":
                await reaction.message.delete()
            if str(reaction.emoji) == "🔨":
                await doforce(
                    reaction.message,
                    user,
                    1,
                    ispreseason,
                    maxlucky,
                    False,
                    True,
                    datapath=datapath,
                )
                advanceForceMsg.remove(reaction.message.id)
            elif str(reaction.emoji) == "😀":
                checkpre = await reinforce.sellforce(
                    reaction.message, user, True, datapath=datapath
                )
                advanceForceMsg.remove(reaction.message.id)
                if checkpre:
                    SeasonChange(checkpre, reaction.message.channel)


@commands.cooldown(1, 2, commands.BucketType.default)
@bot.command()
async def 가입(ctx, nickname=None):

    blackfile = open("blackword.txt", "r", encoding="UTF-8")
    blacklist = blackfile.readlines()
    print(blacklist)
    if nickname == None:
        await ctx.send("닉네임을 입력해주세요.")
        return

    if len(nickname) > 10:
        await ctx.send("10글자를 넘을 수 없습니다.")
        return

    intfind = re.findall(r"\d", nickname)
    if len(intfind) > 4:
        await ctx.send("숫자는 4개까지 넣을수있습니다.")
        return

    for blackword in blacklist:
        if blackword in nickname:
            await ctx.send("사용할수 없는 단어가 포함되어 있습니다.")
            return

    if not os.path.isdir(f"{datapath}{ctx.guild.id}"):
        os.mkdir(f"{datapath}{ctx.guild.id}")
        forcedata = {"1": 100}

        with open(f"{datapath}{ctx.guild.id}/forcestore.json", "w") as f:
            json.dump(forcedata, f)

        with open(f"{datapath}{ctx.guild.id}/advforcestore.json", "w") as f:
            json.dump(forcedata, f)

    if os.path.isfile(f"{datapath}{ctx.guild.id}/{ctx.author.id}.json"):
        await ctx.send("이미 가입하였습니다.")
        return
    else:
        string_pool = string.ascii_letters + string.digits
        result1 = ""
        for i in range(5):
            result1 = result1 + random.choice(string_pool)

        firstData = {
            "nickname": f"{nickname}#{result1}",
            "money": 50000,
            "unknownLevel": 0,
        }

        f = open(f"{datapath}{ctx.guild.id}/{ctx.author.id}.json", "w")
        json.dump(firstData, f)

    await ctx.send("가입 성공!")


@bot.command()
async def 자산(ctx, userid=None):
    userData = None

    if userid == None:
        userData = datamanage.GetUserData(ctx)

    else:
        userData = datamanage.GetUserData(ctx, userid)

    if userData == None:
        await ctx.send(f"존재하지 않는 유저입니다.")
        return

    await ctx.send(f"{userData['nickname']}의 자산은 {userData['money']}모아입니다.")


def get_chance_multiple(mode):
    chance = 0
    multiple = 0
    if mode == 1:
        chance = 80
        multiple = 1.2
    elif mode == 2:
        chance = 64
        multiple = 1.6
    elif mode == 3:
        chance = 48
        multiple = 2.2
    elif mode == 4:
        chance = 32
        multiple = 3
    elif mode == 5:
        chance = 16
        multiple = 4
    elif mode == 6:
        chance = 45
        multiple = 2
    elif mode == 7:
        chance = 50
        multiple = 3

    return chance, multiple


@bot.command()
async def 버전(ctx):
    await ctx.send(f"모아봇 버전 : {version}")


@bot.command()
async def 시즌(ctx):
    if not ispreseason:
        await ctx.send(f"season{seasoncheck['currentseason']}")
    else:
        await ctx.send(
            f"preseason{seasoncheck['currentseason']}-{seasoncheck['resetcount']}"
        )


@commands.cooldown(1, 2, commands.BucketType.default)
@bot.command()
async def 베팅(ctx, mode=None, moa=10000):
    global maxlucky
    try:
        bonusback = 0
        success = True
        userinfo = datamanage.GetUserData(ctx)
        money = userinfo["money"]
        nickname = userinfo["nickname"]

        if money <= 0:
            raise Exception("베팅할 돈이 없습니다.")
        if mode == None:
            raise Exception("모드를 입력해주세요.")

        if int(mode) == 6 or int(mode) == 7:
            if moa == 10000:
                moa = math.floor(money * 0.5 * (int(mode) - 5))
            else:
                await ctx.send("베팅 6,7은 금액 입력을 할 수 없습니다. 6-절반 7-올인")
                return

        if money < int(moa) or int(moa) < 0:
            raise Exception("보유량보다 많거나 0원 미만으로 베팅하실 수 없습니다.")
        if int(mode) > 7 or int(mode) < 1:
            raise Exception("모드를 잘못 입력했습니다.")
    except Exception as e:
        await ctx.send(
            f"{e}\n$베팅 (모드) (모아)\n(모드 종류 : 1 80% 1.2배, 2 64% 1.6배, 3 48% 2.2배, 4 32% 3배, 5 16% 4배, 6 60% 2배(올인만 가능)"
        )
        return
    chance, multiple = get_chance_multiple(int(mode))
    result = random.randrange(0, 100)
    lose = int(moa)
    profit = 0
    if result < chance:
        profit = math.floor(multiple * int(moa))
        await ctx.send(f"{nickname} 베팅 성공!")
        success = True
    else:
        await ctx.send(f"{nickname} 베팅 실패!")
        save2 = random.randrange(0, 100)
        success = False
        if save2 < 10:
            bonusback = math.floor(lose * 0.3)
            await ctx.send("건 돈의 30% 지급")

    givemoney(ctx, nickname, profit - lose + bonusback)

    if not success:
        await setluckypang(math.floor(int(moa) * 0.1), ctx, maxlucky, datapath)


@bot.command()
async def 모두(ctx):
    try:
        userlist = datamanage.GetAllUserData(ctx)

        sumMoney = 0

        for key in userlist.keys():
            sumMoney += userlist[key]["money"]

        showtext = "```"

        for key in userlist.keys():
            rank = 1
            for otherkey in userlist.keys():
                if userlist[key]["money"] < userlist[otherkey]["money"]:
                    rank += 1
            showtext += f"{userlist[key]['nickname']} {userlist[key]['money']} {'%.2f'%(userlist[key]['money']/sumMoney*100)}%({rank}위)\n"
        showtext += "```"
        await ctx.send(showtext)

    except Exception as e:
        await ctx.send(f"{e}\n가입한 사람이 없습니다.")
        traceback.print_exc()


@bot.command()
@commands.cooldown(1, 10, commands.BucketType.default)
async def 일시정지(ctx, reason=None):
    global cancommand
    if ctx.author.id == 382938103435886592:
        cancommand = not cancommand
        if cancommand:
            await ctx.send("명령어 사용이 가능합니다.")
        else:
            await ctx.send(f"명령어 사용이 불가능합니다. 이유: {reason}")


# region 복권
@commands.cooldown(1, Lottocool, commands.BucketType.user)
@bot.command()
async def 복권(ctx, amount=1):
    global canLotto
    try:
        if not canLotto:
            await ctx.send("마감되었습니다.")
            return
        amount = int(amount)
        await BuyLotto(ctx, amount, False)
    except Exception as e:
        await ctx.send(f"복권 (수량)\n{e}")


async def CheckLotto(filename, ctx):
    global canLotto
    global Lottocool

    if ispreseason:
        lottoRange = 8
    else:
        lottoRange = 10

    file = open(filename, "r")
    lines = file.readlines()
    await ctx.send(f"{len(lines)}/{Lottocool}")
    showtext = "```"
    if len(lines) >= Lottocool:
        canLotto = False
        result = [0, 0, 0, 0]
        special = 0
        totalSell = float(len(lines) * 1000)
        i = 0

        # region 로또 추첨
        while i < 4:
            num = random.randint(1, lottoRange)
            if not num in result:
                result[i] = num
                i += 1
        result.sort()
        special = random.choice(result)
        # endregion

        showtext += (
            f"당첨 번호 : {result[0]},{result[1]},{result[2]},{result[3]},{special}\n"
        )
        for line in lines:
            nickname = ""
            submit = line.split(",")
            i = 0
            correct = 0
            place = 0
            getprice = 0
            while i < 4:
                if int(submit[i]) in result:
                    correct += 1
                i += 1
            if correct > 0:
                if correct == 4:
                    if special == int(submit[4]):
                        place = 1
                        getprice = 5000000
                    else:
                        place = 2
                        getprice = 1000000
                elif correct == 3:
                    place = 3
                    getprice = 100000
                elif correct == 2:
                    place = 4
                    getprice = 20000

            userfile = open(f"{datapath}user_info{ctx.guild.id}", "r")
            userdata = userfile.readlines()
            file.close()
            for sub in userdata:
                cuser = sub.split(",")
                if submit[5] == cuser[2]:
                    nickname = cuser[1]
                    givemoney(ctx, nickname, getprice)

            if place != 0:
                showtext += f"{nickname} {place}등 당첨! {getprice}모아 지급! [{submit[0]},{submit[1]},{submit[2]},{submit[3]},{submit[4]}]\n"
        showtext += "```"
        await ctx.send(showtext)
        os.remove(filename)
        canLotto = True
        Lottocool = random.randint(10, 30)


@commands.cooldown(1, 0.5, commands.BucketType.default)
@bot.command()
async def 복권확인(ctx):
    showtext = "```"
    file = open(f"lotto_{ctx.guild.id}", "r")
    lines = file.readlines()
    for line in lines:
        user = line.split(",")
        if user[4] == str(ctx.author.id):
            showtext += f"{user[0]},{user[1]},{user[2]},{user[3]}\n"
    showtext += "```"
    await ctx.send(showtext)


async def BuyLotto(ctx, amount, FromBox=False):

    global Lottomax
    global lottoRange
    lottoPrice = 10000 * amount
    if ispreseason:
        lottoRange = 8
    else:
        lottoRange = 10
    showtext = "```"
    nickname = ""
    filename = f"{datapath}{ctx.guild.id}/{ctx.author.id}.json"
    userData = None

    if int(amount) > Lottomax and not FromBox:
        await ctx.send(f"한번에 {Lottomax}개까지 구매 가능합니다.")
        return

    if not os.path.isfile(filename):
        await ctx.send("가입을 해주세요.")
        return

    with open(filename) as f:
        userData = json.load(f)

    nickname = userData["nickname"]
    money = userData["money"]

    if not FromBox:
        if money < lottoPrice:
            await ctx.send(f"복권을 살 돈이 부족합니다.({lottoPrice}모아)")
            return
        else:
            givemoney(ctx, nickname, -lottoPrice)
    writetext = ""

    for num in range(amount):
        i = 0
        number = [0, 0, 0, 0]
        num = 0

        while i < 4:
            num = random.randint(1, lottoRange)
            if not num in number:
                number[i] = num
                i += 1
        number.sort()
        number.append(random.choice(number))
        showtext += nickname + "   " + str(number) + "\n"

        for num in number:
            writetext += str(num) + ","
        writetext += str(ctx.author.id) + ",\n"
    f = open(f"lotto_{ctx.guild.id}", "a")
    f.write(writetext)
    f.close()

    showtext += "```"
    await ctx.send(showtext)
    await CheckLotto(f"lotto_{ctx.guild.id}", ctx)


# endregion


@commands.cooldown(1, 2, commands.BucketType.default)
@bot.command()
async def 기부(ctx, userid=None, moa=None):
    try:
        if userid == None or not userid.isdigit():
            raise Exception("기부할 유저의 id를 입력해주세요.")

        if moa == None:
            raise Exception("모아를 입력해주세요.")

        if int(moa) <= 0:
            raise Exception("0원이하로 기부할수 없습니다.")

        # 파일 읽어서 기부하는 사람의 닉네임, 기부받는 사람의 닉네임 받아들이기
        giveuserInfo = json.load(f"data/{ctx.guild.id}/{ctx.author.id}.json")
        receiveuserInfo = json.load(f"data/{ctx.guild.id}/{userid}.json")

        if giveuserInfo["money"] < int(moa):
            raise Exception("자신 보유 자산보다 많이 기부할수 없습니다.")

        # 기부 하는 사람이랑 기부 받는 사람이랑 닉네임 같으면 기부불가
        if ctx.author.id == int(userid):
            raise Exception("자신에게 기부할수 없습니다.")

        givemoney(ctx, giveuserInfo["nickname"], -int(moa))
        givemoney(ctx, receiveuserInfo["nickname"], int(moa))

        # 기부 완료 메세지 보내기
        await ctx.send(
            f"{giveuserInfo['nickname']}, {receiveuserInfo['nickname']}에게 {moa}모아 기부완료"
        )

    except Exception as e:
        await ctx.send(f"{e}\n$기부 (닉네임) (기부할 돈)")
        return


@commands.cooldown(1, 2, commands.BucketType.default)
@bot.command()
async def 도움말(ctx, keyword=None):
    await ctx.send("https://www.notion.so/7843d4b09b0d4854ba977b8e0ba682eb")


@commands.cooldown(1, 2, commands.BucketType.default)
@bot.command()
async def 경제규모(ctx, mode=None, moa=None):
    sum_money, countUser = GetSumMoney(ctx)

    sendtext = f"총 경제규모 : {sum_money}모아\n1인당 경제규모 : {'%.3f'%(sum_money/countUser)}모아"
    await ctx.send(sendtext)


@bot.command()
async def 닉네임(ctx):
    file = open(f"user_info{ctx.guild.id}", "r")
    lines = file.readlines()
    file.close()
    nickname = ""
    for line in lines:
        user = line.split(",")
        if int(user[2]) == ctx.author.id:
            nickname = user[1]
    await ctx.send(f"{ctx.author.display_name}의 닉네임은 {nickname}입니다.")


advanceForceMsg = []


@bot.command()
async def 고급강화(ctx, level=None):
    if not level:
        global advanceForceMsg
        embed = discord.Embed(title="고급 강화", description="시즌을 끝내는 새로운 방법?")
        embed.add_field(name="강화 :hammer:", value="강화를 합니다.")
        embed.add_field(name="판매 :grinning:", value="판매를 합니다.")
        msg = await ctx.send(embed=embed, content=ctx.author.display_name)
        advanceForceMsg.append(msg.id)
        emojilist = ["🔨", "😀"]
        for emoji in emojilist:
            if msg:
                await msg.add_reaction(emoji)
        return
    else:
        level = int(level)
        if level < 1 or level > 12:
            await ctx.send("1~12강 확률을 볼 수 있습니다.")
        else:
            rein = reinforce
            need = rein.get_need(level, True)
            fail = rein.get_fail(level, True)
            destroy = rein.GetDestroy(level, ispreseason, True)
            success = rein.GetSuccess(level, True)
            criSuccess = rein.GetCriSuccess(level, True)
            notChange = 100 - fail - destroy - success - criSuccess
            await ctx.send(
                f"크리티컬 성공 확률 : {'%.2f'%criSuccess}%\n성공 확률 : {'%.2f'%success}%\n유지 확률 : {'%.2f'%notChange}%\n단계 하락 확률 : {'%.2f'%fail}%\n파괴 확률 : {'%.2f'%destroy}%\n비용 : {need}모아"
            )


@bot.command()
async def 강화(ctx, level=None):
    if not level:
        global forceMsg
        embed = discord.Embed(title="강화", description="36강을 판매하면 현재 시즌 종료")
        embed.add_field(name="강화 :hammer:", value="강화를 합니다.")
        embed.add_field(name="판매 :grinning:", value="판매를 합니다.")
        embed.add_field(name="강화x3 :fire:", value="강화를 3번 합니다.")
        embed.add_field(name="파괴방지 강화 :shield:", value="파괴방지 후 강화를 합니다.(비용 1.1배)")
        embed.add_field(
            name="4렙업 :fast_forward:", value="성공시 4렙, 크리티컬 성공시 6렙을 올립니다.(비용 3배)"
        )
        embed.add_field(
            name="95%로 강화 :star:",
            value="95% 확률로 업그레이드에 성공합니다. 단,5% 확률로 파괴될 수 있습니다.(비용 10배)",
        )
        msg = await ctx.send(embed=embed, content=ctx.author.display_name)
        forceMsg.append(msg.id)
        emojilist = ["🔨", "😀", "🔥", "🛡️", "⏩", "⭐"]
        for emoji in emojilist:
            if msg:
                await msg.add_reaction(emoji)
        return
    else:
        level = int(level)
        if level < 1 or level > 35:
            await ctx.send("1~35강 확률을 볼 수 있습니다.")
        else:
            rein = reinforce
            need = rein.get_need(level)
            fail = rein.get_fail(level)
            destroy = rein.GetDestroy(level, ispreseason)
            success = rein.GetSuccess(level)
            criSuccess = rein.GetCriSuccess(level)
            notChange = 100 - fail - destroy - success - criSuccess
            await ctx.send(
                f"크리티컬 성공 확률 : {'%.2f'%criSuccess}%\n성공 확률 : {'%.2f'%success}%\n유지 확률 : {'%.2f'%notChange}%\n단계 하락 확률 : {'%.2f'%fail}%\n파괴 확률 : {'%.2f'%destroy}%\n비용 : {need}모아"
            )


@bot.command()
async def 상자구매(ctx):
    global boxMsg
    embed = discord.Embed(title="상자구매", description="")
    embed.add_field(name="강화 관련 아이템 랜덤 박스 :gift:", value="6000모아")
    embed.add_field(name="구매 안함 :x:", value="구매를 하지 않습니다.")
    embed.add_field(name="보유 확인 :handbag:", value="보유 현황을 확인합니다.")
    msg = await ctx.send(embed=embed, content=ctx.author.display_name)
    boxMsg.append(msg.id)
    await msg.add_reaction("🎁")
    await msg.add_reaction("❌")
    await msg.add_reaction("👜")
    return


@bot.command()
async def 한강(ctx):
    file = open("hanriver.txt", "r", encoding="utf-8")
    text = file.read()

    url = "https://hangang.life/"
    result = requests.get(url=url)
    bs_obj = BeautifulSoup(result.content, "html.parser")
    lf_items = str(bs_obj.find("h1", {"class": "white"}))
    lf_items = re.sub("<.+?>", "", lf_items, 0)
    lf_items = re.sub("\n", "", lf_items, 0)
    print(lf_items)

    await ctx.send(text + f"\n\n\n현재 한강 수온{lf_items}```")


@commands.cooldown(1, giveMcool, commands.BucketType.user)
@bot.command()
async def 구걸(ctx):
    filename = f"{datapath}{ctx.guild.id}/{ctx.author.id}.json"

    if not os.path.isfile(filename):
        await ctx.send("가입을 해주세요.")
        return
    userData = {}
    with open(filename, "r") as f:
        userData = json.load(f)

    nickname = userData["nickname"]
    money = userData["money"]

    if money > 0:
        await ctx.send("0모아를 가지고 있어야 구걸할수 있습니다.")
        구걸.reset_cooldown(ctx)
        return

    getmoa = financial.GetBeggingMoa()

    if ispreseason:
        getmoa *= 3

    givemoney(ctx, nickname, getmoa)

    await ctx.send(f"'{nickname}', {getmoa}모아 획득!")


@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command()
async def 자산이전(ctx, nickname1, nickname2, moa):
    if ctx.author.id != 382938103435886592:
        await ctx.send("제작자 전용 명령어입니다.")
        return

    check = []
    moa = int(moa)
    check.append(givemoney(ctx, nickname1, moa))
    check.append(givemoney(ctx, nickname2, moa))

    if 0 in check:
        await ctx.send("존재하지 않는 유저입니다.")
        return

    await ctx.send(f"{nickname1}의 {moa}모아를 {nickname2}에게 이전 완료")


@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command()
async def 강화구매(ctx, level=None):
    await buyforce(ctx, level)


@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command()
async def 고급강화구매(ctx, level=None):
    await buyforce(ctx, level, True)


async def BuyBox(message, reuser):
    haveitem = {}
    ctx = message.channel

    print(sum(getPercent.values()))

    if sum(getPercent.values()) != 100:
        return

    get = ""
    count = 1
    writetext = ""

    if os.path.isfile(f"forceitem{reuser.id}"):
        file = open(f"forceitem{reuser.id}", "r")
        lines = file.readlines()
        for line in lines:
            have = line.split(":")
            haveitem[have[0]] = int(have[1])
            print(haveitem)
    else:
        file = open(f"forceitem{reuser.id}", "w")
        file.close()

    # region 반복 구간 시작

    for i in range(count):
        file = open(f"user_info{message.guild.id}", "r")
        lines = file.readlines()
        file.close()
        userindex = 0

        index = 0
        for user in lines:
            user_info = user.split(",")
            if user_info[2] == str(reuser.id):
                moa = int(user_info[3])
                nickname = user_info[1]
                userindex = index
            index += 1

        need = 40000

        if need > moa:
            await ctx.send(f"{need-moa}모아가 부족합니다.")
            break
        else:
            lines[userindex] = lines[userindex].replace(
                f"{reuser.id},{'%010d'%moa}", f"{reuser.id},{'%010d'%(moa-need)}"
            )
            writetext += ""
            for line in lines:
                writetext += line
            file = open(f"user_info{message.guild.id}", "w")
            file.write(writetext)
            file.close()

        result = random.random() * 100

        print(result)

        cut = 0
        keys = getPercent.keys()
        print(get)
        print(keys)
        for percentkey in keys:
            cut += getPercent[percentkey]

            if result < cut:
                get = percentkey
                break

        if get in haveitem.keys():
            # 보유정보 +1하기
            haveitem[get] += 1
        else:
            # 보유정보 1로 추가
            haveitem[get] = 1

        writetext = ""
        for key, value in haveitem.items():
            writetext += f"{key}:{value}:\n"
            print(writetext)

        file = open(f"forceitem{reuser.id}", "w")
        file.write(writetext)
        file.close()

        await ctx.send(f"{nickname}, '{get}'획득!")
        await setluckypang(need, ctx, maxlucky, datapath)
    # endregion


async def CheckItem(message, reuser):
    file = open(f"forceitem{reuser.id}", "r")
    file_text = file.read()
    file.close()
    writetext = "```"
    writetext += file_text
    writetext += "```"
    if writetext == "``````":
        writetext = "보유중인 아이템이 없습니다."
    await message.channel.send(writetext)


@commands.cooldown(1, 2, commands.BucketType.default)
@bot.command()
async def 아이템사용(ctx, itemname=None):
    if itemname == None:
        await ctx.send("사용할 아이템 이름을 입력해주세요.")
        return

    itemlist = getPercent.keys()
    itemhave = {}
    itemfile = open(f"forceitem{ctx.author.id}", "r")
    itemlines = itemfile.readlines()
    itemfile.close()

    useitem = ""
    gethave = 0
    for line in itemlines:
        info = line.split(":")
        itemhave[info[0]] = int(info[1])

    if itemname in itemlist:
        useitem = itemname
        if itemname in itemhave.keys():
            itemhave[itemname] -= 1
        else:
            await ctx.send("가지고 있지 않는 아이템입니다.")
    else:
        await ctx.send("아이템 이름을 잘못입력했습니다.")
        return

    if itemhave[itemname] <= 0:
        itemhave.pop(itemname)
        print(itemhave)

    writetext = ""
    for key, value in itemhave.items():
        writetext += f"{key}:{value}:\n"
    itemfile = open(f"forceitem{ctx.author.id}", "w")
    itemfile.write(writetext)
    itemfile.close()

    if str(useitem).startswith("복권"):
        intfind = re.findall("\d+", useitem)
        await BuyLotto(ctx, int(intfind[0]), True)
        itemfile.close()
        return
    elif str(useitem) == "성공시 4렙업":
        await doforce(ctx, ctx.author, 4, ispreseason, maxlucky, True)
    else:
        await ctx.send("아이템 사용은 복권 교환권과 '성공시 4렙업'만 가능합니다.")


@commands.cooldown(1, 2, commands.BucketType.default)
@bot.command()
async def 아이템구매(ctx, itemno=None):
    itemhave = {}
    writetext = ""
    # 상자 구매 이력이 없으면 파일 생성
    if not os.path.isfile(f"forceitem{ctx.author.id}"):
        file = open(f"forceitem{ctx.author.id}", "w")
        file.close()
    else:
        file = open(f"forceitem{ctx.author.id}", "r")
        fileline = file.readlines()
        for line in fileline:
            info = line.split(":")
            itemhave[info[0]] = int(info[1])

    showtext = "```"
    tradefile = open("trade.csv", "r")
    filetextline = tradefile.readlines()
    tradefile.close()
    i = 0
    for line in filetextline:
        i += 1
        info = line.split(",")
        showtext += f"{i} : {info[0]},{info[1]}\n"

    showtext += "```"
    if itemno == None:
        await ctx.send(showtext)
    else:
        if int(itemno) < len(filetextline) + 1:
            # filetextline[int(itemno)-1]을 split해서 정보 가져오기
            realinfo = filetextline[int(itemno) - 1].split(",")
            buyitem = realinfo[0]
            buyprice = int(realinfo[1])
            owner = realinfo[2]
            ownerhavingmoney = 0
            ownernick = ""

            buyindex = 0
            sellindex = 0

            # userfile 오픈후 readline으로 정보 가져옴
            userfile = open(f"user_info{ctx.guild.id}", "r")
            userfilelines = userfile.readlines()
            userfile.close()

            havingmoney = 0
            i = 0
            # readline으로 가져온 걸로 for문을 돌려 구매자 닉네임과 보유금액, 판매자 닉네임 가져오기
            for user in userfilelines:
                userinfo = user.split(",")
                if userinfo[2] == str(ctx.author.id):
                    havingmoney = int(userinfo[3])
                    buyindex = i
                elif userinfo[2] == owner:
                    ownernick = userinfo[1]
                    sellindex = i
                    ownerhavingmoney = int(userinfo[3])

                i += 1

            if owner == str(ctx.author.id):
                await ctx.send("자신이 판매한 물건은 구매할 수 없습니다.")
                return

            # 살 돈이 있다면 구매자의 돈을 빼고 그 돈의 10%를 제외한 돈을 판매자에게 지급
            if havingmoney >= buyprice:
                userfilelines[buyindex] = userfilelines[buyindex].replace(
                    f"{ctx.author.id},{'%010d'%havingmoney}",
                    f"{ctx.author.id},{'%010d'%(havingmoney-buyprice)}",
                )
                userfilelines[sellindex] = userfilelines[sellindex].replace(
                    f"{owner},{'%010d'%ownerhavingmoney}",
                    f"{owner},{'%010d'%(ownerhavingmoney+math.floor(buyprice*0.9))}",
                )
            else:
                await ctx.send(f"{buyprice-havingmoney}모아가 부족합니다.")
                return

            writetext = ""
            for line in userfilelines:
                writetext += line
            userfile = open(f"user_info{ctx.guild.id}", "w")
            userfile.write(writetext)
            userfile.close()

            for line in filetextline:
                writetext += line

            # userfile 오픈후 파일쓰기
            userfile = open(f"trade.csv", "w")
            userfile.write(writetext)
            userfile.close()

            # 구매자 아이템 보유 정보 수정
            itemhave[buyitem] += 1
            writetext = ""
            for key, value in itemhave.items():
                writetext += f"{key}:{value}:\n"
                print(writetext)

            file = open(f"forceitem{ctx.author.id}", "w")
            file.write(writetext)
            file.close()

            # 거래시장 csv 수정
            filetextline.pop(int(itemno) - 1)

            writetext = ""
            print(filetextline)
            for line in filetextline:
                if line != "":
                    writetext += line

            tradefile = open("trade.csv", "w", newline="")
            tradefile.write(writetext)
            tradefile.close()

            # 구매, 판매 완료 보내기
            await ctx.send(f"{ownernick}의 {buyitem}을 {buyprice}모아에 구매 완료")

        else:
            return


@commands.cooldown(1, 2, commands.BucketType.default)
@bot.command()
async def 아이템판매(ctx, itemname=None, price=None):
    try:
        if itemname == None:
            raise Exception("아이템 이름을 입력해주세요.")

        if price == None:
            raise Exception("팔 가격을 입력해주세요.")

        itemlist = []
        itemhave = {}
        itemfile = open(f"forceitem{ctx.author.id}", "r")
        itemlines = itemfile.readlines()
        itemfile.close()

        for line in itemlines:
            info = line.split(":")
            itemhave[info[0]] = int(info[1])
            itemlist.append(info[0])

        if itemname in itemhave.keys():
            itemhave[itemname] -= 1
            print(itemhave)
            if itemhave[itemname] <= 0:
                itemhave.pop(itemname)
                print(itemhave)

        else:
            await ctx.send(f"'{itemname}' 보유하지 않음")
            return

        writetext = ""
        for key, value in itemhave.items():
            writetext += f"{key}:{value}:\n"

        itemfile = open(f"forceitem{ctx.author.id}", "w")
        itemfile.write(writetext)
        itemfile.close()

        if itemname in itemlist:
            tradefile = open("trade.csv", "at", newline="")
            writer = csv.writer(tradefile)

            writer.writerow([itemname, int(price), ctx.author.id, None])
            tradefile.close()
            await ctx.send(f"{itemname} 아이템이 {price}모아에 올려짐")
        else:
            await ctx.send("존재하지 않는 아이템입니다.")
            return
    except Exception as e:
        await ctx.send(f"{e}\n$아이템판매 '(아이템 이름)' (판매 가격)")


@bot.command()
async def 운영자지급(ctx, nickname, moa):
    if ctx.author.id != 382938103435886592:
        await ctx.send("권한이 없습니다.")
        return

    check = givemoney(ctx, nickname, moa)

    if check == 0:
        await ctx.send("존재하지 않는 유저입니다.")
        return

    await ctx.send(f"{nickname}에게 {moa}모아 지급 완료")


@bot.command()
async def 럭키팡(ctx):
    global maxlucky
    await GetLuckypang(ctx, maxlucky)


@bot.command()
async def 데이터리셋(ctx, seasoncheck, check=-7000):
    checkpreseason = None
    if ctx.author.id != 382938103435886592:
        await ctx.send("권한이 없습니다.")
        return

    if seasoncheck == "preseason":
        checkpreseason = True
    elif seasoncheck == "regularseason":
        checkpreseason = False
    else:
        await ctx.send("preseason 또는 regularseason으로 입력해주세요.")
        return

    if check == GetSumMoney(ctx)[0]:
        datamanage.datareset(ctx.guild)
        await SeasonChange(checkpreseason, ctx)
    else:
        await ctx.send("총 경제규모를 입력해주세요.")


async def SeasonChange(check, ctx):
    if seasoncheck["ispreseason"]:  # 프리시즌일때
        if check:  # 프리시즌 전환이면
            seasoncheck["resetcount"] += 1  # 1을 더한다
        else:  # 정규시즌 전환이면
            seasoncheck["ispreseason"] = False  # 프리시즌을 끈다
            seasoncheck["resetcount"] = 1
    else:  # 정규시즌일때
        if check:  # 프리시즌 전환이면
            seasoncheck["currentseason"] += 1  # 시즌1을 더한다
            seasoncheck["resetcount"] = 1
        else:
            await ctx.send("현재 정규시즌입니다.")

    seasoncheck["ispreseason"] = check

    with open("seasoninfo.json", "w") as seasonfile:
        json.dump(seasoncheck, seasonfile)


print(f"testmode : {testmode}")
print(f"testmode : {testmode}")
print(f"testmode : {testmode}")

time.sleep(5)
bot.run(token)
