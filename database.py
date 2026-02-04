"""
Stars Shop Bot - Database Layer
Professional Version - 100% Working
"""
import sqlite3
import json
import time
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


@contextmanager
def get_db():
    """Database connection context manager"""
    from config import Config
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database"""
    from config import DefaultSettings
    
    with get_db() as conn:
        c = conn.cursor()
        
        # USERS table
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            balance INTEGER DEFAULT 0,
            is_vip INTEGER DEFAULT 0,
            vip_expires_at INTEGER,
            referral_code TEXT UNIQUE,
            referred_by INTEGER,
            total_earned_stars INTEGER DEFAULT 0,
            created_at INTEGER NOT NULL,
            last_active INTEGER
        )
        """)
        
        # SETTINGS table
        c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK(id=1),
            star_price INTEGER NOT NULL DEFAULT 1000,
            min_stars INTEGER NOT NULL DEFAULT 50,
            post_min INTEGER NOT NULL DEFAULT 50,
            vip_discount INTEGER NOT NULL DEFAULT 20,
            vip_prices TEXT NOT NULL,
            referral_bonus_registration INTEGER DEFAULT 10,
            referral_bonus_first_order INTEGER DEFAULT 5,
            referral_bonus_every_order INTEGER DEFAULT 2,
            bonus_settings TEXT,
            channel_id TEXT,
            force_subscription INTEGER DEFAULT 0,
            gift_prices TEXT NOT NULL
        )
        """)
        
        # Default settings
        c.execute("SELECT id FROM settings WHERE id=1")
        if not c.fetchone():
            c.execute("""
            INSERT INTO settings (
                id, vip_prices, bonus_settings, gift_prices
            ) VALUES (?, ?, ?, ?)
            """, (
                1,
                json.dumps(DefaultSettings.VIP_PRICES),
                json.dumps(DefaultSettings.BONUS_SETTINGS),
                json.dumps(DefaultSettings.GIFT_PRICES)
            ))
        
        # ORDERS table
        c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            detail TEXT,
            price_per_star INTEGER NOT NULL,
            discount_percent INTEGER DEFAULT 0,
            total_sum INTEGER NOT NULL,
            payment_method TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            confirmed_at INTEGER,
            proof_msg_id INTEGER,
            admin_note TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)
        
        # TRANSACTIONS table
        c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            description TEXT,
            order_id INTEGER,
            created_at INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
        """)
        
        # MESSAGES table
        c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            target TEXT NOT NULL,
            message TEXT NOT NULL,
            sent_at INTEGER NOT NULL,
            sent_count INTEGER DEFAULT 0,
            failed_count INTEGER DEFAULT 0
        )
        """)
        
        # SUPPORT_TICKETS table
        c.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            status TEXT DEFAULT 'open',
            created_at INTEGER NOT NULL,
            closed_at INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)
        
        # SUPPORT_MESSAGES table
        c.execute("""
        CREATE TABLE IF NOT EXISTS support_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            is_admin INTEGER DEFAULT 0,
            message TEXT NOT NULL,
            sent_at INTEGER NOT NULL,
            FOREIGN KEY (ticket_id) REFERENCES support_tickets(id)
        )
        """)
        
        # Create indexes
        c.execute("CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_tickets_user ON support_tickets(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_tickets_status ON support_tickets(status)")
        
        logger.info("Database initialized successfully")


# ============ USER OPERATIONS ============

def create_user(user_id: int, username: Optional[str], full_name: str, 
                referred_by: Optional[int] = None) -> bool:
    """Create new user"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            referral_code = f"ref_{user_id}"
            
            c.execute("""
            INSERT INTO users (
                user_id, username, full_name, referral_code, 
                referred_by, created_at, last_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, full_name, referral_code, 
                  referred_by, int(time.time()), int(time.time())))
            
            return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        logger.error(f"create_user error: {e}")
        return False


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
            row = c.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"get_user error: {e}")
        return None


def update_user(user_id: int, **kwargs) -> bool:
    """Update user"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            
            fields = []
            values = []
            for key, value in kwargs.items():
                fields.append(f"{key}=?")
                values.append(value)
            
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(fields)} WHERE user_id=?"
            
            c.execute(query, values)
            return True
    except Exception as e:
        logger.error(f"update_user error: {e}")
        return False


