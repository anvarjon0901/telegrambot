# 🚀 QUICK START GUIDE - Stars Shop Bot

## 5 Daqiqada Ishga Tushiring!

### 📋 Kerak Bo'lgan Narsalar
- Python 3.8 yoki yuqorisi
- Telegram Bot Token
- O'zingizning Telegram ID

---

## ⚡ Tezkor O'rnatish

### 1️⃣ Bot Token Olish
1. Telegram da [@BotFather](https://t.me/BotFather) ga boring
2. `/newbot` yuboring
3. Bot nomi va username kiriting
4. Token ni nusxalang (masalan: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 2️⃣ O'z ID ni Bilish
1. Telegram da [@userinfobot](https://t.me/userinfobot) ga boring
2. Bot sizga ID ni ko'rsatadi (masalan: `123456789`)

### 3️⃣ Botni O'rnatish

**Windows:**
```cmd
# 1. Papkaga kiring
cd stars_shop_bot

# 2. Virtual environment yarating
python -m venv venv
venv\Scripts\activate

# 3. Dependency'larni o'rnating
pip install -r requirements.txt

# 4. .env faylini yarating
copy .env.example .env

# 5. .env ni tahrirlang (Notepad bilan)
notepad .env
```

**Linux/Mac:**
```bash
# 1. Papkaga kiring
cd stars_shop_bot

# 2. Virtual environment yarating
python3 -m venv venv
source venv/bin/activate

# 3. Dependency'larni o'rnating
pip install -r requirements.txt

# 4. .env faylini yarating
cp .env.example .env

# 5. .env ni tahrirlang
nano .env
```

### 4️⃣ .env Faylini To'ldirish

`.env` faylida quyidagilarni o'zgartiring:

```env
# O'z tokeningizni kiriting
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# O'z ID ingizni kiriting
ADMIN_ID=123456789

# Ko'p admin qo'shish uchun vergul bilan ajrating
# ADMIN_ID=123456789,987654321,555666777

# Karta ma'lumotlarini kiriting
CARD_NUMBER=9860160641183316
CARD_OWNER=Toshboltayev ILHOMBEK
```

### 5️⃣ Botni Ishga Tushiring

```bash
python main.py
```

Muvaffaqiyat! 🎉

---

## 📱 Botni Sinab Ko'ring

1. Telegram da botingizni toping
2. `/start` yuboring
3. Admin sifatida "⚙️ Admin panel" tugmasini ko'rasiz

---

## 🎯 Birinchi Buyurtma

### Foydalanuvchi Sifatida:
1. "⭐ Profil uchun Stars" bosing
2. Miqdor tanlang
3. To'lov usulini tanlang
4. Chekni yuboring

### Admin Sifatida:
1. Bot sizga xabar yuboradi
2. `/confirm <order_id>` yuboring
3. Foydalanuvchi tasdiqlash xabarini oladi

---

## ⚙️ Asosiy Sozlamalar

### Narxlarni O'zgartirish
`config.py` faylida:

```python
STAR_PRICE = 1000      # 1 Stars = 1000 so'm
MIN_STARS = 50         # Minimal miqdor
VIP_DISCOUNT = 20      # VIP chegirma 20%
```

### VIP Narxlarini O'zgartirish
`config.py` faylida:

```python
VIP_PRICES = {
    '1_month': 50000,    # 1 oy
    '3_months': 120000,  # 3 oy
    '6_months': 200000,  # 6 oy
    '1_year': 350000     # 1 yil
}
```

---

## 🔧 Foydali Komandalar

### Buyurtmalarni Boshqarish
```bash
/confirm 123        # Buyurtma 123 ni tasdiqlash
/reject 123 xato    # Buyurtma 123 ni rad etish
```

### Balansni Boshqarish
```bash
/addstars 123456789 100      # 100 Stars qo'shish
/deductstars 123456789 50    # 50 Stars yechish
```

### VIP Berish
```bash
/vipgrant 123456789 30    # 30 kun VIP berish
/viprevoke 123456789      # VIP bekor qilish
```

### Statistika
```bash
/stats     # Umumiy statistika
/admins    # Admin ro'yxati
```

---

## 🆘 Tez-tez So'raladigan Savollar

### ❓ Bot ishlamayapti?
**Javob:** 
1. Token to'g'riligini tekshiring
2. Python 3.8+ o'rnatilganligini tekshiring
3. `bot.log` faylini o'qing

### ❓ Admin panel ko'rinmayapti?
**Javob:**
1. `.env` dagi `ADMIN_ID` to'g'riligini tekshiring
2. Botni qayta ishga tushiring
3. `/start` ni qaytadan bosing

### ❓ Database xatosi?
**Javob:**
```bash
rm stars_shop.db
python main.py
```

### ❓ Bir nechta admin qo'shish?
**Javob:**
`.env` da:
```env
ADMIN_ID=123456789,987654321,555666777
```

---

## 📞 Qo'shimcha Yordam

- 📖 To'liq qo'llanma: `README.md`
- 📝 Loglar: `bot.log`
- 🐛 Muammolar: GitHub Issues

---

## ✅ Checklist

- [ ] Python 3.8+ o'rnatilgan
- [ ] Bot Token olindi
- [ ] O'z ID bilinadi
- [ ] Virtual environment yaratildi
- [ ] Dependencies o'rnatildi
- [ ] `.env` fayli to'ldirildi
- [ ] Bot ishga tushirildi
- [ ] Admin panel ishlayapti

---

**🎉 Muvaffaqiyat! Botingiz tayyor!**

Agar savollar bo'lsa, `README.md` ni o'qing yoki admin bilan bog'laning.
