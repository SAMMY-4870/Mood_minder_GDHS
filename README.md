# 🧠 Mental Health Support Website

A comprehensive mental health support platform that helps users reduce stress through interactive games, track their performance, and gain insights about their focus levels.

## 🌟 Features

### 🎮 Stress-Relief Games
- **Memory Match**: Improve focus with classic memory card games
- **Reaction Time Test**: Test and improve reaction speed and focus
- **Stress Puzzle**: Solve relaxing puzzles to calm the mind
- **Breathing Exercise**: Practice mindful breathing to reduce stress
- **Classic Games**: Rock-Paper-Scissors, Guess the Number, Trivia

### 📊 Performance Tracking
- **Real-time Analytics**: Track clicks, time taken, accuracy, scores
- **Focus Level Monitoring**: Calculate focus scores based on performance metrics
- **Session Logging**: Detailed game session data for analysis
- **Progress Visualization**: Charts and graphs showing improvement over time

### 🏆 Gamification
- **Leaderboards**: Compete with other users across different games
- **Achievement System**: Unlock badges and achievements
- **Progress Notifications**: Motivational messages and insights
- **Streak Tracking**: Daily activity streaks and consistency rewards

### 📈 Analytics Dashboard
- **Focus Level Trends**: Track focus improvement over time
- **Game Performance**: Compare performance across different games
- **Activity Timeline**: View detailed activity history
- **Personalized Insights**: AI-powered recommendations and insights

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB (local or cloud)
- Node.js (for frontend development)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd happy_quotes_ml_project
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MongoDB**
   - Install MongoDB locally or use MongoDB Atlas
   - Update the `MONGO_URI` in `web_app.py` with your connection string

4. **Run the application**
   ```bash
   python web_app.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Register a new account or use existing credentials

## 🏗️ Project Structure

```
happy_quotes_ml_project/
├── app.py                          # Streamlit app (legacy)
├── web_app.py                      # Main Flask application
├── user_dashboard.py               # Enhanced dashboard with analytics
├── src/
│   ├── notifications.py            # Notification and achievement system
│   ├── recommender.py              # Recommendation engine
│   └── main.py                     # ML utilities
├── templates/
│   ├── games/                      # Game templates
│   │   ├── index.html             # Games overview
│   │   ├── memory.html            # Memory match game
│   │   ├── reaction.html          # Reaction time test
│   │   ├── puzzle.html            # Stress puzzle game
│   │   ├── breathing.html         # Breathing exercise
│   │   ├── rps.html               # Rock-Paper-Scissors
│   │   ├── guess_number.html      # Guess the number
│   │   ├── trivia.html            # Trivia game
│   │   └── leaderboard.html       # Leaderboard
│   ├── home.html                  # Enhanced home page
│   ├── notifications.html         # Notifications page
│   └── base.html                  # Base template
├── static/
│   ├── css/                       # Stylesheets
│   └── js/                        # JavaScript files
├── data/                          # Media files
│   ├── images/                    # Happy images
│   ├── music/                     # Relaxing music
│   └── quotes/                    # Motivational quotes
└── requirements.txt               # Python dependencies
```

## 🎯 Key Components

### Game Engine
- **Performance Tracking**: Captures detailed metrics for each game session
- **Focus Calculation**: Algorithm to calculate focus scores based on performance
- **Session Management**: Tracks user progress and achievements

### Analytics System
- **Focus Analytics**: Tracks focus levels over time
- **Performance Metrics**: Comprehensive game performance analysis
- **Insight Generation**: AI-powered insights and recommendations

### Notification System
- **Achievement Detection**: Automatically detects and awards achievements
- **Progress Notifications**: Motivational messages and progress updates
- **Real-time Updates**: Live notifications and insights

### Database Schema
- **Users**: User accounts and profiles
- **Game Scores**: Game performance data
- **Game Sessions**: Detailed session analytics
- **User Activity**: Activity logging and tracking
- **Notifications**: Achievement and progress notifications

## 🔧 Configuration

### Environment Variables
```bash
# MongoDB Connection
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key
PORT=5000
```

### Database Collections
- `users`: User accounts and profiles
- `game_scores`: Aggregated game performance data
- `game_sessions`: Detailed game session logs
- `user_activity`: User activity tracking
- `notifications`: Achievement and progress notifications
- `quotes`: Motivational quotes database
- `images`: Happy images database
- `songs`: Relaxing music database

## 🎮 Game Features

### Memory Match
- **Objective**: Match pairs of cards to improve memory and focus
- **Metrics**: Moves, time taken, pairs found, accuracy
- **Focus Score**: Based on efficiency and accuracy

### Reaction Time Test
- **Objective**: Click as fast as possible when prompted
- **Metrics**: Average reaction time, best time, consistency
- **Focus Score**: Based on speed and consistency

### Stress Puzzle
- **Objective**: Solve sliding puzzles to calm the mind
- **Metrics**: Moves, time taken, hints used, efficiency
- **Focus Score**: Based on problem-solving efficiency

### Breathing Exercise
- **Objective**: Follow guided breathing patterns
- **Metrics**: Duration, cycles completed, consistency
- **Focus Score**: Based on completion and consistency

## 📊 Analytics Features

### Focus Level Tracking
- **Real-time Monitoring**: Live focus score calculation
- **Trend Analysis**: Track focus improvement over time
- **Game Comparison**: Compare focus levels across different games

### Performance Analytics
- **Session Analysis**: Detailed breakdown of each game session
- **Improvement Tracking**: Monitor progress and improvement trends
- **Personalized Insights**: AI-generated recommendations

### Achievement System
- **Automatic Detection**: System automatically detects achievements
- **Progress Rewards**: Unlock badges and rewards for milestones
- **Motivational Messages**: Encouraging messages and insights

## 🚀 Deployment

### Local Development
```bash
python web_app.py
```

### Production Deployment
1. Set up MongoDB Atlas or local MongoDB instance
2. Configure environment variables
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `python web_app.py`

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -m "Add feature"`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔮 Future Enhancements

- [ ] Mobile app development
- [ ] Advanced ML models for focus prediction
- [ ] Social features and community challenges
- [ ] Integration with wearable devices
- [ ] Advanced analytics and reporting
- [ ] Multi-language support
- [ ] Voice-guided exercises
- [ ] Custom game creation tools

## 🙏 Acknowledgments

- Built with Flask and MongoDB
- Uses Plotly for data visualization
- Inspired by mental health and wellness research
- Designed with accessibility and user experience in mind

---

**Remember**: This platform is designed to support mental health and wellness. If you're experiencing a mental health crisis, please contact professional help or emergency services.
