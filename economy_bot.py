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

bot = commands.Bot(command_prefix='$')
token = "NzY4MjgzMjcyOTQ5Mzk5NjEy.X4-Njg.NfyDMPVlLmgLAf8LkX9p0s04QDY"
version="V1.0.1"

@bot.event
async def on_ready():
    print("bot login test")
    print(bot.user.name)
    print(bot.user.id)
    print("-----------")
    await bot.change_presence(status=discord.Status.online,activity=discord.Game(f'{version}'))


@commands.cooldown(1, 5, commands.BucketType.default)
@bot.command()
async def 가입(ctx,nickname=None) : 
    if nickname==None:
        await ctx.send("닉네임을 입력해주세요.")
        return
    userdiscordid=[]
    nicks=[]
    file=open("user_info.txt","a+",encoding="utf-8")
    file.seek(0)
    lines=file.readlines()
    for line in lines:
        user=line.split(',')
        userdiscordid.append(user[2])
        nicks.append(user[1].lower())
        print(userdiscordid)
    if str(ctx.author.id) in userdiscordid :
        await ctx.send("이미 가입하였습니다.")
        return
    if str(nickname).lower() in nicks :
        await ctx.send("중복되는 닉네임이 있습니다.")
        return
    string_pool=string.ascii_letters+string.digits
    result1=""
    for i in range(20) : 
        result1=result1+random.choice(string_pool)
    file.write(f"{result1},{nickname},{ctx.author.id},{'%010d'%5000},\n")
    await ctx.send("가입 성공!")
    file.close()


@bot.command()
async def 자산(ctx,nickname=None) : 
    if nickname==None:
        await ctx.send("닉네임을 입력해주세요.")
        return
    file=open("user_info.txt","r",encoding="utf-8")
    lines=file.readlines()
    money=-2000
    for line in lines :
        user=line.split(',')
        if user[1].lower()==str(nickname).lower() :
            money=user[3]
    if money==-2000:
        await ctx.send(f"존재하지 않는 유저입니다.")
    else :
        await ctx.send(f"{nickname}의 자산은 {int(money)}모아입니다.")
    file.close()



def get_chance_multiple(mode) :
    if mode==1 : 
        chance=80
        multiple=1.2
    elif mode==2 : 
        chance=64
        multiple=1.6
    elif mode==3 : 
        chance=48
        multiple=2.2
    elif mode==4 : 
        chance=32
        multiple=3
    elif mode==5 : 
        chance=16
        multiple=4
    elif mode==6 :
        chance=85
        multiple=1.13
           
    return chance,multiple

@commands.cooldown(1, 5, commands.BucketType.default)
@bot.command()
async def 베팅(ctx,mode=None,moa=None) :
    file=open("user_info.txt","r",encoding="utf-8")
    lines=file.readlines()
    file.seek(0)
    file_text=file.read()
    money=0
    for line in lines :
        user=line.split(',')
        if user[2]==str(ctx.author.id) :
            money=int(user[3])
    file.close()
    if mode==None : 
        await ctx.send("$베팅 (모드) (모아)\n(모드 종류 : 1 80% 1.4배, 2 64% 1.8배, 3 48% 2.2배, 4 32% 2.6배, 5 16% 3배, 6 85% 1.13배(올인만 가능)")
        return
    if int(mode)==6 :
        moa=money
    if moa==None : 
        await ctx.send("$베팅 (모드) (모아)\n(모드 종류 : 1 80% 1.4배, 2 64% 1.8배, 3 48% 2.2배, 4 32% 2.6배, 5 16% 3배, 6 85% 1.13배(올인만 가능)")
        return
    if money<int(moa) or int(moa)<0 : 
        await ctx.author.send("보유량보다 많거나 0원 미만으로 베팅하실 수 없습니다.")
        return    
    if int(mode)>6 or int(mode)<1 : 
        await ctx.send("$베팅 (모드) (모아)\n(모드 종류 : 1 80% 1.4배, 2 64% 1.8배, 3 48% 2.2배, 4 32% 2.6배, 5 16% 3배, 6 85% 1.13배(올인만 가능)")
        return
    
    chance,multiple=get_chance_multiple(int(mode))
    result=random.randrange(0,100)
    lose=int(moa)
    end=0
    file=open("user_info.txt","w")
    if result<chance : 
        profit=math.floor(multiple*int(moa))
        end=money-lose+profit
        await ctx.send("베팅 성공!")              
    else :
        end=money-int(moa)
        await ctx.send("베팅 실패!")
    file_text=file_text.replace(f"{ctx.author.id},{'%010d'%money}",f"{ctx.author.id},{'%010d'%end}")
    file.write(file_text)
    file.close()
    
    


bot.run(token)