#!/usr/bin/env python3
"""
Script to create test reminders for users
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import User, Reminder
from app.database import db
from datetime import datetime

def create_test_reminders():
    """Create test reminders for users"""
    app = create_app()
    with app.app_context():
        print("Creating test reminders...")
        print("=" * 50)
        
        # Get all users
        users = User.query.filter_by(is_active=True).all()
        
        if not users:
            print("No users found in database!")
            return
        
        print(f"Found {len(users)} users")
        
        for user in users:
            print(f"\nCreating reminders for user: {user.full_name} ({user.email})")            
            existing_reminders = Reminder.query.filter_by(user_id=user.id).count()
            if existing_reminders > 0:
                print(f"User already has {existing_reminders} reminders")
                continue
            reminders = [
                Reminder(
                    user_id=user.id,
                    reminder_type='new_quiz',
                    message=f'New quiz available in Mathematics! Check it out.',
                    is_read=False,
                    created_at=datetime.utcnow()
                ),
                Reminder(
                    user_id=user.id,
                    reminder_type='inactive_user',
                    message=f'Welcome back! We missed you. Take a quiz to keep your skills sharp.',
                    is_read=False,
                    created_at=datetime.utcnow()
                ),
                Reminder(
                    user_id=user.id,
                    reminder_type='general',
                    message=f'Your monthly report is ready. Check your performance statistics.',
                    is_read=True,
                    created_at=datetime.utcnow()
                )
            ]
            
            for reminder in reminders:
                db.session.add(reminder)
            
            db.session.commit()
            print(f"Created {len(reminders)} reminders")
        
        print("\n" + "=" * 50)
        print("Test reminders created successfully!")
        print("\n To see reminders:")
        print("1. Log in as a user")
        print("2. Go to the dashboard")
        print("3. Look for the 'Reminders' section")
        print("4. You can mark reminders as read or delete them")

if __name__ == "__main__":
    create_test_reminders() 