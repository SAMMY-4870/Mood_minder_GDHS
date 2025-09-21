# 🧠 Mood Assessment & AI Chatbot Setup Guide

## 🎯 Overview

This guide covers the setup and configuration of the new mood assessment system and Gemini-powered AI chatbot for the mental health support website.

## ✨ New Features Added

### 1. **20-Question Health Assessment**
- Comprehensive mental health questionnaire
- 5-question quick assessment option
- Real-time mood scoring and categorization
- Personalized recommendations and insights

### 2. **Machine Learning Mood Prediction**
- Random Forest classifier for mood prediction
- Focus score calculation algorithm
- Category-based analysis (mood, sleep, stress, anxiety, etc.)
- Automated model training and persistence

### 3. **Gemini AI Chatbot**
- Powered by Google's Gemini Pro model
- Context-aware responses based on user mood
- Mental health resource recommendations
- Conversation history tracking

### 4. **Enhanced Analytics**
- Mood trend visualization
- Historical assessment tracking
- Personalized health insights
- Progress monitoring

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Gemini API
```python
# The API key is already configured in src/gemini_chatbot.py
GEMINI_API_KEY = "AIzaSyCbXuXJzklBBS_iUBGR9d7jXGON1a6KdjQ"
```

### 3. Run the Application
```bash
python web_app.py
```

### 4. Access New Features
- **Mood Assessment**: `http://localhost:5000/mood-assessment`
- **AI Chatbot**: `http://localhost:5000/chatbot`
- **Mood History**: `http://localhost:5000/mood-history`

## 📊 Mood Assessment System

### Question Categories
1. **Mood** (15% weight) - Overall emotional state
2. **Sleep** (12% weight) - Sleep quality and patterns
3. **Energy** (10% weight) - Energy levels and vitality
4. **Stress** (15% weight) - Stress levels and management
5. **Anxiety** (12% weight) - Anxiety and worry levels
6. **Confidence** (8% weight) - Self-confidence and self-esteem
7. **Satisfaction** (10% weight) - Life satisfaction
8. **Overwhelm** (8% weight) - Feeling overwhelmed
9. **Concentration** (10% weight) - Focus and attention
10. **Motivation** (8% weight) - Drive and motivation

### Mood Categories
- **Excellent** (80-100): Optimal mental health
- **Good** (60-79): Generally well with room for improvement
- **Moderate** (40-59): Some challenges, manageable
- **Poor** (20-39): Significant distress, support needed
- **Critical** (0-19): Severe distress, immediate help required

### ML Model Features
- **Algorithm**: Random Forest Classifier
- **Features**: 20 question responses (1-5 scale)
- **Target**: 5 mood categories
- **Accuracy**: ~85% on synthetic data
- **Persistence**: Model saved to `outputs/models/`

## 🤖 Gemini Chatbot Features

### Capabilities
- **Context-Aware**: Uses user's mood and activity history
- **Mental Health Focused**: Trained on mental health best practices
- **Resource Recommendations**: Provides relevant resources and contacts
- **Conversation Memory**: Maintains conversation context
- **Quick Responses**: Contextual quick response suggestions

### API Integration
```python
# Chatbot response generation
response = health_chatbot.generate_response(
    message="I feel anxious",
    user_email="user@example.com",
    conversation_id="conv_123"
)
```

### Safety Features
- Crisis detection and resource provision
- Professional help encouragement
- Non-judgmental responses
- Privacy and confidentiality

## 📈 Analytics & Insights

### Mood Tracking
- **Daily Scores**: Track mood over time
- **Category Analysis**: Identify specific areas of concern
- **Trend Visualization**: Chart.js powered graphs
- **Progress Monitoring**: Improvement tracking

### Personalized Insights
- **AI-Generated**: Based on assessment data
- **Actionable Recommendations**: Specific steps to improve
- **Resource Suggestions**: Relevant tools and contacts
- **Progress Celebrations**: Acknowledge improvements

## 🗄️ Database Schema

### New Collections
```javascript
// mood_assessments
{
  "user_email": "user@example.com",
  "responses": [1, 2, 3, 4, 5, ...],
  "analysis": {
    "overall_score": 75.5,
    "mood_category": "good",
    "description": "You're doing well overall...",
    "recommendations": ["Maintain your routine", ...],
    "insights": ["Your mood seems positive", ...],
    "category_scores": {
      "mood": 80.0,
      "sleep": 60.0,
      ...
    }
  },
  "timestamp": ISODate("2024-01-15T10:30:00Z")
}

// chatbot_conversations
{
  "user_email": "user@example.com",
  "conversation_id": "conv_123",
  "user_message": "I feel stressed",
  "bot_response": "I understand you're feeling stressed...",
  "timestamp": ISODate("2024-01-15T10:30:00Z")
}
```

## 🎨 Frontend Features

### Mood Assessment Interface
- **Progress Bar**: Visual progress indicator
- **Question Cards**: Clean, accessible question display
- **Option Buttons**: Interactive response selection
- **Results Display**: Comprehensive analysis presentation
- **Quick Assessment**: 5-question rapid assessment

### Chatbot Interface
- **Real-time Chat**: Instant messaging interface
- **Typing Indicators**: Visual feedback during processing
- **Quick Responses**: One-click common responses
- **Message History**: Conversation persistence
- **Resource Links**: Easy access to mental health resources