def get_user_by_referral(referral_code: str) -> Optional[Dict[str, Any]]:
    """Get user by referral code"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE referral_code=?", (referral_code,))
            row = c.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"get_user_by_referral error: {e}")
        return None


def update_balance(user_id: int, amount: int, 
                   transaction_type: str, description: str = "",
                   order_id: Optional[int] = None) -> bool:
    """Update balance and create transaction"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            
            c.execute("""
            UPDATE users 
            SET balance = balance + ? 
            WHERE user_id=?
            """, (amount, user_id))
            
            c.execute("""
            INSERT INTO transactions (
                user_id, type, amount, description, order_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, transaction_type, amount, description, 
                  order_id, int(time.time())))
            
            return True
    except Exception as e:
        logger.error(f"update_balance error: {e}")
        return False


def get_all_users(limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
    """Get all users"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("""
            SELECT * FROM users 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
            """, (limit, offset))
            return [dict(row) for row in c.fetchall()]
    except Exception as e:
        logger.error(f"get_all_users error: {e}")
        return []


def get_vip_users() -> List[Dict[str, Any]]:
    """Get VIP users"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            current_time = int(time.time())
            c.execute("""
            SELECT * FROM users 
            WHERE is_vip=1 AND vip_expires_at > ?
            ORDER BY vip_expires_at DESC
            """, (current_time,))
            return [dict(row) for row in c.fetchall()]
    except Exception as e:
        logger.error(f"get_vip_users error: {e}")
        return []


def get_referrals(user_id: int) -> List[Dict[str, Any]]:
    """Get user referrals"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("""
            SELECT * FROM users 
            WHERE referred_by=?
            ORDER BY created_at DESC
            """, (user_id,))
            return [dict(row) for row in c.fetchall()]
    except Exception as e:
        logger.error(f"get_referrals error: {e}")
        return []


# ============ SETTINGS OPERATIONS ============

def get_settings() -> Dict[str, Any]:
    """Get settings"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM settings WHERE id=1")
            row = c.fetchone()
            
            if row:
                settings = dict(row)
                settings['vip_prices'] = json.loads(settings['vip_prices'])
                settings['bonus_settings'] = json.loads(settings['bonus_settings']) if settings['bonus_settings'] else {}
                settings['gift_prices'] = json.loads(settings['gift_prices'])
                return settings
            return {}
    except Exception as e:
        logger.error(f"get_settings error: {e}")
        return {}


def update_settings(**kwargs) -> bool:
    """Update settings"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            
            if 'vip_prices' in kwargs:
                kwargs['vip_prices'] = json.dumps(kwargs['vip_prices'])
            if 'bonus_settings' in kwargs:
                kwargs['bonus_settings'] = json.dumps(kwargs['bonus_settings'])
            if 'gift_prices' in kwargs:
                kwargs['gift_prices'] = json.dumps(kwargs['gift_prices'])
            
            fields = []
            values = []
            for key, value in kwargs.items():
                fields.append(f"{key}=?")
                values.append(value)
            
            query = f"UPDATE settings SET {', '.join(fields)} WHERE id=1"
            c.execute(query, values)
            
            return True
    except Exception as e:
        logger.error(f"update_settings error: {e}")
        return False


# ============ ORDER OPERATIONS ============

def create_order(user_id: int, order_type: str, amount: int,
                 detail: Optional[str], price_per_star: int,
                 discount_percent: int, total_sum: int,
                 payment_method: str) -> Optional[int]:
    """Create order"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("""
            INSERT INTO orders (
                user_id, type, amount, detail, price_per_star,
                discount_percent, total_sum, payment_method,
                status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
            """, (user_id, order_type, amount, detail, price_per_star,
                  discount_percent, total_sum, payment_method, int(time.time())))
            
            return c.lastrowid
    except Exception as e:
        logger.error(f"create_order error: {e}")
        return None


def get_order(order_id: int) -> Optional[Dict[str, Any]]:
    """Get order by ID"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM orders WHERE id=?", (order_id,))
            row = c.fetchone()
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"get_order error: {e}")
        return None


