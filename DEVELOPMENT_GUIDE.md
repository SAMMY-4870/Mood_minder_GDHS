# 🚀 Development Guide - Mental Health Support Website

## 📋 Project Overview

This is a comprehensive mental health support platform that helps users reduce stress through interactive games, track their performance, and gain insights about their focus levels. The platform combines gamification, analytics, and mental health support to create an engaging and therapeutic experience.

## 🏗️ Architecture

### Backend (Flask + MongoDB)
- **Framework**: Flask (Python web framework)
- **Database**: MongoDB (NoSQL database for flexible data storage)
- **Authentication**: Session-based user authentication
- **API**: RESTful API endpoints for frontend communication

### Frontend (HTML/CSS/JavaScript)
- **Templates**: Jinja2 templating engine
- **Styling**: Bootstrap 5 + Custom CSS
- **Interactivity**: Vanilla JavaScript + jQuery
- **Charts**: Plotly.js for data visualization

### Key Components
1. **Game Engine**: Interactive stress-relief games with performance tracking
2. **Analytics System**: Focus level calculation and progress monitoring
3. **Notification System**: Achievement detection and motivational messages
4. **Dashboard**: Comprehensive analytics and insights
5. **Leaderboard**: Competitive elements to motivate users

## 🎮 Game Development

### Memory Match Game
**File**: `templates/games/memory.html`

**Features**:
- 4x4 grid of cards with matching pairs
- Real-time performance tracking (moves, time, accuracy)
- Focus score calculation based on efficiency
- Session data logging to database

**Key Metrics**:
- `moves`: Number of card flips
- `time_taken`: Total time to complete
- `pairs_found`: Number of correct matches
- `accuracy`: Percentage of correct moves
- `focus_score`: Calculated focus level (0-100)

### Reaction Time Test
**File**: `templates/games/reaction.html`

**Features**:
- Random delay before click prompt
- Multiple rounds with average calculation
- Performance badges (Excellent, Good, Average, Poor)
- Real-time focus meter

**Key Metrics**:
- `avg_reaction_time`: Average response time in milliseconds
- `best_time`: Fastest reaction time
- `worst_time`: Slowest reaction time
- `rounds`: Number of test rounds
- `focus_score`: Based on speed and consistency

### Stress Puzzle Game
**File**: `templates/games/puzzle.html`

**Features**:
- Sliding puzzle with multiple difficulty levels
- Hint system (limited uses)
- Move efficiency tracking
- Celebration animations

**Key Metrics**:
- `moves`: Total moves to solve
- `time_taken`: Time to complete puzzle
- `hints_used`: Number of hints used
- `efficiency`: Moves per minute
- `focus_score`: Based on problem-solving efficiency

## 📊 Analytics System

### Focus Score Calculation
**File**: `web_app.py` - `_calculate_focus_score()`

```python
def _calculate_focus_score(session_data: dict) -> float:
    accuracy = session_data.get('accuracy', 0)
    reaction_time = session_data.get('avg_reaction_time', 1000)
    consistency = session_data.get('consistency', 0)
    
    # Normalize reaction time (lower is better)
    reaction_score = max(0, (2000 - reaction_time) / 2000)
    
    # Weighted focus score (0-100)
    focus_score = (accuracy * 0.4 + reaction_score * 0.3 + consistency * 0.3) * 100
    return round(focus_score, 2)
```

### Performance Tracking
**File**: `web_app.py` - `_log_game_session()`

Each game session logs:
- User email and game type
- Timestamp
- Session data (moves, time, accuracy, etc.)
- Calculated focus score

### Database Schema

#### Collections:
1. **`users`**: User accounts and profiles
2. **`game_scores`**: Aggregated game performance data
3. **`game_sessions`**: Detailed session logs
4. **`user_activity`**: Activity tracking
5. **`notifications`**: Achievement and progress notifications

#### Sample Document Structure:
```javascript
// game_sessions
{
  "user_email": "user@example.com",
  "game": "memory",
  "timestamp": ISODate("2024-01-15T10:30:00Z"),
  "session_data": {
    "moves": 24,
    "time_taken": 120,
    "pairs_found": 8,
    "accuracy": 0.85,
    "focus_score": 78.5
  }
}
```

## 🔔 Notification System

### Achievement Detection
**File**: `src/notifications.py` - `check_achievements()`

**Achievement Types**:
- **First Session**: Complete first game
- **Focus Master**: 80%+ focus in 5 consecutive sessions
- **Memory Champion**: Find 50+ pairs in memory games
- **Reaction Legend**: Achieve <200ms reaction time
- **Puzzle Master**: Solve 20+ puzzles
- **Streak Warrior**: Play for 7 consecutive days
- **Zen Master**: Complete 100+ breathing cycles

### Notification Types
1. **Achievement**: Unlock new achievements
2. **Insight**: Progress insights and recommendations
3. **Motivation**: Motivational messages and encouragement

### Real-time Updates
- Auto-refresh every 30 seconds
- Toast notifications for new achievements
- Progress insights on home page

## 📈 Dashboard Analytics

### Enhanced Dashboard
**File**: `user_dashboard.py`

**Features**:
- Focus level trends over time
- Game performance comparison
- Activity timeline
- Personalized insights
- Interactive charts using Plotly

### Key Metrics Display
1. **Total Sessions**: Sum of all game sessions
2. **Average Focus Score**: Mean focus level
3. **Weekly Activity**: Recent engagement
4. **Best Game**: Highest performing game type

### Chart Types
- **Line Charts**: Focus trends over time
- **Bar Charts**: Game performance comparison
- **Pie Charts**: Activity distribution
- **Scatter Plots**: Performance correlation

## 🏆 Leaderboard System

