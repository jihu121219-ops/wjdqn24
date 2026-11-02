import traceback
import discord, sqlite3, os, random, asyncio, requests, json, time, sys, re,uuid
from datetime import *
from config import *
from discord_webhook import DiscordEmbed, DiscordWebhook
from discord_componentsss import DiscordComponents, ComponentsBot, Select, SelectOption, Button, ButtonStyle, ActionRow
import string
import random
import secrets

intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def is_admin(user_id):
    try:
        if isinstance(admin_id, (list, tuple, set)):
            return str(user_id) in [str(x) for x in admin_id]
        return str(user_id) == str(admin_id)
    except:
        return False

def start_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    return con, cur
def get_expiretime(time):
    ServerTime = datetime.now()
    ExpireTime = datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        how_long = (ExpireTime - ServerTime)
        days = how_long.days
        hours = how_long.seconds // 3600
        minutes = how_long.seconds // 60 - hours * 60
        return str(round(days)) + "일 " + str(round(hours)) + "시간 " + str(round(minutes)) + "분"
    else:
        return False

def make_expiretime(days):
    ServerTime = datetime.now()
    ExpireTime_STR = (ServerTime + timedelta(days=days)
                      ).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR
def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            dummy1 TEXT,
            expiredate TEXT,
            query TEXT,
            이름 TEXT,
            주민등록번호 TEXT,
            집주소 TEXT,
            주민등록일자 TEXT,
            지역 TEXT,
            얼굴사진 TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            key TEXT PRIMARY KEY,
            expire_days INTEGER
        )
    ''')
    con.commit()
    con.close()

@client.event
async def on_ready():
    init_db()
    DiscordComponents(client)
    print(f"")
    print(f"─────────────────────────────────────────────────────")
    print(
        f"메인시스템을 실행 합니다.: {client.user}\n봇 초대 링크 : https://discord.com/oauth2/authorize?client_id={client.user.id}&permissions=8&scope=bot")
    print(f"─────────────────────────────────────────────────────")
    print(f"사용 중인 서버 : {len(client.guilds)}개 관리 중")
    print(f"")

    await client.change_presence(activity=discord.Game(f"위조민증 제작"), status=discord.Status.online)


@client.event
async def on_message(message):
    if message.author.bot:
        return
    def talmoembed(embedtitle, description):
        return discord.Embed(title=embedtitle, description=description, color=0x2f3136)
    

    if message.content.startswith("!변경"):
        if not is_admin(message.author.id):
            return await message.reply(embed=talmoembed("❌ Fail", f"관리자 권한이 없습니다.\n(당신의 ID: `{message.author.id}`)"))
        parts = message.content.strip().split()
        if len(parts) < 3:
            return await message.reply(embed=talmoembed("ℹ️ 안내", "사용법: `!변경 <유저ID/멘션> <항목(이름/주민등록번호/집주소/주민등록일자/발급지역/얼굴사진/만기일)>`"))
        id = parts[1]
        tab = parts[2]
        try:
            m = id
            m1 = m.split('@')[1]
            m2 = m1.split('>')[0]
            id = m2.split('!')[1]
        except:
            id = id
        con , cur = start_db()
        cur.execute("SELECT * FROM users WHERE id == ?;",(id,))
        info = cur.fetchone()
        con.close()
        if info == None:
            await message.reply(embed=talmoembed("❌ Fail","가입이 되어있지 않습니다."))
            return

            if tab == "이름":
                try:
                    await message.author.send(embed=talmoembed("✅ Success","변경할 이름을 입력해주세요."))
                    await message.reply(embed=talmoembed("✅ Success","DM을 확인해주세요."))
                except:
                    await message.reply(embed=talmoembed("❌ Fail","**```DM이 막혀있습니다!```**"))
                    return
                def check(name):
                    return (isinstance(name.channel, discord.channel.DMChannel) and (message.author.id == name.author.id))
                try:
                    name = await client.wait_for("message", timeout=60, check=check)
                    name = name.content
                    con,cur = start_db()
                    cur.execute("UPDATE users SET 이름 = ? WHERE id == ?;",(name, id))
                    con.commit()
                    con.close()
                    return await message.author.send(embed=talmoembed("✅ Success",f"{tab}이(가) 변경되었습니다"))
                except asyncio.TimeoutError:
                    try:
                        await message.author.send(embed=talmoembed("❌ Fail", "시간이 초과되었습니다."))
                    except:
                        pass
                    return None
            elif tab == "집주소":
                try:
                    await message.author.send(embed=talmoembed("✅ Success",f"변경할 {tab}을(를) 입력해주세요."))
                    await message.reply(embed=talmoembed("✅ Success","DM을 확인해주세요."))
                except:
                    await message.reply(embed=talmoembed("❌ Fail","**```DM이 막혀있습니다!```**"))
                    return
                def check(juso):
                    return (isinstance(juso.channel, discord.channel.DMChannel) and (message.author.id == juso.author.id))
                try:
                    juso = await client.wait_for("message", timeout=60, check=check)
                    juso = juso.content
                    con,cur = start_db()
                    cur.execute("UPDATE users SET 집주소 = ? WHERE id == ?;",(juso, id))
                    con.commit()
                    con.close()
                    return await message.author.send(embed=talmoembed("✅ Success",f"{tab}이(가) 변경되었습니다"))
                except asyncio.TimeoutError:
                    try:
                        await message.author.send(embed=talmoembed("❌ Fail", "시간이 초과되었습니다."))
                    except:
                        pass
                    return None
            elif tab == "주민등록번호":
                try:
                    await message.author.send(embed=talmoembed("✅ Success",f"변경할 {tab}을(를) 입력해주세요.\n\n예)040101-3537921"))
                    await message.reply(embed=talmoembed("✅ Success","DM을 확인해주세요."))
                except:
                    await message.reply(embed=talmoembed("❌ Fail","**```DM이 막혀있습니다!```**"))
                    return
                def check(sex):
                    return (isinstance(sex.channel, discord.channel.DMChannel) and (message.author.id == sex.author.id))
                try:
                    sex = await client.wait_for("message", timeout=60, check=check)
                    sex = sex.content
                    con,cur = start_db()
                    cur.execute("UPDATE users SET 주민등록번호 = ? WHERE id == ?;",(sex, id))
                    con.commit()
                    con.close()
                    return await message.author.send(embed=talmoembed("✅ Success",f"{tab}이(가) 변경되었습니다"))
                except asyncio.TimeoutError:
                    try:
                        await message.author.send(embed=talmoembed("❌ Fail", "시간이 초과되었습니다."))
                    except:
                        pass
                    return None
            elif tab == "주민등록날자":
                try:
                    await message.author.send(embed=talmoembed("✅ Success",f"변경할 {tab}을(를) 입력해주세요."))
                    await message.reply(embed=talmoembed("✅ Success","DM을 확인해주세요."))
                except:
                    await message.reply(embed=talmoembed("❌ Fail","**```DM이 막혀있습니다!```**"))
                    return
                def check(sex1):
                    return (isinstance(sex1.channel, discord.channel.DMChannel) and (message.author.id == sex1.author.id))
                try:
                    sex1 = await client.wait_for("message", timeout=60, check=check)
                    sex1 = sex1.content
                    con,cur = start_db()
                    cur.execute("UPDATE users SET 주민등록일자 = ? WHERE id == ?;",(sex1, id))
                    con.commit()
                    con.close()
                    return await message.author.send(embed=talmoembed("✅ Success",f"{tab}이(가) 변경되었습니다"))
                except asyncio.TimeoutError:
                    try:
                        await message.author.send(embed=talmoembed("❌ Fail", "시간이 초과되었습니다."))
                    except:
                        pass
                    return None
            elif tab == "지역":
                try:
                    await message.author.send(embed=talmoembed("✅ Success",f"변경할 {tab}을(를) 입력해주세요."))
                    await message.reply(embed=talmoembed("✅ Success","DM을 확인해주세요."))
                except:
                    await message.reply(embed=talmoembed("❌ Fail","**```DM이 막혀있습니다!```**"))
                    return
                def check(sex123):
                    return (isinstance(sex123.channel, discord.channel.DMChannel) and (message.author.id == sex123.author.id))
                try:
                    sex123 = await client.wait_for("message", timeout=60, check=check)
                    sex123 = sex123.content
                    con,cur = start_db()
                    cur.execute("UPDATE users SET 지역 = ? WHERE id == ?;",(sex123, id))
                    con.commit()
                    con.close()
                    return await message.author.send(embed=talmoembed("✅ Success",f"{tab}이(가) 변경되었습니다"))
                except asyncio.TimeoutError:
                    try:
                        await message.author.send(embed=talmoembed("❌ Fail", "시간이 초과되었습니다."))
                    except:
                        pass
                    return None
            elif tab == "사진":
                try:
                    await message.author.send(embed=talmoembed("✅ Success",f"변경할 {tab}을(를) 보내주세요."))
                    await message.reply(embed=talmoembed("✅ Success","DM을 확인해주세요."))
                except:
                    await message.reply(embed=talmoembed("❌ Fail","**```DM이 막혀있습니다!```**"))
                    return
                def check_change_img(m):
                    return (isinstance(m.channel, discord.channel.DMChannel) and (message.author.id == m.author.id))
                try:
                    img_msg = await client.wait_for("message", timeout=300, check=check_change_img)
                    imgurl = None
                    if img_msg.attachments and len(img_msg.attachments) > 0:
                        imgurl = img_msg.attachments[0].url
                    elif img_msg.content.startswith("http://") or img_msg.content.startswith("https://"):
                        imgurl = img_msg.content.strip()

                    if not imgurl:
                        await message.author.send(embed=talmoembed("❌ Fail", "올바른 사진 파일이나 이미지 링크를 전송해주세요."))
                        return None
                    con, cur = start_db()
                    cur.execute("UPDATE users SET 얼굴사진 = ? WHERE id == ?;",(str(imgurl), id))
                    con.commit()
                    con.close()
                    return await message.author.send(embed=talmoembed("✅ Success",f"{tab}이(가) 변경되었습니다"))
                except asyncio.TimeoutError:
                    try:
                        await message.author.send(embed=talmoembed("❌ Fail", "시간이 초과되었습니다."))
                    except:
                        pass
                    return None
            elif tab == None:
                await message.reply(embed=talmoembed("❌ Fail","카테고리를 입력해주세요\n예 이름, 집주소, 주민등록날짜, 지역, 사진"))
                return
        else:
            return await message.reply(embed=talmoembed("❌ Fail","관리자 아니면 꺼져라."))

        
        
        

            



        
        

    if message.content.startswith("!내정보"):
        con, cur = start_db()
        cur.execute("SELECT * FROM users WHERE id == ?;", (message.author.id,))
        user_info = cur.fetchone()
        con.close()
        try:
            if (user_info == None):
                return await message.reply(embed=talmoembed("❌ Fail", "가입이 안되셨습니다."))
            else:
                if user_info[2] == None:
                    await message.author.send(embed=talmoembed(str(message.author) + "님의 정보", f"라이센스가 유효하지 않습니다."))
                else:
                    tmp_embed = talmoembed(str(message.author) + "님의 정보", f"**`만기일` : `{user_info[2]}`"
                                                                     f"\n`이름` : `{user_info[4]}`"
                                                                     f"\n`가상 주민등록번호` : `{user_info[5]}`"
                                                                     f"\n`가상 집주소` : `{user_info[6]}`"
                                                                     f"\n`가상 주민등록일자` : `{user_info[7]}`"
                                                                     f"\n`가상 지역` : `{user_info[8]}`"
                                                                     f"\n`사이트주소` : {domain}/{user_info[3]}**")
                    tmp_embed.set_image(url=user_info[9])
                    await message.author.send(embed=tmp_embed)
            await message.reply(embed=talmoembed("✅ Success", f"DM을 확인해주세요."))
        except:
            await message.reply(embed=talmoembed("❌ Fail", f"**```DM이 막혀있습니다!```**"))

    if message.content == ("!도움말"):
        admin_help = "\n`!생성 <개수> <기간>` : `라이센스 생성 (관리자)`\n`!변경 <유저> <항목>` : `정보 수정 (관리자)`" if is_admin(message.author.id) else ""
        tmp_embed = talmoembed("도움말", f"**`!도움말` : `이 도움말을 표시합니다.`"
                                                                     f"\n`!가입` : `Fakeid Service에 가입합니다.`"
                                                                     f"\n`!내정보` : `내 등록 정보를 확인합니다.`"
                                                                     f"\n`!제작` : `위조민증을 제작합니다.`{admin_help}**")
        tmp_embed.set_footer(text="Fake Service")
        await message.reply(embed=tmp_embed)

    if message.content.startswith("!가입"):
        con, cur = start_db()
        cur.execute("SELECT * FROM users WHERE id == ?;", (message.author.id,))
        user_info = cur.fetchone()
        if (user_info == None):
            cur.execute("INSERT INTO users Values(?,?,?,?,?,?,?,?,?,?);", (message.author.id, None, None, None, None, None, None, None, None, None))
            con.commit()
            con.close()
            await message.reply(embed=talmoembed("✅ Success", f"성공적으로 가입이 완료되었습니다.\n\n`{message.author}({message.author.id})`"))
        else:
            con.close()
            await message.reply(embed=talmoembed("❌ Fail", "**이미 가입되있습니다.**"))

    if message.content.startswith("!생성"):
        if not is_admin(message.author.id):
            return await message.reply(embed=talmoembed("❌ Fail", f"관리자 권한이 없습니다.\n(당신의 ID: `{message.author.id}` - config.py의 `admin_id`에 추가해주세요)"))
        
        parts = message.content.strip().split()
        if len(parts) < 3:
            return await message.reply(embed=talmoembed("ℹ️ 안내", "사용법: `!생성 <개수> <기간(일)>`\n예시: `!생성 1 30` (30일권 1개 생성)"))
        
        amount_str = parts[1]
        days_str = parts[2]
        
        if not (amount_str.isdigit() and days_str.isdigit()):
            return await message.reply(embed=talmoembed("❌ Fail", "개수와 기간은 숫자만 입력해주세요.\n예시: `!생성 1 30`"))
        
        amount = int(amount_str)
        expire_days = int(days_str)
        
        if amount < 1 or amount > 10:
            return await message.reply(embed=talmoembed("❌ Fail", "생성 개수는 1개부터 10개까지 가능합니다."))
        
        if expire_days < 1:
            return await message.reply(embed=talmoembed("❌ Fail", "사용 기간은 최소 1일 이상이어야 합니다."))
            
        try:
            con, cur = start_db()
            generated_keys = []
            for _ in range(amount):
                key = str(uuid.uuid4())
                generated_keys.append(key)
                cur.execute("INSERT INTO licenses VALUES(?, ?);", (key, expire_days))
            con.commit()
            con.close()
            
            keys_text = "\n".join(generated_keys)
            await message.reply(embed=talmoembed("✅ Success", f"**{amount}개**의 라이센스 키가 생성되었습니다. (유효기간: {expire_days}일)\n\n```{keys_text}```"))
        except Exception as e:
            traceback.print_exc()
            await message.reply(embed=talmoembed("❌ Fail", f"라이센스 생성 중 오류 발생: {str(e)}"))

    if message.content.startswith("!제작"):
        con, cur = start_db()
        cur.execute("SELECT * FROM users WHERE id == ?;", (message.author.id,))
        user_info = cur.fetchone()
        con.close()
        if (user_info == None):
            return await message.reply(embed=talmoembed("❌ Fail", "가입이 안되셨습니다."))
        try:
            await message.author.send(embed=talmoembed("라이센스 입력", f"구매하신 라이센스 키를 입력해주세요."))
            await message.reply(embed=talmoembed("✅ Success", f"DM을 확인해주세요."))
        except:
            await message.reply(embed=talmoembed("❌ Fail", f"**```DM이 막혀있습니다!```**"))

        def check(license):
            return (isinstance(license.channel, discord.channel.DMChannel) and (message.author.id == license.author.id))

        try:
            license = await client.wait_for("message", timeout=60, check=check)
            license = license.content
            con, cur = start_db()
            cur.execute("SELECT * FROM licenses WHERE key == ?;", (license,))
            key_info = cur.fetchone()
            if (key_info == None):
                con.close()
                await message.author.send(embed=talmoembed("❌ Fail", "존재하지 않거나 이미 사용된 라이센스입니다."))
                return
            new_expiredate = make_expiretime(int(key_info[1]))
            cur.execute("UPDATE users SET expiredate = ? WHERE id == ?;",(new_expiredate, message.author.id))
            con.commit()
            # cur.execute("DELETE FROM licenses WHERE key == ?;", (license,))
            # con.commit()
            con.close()
        except asyncio.TimeoutError:
            try:
                await message.author.send(embed=talmoembed("❌ Fail", "시간이 초과되었습니다."))
            except:
                pass
            return None
        # ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
        name = await message.author.send(embed=talmoembed("위조민증 제작중 [1/6]", "이름을 입력해주세요.\n\n예) 홍길동"))

        def check(name):
            return (isinstance(name.channel, discord.channel.DMChannel) and (
                    message.author.id == name.author.id))

        try:
            name = await client.wait_for("message", timeout=60, check=check)
            name = name.content
        except asyncio.TimeoutError:
            try:
                await message.author.send(embed=talmoembed("❌ Fail", "시간이 초과되었습니다."))
            except:
                pass
            return None
        # ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
        num = await message.author.send(embed=talmoembed("위조민증 제작중 [2/6]", "주민등록번호를 입력해주세요.\n\n예) 040101-3537921"))

        def check(num):
            return (isinstance(num.channel, discord.channel.DMChannel) and (
                    message.author.id == num.author.id))

        try:
            num = await client.wait_for("message", timeout=60, check=check)
            num = num.content
        except asyncio.TimeoutError:
            try:
                await message.author.send(embed=talmoembed("❌ Fail", "시간이 초과되었습니다."))
            except:
                pass
            return None
        # ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
        juso = await message.author.send(embed=talmoembed("위조민증 제작중 [3/6]", "주소를 입력해주세요.\n\n본인 집 주소 또는 위조민증을 사용하실 집 주소를 상세히 입력해주세요\n\n예) 경기도 고양시 일산동구 하늘마을1로 105, 306동 902호(중산동, 하늘마을)\n\n예시의 양식을 무조건 지켜주세요"))


        def check(juso):
            return (isinstance(juso.channel, discord.channel.DMChannel) and (
                    message.author.id == juso.author.id))

        try:
            juso = await client.wait_for("message", timeout=60, check=check)
            juso = juso.content
        except asyncio.TimeoutError:
            try:
                await message.author.send(embed=talmoembed("❌ Fail", "시간이 초과되었습니다."))
            except:
                pass
            return None

        # ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
        make = await message.author.send(embed=talmoembed("위조민증 제작중 [4/6]",
                                                          "주민등록증 일자를 적어주세요.\n\n예) 2021.10.15\n\n점(.) 하나 까지 지켜주셔야합니다, 나이에 맞게 요령껏 만드세요! ( + 주민등록증을 언제 발급받았는지 표기 되는 부분이기 때문에 나이 맞게 잘 부탁드립니다)"))

        def check(make):
            return (isinstance(make.channel, discord.channel.DMChannel) and (
                    message.author.id == make.author.id))

        try:
            make = await client.wait_for("message", timeout=60, check=check)
            make = make.content
        except asyncio.TimeoutError:
            try:
                await message.author.send(embed=talmoembed("❌ Fail", "시간이 초과되었습니다."))
            except:
                pass
            return None
        # ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
        jiname = await message.author.send(embed=talmoembed("위조민증 제작중 [5/6]",
                                                          '민증 발급 지역을 입력해주세요.\n\n예) 부산광역시 남구청장\n\n지역 적으실때는 광역시 또는 특별시는 OO구청장, 시 일때는 oo시장 입니다 부산광역시 남"구청장", 경기도 김포"시장"'))

        def check(jiname):
            return (isinstance(jiname.channel, discord.channel.DMChannel) and (
                    message.author.id == jiname.author.id))

        try:
            jiname = await client.wait_for("message", timeout=60, check=check)
            jiname = jiname.content
        except asyncio.TimeoutError:
            try:
                await message.author.send(embed=talmoembed("❌ Fail", "시간이 초과되었습니다."))
            except:
                pass
            return None

        # ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
        await message.author.send(embed=talmoembed("위조민증 제작중 [6/6]",
                                                    '증명 사진을 업로드 해주세요! (사진 첨부 또는 이미지 링크)'))

        def check_img(m):
            return (isinstance(m.channel, discord.channel.DMChannel) and (
                    message.author.id == m.author.id))

        try:
            img_msg = await client.wait_for("message", timeout=300, check=check_img)
            imgurl = None
            if img_msg.attachments and len(img_msg.attachments) > 0:
                imgurl = img_msg.attachments[0].url
            elif img_msg.content.startswith("http://") or img_msg.content.startswith("https://"):
                imgurl = img_msg.content.strip()

            if not imgurl:
                await message.author.send(embed=talmoembed("❌ Fail", "올바른 사진 파일이나 이미지 링크를 전송해주세요."))
                return None
        except asyncio.TimeoutError:
            try:
                await message.author.send(embed=talmoembed("❌ Fail", "시간이 초과되었습니다."))
            except:
                pass
            return None

        try:
            query = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
            con, cur = start_db()
            cur.execute("UPDATE users SET query = ? WHERE id == ?;",(query, message.author.id))
            cur.execute("UPDATE users SET 이름 = ? WHERE id == ?;",(name, message.author.id))
            cur.execute("UPDATE users SET 주민등록번호 = ? WHERE id == ?;",(num, message.author.id))
            cur.execute("UPDATE users SET 집주소 = ? WHERE id == ?;",(juso, message.author.id))
            cur.execute("UPDATE users SET 주민등록일자 = ? WHERE id == ?;",(make, message.author.id))
            cur.execute("UPDATE users SET 지역 = ? WHERE id == ?;",(jiname, message.author.id))
            cur.execute("UPDATE users SET 얼굴사진 = ? WHERE id == ?;",(str(imgurl), message.author.id))
            con.commit()
            cur.execute("DELETE FROM licenses WHERE key == ?;", (license,))
            con.commit()
            con.close()

            success_text = f"성공적으로 위조민증을 발급했습니다.\n\n🔗 **접속 링크:** {domain}/{query}\n\n잘못 만드셨나요?\n걱정하지마세요! 무상으로 1회 AS가 가능합니다!"
            try:
                await message.author.send(
                    embed=talmoembed("✅ Success", success_text),
                    components=[
                        ActionRow(
                            Button(style=ButtonStyle.URL, label="확인하러 가기",
                                   url=f"{domain}/{query}"))
                    ]
                )
            except Exception:
                await message.author.send(embed=talmoembed("✅ Success", success_text))

            try:
                log = client.get_channel(1088849742408204328)
                if log:
                    con, cur = start_db()
                    cur.execute("SELECT * FROM users WHERE id == ?;", (message.author.id,))
                    user_info = cur.fetchone()
                    con.close()
                    if user_info:
                        tmp_embed = talmoembed(str(message.author) + "님의 정보", f"**`만기일` : `{user_info[2]}`"
                                                                                     f"\n`이름` : `{user_info[4]}`"
                                                                                     f"\n`가상 주민등록번호` : `{user_info[5]}`"
                                                                                     f"\n`가상 집주소` : `{user_info[6]}`"
                                                                                     f"\n`가상 주민등록일자` : `{user_info[7]}`"
                                                                                     f"\n`가상 지역` : `{user_info[8]}`"
                                                                                     f"\n`사이트주소` : {domain}/{user_info[3]}**")
                        tmp_embed.set_image(url=user_info[9])
                        await log.send(embed=tmp_embed)
            except Exception:
                pass
        except Exception as e:
            traceback.print_exc()
            await message.author.send(embed=talmoembed("❌ Fail", f"처리 중 오류가 발생했습니다: {str(e)}"))


client.run(token)
