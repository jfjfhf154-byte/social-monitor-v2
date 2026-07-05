import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_roblox_stats(username):
    try:
        cookie = os.getenv("ROBLOX_COOKIE")
        cookies = {".ROBLOSECURITY": cookie}
        
        # 1. الحصول على User ID من اسم المستخدم
        user_response = requests.post(
            "https://users.roblox.com/v1/usernames/users",
            json={"usernames": [username], "excludeBannedUsers": True}
        )
        
        if user_response.status_code != 200 or not user_response.json().get("data"):
            return {"error": "لم يتم العثور على المستخدم"}
            
        user_id = user_response.json()["data"][0]["id"]
        
        # 2. جلب الأصدقاء
        friends_response = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/friends/count")
        friends_count = friends_response.json().get("count", 0)
        
        # 3. جلب المتابعين
        followers_response = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/followers/count")
        followers_count = followers_response.json().get("count", 0)
        
        # 4. جلب المتابَعين (following)
        following_response = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/followings/count")
        following_count = following_response.json().get("count", 0)
        
        # 5. جلب البادجات
        badges_response = requests.get(f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=100")
        badges_count = len(badges_response.json().get("data", []))
        
        # يمكن إضافة المزيد من البيانات لاحقاً
        
        return {
            "friends": friends_count,
            "followers": followers_count,
            "following": following_count,
            "badges": badges_count,
            "error": None
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(get_roblox_stats("qad4s"))
