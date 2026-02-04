"""
Stars Shop Bot - Keyboards
Professional Version - 100% Working
"""
from telebot import types
from typing import Optional, List


# ============ MAIN MENUS ============

def main_menu_kb(is_admin: bool = False) -> types.ReplyKeyboardMarkup:
    """Main menu keyboard"""
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    kb.add("⭐ Profil uchun Stars", "📝 Post uchun Stars")
    kb.add("🎁 Giftlar", "👑 VIP Obuna")
    kb.add("💼 Mening hisobim", "🔗 Referal tizimi")
    kb.add("ℹ️ Qanday ishlaydi", "📞 Admin bilan bog'lanish")
    
    if is_admin:
        kb.add("⚙️ Admin panel")
    
    return kb


def back_to_main_kb() -> types.ReplyKeyboardMarkup:
    """Back to main menu"""
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🏠 Asosiy menyu")
    return kb


# ============ QUANTITY KEYBOARDS ============

def quantity_kb(min_val: int = 50) -> types.InlineKeyboardMarkup:
    """Quantity selection keyboard"""
    kb = types.InlineKeyboardMarkup(row_width=3)
    
    quantities = [50, 100, 250, 500, 1000, 2000, 5000]
    buttons = [
        types.InlineKeyboardButton(f"{q}⭐", callback_data=f"qty:{q}")
        for q in quantities if q >= min_val
    ]
    
    kb.add(*buttons)
    kb.add(types.InlineKeyboardButton("♾ Boshqa miqdor", callback_data="qty:custom"))
    kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="back_to_main"))
    
    return kb


# ============ PAYMENT KEYBOARDS ============

def payment_method_kb(has_balance: bool = False, 
                     required_amount: int = 0) -> types.InlineKeyboardMarkup:
    """Payment method selection"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    
    if has_balance:
        kb.add(types.InlineKeyboardButton(
            f"💰 Bot hisobi ({required_amount}⭐)",
            callback_data="pay:balance"
        ))
    
    kb.add(types.InlineKeyboardButton(
        "💳 Karta orqali",
        callback_data="pay:card"
    ))
    
    kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="back_to_main"))
    
    return kb


# ============ GIFT KEYBOARDS ============

def gifts_kb(gift_prices: dict) -> types.InlineKeyboardMarkup:
    """Gifts keyboard"""
    from config import DefaultSettings
    
    kb = types.InlineKeyboardMarkup(row_width=2)
    
    for key, name in DefaultSettings.GIFT_NAMES.items():
        price = gift_prices.get(key, 50)
        kb.add(types.InlineKeyboardButton(
            f"{name.split()[0]} {price}⭐",
            callback_data=f"gift:{key}"
        ))
    
    kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="back_to_main"))
    
    return kb


# ============ VIP KEYBOARDS ============

def vip_packages_kb(vip_prices: dict, star_price: int) -> types.InlineKeyboardMarkup:
    """VIP packages"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    
    packages = {
        '1_month': '1 oy',
        '3_months': '3 oy',
        '6_months': '6 oy',
        '1_year': '1 yil'
    }
    
    for key, name in packages.items():
        price_sum = vip_prices.get(key, 0)
        kb.add(types.InlineKeyboardButton(
            f"{name} - {price_sum:,} so'm",
            callback_data=f"vip:{key}"
        ))
    
    kb.add(types.InlineKeyboardButton("ℹ️ VIP haqida", callback_data="vip:info"))
    kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="back_to_main"))
    
    return kb


# ============ PROFILE KEYBOARDS ============

def profile_kb(is_vip: bool = False) -> types.InlineKeyboardMarkup:
    """Profile keyboard"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    
    kb.row(
        types.InlineKeyboardButton("💳 Balansni to'ldirish", callback_data="profile:topup"),
        types.InlineKeyboardButton("📋 Buyurtmalar", callback_data="profile:orders")
    )
    
    kb.row(
        types.InlineKeyboardButton("📊 Tranzaksiyalar", callback_data="profile:transactions"),
        types.InlineKeyboardButton("🔗 Referal", callback_data="profile:referral")
    )
    
    if not is_vip:
        kb.add(types.InlineKeyboardButton("👑 VIP bo'lish", callback_data="profile:vip"))
    
    kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="back_to_main"))
    
    return kb


def balance_topup_kb() -> types.InlineKeyboardMarkup:
    """Balance topup keyboard"""
    kb = types.InlineKeyboardMarkup(row_width=3)
    
    amounts_sum = [10000, 25000, 50000, 100000, 250000, 500000]
    buttons = []
    
    for amount_sum in amounts_sum:
        stars = amount_sum // 1000
        buttons.append(
            types.InlineKeyboardButton(
                f"{amount_sum:,} so'm",
                callback_data=f"topup:{stars}"
            )
        )
    
    kb.add(*buttons)
    kb.add(types.InlineKeyboardButton("♾ Boshqa summa", callback_data="topup:custom"))
    kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="profile:back"))
    
    return kb


# ============ REFERRAL KEYBOARDS ============

def referral_kb(referral_link: str) -> types.InlineKeyboardMarkup:
    """Referral keyboard"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    
    kb.add(types.InlineKeyboardButton(
        "📤 Linkni ulashish",
        url=f"https://t.me/share/url?url={referral_link}&text=Stars Shop botiga qo'shiling!"
    ))
    
    kb.add(types.InlineKeyboardButton("📊 Statistika", callback_data="referral:stats"))
    kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="back_to_main"))
    
    return kb