### Multi-Game Leaderboards
**File**: `templates/games/leaderboard.html`

**Games Tracked**:
- Breathing: Total cycles completed
- Memory: Pairs found
- Reaction: Best reaction time
- Puzzle: Total moves (lower is better)
- RPS: Total wins
- Guess: Total wins
- Trivia: Correct answers

### Ranking System
- Top 10 players per game
- Achievement badges
- Performance categories
- Real-time updates

## 🎨 UI/UX Design

### Design Principles
1. **Accessibility**: Clear contrast, readable fonts
2. **Responsiveness**: Mobile-first design
3. **Gamification**: Engaging visual elements
4. **Mental Health Focus**: Calming colors and animations

### Color Scheme
- **Primary**: #6f42c1 (Purple)
- **Success**: #20c997 (Teal)
- **Warning**: #ff6b6b (Coral)
- **Info**: #feca57 (Yellow)

### Key UI Components
1. **Game Cards**: Interactive game selection
2. **Progress Bars**: Visual focus level indicators
3. **Achievement Badges**: Recognition system
4. **Charts**: Data visualization
5. **Notifications**: Toast and alert systems

## 🔧 Development Setup

### Prerequisites
```bash
# Python 3.8+
python --version

# MongoDB (local or Atlas)
mongod --version

# Node.js (for frontend tools)
node --version
```

### Installation Steps
```bash
# 1. Clone repository
git clone <repository-url>
cd happy_quotes_ml_project

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
export MONGO_URI="your-mongodb-connection-string"
export FLASK_SECRET_KEY="your-secret-key"

# 5. Run application
python web_app.py
```

### Database Setup
```python
# MongoDB collections will be created automatically
# Sample data can be inserted using the web interface
```

## 🧪 Testing

### Manual Testing
1. **User Registration/Login**: Test authentication flow
2. **Game Functionality**: Play each game and verify metrics
3. **Analytics**: Check dashboard data accuracy
4. **Notifications**: Trigger achievements and verify display
5. **Leaderboard**: Test ranking system

### Test Scenarios
1. **New User Journey**: Registration → First Game → Achievement
2. **Returning User**: Login → Dashboard → Progress Check
3. **Performance Tracking**: Multiple sessions → Analytics
4. **Achievement System**: Complete requirements → Notification

## 🚀 Deployment

### Local Development
```bash
python web_app.py
# Access at http://localhost:5000
```

### Production Deployment
1. **Environment Setup**:
   - Set production MongoDB URI
   - Configure Flask secret key
   - Set debug=False

2. **Server Configuration**:
   - Use Gunicorn or similar WSGI server
   - Configure reverse proxy (Nginx)
   - Set up SSL certificates

3. **Database**:
   - Use MongoDB Atlas for production
   - Configure backup and monitoring
   - Set up indexes for performance

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "web_app.py"]
```

## 📝 Code Organization

### File Structure
```
src/
├── notifications.py      # Notification and achievement system
├── recommender.py        # Recommendation engine
└── main.py              # ML utilities

templates/
├── games/               # Game templates
├── home.html           # Enhanced home page
├── notifications.html  # Notifications page
└── base.html          # Base template

static/
├── css/               # Stylesheets
└── js/               # JavaScript files
```

### Key Functions
- **`_calculate_focus_score()`**: Focus calculation algorithm
- **`_log_game_session()`**: Session data logging
- **`check_achievements()`**: Achievement detection
- **`get_performance_metrics()`**: Analytics data retrieval

## 🔍 Debugging

### Common Issues
1. **MongoDB Connection**: Check URI and network access
2. **Session Data**: Verify user authentication
3. **Game Metrics**: Check JavaScript console for errors
4. **Chart Rendering**: Ensure Plotly.js is loaded

### Debug Tools
- Flask debug mode for backend errors
- Browser developer tools for frontend issues
- MongoDB Compass for database inspection
- Network tab for API call debugging

## 📚 API Reference

### Game Session Endpoints
- `POST /games/memory` - Submit memory game results
- `POST /games/reaction` - Submit reaction test results
- `POST /games/puzzle` - Submit puzzle game results

### Analytics Endpoints
- `GET /api/notifications/check` - Check for new notifications
- `GET /api/progress/summary` - Get weekly progress summary
- `POST /api/notifications/mark-read` - Mark notification as read

### Data Endpoints
- `GET /api/random-quotes` - Get random quotes
- `GET /api/random-images` - Get random images
- `GET /api/random-songs` - Get random songs

## 🎯 Future Enhancements

### Planned Features
1. **Mobile App**: React Native or Flutter app
2. **Advanced ML**: Focus prediction models
3. **Social Features**: Friend challenges and sharing
4. **Wearable Integration**: Heart rate and stress monitoring
5. **Custom Games**: User-created game tools
6. **Voice Guidance**: Audio instructions and feedback

### Technical Improvements
1. **Caching**: Redis for session and analytics data
2. **Real-time**: WebSocket for live updates
3. **Microservices**: Break down into smaller services
4. **CI/CD**: Automated testing and deployment
5. **Monitoring**: Application performance monitoring

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Commit with descriptive messages
5. Push and create pull request

### Code Standards
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Write tests for new features
- Update documentation

## 📞 Support

### Getting Help
- Check this development guide
- Review the main README.md
- Create an issue in the repository
- Contact the development team

### Resources
- Flask Documentation: https://flask.palletsprojects.com/
- MongoDB Documentation: https://docs.mongodb.com/
- Bootstrap Documentation: https://getbootstrap.com/
- Plotly.js Documentation: https://plotly.com/javascript/

---

**Happy Coding! 🚀**

Remember to prioritize user mental health and create a positive, supportive environment in all your development work.
