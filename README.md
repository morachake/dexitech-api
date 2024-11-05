# Dexitech Admin Dashboard

A comprehensive admin dashboard for managing service providers, users, and service requests.

## Features

- User Management
- Service Provider Management
- Service Request Tracking
- Document Management
- Analytics Dashboard
- Role-based Access Control

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- virtualenv (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dexitech-admin.git
cd dexitech-admin
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your environment variables:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. (Optional) Load sample data:
```bash
python manage.py seed_data
```

## Running the Application

1. Start the development server:
```bash
python manage.py runserver
```

2. Access the application:
- Admin Dashboard: http://localhost:8000/dashboard/
- API Documentation: http://localhost:8000/swagger/
- Admin Interface: http://localhost:8000/admin/

## Project Structure

```
dexitech/
├── api/                    # API endpoints
│   ├── auth/              # Authentication endpoints
│   ├── providers/         # Provider management
│   ├── requests/          # Service requests
│   ├── services/          # Service management
│   └── users/             # User management
├── dashboard/             # Admin dashboard
│   ├── templates/         # Dashboard templates
│   ├── static/           # Static files
│   └── management/       # Custom management commands
├── services/             # Service app
├── users/               # User app
└── dexitech/           # Project settings
```

## API Documentation

The API documentation is available through Swagger UI at `/swagger/` when the server is running. It provides detailed information about all available endpoints, request/response formats, and authentication requirements.

## Testing

Run the test suite:
```bash
python manage.py test
```

## Deployment

1. Update `.env` file with production settings:
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=your-database-url
```

2. Collect static files:
```bash
python manage.py collectstatic
```

3. Configure your web server (e.g., Nginx, Apache) to serve the application.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team.