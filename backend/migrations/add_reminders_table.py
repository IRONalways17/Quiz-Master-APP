#!/usr/bin/env python3
"""
Migration script to add reminders table
Run this to create the reminders table in your database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import db

def run_migration():
    app = create_app()
    with app.app_context():
        # Create reminders table using text() for raw SQL
        from sqlalchemy import text
        
        with db.engine.connect() as conn:
            # Create reminders table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    reminder_type VARCHAR(50) NOT NULL,
                    is_read BOOLEAN NOT NULL DEFAULT 0,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """))
            
            # Create index for better performance
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders(user_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_reminders_is_read ON reminders(is_read)
            """))
            
            conn.commit()
        
        print("✅ Reminders table created successfully!")
        print("✅ Indexes created for better performance!")

if __name__ == '__main__':
    run_migration()