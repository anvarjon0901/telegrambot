"""
Stars Shop Bot - Utility Functions
Professional Version - 100% Working
"""
from datetime import datetime
from typing import Optional
import logging
import time

logger = logging.getLogger(__name__)


# ============ FORMATTING ============

def format_time(timestamp: int) -> str:
    """Format timestamp"""
    try:
        return datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y %H:%M")
    except:
        return "Unknown"


def format_date(timestamp: int) -> str:
    """Format date only"""
    try:
        return datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y")
    except:
        return "Unknown"


def format_money(amount: int) -> str:
    """Format money"""
    return f"{amount:,}".replace(",", " ")


def format_stars(amount: int) -> str:
    """Format stars"""
    return f"{amount} ⭐"


def get_username(user) -> str:
    """Get username"""
    if hasattr(user, 'username') and user.username:
        return f"@{user.username}"
    elif hasattr(user, 'full_name'):
        return user.full_name or "User"
    return "User"


# ============ VALIDATION ============

def validate_amount(amount: str, min_val: int = 1, max_val: int = 100000) -> Optional[int]:
    """Validate amount"""
    try:
        num = int(amount.strip())
        if min_val <= num <= max_val:
            return num
        return None
    except:
        return None


def validate_user_id(user_id: str) -> Optional[int]:
    """Validate user ID"""
    try:
        uid = int(user_id.strip())
        if uid > 0:
            return uid
        return None
    except:
        return None


# ============ CALCULATIONS ============

def calculate_price(amount: int, star_price: int, discount_percent: int = 0) -> dict:
    """Calculate price"""
    base_price = amount * star_price
    discount_amount = int(base_price * discount_percent / 100)
    final_price = base_price - discount_amount
    
    return {
        'base': base_price,
        'discount': discount_amount,
        'final': final_price,
        'discount_percent': discount_percent
    }


def calculate_referral_bonus(order_amount: int, bonus_percent: int) -> int:
    """Calculate referral bonus"""
    return int(order_amount * bonus_percent / 100)


def calculate_vip_expiry(current_time: int, duration_days: int) -> int:
    """Calculate VIP expiry time"""
    return current_time + (duration_days * 86400)


def is_vip_active(user_data: dict) -> bool:
    """Check if VIP is active"""
    if not user_data.get('is_vip'):
        return False
    
    vip_expires = user_data.get('vip_expires_at', 0)
    return vip_expires > int(time.time())


