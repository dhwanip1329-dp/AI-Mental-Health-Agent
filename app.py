# AI Mental Health & Sleep Support Agent
# Web-Compatible Version of Your Original Code

import os
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import google.generativeai as genai
import datetime
import time
import json
import random
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here' # IMPORTANT: Change this to a strong, unique secret key for production!
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Configure API Key securely
API_key = os.getenv("GEMINI_API_KEY")
if not API_key:
    print("Warning: GEMINI_API_KEY environment variable not set. Please set it for production.")
    # For local testing, you can temporarily hardcode it here, but REMOVE FOR DEPLOYMENT!
    # If you remove this hardcoded key, you MUST set the GEMINI_API_KEY environment variable
    # before running the app, e.g., export GEMINI_API_KEY="YOUR_ACTUAL_KEY_HERE"
    API_key = "AIzaSyBOYiOdvlrP2PGjbqYr5mrHgQoMy7lhn44"
genai.configure(api_key=API_key)

# Initialize the model
model = genai.GenerativeModel('models/gemini-1.5-flash')

# Create user profile storage (in-memory for this demo)
user_profiles = {}

# Your original functions - mostly unchanged, but we'll adapt their prompts for better style where appropriate
def get_current_time_info():
    """Get current time and determine if it's bedtime"""
    now = datetime.datetime.now()
    hour = now.hour
    
    if 22 <= hour or hour <= 6:  # 10 PM to 6 AM
        time_context = "bedtime"
    elif 6 < hour <= 12:
        time_context = "morning"
    elif 12 < hour <= 17:
        time_context = "afternoon"
    else:
        time_context = "evening"
    
    return time_context, now.strftime("%H:%M")

def create_user_profile(name):
    """Create a new user profile"""
    user_profiles[name] = {
        "name": name,
        "stress_level": 5,  # 1-10 scale
        "sleep_quality": 5,  # 1-10 scale
        "last_checkin": None,
        "preferences": [],
        "mood_history": [],
        "sleep_schedule": {"bedtime": "22:00", "wake_time": "07:00"}
    }
    return user_profiles[name]

def daily_checkin(user_name):
    """Conduct a personalized daily check-in"""
    if user_name not in user_profiles:
        create_user_profile(user_name)
    
    time_context, current_time = get_current_time_info()
    
    # Updated prompt for more human touch and emojis
    checkin_prompt = f"""
    You are a friendly, warm, and compassionate AI mental health companion named Luna.
    It's currently {time_context} ({current_time}).
    
    Conduct a personalized daily check-in with {user_name}. Use a conversational tone and natural emojis to add warmth. Do NOT use bullet points or numbered lists.
    
    Ask 2-3 gentle questions:
    - How are they genuinely feeling right now, emotionally and energy-wise? 🤔
    - If it's morning, how was their sleep? 😴 If it's evening, how are they preparing for sleep? 🌙
    - Is there anything specific on their mind or any challenges they're facing today?
    
    End with a supportive and encouraging message, inviting them to share more or ask for support.
    """
    
    response = model.generate_content(checkin_prompt)
    return response.text.strip()

def stress_management_suggestions(user_name, stress_level, specific_concern=""):
    """Generate personalized stress management techniques"""
    if user_name not in user_profiles:
        create_user_profile(user_name)
    
    user_profile = user_profiles[user_name]
    
    # Updated prompt for more human touch and emojis
    stress_prompt = f"""
    You are a calm, supportive, and understanding AI companion named Luna, focused on stress relief.
    {user_name}, you've indicated a stress level of {stress_level}/10.
    Specific concern: {specific_concern if specific_concern else "General stress."}
    
    Provide 3-4 practical and actionable stress-reducing techniques. Present them conversationally, like a friend offering advice. Use relevant emojis naturally. Do NOT use bullet points or numbered lists.
    
    Include:
    1.  An immediate, quick technique (2-3 minutes).
    2.  A simple breathing or mindfulness exercise with brief instructions.
    3.  A gentle physical activity suggestion.
    4.  A thought on cognitive reframing or self-talk.
    
    Keep the tone encouraging and focus on steps {user_name} can take right now.
    """
    
    response = model.generate_content(stress_prompt)
    
    # Update user profile
    user_profile["stress_level"] = stress_level
    user_profile["last_checkin"] = datetime.datetime.now().isoformat()
    
    return response.text.strip()

