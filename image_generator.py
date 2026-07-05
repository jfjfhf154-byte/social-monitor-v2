from PIL import Image, ImageDraw, ImageFont
import os
import datetime

# ألوان المنصات
PLATFORM_COLORS = {
    "youtube":   {"bg": "#FF0000", "text": "#FFFFFF", "accent": "#CC0000"},
    "instagram": {"bg": "#E1306C", "text": "#FFFFFF", "accent": "#833AB4"},
    "tiktok":    {"bg": "#010101", "text": "#FFFFFF", "accent": "#69C9D0"},
    "roblox":    {"bg": "#00A2FF", "text": "#FFFFFF", "accent": "#0077BB"},
    "telegram":  {"bg": "#0088CC", "text": "#FFFFFF", "accent": "#006699"},
    "pinterest": {"bg": "#E60023", "text": "#FFFFFF", "accent": "#AD081B"},
}

PLATFORM_ICONS = {
    "youtube":   "▶",
    "instagram": "📷",
    "tiktok":    "♪",
    "roblox":    "🎮",
    "telegram":  "✈",
    "pinterest": "📌",
}

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_notification_image(platform, changes, output_path=None):
    """
    إنشاء صورة إشعار بالتغييرات
    platform: اسم المنصة (youtube, instagram, etc.)
    changes: قائمة من التغييرات [{"label": "المتابعون", "old": 100, "new": 105, "change": "+5"}]
    """
    width, height = 800, 500
    
    colors = PLATFORM_COLORS.get(platform, {"bg": "#333333", "text": "#FFFFFF", "accent": "#555555"})
    icon = PLATFORM_ICONS.get(platform, "🔔")
    
    bg_color = hex_to_rgb(colors["bg"])
    accent_color = hex_to_rgb(colors["accent"])
    text_color = hex_to_rgb(colors["text"])
    
    # إنشاء الصورة
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # رسم شريط علوي
    draw.rectangle([0, 0, width, 80], fill=accent_color)
    
    # رسم شريط سفلي
    draw.rectangle([0, height-60, width, height], fill=accent_color)
    
    # محاولة تحميل خط عربي أو استخدام الخط الافتراضي
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large
        font_tiny = font_large
    
    # عنوان المنصة
    platform_name = platform.upper()
    draw.text((20, 20), f"{icon} {platform_name} - CHANGE DETECTED", font=font_large, fill=text_color)
    
    # التاريخ والوقت
    now = datetime.datetime.now()
    datetime_str = now.strftime("%Y-%m-%d  %H:%M:%S")
    draw.text((20, height-45), f"Date: {datetime_str}", font=font_small, fill=text_color)
    
    # رسم التغييرات
    y_pos = 110
    for change in changes:
        label = change.get("label", "")
        old_val = change.get("old", 0)
        new_val = change.get("new", 0)
        diff = change.get("change", "")
        
        # تحديد لون التغيير
        if isinstance(diff, str) and diff.startswith("+"):
            change_color = (0, 255, 100)  # أخضر للزيادة
            arrow = "▲"
        elif isinstance(diff, str) and diff.startswith("-"):
            change_color = (255, 100, 100)  # أحمر للنقصان
            arrow = "▼"
        else:
            change_color = (255, 255, 100)  # أصفر للتغيير المحايد
            arrow = "●"
        
        # رسم خلفية للتغيير
        draw.rectangle([20, y_pos-5, width-20, y_pos+55], fill=(*accent_color, 180), outline=text_color)
        
        # اسم الحقل
        draw.text((30, y_pos), label, font=font_medium, fill=text_color)
        
        # القيمة القديمة والجديدة
        draw.text((30, y_pos+28), f"{old_val}  {arrow}  {new_val}", font=font_medium, fill=change_color)
        
        # مقدار التغيير
        draw.text((width-120, y_pos+15), str(diff), font=font_large, fill=change_color)
        
        y_pos += 80
    
    # حفظ الصورة
    if output_path is None:
        output_path = f"/tmp/notification_{platform}_{now.strftime('%Y%m%d_%H%M%S')}.png"
    
    img.save(output_path)
    return output_path

if __name__ == "__main__":
    # اختبار
    test_changes = [
        {"label": "Followers", "old": 100, "new": 105, "change": "+5"},
        {"label": "Following", "old": 50, "new": 48, "change": "-2"},
    ]
    path = create_notification_image("instagram", test_changes, "/tmp/test_notification.png")
    print(f"تم إنشاء الصورة: {path}")
