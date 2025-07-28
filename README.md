# CourseGen AI 🎓

A powerful Django web application that converts YouTube videos into structured online courses using AI. Generate comprehensive courses with chapters, AI-generated notes, quizzes, and interactive video navigation.

## ✨ Features

- **🎬 YouTube Video Integration**: Extract chapters and content from any YouTube video
- **🧠 AI-Powered Course Generation**: Uses OpenAI GPT-4 to create structured courses
- **⏰ Timestamp Navigation**: Jump to specific video timestamps for each lesson
- **📝 AI-Generated Notes**: Comprehensive notes for each lesson
- **🎯 Interactive Quizzes**: Automatic quiz generation for each lesson
- **📊 Progress Tracking**: Track your learning progress
- **📱 Responsive Design**: Works perfectly on all devices
- **⚡ Fast Generation**: Optimized for 10-15 second course generation

## 🚀 Tech Stack

- **Backend**: Django + Django REST Framework
- **Frontend**: React + Tailwind CSS
- **Database**: PostgreSQL (SQLite for development)
- **AI**: OpenAI GPT-4
- **Video**: YouTube Data API v3
- **Deployment**: Ready for AWS/Railway + Vercel

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- OpenAI API Key
- YouTube Data API Key

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ibiiziiy/coursegen.git
cd coursegen
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start Django server
python manage.py runserver
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start React development server
npm start
```

### 4. Environment Variables

Create a `.env` file in the root directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# YouTube API Key
YOUTUBE_API_KEY=your-youtube-api-key-here
```

## 🔑 API Keys Setup

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account and get your API key
3. Add it to your `.env` file

### YouTube Data API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Add it to your `.env` file

## 🎯 Usage

### 1. Start the Application

```bash
# Terminal 1: Backend
python manage.py runserver

# Terminal 2: Frontend
cd frontend && npm start
```

### 2. Generate a Course

1. Open http://localhost:3000
2. Enter a YouTube URL
3. Add an optional topic
4. Select difficulty level
5. Click "Generate Course"
6. Wait 10-15 seconds for AI processing

### 3. Navigate the Course

- **Chapter Navigation**: Click any lesson to jump to that timestamp in the video
- **AI Notes**: Read comprehensive AI-generated notes for each lesson
- **Progress Tracking**: Mark lessons as complete
- **Quiz System**: Take quizzes to test your knowledge

## 📁 Project Structure

```
coursegen/
├── coursegen/              # Django project settings
├── courses/               # Main Django app
│   ├── models.py         # Database models
│   ├── serializers.py    # API serializers
│   ├── services.py       # Business logic
│   ├── views.py          # API views
│   └── urls.py           # URL routing
├── frontend/             # React application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   └── services/     # API services
│   └── public/           # Static files
├── static/               # Django static files
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables
└── README.md           # This file
```

## 🔧 API Endpoints

### Course Generation
- `POST /api/generate/` - Generate a new course

### Course Management
- `GET /api/courses/` - List all courses
- `GET /api/courses/{id}/` - Get course details
- `GET /api/modules/{id}/` - Get module details
- `GET /api/lessons/{id}/` - Get lesson details

### Progress Tracking
- `POST /api/lessons/{id}/complete/` - Mark lesson as complete
- `GET /api/users/{id}/progress/` - Get user progress
- `GET /api/users/{id}/dashboard/` - Get dashboard stats

### Quiz System
- `GET /api/quizzes/{id}/` - Get quiz details
- `POST /api/quizzes/{id}/submit/` - Submit quiz answers

## 🎨 Features in Detail

### YouTube Integration
- **Video Analysis**: Extracts video title, description, and duration
- **Chapter Extraction**: Automatically finds chapters in video descriptions
- **Transcript Analysis**: Uses AI to generate chapters from video transcripts
- **Timestamp Mapping**: Links each lesson to specific video timestamps

### AI Course Generation
- **Smart Structure**: Creates logical course modules based on video content
- **Comprehensive Notes**: Generates detailed AI notes for each lesson
- **Quiz Creation**: Automatically creates relevant quizzes
- **Difficulty Adaptation**: Adjusts content based on selected difficulty level

### Interactive Learning
- **Video Navigation**: Click lessons to jump to specific video timestamps
- **Progress Tracking**: Visual progress indicators
- **Completion System**: Mark lessons as complete
- **Quiz Integration**: Test knowledge with AI-generated quizzes

## 🚀 Deployment

### Backend (Django)
```bash
# Production settings
python manage.py collectstatic
python manage.py migrate
gunicorn coursegen.wsgi:application
```

### Frontend (React)
```bash
cd frontend
npm run build
# Deploy build folder to Vercel/Netlify
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- YouTube Data API for video integration
- Django and React communities
- Tailwind CSS for styling

## 📞 Support

If you have any questions or need help, please open an issue on GitHub.

---

**Made with ❤️ by CourseGen AI Team** 