import asyncio
import math
import random
import discord
from financial import givemoney, setluckypang
import datetime
import datamanage
import json
import financial
import traceback
import datarecord
import os


async def doforce(
    message,
    reuser,
    mode,
    ispreseason,
    maxlucky,
    useitem=False,
    isAdvance=False,
    datapath=None,
):
    chour = datetime.datetime.now().time().hour

    maxlevel = GetMaxLevel(isAdvance)
    NotDestroy = False
    FastUp = False
    count = 1

    if mode == 2:
        NotDestroy = True
    elif mode == 3:
        count = 3
    elif mode == 4:
        FastUp = True

    level = 1
    result = 0.0
    change = 0

    moa = 0
    level = 0
    totalfailneed = 0
    userData = None

    filename = f"data/{message.guild.id}/{reuser.id}.json"

    with open(filename, "r") as f:
        userData = json.load(f)

    level = userData["unknownLevel"]
    moa = userData["money"]
    nickname = userData["nickname"]

    # region 반복 구간 시작

    for i in range(count):
        if isAdvance:
            f = open(f"data/{message.guild.id}/advforceuser.json", "r")
            userlist = json.load(f)
            f.close()

        ctx = message.channel

        if isAdvance:
            if str(reuser.id) in userlist.keys():
                level = userlist[str(reuser.id)]
            else:
                return

        if level == 0:
            await ctx.send("의문의 물건을 가지고 있지 않습니다.")
            break

        need = get_need(level, isAdvance)

        if level >= maxlevel:
            await ctx.send("강화를 완료한 의문의 물건입니다. 판매시 시즌이 종료됩니다.")
            return

        cri_success = GetCriSuccess(level, isAdvance)
        destroy = GetDestroy(level, ispreseason, isAdvance)
        success = GetSuccess(level, isAdvance)
        fail = get_fail(level, isAdvance)
        not_change = 100 - cri_success - success - fail - destroy

        if mode == 5:
            cri_success = 0
            success = 95
            not_change = 0
            fail = 0
            destroy = 100 - success
            need *= 10

        if NotDestroy:
            if destroy != 0:
                if not ispreseason:
                    need = math.floor(need * 1.1)
                not_change += destroy
                destroy = 0
            else:
                await ctx.send("파괴 방지가 불가능합니다.")
                return
        if FastUp:
            if level > 23:
                await ctx.send("24렙 이상은 4렙 업 찬스를 사용할 수 없습니다.")
                return
            else:
                if not useitem:
                    if ispreseason:
                        need = math.floor(need * 2)
                    else:
                        need *= 3

        if mode == 1:
            if chour == 15 and not isAdvance and level >= 25:
                need = math.floor(need * 0.85)
            elif chour == 15 and isAdvance and level >= 7:
                need = math.floor(need * 0.95)

        if need > moa:
            await ctx.send(f"{need-moa}모아가 부족합니다.")
            break
        else:
            userData["money"] -= need

        result = random.random() * 100

        if result < cri_success:
            if FastUp:
                change = 6
            else:
                change = 2
        elif result < cri_success + success:
            if FastUp:
                change = 4
            else:
                change = 1
        elif result < cri_success + success + not_change:
            change = 0
        elif result < cri_success + success + not_change + fail:
            change = -1
        else:
            change = -10

        head = ""
        if isAdvance:
            head = "고오급 "

        if change != -10:
            if isAdvance:
                print(userlist)
                userlist[str(reuser.id)] += change
            else:
                userData["unknownLevel"] += change
            if change > 0:
                await ctx.send(
                    f"{nickname}, 강화 레벨 {level}에서 {change} 상승! 현재 레벨 : {level+change}"
                )
            elif change < 0:
                await ctx.send(
                    f"{nickname}, 강화 레벨 {level}에서 {-change} 감소! 현재 레벨 : {level+change}"
                )
            else:
                await ctx.send(f"{nickname}, 강화 레벨 {level}에서 변동 없음! 현재 레벨 : {level}")
        else:
            if isAdvance:
                userlist.pop(str(reuser.id))
            else:
                userData["unknownLevel"] = 0
            await ctx.send(f"{nickname}, {head}의문의 물건 +{level} 파괴...")

        if change <= 0:
            totalfailneed += math.floor(need * 0.1)

        if change == -10:
            break
        await asyncio.sleep(0.1)

    # endregion

    if not isAdvance:
        f = open(f"data/{ctx.guild.id}/{reuser.id}.json", "w")
        json.dump(userData, f)
        f.close()
    else:
        f = open(f"data/{ctx.guild.id}/advforceuser.json", "w")
        json.dump(userlist, f)
        f.close()

    if totalfailneed != 0:
        await setluckypang(
            math.floor(totalfailneed), message.channel, maxlucky, datapath
        )


