# EduVerse - Learning Management System

A production-grade Learning Management System built with Django, Django REST Framework, React, PostgreSQL, Redis, and Celery. Supports course creation, video lessons, quizzes, assignments, progress tracking, certificates, instructor/student dashboards, discussion forums, and revenue sharing.

## Architecture

```
EduVerse/
├── backend/           # Django + DRF API server
│   ├── config/        # Django project configuration
│   ├── apps/
│   │   ├── accounts/      # User management, profiles
│   │   ├── courses/       # Courses, sections, lessons
│   │   ├── quizzes/       # Quizzes, questions, attempts
│   │   ├── assignments/   # Assignments, submissions, grades
│   │   ├── progress/      # Lesson/course progress, certificates
│   │   ├── discussions/   # Forum threads, comments, votes
│   │   ├── payments/      # Payments, coupons, revenue, payouts
│   │   ├── reviews/       # Course reviews and ratings
│   │   └── notifications/ # Email/push notification system
│   └── utils/             # Shared utilities
├── frontend/          # React SPA
│   ├── src/
│   │   ├── api/           # API client modules
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page-level components
│   │   ├── store/         # Redux store and slices
│   │   ├── hooks/         # Custom React hooks
│   │   └── styles/        # Global CSS
│   └── public/
├── nginx/             # Nginx reverse proxy config
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## Features

- **Course Management**: Create courses with sections, video lessons, and downloadable content
- **Video Lessons**: Stream video content with progress tracking per lesson
- **Quizzes**: Multiple-choice, true/false, and short-answer questions with auto-grading
- **Assignments**: File-upload assignments with manual and rubric-based grading
- **Progress Tracking**: Per-lesson and per-course completion with visual indicators
- **Certificates**: Auto-generated PDF certificates upon course completion
- **Instructor Dashboard**: Revenue analytics, student metrics, course management
- **Student Dashboard**: Enrolled courses, progress overview, upcoming deadlines
- **Discussion Forums**: Threaded discussions per course with voting and moderation
- **Payments & Revenue Sharing**: Stripe integration, coupon codes, instructor payouts
- **Reviews & Ratings**: Star ratings and written reviews with moderation
- **Notifications**: Email and in-app notifications for key events

## Tech Stack

| Component    | Technology                          |
|-------------|-------------------------------------|
| Backend     | Django 5.x, Django REST Framework   |
| Frontend    | React 18, Redux Toolkit             |
| Database    | PostgreSQL 16                        |
| Cache/Queue | Redis 7                              |
| Task Queue  | Celery 5.x                           |
| Proxy       | Nginx                                |
| Containers  | Docker, Docker Compose               |
| Payments    | Stripe API                           |

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/eduverse.git
   cd eduverse
   ```

2. **Copy environment variables**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env`** with your configuration (database credentials, Stripe keys, email settings, etc.)

4. **Build and start containers**
   ```bash
   docker-compose up --build
   ```

5. **Run migrations**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

7. **Access the application**
   - Frontend: http://localhost
   - API: http://localhost/api/
   - Admin: http://localhost/api/admin/

## Development

### Backend Only
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Only
```bash
cd frontend
npm install
npm start
```

### Running Celery Workers
```bash
celery -A config worker -l info
celery -A config beat -l info
```

## API Documentation

Once the backend is running, interactive API docs are available at:
- Swagger UI: http://localhost/api/docs/
- ReDoc: http://localhost/api/redoc/

## Environment Variables

See `.env.example` for the full list. Key variables:

| Variable              | Description                        |
|----------------------|-------------------------------------|
| `SECRET_KEY`         | Django secret key                   |
| `DATABASE_URL`       | PostgreSQL connection string         |
| `REDIS_URL`          | Redis connection string              |
| `STRIPE_SECRET_KEY`  | Stripe API secret key                |
| `STRIPE_PUBLIC_KEY`  | Stripe publishable key               |
| `EMAIL_HOST`         | SMTP server hostname                 |
| `AWS_STORAGE_BUCKET` | S3 bucket for media storage          |

## Testing

```bash
# Backend tests
docker-compose exec backend python manage.py test

# Frontend tests
docker-compose exec frontend npm test
```

## License

This project is licensed under the MIT License.
