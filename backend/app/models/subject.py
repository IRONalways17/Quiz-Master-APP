from datetime import datetime
from sqlalchemy.orm import relationship
from backend.app.database import db
from sqlalchemy.ext.hybrid import hybrid_property
import re

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#3498db')  # Hex color for UI
    icon = db.Column(db.String(50), default='book')  # Icon name for UI
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chapters = relationship('Chapter', back_populates='subject', cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.slug and self.name:
            self.slug = self.generate_slug(self.name)

    @staticmethod
    def generate_slug(name):
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')
        return slug

    def to_dict(self, include_chapters=False):
        """Convert subject to dictionary"""
        chapters_count = len([c for c in self.chapters if c.is_active])
        quizzes_count = sum(len([q for q in c.quizzes if q.is_active]) for c in self.chapters if c.is_active)
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'code': self.code,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'is_active': self.is_active,
            'chapters_count': chapters_count,
            'quizzes_count': quizzes_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_chapters:
            data['chapters'] = [chapter.to_dict() for chapter in self.chapters if chapter.is_active]
        return data

    def __repr__(self):
        return f'<Subject {self.name}>' 