def get_vip_days_left(user_data: dict) -> int:
    """Get VIP days left"""
    if not is_vip_active(user_data):
        return 0
    
    vip_expires = user_data.get('vip_expires_at', 0)
    seconds_left = vip_expires - int(time.time())
    return max(0, seconds_left // 86400)


# ============ TEXT HELPERS ============

def generate_order_text(order: dict, user_data: dict = None) -> str:
    """Generate order text"""
    from config import DefaultSettings
    
    order_type_names = {
        'profile': 'Profil uchun Stars',
        'post': 'Post uchun Stars',
        'gift': 'Gift',
        'vip': 'VIP Obuna',
        'balance': "Balans to'ldirish"
    }
    
    status_emoji = {
        'pending': '⏳',
        'paid': '💸',
        'confirmed': '✅',
        'cancelled': '❌'
    }
    
    text = f"Buyurtma #{order['id']}\n\n"
    
    order_type = order_type_names.get(order['type'], order['type'])
    text += f"Turi: {order_type}\n"
    
    if order['type'] == 'gift' and order['detail']:
        gift_name = DefaultSettings.GIFT_NAMES.get(order['detail'], 'Gift')
        text += f"Gift: {gift_name}\n"
    
    if order['type'] != 'vip':
        text += f"Miqdor: {order['amount']} Stars\n"
    
    text += f"Narx: {format_money(order['price_per_star'])} so'm/Stars\n"
    
    if order['discount_percent'] > 0:
        text += f"Chegirma: {order['discount_percent']}%\n"
    
    text += f"Jami: {format_money(order['total_sum'])} so'm\n\n"
    
    status_text = {
        'pending': 'Kutilmoqda',
        'paid': "To'langan",
        'confirmed': 'Tasdiqlangan',
        'cancelled': 'Bekor qilingan'
    }
    
    emoji = status_emoji.get(order['status'], '❓')
    text += f"{emoji} Status: {status_text.get(order['status'], order['status'])}\n"
    
    text += f"Yaratilgan: {format_time(order['created_at'])}\n"
    
    if order['confirmed_at']:
        text += f"Tasdiqlangan: {format_time(order['confirmed_at'])}\n"
    
    payment_text = 'Bot hisobi' if order['payment_method'] == 'balance' else 'Karta'
    text += f"To'lov: {payment_text}\n"
    
    if order.get('admin_note'):
        text += f"\nIzoh: {order['admin_note']}\n"
    
    return text


def generate_user_profile_text(user_data: dict, settings: dict) -> str:
    """Generate user profile text"""
    text = f"PROFIL\n\n"
    
    text += f"ID: {user_data['user_id']}\n"
    
    if user_data['username']:
        text += f"Username: @{user_data['username']}\n"
    
    text += f"Ism: {user_data['full_name']}\n\n"
    
    text += f"Balans: {user_data['balance']} Stars\n"
    
    if is_vip_active(user_data):
        days_left = get_vip_days_left(user_data)
        text += f"Status: VIP ({days_left} kun qoldi)\n"
        text += f"Chegirma: {settings['vip_discount']}%\n"
    else:
        text += f"Status: Oddiy\n"
    
    text += f"\nReferal:\n"
    text += f"- Taklif qilganlar: {user_data.get('total_referrals', 0)} ta\n"
    text += f"- Jami topilgan: {user_data['total_earned_stars']} Stars\n"
    
    text += f"\nRo'yxatdan o'tgan: {format_time(user_data['created_at'])}\n"
    
    return text


def generate_stats_text(stats: dict, settings: dict) -> str:
    """Generate statistics text"""
    text = "UMUMIY STATISTIKA\n\n"
    
    text += "Foydalanuvchilar:\n"
    text += f"- Jami: {stats.get('total_users', 0)}\n"
    text += f"- VIP: {stats.get('vip_users', 0)}\n"
    
    if stats.get('total_users', 0) > 0:
        vip_percent = (stats.get('vip_users', 0) / stats.get('total_users', 1)) * 100
        text += f"- VIP foiz: {vip_percent:.1f}%\n"
    
    text += "\n"
    
    text += "Buyurtmalar:\n"
    text += f"- Jami: {stats.get('total_orders', 0)}\n"
    text += f"- Kutilmoqda: {stats.get('pending_orders', 0)}\n"
    text += f"- To'langan: {stats.get('paid_orders', 0)}\n"
    text += f"- Tasdiqlangan: {stats.get('confirmed_orders', 0)}\n\n"
    
    text += "Daromad:\n"
    text += f"- Jami: {format_money(stats.get('total_revenue', 0))} so'm\n\n"
    
    text += "Qo'llab-quvvatlash:\n"
    text += f"- Ochiq ticketlar: {stats.get('open_tickets', 0)}\n\n"
    
    text += "Sozlamalar:\n"
    text += f"- Stars narxi: {format_money(settings.get('star_price', 0))} so'm\n"
    text += f"- VIP chegirma: {settings.get('vip_discount', 0)}%\n"
    
    return text


# ============ REFERRAL HELPERS ============

def generate_referral_link(bot_username: str, referral_code: str) -> str:
    """Generate referral link"""
    return f"https://t.me/{bot_username}?start={referral_code}"


def parse_referral_code(start_payload: str) -> Optional[str]:
    """Parse referral code from start parameter"""
    if start_payload and start_payload.startswith('ref_'):
        return start_payload
    return None


# ============ ORDER HELPERS ============

def get_order_type_name(order_type: str) -> str:
    """Get order type name"""
    names = {
        'profile': 'Profil Stars',
        'post': 'Post Stars',
        'gift': 'Gift',
        'vip': 'VIP Obuna',
        'balance': 'Balans'
    }
    return names.get(order_type, order_type)


def get_payment_method_name(payment_method: str) -> str:
    """Get payment method name"""
    names = {
        'balance': 'Bot hisobi',
        'card': 'Karta orqali'
    }
    return names.get(payment_method, payment_method)
