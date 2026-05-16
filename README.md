# 🤖 NyteBot - بوت ديسكورد خاص بك

بوت ديسكورد متكامل يضم نظام الحماية، التذاكر، Giveaways، والإدارة — لسيرفرك فقط، بدون اشتراكات!

---

## ✨ الميزات

| الميزة | الأوامر |
|--------|---------|
| 🛡️ الحماية | Anti-Spam تلقائي، Anti-Raid تلقائي |
| 🎫 التذاكر | `/ticket-setup`, `/ticket-add`, `/ticket-remove` |
| 🎉 Giveaways | `/giveaway`, `/giveaway-list` |
| ⚡ الإدارة | `/ban`, `/kick`, `/mute`, `/unmute`, `/warn`, `/clear`, `/lock`, `/unlock` |

---

## 🚀 خطوات التشغيل

### الخطوة 1: إنشاء البوت على Discord

1. روح على [discord.com/developers/applications](https://discord.com/developers/applications)
2. اضغط **New Application** وسمّيه
3. روح لـ **Bot** من القائمة الجانبية
4. اضغط **Reset Token** وانسخ التوكن
5. فعّل كل الـ **Privileged Gateway Intents**:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
6. روح لـ **OAuth2 > URL Generator**:
   - اختر: `bot` + `applications.commands`
   - اختر الصلاحيات: `Administrator`
   - انسخ الرابط وأضف البوت لسيرفرك

---

### الخطوة 2: إعداد الملفات

افتح ملف `.env` وضع التوكن:
```
DISCORD_TOKEN=توكن_البوت_هنا
```

---

### الخطوة 3: الاستضافة على Railway (مجاني)

1. سجل على [railway.app](https://railway.app) بحساب GitHub
2. اضغط **New Project > Deploy from GitHub repo**
3. ارفع الملفات على GitHub أولاً (مجاني)
4. في Railway، روح لـ **Variables** وأضف:
   - `DISCORD_TOKEN` = توكنك
5. اضغط **Deploy** ✅

> **بديل:** تقدر تشغله على جهازك مباشرة (الخطوة 4)

---

### الخطوة 4: تشغيل محلي (اختياري)

```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل البوت
python bot.py
```

---

## ⚙️ إعداد التذاكر في السيرفر

1. اعمل **Category** اسمها `التذاكر`
2. اعمل **Role** اسمها `Support` أو `دعم` للستاف
3. شغّل الأمر `/ticket-setup` في القناة اللي تريدها

---

## 🛡️ إعدادات الحماية (في `cogs/protection.py`)

```python
self.SPAM_LIMIT = 5       # عدد الرسائل قبل الكتم
self.SPAM_WINDOW = 5      # النافذة الزمنية (ثواني)
self.SPAM_MUTE_MINUTES = 5 # مدة الكتم

self.RAID_JOIN_LIMIT = 8  # انضمامات تُفعّل وضع الريد
self.RAID_WINDOW = 10     # النافذة الزمنية (ثواني)
```

---

## 📁 هيكل الملفات

```
discord-bot/
├── bot.py                  # الملف الرئيسي
├── requirements.txt        # المتطلبات
├── .env                    # التوكن (لا ترفعه على GitHub!)
└── cogs/
    ├── moderation.py       # الإدارة
    ├── protection.py       # الحماية
    ├── tickets.py          # التذاكر
    └── giveaways.py        # Giveaways
```

---

## ⚠️ تنبيه مهم

لا ترفع ملف `.env` على GitHub أبداً!
أضف `.env` لملف `.gitignore`

---

صُنع بـ ❤️ خصيصًا لسيرفرك
