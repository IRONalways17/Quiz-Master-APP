# Quiz Master - Interactive Quiz Management System

A comprehensive web-based quiz management system built with Flask, Vue.js, and Celery for asynchronous task processing.

## 🚀 Features

### For Users
- **Interactive Quiz Taking**: Take quizzes with real-time scoring
- **Progress Tracking**: View your quiz history and performance statistics
- **CSV Export**: Export your quiz scores to CSV format with email notifications
- **Personal Dashboard**: Track your progress across different subjects
- **Reminder System**: Get notifications for available quizzes and inactivity

### For Administrators
- **Subject Management**: Create and manage subjects with chapters
- **Quiz Creation**: Build quizzes with multiple-choice questions
- **User Management**: Monitor user activity and performance
- **Report Generation**: Export comprehensive reports in CSV format
- **Analytics Dashboard**: View system-wide statistics and performance metrics

### System Features
- **Asynchronous Processing**: Background tasks for CSV exports and email notifications
- **Email Notifications**: Automated email alerts for completed exports
- **Redis Caching**: Performance optimization with Redis caching
- **Responsive Design**: Mobile-friendly interface
- **Real-time Updates**: Live progress tracking and notifications

## 🛠️ Technology Stack

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: ORM for database management
- **Celery**: Asynchronous task processing
- **Redis**: Message broker and caching
- **SMTP**: Email notifications
- **Pandas**: CSV data processing

### Frontend
- **Vue.js 3**: Progressive JavaScript framework
- **Bootstrap 5**: CSS framework for responsive design
- **Axios**: HTTP client for API communication
- **Vue Router**: Client-side routing

### Database
- **SQLite**: Lightweight database (development)
- **PostgreSQL**: Production-ready database (recommended)

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Redis Server
- Git

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd quiz-master
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Configure Environment Variables
```bash
cp env.example .env
```

Edit `.env` file with your configuration:
```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database
DATABASE_URL=sqlite:///quizmaster.db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Admin Credentials
ADMIN_EMAIL=admin@quizmaster.com
ADMIN_PASSWORD=admin123
```

#### Initialize Database
```bash
flask db upgrade
```

#### Start Celery Workers
```bash
# Terminal 1: Start Celery Worker
celery -A celery_app worker --loglevel=info --concurrency=1 --pool=solo

# Terminal 2: Start Celery Beat (for scheduled tasks)
celery -A celery_app beat --loglevel=info
```

#### Run Backend Server
```bash
flask run
```

### 3. Frontend Setup

#### Install Node.js Dependencies
```bash
cd frontend
npm install
```

#### Run Development Server
```bash
npm run dev
```

## 📁 Project Structure

```
quiz-master/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API endpoints
│   │   └── services/        # Business logic
│   ├── celery_tasks/        # Asynchronous tasks
│   ├── migrations/          # Database migrations
│   ├── exports/            # Generated CSV files
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── views/          # Page components
│   │   ├── services/       # API services
│   │   └── router/         # Vue router
│   └── package.json
└── README.md
```

## 🔧 Configuration

### Email Setup
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password
3. Update SMTP settings in `.env` file

### Redis Setup
```bash
# Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server
```

### Database Setup
```bash
# For SQLite (default)
flask db upgrade

# For PostgreSQL
pip install psycopg2-binary
# Update DATABASE_URL in .env
```

## 🚀 Usage

### Starting the Application

1. **Start Redis Server**
```bash
redis-server
```

2. **Start Celery Workers**
```bash
cd backend
source venv/bin/activate
celery -A celery_app worker --loglevel=info --concurrency=1 --pool=solo
```

3. **Start Celery Beat**
```bash
celery -A celery_app beat --loglevel=info
```

4. **Start Backend Server**
```bash
flask run
```

5. **Start Frontend Development Server**
```bash
cd frontend
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Admin Panel**: http://localhost:5173/admin

### Default Admin Credentials
- **Email**: admin@quizmaster.com
- **Password**: admin123

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout

### User Management
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile
- `GET /api/user/scores` - Get user scores
- `POST /api/user/export/scores` - Export user scores to CSV

### Quiz Management
- `GET /api/user/subjects` - Get available subjects
- `GET /api/user/chapters/:slug/quizzes` - Get chapter quizzes
- `GET /api/user/quizzes/:slug/info` - Get quiz information
- `POST /api/user/quizzes/:slug/submit` - Submit quiz answers

### Admin Endpoints
- `GET /api/admin/users` - Get all users
- `POST /api/admin/subjects` - Create subject
- `POST /api/admin/quizzes` - Create quiz
- `POST /api/admin/export/:report_type` - Export admin reports

## 🔄 Background Tasks

### CSV Export Tasks
- **User Score Export**: Exports user's quiz scores to CSV
- **Admin Report Export**: Exports system-wide reports to CSV
- **Email Notifications**: Sends completion notifications

### Scheduled Tasks
- **Daily Reminders**: Creates reminders for inactive users
- **Monthly Reports**: Generates and sends monthly activity reports

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### SMTP Configuration Test
```bash
cd backend
python test_smtp.py
```

### Celery Task Test
```bash
cd backend
python test_celery_email.py
```

## 🐛 Troubleshooting

### Common Issues

1. **Celery Worker Not Starting**
   - Ensure Redis is running
   - Check Celery configuration in `celery_app.py`

2. **Email Notifications Not Working**
   - Verify SMTP settings in `.env`
   - Check if App Password is correctly set
   - Run SMTP test script

3. **Database Migration Issues**
   - Delete `migrations/` folder
   - Run `flask db init`
   - Run `flask db migrate`
   - Run `flask db upgrade`

4. **Frontend Build Issues**
   - Clear node_modules: `rm -rf node_modules`
   - Reinstall dependencies: `npm install`

### Logs and Debugging

- **Backend Logs**: Check Flask application logs
- **Celery Logs**: Monitor Celery worker output
- **Redis Logs**: Check Redis server logs
- **Frontend Logs**: Check browser console

## 📈 Performance Optimization

### Caching Strategy
- Redis caching for frequently accessed data
- Cache user dashboard statistics
- Cache quiz questions and answers

### Database Optimization
- Index frequently queried columns
- Use database connection pooling
- Implement query optimization

### Frontend Optimization
- Lazy loading for components
- Image optimization
- Code splitting

## 🔒 Security Considerations

### Authentication
- JWT token-based authentication
- Secure password hashing
- Session management

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection

### API Security
- Rate limiting
- CORS configuration
- Request validation

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation

## 🔄 Changelog

### Version 1.0.0
- Initial release
- User and admin interfaces
- Quiz management system
- CSV export functionality
- Email notifications
- Background task processing

---

**Note**: This is a development version. For production deployment, ensure proper security configurations and use production-grade databases and servers. 