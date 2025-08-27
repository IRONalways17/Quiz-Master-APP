release: python -c "from backend.app import create_app; app = create_app(); app.app_context().push(); from backend.app.database import db; db.create_all()"
web: gunicorn --bind 0.0.0.0:$PORT wsgi:app
