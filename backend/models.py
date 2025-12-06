"""
Database models for Todo application
"""
from datetime import datetime
from backend.database import db

class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Todo(BaseModel):
    """Todo model"""
    __tablename__ = 'todos'
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    priority = db.Column(db.String(20), default='medium', nullable=False)  # low, medium, high
    due_date = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    tags = db.Column(db.String(200), nullable=True)  # Comma-separated tags
    
    # Relationships
    user = db.relationship('User', backref=db.backref('todos', lazy=True))
    notifications = db.relationship('Notification', backref='todo', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id,
            'category': self.category,
            'tags': self.tags.split(',') if self.tags else []
        }
    
    def __repr__(self):
        return f'<Todo {self.id}: {self.title}>'


class User(BaseModel):
    """User model"""
    __tablename__ = 'users'
    
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    email_notifications_enabled = db.Column(db.Boolean, default=True, nullable=False)
    browser_notifications_enabled = db.Column(db.Boolean, default=True, nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'email_notifications_enabled': self.email_notifications_enabled,
            'browser_notifications_enabled': self.browser_notifications_enabled
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class Notification(BaseModel):
    """Notification model"""
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    todo_id = db.Column(db.Integer, db.ForeignKey('todos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # email, browser, both
    sent = db.Column(db.Boolean, default=False, nullable=False)
    sent_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'todo_id': self.todo_id,
            'user_id': self.user_id,
            'message': self.message,
            'type': self.type,
            'sent': self.sent,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.message[:50]}>'

