"""
Stars Shop Bot - VIP Service
Professional Version - 100% Working
"""
import logging
import time
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class VIPService:
    """VIP management service"""
    
    @staticmethod
    def grant_vip(user_id: int, duration_key: str, settings: dict) -> Tuple[bool, str]:
        """Grant VIP"""
        try:
            from database import get_user, update_user
            from utils import calculate_vip_expiry, is_vip_active
            from config import Constants
            
            user = get_user(user_id)
            if not user:
                return False, "Foydalanuvchi topilmadi!"
            
            duration_days = Constants.VIP_DURATIONS.get(duration_key, 30)
            
            current_time = int(time.time())
            
            if is_vip_active(user):
                new_expiry = user['vip_expires_at'] + (duration_days * 86400)
            else:
                new_expiry = calculate_vip_expiry(current_time, duration_days)
            
            success = update_user(
                user_id,
                is_vip=1,
                vip_expires_at=new_expiry
            )
            
            if success:
                return True, f"VIP muvaffaqiyatli faollashtirildi! Muddat: {duration_days} kun"
            return False, "VIP berishda xato!"
            
        except Exception as e:
            logger.error(f"grant_vip error: {e}")
            return False, "Tizim xatosi!"
    
    
    @staticmethod
    def revoke_vip(user_id: int) -> Tuple[bool, str]:
        """Revoke VIP"""
        try:
            from database import get_user, update_user
            from utils import is_vip_active
            
            user = get_user(user_id)
            if not user:
                return False, "Foydalanuvchi topilmadi!"
            
            if not is_vip_active(user):
                return False, "Foydalanuvchi VIP emas!"
            
            success = update_user(
                user_id,
                is_vip=0,
                vip_expires_at=None
            )
            
            if success:
                return True, "VIP bekor qilindi!"
            return False, "VIP bekor qilishda xato!"
            
        except Exception as e:
            logger.error(f"revoke_vip error: {e}")
            return False, "Tizim xatosi!"
    
    
    @staticmethod
    def extend_vip(user_id: int, days: int) -> Tuple[bool, str]:
        """Extend VIP (Admin)"""
        try:
            from database import get_user, update_user
            from utils import calculate_vip_expiry, is_vip_active
            
            user = get_user(user_id)
            if not user:
                return False, "Foydalanuvchi topilmadi!"
            
            current_time = int(time.time())
            
            if is_vip_active(user):
                new_expiry = user['vip_expires_at'] + (days * 86400)
            else:
                new_expiry = calculate_vip_expiry(current_time, days)
            
            success = update_user(
                user_id,
                is_vip=1,
                vip_expires_at=new_expiry
            )
            
            if success:
                return True, f"VIP {days} kun uzaytirildi!"
            return False, "VIP uzaytirishda xato!"
            
        except Exception as e:
            logger.error(f"extend_vip error: {e}")
            return False, "Tizim xatosi!"
    
    
    @staticmethod
    def check_and_expire_vip(user_id: int) -> bool:
        """Check and expire VIP"""
        try:
            from database import get_user, update_user
            from utils import is_vip_active
            
            user = get_user(user_id)
            if not user or not user.get('is_vip'):
                return False
            
            if not is_vip_active(user):
                update_user(user_id, is_vip=0)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"check_and_expire_vip error: {e}")
            return False
    
    
    @staticmethod
    def get_vip_info(user_id: int, settings: dict) -> Dict[str, Any]:
        """Get VIP info"""
        try:
            from database import get_user
            from utils import is_vip_active, get_vip_days_left
            
            user = get_user(user_id)
            if not user:
                return {}
            
            info = {
                'is_vip': is_vip_active(user),
                'days_left': get_vip_days_left(user) if is_vip_active(user) else 0,
                'discount': settings['vip_discount'] if is_vip_active(user) else 0,
                'expires_at': user.get('vip_expires_at', 0)
            }
            
            return info
            
        except Exception as e:
            logger.error(f"get_vip_info error: {e}")
            return {}
