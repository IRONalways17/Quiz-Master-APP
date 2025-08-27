web: cd backend && gunicorn --bind 0.0.0.0:$PORT run:app
release: cd backend && python -c "from app import create_app; from app.database import db; app = create_app(); app.app_context().push(); db.create_all()"
