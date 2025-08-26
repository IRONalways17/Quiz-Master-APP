from datetime import datetime
from sqlalchemy.orm import relationship
import json
from app.database import db

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default='multiple_choice')  # multiple_choice, true_false
    points = db.Column(db.Integer, default=1)
    
    # Store options as JSON
    options = db.Column(db.Text, nullable=False)  # JSON array of options
    correct_answer = db.Column(db.String(255), nullable=False)  # For MCQ: option index, for T/F: 'true' or 'false'
    explanation = db.Column(db.Text)  # Explanation for the correct answer
    
    order = db.Column(db.Integer, default=0)  # Question order in quiz
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quiz = relationship('Quiz', back_populates='questions')
    
    def get_options(self):
        """Get options as list"""
        try:
            return json.loads(self.options) if self.options else []
        except:
            return []
    
    def set_options(self, options_list):
        """Set options from list"""
        self.options = json.dumps(options_list)
    
    def to_dict(self):
        """Convert question to dictionary"""
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'points': self.points,
            'options': self.get_options(),
            'correct_answer': self.correct_answer,
            'explanation': self.explanation,
            'order': self.order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def to_dict_for_quiz(self):
        """Convert question to dictionary for quiz taking (hide correct answer)"""
        return {
            'id': self.id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'points': self.points,
            'options': self.get_options(),
            'order': self.order
        }
    
    def __repr__(self):
        return f'<Question {self.id} for Quiz {self.quiz_id}>' 