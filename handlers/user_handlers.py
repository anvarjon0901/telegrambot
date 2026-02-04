"""
Stars Shop Bot - User Handlers
Professional Version - 100% Working - COMPLETE
"""
import logging
import time
from telebot import TeleBot, types

logger = logging.getLogger(__name__)

user_states = {}


def register_user_handlers(bot: TeleBot):
    """Register all user handlers"""
    
    @bot.message_handler(commands=['start', 'help'])
    def start_handler(message: types.Message):
        """Start command handler"""
        try:
            from config import Config
            from database import create_user, get_user, update_user, get_user_by_referral, get_settings
            from keyboards import main_menu_kb
            from utils import parse_referral_code
            
            user = message.from_user
            referrer_id = None
            
            if message.text.startswith('/start '):
                try:
                    payload = message.text.split(' ', 1)[1]
                    ref_code = parse_referral_code(payload)
                    if ref_code:
                        referrer = get_user_by_referral(ref_code)
                        if referrer and referrer['user_id'] != user.id:
                            referrer_id = referrer['user_id']
                except:
                    pass
            
            existing_user = get_user(user.id)
            if not existing_user:
                full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                if not full_name:
                    full_name = "Foydalanuvchi"
                
                create_user(user.id, user.username, full_name, referrer_id)
                
                if referrer_id:
                    try:
                        username = f"@{user.username}" if user.username else "Foydalanuvchi"
                        bot.send_message(referrer_id, f"🎉 Yangi referal: {username}")
                    except Exception as e:
                        logger.error(f"Referrer notification error: {e}")
            else:
                update_user(user.id, last_active=int(time.time()))
            
            settings = get_settings()
            welcome_text = (
                "🌟 Stars Shop botiga xush kelibsiz!\n\n"
                "📌 Xizmatlar:\n"
                "• ⭐ Profil uchun Stars\n"
                "• 📝 Post uchun Stars\n"
                "• 🎁 Giftlar\n"
                "• 👑 VIP obuna\n\n"
                f"💎 Narx: 1 Stars = {settings['star_price']:,} so'm\n\n"
                "👇 Quyidagi tugmalardan foydalaning:"
            )
            
            is_admin = user.id in (Config.ADMIN_ID if isinstance(Config.ADMIN_ID, list) else [Config.ADMIN_ID])
            bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu_kb(is_admin))
            
        except Exception as e:
            logger.error(f"start_handler error: {e}", exc_info=True)
            bot.send_message(message.chat.id, "❗ Xatolik yuz berdi!")
    
    
    @bot.message_handler(func=lambda m: m.text == "⭐ Profil uchun Stars")
    def profile_stars_handler(message: types.Message):
        """Profile stars handler"""
        try:
            from database import get_settings
            from keyboards import quantity_kb
            
            settings = get_settings()
            text = (
                f"⭐ Profil uchun Stars\n\n"
                f"Minimal: {settings['min_stars']} Stars\n"
                f"Miqdorni tanlang:"
            )
            bot.send_message(
                message.chat.id, 
                text, 
                reply_markup=quantity_kb(settings['min_stars'])
            )
            user_states[message.from_user.id] = {'action': 'profile_stars'}
        except Exception as e:
            logger.error(f"profile_stars error: {e}")
            bot.reply_to(message, "❗ Xatolik!")
    
    
    @bot.message_handler(func=lambda m: m.text == "📝 Post uchun Stars")
    def post_stars_handler(message: types.Message):
        """Post stars handler"""
        try:
            from database import get_settings
            from keyboards import quantity_kb
            
            settings = get_settings()
            text = (
                f"📝 Post uchun Stars\n\n"
                f"Minimal: {settings['post_min']} Stars\n"
                f"Miqdorni tanlang:"
            )
            bot.send_message(
                message.chat.id, 
                text, 
                reply_markup=quantity_kb(settings['post_min'])
            )
            user_states[message.from_user.id] = {'action': 'post_stars'}
        except Exception as e:
            logger.error(f"post_stars error: {e}")
            bot.reply_to(message, "❗ Xatolik!")
    
    
    @bot.message_handler(func=lambda m: m.text == "🎁 Giftlar")
    def gifts_handler(message: types.Message):
        """Gifts handler"""
        try:
            from database import get_settings
            from keyboards import gifts_kb
            
            settings = get_settings()
            text = "🎁 Giftlar ro'yxati:\n\nGift tanlang:"
            bot.send_message(
                message.chat.id, 
                text, 
                reply_markup=gifts_kb(settings['gift_prices'])
            )
        except Exception as e:
            logger.error(f"gifts error: {e}")
            bot.reply_to(message, "❗ Xatolik!")
    
    
    @bot.message_handler(func=lambda m: m.text == "👑 VIP Obuna")
    def vip_handler(message: types.Message):
        """VIP subscription handler"""
        try:
            from database import get_settings
            from keyboards import vip_packages_kb
            from services.vip_service import VIPService
            
            settings = get_settings()
            vip_info = VIPService.get_vip_info(message.from_user.id, settings)
            
            if vip_info.get('is_vip'):
                text = (
                    f"👑 VIP Status\n\n"
                    f"Qolgan muddat: {vip_info['days_left']} kun\n"
                    f"Chegirma: {vip_info['discount']}%\n\n"
                    "Yangi paket tanlang:"
                )
            else:
                text = (
                    f"👑 VIP OBUNA\n\n"
                    f"Chegirma: {settings['vip_discount']}%\n\n"
                    "Paket tanlang:"
                )
            
            bot.send_message(
                message.chat.id, 
                text, 
                reply_markup=vip_packages_kb(settings['vip_prices'], settings['star_price'])
            )
        except Exception as e:
            logger.error(f"vip error: {e}")
            bot.reply_to(message, "❗ Xatolik!")
    
    
    @bot.message_handler(func=lambda m: m.text == "💼 Mening hisobim")
    def my_account_handler(message: types.Message):
        """My account handler"""
        try:
            from database import get_user, get_settings
            from keyboards import profile_kb
            from utils import generate_user_profile_text, is_vip_active
            from services.referral_service import ReferralService
            
            user = get_user(message.from_user.id)
            if not user:
                bot.reply_to(message, "❗ Foydalanuvchi topilmadi!")
                return
            
            settings = get_settings()
            ref_stats = ReferralService.get_referral_stats(user['user_id'])
            user['total_referrals'] = ref_stats.get('total_referrals', 0)
            
            text = generate_user_profile_text(user, settings)
            bot.send_message(
                message.chat.id, 
                text, 
                reply_markup=profile_kb(is_vip_active(user))
            )
        except Exception as e:
            logger.error(f"my_account error: {e}")
            bot.reply_to(message, "❗ Xatolik!")
    
    
    @bot.message_handler(func=lambda m: m.text == "🔗 Referal tizimi")
    def referral_handler(message: types.Message):
        """Referral system handler"""
        try:
            from database import get_user
            from keyboards import referral_kb
            from utils import generate_referral_link
            from services.referral_service import ReferralService
            
            user = get_user(message.from_user.id)
            if not user:
                bot.reply_to(message, "❗ Xatolik!")
                return
            
            stats = ReferralService.get_referral_stats(user['user_id'])
            bot_info = bot.get_me()
            ref_link = generate_referral_link(bot_info.username, stats['referral_code'])
            
            text = (
                f"🔗 REFERAL TIZIMI\n\n"
                f"Taklif qilganlar: {stats['total_referrals']} ta\n"
                f"Topilgan bonus: {stats['total_earned']} ⭐\n\n"
                f"Sizning linkingiz:\n{ref_link}"
            )
            bot.send_message(
                message.chat.id, 
                text, 
                reply_markup=referral_kb(ref_link)
            )
        except Exception as e:
            logger.error(f"referral error: {e}")
            bot.reply_to(message, "❗ Xatolik!")
    
    
    @bot.message_handler(func=lambda m: m.text == "ℹ️ Qanday ishlaydi")
    def how_it_works_handler(message: types.Message):
        """How it works handler"""
        text = (
            "📖 QANDAY ISHLAYDI:\n\n"
            "1️⃣ Mahsulot tanlang\n"
            "2️⃣ To'lov usulini tanlang\n"
            "3️⃣ Admin tasdiqlaydi\n\n"
            "⏳ Jarayon: 5-30 daqiqa\n"
            "🔒 100% xavfsiz"
        )
        bot.send_message(message.chat.id, text)
    
    
    @bot.message_handler(func=lambda m: m.text == "📞 Admin bilan bog'lanish")
    def contact_admin_handler(message: types.Message):
        """Contact admin handler"""
        try:
            from keyboards import back_kb
            
            text = "📞 Savolingizni yozing:"
            bot.send_message(
                message.chat.id, 
                text, 
                reply_markup=back_kb("back_to_main")
            )
            user_states[message.from_user.id] = {'action': 'support_message'}
        except Exception as e:
            logger.error(f"contact_admin error: {e}")
    
    
    @bot.message_handler(func=lambda m: m.text == "🏠 Asosiy menyu")
    def back_to_main_handler(message: types.Message):
        """Back to main menu handler"""
        try:
            from config import Config
            from keyboards import main_menu_kb
            
            user_states.pop(message.from_user.id, None)
            is_admin = message.from_user.id in (Config.ADMIN_ID if isinstance(Config.ADMIN_ID, list) else [Config.ADMIN_ID])
            bot.send_message(
                message.chat.id, 
                "🏠 Asosiy menyu", 
                reply_markup=main_menu_kb(is_admin)
            )
        except Exception as e:
            logger.error(f"back_to_main error: {e}")
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('qty:'))
    def quantity_callback(call: types.CallbackQuery):
        """Quantity selection callback"""
        try:
            from database import get_settings, get_user, get_order
            from keyboards import payment_method_kb, back_kb
            from utils import generate_order_text
            from services.order_service import OrderService
            
            data = call.data.split(':')[1]
            settings = get_settings()
            state = user_states.get(call.from_user.id, {})
            action = state.get('action', 'profile_stars')
            
            if data == 'custom':
                bot.answer_callback_query(call.id, "Miqdorni kiriting")
                bot.send_message(
                    call.message.chat.id, 
                    "💎 Miqdorni kiriting (Stars):", 
                    reply_markup=back_kb("back_to_main")
                )
                user_states[call.from_user.id] = {
                    'action': f'{action}_custom', 
                    'order_type': action.replace('_stars', '')
                }
                return
            
            amount = int(data)
            order_type = action.replace('_stars', '')
            
            order_id, msg = OrderService.create_stars_order(
                call.from_user.id, 
                order_type, 
                amount, 
                settings
            )
            
            if not order_id:
                bot.answer_callback_query(call.id, msg, show_alert=True)
                return
            
            user = get_user(call.from_user.id)
            order = get_order(order_id)
            has_balance = user['balance'] >= amount
            
            text = f"✅ Buyurtma yaratildi!\n\n{generate_order_text(order, user)}\n\n💳 To'lov usulini tanlang:"
            
            bot.edit_message_text(
                text, 
                call.message.chat.id, 
                call.message.message_id, 
                reply_markup=payment_method_kb(has_balance, amount)
            )
            
            user_states[call.from_user.id] = {
                'action': 'select_payment', 
                'order_id': order_id
            }
            
        except Exception as e:
            logger.error(f"quantity_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!", show_alert=True)
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('gift:'))
    def gift_callback(call: types.CallbackQuery):
        """Gift selection callback"""
        try:
            from database import get_settings, get_user, get_order
            from keyboards import payment_method_kb
            from utils import generate_order_text
            from services.order_service import OrderService
            
            gift_key = call.data.split(':')[1]
            settings = get_settings()
            
            order_id, msg = OrderService.create_gift_order(
                call.from_user.id,
                gift_key,
                settings
            )
            
            if not order_id:
                bot.answer_callback_query(call.id, msg, show_alert=True)
                return
            
            user = get_user(call.from_user.id)
            order = get_order(order_id)
            has_balance = user['balance'] >= order['amount']
            
            text = f"✅ Buyurtma yaratildi!\n\n{generate_order_text(order, user)}\n\n💳 To'lov usulini tanlang:"
            
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=payment_method_kb(has_balance, order['amount'])
            )
            
            user_states[call.from_user.id] = {
                'action': 'select_payment',
                'order_id': order_id
            }
            
        except Exception as e:
            logger.error(f"gift_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!", show_alert=True)
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('vip:'))
    def vip_callback(call: types.CallbackQuery):
        """VIP selection callback"""
        try:
            from database import get_settings, get_user, get_order
            from keyboards import payment_method_kb
            from utils import generate_order_text
            from services.order_service import OrderService
            
            action = call.data.split(':')[1]
            
            if action == 'info':
                settings = get_settings()
                text = (
                    "👑 VIP OBUNA AFZALLIKLARI\n\n"
                    "✨ VIP a'zo bo'lib, quyidagilardan bahramand bo'ling:\n\n"
                    "🎯 CHEGIRMALAR:\n"
                    f"• {settings['vip_discount']}% chegirma barcha xaridlarda\n"
                    "• Maxsus VIP narxlar\n\n"
                    "🎁 BONUSLAR:\n"
                    "• Oylik bonus Stars\n"
                    "• Tug'ilgan kun bonusi\n"
                    "• Maxsus takliflar\n\n"
                    "⚡ USTUVORLIK:\n"
                    "• Tezkor qo'llab-quvvatlash\n"
                    "• Birinchi bo'lib yangi funksiyalar"
                )
                bot.answer_callback_query(call.id, "VIP haqida", show_alert=False)
                bot.send_message(call.message.chat.id, text)
                return
            
            settings = get_settings()
            
            order_id, msg = OrderService.create_vip_order(
                call.from_user.id,
                action,
                settings
            )
            
            if not order_id:
                bot.answer_callback_query(call.id, msg, show_alert=True)
                return
            
            user = get_user(call.from_user.id)
            order = get_order(order_id)
            
            text = f"✅ Buyurtma yaratildi!\n\n{generate_order_text(order, user)}\n\n💳 To'lov usulini tanlang:"
            
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=payment_method_kb(False, 0)
            )
            
            user_states[call.from_user.id] = {
                'action': 'select_payment',
                'order_id': order_id
            }
            
        except Exception as e:
            logger.error(f"vip_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!", show_alert=True)
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('profile:'))
    def profile_callback(call: types.CallbackQuery):
        """Profile actions callback"""
        try:
            from database import get_user_orders, get_user_transactions, get_user
            from keyboards import balance_topup_kb, back_kb, order_detail_kb
            from utils import format_time, format_money, generate_order_text
            
            action = call.data.split(':')[1]
            
            if action == 'topup':
                text = "💳 Balansni to'ldirish\n\nSummani tanlang:"
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=balance_topup_kb()
                )
            
            elif action == 'orders':
                orders = get_user_orders(call.from_user.id, limit=10)
                if orders:
                    text = "📋 SIZNING BUYURTMALARINGIZ\n\n"
                    for order in orders[:5]:
                        status_emoji = {'pending': '⏳', 'paid': '💸', 'confirmed': '✅', 'cancelled': '❌'}
                        emoji = status_emoji.get(order['status'], '❓')
                        text += f"{emoji} #{order['id']} - {format_money(order['total_sum'])} so'm\n"
                else:
                    text = "📋 Sizda hali buyurtmalar yo'q"
                
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=back_kb("back_to_main")
                )
            
            elif action == 'transactions':
                transactions = get_user_transactions(call.from_user.id, limit=10)
                if transactions:
                    text = "📊 TRANZAKSIYALAR\n\n"
                    for tx in transactions[:5]:
                        sign = "+" if tx['amount'] > 0 else ""
                        text += f"{sign}{tx['amount']}⭐ - {tx['description']}\n"
                        text += f"{format_time(tx['created_at'])}\n\n"
                else:
                    text = "📊 Tranzaksiyalar yo'q"
                
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=back_kb("back_to_main")
                )
            
            elif action == 'referral':
                from services.referral_service import ReferralService
                from utils import generate_referral_link
                
                user = get_user(call.from_user.id)
                stats = ReferralService.get_referral_stats(user['user_id'])
                bot_info = bot.get_me()
                ref_link = generate_referral_link(bot_info.username, stats['referral_code'])
                
                text = (
                    f"🔗 REFERAL TIZIMI\n\n"
                    f"Taklif qilganlar: {stats['total_referrals']} ta\n"
                    f"Aktiv: {stats['active_referrals']} ta\n"
                    f"Topilgan: {stats['total_earned']} ⭐\n\n"
                    f"Link:\n{ref_link}"
                )
                
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=back_kb("back_to_main")
                )
            
            elif action == 'vip':
                from database import get_settings
                from keyboards import vip_packages_kb
                
                settings = get_settings()
                text = (
                    f"👑 VIP OBUNA\n\n"
                    f"Chegirma: {settings['vip_discount']}%\n\n"
                    "Paket tanlang:"
                )
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=vip_packages_kb(settings['vip_prices'], settings['star_price'])
                )
            
            elif action == 'back':
                from config import Config
                from keyboards import main_menu_kb
                
                is_admin = call.from_user.id in (Config.ADMIN_ID if isinstance(Config.ADMIN_ID, list) else [Config.ADMIN_ID])
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(
                    call.message.chat.id,
                    "🏠 Asosiy menyu",
                    reply_markup=main_menu_kb(is_admin)
                )
            
        except Exception as e:
            logger.error(f"profile_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!")
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('topup:'))
    def topup_callback(call: types.CallbackQuery):
        """Balance topup callback"""
        try:
            from database import get_settings, get_user, get_order
            from keyboards import payment_method_kb, back_kb
            from utils import generate_order_text
            from services.order_service import OrderService
            
            data = call.data.split(':')[1]
            
            if data == 'custom':
                bot.answer_callback_query(call.id, "Summani kiriting")
                bot.send_message(
                    call.message.chat.id,
                    "💰 Summani kiriting (so'mda):",
                    reply_markup=back_kb("profile:back")
                )
                user_states[call.from_user.id] = {'action': 'topup_custom'}
                return
            
            stars = int(data)
            settings = get_settings()
            
            order_id, msg = OrderService.create_balance_topup_order(
                call.from_user.id,
                stars,
                settings
            )
            
            if not order_id:
                bot.answer_callback_query(call.id, msg, show_alert=True)
                return
            
            user = get_user(call.from_user.id)
            order = get_order(order_id)
            
            text = f"✅ Buyurtma yaratildi!\n\n{generate_order_text(order, user)}\n\n💳 To'lov usulini tanlang:"
            
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=payment_method_kb(False, 0)
            )
            
            user_states[call.from_user.id] = {
                'action': 'select_payment',
                'order_id': order_id
            }
            
        except Exception as e:
            logger.error(f"topup_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!", show_alert=True)
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('pay:'))
    def payment_method_callback(call: types.CallbackQuery):
        """Payment method callback"""
        try:
            from config import Config
            from database import get_order
            from utils import format_money
            from services.order_service import OrderService
            
            method = call.data.split(':')[1]
            state = user_states.get(call.from_user.id, {})
            order_id = state.get('order_id')
            
            if not order_id:
                bot.answer_callback_query(call.id, "Buyurtma topilmadi!", show_alert=True)
                return
            
            success = OrderService.set_payment_method(order_id, method)
            if not success:
                bot.answer_callback_query(call.id, "Xatolik yuz berdi!", show_alert=True)
                return
            
            if method == 'balance':
                success, msg = OrderService.process_balance_payment(order_id)
                if success:
                    text = f"✅ {msg}\n\nBuyurtma #{order_id}"
                    bot.edit_message_text(
                        text,
                        call.message.chat.id,
                        call.message.message_id
                    )
                    user_states.pop(call.from_user.id, None)
                else:
                    bot.answer_callback_query(call.id, msg, show_alert=True)
            
            elif method == 'card':
                order = get_order(order_id)
                text = (
                    f"💳 Karta orqali to'lov\n\n"
                    f"Karta raqam: {Config.CARD_NUMBER}\n"
                    f"Egasi: {Config.CARD_OWNER}\n\n"
                    f"Summa: {format_money(order['total_sum'])} so'm\n\n"
                    f"📸 To'lov chekini yuboring:"
                )
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id)
                user_states[call.from_user.id] = {
                    'action': 'upload_payment_proof',
                    'order_id': order_id
                }
        
        except Exception as e:
            logger.error(f"payment_method error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!", show_alert=True)
    
    
    @bot.callback_query_handler(func=lambda call: call.data == 'back_to_main')
    def back_to_main_callback(call: types.CallbackQuery):
        """Back to main menu callback"""
        try:
            from config import Config
            from keyboards import main_menu_kb
            
            bot.delete_message(call.message.chat.id, call.message.message_id)
            user_states.pop(call.from_user.id, None)
            is_admin = call.from_user.id in (Config.ADMIN_ID if isinstance(Config.ADMIN_ID, list) else [Config.ADMIN_ID])
            bot.send_message(
                call.message.chat.id,
                "🏠 Asosiy menyu",
                reply_markup=main_menu_kb(is_admin)
            )
        except Exception as e:
            logger.error(f"back_to_main_callback error: {e}")
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('order:'))
    def order_action_callback(call: types.CallbackQuery):
        """Order action callback"""
        try:
            from services.order_service import OrderService
            
            parts = call.data.split(':')
            action = parts[1]
            order_id = int(parts[2])
            
            if action == 'cancel':
                success, msg = OrderService.cancel_order(order_id, call.from_user.id)
                if success:
                    bot.answer_callback_query(call.id, msg, show_alert=True)
                    bot.edit_message_text(
                        f"❌ {msg}",
                        call.message.chat.id,
                        call.message.message_id
                    )
                else:
                    bot.answer_callback_query(call.id, msg, show_alert=True)
        
        except Exception as e:
            logger.error(f"order_action_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!")
    
    
    @bot.message_handler(content_types=['photo', 'document'])
    def payment_proof_handler(message: types.Message):
        """Payment proof handler"""
        try:
            from config import Config
            from database import get_order
            from utils import format_money
            from services.order_service import OrderService
            
            state = user_states.get(message.from_user.id, {})
            if state.get('action') != 'upload_payment_proof':
                return
            
            order_id = state.get('order_id')
            if not order_id:
                return
            
            success, msg = OrderService.attach_payment_proof(order_id, message.message_id)
            
            if success:
                bot.reply_to(
                    message,
                    f"✅ {msg}\n\nBuyurtma #{order_id}\n\n⏳ Admin tekshirayapti (5-30 daqiqa)"
                )
                
                try:
                    # Send to first admin (or all admins)
                    admin_list = Config.ADMIN_ID if isinstance(Config.ADMIN_ID, list) else [Config.ADMIN_ID]
                    first_admin = admin_list[0]
                    
                    order = get_order(order_id)
                    username = f"@{message.from_user.username}" if message.from_user.username else "Foydalanuvchi"
                    
                    forwarded = bot.forward_message(
                        first_admin,
                        message.chat.id,
                        message.message_id
                    )
                    
                    admin_text = (
                        f"💸 YANGI TO'LOV!\n\n"
                        f"Buyurtma ID: #{order_id}\n"
                        f"Foydalanuvchi: {username}\n"
                        f"User ID: {message.from_user.id}\n"
                        f"Summa: {format_money(order['total_sum'])} so'm\n\n"
                        f"Tasdiqlash:\n/confirm {order_id}\n"
                        f"Rad etish:\n/reject {order_id} <sabab>"
                    )
                    
                    bot.send_message(
                        first_admin,
                        admin_text,
                        reply_to_message_id=forwarded.message_id
                    )
                except Exception as e:
                    logger.error(f"Admin notification error: {e}")
                
                user_states.pop(message.from_user.id, None)
            else:
                bot.reply_to(message, f"❌ {msg}")
        
        except Exception as e:
            logger.error(f"payment_proof error: {e}", exc_info=True)
            bot.reply_to(message, "❗ Xatolik!")
    
    
    @bot.message_handler(func=lambda m: True, content_types=['text'])
    def text_message_handler(message: types.Message):
        """General text handler"""
        try:
            from config import Config
            from database import get_settings, get_user, get_order, create_ticket, add_ticket_message
            from keyboards import main_menu_kb, payment_method_kb
            from utils import generate_order_text
            from services.order_service import OrderService
            
            state = user_states.get(message.from_user.id, {})
            action = state.get('action', '')
            
            # Custom quantity
            if action.endswith('_custom'):
                try:
                    amount = int(message.text.strip())
                except:
                    bot.reply_to(message, "❗ Faqat raqam kiriting!")
                    return
                
                if amount < 1:
                    bot.reply_to(message, "❗ Minimal 1 Stars!")
                    return
                
                if amount > 100000:
                    bot.reply_to(message, "❗ Maksimal 100,000 Stars!")
                    return
                
                settings = get_settings()
                order_type = state.get('order_type', 'profile')
                
                order_id, msg = OrderService.create_stars_order(
                    message.from_user.id,
                    order_type,
                    amount,
                    settings
                )
                
                if order_id:
                    user = get_user(message.from_user.id)
                    order = get_order(order_id)
                    has_balance = user['balance'] >= amount
                    
                    text = f"✅ Buyurtma yaratildi!\n\n{generate_order_text(order, user)}\n\n💳 To'lov:"
                    bot.send_message(
                        message.chat.id,
                        text,
                        reply_markup=payment_method_kb(has_balance, amount)
                    )
                    user_states[message.from_user.id] = {
                        'action': 'select_payment',
                        'order_id': order_id
                    }
                else:
                    bot.reply_to(message, f"❌ {msg}")
            
            # Custom topup
            elif action == 'topup_custom':
                try:
                    amount_sum = int(message.text.strip())
                except:
                    bot.reply_to(message, "❗ Faqat raqam kiriting!")
                    return
                
                if amount_sum < 1000:
                    bot.reply_to(message, "❗ Minimal 1,000 so'm!")
                    return
                
                stars = amount_sum // 1000
                settings = get_settings()
                
                order_id, msg = OrderService.create_balance_topup_order(
                    message.from_user.id,
                    stars,
                    settings
                )
                
                if order_id:
                    user = get_user(message.from_user.id)
                    order = get_order(order_id)
                    
                    text = f"✅ Buyurtma yaratildi!\n\n{generate_order_text(order, user)}\n\n💳 To'lov:"
                    bot.send_message(
                        message.chat.id,
                        text,
                        reply_markup=payment_method_kb(False, 0)
                    )
                    user_states[message.from_user.id] = {
                        'action': 'select_payment',
                        'order_id': order_id
                    }
                else:
                    bot.reply_to(message, f"❌ {msg}")
            
            # Support message
            elif action == 'support_message':
                ticket_id = create_ticket(message.from_user.id)
                
                if ticket_id:
                    add_ticket_message(
                        ticket_id,
                        message.from_user.id,
                        message.text,
                        is_admin=False
                    )
                    bot.reply_to(message, "✅ Xabaringiz yuborildi! Tez orada javob beramiz.")
                    
                    try:
                        admin_list = Config.ADMIN_ID if isinstance(Config.ADMIN_ID, list) else [Config.ADMIN_ID]
                        first_admin = admin_list[0]
                        
                        username = f"@{message.from_user.username}" if message.from_user.username else "Foydalanuvchi"
                        admin_text = (
                            f"📬 YANGI MUROJAAT #{ticket_id}\n\n"
                            f"Foydalanuvchi: {username}\n"
                            f"User ID: {message.from_user.id}\n\n"
                            f"Xabar:\n{message.text}\n\n"
                            f"Javob:\n/reply {ticket_id} <javob>"
                        )
                        bot.send_message(first_admin, admin_text)
                    except Exception as e:
                        logger.error(f"Admin notification error: {e}")
                    
                    user_states.pop(message.from_user.id, None)
                else:
                    bot.reply_to(message, "❌ Xatolik!")
            
            # Unknown message
            else:
                is_admin = message.from_user.id in (Config.ADMIN_ID if isinstance(Config.ADMIN_ID, list) else [Config.ADMIN_ID])
                bot.send_message(
                    message.chat.id,
                    "❗ Menyudan foydalaning.",
                    reply_markup=main_menu_kb(is_admin)
                )
        
        except Exception as e:
            logger.error(f"text_handler error: {e}", exc_info=True)
            bot.reply_to(message, "❗ Xatolik!")
    
    logger.info("✅ User handlers registered successfully")
