import discord
import asyncio

# intentsの設定
intents=discord.Intents.all()
client = discord.Client(intents=intents)

# BOTのトークン
TOKEN = 'AAAAAAAA'

# 役職のID
OLD_ROLE_ID = 1111111111 #古いロールID
NEW_ROLE = 111111111 #新しく付けるロールのID
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.content.startswith('!change'):
        print("処理開始")
        guild = client.get_guild(268606771222806529)
        member = message.author
        role = member.guild.get_role(OLD_ROLE_ID)
        new_role = member.guild.get_role(NEW_ROLE)
        for member in guild.members:
            if role in member.roles:
                await member.remove_roles(role)
                asyncio.sleep(1) #稀に正しく処理されない場合があるので念のためのsleep
                await member.add_roles(new_role)
                asyncio.sleep(1)
                print(member.add_roles) #役職を付けたユーザの情報を出力
                username = member.add_roles
                await message.channel.send(f"{username}の処理が完了しました")
        await message.channel.send("処理が完了")

# BOTの起動
client.run(TOKEN)