def update_order(order_id: int, **kwargs) -> bool:
    """Update order"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            
            fields = []
            values = []
            for key, value in kwargs.items():
                fields.append(f"{key}=?")
                values.append(value)
            
            values.append(order_id)
            query = f"UPDATE orders SET {', '.join(fields)} WHERE id=?"
            
            c.execute(query, values)
            return True
    except Exception as e:
        logger.error(f"update_order error: {e}")
        return False


def get_user_orders(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """Get user orders"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("""
            SELECT * FROM orders 
            WHERE user_id=?
            ORDER BY created_at DESC
            LIMIT ?
            """, (user_id, limit))
            return [dict(row) for row in c.fetchall()]
    except Exception as e:
        logger.error(f"get_user_orders error: {e}")
        return []


def get_orders_by_status(status: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get orders by status"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("""
            SELECT * FROM orders 
            WHERE status=?
            ORDER BY created_at DESC
            LIMIT ?
            """, (status, limit))
            return [dict(row) for row in c.fetchall()]
    except Exception as e:
        logger.error(f"get_orders_by_status error: {e}")
        return []


# ============ TRANSACTION OPERATIONS ============

def get_user_transactions(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Get user transactions"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("""
            SELECT * FROM transactions 
            WHERE user_id=?
            ORDER BY created_at DESC
            LIMIT ?
            """, (user_id, limit))
            return [dict(row) for row in c.fetchall()]
    except Exception as e:
        logger.error(f"get_user_transactions error: {e}")
        return []


# ============ SUPPORT OPERATIONS ============

def create_ticket(user_id: int) -> Optional[int]:
    """Create support ticket"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("""
            INSERT INTO support_tickets (user_id, created_at)
            VALUES (?, ?)
            """, (user_id, int(time.time())))
            return c.lastrowid
    except Exception as e:
        logger.error(f"create_ticket error: {e}")
        return None


def add_ticket_message(ticket_id: int, sender_id: int, 
                       message: str, is_admin: bool = False) -> bool:
    """Add message to ticket"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("""
            INSERT INTO support_messages (
                ticket_id, sender_id, is_admin, message, sent_at
            ) VALUES (?, ?, ?, ?, ?)
            """, (ticket_id, sender_id, 1 if is_admin else 0, 
                  message, int(time.time())))
            
            c.execute("""
            UPDATE support_tickets 
            SET status=? 
            WHERE id=?
            """, ('answered' if is_admin else 'open', ticket_id))
            
            return True
    except Exception as e:
        logger.error(f"add_ticket_message error: {e}")
        return False


def get_open_tickets() -> List[Dict[str, Any]]:
    """Get open tickets"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("""
            SELECT * FROM support_tickets 
            WHERE status IN ('open', 'answered')
            ORDER BY created_at DESC
            """)
            return [dict(row) for row in c.fetchall()]
    except Exception as e:
        logger.error(f"get_open_tickets error: {e}")
        return []


def close_ticket(ticket_id: int) -> bool:
    """Close ticket"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("""
            UPDATE support_tickets 
            SET status='closed', closed_at=?
            WHERE id=?
            """, (int(time.time()), ticket_id))
            return True
    except Exception as e:
        logger.error(f"close_ticket error: {e}")
        return False


def get_ticket_messages(ticket_id: int) -> List[Dict[str, Any]]:
    """Get ticket messages"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("""
            SELECT * FROM support_messages 
            WHERE ticket_id=?
            ORDER BY sent_at ASC
            """, (ticket_id,))
            return [dict(row) for row in c.fetchall()]
    except Exception as e:
        logger.error(f"get_ticket_messages error: {e}")
        return []


# ============ STATISTICS ============

def get_stats() -> Dict[str, Any]:
    """Get statistics"""
    try:
        with get_db() as conn:
            c = conn.cursor()
            
            stats = {}
            
            c.execute("SELECT COUNT(*) FROM users")
            stats['total_users'] = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM users WHERE is_vip=1")
            stats['vip_users'] = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM orders")
            stats['total_orders'] = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM orders WHERE status='pending'")
            stats['pending_orders'] = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM orders WHERE status='paid'")
            stats['paid_orders'] = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM orders WHERE status='confirmed'")
            stats['confirmed_orders'] = c.fetchone()[0]
            
            c.execute("SELECT SUM(total_sum) FROM orders WHERE status='confirmed'")
            stats['total_revenue'] = c.fetchone()[0] or 0
            
            c.execute("SELECT COUNT(*) FROM support_tickets WHERE status='open'")
            stats['open_tickets'] = c.fetchone()[0]
            
            return stats
    except Exception as e:
        logger.error(f"get_stats error: {e}")
        return {}
