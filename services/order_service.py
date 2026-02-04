"""
Stars Shop Bot - Order Service
Professional Version - 100% Working
"""
import logging
from typing import Optional, Tuple
import time

logger = logging.getLogger(__name__)


class OrderService:
    """Order management service"""
    
    @staticmethod
    def create_stars_order(user_id: int, order_type: str, amount: int,
                          settings: dict) -> Tuple[Optional[int], str]:
        """Create stars order"""
        try:
            from database import create_order, get_user
            from utils import calculate_price, is_vip_active
            
            user = get_user(user_id)
            if not user:
                return None, "Foydalanuvchi topilmadi!"
            
            min_amount = settings['min_stars'] if order_type == 'profile' else settings['post_min']
            if amount < min_amount:
                return None, f"Minimal miqdor: {min_amount} Stars"
            
            discount = settings['vip_discount'] if is_vip_active(user) else 0
            price_info = calculate_price(amount, settings['star_price'], discount)
            
            order_id = create_order(
                user_id=user_id,
                order_type=order_type,
                amount=amount,
                detail=None,
                price_per_star=settings['star_price'],
                discount_percent=discount,
                total_sum=price_info['final'],
                payment_method='pending'
            )
            
            if not order_id:
                return None, "Buyurtma yaratishda xato!"
            
            return order_id, "Buyurtma yaratildi!"
            
        except Exception as e:
            logger.error(f"create_stars_order error: {e}")
            return None, "Tizim xatosi!"
    
    
    @staticmethod
    def create_gift_order(user_id: int, gift_key: str, 
                         settings: dict) -> Tuple[Optional[int], str]:
        """Create gift order"""
        try:
            from database import create_order, get_user
            from utils import calculate_price, is_vip_active
            
            user = get_user(user_id)
            if not user:
                return None, "Foydalanuvchi topilmadi!"
            
            gift_prices = settings.get('gift_prices', {})
            amount = gift_prices.get(gift_key, 50)
            
            discount = settings['vip_discount'] if is_vip_active(user) else 0
            price_info = calculate_price(amount, settings['star_price'], discount)
            
            order_id = create_order(
                user_id=user_id,
                order_type='gift',
                amount=amount,
                detail=gift_key,
                price_per_star=settings['star_price'],
                discount_percent=discount,
                total_sum=price_info['final'],
                payment_method='pending'
            )
            
            if not order_id:
                return None, "Buyurtma yaratishda xato!"
            
            return order_id, "Gift buyurtmasi yaratildi!"
            
        except Exception as e:
            logger.error(f"create_gift_order error: {e}")
            return None, "Tizim xatosi!"
    
    
    @staticmethod
    def create_vip_order(user_id: int, duration_key: str,
                        settings: dict) -> Tuple[Optional[int], str]:
        """Create VIP order"""
        try:
            from database import create_order, get_user
            
            user = get_user(user_id)
            if not user:
                return None, "Foydalanuvchi topilmadi!"
            
            vip_prices = settings.get('vip_prices', {})
            total_sum = vip_prices.get(duration_key, 0)
            
            if total_sum == 0:
                return None, "Narx topilmadi!"
            
            order_id = create_order(
                user_id=user_id,
                order_type='vip',
                amount=1,
                detail=duration_key,
                price_per_star=total_sum,
                discount_percent=0,
                total_sum=total_sum,
                payment_method='pending'
            )
            
            if not order_id:
                return None, "Buyurtma yaratishda xato!"
            
            return order_id, "VIP buyurtmasi yaratildi!"
            
        except Exception as e:
            logger.error(f"create_vip_order error: {e}")
            return None, "Tizim xatosi!"
    
    
    @staticmethod
    def create_balance_topup_order(user_id: int, amount: int,
                                   settings: dict) -> Tuple[Optional[int], str]:
        """Create balance topup order"""
        try:
            from database import create_order, get_user
            
            user = get_user(user_id)
            if not user:
                return None, "Foydalanuvchi topilmadi!"
            
            if amount < 1:
                return None, "Minimal 1 Stars (1,000 so'm)"
            
            total_sum = amount * settings['star_price']
            
            order_id = create_order(
                user_id=user_id,
                order_type='balance',
                amount=amount,
                detail=None,
                price_per_star=settings['star_price'],
                discount_percent=0,
                total_sum=total_sum,
                payment_method='pending'
            )
            
            if not order_id:
                return None, "Buyurtma yaratishda xato!"
            
            return order_id, "Balans to'ldirish buyurtmasi yaratildi!"
            
        except Exception as e:
            logger.error(f"create_balance_topup_order error: {e}")
            return None, "Tizim xatosi!"
    
    
    @staticmethod
    def set_payment_method(order_id: int, payment_method: str) -> bool:
        """Set payment method"""
        try:
            from database import get_order, get_user, update_order
            
            order = get_order(order_id)
            if not order or order['status'] != 'pending':
                return False
            
            if payment_method == 'balance':
                user = get_user(order['user_id'])
                if not user:
                    return False
                
                required_stars = order['amount']
                
                if order['type'] == 'vip':
                    return False
                
                if user['balance'] < required_stars:
                    return False
            
            return update_order(order_id, payment_method=payment_method)
            
        except Exception as e:
            logger.error(f"set_payment_method error: {e}")
            return False
    
    
    @staticmethod
    def process_balance_payment(order_id: int) -> Tuple[bool, str]:
        """Process balance payment"""
        try:
            from database import get_order, get_user, update_order, update_balance
            from config import Constants
            
            order = get_order(order_id)
            if not order:
                return False, "Buyurtma topilmadi!"
            
            if order['payment_method'] != 'balance':
                return False, "To'lov usuli balans emas!"
            
            if order['status'] != 'pending':
                return False, "Buyurtma allaqachon ishlov berilgan!"
            
            user = get_user(order['user_id'])
            if not user:
                return False, "Foydalanuvchi topilmadi!"
            
            required = order['amount']
            
            if user['balance'] < required:
                return False, "Balansda yetarli Stars yo'q!"
            
            success = update_balance(
                user_id=order['user_id'],
                amount=-required,
                transaction_type=Constants.TRANSACTION_TYPES['PURCHASE'],
                description=f"Buyurtma #{order_id}",
                order_id=order_id
            )
            
            if not success:
                return False, "Balansdan yechishda xato!"
            
            update_order(order_id, status='confirmed', confirmed_at=int(time.time()))
            
            if order['type'] == 'balance':
                update_balance(
                    user_id=order['user_id'],
                    amount=order['amount'],
                    transaction_type=Constants.TRANSACTION_TYPES['PURCHASE'],
                    description=f"Balans to'ldirildi #{order_id}",
                    order_id=order_id
                )
            
            return True, "To'lov muvaffaqiyatli!"
            
        except Exception as e:
            logger.error(f"process_balance_payment error: {e}")
            return False, "Tizim xatosi!"
    
    
    @staticmethod
    def attach_payment_proof(order_id: int, message_id: int) -> Tuple[bool, str]:
        """Attach payment proof"""
        try:
            from database import get_order, update_order
            
            order = get_order(order_id)
            if not order:
                return False, "Buyurtma topilmadi!"
            
            if order['status'] != 'pending':
                return False, "Buyurtma allaqachon ishlov berilgan!"
            
            success = update_order(
                order_id,
                proof_msg_id=message_id,
                status='paid'
            )
            
            if success:
                return True, "Chek qabul qilindi! Admin tekshiradi."
            return False, "Xatolik yuz berdi!"
            
        except Exception as e:
            logger.error(f"attach_payment_proof error: {e}")
            return False, "Tizim xatosi!"
    
    
    @staticmethod
    def confirm_order(order_id: int, settings: dict) -> Tuple[bool, str]:
        """Confirm order (Admin)"""
        try:
            from database import get_order, update_order, update_balance
            from config import Constants
            
            order = get_order(order_id)
            if not order:
                return False, "Buyurtma topilmadi!"
            
            if order['status'] == 'confirmed':
                return False, "Buyurtma allaqachon tasdiqlangan!"
            
            if order['status'] != 'paid':
                return False, "Buyurtma to'lanmagan!"
            
            update_order(order_id, status='confirmed', confirmed_at=int(time.time()))
            
            if order['type'] in ['profile', 'post']:
                pass
            
            elif order['type'] == 'gift':
                pass
            
            elif order['type'] == 'vip':
                from services.vip_service import VIPService
                VIPService.grant_vip(order['user_id'], order['detail'], settings)
            
            elif order['type'] == 'balance':
                update_balance(
                    user_id=order['user_id'],
                    amount=order['amount'],
                    transaction_type=Constants.TRANSACTION_TYPES['PURCHASE'],
                    description=f"Balans to'ldirildi #{order_id}",
                    order_id=order_id
                )
            
            from services.referral_service import ReferralService
            ReferralService.process_order_bonus(order, settings)
            
            return True, "Buyurtma tasdiqlandi!"
            
        except Exception as e:
            logger.error(f"confirm_order error: {e}")
            return False, "Tizim xatosi!"
    
    
    @staticmethod
    def reject_order(order_id: int, reason: str) -> Tuple[bool, str]:
        """Reject order (Admin)"""
        try:
            from database import get_order, update_order
            
            order = get_order(order_id)
            if not order:
                return False, "Buyurtma topilmadi!"
            
            if order['status'] in ['confirmed', 'cancelled']:
                return False, "Buyurtmani rad etib bo'lmaydi!"
            
            update_order(
                order_id,
                status='cancelled',
                admin_note=reason
            )
            
            return True, "Buyurtma rad etildi!"
            
        except Exception as e:
            logger.error(f"reject_order error: {e}")
            return False, "Tizim xatosi!"
    
    
    @staticmethod
    def cancel_order(order_id: int, user_id: int) -> Tuple[bool, str]:
        """Cancel order (User)"""
        try:
            from database import get_order, update_order, update_balance
            from config import Constants
            
            order = get_order(order_id)
            if not order:
                return False, "Buyurtma topilmadi!"
            
            if order['user_id'] != user_id:
                return False, "Ruxsat yo'q!"
            
            if order['status'] not in ['pending', 'paid']:
                return False, "Bu buyurtmani bekor qilib bo'lmaydi!"
            
            update_order(order_id, status='cancelled', admin_note='Foydalanuvchi bekor qildi')
            
            if order['payment_method'] == 'balance' and order['status'] == 'paid':
                update_balance(
                    user_id=user_id,
                    amount=order['amount'],
                    transaction_type=Constants.TRANSACTION_TYPES['ADMIN_ADD'],
                    description=f"Buyurtma #{order_id} bekor qilindi",
                    order_id=order_id
                )
                return True, "Buyurtma bekor qilindi! Pul virtual hisobingizga qaytarildi."
            
            elif order['payment_method'] == 'card' and order['status'] == 'paid':
                stars_amount = order['total_sum'] // order['price_per_star']
                update_balance(
                    user_id=user_id,
                    amount=stars_amount,
                    transaction_type=Constants.TRANSACTION_TYPES['ADMIN_ADD'],
                    description=f"Buyurtma #{order_id} bekor qilindi (chek qaytarildi)",
                    order_id=order_id
                )
                return True, f"Buyurtma bekor qilindi! {stars_amount} Stars virtual hisobingizga qaytarildi."
            
            return True, "Buyurtma bekor qilindi!"
            
        except Exception as e:
            logger.error(f"cancel_order error: {e}")
            return False, "Tizim xatosi!"
