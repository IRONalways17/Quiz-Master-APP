from datetime import datetime
from sqlalchemy.orm import relationship
from app.database import db
from sqlalchemy.ext.hybrid import hybrid_property
import re

class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), nullable=False)
    chapter_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subject = relationship('Subject', back_populates='chapters')
    quizzes = relationship('Quiz', back_populates='chapter', cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.slug and self.name:
            self.slug = self.generate_unique_slug()

    def generate_unique_slug(self):
        """Generate unique slug for chapter"""
        if not self.name:
            return ""
        
        base_slug = self.generate_slug(self.name)
        
        # Check for duplicates in same subject
        if self.subject_id:
            existing = Chapter.query.filter(
                Chapter.slug == base_slug,
                Chapter.subject_id == self.subject_id,
                Chapter.id != (self.id or 0)
            ).first()
            
            if not existing:
                return base_slug
        
        # Make slug unique if needed
        counter = 1
        unique_slug = f"{base_slug}-{counter}"
        
        while Chapter.query.filter(
            Chapter.slug == unique_slug,
            Chapter.subject_id == self.subject_id if self.subject_id else True
        ).first():
            counter += 1
            unique_slug = f"{base_slug}-{counter}"
            
        return unique_slug

    @staticmethod
    def generate_slug(name):
        """Convert name to URL-safe slug"""
        return re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')

    def to_dict(self, include_quizzes=False):
        """Convert chapter to dictionary"""
        quizzes_count = len([q for q in self.quizzes if q.is_active])
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'chapter_number': self.chapter_number,
            'description': self.description,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'subject_slug': self.subject.slug if self.subject else None,
            'quizzes_count': quizzes_count,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_quizzes:
            data['quizzes'] = [quiz.to_dict() for quiz in self.quizzes if quiz.is_active]
        return data

    @classmethod
    def get_duplicate_names(cls):
        """Get chapter names used across multiple subjects"""
        from sqlalchemy import func
        from app.database import db
        
        result = db.session.query(
            cls.name,
            func.count(func.distinct(cls.subject_id)).label('subject_count')
        ).group_by(cls.name).having(
            func.count(func.distinct(cls.subject_id)) > 1
        ).all()
        
        return [{'name': name, 'subject_count': count} for name, count in result]

    def __repr__(self):
        return f'<Chapter {self.name}>' 