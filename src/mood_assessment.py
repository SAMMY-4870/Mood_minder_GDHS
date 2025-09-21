"""
Mood Assessment System with Machine Learning
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime
from pymongo import MongoClient

# MongoDB Connection
MONGO_URI = "mongodb+srv://Samarth_90:Samarth%409090@moodminder.dci9zcf.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["happy_quotes_db"]

# Comprehensive Mental Health Assessment Questions
HEALTH_QUESTIONS = [
    # Depression-related questions
    {
        "id": 1,
        "question": "How would you rate your overall mood today?",
        "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"],
        "category": "depression",
        "weight": 0.12,
        "mental_condition": "depression"
    },
    {
        "id": 2,
        "question": "How often do you feel sad, empty, or hopeless?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "depression",
        "weight": 0.10,
        "mental_condition": "depression"
    },
    {
        "id": 3,
        "question": "How interested are you in activities you used to enjoy?",
        "options": ["Not at all", "Slightly", "Moderately", "Very", "Extremely"],
        "category": "depression",
        "weight": 0.08,
        "mental_condition": "depression"
    },
    {
        "id": 4,
        "question": "How often do you feel worthless or guilty?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "depression",
        "weight": 0.08,
        "mental_condition": "depression"
    },
    {
        "id": 5,
        "question": "How is your energy level right now?",
        "options": ["Very Low", "Low", "Moderate", "High", "Very High"],
        "category": "depression",
        "weight": 0.08,
        "mental_condition": "depression"
    },
    
    # Anxiety-related questions
    {
        "id": 6,
        "question": "How anxious or worried do you feel?",
        "options": ["Not at all", "Slightly", "Moderately", "Very", "Extremely"],
        "category": "anxiety",
        "weight": 0.10,
        "mental_condition": "anxiety"
    },
    {
        "id": 7,
        "question": "How often do you experience excessive worry or fear?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "anxiety",
        "weight": 0.08,
        "mental_condition": "anxiety"
    },
    {
        "id": 8,
        "question": "How often do you feel restless or on edge?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "anxiety",
        "weight": 0.07,
        "mental_condition": "anxiety"
    },
    {
        "id": 9,
        "question": "How often do you experience panic attacks or sudden intense fear?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "anxiety",
        "weight": 0.08,
        "mental_condition": "anxiety"
    },
    {
        "id": 10,
        "question": "How often do you avoid situations that make you anxious?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "anxiety",
        "weight": 0.07,
        "mental_condition": "anxiety"
    },
    
    # Bipolar-related questions
    {
        "id": 11,
        "question": "How often do you experience extreme mood swings?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "bipolar",
        "weight": 0.08,
        "mental_condition": "bipolar"
    },
    {
        "id": 12,
        "question": "How often do you feel unusually energetic or hyperactive?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "bipolar",
        "weight": 0.07,
        "mental_condition": "bipolar"
    },
    {
        "id": 13,
        "question": "How often do you engage in risky or impulsive behaviors?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "bipolar",
        "weight": 0.07,
        "mental_condition": "bipolar"
    },
    {
        "id": 14,
        "question": "How often do you need less sleep than usual?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "bipolar",
        "weight": 0.06,
        "mental_condition": "bipolar"
    },
    
    # PTSD-related questions
    {
        "id": 15,
        "question": "How often do you experience flashbacks or intrusive memories?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "ptsd",
        "weight": 0.08,
        "mental_condition": "ptsd"
    },
    {
        "id": 16,
        "question": "How often do you have nightmares or disturbing dreams?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "ptsd",
        "weight": 0.07,
        "mental_condition": "ptsd"
    },
    {
        "id": 17,
        "question": "How often do you feel hypervigilant or constantly on guard?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "ptsd",
        "weight": 0.07,
        "mental_condition": "ptsd"
    },
    {
        "id": 18,
        "question": "How often do you avoid reminders of traumatic events?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "ptsd",
        "weight": 0.06,
        "mental_condition": "ptsd"
    },
    
    # OCD-related questions
    {
        "id": 19,
        "question": "How often do you experience intrusive, unwanted thoughts?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "ocd",
        "weight": 0.08,
        "mental_condition": "ocd"
    },
    {
        "id": 20,
        "question": "How often do you feel compelled to repeat certain behaviors or rituals?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "ocd",
        "weight": 0.08,
        "mental_condition": "ocd"
    },
    {
        "id": 21,
        "question": "How often do you check things repeatedly (locks, switches, etc.)?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "ocd",
        "weight": 0.06,
        "mental_condition": "ocd"
    },
    {
        "id": 22,
        "question": "How often do you feel the need to arrange things in a specific order?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "ocd",
        "weight": 0.06,
        "mental_condition": "ocd"
    },
    
    # ADHD-related questions
    {
        "id": 23,
        "question": "How well can you concentrate on tasks?",
        "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"],
        "category": "adhd",
        "weight": 0.08,
        "mental_condition": "adhd"
    },
    {
        "id": 24,
        "question": "How often do you have trouble sitting still or feel restless?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "adhd",
        "weight": 0.07,
        "mental_condition": "adhd"
    },
    {
        "id": 25,
        "question": "How often do you interrupt others or have trouble waiting your turn?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "adhd",
        "weight": 0.06,
        "mental_condition": "adhd"
    },
    {
        "id": 26,
        "question": "How often do you lose or misplace things?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "adhd",
        "weight": 0.06,
        "mental_condition": "adhd"
    },
    
    # General mental health questions
    {
        "id": 27,
        "question": "How well did you sleep last night?",
        "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"],
        "category": "sleep",
        "weight": 0.08,
        "mental_condition": "general"
    },
    {
        "id": 28,
        "question": "How stressed do you feel today?",
        "options": ["Not at all", "Slightly", "Moderately", "Very", "Extremely"],
        "category": "stress",
        "weight": 0.08,
        "mental_condition": "general"
    },
    {
        "id": 29,
        "question": "How confident do you feel about handling daily tasks?",
        "options": ["Not at all", "Slightly", "Moderately", "Very", "Extremely"],
        "category": "confidence",
        "weight": 0.06,
        "mental_condition": "general"
    },
    {
        "id": 30,
        "question": "How satisfied are you with your current life situation?",
        "options": ["Very Dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very Satisfied"],
        "category": "satisfaction",
        "weight": 0.07,
        "mental_condition": "general"
    },
    {
        "id": 31,
        "question": "How often do you feel overwhelmed by your responsibilities?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "overwhelm",
        "weight": 0.06,
        "mental_condition": "general"
    },
    {
        "id": 32,
        "question": "How motivated do you feel to pursue your goals?",
        "options": ["Not at all", "Slightly", "Moderately", "Very", "Extremely"],
        "category": "motivation",
        "weight": 0.06,
        "mental_condition": "general"
    },
    {
        "id": 33,
        "question": "How often do you experience physical tension or muscle tightness?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "physical_tension",
        "weight": 0.05,
        "mental_condition": "general"
    },
    {
        "id": 34,
        "question": "How is your appetite today?",
        "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"],
        "category": "appetite",
        "weight": 0.05,
        "mental_condition": "general"
    },
    {
        "id": 35,
        "question": "How often do you feel irritable or easily frustrated?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "irritability",
        "weight": 0.06,
        "mental_condition": "general"
    },
    {
        "id": 36,
        "question": "How connected do you feel to others around you?",
        "options": ["Not at all", "Slightly", "Moderately", "Very", "Extremely"],
        "category": "social_connection",
        "weight": 0.06,
        "mental_condition": "general"
    },
    {
        "id": 37,
        "question": "How hopeful do you feel about the future?",
        "options": ["Not at all", "Slightly", "Moderately", "Very", "Extremely"],
        "category": "hope",
        "weight": 0.07,
        "mental_condition": "general"
    },
    {
        "id": 38,
        "question": "How often do you experience racing thoughts or mental chatter?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "racing_thoughts",
        "weight": 0.06,
        "mental_condition": "general"
    },
    {
        "id": 39,
        "question": "How well do you handle unexpected changes or challenges?",
        "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"],
        "category": "resilience",
        "weight": 0.07,
        "mental_condition": "general"
    },
    {
        "id": 40,
        "question": "How often do you feel lonely or isolated?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "loneliness",
        "weight": 0.06,
        "mental_condition": "general"
    },
    {
        "id": 41,
        "question": "How satisfied are you with your current work-life balance?",
        "options": ["Very Dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very Satisfied"],
        "category": "work_life_balance",
        "weight": 0.06,
        "mental_condition": "general"
    },
    {
        "id": 42,
        "question": "How often do you engage in activities that bring you joy?",
        "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
        "category": "joy_activities",
        "weight": 0.06,
        "mental_condition": "general"
    }
]

# Mental Health Conditions and their characteristics
MENTAL_HEALTH_CONDITIONS = {
    "depression": {
        "threshold": 0.6,
        "description": "Signs of depression detected. You may be experiencing persistent sadness, loss of interest, or feelings of hopelessness.",
        "recommendations": [
            "Consider professional therapy or counseling",
            "Practice regular physical exercise",
            "Maintain a consistent sleep schedule",
            "Engage in activities you used to enjoy",
            "Connect with supportive friends and family",
            "Try mindfulness and meditation practices"
        ],
        "games": ["breathing", "memory", "puzzle"],
        "color": "#6f42c1",
        "icon": "💙"
    },
    "anxiety": {
        "threshold": 0.6,
        "description": "Signs of anxiety detected. You may be experiencing excessive worry, restlessness, or panic symptoms.",
        "recommendations": [
            "Practice deep breathing exercises",
            "Try progressive muscle relaxation",
            "Limit caffeine and alcohol intake",
            "Establish a regular routine",
            "Consider cognitive behavioral therapy",
            "Use grounding techniques during panic attacks"
        ],
        "games": ["breathing", "reaction", "memory"],
        "color": "#ff6b6b",
        "icon": "😰"
    },
    "bipolar": {
        "threshold": 0.5,
        "description": "Signs of bipolar disorder detected. You may be experiencing extreme mood swings or periods of high energy.",
        "recommendations": [
            "Seek professional psychiatric evaluation",
            "Maintain a mood journal",
            "Establish regular sleep patterns",
            "Avoid alcohol and drugs",
            "Learn about triggers and warning signs",
            "Build a strong support network"
        ],
        "games": ["breathing", "puzzle", "trivia"],
        "color": "#feca57",
        "icon": "🌊"
    },
    "ptsd": {
        "threshold": 0.5,
        "description": "Signs of PTSD detected. You may be experiencing flashbacks, nightmares, or hypervigilance.",
        "recommendations": [
            "Seek trauma-focused therapy (EMDR, CBT)",
            "Practice grounding techniques",
            "Avoid triggers when possible",
            "Build a safety plan",
            "Consider support groups",
            "Focus on present-moment awareness"
        ],
        "games": ["breathing", "memory", "puzzle"],
        "color": "#ff9ff3",
        "icon": "🛡️"
    },
    "ocd": {
        "threshold": 0.5,
        "description": "Signs of OCD detected. You may be experiencing intrusive thoughts or compulsive behaviors.",
        "recommendations": [
            "Seek exposure and response prevention therapy",
            "Practice mindfulness meditation",
            "Challenge obsessive thoughts",
            "Gradually reduce compulsive behaviors",
            "Consider medication evaluation",
            "Join OCD support groups"
        ],
        "games": ["memory", "puzzle", "trivia"],
        "color": "#54a0ff",
        "icon": "🔄"
    },
    "adhd": {
        "threshold": 0.5,
        "description": "Signs of ADHD detected. You may be experiencing difficulty concentrating or hyperactivity.",
        "recommendations": [
            "Consider professional evaluation",
            "Use organizational tools and apps",
            "Break tasks into smaller steps",
            "Practice mindfulness and meditation",
            "Establish routines and structure",
            "Consider medication if recommended"
        ],
        "games": ["reaction", "memory", "trivia"],
        "color": "#5f27cd",
        "icon": "⚡"
    }
}

# Overall Mood Categories
MOOD_CATEGORIES = {
    "excellent": {
        "score_range": (80, 100),
        "description": "You're feeling great! Your mental health is in excellent condition.",
        "recommendations": [
            "Continue your current healthy habits",
            "Share your positive energy with others",
            "Consider mentoring someone who might be struggling",
            "Document what's working well for you"
        ],
        "color": "#28a745",
        "icon": "🌟"
    },
    "good": {
        "score_range": (60, 79),
        "description": "You're doing well overall with some areas for improvement.",
        "recommendations": [
            "Maintain your current routine",
            "Focus on areas that scored lower",
            "Try some stress-relief activities",
            "Connect with friends or family"
        ],
        "color": "#17a2b8",
        "icon": "😊"
    },
    "moderate": {
        "score_range": (40, 59),
        "description": "You're experiencing some challenges but have the strength to overcome them.",
        "recommendations": [
            "Practice mindfulness and breathing exercises",
            "Consider talking to a trusted friend or counselor",
            "Engage in physical activity",
            "Focus on small, achievable goals"
        ],
        "color": "#ffc107",
        "icon": "😐"
    },
    "poor": {
        "score_range": (20, 39),
        "description": "You're going through a difficult time. It's important to seek support.",
        "recommendations": [
            "Consider professional mental health support",
            "Reach out to trusted friends or family",
            "Practice self-care activities",
            "Consider reducing your workload temporarily"
        ],
        "color": "#fd7e14",
        "icon": "😔"
    },
    "critical": {
        "score_range": (0, 19),
        "description": "You're experiencing significant distress. Please seek immediate support.",
        "recommendations": [
            "Contact a mental health professional immediately",
            "Reach out to crisis support services",
            "Stay connected with supportive people",
            "Consider emergency mental health resources"
        ],
        "color": "#dc3545",
        "icon": "🚨"
    }
}

class MoodAssessment:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_path = "outputs/models/mood_model.pkl"
        self.scaler_path = "outputs/models/mood_scaler.pkl"
        self.load_or_train_model()
    
    def analyze_game_performance(self, game_data):
        """Analyze game performance to understand mood patterns"""
        analysis = {
            "concentration_score": 0,
            "stress_level": 0,
            "patience_level": 0,
            "mood_indicators": []
        }
        
        # Analyze different game types
        for game_type, performance in game_data.items():
            if game_type == "memory":
                # Memory game performance indicates concentration
                if performance.get("accuracy", 0) > 0.8:
                    analysis["concentration_score"] += 20
                    analysis["mood_indicators"].append("Good concentration")
                elif performance.get("accuracy", 0) < 0.5:
                    analysis["concentration_score"] -= 15
                    analysis["mood_indicators"].append("Difficulty concentrating")
            
            elif game_type == "reaction":
                # Reaction time indicates stress and anxiety
                avg_reaction_time = performance.get("avg_reaction_time", 0)
                if avg_reaction_time > 500:  # milliseconds
                    analysis["stress_level"] += 20
                    analysis["mood_indicators"].append("High stress levels")
                elif avg_reaction_time < 200:
                    analysis["stress_level"] -= 10
                    analysis["mood_indicators"].append("Calm and focused")
            
            elif game_type == "breathing":
                # Breathing exercise completion indicates self-regulation
                if performance.get("completed", False):
                    analysis["stress_level"] -= 15
                    analysis["mood_indicators"].append("Good self-regulation")
                else:
                    analysis["stress_level"] += 10
                    analysis["mood_indicators"].append("Difficulty with relaxation")
            
            elif game_type == "puzzle":
                # Puzzle solving indicates patience and problem-solving
                if performance.get("time_to_solve", 0) < 60:  # seconds
                    analysis["patience_level"] += 15
                    analysis["mood_indicators"].append("Good problem-solving skills")
                elif performance.get("time_to_solve", 0) > 300:
                    analysis["patience_level"] -= 10
                    analysis["mood_indicators"].append("Difficulty with complex tasks")
        
        return analysis
    
    def detect_mental_health_conditions(self, responses):
        """Detect specific mental health conditions based on responses"""
        condition_scores = {}
        
        # Handle both dictionary and list formats
        if isinstance(responses, dict):
            # Dictionary format - use question IDs as keys
            response_dict = responses
        else:
            # List format - convert to dictionary
            response_dict = {}
            for i, response in enumerate(responses):
                if i < len(HEALTH_QUESTIONS):
                    response_dict[HEALTH_QUESTIONS[i]["id"]] = response
        
        # Group responses by mental condition
        for condition in MENTAL_HEALTH_CONDITIONS.keys():
            condition_questions = [q for q in HEALTH_QUESTIONS if q.get("mental_condition") == condition]
            if not condition_questions:
                continue
                
            total_score = 0
            total_weight = 0
            
            for question in condition_questions:
                question_id = question["id"]
                if question_id in response_dict:
                    # Convert 1-5 scale to 0-1 scale
                    normalized_response = (response_dict[question_id] - 1) / 4
                    weighted_score = normalized_response * question["weight"]
                    total_score += weighted_score
                    total_weight += question["weight"]
            
            if total_weight > 0:
                condition_scores[condition] = total_score / total_weight
        
        return condition_scores
    
    def get_recommended_games(self, detected_conditions, overall_mood):
        """Get recommended games based on detected conditions and mood"""
        recommended_games = set()
        
        # Add games based on detected conditions
        for condition, score in detected_conditions.items():
            if score > MENTAL_HEALTH_CONDITIONS[condition]["threshold"]:
                condition_games = MENTAL_HEALTH_CONDITIONS[condition]["games"]
                recommended_games.update(condition_games)
        
        # Add games based on overall mood
        if overall_mood in ["poor", "critical"]:
            recommended_games.update(["breathing", "puzzle", "memory"])
        elif overall_mood == "moderate":
            recommended_games.update(["memory", "reaction", "trivia"])
        else:
            recommended_games.update(["trivia", "rps", "guess"])
        
        return list(recommended_games)
    
    def load_or_train_model(self):
        """Load existing model or train a new one"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            try:
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                print("Loaded existing mood assessment model")
            except:
                self.train_model()
        else:
            self.train_model()
    
    def train_model(self):
        """Train a machine learning model for mood prediction"""
        print("Training mood assessment model...")
        print(f"Training with {len(HEALTH_QUESTIONS)} questions")
        
        # Create synthetic training data based on question patterns
        np.random.seed(42)
        n_samples = 1000
        
        # Generate synthetic data
        X = np.random.randint(1, 6, (n_samples, len(HEALTH_QUESTIONS)))
        
        # Calculate mood scores based on weighted responses
        mood_scores = []
        for i in range(n_samples):
            score = 0
            for j, question in enumerate(HEALTH_QUESTIONS):
                response = X[i, j]
                # Convert 1-5 scale to 0-4 scale, then to 0-100
                normalized_response = (response - 1) / 4 * 100
                # Apply question weight
                weighted_score = normalized_response * question["weight"]
                score += weighted_score
            mood_scores.append(score)
        
        # Categorize mood scores
        y = []
        for score in mood_scores:
            if score >= 80:
                y.append(0)  # excellent
            elif score >= 60:
                y.append(1)  # good
            elif score >= 40:
                y.append(2)  # moderate
            elif score >= 20:
                y.append(3)  # poor
            else:
                y.append(4)  # critical
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        
        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        # Calculate accuracy
        accuracy = self.model.score(X_test_scaled, y_test)
        print(f"Model trained with accuracy: {accuracy:.2f}")
        print(f"Model expects {len(HEALTH_QUESTIONS)} features")
    
    def calculate_mood_score(self, responses):
        """Calculate mood score from responses"""
        if len(responses) != len(HEALTH_QUESTIONS):
            raise ValueError("Number of responses must match number of questions")
        
        total_score = 0
        category_scores = {}
        
        for i, response in enumerate(responses):
            question = HEALTH_QUESTIONS[i]
            # Convert 1-5 scale to 0-100 scale
            normalized_response = (response - 1) / 4 * 100
            # Apply question weight
            weighted_score = normalized_response * question["weight"]
            total_score += weighted_score
            
            # Track category scores
            category = question["category"]
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(normalized_response)
        
        # Calculate average scores for each category
        for category in category_scores:
            category_scores[category] = np.mean(category_scores[category])
        
        return total_score, category_scores
    
    def predict_mood_category(self, responses):
        """Predict mood category using ML model"""
        if self.model is None or self.scaler is None:
            # Fallback to rule-based approach
            score, _ = self.calculate_mood_score(responses)
            return self.score_to_category(score)
        
        # Prepare data for prediction
        X = np.array(responses).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.model.predict(X_scaled)[0]
        
        # Map prediction to category
        categories = ["excellent", "good", "moderate", "poor", "critical"]
        return categories[prediction]
    
    def score_to_category(self, score):
        """Convert numerical score to mood category"""
        for category, info in MOOD_CATEGORIES.items():
            min_score, max_score = info["score_range"]
            if min_score <= score <= max_score:
                return category
        return "moderate"  # Default fallback
    
    def get_mood_analysis(self, responses, game_data=None):
        """Get comprehensive mood analysis with mental health condition detection"""
        # Handle both dictionary (from Quick Mood Check) and list (from Full Assessment) formats
        if isinstance(responses, dict):
            # Convert dictionary to list format for compatibility
            response_list = []
            for question in HEALTH_QUESTIONS:
                question_id = question["id"]
                if question_id in responses:
                    response_list.append(responses[question_id])
                else:
                    # Use default value (3 = "Fair/Moderate") for missing questions
                    response_list.append(3)
            responses = response_list
        
        score, category_scores = self.calculate_mood_score(responses)
        category = self.predict_mood_category(responses)
        
        # Detect mental health conditions
        condition_scores = self.detect_mental_health_conditions(responses)
        detected_conditions = {k: v for k, v in condition_scores.items() 
                             if v > MENTAL_HEALTH_CONDITIONS[k]["threshold"]}
        
        # Analyze game performance if provided
        game_analysis = None
        if game_data:
            game_analysis = self.analyze_game_performance(game_data)
        
        # Get recommended games
        recommended_games = self.get_recommended_games(condition_scores, category)
        
        # Get category information
        mood_info = MOOD_CATEGORIES[category]
        
        # Identify areas of concern
        areas_of_concern = []
        areas_of_strength = []
        
        for cat, cat_score in category_scores.items():
            if cat_score < 40:
                areas_of_concern.append(cat)
            elif cat_score > 70:
                areas_of_strength.append(cat)
        
        # Generate personalized insights
        insights = self.generate_insights(category_scores, areas_of_concern, areas_of_strength)
        
        # Add mental health condition insights
        if detected_conditions:
            for condition, score in detected_conditions.items():
                condition_info = MENTAL_HEALTH_CONDITIONS[condition]
                insights.append(f"⚠️ {condition_info['description']}")
                insights.extend(condition_info['recommendations'][:3])  # Top 3 recommendations
        
        # Add game-based insights
        if game_analysis:
            insights.extend(game_analysis['mood_indicators'])
        
        # Create comprehensive recommendations
        all_recommendations = list(mood_info["recommendations"])
        for condition in detected_conditions.keys():
            condition_recommendations = MENTAL_HEALTH_CONDITIONS[condition]["recommendations"]
            all_recommendations.extend(condition_recommendations[:2])  # Top 2 per condition
        
        return {
            "overall_score": round(score, 1),
            "mood_category": category,
            "description": mood_info["description"],
            "recommendations": all_recommendations,
            "color": mood_info["color"],
            "icon": mood_info["icon"],
            "category_scores": category_scores,
            "areas_of_concern": areas_of_concern,
            "areas_of_strength": areas_of_strength,
            "insights": insights,
            "detected_conditions": detected_conditions,
            "condition_scores": condition_scores,
            "recommended_games": recommended_games,
            "game_analysis": game_analysis,
            "timestamp": datetime.utcnow()
        }
    
    def generate_insights(self, category_scores, areas_of_concern, areas_of_strength):
        """Generate personalized insights based on assessment"""
        insights = []
        
        # Mood insights
        if category_scores.get("mood", 0) < 40:
            insights.append("Your mood seems to be low today. Consider engaging in activities that usually bring you joy.")
        elif category_scores.get("mood", 0) > 70:
            insights.append("You're in a great mood! This is a perfect time to tackle challenging tasks.")
        
        # Sleep insights
        if category_scores.get("sleep", 0) < 40:
            insights.append("Poor sleep quality can significantly impact your mood and energy. Try establishing a consistent bedtime routine.")
        
        # Stress insights
        if category_scores.get("stress", 0) > 60:
            insights.append("High stress levels detected. Consider practicing relaxation techniques like deep breathing or meditation.")
        
        # Anxiety insights
        if category_scores.get("anxiety", 0) > 60:
            insights.append("You're experiencing elevated anxiety. Grounding techniques and mindfulness can help manage these feelings.")
        
        # Energy insights
        if category_scores.get("energy", 0) < 40:
            insights.append("Low energy levels might be affecting your overall well-being. Consider light physical activity or a short walk.")
        
        # Social connection insights
        if category_scores.get("social_connection", 0) < 40:
            insights.append("Feeling disconnected from others? Consider reaching out to a friend or joining a social activity.")
        
        # Hope insights
        if category_scores.get("hope", 0) < 40:
            insights.append("It's normal to feel less hopeful sometimes. Focus on small, achievable goals to rebuild optimism.")
        
        return insights
    
    def save_assessment(self, user_email, responses, analysis):
        """Save assessment to database"""
        assessment_data = {
            "user_email": user_email,
            "responses": responses,
            "analysis": analysis,
            "timestamp": datetime.utcnow()
        }
        
        db.mood_assessments.insert_one(assessment_data)
        
        # Also update user's current mood status
        db.users.update_one(
            {"email": user_email},
            {
                "$set": {
                    "current_mood": analysis["mood_category"],
                    "mood_score": analysis["overall_score"],
                    "last_assessment": datetime.utcnow()
                }
            }
        )
    
    def get_user_mood_history(self, user_email, days=30):
        """Get user's mood assessment history"""
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        assessments = list(db.mood_assessments.find({
            "user_email": user_email,
            "timestamp": {"$gte": start_date}
        }).sort("timestamp", -1))
        
        return assessments
    
    def get_random_questions(self, count=5):
        """Get random subset of questions for quick assessment"""
        import random
        return random.sample(HEALTH_QUESTIONS, count)

# Initialize global mood assessment instance
mood_assessor = MoodAssessment()
