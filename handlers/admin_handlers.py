"""
Stars Shop Bot - Admin Handlers
Professional Version - 100% Working
SUPPORTS MULTIPLE ADMINS
"""
import logging
import time
from telebot import TeleBot, types

logger = logging.getLogger(__name__)

admin_states = {}


def is_admin(user_id: int) -> bool:
    """Check if user is admin - SUPPORTS MULTIPLE ADMINS"""
    from config import Config
    
    # Get admin IDs (supports both single and multiple admins)
    admin_ids = Config.admin_ids()
    
    # Convert to list if single admin
    if isinstance(admin_ids, int):
        admin_ids = [admin_ids]
    elif isinstance(admin_ids, str):
        # Parse comma-separated string
        admin_ids = [int(x.strip()) for x in admin_ids.split(',') if x.strip().isdigit()]
    
    return user_id in admin_ids


def register_admin_handlers(bot: TeleBot):
    """Register all admin handlers"""
    
    def _parse_int(text: str, min_val: int = 1, max_val: int = 1000000000):
        try:
            value = int(text.strip())
        except Exception:
            return None
        
        if value < min_val or value > max_val:
            return None
        return value
    
    
    def _admin_summary_text():
        from database import get_stats
        from utils import format_money
        
        stats = get_stats()
        text = (
            "⚙️ ADMIN PANEL\n\n"
            f"👥 Foydalanuvchilar: {stats.get('total_users', 0)}\n"
            f"👑 VIP: {stats.get('vip_users', 0)}\n"
            f"📦 Jami buyurtmalar: {stats.get('total_orders', 0)}\n"
            f"⏳ Kutilmoqda: {stats.get('pending_orders', 0)}\n"
            f"💸 To'langan: {stats.get('paid_orders', 0)}\n"
            f"💰 Jami daromad: {format_money(stats.get('total_revenue', 0))} so'm\n\n"
            "Kerakli bo'limni tanlang:"
        )
        return text
    
    
    def _show_admin_panel(chat_id: int, message_id: int = None):
        from keyboards import admin_main_kb
        
        text = _admin_summary_text()
        if message_id:
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=admin_main_kb()
            )
        else:
            bot.send_message(
                chat_id,
                text,
                reply_markup=admin_main_kb()
            )
    
    
    def _show_users_list(chat_id: int, message_id: int = None):
        from database import get_all_users
        from utils import format_money
        from telebot import types
        
        users = get_all_users(limit=10)
        
        text = f"👥 FOYDALANUVCHILAR (Jami: {len(users)})\n\n"
        if users:
            for user in users[:10]:
                vip = "👑" if user.get('is_vip') else ""
                username = f"@{user['username']}" if user.get('username') else user['full_name']
                text += f"{vip} {username} - {format_money(user['balance'])} so'm (ID: {user['user_id']})\n"
        else:
            text += "Hozircha foydalanuvchilar yo'q."
        
        kb = types.InlineKeyboardMarkup(row_width=2)
        for user in users[:6]:
            label = f"{user['user_id']}"
            if user.get('username'):
                label = f"@{user['username']}"
            kb.add(types.InlineKeyboardButton(label, callback_data=f"user:view:{user['user_id']}"))
        
        kb.add(types.InlineKeyboardButton("🔎 ID bo'yicha qidirish", callback_data="user:search"))
        kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="admin:back"))
        
        if message_id:
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=kb
            )
        else:
            bot.send_message(chat_id, text, reply_markup=kb)
    
    
    def _show_order_details(order_id: int, chat_id: int, message_id: int = None):
        from database import get_order
        from keyboards import admin_order_actions_kb
        from utils import generate_order_text
        
        order = get_order(order_id)
        if not order:
            bot.send_message(chat_id, "❗ Buyurtma topilmadi!")
            return
        
        text = generate_order_text(order)
        kb = admin_order_actions_kb(order_id, order['status'])
        
        if message_id:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=kb)
        else:
            bot.send_message(chat_id, text, reply_markup=kb)
    
    
    def _show_user_details(user_id: int, chat_id: int, message_id: int = None):
        from database import get_user, get_settings
        from keyboards import admin_user_actions_kb
        from utils import generate_user_profile_text, is_vip_active
        
        user = get_user(user_id)
        if not user:
            bot.send_message(chat_id, "❗ Foydalanuvchi topilmadi!")
            return
        
        settings = get_settings()
        text = generate_user_profile_text(user, settings)
        kb = admin_user_actions_kb(user_id, is_vip_active(user))
        
        if message_id:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=kb)
        else:
            bot.send_message(chat_id, text, reply_markup=kb)


    def _show_orders_list(status: str, chat_id: int, message_id: int = None):
        from database import get_orders_by_status, get_stats
        from utils import format_money
        from telebot import types
        
        if status in ['pending', 'paid', 'confirmed', 'cancelled']:
            orders = get_orders_by_status(status, limit=10)
            if orders:
                text = f"📦 {status.upper()} BUYURTMALAR\n\n"
                for order in orders[:5]:
                    text += f"#{order['id']} - {format_money(order['total_sum'])} so'm\n"
                    text += f"User ID: {order['user_id']}\n\n"
            else:
                text = f"📦 {status.upper()} buyurtmalar yo'q."
        else:
            stats = get_stats()
            text = f"📦 BARCHA BUYURTMALAR\n\nJami: {stats.get('total_orders', 0)}"
            orders = []
        
        kb = types.InlineKeyboardMarkup(row_width=2)
        for order in orders[:6]:
            kb.add(types.InlineKeyboardButton(
                f"#{order['id']} - {format_money(order['total_sum'])} so'm",
                callback_data=f"order:view:{order['id']}"
            ))
        
        kb.add(types.InlineKeyboardButton("🔎 ID bo'yicha qidirish", callback_data="orders:search"))
        kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="admin:orders"))
        
        if message_id:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=kb)
        else:
            bot.send_message(chat_id, text, reply_markup=kb)


    def _show_support_list(chat_id: int, message_id: int = None):
        from database import get_open_tickets
        from telebot import types
        
        tickets = get_open_tickets()
        if tickets:
            text = f"💬 Ochiq ticketlar: {len(tickets)}\n\n"
            for ticket in tickets[:6]:
                text += f"#{ticket['id']} - {ticket['status']} (User: {ticket['user_id']})\n"
        else:
            text = "💬 Ochiq ticketlar yo'q."
        
        kb = types.InlineKeyboardMarkup(row_width=2)
        for ticket in tickets[:6]:
            kb.add(types.InlineKeyboardButton(
                f"Ticket #{ticket['id']}",
                callback_data=f"ticket:view:{ticket['id']}"
            ))
        
        kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="admin:back"))
        
        if message_id:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=kb)
        else:
            bot.send_message(chat_id, text, reply_markup=kb)


    def _show_ticket_details(ticket_id: int, chat_id: int, message_id: int = None):
        from database import get_ticket_messages
        from utils import format_time
        from telebot import types
        
        messages = get_ticket_messages(ticket_id)
        if not messages:
            text = f"Ticket #{ticket_id}\n\nXabarlar topilmadi."
        else:
            text = f"Ticket #{ticket_id}\n\n"
            for msg in messages[-6:]:
                sender = "Admin" if msg.get('is_admin') else "User"
                time_text = format_time(msg.get('sent_at', 0))
                text += f"{sender} ({time_text}):\n{msg['message']}\n\n"
        
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.row(
            types.InlineKeyboardButton("Javob berish", callback_data=f"ticket:reply:{ticket_id}"),
            types.InlineKeyboardButton("Yopish", callback_data=f"ticket:close:{ticket_id}")
        )
        kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="admin:support"))
        
        if message_id:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=kb)
        else:
            bot.send_message(chat_id, text, reply_markup=kb)
    
    @bot.message_handler(func=lambda m: m.text == "⚙️ Admin panel" and is_admin(m.from_user.id))
    def admin_panel_handler(message: types.Message):
        """Admin panel main"""
        try:
            _show_admin_panel(message.chat.id)
        except Exception as e:
            logger.error(f"admin_panel error: {e}", exc_info=True)
            bot.reply_to(message, "❗ Xatolik!")
    
    
    @bot.message_handler(commands=['stats'])
    def stats_command(message: types.Message):
        """Statistics"""
        try:
            if not is_admin(message.from_user.id):
                return
            
            from database import get_stats, get_settings
            from utils import generate_stats_text
            
            stats = get_stats()
            settings = get_settings()
            text = generate_stats_text(stats, settings)
            
            bot.send_message(message.chat.id, text)
        except Exception as e:
            logger.error(f"stats error: {e}")
            bot.reply_to(message, "❗ Xatolik!")
    
    
    @bot.message_handler(commands=['confirm'])
    def confirm_order_command(message: types.Message):
        """Confirm order"""
        try:
            if not is_admin(message.from_user.id):
                return
            
            from database import get_order, get_settings
            from utils import format_money
            from services.order_service import OrderService
            
            try:
                order_id = int(message.text.split()[1])
            except:
                bot.reply_to(message, "❗ Format: /confirm <order_id>")
                return
            
            settings = get_settings()
            success, msg = OrderService.confirm_order(order_id, settings)
            
            if success:
                order = get_order(order_id)
                bot.reply_to(message, f"✅ {msg}")
                
                try:
                    user_text = (
                        f"✅ Buyurtmangiz tasdiqlandi!\n\n"
                        f"Buyurtma #{order_id}\n"
                        f"Summa: {format_money(order['total_sum'])} so'm\n\n"
                        f"Rahmat! 🎉"
                    )
                    bot.send_message(order['user_id'], user_text)
                except Exception as e:
                    logger.error(f"User notification error: {e}")
            else:
                bot.reply_to(message, f"❌ {msg}")
        
        except Exception as e:
            logger.error(f"confirm error: {e}", exc_info=True)
            bot.reply_to(message, "❗ Xatolik!")
    
    
    @bot.message_handler(commands=['reject'])
    def reject_order_command(message: types.Message):
        """Reject order"""
        try:
            if not is_admin(message.from_user.id):
                return
            
            from database import get_order
            from services.order_service import OrderService
            
            try:
                parts = message.text.split(maxsplit=2)
                order_id = int(parts[1])
                reason = parts[2] if len(parts) > 2 else "Sabab ko'rsatilmagan"
            except:
                bot.reply_to(message, "❗ Format: /reject <order_id> <sabab>")
                return
            
            success, msg = OrderService.reject_order(order_id, reason)
            
            if success:
                order = get_order(order_id)
                bot.reply_to(message, f"✅ {msg}")
                
                try:
                    user_text = (
                        f"❌ Buyurtmangiz rad etildi\n\n"
                        f"Buyurtma #{order_id}\n"
                        f"Sabab: {reason}\n\n"
                        "Admin bilan bog'laning."
                    )
                    bot.send_message(order['user_id'], user_text)
                except Exception as e:
                    logger.error(f"User notification error: {e}")
            else:
                bot.reply_to(message, f"❌ {msg}")
        
        except Exception as e:
            logger.error(f"reject error: {e}", exc_info=True)
            bot.reply_to(message, "❗ Xatolik!")
    
    
    @bot.message_handler(commands=['addstars'])
    def addstars_command(message: types.Message):
        """Add stars to user"""
        try:
            if not is_admin(message.from_user.id):
                return
            
            from database import get_user, update_balance
            from config import Constants
            
            try:
                parts = message.text.split()
                user_id = int(parts[1])
                amount = int(parts[2])
            except:
                bot.reply_to(message, "❗ Format: /addstars <user_id> <amount>")
                return
            
            user = get_user(user_id)
            if not user:
                bot.reply_to(message, "❌ Foydalanuvchi topilmadi!")
                return
            
            success = update_balance(
                user_id,
                amount,
                Constants.TRANSACTION_TYPES['ADMIN_ADD'],
                f"Admin tomonidan qo'shildi"
            )
            
            if success:
                new_balance = user['balance'] + amount
                bot.reply_to(message, f"✅ {amount} so'm qo'shildi!\n\nYangi balans: {new_balance} so'm")
                
                try:
                    bot.send_message(
                        user_id,
                        f"🎁 Sizga {amount} so'm qo'shildi!\n\n"
                        f"Yangi balans: {new_balance} so'm"
                    )
                except Exception as e:
                    logger.error(f"User notification error: {e}")
            else:
                bot.reply_to(message, "❌ Xatolik!")
        
        except Exception as e:
            logger.error(f"addstars error: {e}", exc_info=True)
            bot.reply_to(message, "❗ Xatolik!")
    
    
    @bot.message_handler(commands=['deductstars'])
    def deductstars_command(message: types.Message):
        """Deduct stars from user"""
        try:
            if not is_admin(message.from_user.id):
                return
            
            from database import get_user, update_balance
            from config import Constants
            
            try:
                parts = message.text.split()
                user_id = int(parts[1])
                amount = int(parts[2])
            except:
                bot.reply_to(message, "❗ Format: /deductstars <user_id> <amount>")
                return
            
            user = get_user(user_id)
            if not user:
                bot.reply_to(message, "❌ Foydalanuvchi topilmadi!")
                return
            
            success = update_balance(
                user_id,
                -amount,
                Constants.TRANSACTION_TYPES['ADMIN_DEDUCT'],
                f"Admin tomonidan yechildi"
            )
            
            if success:
                new_balance = max(0, user['balance'] - amount)
                bot.reply_to(message, f"✅ {amount} so'm yechildi!\n\nYangi balans: {new_balance} so'm")
                
                try:
                    bot.send_message(
                        user_id,
                        f"⚠️ Balansdan {amount} so'm yechildi.\n\n"
                        f"Yangi balans: {new_balance} so'm"
                    )
                except Exception as e:
                    logger.error(f"User notification error: {e}")
            else:
                bot.reply_to(message, "❌ Xatolik!")
        
        except Exception as e:
            logger.error(f"deductstars error: {e}", exc_info=True)
            bot.reply_to(message, "❗ Xatolik!")
    
    
    @bot.message_handler(commands=['vipgrant'])
    def vipgrant_command(message: types.Message):
        """Grant VIP to user"""
        try:
            if not is_admin(message.from_user.id):
                return
            
            from services.vip_service import VIPService
            
            try:
                parts = message.text.split()
                user_id = int(parts[1])
                days = int(parts[2])
            except:
                bot.reply_to(message, "❗ Format: /vipgrant <user_id> <days>")
                return
            
            success, msg = VIPService.extend_vip(user_id, days)
            
            if success:
                bot.reply_to(message, f"✅ {msg}")
                
                try:
                    bot.send_message(
                        user_id,
                        f"👑 Sizga VIP status berildi!\n\n"
                        f"Muddat: {days} kun\n"
                        f"Chegirma: 20%\n\n"
                        f"Rahmat! 🎉"
                    )
                except Exception as e:
                    logger.error(f"User notification error: {e}")
            else:
                bot.reply_to(message, f"❌ {msg}")
        
        except Exception as e:
            logger.error(f"vipgrant error: {e}", exc_info=True)
            bot.reply_to(message, "❗ Xatolik!")
    
    
    @bot.message_handler(commands=['viprevoke'])
    def viprevoke_command(message: types.Message):
        """Revoke VIP from user"""
        try:
            if not is_admin(message.from_user.id):
                return
            
            from services.vip_service import VIPService
            
            try:
                user_id = int(message.text.split()[1])
            except:
                bot.reply_to(message, "❗ Format: /viprevoke <user_id>")
                return
            
            success, msg = VIPService.revoke_vip(user_id)
            
            if success:
                bot.reply_to(message, f"✅ {msg}")
                
                try:
                    bot.send_message(user_id, "⚠️ VIP statusingiz bekor qilindi.")
                except Exception as e:
                    logger.error(f"User notification error: {e}")
            else:
                bot.reply_to(message, f"❌ {msg}")
        
        except Exception as e:
            logger.error(f"viprevoke error: {e}", exc_info=True)
            bot.reply_to(message, "❗ Xatolik!")
    
    
    @bot.message_handler(commands=['broadcast'])
    def broadcast_command(message: types.Message):
        """Start broadcast"""
        try:
            if not is_admin(message.from_user.id):
                return
            
            bot.reply_to(
                message,
                "📨 BROADCAST\n\nYubormoqchi bo'lgan xabaringizni yozing:"
            )
            
            admin_states[message.from_user.id] = {'action': 'broadcast_message'}
        
        except Exception as e:
            logger.error(f"broadcast error: {e}")
    
    
    @bot.message_handler(commands=['reply'])
    def reply_ticket_command(message: types.Message):
        """Reply to support ticket"""
        try:
            if not is_admin(message.from_user.id):
                return
            
            from database import add_ticket_message, get_db
            
            try:
                parts = message.text.split(maxsplit=2)
                ticket_id = int(parts[1])
                reply_text = parts[2]
            except:
                bot.reply_to(message, "❗ Format: /reply <ticket_id> <javob>")
                return
            
            success = add_ticket_message(
                ticket_id,
                message.from_user.id,
                reply_text,
                is_admin=True
            )
            
            if success:
                bot.reply_to(message, "✅ Javob yuborildi!")
                
                try:
                    with get_db() as conn:
                        c = conn.cursor()
                        c.execute("SELECT user_id FROM support_tickets WHERE id=?", (ticket_id,))
                        row = c.fetchone()
                        if row:
                            user_id = row['user_id']
                            bot.send_message(
                                user_id,
                                f"💬 Admin javobi:\n\n{reply_text}"
                            )
                except Exception as e:
                    logger.error(f"User notification error: {e}")
            else:
                bot.reply_to(message, "❌ Xatolik!")
        
        except Exception as e:
            logger.error(f"reply error: {e}", exc_info=True)
            bot.reply_to(message, "❗ Xatolik!")
    
    
    @bot.message_handler(commands=['admins'])
    def admins_command(message: types.Message):
        """List all admins"""
        try:
            if not is_admin(message.from_user.id):
                return
            
            from config import Config
            
            admin_ids = Config.admin_ids()
            
            text = "👨‍💼 ADMIN RO'YXATI:\n\n"
            for admin_id in admin_ids:
                text += f"• ID: {admin_id}\n"
            
            bot.send_message(message.chat.id, text)
        
        except Exception as e:
            logger.error(f"admins error: {e}")
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('admin:') and is_admin(call.from_user.id))
    def admin_callback(call: types.CallbackQuery):
        """Admin panel callbacks"""
        try:
            from database import get_stats, get_settings
            from keyboards import (
                admin_main_kb,
                admin_orders_kb,
                admin_system_kb,
                admin_prices_kb,
                admin_bonuses_kb,
                admin_broadcast_kb
            )
            from utils import generate_stats_text
            
            action = call.data.split(':')[1]
            
            if action == 'stats':
                stats = get_stats()
                settings = get_settings()
                text = generate_stats_text(stats, settings)
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=admin_main_kb()
                )
            
            elif action == 'orders':
                text = "📦 BUYURTMALAR\n\nStatus bo'yicha tanlang:"
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=admin_orders_kb()
                )
            
            elif action == 'users':
                _show_users_list(call.message.chat.id, call.message.message_id)
            
            elif action == 'settings':
                text = "⚙️ SOZLAMALAR\n\nBo'limni tanlang:"
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=admin_system_kb()
                )
            
            elif action == 'prices':
                text = "💳 NARXLAR\n\nNimani o'zgartiramiz?"
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=admin_prices_kb()
                )
            
            elif action == 'bonuses':
                text = "🎁 BONUSLAR\n\nNimani o'zgartiramiz?"
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=admin_bonuses_kb()
                )
            
            elif action == 'support':
                _show_support_list(call.message.chat.id, call.message.message_id)
            
            elif action == 'broadcast':
                text = "📨 BROADCAST\n\nQaysi guruhga yuboramiz?"
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=admin_broadcast_kb()
                )
            
            elif action == 'back':
                _show_admin_panel(call.message.chat.id, call.message.message_id)
        
        except Exception as e:
            logger.error(f"admin_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!")
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('orders:') and is_admin(call.from_user.id))
    def admin_orders_callback(call: types.CallbackQuery):
        """Admin orders callbacks"""
        try:
            status = call.data.split(':')[1]
            
            if status == 'search':
                bot.edit_message_text(
                    "Buyurtma ID kiriting:",
                    call.message.chat.id,
                    call.message.message_id
                )
                admin_states[call.from_user.id] = {'action': 'order_search'}
                return
            
            _show_orders_list(status, call.message.chat.id, call.message.message_id)
        
        except Exception as e:
            logger.error(f"admin_orders_callback error: {e}", exc_info=True)
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('user:') and is_admin(call.from_user.id))
    def admin_user_callback(call: types.CallbackQuery):
        """Admin user callbacks"""
        try:
            from database import get_user_orders, get_user_transactions
            from utils import format_time, format_money
            from services.vip_service import VIPService
            from telebot import types
            
            parts = call.data.split(':')
            action = parts[1]
            user_id = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None
            
            if action == 'search':
                bot.edit_message_text(
                    "Foydalanuvchi ID kiriting:",
                    call.message.chat.id,
                    call.message.message_id
                )
                admin_states[call.from_user.id] = {'action': 'user_search'}
                return
            
            if action == 'view' and user_id:
                _show_user_details(user_id, call.message.chat.id, call.message.message_id)
                return
            
            if not user_id:
                bot.answer_callback_query(call.id, "User ID topilmadi!", show_alert=True)
                return
            
            if action == 'addstars':
                admin_states[call.from_user.id] = {'action': 'user_addstars', 'user_id': user_id}
                bot.edit_message_text(
                    f"User ID {user_id} uchun summa (so'm) kiriting:",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
            
            if action == 'deduct':
                admin_states[call.from_user.id] = {'action': 'user_deductstars', 'user_id': user_id}
                bot.edit_message_text(
                    f"User ID {user_id} uchun yechiladigan summa (so'm) kiriting:",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
            
            if action == 'grant_vip':
                admin_states[call.from_user.id] = {'action': 'user_grant_vip', 'user_id': user_id}
                bot.edit_message_text(
                    f"User ID {user_id} uchun VIP kunini kiriting:",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
            
            if action == 'revoke_vip':
                success, msg = VIPService.revoke_vip(user_id)
                if success:
                    bot.answer_callback_query(call.id, msg, show_alert=True)
                    try:
                        bot.send_message(user_id, "VIP statusingiz bekor qilindi.")
                    except Exception as e:
                        logger.error(f"User notification error: {e}")
                    _show_user_details(user_id, call.message.chat.id, call.message.message_id)
                else:
                    bot.answer_callback_query(call.id, msg, show_alert=True)
                return
            
            if action == 'orders':
                orders = get_user_orders(user_id, limit=10)
                if orders:
                    text = f"User {user_id} buyurtmalari:\n\n"
                    for order in orders[:5]:
                        text += f"#{order['id']} - {format_money(order['total_sum'])} so'm ({order['status']})\n"
                else:
                    text = f"User {user_id} uchun buyurtmalar topilmadi."
                
                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data=f"user:view:{user_id}"))
                
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb)
                return
            
            if action == 'transactions':
                txs = get_user_transactions(user_id, limit=10)
                if txs:
                    text = f"User {user_id} tranzaksiyalari:\n\n"
                    for tx in txs[:5]:
                        sign = "+" if tx['amount'] > 0 else ""
                        text += f"{sign}{tx['amount']}⭐ - {tx['description']}\n"
                        text += f"{format_time(tx['created_at'])}\n\n"
                else:
                    text = f"User {user_id} uchun tranzaksiyalar topilmadi."
                
                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data=f"user:view:{user_id}"))
                
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb)
                return
            
            if action == 'message':
                admin_states[call.from_user.id] = {'action': 'user_message', 'user_id': user_id}
                bot.edit_message_text(
                    f"User ID {user_id} ga yuboriladigan xabarni yozing:",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
        
        except Exception as e:
            logger.error(f"admin_user_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!")


    @bot.callback_query_handler(func=lambda call: call.data.startswith('order:') and is_admin(call.from_user.id))
    def admin_order_action_callback(call: types.CallbackQuery):
        """Admin order actions"""
        try:
            from database import get_order, get_settings
            from services.order_service import OrderService
            from utils import format_money
            
            parts = call.data.split(':')
            if len(parts) < 3:
                return
            
            action = parts[1]
            order_id = int(parts[2])
            
            if action == 'view':
                _show_order_details(order_id, call.message.chat.id, call.message.message_id)
                return
            
            if action == 'user':
                order = get_order(order_id)
                if order:
                    _show_user_details(order['user_id'], call.message.chat.id, call.message.message_id)
                else:
                    bot.answer_callback_query(call.id, "Buyurtma topilmadi!", show_alert=True)
                return
            
            if action == 'confirm':
                settings = get_settings()
                success, msg = OrderService.confirm_order(order_id, settings)
                if success:
                    bot.answer_callback_query(call.id, msg, show_alert=True)
                    order = get_order(order_id)
                    if order:
                        try:
                            user_text = (
                                f"✅ Buyurtmangiz tasdiqlandi!\n\n"
                                f"Buyurtma #{order_id}\n"
                                f"Summa: {format_money(order['total_sum'])} so'm\n\n"
                                f"Rahmat!"
                            )
                            bot.send_message(order['user_id'], user_text)
                        except Exception as e:
                            logger.error(f"User notification error: {e}")
                    _show_order_details(order_id, call.message.chat.id, call.message.message_id)
                else:
                    bot.answer_callback_query(call.id, msg, show_alert=True)
                return
            
            if action == 'reject':
                admin_states[call.from_user.id] = {'action': 'order_reject', 'order_id': order_id}
                bot.edit_message_text(
                    f"Buyurtma #{order_id} uchun rad etish sababini yozing:",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
        
        except Exception as e:
            logger.error(f"admin_order_action_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!")


    @bot.callback_query_handler(func=lambda call: call.data.startswith('broadcast:') and is_admin(call.from_user.id))
    def admin_broadcast_callback(call: types.CallbackQuery):
        """Admin broadcast callbacks"""
        try:
            target = call.data.split(':')[1]
            
            if target == 'all':
                admin_states[call.from_user.id] = {'action': 'broadcast_message', 'target': 'all'}
                bot.edit_message_text(
                    "Hammaga yuboriladigan xabarni yozing:",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
            
            if target == 'vip':
                admin_states[call.from_user.id] = {'action': 'broadcast_message', 'target': 'vip'}
                bot.edit_message_text(
                    "VIP foydalanuvchilarga yuboriladigan xabarni yozing:",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
            
            if target == 'id':
                admin_states[call.from_user.id] = {'action': 'broadcast_target_id'}
                bot.edit_message_text(
                    "Foydalanuvchi ID kiriting:",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
        
        except Exception as e:
            logger.error(f"admin_broadcast_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!")


    @bot.callback_query_handler(func=lambda call: call.data.startswith('sys:') and is_admin(call.from_user.id))
    def admin_system_callback(call: types.CallbackQuery):
        """Admin system settings"""
        try:
            from database import get_settings, update_settings
            from keyboards import admin_system_kb
            
            action = call.data.split(':')[1]
            
            if action == 'card_number':
                admin_states[call.from_user.id] = {'action': 'set_card_number'}
                bot.edit_message_text(
                    "Yangi karta raqamini kiriting:",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
            
            if action == 'card_owner':
                admin_states[call.from_user.id] = {'action': 'set_card_owner'}
                bot.edit_message_text(
                    "Karta egasini kiriting:",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
            
            if action == 'channel_id':
                admin_states[call.from_user.id] = {'action': 'set_channel_id'}
                bot.edit_message_text(
                    "Kanal ID yoki @username kiriting (o'chirish uchun 'off'):",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
            
            if action == 'force_sub':
                settings = get_settings()
                current = int(settings.get('force_subscription', 0) or 0)
                new_val = 0 if current == 1 else 1
                update_settings(force_subscription=new_val)
                status_text = "yoqildi" if new_val == 1 else "o'chirildi"
                bot.edit_message_text(
                    f"Majburiy obuna {status_text}.",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=admin_system_kb()
                )
                return
        
        except Exception as e:
            logger.error(f"admin_system_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!")


    @bot.callback_query_handler(func=lambda call: call.data.startswith('prices:') and is_admin(call.from_user.id))
    def admin_prices_callback(call: types.CallbackQuery):
        """Admin prices callbacks"""
        try:
            from database import get_settings
            from keyboards import admin_prices_kb, admin_vip_prices_kb, admin_gift_prices_kb
            
            action = call.data.split(':')[1]
            
            if action == 'star_price':
                admin_states[call.from_user.id] = {'action': 'set_star_price'}
                bot.edit_message_text(
                    "Yangi Stars narxini kiriting (so'm):",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
            
            if action == 'min_stars':
                admin_states[call.from_user.id] = {'action': 'set_min_stars'}
                bot.edit_message_text(
                    "Minimal Stars miqdorini kiriting:",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
            
            if action == 'post_min':
                admin_states[call.from_user.id] = {'action': 'set_post_min'}
                bot.edit_message_text(
                    "Post uchun minimal Stars miqdorini kiriting:",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
            
            if action == 'vip_prices':
                settings = get_settings()
                bot.edit_message_text(
                    "VIP narxlaridan birini tanlang:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=admin_vip_prices_kb(settings.get('vip_prices', {}))
                )
                return
            
            if action == 'gift_prices':
                settings = get_settings()
                bot.edit_message_text(
                    "Gift narxlarini tanlang:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=admin_gift_prices_kb(settings.get('gift_prices', {}))
                )
                return
        
        except Exception as e:
            logger.error(f"admin_prices_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!")


    @bot.callback_query_handler(func=lambda call: call.data.startswith('bonuses:') and is_admin(call.from_user.id))
    def admin_bonuses_callback(call: types.CallbackQuery):
        """Admin bonuses callbacks"""
        try:
            from keyboards import admin_referral_bonuses_kb, admin_bonus_settings_kb
            
            action = call.data.split(':')[1]
            
            if action == 'vip_discount':
                admin_states[call.from_user.id] = {'action': 'set_vip_discount'}
                bot.edit_message_text(
                    "VIP chegirma foizini kiriting (0-100):",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
            
            if action == 'referral':
                bot.edit_message_text(
                    "Referal bonusini tanlang:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=admin_referral_bonuses_kb()
                )
                return
            
            if action == 'bonus_settings':
                bot.edit_message_text(
                    "Bonus sozlamalarini tanlang:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=admin_bonus_settings_kb()
                )
                return
        
        except Exception as e:
            logger.error(f"admin_bonuses_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!")


    @bot.callback_query_handler(func=lambda call: call.data.startswith('vipprice:') and is_admin(call.from_user.id))
    def admin_vip_price_callback(call: types.CallbackQuery):
        """Admin VIP price edit"""
        try:
            duration_key = call.data.split(':')[1]
            admin_states[call.from_user.id] = {
                'action': 'set_vip_price',
                'duration_key': duration_key
            }
            bot.edit_message_text(
                f"{duration_key} uchun yangi narxni kiriting (so'm):",
                call.message.chat.id,
                call.message.message_id
            )
        except Exception as e:
            logger.error(f"admin_vip_price_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!")


    @bot.callback_query_handler(func=lambda call: call.data.startswith('giftprice:') and is_admin(call.from_user.id))
    def admin_gift_price_callback(call: types.CallbackQuery):
        """Admin gift price edit"""
        try:
            gift_key = call.data.split(':')[1]
            admin_states[call.from_user.id] = {
                'action': 'set_gift_price',
                'gift_key': gift_key
            }
            bot.edit_message_text(
                f"{gift_key} uchun yangi narxni kiriting (Stars):",
                call.message.chat.id,
                call.message.message_id
            )
        except Exception as e:
            logger.error(f"admin_gift_price_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!")


    @bot.callback_query_handler(func=lambda call: call.data.startswith('refbonus:') and is_admin(call.from_user.id))
    def admin_referral_bonus_callback(call: types.CallbackQuery):
        """Admin referral bonus edit"""
        try:
            key = call.data.split(':')[1]
            action_map = {
                'registration': 'set_referral_registration',
                'first_order': 'set_referral_first',
                'every_order': 'set_referral_every'
            }
            if key in action_map:
                admin_states[call.from_user.id] = {'action': action_map[key]}
                prompt = "Bonus miqdorini kiriting:"
                if key in ['first_order', 'every_order']:
                    prompt = "Bonus foizini kiriting (0-100):"
                bot.edit_message_text(
                    prompt,
                    call.message.chat.id,
                    call.message.message_id
                )
        except Exception as e:
            logger.error(f"admin_referral_bonus_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!")


    @bot.callback_query_handler(func=lambda call: call.data.startswith('bonusset:') and is_admin(call.from_user.id))
    def admin_bonus_settings_callback(call: types.CallbackQuery):
        """Admin bonus settings edit"""
        try:
            key = call.data.split(':')[1]
            action_map = {
                'vip_monthly': 'set_bonus_vip_monthly',
                'birthday': 'set_bonus_birthday'
            }
            if key in action_map:
                admin_states[call.from_user.id] = {'action': action_map[key]}
                bot.edit_message_text(
                    "Bonus miqdorini kiriting (Stars):",
                    call.message.chat.id,
                    call.message.message_id
                )
        except Exception as e:
            logger.error(f"admin_bonus_settings_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!")


    @bot.callback_query_handler(func=lambda call: call.data.startswith('settings:') and is_admin(call.from_user.id))
    def admin_legacy_settings_callback(call: types.CallbackQuery):
        """Legacy settings menu (compatibility)"""
        try:
            from database import get_settings
            from keyboards import admin_vip_prices_kb, admin_gift_prices_kb, admin_referral_bonuses_kb
            
            action = call.data.split(':')[1]
            
            if action == 'star_price':
                admin_states[call.from_user.id] = {'action': 'set_star_price'}
                bot.edit_message_text(
                    "Yangi Stars narxini kiriting (so'm):",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
            
            if action == 'vip':
                settings = get_settings()
                bot.edit_message_text(
                    "VIP narxlaridan birini tanlang:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=admin_vip_prices_kb(settings.get('vip_prices', {}))
                )
                return
            
            if action == 'referral':
                bot.edit_message_text(
                    "Referal bonusini tanlang:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=admin_referral_bonuses_kb()
                )
                return
            
            if action == 'gifts':
                settings = get_settings()
                bot.edit_message_text(
                    "Gift narxlarini tanlang:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=admin_gift_prices_kb(settings.get('gift_prices', {}))
                )
                return
        
        except Exception as e:
            logger.error(f"admin_legacy_settings_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!")


    @bot.callback_query_handler(func=lambda call: call.data.startswith('ticket:') and is_admin(call.from_user.id))
    def admin_ticket_callback(call: types.CallbackQuery):
        """Admin ticket callbacks"""
        try:
            from database import close_ticket, get_db
            
            parts = call.data.split(':')
            if len(parts) < 3:
                return
            
            action = parts[1]
            ticket_id = int(parts[2])
            
            if action == 'view':
                _show_ticket_details(ticket_id, call.message.chat.id, call.message.message_id)
                return
            
            if action == 'reply':
                admin_states[call.from_user.id] = {'action': 'ticket_reply', 'ticket_id': ticket_id}
                bot.edit_message_text(
                    f"Ticket #{ticket_id} uchun javob yozing:",
                    call.message.chat.id,
                    call.message.message_id
                )
                return
            
            if action == 'close':
                close_ticket(ticket_id)
                bot.answer_callback_query(call.id, "Ticket yopildi!", show_alert=True)
                
                # Notify user
                try:
                    with get_db() as conn:
                        c = conn.cursor()
                        c.execute("SELECT user_id FROM support_tickets WHERE id=?", (ticket_id,))
                        row = c.fetchone()
                        if row:
                            bot.send_message(row['user_id'], f"Ticket #{ticket_id} yopildi.")
                except Exception as e:
                    logger.error(f"User notification error: {e}")
                
                _show_support_list(call.message.chat.id, call.message.message_id)
                return
        
        except Exception as e:
            logger.error(f"admin_ticket_callback error: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "❗ Xatolik!")

    @bot.message_handler(func=lambda m: is_admin(m.from_user.id) and m.from_user.id in admin_states)
    def admin_text_handler(message: types.Message):
        """Admin text handler"""
        try:
            from database import (
                get_all_users,
                get_vip_users,
                get_user,
                get_settings,
                update_settings,
                update_balance,
                get_db,
                get_order
            )
            from config import Constants, Config
            from services.vip_service import VIPService
            from services.order_service import OrderService
            from utils import format_money
            
            state = admin_states.get(message.from_user.id, {})
            action = state.get('action')
            
            def _clear_state():
                admin_states.pop(message.from_user.id, None)
            
            if action == 'broadcast_target_id':
                user_id = _parse_int(message.text, 1, 10**12)
                if not user_id:
                    bot.reply_to(message, "❗ Faqat to'g'ri ID kiriting.")
                    return
                admin_states[message.from_user.id] = {
                    'action': 'broadcast_message',
                    'target': 'id',
                    'user_id': user_id
                }
                bot.reply_to(message, "Endi yuboriladigan xabarni yozing:")
                return
            
            if action == 'broadcast_message':
                target = state.get('target', 'all')
                sent = 0
                failed = 0
                
                if target == 'vip':
                    users = get_vip_users()
                elif target == 'id':
                    uid = state.get('user_id')
                    users = [{'user_id': uid}] if uid else []
                else:
                    users = get_all_users()
                
                if not users:
                    bot.reply_to(message, "Yuborish uchun foydalanuvchi topilmadi.")
                    _clear_state()
                    return
                
                progress_msg = bot.reply_to(message, f"📨 Xabar yuborilmoqda... 0/{len(users)}")
                delay = 1 / max(Config.MAX_BROADCAST_PER_SECOND, 1)
                
                for i, user in enumerate(users):
                    try:
                        bot.send_message(user['user_id'], message.text)
                        sent += 1
                        time.sleep(delay)
                        
                        if (i + 1) % 20 == 0:
                            try:
                                bot.edit_message_text(
                                    f"📨 Xabar yuborilmoqda... {i + 1}/{len(users)}",
                                    message.chat.id,
                                    progress_msg.message_id
                                )
                            except Exception:
                                pass
                    except Exception as e:
                        logger.error(f"Broadcast user {user['user_id']}: {e}")
                        failed += 1
                
                final_text = (
                    f"✅ Broadcast tugadi!\n\n"
                    f"Yuborildi: {sent}\n"
                    f"Xato: {failed}"
                )
                bot.send_message(message.chat.id, final_text)
                _clear_state()
                return
            
            if action == 'order_search':
                order_id = _parse_int(message.text, 1, 10**12)
                if not order_id:
                    bot.reply_to(message, "❗ Buyurtma ID noto'g'ri.")
                    return
                _show_order_details(order_id, message.chat.id)
                _clear_state()
                return
            
            if action == 'user_search':
                user_id = _parse_int(message.text, 1, 10**12)
                if not user_id:
                    bot.reply_to(message, "❗ User ID noto'g'ri.")
                    return
                _show_user_details(user_id, message.chat.id)
                _clear_state()
                return
            
            if action == 'order_reject':
                order_id = state.get('order_id')
                reason = message.text.strip() if message.text else "Sabab ko'rsatilmagan"
                success, msg = OrderService.reject_order(order_id, reason)
                if success:
                    bot.reply_to(message, f"✅ {msg}")
                    order = get_order(order_id)
                    if order:
                        try:
                            user_text = (
                                f"❌ Buyurtmangiz rad etildi\n\n"
                                f"Buyurtma #{order_id}\n"
                                f"Sabab: {reason}\n\n"
                                "Admin bilan bog'laning."
                            )
                            bot.send_message(order['user_id'], user_text)
                        except Exception as e:
                            logger.error(f"User notification error: {e}")
                else:
                    bot.reply_to(message, f"❌ {msg}")
                _clear_state()
                return
            
            if action == 'ticket_reply':
                ticket_id = state.get('ticket_id')
                reply_text = message.text.strip()
                if not reply_text:
                    bot.reply_to(message, "Javob matnini kiriting.")
                    return
                
                from database import add_ticket_message
                success = add_ticket_message(ticket_id, message.from_user.id, reply_text, is_admin=True)
                if success:
                    bot.reply_to(message, "✅ Javob yuborildi!")
                    try:
                        with get_db() as conn:
                            c = conn.cursor()
                            c.execute("SELECT user_id FROM support_tickets WHERE id=?", (ticket_id,))
                            row = c.fetchone()
                            if row:
                                bot.send_message(row['user_id'], f"💬 Admin javobi:\n\n{reply_text}")
                    except Exception as e:
                        logger.error(f"User notification error: {e}")
                else:
                    bot.reply_to(message, "❌ Xatolik!")
                _clear_state()
                return
            
            if action == 'user_addstars':
                user_id = state.get('user_id')
                amount = _parse_int(message.text, 1, 100000000)
                if not amount:
                    bot.reply_to(message, "❗ To'g'ri miqdor kiriting.")
                    return
                
                user = get_user(user_id)
                if not user:
                    bot.reply_to(message, "❗ Foydalanuvchi topilmadi!")
                    _clear_state()
                    return
                
                success = update_balance(
                    user_id,
                    amount,
                    Constants.TRANSACTION_TYPES['ADMIN_ADD'],
                    "Admin tomonidan qo'shildi"
                )
                
                if success:
                    new_balance = user['balance'] + amount
                    bot.reply_to(message, f"✅ {amount} so'm qo'shildi! Yangi balans: {new_balance} so'm")
                    try:
                        bot.send_message(user_id, f"🎁 Sizga {amount} so'm qo'shildi! Yangi balans: {new_balance} so'm")
                    except Exception as e:
                        logger.error(f"User notification error: {e}")
                else:
                    bot.reply_to(message, "❌ Xatolik!")
                _clear_state()
                return
            
            if action == 'user_deductstars':
                user_id = state.get('user_id')
                amount = _parse_int(message.text, 1, 100000000)
                if not amount:
                    bot.reply_to(message, "❗ To'g'ri miqdor kiriting.")
                    return
                
                user = get_user(user_id)
                if not user:
                    bot.reply_to(message, "❗ Foydalanuvchi topilmadi!")
                    _clear_state()
                    return
                
                if user['balance'] < amount:
                    bot.reply_to(message, "❗ Balansda yetarli mablag' yo'q.")
                    _clear_state()
                    return
                
                success = update_balance(
                    user_id,
                    -amount,
                    Constants.TRANSACTION_TYPES['ADMIN_DEDUCT'],
                    "Admin tomonidan yechildi"
                )
                
                if success:
                    new_balance = max(0, user['balance'] - amount)
                    bot.reply_to(message, f"✅ {amount} so'm yechildi! Yangi balans: {new_balance} so'm")
                    try:
                        bot.send_message(user_id, f"⚠️ Balansdan {amount} so'm yechildi. Yangi balans: {new_balance} so'm")
                    except Exception as e:
                        logger.error(f"User notification error: {e}")
                else:
                    bot.reply_to(message, "❌ Xatolik!")
                _clear_state()
                return
            
            if action == 'user_grant_vip':
                user_id = state.get('user_id')
                days = _parse_int(message.text, 1, 3650)
                if not days:
                    bot.reply_to(message, "❗ To'g'ri kun kiriting.")
                    return
                
                success, msg = VIPService.extend_vip(user_id, days)
                if success:
                    bot.reply_to(message, f"✅ {msg}")
                    try:
                        bot.send_message(user_id, f"👑 Sizga VIP status berildi! Muddat: {days} kun")
                    except Exception as e:
                        logger.error(f"User notification error: {e}")
                else:
                    bot.reply_to(message, f"❌ {msg}")
                _clear_state()
                return
            
            if action == 'user_message':
                user_id = state.get('user_id')
                text = message.text.strip()
                if not text:
                    bot.reply_to(message, "Xabar matnini kiriting.")
                    return
                
                try:
                    bot.send_message(user_id, text)
                    bot.reply_to(message, "✅ Xabar yuborildi!")
                except Exception as e:
                    logger.error(f"User notification error: {e}")
                    bot.reply_to(message, "❌ Xabar yuborilmadi!")
                _clear_state()
                return
            
            if action == 'set_star_price':
                value = _parse_int(message.text, 100, 100000000)
                if value is None:
                    bot.reply_to(message, "❗ To'g'ri narx kiriting.")
                    return
                update_settings(star_price=value)
                bot.reply_to(message, f"✅ Stars narxi yangilandi: {value} so'm")
                _clear_state()
                return
            
            if action == 'set_min_stars':
                value = _parse_int(message.text, 1, 1000000)
                if value is None:
                    bot.reply_to(message, "❗ To'g'ri miqdor kiriting.")
                    return
                update_settings(min_stars=value)
                bot.reply_to(message, f"✅ Minimal Stars yangilandi: {value}")
                _clear_state()
                return
            
            if action == 'set_post_min':
                value = _parse_int(message.text, 1, 1000000)
                if value is None:
                    bot.reply_to(message, "❗ To'g'ri miqdor kiriting.")
                    return
                update_settings(post_min=value)
                bot.reply_to(message, f"✅ Post minimal yangilandi: {value}")
                _clear_state()
                return
            
            if action == 'set_vip_discount':
                value = _parse_int(message.text, 0, 100)
                if value is None:
                    bot.reply_to(message, "❗ 0-100 oralig'ida kiriting.")
                    return
                update_settings(vip_discount=value)
                bot.reply_to(message, f"✅ VIP chegirma yangilandi: {value}%")
                _clear_state()
                return
            
            if action == 'set_vip_price':
                duration_key = state.get('duration_key')
                value = _parse_int(message.text, 1000, 100000000)
                if value is None or not duration_key:
                    bot.reply_to(message, "❗ To'g'ri narx kiriting.")
                    return
                settings = get_settings()
                vip_prices = settings.get('vip_prices', {})
                vip_prices[duration_key] = value
                update_settings(vip_prices=vip_prices)
                bot.reply_to(message, f"✅ VIP narx yangilandi: {duration_key} = {value} so'm")
                _clear_state()
                return
            
            if action == 'set_gift_price':
                gift_key = state.get('gift_key')
                value = _parse_int(message.text, 1, 1000000)
                if value is None or not gift_key:
                    bot.reply_to(message, "❗ To'g'ri narx kiriting.")
                    return
                settings = get_settings()
                gift_prices = settings.get('gift_prices', {})
                gift_prices[gift_key] = value
                update_settings(gift_prices=gift_prices)
                bot.reply_to(message, f"✅ Gift narxi yangilandi: {gift_key} = {value} Stars")
                _clear_state()
                return
            
            if action == 'set_referral_registration':
                value = _parse_int(message.text, 0, 100000)
                if value is None:
                    bot.reply_to(message, "❗ To'g'ri bonus kiriting.")
                    return
                update_settings(referral_bonus_registration=value)
                bot.reply_to(message, f"✅ Registratsiya bonusi: {value} Stars")
                _clear_state()
                return
            
            if action == 'set_referral_first':
                value = _parse_int(message.text, 0, 100)
                if value is None:
                    bot.reply_to(message, "❗ 0-100 oralig'ida kiriting.")
                    return
                update_settings(referral_bonus_first_order=value)
                bot.reply_to(message, f"✅ Birinchi buyurtma bonusi: {value}%")
                _clear_state()
                return
            
            if action == 'set_referral_every':
                value = _parse_int(message.text, 0, 100)
                if value is None:
                    bot.reply_to(message, "❗ 0-100 oralig'ida kiriting.")
                    return
                update_settings(referral_bonus_every_order=value)
                bot.reply_to(message, f"✅ Har buyurtma bonusi: {value}%")
                _clear_state()
                return
            
            if action == 'set_bonus_vip_monthly':
                value = _parse_int(message.text, 0, 1000000)
                if value is None:
                    bot.reply_to(message, "❗ To'g'ri bonus kiriting.")
                    return
                settings = get_settings()
                bonus_settings = settings.get('bonus_settings', {})
                bonus_settings['vip_monthly_bonus'] = value
                update_settings(bonus_settings=bonus_settings)
                bot.reply_to(message, f"✅ VIP oylik bonus yangilandi: {value} Stars")
                _clear_state()
                return
            
            if action == 'set_bonus_birthday':
                value = _parse_int(message.text, 0, 1000000)
                if value is None:
                    bot.reply_to(message, "❗ To'g'ri bonus kiriting.")
                    return
                settings = get_settings()
                bonus_settings = settings.get('bonus_settings', {})
                bonus_settings['birthday_bonus'] = value
                update_settings(bonus_settings=bonus_settings)
                bot.reply_to(message, f"✅ Tug'ilgan kun bonusi: {value} Stars")
                _clear_state()
                return
            
            if action == 'set_card_number':
                card_number = message.text.strip()
                if not card_number:
                    bot.reply_to(message, "❗ Karta raqamini kiriting.")
                    return
                update_settings(card_number=card_number)
                bot.reply_to(message, "✅ Karta raqam yangilandi.")
                _clear_state()
                return
            
            if action == 'set_card_owner':
                card_owner = message.text.strip()
                if not card_owner:
                    bot.reply_to(message, "❗ Karta egasini kiriting.")
                    return
                update_settings(card_owner=card_owner)
                bot.reply_to(message, "✅ Karta egasi yangilandi.")
                _clear_state()
                return
            
            if action == 'set_channel_id':
                channel_id = message.text.strip()
                if channel_id.lower() in ['off', '0', 'yoq', "yo'q", 'null', '-']:
                    channel_id = None
                update_settings(channel_id=channel_id)
                bot.reply_to(message, "✅ Kanal ID yangilandi.")
                _clear_state()
                return
        
        except Exception as e:
            logger.error(f"admin_text_handler error: {e}", exc_info=True)
    
    logger.info("✅ Admin handlers registered successfully")
