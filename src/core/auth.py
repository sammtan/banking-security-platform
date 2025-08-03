import hashlib
from typing import Optional, Dict
from PySide6.QtCore import QObject, Signal

class AuthManager(QObject):
    # Signals
    login_success = Signal(dict)  # user_info
    login_failed = Signal(str)    # error_message
    logout_success = Signal()
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_user = None
        
    def login(self, username: str, password: str) -> bool:
        """Authenticate user with username and password"""
        if not self.db.conn:
            self.login_failed.emit("Database not connected")
            return False
            
        # Hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Query database
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT id, username, role FROM users 
            WHERE username = ? AND password_hash = ?
        """, (username, password_hash))
        
        user = cursor.fetchone()
        
        if user:
            # Update last login
            cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (user[0],))
            self.db.conn.commit()
            
            # Store user info
            self.current_user = {
                'id': user[0],
                'username': user[1],
                'role': user[2]
            }
            
            self.login_success.emit(self.current_user)
            return True
        else:
            self.login_failed.emit("Invalid username or password")
            return False
            
    def logout(self):
        """Logout current user"""
        self.current_user = None
        self.logout_success.emit()
        
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.current_user is not None
        
    def has_permission(self, permission: str) -> bool:
        """Check if current user has specific permission"""
        if not self.current_user:
            return False
            
        # Simple role-based permissions
        permissions = {
            'admin': ['view', 'edit', 'delete', 'manage_users', 'export'],
            'analyst': ['view', 'export'],
            'viewer': ['view']
        }
        
        user_role = self.current_user.get('role', 'viewer')
        return permission in permissions.get(user_role, [])
        
    def create_user(self, username: str, password: str, role: str = 'analyst') -> bool:
        """Create a new user (admin only)"""
        if not self.has_permission('manage_users'):
            return False
            
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor = self.db.conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, (username, password_hash, role))
            self.db.conn.commit()
            return True
        except:
            return False