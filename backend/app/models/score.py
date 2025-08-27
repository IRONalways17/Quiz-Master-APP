from datetime import datetime
from sqlalchemy.orm import relationship
import json
from backend.app.database import db

class Score(db.Model):
    __tablename__ = 'scores'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    
    # Score details
    score = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    passed = db.Column(db.Boolean, default=False)
    
    # Time tracking
    started_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=False)
    time_taken_seconds = db.Column(db.Integer)
    
    # Store answers as JSON
    answers = db.Column(db.Text)  # JSON object with question_id: answer mapping
    
    # Attempt tracking
    attempt_number = db.Column(db.Integer, default=1)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='scores')
    quiz = relationship('Quiz', back_populates='scores')
    
    def get_answers(self):
        """Get answers as dictionary"""
        try:
            return json.loads(self.answers) if self.answers else {}
        except:
            return {}
    
    def set_answers(self, answers_dict):
        """Set answers from dictionary"""
        self.answers = json.dumps(answers_dict)
    
    def calculate_time_taken(self):
        """Calculate time taken in seconds"""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.time_taken_seconds = int(delta.total_seconds())
    
    def to_dict(self):
        """Convert score to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quiz_id': self.quiz_id,
            'quiz_title': self.quiz.title if self.quiz else None,
            'subject_name': self.quiz.chapter.subject.name if self.quiz and self.quiz.chapter and self.quiz.chapter.subject else None,
            'score': self.score,
            'max_score': self.max_score,
            'percentage': self.percentage,
            'passed': self.passed,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'time_taken_seconds': self.time_taken_seconds,
            'attempt_number': self.attempt_number,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def to_dict_with_details(self):
        """Convert score to dictionary with answer details"""
        data = self.to_dict()
        data['answers'] = self.get_answers()
        return data
    
    def __repr__(self):
        return f'<Score User:{self.user_id} Quiz:{self.quiz_id} Score:{self.score}/{self.max_score}>' 
