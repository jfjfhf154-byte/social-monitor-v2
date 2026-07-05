import os
import json
import time
import logging
import datetime
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from image_generator import create_notification_image

# تحميل الإعدادات
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ROBLOX_COOKIE = os.getenv("ROBLOX_COOKIE")
YOUTUBE_URL = os.getenv("YOUTUBE_URL", "https://youtube.com/@taleencute9315")
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "tulyx_v")
TIKTOK_USERNAME = os.getenv("TIKTOK_USERNAME", "tulyx_v")
ROBLOX_USERNAME = os.getenv("ROBLOX_USERNAME", "qad4s")
TELEGRAM_USERNAME = os.getenv("TELEGRAM_USERNAME", "tulyx_v")
PINTEREST_USERNAME = os.getenv("PINTEREST_USERNAME", "tulyx_v")

# ملف حفظ البيانات السابقة
DATA_FILE = "data.json"

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===================== جلب البيانات =====================

def get_youtube_stats():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        response = requests.get(YOUTUBE_URL, headers=headers, timeout=15)
        
        match = re.search(r'var ytInitialData = ({.*?});</script>', response.text)
        if match:
            data = json.loads(match.group(1))
            try:
                header = data['header']['pageHeaderRenderer']['content']['pageHeaderViewModel']
                metadata = header['metadata']['contentMetadataViewModel']['metadataRows'][1]['metadataParts']
                subscribers = metadata[0]['text']['content']
                videos = metadata[1]['text']['content']
                return {"subscribers": subscribers, "videos": videos, "error": None}
            except (KeyError, IndexError):
                try:
                    header = data['header']['c4TabbedHeaderRenderer']
                    subscribers = header['subscriberCountText']['simpleText']
                    videos = header['videosCountText']['runs'][0]['text']
                    return {"subscribers": subscribers, "videos": videos, "error": None}
                except KeyError:
                    pass
        return {"error": "فشل في جلب بيانات يوتيوب"}
    except Exception as e:
        return {"error": str(e)}

