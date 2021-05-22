import datetime
import io
import json
import random
import sys
import uuid

import aiohttp
import discord
from dispander import dispand
import requests
from discord.ext import tasks
from PIL import Image, ImageDraw, ImageFont

from func import diceroll

client = discord.Client()
channel = client.get_channel(Channel_ID)

json_open = open('token.json', 'r')
json_load = json.load(json_open)
token = json_load['section']['token']


@client.event
async def on_ready():
    """起動時に通知してくれる処理"""
    print('System Ready')
    print(client.user.id)  # ボットのID
    print(discord.__version__)  # discord.pyのバージョン
    print('------')
    print(f'websocket latency={client.latency*1000:.0f}')

@client.event 
async def on_message(message):
    OWNER = 455111438005174283
    if message.author.bot:  # ボットのメッセージをハネる
        return
    
    #URL展開
    await dispand(message)

#ヘルプ機能
    if message.content == "!help":
        embed = discord.Embed(title="昆布君", description="welcome",color=0xff0000)
        embed.add_field(name="!dice", value="サイコロを振ります", inline=True)
        embed.add_field(name="!t (内容)", value="AIと簡単な会話ができます", inline=True)
        embed.add_field(name="!now", value="今の時間を送信します", inline=True)
        embed.add_field(name="!ping", value="PINGを測定します", inline=True)
        embed.add_field(name="!make (文字) (文字色) (背景色)", value="文字の画像を生成します", inline=True)
        embed.add_field(name="!qrcode (URL)", value="QRコードを生成します", inline=True)
        embed.add_field(name="!yatte (某氏にやってほしいこと)", value="某氏にやってほしいことを追加します", inline=True)
        embed.add_field(name="!katte (買ってほしいもの)", value="買ってほしいものを追加します", inline=True)
        embed.add_field(name="!list (リストの名前)", value="リストの内容を送信します", inline=True)
        await message.channel.send(embed=embed)


#Dice BOT
    if message.content.startswith("!dice"):
        # 入力された内容を受け取る
        say = message.content 
        if len(say) < 13:
            say = say
        else:
            await message.channel.send("Error:文字数が多すぎます")
            return

        # [!dice ]部分を消し、AdBのdで区切ってリスト化する
        order = say.strip('!dice ')
        cnt, mx = list(map(int, order.split('d'))) # さいころの個数と面数
        dice = diceroll(cnt, mx) # 和を計算する関数(後述)
        await message.channel.send(dice[cnt])
        del dice[cnt]

        # さいころの目の総和の内訳を表示する
        await message.channel.send(dice)

#普通のBOT

    if message.content.startswith("!t"):
        msg = message.content.split(" ")[1]

        payload = { "apikey" : "APIKEY" ,"query": msg }

        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.a3rt.recruit-tech.co.jp/talk/v1/smalltalk',data=payload) as resp:
                script = await resp.json()

        await message.channel.send(script["results"][0]["reply"])

    


    if message.content == "!exit":
        if OWNER == message.author.id:
            await message.channel.send("終了します")
            sys.exit()
        else:
            await message.channel.send("権限がありません")
            return

    if message.content == "!channel":
        test = message.channel.guild.channels
        await message.channel.send(test)
    

    if message.content == "!now":
        dt_now = datetime.datetime.now()
        await message.channel.send(dt_now)

    if message.content == "!uuid":
        tmp = str(uuid.uuid4())
        await message.channel.send(tmp)
    
    if message.content.startswith("!status"):
        if OWNER == message.author.id:
            tmp10 = message.content.split(" ")
            tmp10 = tmp10[1]
            game = discord.Game(tmp10)
            await client.change_presence(activity=game)
            await message.channel.send(f"ステータスを「{tmp10}」に変更しました")
        else:
            return

    
    if message.content == "!ping":
        ping = (f'{client.latency*1000:.0f}')
        await message.channel.send(f'PINGは{ping}msでした')
    
    if message.content.startswith("!make"):
        make = message.content.split(" ")
        dt = datetime.datetime.now()
        dt = str(dt)
        #fonts = {1:'./Uni Sans Heavy.otf',2:'./HackGenConsole-Bold-forPowerline.ttf'}
        try:
            backcolor = make[3]
        except IndexError:
            backcolor = 1, 5, 53 #背景処理


        try:
            color = make[2]
        except IndexError:
            color = 'white'   #文字色指定
        make = make[1]
        #try:
        #    fontsr = (fonts[font])
        #except KeyError:
        #    await message.channel.send("フォントが見つかりませんでした")

        #ここから画像生成 ↓
        im = Image.new('RGBA', (1000, 100), (backcolor))
        draw = ImageDraw.Draw(im)
        arial_font = ImageFont.truetype('./marukoias.ttf', 60)
        try:
            draw.text((15, 10), make, fill=color, font=arial_font)
        except ValueError:
            await message.channel.send ("Error!")
            return
        im.save('text.png')
        print ("OK")
        await message.channel.send(file=discord.File("./text.png"))

    if message.content.startswith("!len"):
        lens = message.content.split(" ")
        if len(lens) > 1:
            lens = lens
        else:
            await message.channel.send("Error:引数が指定されていません")
        lens = lens[1]
        sentlens = len(lens)
        await message.channel.send(sentlens)


    if message.content == "!history":
        tmp = await message.channel.history( limit = 10 ).flatten()
        await message.channel.send( "\n".join( [ i.content for i in tmp] ) )
    



