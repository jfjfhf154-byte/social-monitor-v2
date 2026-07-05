import requests
import json
import re
from bs4 import BeautifulSoup

def get_tiktok_stats(username):
    """جلب إحصائيات تيك توك باستخدام عدة طرق"""
    
    # الطريقة 1: صفحة الملف الشخصي بـ User-Agent موبايل
    try:
        url = f"https://www.tiktok.com/@{username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
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
                if 'followerCount' in user_stats:
                    return {
                        "followers": user_stats.get('followerCount', 0),
                        "following": user_stats.get('followingCount', 0),
                        "likes": user_stats.get('heartCount', 0),
                        "error": None
                    }
    except:
        pass
    
    # الطريقة 2: البحث في الميتا داتا
    try:
        url = f"https://www.tiktok.com/@{username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        
        if meta_desc:
            desc = meta_desc['content']
            
            def parse_short_num(s):
                if not s: return 0
                s = s.strip().replace(',', '')
                try:
                    if s[-1].upper() == 'K': return int(float(s[:-1]) * 1000)
                    if s[-1].upper() == 'M': return int(float(s[:-1]) * 1000000)
                    if s[-1].upper() == 'B': return int(float(s[:-1]) * 1000000000)
                    return int(float(s))
                except:
                    return 0
            
            followers_match = re.search(r'([\d,\.]+[KMBkmb]?)\s+Followers', desc, re.IGNORECASE)
            likes_match = re.search(r'([\d,\.]+[KMBkmb]?)\s+Likes', desc, re.IGNORECASE)
            
            if followers_match or likes_match:
                return {
                    "followers": parse_short_num(followers_match.group(1)) if followers_match else 0,
                    "following": 0,
                    "likes": parse_short_num(likes_match.group(1)) if likes_match else 0,
                    "error": None
                }
    except:
        pass
    
    # الطريقة 3: استخدام Scraptik أو API مجاني آخر
    try:
        url = f"https://scraptik.app/api/user?username={username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            user_info = data.get('userInfo', {}).get('stats', {})
            if user_info:
                return {
                    "followers": user_info.get('followerCount', 0),
                    "following": user_info.get('followingCount', 0),
                    "likes": user_info.get('heartCount', 0),
                    "error": None
                }
    except:
        pass
    
    return {"error": "لا يمكن جلب بيانات تيك توك (حماية نشطة)"}

if __name__ == "__main__":
    print(get_tiktok_stats("tulyx_v"))
