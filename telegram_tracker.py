import requests
from bs4 import BeautifulSoup

def get_telegram_stats(username):
    try:
        url = f"https://t.me/{username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # البحث عن عدد المشتركين/الأعضاء إذا كانت قناة أو مجموعة
        subscribers_div = soup.find('div', class_='tgme_page_extra')
        
        # البحث عن صورة الحساب
        photo_meta = soup.find('meta', property='og:image')
        photo_url = photo_meta['content'] if photo_meta else None
        
        subscribers_text = subscribers_div.text if subscribers_div else "0"
        
        # استخراج الرقم من النص (مثال: "1,234 subscribers")
        import re
        numbers = re.findall(r'\d+', subscribers_text.replace(',', ''))
        count = int(numbers[0]) if numbers else 0
        
        return {
            "subscribers": count,
            "photo_url": photo_url,
            "error": None
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(get_telegram_stats("tulyx_v"))
