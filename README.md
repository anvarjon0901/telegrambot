# 🌟 Stars Shop Bot - Professional Edition

**100% Ishlaydigan Professional Telegram Bot** - Telegram Stars sotish uchun to'liq funktsional tizim.

## ✨ Asosiy Funksiyalar

### 👤 Foydalanuvchi Funksiyalari
- ⭐ **Profil/Post uchun Stars** - Sotib olish
- 🎁 **Giftlar** - 12 xil turli gift
- 👑 **VIP Obuna** - Chegirmalar va bonuslar
- 💰 **Ichki Balans Tizimi** - Virtual Stars hisobi
- 🔗 **Referal Tizimi** - Do'stlarni taklif qiling va bonus oling
- 📞 **Admin Bilan Aloqa** - Support ticket tizimi
- 📋 **Buyurtmalar Tarixi** - Barcha buyurtmalarni ko'rish
- 💳 **2 Xil To'lov** - Bot hisobi yoki Karta

### 👨‍💼 Admin Funksiyalari
- 🧾 **Buyurtmalarni Boshqarish** - Tasdiqlash/Rad etish
- 💰 **Balans Boshqarish** - Qo'shish/Yechish
- 👑 **VIP Boshqarish** - Berish/Bekor qilish
- 📊 **Real-time Statistika** - Onlayn ko'rsatkichlar
- 📨 **Broadcast** - Hammaga/VIP larga xabar
- 💬 **Support Ticketlar** - Foydalanuvchilar bilan muloqot
- ⚙️ **Sozlamalar** - Narxlar, chegirmalar
- 👥 **Ko'p Admin** - Bir nechta admin qo'shish

## 🚀 O'rnatish va Ishga Tushirish

### 1. Talablar
- Python 3.8+
- pip (Python package manager)
- Telegram Bot Token (@BotFather dan oling)
- O'zingizning Telegram ID

### 2. Loyihani Yuklab Olish
```bash
# Clone the repository
git clone <repository_url>
cd stars_shop_bot

# Or download as ZIP and extract
```

### 3. Virtual Environment Yaratish (Tavsiya etiladi)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 4. Dependency'larni O'rnatish
```bash
pip install -r requirements.txt
```

### 5. Environment Variables Sozlash
```bash
# .env.example dan .env yaratish
cp .env.example .env

# .env faylini tahrirlash
nano .env  # yoki istalgan text editor
```

**.env fayliga quyidagilarni kiriting:**
```env
BOT_TOKEN=8428287396:AAFoOQEbA8uteR8h1yZeHX_P9S19DxfmVNY
ADMIN_ID=7003178192
CARD_NUMBER=9860160641183316
CARD_OWNER=Toshboltayev ILHOMBEK
```

**KO'P ADMIN qo'shish uchun:**
```env
# Vergul bilan ajrating
ADMIN_ID=7003178192,123456789,987654321
```

### 6. Botni Ishga Tushirish
```bash
python main.py
```

Muvaffaqiyatli ishga tushsa, quyidagi ko'rinishda chiqadi:
```
============================================================
🌟 STARS SHOP BOT - PROFESSIONAL VERSION
============================================================
📅 Started: 03.02.2026 15:30:45
👨‍💼 Admin ID: 7003178192
💳 Card: 9860160641183316
============================================================
✅ Configuration validated
✅ Database initialized
✅ Bot created
✅ Admin handlers registered
✅ User handlers registered
✅ Bot ready: @YourBotUsername
============================================================
🤖 Bot polling started: @YourBotUsername
⏸️  Stop with: Ctrl+C
============================================================
```

## 📊 Loyiha Strukturasi

```
stars_shop_bot/
├── config.py              # Konfiguratsiya va sozlamalar
├── database.py            # Database operations
├── utils.py               # Yordamchi funksiyalar
├── keyboards.py           # Telegram klaviaturalar
├── services/
│   ├── __init__.py
│   ├── order_service.py   # Buyurtma logikasi
│   ├── vip_service.py     # VIP logikasi
│   └── referral_service.py # Referal logikasi
├── handlers/
│   ├── __init__.py
│   ├── user_handlers.py   # Foydalanuvchi handlerlari
│   └── admin_handlers.py  # Admin handlerlari
├── main.py                # Entry point
├── .env                   # Environment variables (yaratiladi)
├── .env.example           # Environment example
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # Bu fayl
```

## 🎯 Asosiy Komandalar

### Foydalanuvchi Komandalar
- `/start` - Botni boshlash
- `/help` - Yordam

### Admin Komandalar
```bash
# Buyurtmalar
/confirm <order_id>              # Buyurtmani tasdiqlash
/reject <order_id> <sabab>       # Buyurtmani rad etish

# Balans
/addstars <user_id> <amount>     # Stars qo'shish
/deductstars <user_id> <amount>  # Stars yechish

# VIP
/vipgrant <user_id> <days>       # VIP berish
/viprevoke <user_id>             # VIP bekor qilish

# Statistika
/stats                           # Umumiy statistika
/admins                          # Admin ro'yxati

# Support
/reply <ticket_id> <javob>       # Ticketga javob

# Broadcast
/broadcast                       # Xabar yuborish (keyin matn)
```

