"""
Stars Shop Bot - Referral Service
Professional Version - 100% Working
"""
import logging
from typing import Optional, Dict, Any, Tuple, List

logger = logging.getLogger(__name__)


class ReferralService:
    """Referral management service"""
    
    @staticmethod
    def is_valid_language(language_code: Optional[str]) -> bool:
        """Check if language is Uzbek or Russian"""
        if not language_code:
            return False
        
        valid_languages = ['uz', 'ru']
        return language_code.lower() in valid_languages
    
    
    @staticmethod
    def is_cyrillic_or_latin(text: str) -> bool:
        """Check if text is Cyrillic or Latin"""
        if not text:
            return False
        
        cyrillic_chars = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюяғқҳўАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯҒҚҲЎ')
        latin_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        uzbek_chars = set('oʻgʻOʻGʻ')
        
        valid_chars = cyrillic_chars | latin_chars | uzbek_chars
        
        text_chars = [c for c in text if c.isalpha()]
        if not text_chars:
            return False
        
        valid_count = sum(1 for c in text_chars if c in valid_chars)
        return (valid_count / len(text_chars)) >= 0.5
    
    
    @staticmethod
    def can_be_referral(user_data: dict, language_code: Optional[str] = None) -> bool:
        """Check if user can be referral"""
        if language_code and ReferralService.is_valid_language(language_code):
            return True
        
        full_name = user_data.get('full_name', '')
        if ReferralService.is_cyrillic_or_latin(full_name):
            return True
        
        username = user_data.get('username', '')
        if username and ReferralService.is_cyrillic_or_latin(username):
            return True
        
        return False
    
    
    @staticmethod
    def process_order_bonus(order: dict, settings: dict) -> Tuple[bool, str]:
        """Process order bonus"""
        try:
            from database import get_user, update_user, update_balance, get_user_orders
            from config import Constants
            from utils import calculate_referral_bonus
            
            user = get_user(order['user_id'])
            if not user:
                return False, "Foydalanuvchi topilmadi!"
            
            referrer_id = user.get('referred_by')
            if not referrer_id:
                return False, "Referal yo'q"
            
            referrer = get_user(referrer_id)
            if not referrer:
                return False, "Referal egasi topilmadi!"
            
            user_orders = get_user_orders(user['user_id'], limit=100)
            confirmed_orders = [o for o in user_orders if o['status'] == 'confirmed']
            
            if len(confirmed_orders) > 1:
                return False, "Faqat birinchi buyurtmada bonus beriladi"
            
            bonus_percent = settings.get('referral_bonus_first_order', 5)
            bonus_amount = calculate_referral_bonus(order['amount'], bonus_percent)
            
            if bonus_amount < 1:
                bonus_amount = 1
            
            success = update_balance(
                user_id=referrer_id,
                amount=bonus_amount,
                transaction_type=Constants.TRANSACTION_TYPES['REFERRAL_BONUS'],
                description=f"Referal bonusi @{user.get('username', user['user_id'])} buyurtmasi uchun",
                order_id=order['id']
            )
            
            if not success:
                return False, "Bonus berishda xato!"
            
            update_user(
                referrer_id,
                total_earned_stars=referrer['total_earned_stars'] + bonus_amount
            )
            
            return True, f"Referal egasiga {bonus_amount} Stars bonus berildi!"
            
        except Exception as e:
            logger.error(f"process_order_bonus error: {e}")
            return False, "Tizim xatosi!"
    
    
    @staticmethod
    def get_referral_stats(user_id: int) -> Dict[str, Any]:
        """Get referral statistics"""
        try:
            from database import get_user, get_referrals, get_user_orders
            
            user = get_user(user_id)
            if not user:
                return {}
            
            referral_code = user.get('referral_code', f"ref_{user_id}")
            
            referrals = get_referrals(user_id)
            
            active_referrals = []
            for ref in referrals:
                orders = get_user_orders(ref['user_id'], limit=1)
                if orders:
                    active_referrals.append(ref)
            
            stats = {
                'referral_code': referral_code,
                'total_referrals': len(referrals),
                'active_referrals': len(active_referrals),
                'total_earned': user.get('total_earned_stars', 0)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"get_referral_stats error: {e}")
            return {}
    
    
    @staticmethod
    def get_referral_list(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get referral list"""
        try:
            from database import get_referrals, get_user_orders
            
            referrals = get_referrals(user_id)
            
            result = []
            for ref in referrals[:limit]:
                orders = get_user_orders(ref['user_id'])
                confirmed = [o for o in orders if o['status'] == 'confirmed']
                
                result.append({
                    'user_id': ref['user_id'],
                    'username': ref.get('username'),
                    'full_name': ref.get('full_name'),
                    'total_orders': len(confirmed),
                    'joined_at': ref.get('created_at')
                })
            
            return result
            
        except Exception as e:
            logger.error(f"get_referral_list error: {e}")
            return []
