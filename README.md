# Social Media Tracker Bot 🤖

بوت مراقبة حسابات السوشيال ميديا يرسل إشعارات عبر تيليجرام عند حدوث أي تغيير.

## المنصات المدعومة

| المنصة | التغييرات المراقبة |
|--------|-------------------|
| YouTube | المشتركون، عدد المقاطع |
| Instagram | المتابعون، المتابَعون، المنشورات |
| TikTok | المتابعون، المتابَعون، الإعجابات |
| Roblox | الأصدقاء، المتابعون، المتابَعون، البادجات، المجموعات، المفضلة، الانفنتوري |
| Telegram | المشتركون، صورة الحساب |
| Pinterest | المتابعون، المتابَعون |

## المتغيرات البيئية المطلوبة

```
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
ROBLOX_COOKIE=your_roblox_cookie
YOUTUBE_URL=https://youtube.com/@your_channel
INSTAGRAM_USERNAME=your_username
TIKTOK_USERNAME=your_username
ROBLOX_USERNAME=your_username
TELEGRAM_USERNAME=your_username
PINTEREST_USERNAME=your_username
```

## التشغيل المحلي

```bash
pip install -r requirements.txt
python main.py
```

## النشر على Render

1. ارفع الكود على GitHub
2. أنشئ Worker service جديد على Render
3. أضف المتغيرات البيئية
4. انشر!
