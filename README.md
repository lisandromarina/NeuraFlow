# NeuraFlow

A powerful workflow automation platform with a modern React frontend and FastAPI backend, featuring visual workflow design, Google Sheets integration, and real-time execution.

## 🚀 Features

- **Visual Workflow Designer**: Drag-and-drop interface for creating complex workflows
- **Google Sheets Integration**: Connect and manipulate Google Sheets data
- **Real-time Execution**: Live workflow monitoring and execution
- **User Authentication**: Secure JWT-based authentication system
- **Scheduled Workflows**: Time-based workflow triggers
- **Node-based Architecture**: Extensible system with custom node types
- **RESTful API**: Comprehensive API for workflow management
- **Modern UI**: Built with React, TypeScript, and Tailwind CSS

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for real-time data and job queuing
- **Authentication**: JWT tokens with Argon2 password hashing
- **API**: RESTful endpoints with automatic OpenAPI documentation
- **Security**: Environment-based configuration with encrypted credentials

### Frontend (React)
- **Framework**: React 19 with TypeScript
- **UI Library**: Radix UI components with Tailwind CSS
- **Workflow Designer**: React Flow for visual workflow creation
- **State Management**: React Context API
- **HTTP Client**: Axios for API communication
- **Build Tool**: Vite for fast development and building

### Infrastructure
- **Containerization**: Docker and Docker Compose
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Development**: Hot reload for both frontend and backend

## 📋 Prerequisites

- [Docker](https://www.docker.com/get-started) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)
- [Git](https://git-scm.com/)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/lisandromarina/NeuraFlow.git
cd NeuraFlow
```

### 2. Environment Setup

Create a `.env` file in the `backend/app/` directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/mydatabase

# Redis Configuration
REDIS_URL=redis://redis_db:6379/0

# JWT Authentication
SECRET_KEY=your-super-secure-jwt-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Credentials Encryption
CREDENTIALS_SECRET_KEY=your-base64-encoded-32-byte-key-here

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/credentials/callback/google

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Ngrok URL (for Telegram webhooks - set after running ngrok)
NGROK_URL=https://your-ngrok-url.ngrok-free.app
```

### 3. Ngrok Setup (Required for Telegram Integration)

If you plan to use Telegram triggers, you need to set up ngrok to expose your local backend:

1. **Set up ngrok configuration**:
   ```bash
   mkdir -p ngrok_config
   cp ngrok_config/ngrok.yml.example ngrok_config/ngrok.yml
   ```
   
2. **Edit `ngrok_config/ngrok.yml`** and add your ngrok authtoken:
   ```yaml
   authtoken: YOUR_NGROK_AUTH_TOKEN_HERE
   ```

3. **Start ngrok manually**:
   ```bash
   docker-compose -f docker-compose.ngrok.yml up -d
   ```

4. **Get your ngrok URL**:
   - Visit http://localhost:4040 to view the ngrok web interface
   - Or run: `curl http://localhost:4040/api/tunnels`
   - Copy the public URL (e.g., `https://471946aba7ad.ngrok-free.app`)

5. **Add the ngrok URL to your `.env` file**:
   ```bash
   NGROK_URL=https://your-ngrok-url.ngrok-free.app
   ```
   Replace `your-ngrok-url.ngrok-free.app` with your actual ngrok URL.

### 4. Build and Start the Application

```bash
docker-compose up --build
```

This will start all services:
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 🏃‍♂️ Development

### Running Individual Services

#### Backend Only
```bash
cd backend
docker-compose up postgres redis backend
```

#### Frontend Only
```bash
cd frontend
npm install
npm run dev
```

#### Database Migrations
```bash
# Access the backend container
docker-compose exec backend bash

# Run migrations (if using Alembic)
alembic upgrade head
```

### Project Structure

```
NeuraFlow/
├── backend/
│   ├── app/
│   │   ├── api/                 # API routes
│   │   │   └── v1/
│   │   │       ├── auth_routes.py
│   │   │       ├── workflow_routes.py
│   │   │       ├── node_routes.py
│   │   │       └── google_routes.py
│   │   ├── core/                # Core business logic
│   │   ├── models/              # Database models and schemas
│   │   ├── services/            # Business logic services
│   │   ├── repositories/        # Data access layer
│   │   ├── nodes/               # Workflow node implementations
│   │   ├── utils/               # Utility functions
│   │   └── main.py              # FastAPI application entry point
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── ui/              # Reusable UI components
│   │   │   ├── workflow/        # Workflow-specific components
│   │   │   └── nodes/           # Node components
│   │   ├── pages/               # Page components
│   │   ├── context/             # React context providers
│   │   ├── hooks/               # Custom React hooks
│   │   ├── api/                 # API client and endpoints
│   │   └── router/              # React Router configuration
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ | - |
| `REDIS_URL` | Redis connection string | ✅ | - |
| `SECRET_KEY` | JWT signing secret | ✅ | - |
| `CREDENTIALS_SECRET_KEY` | Encryption key for user credentials | ✅ | - |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | ✅ | - |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | ✅ | - |
| `GOOGLE_REDIRECT_URI` | Google OAuth redirect URI | ✅ | - |
| `FRONTEND_URL` | Frontend application URL | ✅ | - |
| `NGROK_URL` | Ngrok public URL (for Telegram webhooks) | ⚠️ | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration time | ❌ | 30 |

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:8000/credentials/callback/google`
6. Copy Client ID and Client Secret to your `.env` file

## 📚 API Documentation

Once the application is running, you can access:

- **Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key API Endpoints

- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `GET /workflows/` - List workflows
- `POST /workflows/` - Create workflow
- `GET /nodes/` - List available nodes
- `POST /credentials/google/connect` - Connect Google account

## 🧪 Testing

### Backend Tests
```bash
# Run tests in the backend container
docker-compose exec backend pytest
```

### Frontend Tests
```bash
# Run tests in the frontend container
docker-compose exec frontend npm test
```

## 🚀 Deployment

### Production Environment

1. **Update Environment Variables**:
   - Use strong, unique secrets
   - Set production database URLs
   - Configure production frontend URL
   - Set up proper Google OAuth credentials

2. **Security Considerations**:
   - Use HTTPS in production
   - Set up proper CORS origins
   - Use environment-specific secrets
   - Enable database SSL connections

3. **Deploy with Docker**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## 🛠️ Troubleshooting

### Common Issues

#### CORS Errors
- Ensure `FRONTEND_URL` is correctly set in your `.env` file
- Check that the frontend URL matches your actual frontend address

#### Database Connection Issues
- Verify PostgreSQL is running: `docker-compose ps postgres`
- Check database credentials in your `.env` file
- Ensure database is accessible from the backend container

#### Google OAuth Issues
- Verify Google OAuth credentials are correct
- Check that redirect URI matches your configuration
- Ensure Google Sheets API is enabled in Google Cloud Console

#### Redis Connection Issues
- Verify Redis is running: `docker-compose ps redis`
- Check Redis URL in your `.env` file

### Logs

View logs for specific services:
```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# Database logs
docker-compose logs postgres

# All logs
docker-compose logs
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review the [API documentation](#-api-documentation)
3. Open an [issue](https://github.com/lisandromarina/NeuraFlow/issues)

---

**Happy Workflow Building! 🎉**