# ============ ORDERS LIST KEYBOARDS ============

def order_detail_kb(order_id: int, status: str) -> types.InlineKeyboardMarkup:
    """Order detail keyboard"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    
    if status == 'pending':
        kb.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data=f"order:cancel:{order_id}"))
    
    kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="profile:orders"))
    
    return kb


# ============ ADMIN KEYBOARDS ============

def admin_main_kb() -> types.InlineKeyboardMarkup:
    """Admin main menu"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    
    kb.row(
        types.InlineKeyboardButton("📊 Statistika", callback_data="admin:stats"),
        types.InlineKeyboardButton("⚙️ Sozlamalar", callback_data="admin:settings")
    )
    
    kb.row(
        types.InlineKeyboardButton("🧾 Buyurtmalar", callback_data="admin:orders"),
        types.InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin:users")
    )
    
    kb.row(
        types.InlineKeyboardButton("💬 Qo'llab-quvvatlash", callback_data="admin:support"),
        types.InlineKeyboardButton("📨 Xabar yuborish", callback_data="admin:broadcast")
    )
    
    kb.row(
        types.InlineKeyboardButton("💳 Narxlar", callback_data="admin:prices"),
        types.InlineKeyboardButton("🎁 Bonuslar", callback_data="admin:bonuses")
    )
    
    return kb


def admin_orders_kb() -> types.InlineKeyboardMarkup:
    """Admin orders keyboard"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    
    kb.row(
        types.InlineKeyboardButton("⏳ Kutilmoqda", callback_data="orders:pending"),
        types.InlineKeyboardButton("💸 To'langan", callback_data="orders:paid")
    )
    
    kb.row(
        types.InlineKeyboardButton("✅ Tasdiqlangan", callback_data="orders:confirmed"),
        types.InlineKeyboardButton("❌ Bekor", callback_data="orders:cancelled")
    )
    
    kb.add(types.InlineKeyboardButton("📊 Barchasi", callback_data="orders:all"))
    kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="admin:back"))
    
    return kb


def admin_order_actions_kb(order_id: int, status: str) -> types.InlineKeyboardMarkup:
    """Admin order actions"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    
    if status == 'paid':
        kb.row(
            types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"order:confirm:{order_id}"),
            types.InlineKeyboardButton("❌ Rad etish", callback_data=f"order:reject:{order_id}")
        )
    
    kb.add(types.InlineKeyboardButton("👤 Foydalanuvchi", callback_data=f"order:user:{order_id}"))
    kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="admin:orders"))
    
    return kb


def admin_settings_kb() -> types.InlineKeyboardMarkup:
    """Admin settings"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    
    kb.row(
        types.InlineKeyboardButton("⭐ Stars narxi", callback_data="settings:star_price"),
        types.InlineKeyboardButton("👑 VIP sozlamalar", callback_data="settings:vip")
    )
    
    kb.row(
        types.InlineKeyboardButton("🔗 Referal", callback_data="settings:referral"),
        types.InlineKeyboardButton("🎁 Giftlar", callback_data="settings:gifts")
    )
    
    kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="admin:back"))
    
    return kb


def admin_user_actions_kb(user_id: int, is_vip: bool) -> types.InlineKeyboardMarkup:
    """Admin user actions"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    
    kb.row(
        types.InlineKeyboardButton("💰 Stars berish", callback_data=f"user:addstars:{user_id}"),
        types.InlineKeyboardButton("➖ Yechish", callback_data=f"user:deduct:{user_id}")
    )
    
    if is_vip:
        kb.add(types.InlineKeyboardButton("❌ VIP bekor qilish", callback_data=f"user:revoke_vip:{user_id}"))
    else:
        kb.add(types.InlineKeyboardButton("👑 VIP berish", callback_data=f"user:grant_vip:{user_id}"))
    
    kb.row(
        types.InlineKeyboardButton("📋 Buyurtmalar", callback_data=f"user:orders:{user_id}"),
        types.InlineKeyboardButton("📊 Tranzaksiyalar", callback_data=f"user:transactions:{user_id}")
    )
    
    kb.add(types.InlineKeyboardButton("📨 Xabar yuborish", callback_data=f"user:message:{user_id}"))
    kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="admin:users"))
    
    return kb


def admin_broadcast_kb() -> types.InlineKeyboardMarkup:
    """Admin broadcast"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    
    kb.row(
        types.InlineKeyboardButton("👥 Hammaga", callback_data="broadcast:all"),
        types.InlineKeyboardButton("👑 VIP larga", callback_data="broadcast:vip")
    )
    
    kb.add(types.InlineKeyboardButton("👤 ID bo'yicha", callback_data="broadcast:id"))
    kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="admin:back"))
    
    return kb


# ============ CONFIRMATION KEYBOARDS ============

def confirm_kb(action: str, data: str = "") -> types.InlineKeyboardMarkup:
    """Confirmation keyboard"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    
    kb.row(
        types.InlineKeyboardButton("✅ Ha", callback_data=f"confirm:{action}:{data}"),
        types.InlineKeyboardButton("❌ Yo'q", callback_data=f"cancel:{action}:{data}")
    )
    
    return kb


# ============ BACK BUTTONS ============

def back_kb(callback_data: str = "back_to_main") -> types.InlineKeyboardMarkup:
    """Back button"""
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data=callback_data))
    return kb


def cancel_button() -> types.InlineKeyboardMarkup:
    """Cancel button"""
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_action"))
    return kb