def get_instagram_stats():
    try:
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={INSTAGRAM_USERNAME}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "X-IG-App-ID": "936619743392459"
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            user = data['data']['user']
            return {
                "followers": user['edge_followed_by']['count'],
                "following": user['edge_follow']['count'],
                "posts": user['edge_owner_to_timeline_media']['count'],
                "error": None
            }
        return {"error": f"Instagram API: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_tiktok_stats():
    try:
        url = f"https://www.tiktok.com/@{TIKTOK_USERNAME}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Accept-Language": "en-US,en;q=0.9"
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        # البحث في SIGI_STATE
        match = re.search(r'id="SIGI_STATE"[^>]*>(.*?)</script>', response.text, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
            user_module = data.get('UserModule', {})
            stats = user_module.get('stats', {})
            for key in stats:
                user_stats = stats[key]
                return {
                    "followers": user_stats.get('followerCount', 0),
                    "following": user_stats.get('followingCount', 0),
                    "likes": user_stats.get('heartCount', 0),
                    "error": None
                }
        
        # محاولة بديلة
        soup = BeautifulSoup(response.text, 'html.parser')
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            desc = meta_desc['content']
            followers_match = re.search(r'([\d,\.]+[KMB]?)\s+Followers', desc, re.IGNORECASE)
            likes_match = re.search(r'([\d,\.]+[KMB]?)\s+Likes', desc, re.IGNORECASE)
            
            def parse_short_num(s):
                if not s: return 0
                s = s.replace(',', '')
                if s[-1].upper() == 'K': return int(float(s[:-1]) * 1000)
                if s[-1].upper() == 'M': return int(float(s[:-1]) * 1000000)
                if s[-1].upper() == 'B': return int(float(s[:-1]) * 1000000000)
                return int(float(s))
            
            return {
                "followers": parse_short_num(followers_match.group(1)) if followers_match else 0,
                "following": 0,
                "likes": parse_short_num(likes_match.group(1)) if likes_match else 0,
                "error": None
            }
        
        return {"error": "لم يتم العثور على بيانات تيك توك"}
    except Exception as e:
        return {"error": str(e)}

def get_roblox_stats():
    try:
        cookies = {".ROBLOSECURITY": ROBLOX_COOKIE}
        
        # الحصول على User ID
        user_response = requests.post(
            "https://users.roblox.com/v1/usernames/users",
            json={"usernames": [ROBLOX_USERNAME], "excludeBannedUsers": True},
            timeout=15
        )
        if user_response.status_code != 200 or not user_response.json().get("data"):
            return {"error": "لم يتم العثور على مستخدم روبلكس"}
        
        user_id = user_response.json()["data"][0]["id"]
        
        # جلب الأصدقاء
        friends_r = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/friends/count", timeout=10)
        friends_count = friends_r.json().get("count", 0)
        
        # جلب المتابعين
        followers_r = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/followers/count", timeout=10)
        followers_count = followers_r.json().get("count", 0)
        
        # جلب المتابَعين
        following_r = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/followings/count", timeout=10)
        following_count = following_r.json().get("count", 0)
        
        # جلب البادجات
        badges_r = requests.get(f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=100", cookies=cookies, timeout=10)
        badges_data = badges_r.json().get("data", [])
        badges_count = len(badges_data)
        badges_list = [b.get("name", "") for b in badges_data]
        
        # جلب المجموعات
        groups_r = requests.get(f"https://groups.roblox.com/v1/users/{user_id}/groups/roles", timeout=10)
        groups_data = groups_r.json().get("data", [])
        groups_count = len(groups_data)
        groups_list = [g.get("group", {}).get("name", "") for g in groups_data]
        
        # جلب المفضلة (المابات)
        favorites_r = requests.get(
            f"https://games.roblox.com/v2/users/{user_id}/favorite/games?accessFilter=Public&limit=50",
            cookies=cookies, timeout=10
        )
        favorites_data = favorites_r.json().get("data", [])
        favorites_count = len(favorites_data)
        favorites_list = [f.get("name", "") for f in favorites_data]
        
        # جلب الانفنتوري
        inventory_r = requests.get(
            f"https://inventory.roblox.com/v1/users/{user_id}/assets/collectibles?limit=100",
            cookies=cookies, timeout=10
        )
        inventory_data = inventory_r.json().get("data", [])
        inventory_count = len(inventory_data)
        
        return {
            "friends": friends_count,
            "followers": followers_count,
            "following": following_count,
            "badges": badges_count,
            "badges_list": badges_list,
            "groups": groups_count,
            "groups_list": groups_list,
            "favorites": favorites_count,
            "favorites_list": favorites_list,
            "inventory": inventory_count,
            "error": None
        }
    except Exception as e:
        return {"error": str(e)}

def get_telegram_stats():
    try:
        url = f"https://t.me/{TELEGRAM_USERNAME}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=15)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # البحث عن صورة الحساب
        photo_meta = soup.find('meta', property='og:image')
        photo_url = photo_meta['content'] if photo_meta else None
        
        # البحث عن عدد المشتركين (للقنوات)
        subscribers_div = soup.find('div', class_='tgme_page_extra')
        subscribers_text = subscribers_div.text if subscribers_div else "0"
        numbers = re.findall(r'\d+', subscribers_text.replace(',', ''))
        count = int(numbers[0]) if numbers else 0
        
        return {
            "subscribers": count,
            "photo_url": photo_url,
            "error": None
        }
    except Exception as e:
        return {"error": str(e)}

def get_pinterest_stats():
    try:
        url = f"https://www.pinterest.com/{PINTEREST_USERNAME}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        
        if meta_desc:
            desc = meta_desc['content']
            followers_match = re.search(r'([\d,]+)\s+followers?', desc, re.IGNORECASE)
            following_match = re.search(r'([\d,]+)\s+following', desc, re.IGNORECASE)
            followers = int(followers_match.group(1).replace(',', '')) if followers_match else 0
            following = int(following_match.group(1).replace(',', '')) if following_match else 0
            return {"followers": followers, "following": following, "error": None}
        
        return {"error": "لم يتم العثور على بيانات بنترست"}
    except Exception as e:
        return {"error": str(e)}

# ===================== إرسال الإشعارات =====================

def send_telegram_photo(image_path, caption=""):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        with open(image_path, 'rb') as photo:
            response = requests.post(url, data={
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption
            }, files={"photo": photo}, timeout=30)
        return response.json()
    except Exception as e:
        logger.error(f"فشل إرسال الصورة: {e}")
        return None

def send_telegram_message(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        response = requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }, timeout=15)
        return response.json()
    except Exception as e:
        logger.error(f"فشل إرسال الرسالة: {e}")
        return None

# ===================== حفظ وقراءة البيانات =====================

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ===================== مقارنة وإرسال التغييرات =====================

def compare_and_notify(platform, old_data, new_data, field_labels):
    """
    مقارنة البيانات القديمة والجديدة وإرسال إشعار إذا كان هناك تغيير
    field_labels: قاموس {اسم_الحقل: تسمية_عربية}
    """
    changes = []
    
    for field, label in field_labels.items():
        old_val = old_data.get(field)
        new_val = new_data.get(field)
        
        if old_val is None or new_val is None:
            continue
        
        # للقوائم (مثل البادجات والمجموعات)
        if isinstance(old_val, list) and isinstance(new_val, list):
            added = [x for x in new_val if x not in old_val]
            removed = [x for x in old_val if x not in new_val]
            
            if added:
                changes.append({
                    "label": f"{label} (Added)",
                    "old": len(old_val),
                    "new": len(new_val),
                    "change": f"+{len(added)}: {', '.join(added[:3])}"
                })
            if removed:
                changes.append({
                    "label": f"{label} (Removed)",
                    "old": len(old_val),
                    "new": len(new_val),
                    "change": f"-{len(removed)}: {', '.join(removed[:3])}"
                })
        # للأرقام
        elif isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
            if old_val != new_val:
                diff = new_val - old_val
                changes.append({
                    "label": label,
                    "old": old_val,
                    "new": new_val,
                    "change": f"+{diff}" if diff > 0 else str(diff)
                })
        # للنصوص
        elif isinstance(old_val, str) and isinstance(new_val, str):
            if old_val != new_val:
                changes.append({
                    "label": label,
                    "old": old_val,
                    "new": new_val,
                    "change": "Changed"
                })
    
    if changes:
        # إنشاء صورة الإشعار
        img_path = f"/tmp/notification_{platform}_{int(time.time())}.png"
        create_notification_image(platform, changes, img_path)
        
        # إرسال الصورة
        caption = f"🔔 {platform.upper()} - تم رصد تغيير!"
        send_telegram_photo(img_path, caption)
        
        # حذف الصورة المؤقتة
        try:
            os.remove(img_path)
        except:
            pass
        
        logger.info(f"تم إرسال إشعار {platform}: {len(changes)} تغيير")
    else:
        logger.info(f"{platform}: لا يوجد تغيير")

# ===================== دوال المراقبة =====================

def check_youtube():
    logger.info("فحص يوتيوب...")
    data = load_data()
    new_stats = get_youtube_stats()
    
    if new_stats.get("error"):
        logger.error(f"يوتيوب: {new_stats['error']}")
        return
    
    old_stats = data.get("youtube", {})
    
    compare_and_notify("youtube", old_stats, new_stats, {
        "subscribers": "Subscribers",
        "videos": "Videos"
    })
    
    data["youtube"] = new_stats
    save_data(data)

def check_instagram():
    logger.info("فحص إنستغرام...")
    data = load_data()
    new_stats = get_instagram_stats()
    
    if new_stats.get("error"):
        logger.error(f"إنستغرام: {new_stats['error']}")
        return
    
    old_stats = data.get("instagram", {})
    
    compare_and_notify("instagram", old_stats, new_stats, {
        "followers": "Followers",
        "following": "Following",
        "posts": "Posts"
    })
    
    data["instagram"] = new_stats
    save_data(data)

def check_tiktok():
    logger.info("فحص تيك توك...")
    data = load_data()
    new_stats = get_tiktok_stats()
    
    if new_stats.get("error"):
        logger.error(f"تيك توك: {new_stats['error']}")
        return
    
    old_stats = data.get("tiktok", {})
    
    compare_and_notify("tiktok", old_stats, new_stats, {
        "followers": "Followers",
        "following": "Following",
        "likes": "Likes"
    })
    
    data["tiktok"] = new_stats
    save_data(data)

def check_roblox():
    logger.info("فحص روبلكس...")
    data = load_data()
    new_stats = get_roblox_stats()
    
    if new_stats.get("error"):
        logger.error(f"روبلكس: {new_stats['error']}")
        return
    
    old_stats = data.get("roblox", {})
    
    compare_and_notify("roblox", old_stats, new_stats, {
        "friends": "Friends",
        "followers": "Followers",
        "following": "Following",
        "badges": "Badges",
        "badges_list": "Badge Names",
        "groups": "Groups",
        "groups_list": "Group Names",
        "favorites": "Favorite Games",
        "favorites_list": "Favorite Game Names",
        "inventory": "Inventory Items"
    })
    
    data["roblox"] = new_stats
    save_data(data)

def check_telegram():
    logger.info("فحص تيليجرام...")
    data = load_data()
    new_stats = get_telegram_stats()
    
    if new_stats.get("error"):
        logger.error(f"تيليجرام: {new_stats['error']}")
        return
    
    old_stats = data.get("telegram", {})
    
    compare_and_notify("telegram", old_stats, new_stats, {
        "subscribers": "Subscribers",
        "photo_url": "Profile Photo"
    })
    
    data["telegram"] = new_stats
    save_data(data)

def check_pinterest():
    logger.info("فحص بنترست...")
    data = load_data()
    new_stats = get_pinterest_stats()
    
    if new_stats.get("error"):
        logger.error(f"بنترست: {new_stats['error']}")
        return
    
    old_stats = data.get("pinterest", {})
    
    compare_and_notify("pinterest", old_stats, new_stats, {
        "followers": "Followers",
        "following": "Following"
    })
    
    data["pinterest"] = new_stats
    save_data(data)

def check_all():
    """فحص جميع المنصات"""
    logger.info("=" * 50)
    logger.info(f"بدء الفحص الشامل: {datetime.datetime.now()}")
    logger.info("=" * 50)
    
    check_youtube()
    time.sleep(2)
    check_instagram()
    time.sleep(2)
    check_tiktok()
    time.sleep(2)
    check_roblox()
    time.sleep(2)
    check_telegram()
    time.sleep(2)
    check_pinterest()
    
    logger.info("انتهى الفحص الشامل")

# ===================== نقطة البداية =====================

if __name__ == "__main__":
    logger.info("🤖 بدء تشغيل بوت المراقبة...")
    
    # إرسال رسالة ترحيب
    send_telegram_message(
        "🤖 <b>بوت المراقبة يعمل الآن!</b>\n\n"
        "📊 سيتم مراقبة:\n"
        "▶️ YouTube\n"
        "📷 Instagram\n"
        "♪ TikTok\n"
        "🎮 Roblox\n"
        "✈️ Telegram\n"
        "📌 Pinterest\n\n"
        "⏰ يتم الفحص كل 30 دقيقة"
    )
    
    # تشغيل فحص أولي
    check_all()
    
    # إعداد الجدولة
    scheduler = BlockingScheduler()
    scheduler.add_job(check_all, 'interval', minutes=30, id='check_all')
    
    logger.info("⏰ الجدولة تعمل - فحص كل 30 دقيقة")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("تم إيقاف البوت")
