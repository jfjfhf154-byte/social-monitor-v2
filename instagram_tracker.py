import requests
import json
import re
import time

def get_instagram_stats(username):
    """جلب إحصائيات إنستغرام باستخدام عدة طرق"""
    
    # الطريقة 1: API الرسمي غير الرسمي
    try:
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
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
    except:
        pass
    
    # الطريقة 2: صفحة الملف الشخصي مباشرة
    try:
        url = f"https://www.instagram.com/{username}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Accept-Language": "en-US,en;q=0.9"
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        # البحث عن البيانات في الصفحة
        match = re.search(r'"edge_followed_by":\{"count":(\d+)\}', response.text)
        match2 = re.search(r'"edge_follow":\{"count":(\d+)\}', response.text)
        match3 = re.search(r'"edge_owner_to_timeline_media":\{"count":(\d+)', response.text)
        
        if match:
            return {
                "followers": int(match.group(1)),
                "following": int(match2.group(1)) if match2 else 0,
                "posts": int(match3.group(1)) if match3 else 0,
                "error": None
            }
    except:
        pass
    
    # الطريقة 3: استخدام خدمة مجانية بديلة
    try:
        url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            user = data.get('graphql', {}).get('user', {})
            if user:
                return {
                    "followers": user.get('edge_followed_by', {}).get('count', 0),
                    "following": user.get('edge_follow', {}).get('count', 0),
                    "posts": user.get('edge_owner_to_timeline_media', {}).get('count', 0),
                    "error": None
                }
    except:
        pass
    
    return {"error": "لا يمكن جلب بيانات إنستغرام (حماية نشطة)"}