## ⚙️ Sozlamalar

### Narxlar (config.py ichida)
```python
STAR_PRICE = 1000          # 1 Stars = 1000 so'm
MIN_STARS = 50             # Minimal miqdor
POST_MIN = 50              # Post uchun minimal
VIP_DISCOUNT = 20          # VIP chegirma (%)
```

### VIP Paketlar
| Muddat | Narx |
|--------|------|
| 1 oy   | 50,000 so'm |
| 3 oy   | 120,000 so'm |
| 6 oy   | 200,000 so'm |
| 1 yil  | 350,000 so'm |

### Gift Narxlari
| Gift | Stars |
|------|-------|
| 🎄 Archa | 50 |
| 💝 Yurak | 15 |
| 🧸 Ayiq | 50 |
| 🎁 Quti | 25 |
| 🌹 Gul | 25 |
| 🎂 Tort | 50 |
| 💐 Gul Bog'lam | 50 |
| 🚀 Raketa | 50 |
| 🏆 Kubok | 100 |
| 💍 Uzuk | 100 |
| 💎 Olmos | 100 |
| 🍾 Shampan | 50 |

### Referal Tizimi
- ✅ Faqat O'zbek/Rus foydalanuvchilar
- ✅ Bonus: Birinchi buyurtmada 5%
- ✅ Avtomatik bonus berish

## 🔐 Xavfsizlik

### Environment Variables
- ✅ Token va Admin ID `.env` da
- ✅ `.env` `.gitignore` da
- ❌ Hech qachon commit qilmang

### Database
- ✅ SQLite local faylda
- ✅ Backup muntazam oling
- ✅ SQL injection himoyasi

### Input Validation
- ✅ Barcha inputlar tekshiriladi
- ✅ Min/Max limitlar
- ✅ Type checking

## 📝 Database Strukturasi

### Users Table
```sql
- user_id (PRIMARY KEY)
- username
- full_name
- balance (Stars)
- is_vip (boolean)
- vip_expires_at (timestamp)
- referral_code
- referred_by
- total_earned_stars
- created_at
- last_active
```

### Orders Table
```sql
- id (PRIMARY KEY)
- user_id
- type (profile/post/gift/vip/balance)
- amount
- detail
- price_per_star
- discount_percent
- total_sum
- payment_method (balance/card)
- status (pending/paid/confirmed/cancelled)
- created_at
- confirmed_at
- proof_msg_id
- admin_note
```

### Transactions Table
```sql
- id (PRIMARY KEY)
- user_id
- type (referral_bonus/purchase/admin_add/admin_deduct)
- amount
- description
- order_id
- created_at
```

### Support Tickets Table
```sql
- id (PRIMARY KEY)
- user_id
- status (open/answered/closed)
- created_at
- closed_at
```

## 🆘 Muammolarni Hal Qilish

### Bot ishlamayapti
```bash
# Loglarni tekshiring
tail -f bot.log

# Token to'g'riligini tekshiring
cat .env | grep BOT_TOKEN

# Dependency'larni qayta o'rnating
pip install -r requirements.txt --force-reinstall
```

### Database xatosi
```bash
# Database backup
cp stars_shop.db stars_shop.db.backup

# Qayta init
rm stars_shop.db
python main.py
```

### Module topilmadi
```bash
# Virtual environment faol ekanligini tekshiring
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Dependencies qayta o'rnating
pip install -r requirements.txt
```

### Bot javob bermayapti
1. Bot tokenini tekshiring (@BotFather)
2. Admin ID to'g'riligini tekshiring
3. Internet aloqasini tekshiring
4. Loglarni o'qing (`bot.log`)

## 🔄 Yangilanishlar

### Yangilanishni O'rnatish
```bash
# Git orqali
git pull origin main

# Dependencies yangilash
pip install -r requirements.txt --upgrade

# Botni qayta ishga tushirish
python main.py
```

## 📞 Qo'llab-quvvatlash

Muammo yoki savol bo'lsa:
1. `bot.log` faylini tekshiring
2. Issue oching GitHub da
3. Admin bilan bog'laning

## 📜 Litsenziya

MIT License - O'zingiz uchun erkin foydalaning!

## 🙏 Minnatdorchilik

- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) - Telegram Bot API wrapper
- SQLite - Database
- Python Community

## 👨‍💻 Muallif

Professional Bot Developer
Sana: 2026

---

## ⭐ Agar Foydali Bo'lsa

Agar bu bot sizga foydali bo'lsa:
- ⭐ Star bering GitHub da
- 🔄 Share qiling do'stlaringiz bilan
- 💬 Feedback bering

---

**🌟 STARS SHOP BOT - 100% PROFESSIONAL - 100% WORKING**
