from datetime import datetime
from sqlalchemy.orm import relationship
from backend.app.database import db
from sqlalchemy.ext.hybrid import hybrid_property
import re

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), nullable=False)
    description = db.Column(db.Text)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    passing_score = db.Column(db.Integer, default=60)
    max_attempts = db.Column(db.Integer, default=3)
    
    # Scheduling
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chapter = relationship('Chapter', back_populates='quizzes')
    questions = relationship('Question', back_populates='quiz', cascade='all, delete-orphan')
    scores = relationship('Score', back_populates='quiz', cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.slug and self.title:
            self.slug = self.generate_slug(self.title)

    @staticmethod
    def generate_slug(title):
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
        return slug
    
    @property
    def is_available(self):
        """Check if quiz is currently available based on schedule"""
        now = datetime.utcnow()
        return self.is_active and self.start_date <= now <= self.end_date
    
    @property
    def status(self):
        """Get current status of the quiz"""
        now = datetime.utcnow()
        if not self.is_active:
            return 'inactive'
        elif now < self.start_date:
            return 'upcoming'
        elif now > self.end_date:
            return 'expired'
        else:
            return 'active'
    
    def to_dict(self, include_questions=False):
        """Convert quiz to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'chapter_id': self.chapter_id,
            'chapter_name': self.chapter.name if self.chapter else None,
            'subject_name': self.chapter.subject.name if self.chapter and self.chapter.subject else None,
            'duration_minutes': self.duration_minutes,
            'passing_score': self.passing_score,
            'max_attempts': self.max_attempts,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'is_available': self.is_available,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'questions_count': len(self.questions) if self.questions else 0,
            'total_questions': len(self.questions) if self.questions else 0
        }
        
        if include_questions:
            data['questions'] = [q.to_dict_for_quiz() for q in self.questions if q.is_active]
        
        return data
    
    def __repr__(self):
        return f'<Quiz {self.title}>' 
