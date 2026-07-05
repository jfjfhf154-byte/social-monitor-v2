import requests
from bs4 import BeautifulSoup
import json

def get_pinterest_stats(username):
    try:
        url = f"https://www.pinterest.com/{username}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        response = requests.get(url, headers=headers)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # محاولة البحث عن البيانات في الميتا داتا
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            desc = meta_desc['content']
            # عادة يكون الوصف بهذا الشكل: "See what Username (username) has discovered on Pinterest, the world's biggest collection of ideas. - 100 followers, 50 following"
            import re
            
            followers_match = re.search(r'([\d,]+)\s+followers?', desc, re.IGNORECASE)
            following_match = re.search(r'([\d,]+)\s+following', desc, re.IGNORECASE)
            
            followers = int(followers_match.group(1).replace(',', '')) if followers_match else 0
            following = int(following_match.group(1).replace(',', '')) if following_match else 0
            
            return {
                "followers": followers,
                "following": following,
                "error": None
            }
            
        return {"error": "لم يتم العثور على البيانات"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(get_pinterest_stats("tulyx_v"))