def bedtime_support(user_name, sleep_concerns=""):
    """Provide bedtime support and sleep hygiene tips"""
    if user_name not in user_profiles:
        create_user_profile(user_name)
    
    user_profile = user_profiles[user_name]
    
    # Updated prompt for more human touch and emojis
    bedtime_prompt = f"""
    You are a gentle and soothing AI sleep companion named Luna.
    {user_name}, you're looking for bedtime support.
    Sleep concerns: {sleep_concerns if sleep_concerns else "General sleep support."}
    
    Provide a calming bedtime routine with practical tips. Present them conversationally, like guiding a friend to peaceful sleep. Use gentle, sleep-promoting emojis. Do NOT use bullet points or numbered lists.
    
    Include:
    1.  2-3 immediate relaxation techniques for tonight.
    2.  A brief, guided mental exercise (e.g., a simple body scan or visualization).
    3.  A couple of key sleep hygiene tips for better long-term rest.
    4.  A gentle, encouraging message for peaceful dreams. 😴✨
    
    Focus on techniques that can be done without screens, creating a serene atmosphere.
    """
    
    response = model.generate_content(bedtime_prompt)
    return response.text.strip()

def mood_tracking(user_name, mood_rating, mood_description=""):
    """Track and analyze mood patterns"""
    if user_name not in user_profiles:
        create_user_profile(user_name)
    
    user_profile = user_profiles[user_name]
    
    # Store mood data
    mood_entry = {
        "date": datetime.datetime.now().isoformat(),
        "rating": mood_rating,
        "description": mood_description
    }
    user_profile["mood_history"].append(mood_entry)
    
    # Updated prompt for more human touch and emojis
    mood_prompt = f"""
    You are a supportive and insightful AI companion named Luna, helping {user_name} track their mood.
    {user_name}, you've rated your current mood at {mood_rating}/10.
    You described it as: "{mood_description}"
    
    Provide an empathetic response. Use a conversational tone and natural emojis. Do NOT use bullet points or numbered lists.
    
    - If mood is low (1-4): Offer gentle validation, support, and suggest coping strategies.
    - If mood is moderate (5-7): Provide understanding and encouragement for maintaining well-being.
    - If mood is high (8-10): Celebrate their positive feelings and discuss how to nurture them.
    
    End with an open invitation for further conversation or support.
    """
    
    response = model.generate_content(mood_prompt)
    return response.text.strip()

def emergency_support():
    """Provide immediate support for crisis situations"""
    # This prompt should remain very direct and clear, less "chatty" for safety
    crisis_prompt = """
    You are an immediate crisis support AI assistant. Someone may be experiencing severe distress.
    
    Provide:
    1.  Immediate validation, reassurance, and a clear statement of support.
    2.  A very simple, immediate grounding technique (e.g., focusing on breath or senses).
    3.  A clear reminder that they are not alone and help is available.
    4.  **Crucially, strongly advise them to reach out to a trusted person or professional help.**
    5.  **Provide examples of where to find crisis support (e.g., "a local crisis hotline," "emergency services," "a mental health professional"). Avoid giving specific numbers as they can vary by region.**
    
    Be compassionate, non-judgmental, and focus on immediate safety and stabilization. Keep the response calm, direct, and reassuring. Use very few, subtle emojis if any, focusing on clarity.
    """
    
    response = model.generate_content(crisis_prompt)
    return response.text.strip()

def positive_affirmations(user_name):
    """Generate personalized positive affirmations"""
    # Updated prompt for more human touch and emojis
    affirmation_prompt = f"""
    You are a positive and uplifting AI companion named Luna, creating affirmations for {user_name}.
    
    Generate 3-5 personalized positive affirmations. Present them as if you're gently speaking to {user_name}, encouraging them. Use encouraging emojis naturally. Do NOT use bullet points or numbered lists.
    
    Make sure they are:
    - Present tense and positive.
    - Relevant to common challenges (e.g., self-worth, capability, growth, peace).
    - Empowering and realistic.
    
    Wrap them in a warm, inspiring message that {user_name} can repeat to themselves.
    """
    
    response = model.generate_content(affirmation_prompt)
    return response.text.strip()