def GetSuccess(level, isAdvance=False):
    if isAdvance:
        return 100 - 7.8 * level
    else:
        return 100 - 2.57 * level


def GetDestroy(level, ispreseason, isAdvance=False):
    if not isAdvance:
        destroy = 0
        if ispreseason:
            destroy = 0
        else:
            destroy = 0.8 * (level - 1)
        return destroy
    else:
        return 4.33 * (level - 1)


def GetCriSuccess(level, isAdvance=False):
    if isAdvance:
        return 0
    else:
        if level <= 29:
            cri_success = 0.05 * (30 - level)
        else:
            cri_success = 0.0
        return cri_success


def get_need(level, isAdvance=False):

    if isAdvance:
        return math.floor(500000 * level ** (1 + 0.22 * level - 1))
    else:
        temp = [0, 0, 0, 0, 0, 0]
        temp2 = 0
        for i in range(level):
            if i < 6:
                temp[i] = 1
                temp2 = 1
            else:
                temp2 = sum(temp)
                temp[0] = temp[1]
                temp[1] = temp[2]
                temp[2] = temp[3]
                temp[3] = temp[4]
                temp[4] = temp[5]
                temp[5] = temp2
        return temp2


def get_fail(level, isAdvance=False):
    temp = 0
    if isAdvance:
        return 4.07 * (level - 1)
    else:
        for i in range(level):
            if i == 0:
                temp = 0
            else:
                temp += 0.1 * i

        if level % 7 == 0:
            temp = 0

        return temp


def GetMaxLevel(isadvance):
    if isadvance:
        return 13
    else:
        return 36


async def sellforce(message, reuser, isAdvance=False):
    head = ""
    filename = ""
    userhave = {}
    if isAdvance:
        head = "고오급 "
        filename = "data/advforcestore.json"
        with open("data/advforceuser.json", "r") as file:
            userhave = json.load(file)
    else:
        head = ""
        filename = "data/forcestore.json"

    ctx = message.channel
    level = 0
    maxlevel = GetMaxLevel(isAdvance)

    file = open(f"data/user_info{message.guild.id}", "r")
    file.seek(0)
    lines = file.readlines()
    file.close()

    nickname = ""

    for user in lines:
        user_info = user.split(",")
        if user_info[2] == str(reuser.id):
            nickname = user_info[1]
            level = int(user_info[4])

    if isAdvance:
        if str(reuser.id) in userhave.keys():
            level = userhave[str(reuser.id)]
        else:
            return

    if level <= 1:
        await reuser.send(f"{head}의문의 물건이 +1이거나 가지고 있지 않습니다.")
        return

    pricesell = get_price(level, isAdvance)[1]

    if not isAdvance:
        givemoney(ctx, nickname, pricesell, 1)
    else:
        givemoney(ctx, nickname, pricesell)

    if level >= maxlevel:
        await ctx.send(
            f"{head}의문의 물건 {maxlevel}강을 판매되어서 시즌이 종료되었습니다. 관련 공지가 있을때까지 프리시즌이 유지됩니다."
        )

        datamanage.datareset(message.guild)

        return True

    forceSale = {}

    with open(filename, "r") as forceFile:
        forceSale = json.load(forceFile)

    print(userhave)
    if isAdvance:
        userhave.pop(str(reuser.id))

    if f"{level}" in forceSale.keys():
        forceSale[f"{level}"] += 1
    else:
        forceSale[f"{level}"] = 1

    with open(filename, "w") as forceFile:
        json.dump(forceSale, forceFile)

    if isAdvance:
        with open("data/advforceuser.json", "w") as file:
            json.dump(userhave, file)

    await ctx.send(f"의문의 물건 +{level}이 판매되었습니다.")


def get_price(level, isadv=False):
    temp_buy = 0
    temp_sell = 0
    level = int(level)
    if not isadv:
        temp = [0, 0, 0, 0]

        for i in range(level):
            if i < 4:
                temp[i] = i + 1
                temp_sell = i + 1
            else:
                temp_sell = sum(temp)
                temp[0] = temp[1]
                temp[1] = temp[2]
                temp[2] = temp[3]
                temp[3] = temp_sell
        for i in range(level):
            if i < 4:
                temp[i] = i + 2
                temp_buy = i + 2
            else:
                temp_buy = sum(temp)
                temp[0] = temp[1]
                temp[1] = temp[2]
                temp[2] = temp[3]
                temp[3] = temp_buy
    else:
        temp_buy = math.floor(5000000 * level ** (1 + 0.18 * level - 1))
        temp_sell = math.floor(6230000 * (level - 1) ** (1 + 0.17 * level - 1))
    return temp_buy, temp_sell


