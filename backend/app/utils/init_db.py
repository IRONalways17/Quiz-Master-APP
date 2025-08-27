from backend.app.database import db
from backend.app.models import Admin
from flask import current_app

def create_default_admin():
    """Create default admin user if not exists"""
    try:
        # Check if admin already exists
        admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@quizmaster.com')
        admin = Admin.query.filter_by(email=admin_email).first()
        
        if not admin:
            # Create new admin
            admin = Admin(
                email=admin_email,
                full_name='System Administrator'
            )
            admin.set_password(current_app.config.get('ADMIN_PASSWORD', 'admin123'))
            
            db.session.add(admin)
            db.session.commit()
            print(f"Default admin created: {admin_email}")
        else:
            print(f"Admin already exists: {admin_email}")
            
    except Exception as e:
        print(f"Error creating default admin: {str(e)}")
        db.session.rollback() 
