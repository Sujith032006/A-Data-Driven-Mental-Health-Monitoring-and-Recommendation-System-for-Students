import json
import random
import re
import datetime
import nltk
from textblob import TextBlob
import pandas as pd
import os
from analysis import generate_recommendation, load_data
from collections import defaultdict, Counter
import math

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('tokenizers/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class AdvancedMentalHealthChatbot:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))

        # Enhanced response database with more context-aware responses
        self.responses = {
            'greeting': [
                "Hi there! I'm August, your mental health companion. How are you doing today?",
                "Hello! I'm here to support you. What's on your mind?",
                "Hey! I'm August, ready to listen and help. How can I support you today?"
            ],
            'casual_greeting': [
                "Hi!",
                "Hello!",
                "Hey there!",
                "Hi! How's it going?"
            ],
            'mood_great': [
                "That's fantastic! I'm really happy to hear that. What's making you feel so good?",
                "Wonderful! Your positive energy is contagious. What's been the highlight of your day?",
                "That's awesome! Let's celebrate this good feeling. What's contributing to your great mood?"
            ],
            'mood_good': [
                "I'm glad you're feeling good! That's something to appreciate. What's been going well for you?",
                "Good to hear! Even small positive moments matter. What's lifted your spirits today?",
                "That's encouraging! Let's build on this positive momentum. What's making you feel this way?"
            ],
            'mood_neutral': [
                "I appreciate you sharing that. Sometimes 'okay' is exactly where we need to be. What's been on your mind?",
                "Thanks for being honest about feeling neutral. How has your day been treating you?",
                "I understand - not every day is amazing, and that's okay. Would you like to talk about anything specific?"
            ],
            'mood_bad': [
                "I'm really sorry you're feeling this way. I'm here for you. Would you like to talk about what's going on?",
                "I can hear that you're struggling, and I want you to know I'm here to listen without any judgment.",
                "Thank you for trusting me with how you're feeling. What's been the most difficult part lately?"
            ],
            'stress_high': [
                "I can sense how overwhelming this stress feels. Let's work through this together. What's causing you the most stress right now?",
                "Stress can be really challenging. You're taking an important step by acknowledging it. What's been weighing on you?",
                "I understand how debilitating stress can feel. Let's identify what's contributing to this and find some relief strategies."
            ],
            'anxiety': [
                "I hear the anxiety in your words, and I'm right here with you. Let's explore some techniques to help ease this feeling.",
                "Anxiety can feel so overwhelming, but you're not alone in this. What's been triggering these feelings lately?",
                "Thank you for sharing about your anxiety. Let's work on some grounding techniques to help you feel more centered."
            ],
            'depression': [
                "I want you to know that I see your courage in reaching out during this difficult time. What's been the hardest part for you?",
                "Your feelings are completely valid, and I'm here to support you through this. Would you like to talk about what's been weighing on you?",
                "Depression can make everything feel so heavy. I'm here to listen and help you find some light in the darkness."
            ],
            'sleep_issues': [
                "Sleep challenges can really impact our mental health. Let's explore what's affecting your sleep and develop a plan to improve it.",
                "I understand how frustrating poor sleep can be. What's been interfering with your rest lately?",
                "Quality sleep is so important for mental wellness. Let's identify what's disrupting your sleep patterns."
            ],
            'headache': [
                "I'm sorry to hear you're experiencing head pain. Headaches can be really debilitating. Are you feeling stressed or anxious lately? Sometimes tension and stress can contribute to headaches.",
                "Head pain can be challenging to deal with. I notice you mentioned having a headache - could stress or lack of sleep be playing a role? Let's explore what might be causing this.",
                "I can sense this headache is causing you discomfort. Sometimes headaches are related to stress, tension, or other factors. Would you like to talk about what might be contributing to this?"
            ],
            'crisis': [
                "I hear the depth of your pain, and I'm deeply concerned about your safety. Please reach out to a crisis professional immediately - you don't have to face this alone.",
                "Your wellbeing is the most important thing right now. Please contact emergency services (911) or the National Suicide Prevention Lifeline (988) immediately. I'm here, but professionals can provide the immediate help you need.",
                "I can sense this is an extremely difficult time for you. Please seek immediate professional help - call 988 for the Suicide Prevention Lifeline or 911 for emergency services. You're not alone, and there are people ready to help you through this crisis."
            ],
            'encouragement': [
                "You're showing incredible strength by taking care of your mental health. Every step you take matters.",
                "Your dedication to your wellbeing is inspiring. Remember that progress isn't always linear, but every effort counts.",
                "I admire your courage in prioritizing your mental health. You're building resilience with each positive choice."
            ],
            'follow_up_questions': [
                "How has your energy level been lately?",
                "What's been the most challenging part of your day?",
                "What activities usually help lift your mood?",
                "How are you sleeping these days?",
                "What's one thing that's been worrying you?",
                "How connected do you feel to the people around you?",
                "What's bringing you a sense of purpose right now?",
                "How do you typically cope with difficult emotions?",
                "What's been going well for you recently?",
                "Is there anything specific you'd like support with today?"
            ]
        }

        # Enhanced coping strategies with more detailed explanations
        self.coping_strategies = {
            'stress': [
                {
                    'technique': '5-4-3-2-1 Grounding',
                    'description': 'Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste. This brings you back to the present moment.',
                    'duration': '2-3 minutes',
                    'frequency': 'As needed during high stress'
                },
                {
                    'technique': '4-7-8 Breathing',
                    'description': 'Inhale for 4 counts, hold for 7, exhale for 8. This activates your parasympathetic nervous system for quick stress relief.',
                    'duration': '1-2 minutes',
                    'frequency': '3-5 times when feeling stressed'
                },
                {
                    'technique': 'Progressive Muscle Relaxation',
                    'description': 'Tense and release each muscle group from toes to head. This releases physical tension that accompanies stress.',
                    'duration': '10-15 minutes',
                    'frequency': 'Daily, especially before bed'
                },
                {
                    'technique': 'Gratitude Journaling',
                    'description': 'Write down 3 specific things you\'re grateful for each day. This shifts focus from stressors to positive aspects.',
                    'duration': '5 minutes',
                    'frequency': 'Daily, preferably in the morning'
                }
            ],
            'anxiety': [
                {
                    'technique': 'Cognitive Reframing',
                    'description': 'Challenge anxious thoughts by asking: "What\'s the evidence for this worry? What\'s the evidence against it? What\'s a more balanced thought?"',
                    'duration': '5-10 minutes',
                    'frequency': 'When anxious thoughts arise'
                },
                {
                    'technique': 'Mindfulness Meditation',
                    'description': 'Focus on your breath or present sensations without judgment. Apps like Headspace can guide you through this.',
                    'duration': '5-20 minutes',
                    'frequency': 'Daily practice builds resilience'
                },
                {
                    'technique': 'Grounding Objects',
                    'description': 'Keep a small object (stone, keychain) in your pocket. When anxious, focus all attention on its texture, weight, and temperature.',
                    'duration': '1-2 minutes',
                    'frequency': 'As needed for immediate relief'
                },
                {
                    'technique': 'Positive Affirmations',
                    'description': 'Repeat phrases like "I am safe," "I am capable," "This feeling will pass," and "I have handled difficult situations before."',
                    'duration': '2-3 minutes',
                    'frequency': 'Multiple times daily'
                }
            ],
            'depression': [
                {
                    'technique': 'Behavioral Activation',
                    'description': 'Break tasks into tiny steps and celebrate each completion. Even getting out of bed is a victory worth acknowledging.',
                    'duration': 'Varies',
                    'frequency': 'Daily small steps'
                },
                {
                    'technique': 'Social Connection',
                    'description': 'Reach out to one person daily, even if just to say "hello." Connection combats isolation that often accompanies depression.',
                    'duration': '5-15 minutes',
                    'frequency': 'Daily social contact'
                },
                {
                    'technique': 'Sunlight Exposure',
                    'description': 'Spend 10-15 minutes in natural sunlight daily. This helps regulate mood through vitamin D and circadian rhythm support.',
                    'duration': '10-15 minutes',
                    'frequency': 'Daily, preferably morning'
                },
                {
                    'technique': 'Self-Compassion Practice',
                    'description': 'Speak to yourself as you would to a dear friend. Acknowledge that it\'s okay to struggle and that you\'re worthy of kindness.',
                    'duration': '3-5 minutes',
                    'frequency': 'Multiple times daily'
                }
            ],
            'sleep': [
                {
                    'technique': 'Sleep Hygiene Routine',
                    'description': 'Create a consistent pre-bed routine: dim lights, avoid screens 1 hour before bed, keep bedroom cool and dark.',
                    'duration': '30-60 minutes before bed',
                    'frequency': 'Every night'
                },
                {
                    'technique': 'Stimulus Control',
                    'description': 'Use bed only for sleep and intimacy. If you can\'t sleep after 20 minutes, get up and do a quiet activity until drowsy.',
                    'duration': 'As needed',
                    'frequency': 'When sleep issues occur'
                },
                {
                    'technique': 'Cognitive Behavioral Techniques',
                    'description': 'Challenge racing thoughts by writing them down before bed and scheduling "worry time" earlier in the day.',
                    'duration': '10-15 minutes before bed',
                    'frequency': 'Nightly as needed'
                },
                {
                    'technique': 'Relaxation Response',
                    'description': 'Practice deep breathing or gentle yoga poses before bed to signal to your body that it\'s time to rest.',
                    'duration': '5-10 minutes',
                    'frequency': 'Every night before bed'
                }
            ]
        }

        # Enhanced resources with more comprehensive options
        self.resources = {
            'crisis': [
                "🚨 National Suicide Prevention Lifeline: Call or text 988 (24/7) - Trained counselors ready to help",
                "🚨 Crisis Text Line: Text HOME to 741741 - Text-based crisis support available 24/7",
                "🚨 Emergency Services: Call 911 - For immediate danger or medical emergencies",
                "🏫 Campus Counseling Center: Most schools offer free, confidential mental health services to students"
            ],
            'professional_help': [
                "🩺 Psychology Today (psychologytoday.com): Find licensed therapists in your area with detailed profiles",
                "💻 BetterHelp (betterhelp.com): Licensed online therapy with flexible scheduling",
                "💬 Talkspace (talkspace.com): Text and video therapy with licensed professionals",
                "🎓 Your School's Counseling Center: Free and confidential services for students",
                "🏥 Community Mental Health Centers: Low-cost or sliding-scale fee services based on income"
            ],
            'self_help': [
                "🧘 Headspace or Calm: Guided meditation and mindfulness exercises",
                "📊 Mood Tracking: Daylio, Moodpath, or eMoods apps for tracking patterns",
                "📚 CBT Workbooks: 'Feeling Good' by David Burns or 'Mind Over Mood'",
                "🌱 7 Cups: Free emotional support and trained listeners available 24/7",
                "💪 Sanvello: CBT-based anxiety and depression management with coping tools",
                "🎵 Music Therapy: Curated playlists for different moods and relaxation"
            ],
            'educational': [
                "📖 'The Body Keeps the Score' by Bessel van der Kolk - Understanding trauma",
                "📖 'Man's Search for Meaning' by Viktor Frankl - Finding purpose",
                "📖 'Atomic Habits' by James Clear - Building positive routines",
                "🎧 Mental Health Podcasts: 'The Mental Illness Happy Hour', 'Therapy for Black Girls'",
                "🎬 Documentaries: 'The Mind, Explained' on Netflix"
            ]
        }

        # Add general knowledge and Q&A responses
        self.general_responses = {
            'questions': {
                'how are you': ["I'm doing well, thank you for asking! I'm here and ready to support you. How are you feeling today?"],
                'what can you do': ["I can help you with mental health support, coping strategies, crisis intervention, and general wellbeing guidance. I'm here to listen and provide evidence-based support."],
                'tell me about yourself': ["I'm August, an AI mental health companion created to provide empathetic, intelligent support for mental wellness. I'm designed to understand emotions, provide coping strategies, and connect you with helpful resources."],
                'what is mental health': ["Mental health includes our emotional, psychological, and social wellbeing. It affects how we think, feel, and act, and it's important at every stage of life. Good mental health helps us cope with stress, relate to others, and make healthy choices."],
                'how to reduce stress': ["There are many effective ways to reduce stress: regular exercise, mindfulness practices, maintaining social connections, getting enough sleep, and setting healthy boundaries. Would you like specific techniques for stress management?"],
                'what is anxiety': ["Anxiety is your body's natural response to stress, but when it becomes excessive or persistent, it can interfere with daily life. It's characterized by feelings of worry, nervousness, or fear that are difficult to control."],
                'how to help depression': ["Supporting someone with depression involves listening without judgment, encouraging professional help, being patient, and helping with small daily tasks. If you're experiencing depression, reaching out for professional support is often the most helpful step."],
                'what is mindfulness': ["Mindfulness is the practice of maintaining a moment-by-moment awareness of our thoughts, feelings, bodily sensations, and surrounding environment with acceptance and without judgment. It helps reduce stress and improve mental clarity."],
                'how to sleep better': ["Good sleep hygiene includes maintaining a consistent sleep schedule, creating a relaxing bedtime routine, avoiding screens before bed, keeping your bedroom cool and dark, and avoiding caffeine late in the day. Would you like more specific sleep strategies?"]
            }
        }

        # Conversation context tracking
        self.conversation_memory = defaultdict(list)
        self.user_profiles = {}
        self.emotional_states = defaultdict(lambda: {'current_mood': 'neutral', 'stress_level': 5, 'anxiety_level': 5})

    def analyze_sentiment_advanced(self, text):
        """Advanced sentiment analysis using VADER"""
        scores = self.vader_analyzer.polarity_scores(text)

        # Get compound score and categorize
        compound = scores['compound']

        if compound >= 0.05:
            return 'positive', scores
        elif compound <= -0.05:
            return 'negative', scores
        else:
            return 'neutral', scores

    def detect_intent_advanced(self, message, conversation_history=None):
        """Advanced intent detection with context awareness"""
        message_lower = message.lower()
        tokens = word_tokenize(message_lower)

        # Remove stopwords for better analysis
        filtered_tokens = [word for word in tokens if word not in self.stop_words]

        # Simple greeting detection (handle casual greetings like "hi", "hello")
        simple_greetings = ['hi', 'hello', 'hey', 'hi there', 'hello there', 'hey there']
        if message_lower.strip() in simple_greetings or message_lower.strip() in ['hi', 'hello', 'hey']:
            return 'casual_greeting'

        # Crisis detection (highest priority)
        crisis_keywords = [
            'suicide', 'kill myself', 'end it all', 'not worth living', 'harm myself',
            'die', 'crisis', 'emergency', 'help me', 'can\'t take it anymore',
            'want to die', 'life not worth living'
        ]

        for keyword in crisis_keywords:
            if keyword in message_lower:
                return 'crisis'

        # Enhanced keyword detection with context
        intent_scores = defaultdict(float)

        # Mood-related (most common)
        mood_keywords = ['feel', 'feeling', 'mood', 'emotion', 'happy', 'sad', 'angry', 'excited', 'down', 'upset']
        for keyword in mood_keywords:
            if keyword in message_lower:
                intent_scores['mood'] += 1

        # Stress-related
        stress_keywords = ['stress', 'stressed', 'overwhelmed', 'pressure', 'workload', 'deadlines', 'busy', 'tired']
        for keyword in stress_keywords:
            if keyword in message_lower:
                intent_scores['stress'] += 1

        # Anxiety-related
        anxiety_keywords = ['anxious', 'anxiety', 'worried', 'worrying', 'panic', 'nervous', 'scared', 'fear']
        for keyword in anxiety_keywords:
            if keyword in message_lower:
                intent_scores['anxiety'] += 1

        # Depression-related
        depression_keywords = ['depressed', 'depression', 'sad', 'hopeless', 'empty', 'worthless', 'lonely', 'isolated']
        for keyword in depression_keywords:
            if keyword in message_lower:
                intent_scores['depression'] += 1

        # Sleep-related
        sleep_keywords = ['sleep', 'insomnia', 'tired', 'exhausted', 'fatigue', 'restless', 'nightmares']
        for keyword in sleep_keywords:
            if keyword in message_lower:
                intent_scores['sleep'] += 1

        # Headache-related keywords
        if any(word in message_lower for word in ['headache', 'head pain', 'migraine', 'head hurt', 'head hurts']):
            return 'headache'

        # Context from conversation history
        if conversation_history:
            recent_topics = conversation_history[-3:] if len(conversation_history) >= 3 else conversation_history
            for past_message in recent_topics:
                past_lower = past_message.lower()
                for intent, keywords in [('stress', stress_keywords), ('anxiety', anxiety_keywords), ('depression', depression_keywords)]:
                    for keyword in keywords:
                        if keyword in past_lower:
                            intent_scores[intent] += 0.5  # Boost score for recurring topics

        # Determine primary intent
        if intent_scores:
            primary_intent = max(intent_scores, key=intent_scores.get)
            if intent_scores[primary_intent] > 0:
                return primary_intent

        return 'general'

    def generate_contextual_response(self, intent, sentiment, user_data=None, conversation_history=None):
        """Generate sophisticated, context-aware responses"""
        response = {
            'message': '',
            'suggestions': [],
            'resources': [],
            'follow_up': [],
            'emotional_validation': '',
            'action_items': []
        }

        # Base response selection with sentiment awareness
        if intent == 'crisis':
            response['message'] = random.choice(self.responses['crisis'])
            response['resources'] = self.resources['crisis']
            response['action_items'] = ['Contact crisis services immediately', 'Tell a trusted person how you\'re feeling']

        elif intent == 'casual_greeting':
            response['message'] = random.choice(self.responses['casual_greeting'])
            response['follow_up'] = random.sample(self.responses['follow_up_questions'], 2)

        elif intent == 'mood':
            if sentiment == 'positive':
                response['message'] = random.choice(self.responses['mood_great'])
                response['emotional_validation'] = "I love hearing about your positive experiences!"
            elif sentiment == 'negative':
                response['message'] = random.choice(self.responses['mood_bad'])
                response['emotional_validation'] = "I can sense this is really difficult for you right now."
            else:
                response['message'] = random.choice(self.responses['mood_neutral'])
                response['emotional_validation'] = "Thank you for sharing how you're feeling with me."

            response['follow_up'] = random.sample(self.responses['follow_up_questions'], 2)

        elif intent == 'stress':
            response['message'] = random.choice(self.responses['stress_high'])
            response['emotional_validation'] = "I understand how overwhelming stress can feel."
            stress_strategies = random.sample(self.coping_strategies['stress'], min(2, len(self.coping_strategies['stress'])))
            response['suggestions'] = [f"{s['technique']}: {s['description']}" for s in stress_strategies]

        elif intent == 'anxiety':
            response['message'] = random.choice(self.responses['anxiety'])
            response['emotional_validation'] = "Anxiety can be incredibly challenging, and I want you to know you're not alone."
            anxiety_strategies = random.sample(self.coping_strategies['anxiety'], min(2, len(self.coping_strategies['anxiety'])))
            response['suggestions'] = [f"{s['technique']}: {s['description']}" for s in anxiety_strategies]

        elif intent == 'depression':
            response['message'] = random.choice(self.responses['depression'])
            response['emotional_validation'] = "Your feelings are valid, and reaching out shows incredible strength."
            depression_strategies = random.sample(self.coping_strategies['depression'], min(2, len(self.coping_strategies['depression'])))
            response['suggestions'] = [f"{s['technique']}: {s['description']}" for s in depression_strategies]

        elif intent == 'sleep':
            response['message'] = random.choice(self.responses['sleep_issues'])
            response['emotional_validation'] = "Sleep challenges are common and treatable."
            sleep_strategies = random.sample(self.coping_strategies['sleep'], min(2, len(self.coping_strategies['sleep'])))
            response['suggestions'] = [f"{s['technique']}: {s['description']}" for s in sleep_strategies]

        elif intent == 'headache':
            response['message'] = random.choice(self.responses['headache'])
            response['emotional_validation'] = "I understand how uncomfortable and distracting headaches can be."
            response['follow_up'] = ["Are you feeling stressed or anxious lately? Sometimes tension contributes to headaches.",
                                   "Have you been getting enough sleep? Poor sleep can often trigger headaches.",
                                   "Are you staying hydrated? Dehydration is a common headache trigger."]

        elif intent == 'help':
            response['message'] = "I'm here to support you in whatever way I can. What specific type of help are you looking for?"
            response['resources'] = self.resources['professional_help'][:2] + self.resources['self_help'][:2]
            response['follow_up'] = ["Are you looking for immediate coping strategies or longer-term support?",
                                   "What's been the most challenging aspect of your mental health lately?"]

        else:  # general conversation
            # Check if it's a general question
            question_answered = False
            for question, answers in self.general_responses['questions'].items():
                if question in message_lower:
                    response['message'] = random.choice(answers)
                    question_answered = True
                    break

            if not question_answered:
                response['message'] = random.choice(self.responses['greeting'])
                response['follow_up'] = random.sample(self.responses['follow_up_questions'], 2)

        # Add contextual insights based on user data
        if user_data and isinstance(user_data, dict):
            # Personalized suggestions based on survey data
            if 'Stress_Level' in user_data and user_data['Stress_Level'] >= 7:
                pass  # Remove stress level suggestion
            if 'Sleep_Hours' in user_data and user_data['Sleep_Hours'] <= 6:
                pass  # Remove sleep suggestion
            if 'Depression_Level' in user_data and user_data['Depression_Level'] >= 7:
                pass  # Remove depression suggestion

        # Add encouragement and validation
        if sentiment == 'negative' or intent in ['stress', 'anxiety', 'depression']:
            response['emotional_validation'] += " " + random.choice(self.responses['encouragement'])

        return response

    def update_emotional_state(self, username, intent, sentiment):
        """Track user's emotional state over time"""
        if username not in self.emotional_states:
            self.emotional_states[username] = {'current_mood': 'neutral', 'stress_level': 5, 'anxiety_level': 5}

        # Update based on conversation patterns
        if intent == 'stress':
            self.emotional_states[username]['stress_level'] = min(10, self.emotional_states[username]['stress_level'] + 1)
        elif intent == 'anxiety':
            self.emotional_states[username]['anxiety_level'] = min(10, self.emotional_states[username]['anxiety_level'] + 1)
        elif intent == 'mood' and sentiment == 'positive':
            self.emotional_states[username]['stress_level'] = max(1, self.emotional_states[username]['stress_level'] - 0.5)
            self.emotional_states[username]['anxiety_level'] = max(1, self.emotional_states[username]['anxiety_level'] - 0.5)

        # Update current mood
        if sentiment == 'positive':
            self.emotional_states[username]['current_mood'] = 'positive'
        elif sentiment == 'negative':
            self.emotional_states[username]['current_mood'] = 'negative'
        else:
            self.emotional_states[username]['current_mood'] = 'neutral'

    def get_response(self, message, user_data=None, username=None, conversation_history=None):
        """Enhanced main response generation method"""
        # Analyze sentiment and intent
        sentiment, sentiment_scores = self.analyze_sentiment_advanced(message)
        intent = self.detect_intent_advanced(message, conversation_history or [])

        # Update emotional state tracking
        if username:
            self.update_emotional_state(username, intent, sentiment)
            self.conversation_memory[username].append({
                'message': message,
                'intent': intent,
                'sentiment': sentiment,
                'timestamp': datetime.datetime.now()
            })

        # Generate contextual response
        response = self.generate_contextual_response(intent, sentiment, user_data, conversation_history)

        # Add personalized elements if we have username
        if username:
            current_state = self.emotional_states.get(username, {})
            if current_state.get('stress_level', 5) > 7:
                response['suggestions'].append("Remember to be gentle with yourself during high-stress periods.")
            if current_state.get('anxiety_level', 5) > 7:
                response['suggestions'].append("Take things one moment at a time - you're doing better than you think.")

        # Ensure response has meaningful content
        if not response['message']:
            response['message'] = "I'm here to support you. Could you tell me more about how you're feeling or what you'd like to discuss?"

        return response

    def save_conversation(self, username, message, response):
        """Enhanced conversation saving with more detailed tracking"""
        conversation_file = f"conversations/{username}_chat.json"

        os.makedirs("conversations", exist_ok=True)

        conversation_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'user_message': message,
            'bot_response': response['message'],
            'intent': self.detect_intent_advanced(message),
            'sentiment': self.analyze_sentiment_advanced(message)[0],
            'emotional_state': dict(self.emotional_states.get(username, {}))
        }

        # Load existing conversation or create new one
        if os.path.exists(conversation_file):
            try:
                with open(conversation_file, 'r') as f:
                    conversations = json.load(f)
            except:
                conversations = []
        else:
            conversations = []

        conversations.append(conversation_data)

        # Keep only last 200 conversations per user for advanced AI
        if len(conversations) > 200:
            conversations = conversations[-200:]

        with open(conversation_file, 'w') as f:
            json.dump(conversations, f, indent=2)

    def get_user_insights(self, username):
        """Advanced user insights with detailed analytics"""
        conversation_file = f"conversations/{username}_chat.json"

        if not os.path.exists(conversation_file):
            return None

        try:
            with open(conversation_file, 'r') as f:
                conversations = json.load(f)
        except:
            return None

        if not conversations:
            return None

        # Advanced analytics
        intents = [conv.get('intent', 'general') for conv in conversations]
        sentiments = [conv.get('sentiment', 'neutral') for conv in conversations]

        # Calculate conversation patterns
        intent_counts = Counter(intents)
        sentiment_counts = Counter(sentiments)

        # Time-based analysis (last 30 days)
        thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        recent_conversations = [
            conv for conv in conversations
            if datetime.datetime.fromisoformat(conv['timestamp']) > thirty_days_ago
        ]

        recent_intents = [conv.get('intent', 'general') for conv in recent_conversations]

        insights = {
            'total_conversations': len(conversations),
            'most_common_intent': intent_counts.most_common(1)[0][0] if intent_counts else 'general',
            'intent_distribution': dict(intent_counts.most_common()),
            'overall_sentiment': sentiment_counts.most_common(1)[0][0] if sentiment_counts else 'neutral',
            'sentiment_distribution': dict(sentiment_counts.most_common()),
            'recent_trends': Counter(recent_intents).most_common(),
            'emotional_state_history': [conv.get('emotional_state', {}) for conv in conversations[-10:]]
        }

        return insights

# Global chatbot instance
chatbot = AdvancedMentalHealthChatbot()