async def buyforce(ctx, level, isadvance=False):
    try:
        filename = datamanage.GetFileName(ctx)
        if not os.path.isfile(filename):
            await ctx.send("가입을 해주세요.")
            return

        name = ""
        forceSale = {}
        userforce = {}
        if isadvance:
            name = "고오급 "
            with open(f"data/{ctx.guild.id}/advforcestore.json", "r") as forceFile:
                forceSale = json.load(forceFile)
        else:
            with open(f"data/{ctx.guild.id}/forcestore.json", "r") as forceFile:
                forceSale = json.load(forceFile)

        sale = False
        chour = datetime.datetime.now().time().hour
        if chour == 13 or chour == 21 or chour == 17:
            sale = True
        nickname = ""
        showtext = "```"

        if level == None:
            head = ""
            if isadvance:
                head = "고오급 "
            if sale:
                showtext += "의문의 물건 +15이상 20% 할인중!\n"
            for key, value in list(sorted(forceSale.items())):
                price = get_price(key, isadvance)[0]
                if int(key) >= 15 and sale:
                    showtext += (
                        f"{head}의문의 물건 +{key}, {value}개 남음, {math.floor(price*0.8)}모아\n"
                    )
                else:
                    showtext += f"{head}의문의 물건 +{key}, {value}개 남음, {price}모아\n"
            showtext += "```"
            await ctx.send(showtext)
            return

        userfile = open(filename, "r")
        userInfo = json.load(userfile)

        nickname = userInfo["nickname"]
        money = userInfo["money"]
        mylevel = userInfo["unknownLevel"]

        if isadvance:
            with open(f"data/{ctx.guild.id}/advforceuser.json", "r") as forceFile:
                userforce = json.load(forceFile)
            if str(ctx.author.id) in userforce.keys():
                mylevel = userforce[str(ctx.author.id)]
            else:
                mylevel = 0

        if mylevel > 0:

            await ctx.send("의문의 물건은 1개만 보유할수 있습니다.")
            return

        if not str(level) in forceSale.keys():
            await ctx.send(f"의문의 물건 +{level}의 매물이 없습니다.")
            return

        price = 0
        if int(level) >= 15 and sale and (not isadvance):
            price = math.floor(get_price(level)[0] * 0.8)
        else:
            price = get_price(level, isadvance)[0]

        print(price)

        if money >= price:
            if not isadvance:
                givemoney(ctx, nickname, price, 2, level)
            else:
                givemoney(ctx, nickname, -price)
        else:
            await ctx.send(f"{price-money}모아가 부족합니다.")
            return

        forceSale[level] -= 1
        if forceSale[level] <= 0:
            forceSale.pop(level)

        userforce[str(ctx.author.id)] = int(level)

        if not isadvance:
            with open(f"data/{ctx.guild.id}/forcestore.json", "w") as forceFile:
                json.dump(forceSale, forceFile)
        else:
            with open(f"data/{ctx.guild.id}/advforcestore.json", "w") as forceFile:
                json.dump(forceSale, forceFile)
            with open(f"data/{ctx.guild.id}/advforceuser.json", "w") as forceFile:
                json.dump(userforce, forceFile)

        await ctx.send(f"{nickname}, {name}의문의 물건 +{level} 구매 성공")

    except Exception as e:
        await ctx.send(f"{e}\n$강화구매 (레벨)")
        traceback.print_exc()


def TestForce():
    clevel = 1
    maxlevel = GetMaxLevel(True)
    totaluse = get_price(clevel, True)[0]
    trycount = 0
    destroy = 0
    while clevel < maxlevel:
        f = get_fail(clevel, True)
        s = GetSuccess(clevel, True)
        cs = GetCriSuccess(clevel, True)
        d = GetDestroy(clevel, False, True)
        nc = 100 - f - s - cs - d
        totaluse += get_need(clevel, True)

        result = random.random() * 100

        if result < cs:
            change = 2
        elif result < cs + s:
            change = 1
        elif result < cs + s + nc:
            change = 0
        elif result < cs + s + nc + f:
            change = -1
        else:
            change = -10

        if change != -10:
            clevel += change
        else:
            clevel = 1
            totaluse += get_price(clevel, True)[0]
            destroy += 1

        trycount += 1

        print(
            f"trycount:{trycount}  level:{clevel} totaluse:{format(totaluse,',')}    destroy:{destroy}"
        )
