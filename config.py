"""
Stars Shop Bot - Configuration
Professional Version - 100% Working
"""
import os
from typing import Dict, Any


class Config:
    """Main configuration class"""
    
    # Bot settings
    BOT_TOKEN = os.getenv('BOT_TOKEN', '8428287396:AAFoOQEbA8uteR8h1yZeHX_P9S19DxfmVNY')
    
    # Admin ID - supports single or multiple admins
    # Single: ADMIN_ID=123456789
    # Multiple: ADMIN_ID=123456789,987654321,555666777
    _admin_env = os.getenv('ADMIN_ID', '7003178192')
    if ',' in _admin_env:
        # Multiple admins
        ADMIN_ID = [int(x.strip()) for x in _admin_env.split(',') if x.strip().isdigit()]
    else:
        # Single admin
        ADMIN_ID = int(_admin_env)
    
    # Payment details
    CARD_NUMBER = os.getenv('CARD_NUMBER', '9860160641183316')
    CARD_OWNER = os.getenv('CARD_OWNER', 'Toshboltayev ILHOMBEK')
    
    # Database
    DB_PATH = os.getenv('DB_PATH', 'stars_shop.db')
    
    # Rate limiting
    MAX_BROADCAST_PER_SECOND = 30
    MAX_REFERRALS_PER_DAY = 50
    
    # Cache TTL (seconds)
    CACHE_TTL = 300
    
    # Logging
    LOG_FILE = 'bot.log'
    LOG_LEVEL = 'INFO'
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN not set!")
        if not cls.ADMIN_ID:
            raise ValueError("ADMIN_ID not set!")
        
        # Ensure ADMIN_ID is list
        if isinstance(cls.ADMIN_ID, int):
            cls.ADMIN_ID = [cls.ADMIN_ID]
        
        return True


class Constants:
    """Constant values"""
    
    # Order statuses
    ORDER_STATUS = {
        'PENDING': 'pending',
        'PAID': 'paid',
        'CONFIRMED': 'confirmed',
        'CANCELLED': 'cancelled'
    }
    
    # Transaction types
    TRANSACTION_TYPES = {
        'REFERRAL_BONUS': 'referral_bonus',
        'PURCHASE': 'purchase',
        'ADMIN_ADD': 'admin_add',
        'ADMIN_DEDUCT': 'admin_deduct',
        'VIP_PURCHASE': 'vip_purchase'
    }
    
    # Order types
    ORDER_TYPES = {
        'PROFILE': 'profile',
        'POST': 'post',
        'GIFT': 'gift',
        'VIP': 'vip',
        'BALANCE': 'balance'
    }
    
    # Payment methods
    PAYMENT_METHODS = {
        'BALANCE': 'balance',
        'CARD': 'card'
    }
    
    # VIP durations (in days)
    VIP_DURATIONS = {
        '1_month': 30,
        '3_months': 90,
        '6_months': 180,
        '1_year': 365
    }
    
    # Support ticket statuses
    TICKET_STATUS = {
        'OPEN': 'open',
        'ANSWERED': 'answered',
        'CLOSED': 'closed'
    }
    
    # Emojis
    EMOJI = {
        'star': '⭐',
        'vip': '👑',
        'gift': '🎁',
        'money': '💰',
        'card': '💳',
        'check': '✅',
        'cross': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'link': '🔗',
        'profile': '👤',
        'admin': '👨‍💼',
        'support': '💬',
        'stats': '📊'
    }


class DefaultSettings:
    """Default settings"""
    
    # Base prices
    STAR_PRICE = 1000  # 1 Stars = 1000 som
    MIN_STARS = 50
    POST_MIN = 50
    
    # VIP settings
    VIP_DISCOUNT = 20  # Percent
    VIP_PRICES = {
        '1_month': 50000,
        '3_months': 120000,
        '6_months': 200000,
        '1_year': 350000
    }
    
    # Referral settings
    REFERRAL_BONUS_REGISTRATION = 10  # Stars
    REFERRAL_BONUS_FIRST_ORDER = 5    # Percent
    REFERRAL_BONUS_EVERY_ORDER = 2    # Percent
    
    # Gift prices (Stars)
    GIFT_PRICES = {
        'tree': 50,
        'heart': 15,
        'bear': 50,
        'box': 25,
        'rose': 25,
        'cake': 50,
        'bouquet': 50,
        'rocket': 50,
        'trophy': 100,
        'ring': 100,
        'diamond': 100,
        'champagne': 50
    }
    
    # Gift names
    GIFT_NAMES = {
        'tree': "🎄 Yangi Yil Archasi",
        'heart': "💝 Sevgi Yurak",
        'bear': "🧸 Sevimli Ayiq",
        'box': "🎁 Sirli Quti",
        'rose': "🌹 Qizil Gul",
        'cake': "🎂 Tug'ilgan kun Torti",
        'bouquet': "💐 Gul Bog'lam",
        'rocket': "🚀 Kosmik Raketa",
        'trophy': "🏆 G'olib Kubogi",
        'ring': "💍 Olmos Uzuk",
        'diamond': "💎 Qimmatbaho Olmos",
        'champagne': "🍾 Shampan Shishasi"
    }
    
    # Bonus settings
    BONUS_SETTINGS = {
        'registration': 0,
        'first_order': 0,
        'vip_monthly_bonus': 50,
        'birthday_bonus': 100
    }
    
    # Other
    FORCE_SUBSCRIPTION = False
    CHANNEL_ID = None