# Web API endpoints using your original functions
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle general chat messages"""
    data = request.json
    message = data.get('message', '')
    
    # Get or create user session
    user_name = session.get('user_name', data.get('user_name', 'Friend'))
    session['user_name'] = user_name # Ensure user_name is in session for subsequent calls
    
    message_lower = message.lower()
    response_text = ""
    response_type = "general"

    # --- Specific Command Routing (these are mostly unchanged in their prompt structure) ---
    if any(word in message_lower for word in ['checkin', 'check in', 'how am i doing']):
        response_text = daily_checkin(user_name)
        response_type = 'checkin'
    elif any(word in message_lower for word in ['emergency', 'crisis', 'help me', 'urgent']):
        response_text = emergency_support()
        response_type = 'emergency'
    elif any(word in message_lower for word in ['affirmation', 'positive', 'encourage']):
        response_text = positive_affirmations(user_name)
        response_type = 'affirmations'
    # --- General Chat Handling with Human Touch and Emojis ---
    else:
        # Define base conversational prompt instructions
        base_instructions = "You are a warm, empathetic, and encouraging AI mental health companion named Luna. Your responses should feel like a supportive friend talking. Use a conversational tone, be gentle, and integrate relevant emojis naturally to convey emotion and warmth, but don't overdo them. Do NOT use bullet points, asterisks, or numbered lists. Introduce suggestions smoothly within paragraphs."

        # Keyword-based routing for nuanced general chat responses
        if any(word in message_lower for word in ['sad', 'unhappy', 'down', 'depressed', 'lonely', 'mourning']):
            prompt_template = f"""
            {base_instructions}

            {user_name} has just shared: "{message}". They seem to be feeling sad or down.

            Your response should:
            1.  Acknowledge and Validate: Start by expressing genuine empathy and validating their feelings. Normalize sadness.
            2.  Gentle Inquiry: Casually ask if there's a specific reason, offering space to share but ensuring no pressure.
            3.  Offer Simple, Actionable Tips (2-3): Embed 2-3 very easy, immediate, and practical suggestions directly into the conversation. Examples: a quick breathing exercise, listening to a favorite comforting song, or a reminder about self-kindness.
            4.  Professional Help Disclaimer: Include a gentle, non-alarming suggestion to reach out for professional help if feelings persist or worsen, emphasizing it's a sign of strength. Mention general types of resources (e.g., a doctor, a therapist, or a helpline).
            5.  Encouraging Closing: End on a hopeful and supportive note, inviting further conversation.
            
            Aim for a comforting and actionable response, around 3-5 short paragraphs.
            """
        elif any(word in message_lower for word in ['anxious', 'nervous', 'worried', 'stressed', 'overwhelmed', 'panic']):
            prompt_template = f"""
            {base_instructions}

            {user_name} has just shared: "{message}". They seem to be feeling anxious or stressed.

            Your response should:
            1.  Acknowledge and Validate: Express empathy for their anxiety/worry.
            2.  Gentle Inquiry: Ask if they can pinpoint a source of anxiety, with no pressure.
            3.  Immediate Grounding/Calming Technique: Offer one simple grounding exercise (e.g., 5-4-3-2-1 senses, or a box breathing). Explain it briefly.
            4.  Perspective/Acceptance: A gentle reminder that these feelings are temporary.
            5.  Professional Help: Reiterate the importance of professional help if anxiety is overwhelming or persistent.
            6.  Open Invitation: Invite them to share more or ask for other types of support.

            Keep the tone soothing and practical.
            """
        elif any(word in message_lower for word in ['tired', 'sleepy', 'can\'t sleep', 'insomnia', 'awake']):
             prompt_template = f"""
            {base_instructions}

            {user_name} has just shared: "{message}". They seem to be struggling with sleep or feeling tired.

            Your response should:
            1.  Acknowledge and Validate: Express understanding for their sleep struggles or fatigue.
            2.  Gentle Inquiry: Ask if they know what might be contributing to it (e.g., mind racing, discomfort).
            3.  Offer a couple of very simple, immediate relaxation tips for bedtime: a quick body scan, deep breathing, or a gentle visualization.
            4.  Brief Sleep Hygiene Tip: Suggest one easy long-term sleep hygiene tip (e.g., consistent schedule, dimming lights).
            5.  Supportive Closing: Offer words of comfort and hope for better rest.
            """
        elif any(word in message_lower for word in ['happy', 'good', 'great', 'excited', 'joyful']):
            prompt_template = f"""
            {base_instructions}

            {user_name} has just shared: "{message}". They seem to be feeling happy or positive!

            Your response should:
            1.  Celebrate their positive mood genuinely! 🎉
            2.  Ask what's making them feel good, encouraging them to savor it.
            3.  Suggest a simple way to prolong or deepen this positive feeling (e.g., gratitude journaling, sharing with someone, a moment of reflection).
            4.  Reinforce the importance of appreciating these moments.
            5.  Offer continued support for maintaining well-being.
            """
        else:
            # Default general conversational prompt if no specific sentiment is detected
            prompt_template = f"""
            {base_instructions}

            {user_name} said: "{message}".

            Respond in a thoughtful and engaging way. Ask a gentle follow-up question if appropriate to keep the conversation flowing.
            """

        response_text = model.generate_content(prompt_template).text.strip()
        response_type = 'general' # Ensure this is set for general conversation
    
    return jsonify({
        'response': response_text,
        'type': response_type,
        'user_name': user_name
    })

@app.route('/api/checkin', methods=['POST'])
def api_checkin():
    """Your original daily check-in function"""
    data = request.json
    user_name = data.get('user_name', 'Friend')
    session['user_name'] = user_name
    
    response = daily_checkin(user_name)
    return jsonify({'response': response})

@app.route('/api/stress', methods=['POST'])
def api_stress():
    """Your original stress management function"""
    data = request.json
    user_name = data.get('user_name', session.get('user_name', 'Friend'))
    stress_level = data.get('stress_level', 5)
    concern = data.get('concern', '')
    
    response = stress_management_suggestions(user_name, stress_level, concern)
    return jsonify({'response': response})

@app.route('/api/bedtime', methods=['POST'])
def api_bedtime():
    """Your original bedtime support function"""
    data = request.json
    user_name = data.get('user_name', session.get('user_name', 'Friend'))
    sleep_concerns = data.get('sleep_concerns', '')
    
    response = bedtime_support(user_name, sleep_concerns)
    return jsonify({'response': response})

@app.route('/api/mood', methods=['POST'])
def api_mood():
    """Your original mood tracking function"""
    data = request.json
    user_name = data.get('user_name', session.get('user_name', 'Friend'))
    mood_rating = data.get('mood_rating', 5)
    mood_description = data.get('mood_description', '')
    
    response = mood_tracking(user_name, mood_rating, mood_description)
    return jsonify({'response': response})

@app.route('/api/affirmations', methods=['POST'])
def api_affirmations():
    """Your original positive affirmations function"""
    data = request.json
    user_name = data.get('user_name', session.get('user_name', 'Friend'))
    
    response = positive_affirmations(user_name)
    return jsonify({'response': response})

@app.route('/api/emergency', methods=['POST'])
def api_emergency():
    """Your original emergency support function"""
    response = emergency_support()
    return jsonify({'response': response})

@app.route('/api/user-profile', methods=['GET'])
def get_user_profile():
    """Get current user profile"""
    user_name = session.get('user_name', 'Friend')
    if user_name in user_profiles:
        return jsonify(user_profiles[user_name])
    else:
        return jsonify(create_user_profile(user_name))

if __name__ == '__main__':
    print("🌟 AI Mental Health & Sleep Support Agent - Web Version 🌟")
    print("Starting server...")
    app.run(debug=True, host='0.0.0.0', port=5000)