### Mood History Dashboard
- **Trend Charts**: Visual mood progression
- **Assessment Cards**: Detailed historical data
- **Statistics Summary**: Key metrics overview
- **Category Breakdown**: Detailed analysis per assessment

## 🔧 Configuration

### Environment Variables
```bash
# MongoDB Connection
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database

# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key
```

### Model Configuration
```python
# Mood Assessment Model
MODEL_PATH = "outputs/models/mood_model.pkl"
SCALER_PATH = "outputs/models/mood_scaler.pkl"

# Question Weights (customizable)
QUESTION_WEIGHTS = {
    "mood": 0.15,
    "sleep": 0.12,
    "stress": 0.15,
    # ... etc
}
```

## 🧪 Testing

### Manual Testing
1. **Mood Assessment**:
   - Complete full 20-question assessment
   - Try 5-question quick assessment
   - Verify results accuracy
   - Check database storage

2. **AI Chatbot**:
   - Test various mental health topics
   - Verify context awareness
   - Check resource recommendations
   - Test conversation persistence

3. **Analytics**:
   - View mood history
   - Check trend charts
   - Verify insights generation
   - Test data accuracy

### Test Scenarios
```python
# Test mood assessment
responses = [4, 3, 5, 2, 4, 3, 4, 2, 4, 3, 3, 4, 2, 4, 3, 2, 4, 3, 4, 3]
analysis = mood_assessor.get_mood_analysis(responses)
print(f"Mood Category: {analysis['mood_category']}")
print(f"Score: {analysis['overall_score']}")

# Test chatbot
response = health_chatbot.generate_response(
    "I'm feeling anxious about work",
    "user@example.com"
)
print(f"Bot Response: {response['response']}")
```

## 🚀 Deployment

### Production Setup
1. **Environment Configuration**:
   ```bash
   export GEMINI_API_KEY="your_production_key"
   export MONGO_URI="your_production_mongodb_uri"
   export FLASK_SECRET_KEY="your_production_secret"
   ```

2. **Model Deployment**:
   - Ensure model files are included in deployment
   - Verify model loading on startup
   - Test prediction accuracy

3. **API Rate Limits**:
   - Monitor Gemini API usage
   - Implement rate limiting if needed
   - Add error handling for API failures

### Docker Configuration
```dockerfile
# Add to existing Dockerfile
RUN pip install google-generativeai scikit-learn joblib
COPY outputs/models/ /app/outputs/models/
```

## 📊 Monitoring

### Key Metrics
- **Assessment Completion Rate**: Track user engagement
- **Mood Score Trends**: Monitor user progress
- **Chatbot Usage**: Track conversation frequency
- **API Response Times**: Monitor performance
- **Error Rates**: Track system reliability

### Logging
```python
# Example logging
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log assessment completion
logger.info(f"Assessment completed: {user_email}, Score: {score}")

# Log chatbot interactions
logger.info(f"Chatbot response: {response_time}ms")
```

## 🔒 Privacy & Security

### Data Protection
- **User Consent**: Clear data usage policies
- **Data Encryption**: Secure data transmission
- **Access Control**: User-specific data access
- **Retention Policies**: Data cleanup procedures

### API Security
- **Rate Limiting**: Prevent API abuse
- **Input Validation**: Sanitize user inputs
- **Error Handling**: Secure error messages
- **Monitoring**: Track suspicious activity

## 🆘 Troubleshooting

### Common Issues
1. **Model Loading Errors**:
   - Check file paths
   - Verify model files exist
   - Check permissions

2. **Gemini API Errors**:
   - Verify API key
   - Check rate limits
   - Monitor API status

3. **Database Connection**:
   - Verify MongoDB URI
   - Check network connectivity
   - Monitor connection pool

### Debug Commands
```python
# Test mood assessment
python -c "from src.mood_assessment import mood_assessor; print('Model loaded successfully')"

# Test chatbot
python -c "from src.gemini_chatbot import health_chatbot; print('Chatbot initialized')"

# Test database
python -c "from pymongo import MongoClient; client = MongoClient('your_uri'); print('Database connected')"
```

## 📚 API Reference

### Mood Assessment Endpoints
- `GET /mood-assessment` - Assessment interface
- `POST /api/mood-assessment` - Submit assessment
- `GET /mood-history` - View assessment history

### Chatbot Endpoints
- `GET /chatbot` - Chatbot interface
- `POST /api/chatbot` - Send message
- `GET /api/chatbot/insights` - Get health insights
- `GET /api/chatbot/resources` - Get mental health resources

## 🎯 Future Enhancements

### Planned Features
1. **Advanced ML Models**: Deep learning for mood prediction
2. **Voice Integration**: Voice-based assessments
3. **Wearable Integration**: Heart rate and stress monitoring
4. **Group Therapy**: Multi-user support features
5. **Crisis Intervention**: Automated crisis detection

### Technical Improvements
1. **Caching**: Redis for faster responses
2. **Real-time Updates**: WebSocket integration
3. **Mobile App**: React Native implementation
4. **Analytics Dashboard**: Advanced reporting
5. **A/B Testing**: Feature experimentation

---

**🎉 Congratulations!** You now have a comprehensive mood assessment and AI chatbot system integrated into your mental health support website. The system provides personalized insights, real-time support, and comprehensive tracking to help users on their mental health journey.

For support or questions, please refer to the main documentation or contact the development team.
