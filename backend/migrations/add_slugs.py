#!/usr/bin/env python3
"""
Migration script to add slug fields to existing subjects, chapters, and quizzes.
Run this script to populate slugs for existing data.
"""

import sys
import os
import re
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import db
from app.models import Subject, Chapter, Quiz

def generate_slug(name):
    """Generate a slug from a name"""
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')
    return slug

def add_slugs():
    """Add slugs to existing records"""
    app = create_app()
    
    with app.app_context():
        print("Starting migration: Adding slugs to existing records...")
        
        # Add slugs to subjects
        subjects = Subject.query.all()
        for subject in subjects:
            if not subject.slug:
                subject.slug = generate_slug(subject.name)
                print(f"Added slug '{subject.slug}' to subject '{subject.name}'")
        
        # Add slugs to chapters
        chapters = Chapter.query.all()
        for chapter in chapters:
            if not chapter.slug:
                chapter.slug = generate_slug(chapter.name)
                print(f"Added slug '{chapter.slug}' to chapter '{chapter.name}'")
        
        # Add slugs to quizzes
        quizzes = Quiz.query.all()
        for quiz in quizzes:
            if not quiz.slug:
                quiz.slug = generate_slug(quiz.title)
                print(f"Added slug '{quiz.slug}' to quiz '{quiz.title}'")
        
        # Commit all changes
        try:
            db.session.commit()
            print("Migration completed successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {e}")
            return False
        
        return True

if __name__ == '__main__':
    success = add_slugs()
    sys.exit(0 if success else 1) 