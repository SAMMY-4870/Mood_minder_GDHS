"""
Gemini AI Chatbot for Mental Health Support
"""
import google.generativeai as genai
import json
from datetime import datetime
from pymongo import MongoClient
import os

# MongoDB Connection
MONGO_URI = "mongodb+srv://Samarth_90:Samarth%409090@moodminder.dci9zcf.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["happy_quotes_db"]

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyAXk9rw8otEWVJw_MmyDxLGGh5WxGj9Q9Q"
genai.configure(api_key=GEMINI_API_KEY)

class GeminiHealthChatbot:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.conversation_history = {}
        
        # Enhanced system prompt for comprehensive health support
        self.system_prompt = """
        You are a comprehensive AI health and wellness assistant. Your role is to provide support across multiple areas:
        
        MENTAL HEALTH SUPPORT:
        1. Provide empathetic, non-judgmental responses
        2. Offer evidence-based mental health information
        3. Suggest practical coping strategies and techniques
        4. Encourage professional help when appropriate
        5. Focus on positive mental health practices
        6. Be supportive and encouraging
        7. Avoid giving medical diagnoses or treatment advice
        8. Always prioritize user safety and well-being
        
        PHYSICAL HEALTH & FITNESS:
        1. Provide general fitness tips and exercise suggestions
        2. Offer nutrition and healthy eating guidance
        3. Suggest sleep improvement strategies
        4. Give hydration and wellness reminders
        5. Recommend preventive care practices
        6. Encourage healthy lifestyle choices
        
        STRESS MANAGEMENT:
        1. Teach breathing exercises and relaxation techniques
        2. Suggest mindfulness and meditation practices
        3. Provide time management and organization tips
        4. Offer work-life balance strategies
        5. Recommend stress-reducing activities
        
        MOOD-BASED SUGGESTIONS:
        - For sad/depressed users: Suggest uplifting music, positive quotes, gentle activities
        - For anxious users: Recommend breathing exercises, grounding techniques, calming games
        - For stressed users: Suggest meditation, relaxation music, stress-relief activities
        - For energetic users: Recommend physical activities, goal-setting, productivity tips
        
        Guidelines:
        - Use a warm, supportive tone
        - Ask clarifying questions when needed
        - Provide actionable, specific advice
        - Include relevant resources and activities
        - Be culturally sensitive and inclusive
        - Keep responses concise but helpful
        - Encourage self-care and professional support
        - Suggest specific app features when relevant (breathing games, music, quotes)
        
        If someone expresses thoughts of self-harm or suicide, immediately encourage them to:
        - Contact emergency services (911/112)
        - Call a suicide prevention hotline
        - Reach out to a trusted friend or family member
        - Seek immediate professional help
        
        Remember: You are not a replacement for professional medical or mental health care.
        """
    
    def get_user_context(self, user_email):
        """Get user's recent mood and activity context"""
        try:
            # Get recent mood assessment
            recent_assessment = db.mood_assessments.find_one(
                {"user_email": user_email},
                sort=[("timestamp", -1)]
            )
            
            # Get recent activity
            recent_activities = list(db.user_activity.find(
                {"user_email": user_email}
            ).sort("timestamp", -1).limit(5))
            
            context = ""
            
            if recent_assessment:
                mood_data = recent_assessment.get("analysis", {})
                context += f"User's recent mood: {mood_data.get('mood_category', 'unknown')} "
                context += f"(Score: {mood_data.get('overall_score', 'N/A')}/100). "
                
                if mood_data.get("areas_of_concern"):
                    context += f"Areas of concern: {', '.join(mood_data['areas_of_concern'])}. "
                
                if mood_data.get("areas_of_strength"):
                    context += f"Areas of strength: {', '.join(mood_data['areas_of_strength'])}. "
            
            if recent_activities:
                activity_types = [act.get("action", "") for act in recent_activities]
                context += f"Recent activities: {', '.join(set(activity_types))}. "
            
            return context
            
        except Exception as e:
            print(f"Error getting user context: {e}")
            return ""
    
    def generate_response(self, user_message, user_email=None, conversation_id=None):
        """Generate chatbot response using Gemini"""
        try:
            # Get user context if available
            user_context = ""
            if user_email:
                user_context = self.get_user_context(user_email)
            
            # Get conversation history
            if conversation_id:
                history = self.conversation_history.get(conversation_id, [])
            else:
                history = []
            
            # Build conversation context
            conversation_context = ""
            if history:
                conversation_context = "Previous conversation:\n"
                for msg in history[-6:]:  # Last 6 messages
                    conversation_context += f"{msg['role']}: {msg['content']}\n"
                conversation_context += "\n"
            
            # Create full prompt
            full_prompt = f"""
            {self.system_prompt}
            
            {user_context}
            
            {conversation_context}
            
            User: {user_message}
            
            Assistant:"""
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            if response.text:
                # Clean up response
                response_text = response.text.strip()
                
                # Save to conversation history
                if conversation_id:
                    if conversation_id not in self.conversation_history:
                        self.conversation_history[conversation_id] = []
                    
                    self.conversation_history[conversation_id].append({
                        "role": "user",
                        "content": user_message,
                        "timestamp": datetime.utcnow()
                    })
                    
                    self.conversation_history[conversation_id].append({
                        "role": "assistant",
                        "content": response_text,
                        "timestamp": datetime.utcnow()
                    })
                
                # Save to database
                self.save_conversation(user_email, user_message, response_text, conversation_id)
                
                return {
                    "response": response_text,
                    "timestamp": datetime.utcnow(),
                    "success": True
                }
            else:
                # Provide a fallback response based on keywords
                fallback_response = self.get_fallback_response(user_message)
                return {
                    "response": fallback_response,
                    "timestamp": datetime.utcnow(),
                    "success": True
                }
                
        except Exception as e:
            print(f"Error generating response: {e}")
            import traceback
            traceback.print_exc()
            
            # Provide more specific error messages
            if "404" in str(e):
                return {
                    "response": "I'm currently updating my systems. Please try again in a moment.",
                    "timestamp": datetime.utcnow(),
                    "success": False
                }
            elif "quota" in str(e).lower() or "limit" in str(e).lower():
                return {
                    "response": "I'm experiencing high demand right now. Please try again in a few minutes.",
                    "timestamp": datetime.utcnow(),
                    "success": False
                }
            else:
                return {
                    "response": "I'm sorry, I'm experiencing technical difficulties. Please try again in a moment.",
                    "timestamp": datetime.utcnow(),
                    "success": False
                }
    
    def save_conversation(self, user_email, user_message, bot_response, conversation_id):
        """Save conversation to database"""
        try:
            conversation_data = {
                "user_email": user_email,
                "conversation_id": conversation_id,
                "user_message": user_message,
                "bot_response": bot_response,
                "timestamp": datetime.utcnow()
            }
            
            db.chatbot_conversations.insert_one(conversation_data)
            
        except Exception as e:
            print(f"Error saving conversation: {e}")
    
    def get_conversation_history(self, user_email, conversation_id=None, limit=20):
        """Get conversation history for user"""
        try:
            query = {"user_email": user_email}
            if conversation_id:
                query["conversation_id"] = conversation_id
            
            conversations = list(db.chatbot_conversations.find(query)
                               .sort("timestamp", -1)
                               .limit(limit))
            
            return conversations
            
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    def get_quick_responses(self, mood_category):
        """Get quick response suggestions based on mood"""
        quick_responses = {
            "excellent": [
                "That's wonderful! What's contributing to your great mood today?",
                "I'm so happy to hear you're feeling excellent! How can we maintain this positive energy?",
                "Your positive mood is inspiring! What activities are bringing you joy?",
                "Share your positive energy with others today!",
                "What goals would you like to tackle with this great energy?"
            ],
            "good": [
                "I'm glad you're feeling good! What's working well for you right now?",
                "That's great to hear! How can we build on this positive momentum?",
                "You're doing well! What would you like to focus on today?",
                "Let's keep this positive momentum going!",
                "What healthy habits are you maintaining?"
            ],
            "moderate": [
                "I understand you're feeling moderate today. What's on your mind?",
                "It's okay to have mixed feelings. What would help you feel better?",
                "I'm here to listen. What's been challenging for you lately?",
                "Let's find some activities to boost your mood",
                "What self-care would feel good right now?"
            ],
            "poor": [
                "I'm sorry you're having a tough time. You're not alone in this. What's weighing on you?",
                "I can hear that you're struggling. What would be most helpful right now?",
                "It takes courage to acknowledge when things are difficult. How can I support you today?",
                "Let's try some gentle breathing exercises together",
                "Would you like to listen to some calming music?"
            ],
            "critical": [
                "I'm concerned about how you're feeling. Are you safe right now?",
                "Your well-being is important. Please consider reaching out to a mental health professional.",
                "I want to help you get the support you need. What's the most urgent concern right now?",
                "Please reach out to someone you trust right now",
                "Your safety is the most important thing right now"
            ]
        }
        
        return quick_responses.get(mood_category, [
            "I'm here to listen and support you. What would you like to talk about?",
            "How are you feeling today? I'm here to help.",
            "What's on your mind? I'm ready to listen.",
            "Would you like to try a breathing exercise?",
            "Let's explore some wellness activities together"
        ])
    
    def get_fallback_response(self, user_message):
        """Provide fallback responses when API fails"""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['anxiety', 'anxious', 'worried', 'nervous']):
            return """I understand you're dealing with anxiety. Here are some helpful strategies:

• **Deep Breathing**: Try the 4-7-8 technique - inhale for 4, hold for 7, exhale for 8
• **Grounding**: Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste
• **Progressive Muscle Relaxation**: Tense and release each muscle group
• **Mindfulness**: Focus on the present moment without judgment

Remember, anxiety is treatable. Consider reaching out to a mental health professional for ongoing support."""

        elif any(word in message_lower for word in ['depression', 'depressed', 'sad', 'down']):
            return """I'm sorry you're feeling this way. Depression can be really challenging. Here are some supportive strategies:

• **Small Steps**: Focus on one small task at a time
• **Stay Connected**: Reach out to friends, family, or support groups
• **Physical Activity**: Even a short walk can help boost mood
• **Routine**: Try to maintain regular sleep and meal times
• **Professional Help**: Consider therapy or counseling

You're not alone in this. Professional help can make a significant difference."""

        elif any(word in message_lower for word in ['stress', 'stressed', 'overwhelmed']):
            return """Stress can feel overwhelming. Here are some effective stress management techniques:

• **Time Management**: Break large tasks into smaller, manageable steps
• **Relaxation**: Try meditation, yoga, or deep breathing exercises
• **Physical Activity**: Regular exercise helps reduce stress hormones
• **Healthy Boundaries**: Learn to say no when you're already stretched thin
• **Support Network**: Don't hesitate to ask for help when needed

Remember, it's okay to take breaks and prioritize your well-being."""

        elif any(word in message_lower for word in ['sleep', 'insomnia', 'tired', 'exhausted']):
            return """Sleep issues can really impact your well-being. Here are some sleep hygiene tips:

• **Consistent Schedule**: Go to bed and wake up at the same time daily
• **Bedroom Environment**: Keep it cool, dark, and quiet
• **Wind Down Routine**: Avoid screens 1 hour before bed
• **Limit Caffeine**: Avoid caffeine after 2 PM
• **Relaxation**: Try reading, gentle stretching, or meditation before bed

If sleep problems persist, consider consulting a healthcare provider."""

        else:
            return """I'm here to listen and support you. While I'm experiencing some technical difficulties, I want you to know that:

• Your feelings are valid and important
• It's okay to not be okay sometimes
• Seeking help is a sign of strength, not weakness
• There are resources and people who care about your well-being

If you're in crisis, please reach out to:
• National Suicide Prevention Lifeline: 988
• Crisis Text Line: Text HOME to 741741
• Emergency Services: 911

You matter, and help is available."""

    def get_mental_health_resources(self, topic=None):
        """Get relevant mental health resources"""
        resources = {
            "general": [
                "National Suicide Prevention Lifeline: 988",
                "Crisis Text Line: Text HOME to 741741",
                "National Alliance on Mental Illness (NAMI): 1-800-950-NAMI",
                "Mental Health America: www.mhanational.org"
            ],
            "anxiety": [
                "Anxiety and Depression Association of America: www.adaa.org",
                "Anxiety.org: www.anxiety.org",
                "Calm app for meditation and relaxation",
                "Headspace app for mindfulness"
            ],
            "depression": [
                "Depression and Bipolar Support Alliance: www.dbsalliance.org",
                "National Institute of Mental Health: www.nimh.nih.gov",
                "MoodGYM: Online CBT program",
                "7 Cups: Online therapy and support"
            ],
            "stress": [
                "American Psychological Association: www.apa.org",
                "Stress Management Society: www.stress.org",
                "Mindful.org for mindfulness resources",
                "Insight Timer app for meditation"
            ],
            "sleep": [
                "National Sleep Foundation: www.sleepfoundation.org",
                "Sleep.org for sleep tips and resources",
                "Sleep Cycle app for sleep tracking",
                "Calm app for sleep stories"
            ]
        }
        
        if topic and topic in resources:
            return resources[topic]
        else:
            return resources["general"]
    
    def generate_health_insights(self, user_email):
        """Generate personalized health insights based on user data"""
        try:
            # Get recent mood assessment
            recent_assessment = db.mood_assessments.find_one(
                {"user_email": user_email},
                sort=[("timestamp", -1)]
            )
            
            if not recent_assessment:
                return "Complete a mood assessment to get personalized health insights."
            
            mood_data = recent_assessment.get("analysis", {})
            mood_category = mood_data.get("mood_category", "moderate")
            areas_of_concern = mood_data.get("areas_of_concern", [])
            areas_of_strength = mood_data.get("areas_of_strength", [])
            
            # Generate insights using Gemini
            prompt = f"""
            Based on this mental health assessment data, provide personalized health insights and recommendations:
            
            Mood Category: {mood_category}
            Overall Score: {mood_data.get('overall_score', 'N/A')}/100
            Areas of Concern: {', '.join(areas_of_concern) if areas_of_concern else 'None'}
            Areas of Strength: {', '.join(areas_of_strength) if areas_of_strength else 'None'}
            
            Please provide:
            1. A brief analysis of their current mental health status
            2. 3-5 specific, actionable recommendations
            3. Encouraging and supportive tone
            4. Focus on practical steps they can take today
            
            Keep the response concise but helpful (200-300 words).
            """
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text.strip()
            else:
                return "I'm having trouble generating insights right now. Please try again later."
                
        except Exception as e:
            print(f"Error generating health insights: {e}")
            return "I'm experiencing technical difficulties. Please try again later."
    
    def get_daily_health_tips(self, category=None):
        """Get daily health and wellness tips"""
        health_tips = {
            "general": [
                "Start your day with a glass of water to kickstart your metabolism",
                "Take a 5-minute walk every hour to improve circulation",
                "Practice deep breathing for 2 minutes to reduce stress",
                "Eat a rainbow of fruits and vegetables for optimal nutrition",
                "Get 7-9 hours of quality sleep for better mental health"
            ],
            "nutrition": [
                "Include protein in every meal to maintain stable energy",
                "Drink water before meals to help with portion control",
                "Eat slowly and mindfully to improve digestion",
                "Include healthy fats like avocado and nuts in your diet",
                "Limit processed foods and focus on whole foods"
            ],
            "fitness": [
                "Take the stairs instead of the elevator when possible",
                "Do 10 minutes of stretching in the morning",
                "Try a 20-minute walk during your lunch break",
                "Practice yoga or gentle movement for flexibility",
                "Set a goal to move for at least 30 minutes daily"
            ],
            "sleep": [
                "Keep your bedroom cool, dark, and quiet",
                "Avoid screens 1 hour before bedtime",
                "Establish a consistent sleep schedule",
                "Create a relaxing bedtime routine",
                "Limit caffeine after 2 PM"
            ],
            "stress": [
                "Practice the 4-7-8 breathing technique daily",
                "Take regular breaks from work or screens",
                "Try progressive muscle relaxation",
                "Spend time in nature when possible",
                "Practice gratitude by writing down 3 good things daily"
            ]
        }
        
        if category and category in health_tips:
            return health_tips[category]
        else:
            # Return a mix of tips from different categories
            all_tips = []
            for tips in health_tips.values():
                all_tips.extend(tips)
            return all_tips[:5]  # Return 5 random tips
    
    def get_fitness_suggestions(self, fitness_level="beginner"):
        """Get personalized fitness suggestions"""
        suggestions = {
            "beginner": [
                "Start with 10-15 minutes of walking daily",
                "Try bodyweight exercises like squats and push-ups",
                "Join a beginner yoga class or follow online videos",
                "Focus on consistency rather than intensity",
                "Listen to your body and rest when needed"
            ],
            "intermediate": [
                "Increase workout duration to 30-45 minutes",
                "Add resistance training 2-3 times per week",
                "Try interval training for cardiovascular fitness",
                "Include flexibility and mobility work",
                "Set specific, measurable fitness goals"
            ],
            "advanced": [
                "Incorporate high-intensity interval training (HIIT)",
                "Focus on sport-specific training",
                "Include recovery and active rest days",
                "Consider working with a personal trainer",
                "Track performance metrics and adjust accordingly"
            ]
        }
        
        return suggestions.get(fitness_level, suggestions["beginner"])
    
    def get_sleep_improvement_tips(self):
        """Get comprehensive sleep improvement strategies"""
        return [
            "Maintain a consistent sleep schedule, even on weekends",
            "Create a relaxing bedtime routine (reading, gentle music)",
            "Keep your bedroom temperature between 65-68°F (18-20°C)",
            "Use blackout curtains or an eye mask to block light",
            "Avoid large meals, caffeine, and alcohol before bedtime",
            "Try relaxation techniques like meditation or deep breathing",
            "Limit screen time 1 hour before bed",
            "Exercise regularly, but not too close to bedtime",
            "Keep your bedroom only for sleep and intimacy",
            "If you can't sleep, get up and do something relaxing until you feel tired"
        ]
    
    def get_nutrition_guidance(self, goal="general_health"):
        """Get nutrition guidance based on goals"""
        guidance = {
            "general_health": [
                "Eat a variety of colorful fruits and vegetables",
                "Choose whole grains over refined grains",
                "Include lean proteins in every meal",
                "Stay hydrated with water throughout the day",
                "Limit added sugars and processed foods"
            ],
            "weight_management": [
                "Focus on portion control and mindful eating",
                "Include fiber-rich foods to feel full longer",
                "Eat regular meals to maintain stable blood sugar",
                "Choose nutrient-dense foods over calorie-dense ones",
                "Keep a food journal to track eating patterns"
            ],
            "energy_boost": [
                "Eat regular, balanced meals throughout the day",
                "Include complex carbohydrates for sustained energy",
                "Stay hydrated - dehydration causes fatigue",
                "Limit caffeine to avoid energy crashes",
                "Include iron-rich foods to prevent anemia"
            ],
            "heart_health": [
                "Choose healthy fats like olive oil and avocados",
                "Limit saturated and trans fats",
                "Include omega-3 rich foods like fish and nuts",
                "Reduce sodium intake",
                "Eat plenty of fiber-rich foods"
            ]
        }
        
        return guidance.get(goal, guidance["general_health"])
    
    def get_mood_based_activities(self, mood_category):
        """Get specific activities based on user's mood"""
        activities = {
            "sad": {
                "immediate": [
                    "Listen to uplifting music",
                    "Read positive quotes",
                    "Take a gentle walk outside",
                    "Call a friend or family member",
                    "Practice gratitude by writing down 3 good things"
                ],
                "app_features": [
                    "Try the breathing exercise game",
                    "Listen to calming music",
                    "Read inspirational quotes",
                    "Play a gentle memory game",
                    "View happy images"
                ]
            },
            "stressed": {
                "immediate": [
                    "Practice 4-7-8 breathing technique",
                    "Do progressive muscle relaxation",
                    "Take a 10-minute break from current task",
                    "Listen to nature sounds or calming music",
                    "Try the 5-4-3-2-1 grounding technique"
                ],
                "app_features": [
                    "Use the breathing exercise game",
                    "Listen to meditation music",
                    "Play stress-relief puzzle games",
                    "Read calming quotes",
                    "Try the reaction time game for focus"
                ]
            },
            "anxious": {
                "immediate": [
                    "Practice box breathing (4-4-4-4)",
                    "Use grounding techniques",
                    "Focus on slow, deep breathing",
                    "Try gentle stretching or yoga",
                    "Listen to calming instrumental music"
                ],
                "app_features": [
                    "Try the breathing exercise game",
                    "Listen to calming music",
                    "Play memory games for distraction",
                    "Read positive affirmations",
                    "Use the puzzle game for focus"
                ]
            },
            "energetic": {
                "immediate": [
                    "Channel energy into physical activity",
                    "Set and work toward a goal",
                    "Try a new hobby or skill",
                    "Help someone else with a task",
                    "Plan something exciting for later"
                ],
                "app_features": [
                    "Play challenging games",
                    "Listen to upbeat music",
                    "Read motivational quotes",
                    "Try the reaction time game",
                    "Explore new content"
                ]
            }
        }
        
        return activities.get(mood_category, activities["sad"])
    
    def get_symptom_guidance(self, symptoms):
        """Provide general health guidance for symptoms (not diagnosis)"""
        symptom_guidance = {
            "headache": [
                "Stay hydrated - drink plenty of water",
                "Rest in a quiet, dark room",
                "Apply a cold compress to your forehead",
                "Practice relaxation techniques",
                "Consider over-the-counter pain relief if appropriate",
                "If severe or persistent, consult a healthcare provider"
            ],
            "fatigue": [
                "Ensure you're getting 7-9 hours of quality sleep",
                "Stay hydrated throughout the day",
                "Eat regular, balanced meals",
                "Get some gentle exercise or fresh air",
                "Check if you're getting enough iron and B vitamins",
                "If persistent, consider consulting a healthcare provider"
            ],
            "stress": [
                "Practice deep breathing exercises",
                "Take regular breaks from work or screens",
                "Try meditation or mindfulness",
                "Engage in physical activity",
                "Maintain a regular sleep schedule",
                "Consider talking to a mental health professional"
            ],
            "sleep_issues": [
                "Maintain a consistent sleep schedule",
                "Create a relaxing bedtime routine",
                "Keep your bedroom cool, dark, and quiet",
                "Avoid screens 1 hour before bed",
                "Limit caffeine after 2 PM",
                "If problems persist, consult a healthcare provider"
            ]
        }
        
        # Find matching symptoms
        guidance = []
        for symptom, tips in symptom_guidance.items():
            if any(keyword in symptoms.lower() for keyword in [symptom, symptom.replace("_", " ")]):
                guidance.extend(tips)
        
        if not guidance:
            guidance = [
                "Listen to your body and rest when needed",
                "Stay hydrated and eat nutritious foods",
                "Practice stress management techniques",
                "Get adequate sleep and exercise",
                "If symptoms persist or worsen, consult a healthcare provider"
            ]
        
        return guidance[:6]  # Return up to 6 tips

# Initialize global chatbot instance
health_chatbot = GeminiHealthChatbot()