#QR生成
    if message.content.startswith("!qrcode"):
        tmp = message.content.split(" ")

        if len(tmp) > 1:
            url = tmp[1]
        else:
            await message.channel.send("Error:URLが指定されていません。")
            return

        payload = {"data":url,"size":"300x300"} # sizeは自由に変更可

        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.qrserver.com/v1/create-qr-code/",params=payload) as resp:
                if resp.status != 200:
                    return await message.channel.send('Error:ファイルをダウンロードできませんでした。\n時間を置いてからお試しください')

                data = io.BytesIO(await resp.read())

        await message.channel.send(file=discord.File(data, url+'.png'))



#やってシステム
    if message.content.startswith("!yatte"):
        tmp = message.content.split(" ")
        
        file = open('yatte.txt','a', encoding='utf-8')
        tmp = tmp[1]
        tmp2 = tmp
        tmp1 = (f"{tmp} , ")
        file.writelines(tmp1)
        file.close()
        await message.channel.send(f"「{tmp2}」をやることリストに追加しました")
    

    if message.content.startswith("!katte"):
        tmp = message.content.split(" ")
        
        file = open('katte.txt','a', encoding='utf-8')
        tmp = tmp[1]
        tmp2 = tmp
        tmp1 = (f"{tmp} , ")
        file.writelines(tmp1)
        file.close()
        await message.channel.send(f"「{tmp2}」を欲しい物リストに追加しました")


    if message.content.startswith("!list"):
        tmp = message.content.split(" ")
        tmp = tmp[1]
        tmp1 = tmp[2]
        if tmp == ("yatte"):
            file = open('yatte.txt','r', encoding='utf-8')
            string = file.read()
            embed=discord.Embed(title="やることリスト", color=0xff0000)
            embed.add_field(name="~~~~", value=string, inline=False)
            await message.channel.send(embed=embed)

            if tmp1 == ("clear"):
                text = ' '
                file = open('yatte.txt','w', encoding='utf-8')
                string = file.write(text)
                file.close
        if tmp == ("katte"):
            file = open('katte.txt','r', encoding='utf-8')
            string = file.read()
            embed=discord.Embed(title="欲しい物リスト", color=0xff0000)
            embed.add_field(name="~~~~", value=string, inline=False)
            await message.channel.send(embed=embed)
        else:
            return





    


    
    #if message.content == "!reiwa":
    #    await message.channel.send("新しい元号は令和であります。", file=discord.File('reiwa.png'))
    #if message.content == "!heisei":
    #    await message.channel.send("新しい元号は平成であります。", file=discord.File('heisei.png')) 
    #if message.content == "!mokusou":
    #    await message.channel.send("新しい元号は黙想であります。", file=discord.File('mokusou.jpg'))
    #if message.content == "!nikkei":
    #    await message.channel.send(f"日経平均株価は{result}円です。")
    #if message.content == "!ny":
    #    await message.channel.send(f"NYダウは{result2}です。")
    #if message.content == "!help":
    #    await message.channel.send("!reiwaで令和 !heiseiで平成 !mokusouで黙想 !nikkeiで日経平均株価 !nyでNYダウ !おみくじでおみくじができます。")
    #if message.content == "!おみくじ":
    #    # Embedを使ったメッセージ送信 と ランダムで要素を選択
    #    embed = discord.Embed(title="おみくじ", description=f"{message.author.mention}さんの今日の運勢は！",
    #                          color=0x2ECC69)
    #    embed.set_thumbnail(url=message.author.avatar_url)
    #    embed.add_field(name="[運勢] ", value=random.choice(('大大吉', '大吉', '中吉', '吉', '小吉', '凶', '大凶', '吉','システム障害','エラー')), inline=False)
    #    await message.channel.send(embed=embed)
    #if message.content == "!DM":
    #    # ダイレクトメッセージ送信
    #    dm = await message.author.create_dm()
    #    await dm.send(f"{message.author.mention}さん こんにちは")
client.run(token)
