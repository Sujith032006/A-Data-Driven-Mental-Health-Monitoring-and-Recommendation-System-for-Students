# Simple user management and session persistence fix
import streamlit as st
import pandas as pd
from analysis import load_data, analyze_data, save_results, plot_stress_distribution, plot_sleep_distribution, plot_recommendation_summary
from chatbot import chatbot
import os
import json
import random
import hashlib
import time

# Session persistence functions
def generate_session_token(username, password):
    """Generate a secure session token"""
    timestamp = str(time.time())
    token_data = f"{username}:{password}:{timestamp}"
    return hashlib.sha256(token_data.encode()).hexdigest()[:16]

def get_session_from_url():
    """Check for existing session in URL parameters"""
    try:
        query_params = st.query_params
        if 'user' in query_params and 'token' in query_params:
            username = query_params['user']
            token = query_params['token']
            if username in users and users[username].get('session_token') == token:
                # Check if token is not too old (24 hours)
                token_time = users[username].get('token_timestamp', 0)
                if time.time() - token_time < 86400:  # 24 hours
                    return username, users[username].get('is_admin', False), users[username].get('is_super_admin', False)
    except:
        pass
    return None, False, False

def update_session_url(username, is_admin, is_super_admin):
    token = generate_session_token(username, users[username]['password'])
    users[username]['session_token'] = token
    users[username]['token_timestamp'] = time.time()

    # Update query parameters
    try:
        st.query_params['user'] = username
        st.query_params['token'] = token
    except:
        pass

def save_session_state(username, is_admin, is_super_admin):
    """Save session state to a persistent file"""
    session_data = {
        'username': username,
        'is_admin': is_admin,
        'is_super_admin': is_super_admin,
        'timestamp': time.time()
    }
    try:
        with open(f'session_{username}.json', 'w') as f:
            json.dump(session_data, f)
    except:
        pass

def load_session_state():
    """Load session state from persistent file"""
    try:
        # Look for any session files
        import glob
        session_files = glob.glob('session_*.json')
        for session_file in session_files:
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    # Check if session is not too old (24 hours)
                    if time.time() - session_data.get('timestamp', 0) < 86400:
                        username = session_data['username']
                        if username in users:
                            return username, session_data.get('is_admin', False), session_data.get('is_super_admin', False)
    except:
        pass
    return None, False, False

def clear_session_state(username):
    """Clear session state file"""
    try:
        session_file = f'session_{username}.json'
        if os.path.exists(session_file):
            os.remove(session_file)
    except:
        pass

st.title("A Data-Driven Mental Health Monitoring and Recommendation System for Students")

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        color: #2E86AB;
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
        background: linear-gradient(45deg, #7c3aed, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2E86AB 0%, #A23B72 100%);
        color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #2a5298, #3a7bd5);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {
        border-radius: 8px;
        border: 2px solid #ddd;
        padding: 10px;
        transition: border-color 0.3s ease;
    }
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus, .stSelectbox>div>div>select:focus {
        border-color: #1e3c72;
        box-shadow: 0 0 5px rgba(30, 60, 114, 0.3);
    }
    .stSlider>div>div>div {
        background: linear-gradient(45deg, #1e3c72, #2a5298);
    }
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 8px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        color: #ffffff;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        margin: 0 2px;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: transparent;
        color: #ffffff;
        box-shadow: none;
    }
    .stSuccess, .stError, .stInfo {
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        margin-top: 10px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }
    body {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #3a7bd5 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin: 0;
        padding: 0;
        min-height: 100vh;
    }
    .chat-container { background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; margin: 10px 0; }
    .chat-message { padding: 10px 15px; margin: 5px 0; border-radius: 15px; max-width: 80%; }
    .user-message { background: linear-gradient(45deg, #1e3c72, #2a5298); color: white; margin-left: auto; }
    .bot-message { background: rgba(255, 255, 255, 0.1); color: white; margin-right: auto; }
    .chat-input { margin-top: 20px; }
    .quick-actions { display: flex; gap: 10px; margin: 10px 0; flex-wrap: wrap; }
    .quick-action-btn { background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 20px; padding: 8px 16px; color: white; text-decoration: none; font-size: 14px; transition: all 0.3s ease; }
    .quick-action-btn:hover { background: rgba(255, 255, 255, 0.2); transform: translateY(-1px); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">Mental Health Monitoring & Recommendation System</div>', unsafe_allow_html=True)

# Simple user management
if os.path.exists('users.json'):
    with open('users.json', 'r') as f:
        raw_users = json.load(f)
    users = {}
    for k, v in raw_users.items():
        if isinstance(v, str):
            users[k] = {"password": v, "is_admin": False, "security_question": "", "security_answer": "", "is_super_admin": False}
        else:
            users[k] = v
            if 'security_question' not in users[k]:
                users[k]['security_question'] = ""
            if 'security_answer' not in users[k]:
                users[k]['security_answer'] = ""
            if 'is_super_admin' not in users[k]:
                users[k]['is_super_admin'] = False
else:
    users = {"student": {"password": "pass", "is_admin": False, "security_question": "", "security_answer": "", "is_super_admin": False}, "Sujith": {"password": "Sujith@123", "is_admin": False, "is_super_admin": True, "security_question": "", "security_answer": ""}}

if 'users' not in st.session_state:
    st.session_state.users = users

# Enhanced session persistence - using session state with backup
def get_session_from_url():
    """Check for existing session in URL parameters"""
    try:
        query_params = st.query_params
        if 'user' in query_params and 'token' in query_params:
            username = query_params['user']
            token = query_params['token']
            if username in users and users[username].get('session_token') == token:
                # Check if token is not too old (24 hours)
                token_time = users[username].get('token_timestamp', 0)
                if time.time() - token_time < 86400:  # 24 hours
                    return username, users[username].get('is_admin', False), users[username].get('is_super_admin', False)
    except:
        pass
    return None, False, False

def update_session_url(username, is_admin, is_super_admin):
    """Update URL with session information"""
    token = generate_session_token(username, users[username]['password'])
    users[username]['session_token'] = token
    users[username]['token_timestamp'] = time.time()

    # Update query parameters
    try:
        st.query_params['user'] = username
        st.query_params['token'] = token
    except:
        pass

# Initialize session state with file-based persistence and URL fallback
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'current_user' not in st.session_state:
    st.session_state.current_user = ""

if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

if 'is_super_admin' not in st.session_state:
    st.session_state.is_super_admin = False

# Check for existing session from file first, then URL
file_user, file_is_admin, file_is_super_admin = load_session_state()
url_user, url_is_admin, url_is_super_admin = get_session_from_url()

# Use file session if available, otherwise use URL session
if file_user and not st.session_state.logged_in:
    st.session_state.logged_in = True
    st.session_state.current_user = file_user
    st.session_state.is_admin = file_is_admin
    st.session_state.is_super_admin = file_is_super_admin
    # Update URL for consistency
    update_session_url(file_user, file_is_admin, file_is_super_admin)
elif url_user and not st.session_state.logged_in:
    st.session_state.logged_in = True
    st.session_state.current_user = url_user
    st.session_state.is_admin = url_is_admin
    st.session_state.is_super_admin = url_is_super_admin
    # Save to file for persistence
    save_session_state(url_user, url_is_admin, url_is_super_admin)
    # Update URL to ensure persistence
    update_session_url(url_user, url_is_admin, url_is_super_admin)
elif st.session_state.current_user and st.session_state.logged_in:
    # Session exists in memory, ensure both file and URL are updated
    save_session_state(st.session_state.current_user, st.session_state.is_admin, st.session_state.is_super_admin)
    update_session_url(st.session_state.current_user, st.session_state.is_admin, st.session_state.is_super_admin)

if not st.session_state.logged_in:
    tab1, tab2, tab3, tab4 = st.tabs(["User Login", "Admin Login", "Super Admin Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.form_submit_button("Login"):
                if username in st.session_state.users and st.session_state.users[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.session_state.is_admin = st.session_state.users[username]["is_admin"]
                    st.session_state.is_super_admin = st.session_state.users[username].get("is_super_admin", False)
                    # Save session state for persistence across browser refreshes
                    save_session_state(username, st.session_state.is_admin, st.session_state.is_super_admin)
                    # Update URL with session info for additional persistence
                    update_session_url(username, st.session_state.is_admin, st.session_state.is_super_admin)
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        with st.expander("Forgot Password?"):
            forgot_user = st.text_input("Enter your username", key="forgot_username")
            if st.button("Reset Password"):
                if forgot_user in st.session_state.users:
                    if st.session_state.users[forgot_user]["security_question"]:
                        st.session_state.forgot_user = forgot_user
                        st.session_state.forgot_step = "question"
                        st.rerun()
                    else:
                        st.error("No security question set for this account. Contact admin.")
                else:
                    st.error("Username not found")
        
        if 'forgot_step' in st.session_state and st.session_state.forgot_step == "question":
            st.subheader("Security Question")
            question = st.session_state.users[st.session_state.forgot_user]["security_question"]
            st.write(question)
            answer = st.text_input("Your answer", key="forgot_answer")
            if st.button("Submit Answer"):
                if answer.lower() == st.session_state.users[st.session_state.forgot_user]["security_answer"]:
                    st.session_state.forgot_step = "new_password"
                    st.rerun()
                else:
                    st.error("Incorrect answer")
        
        if 'forgot_step' in st.session_state and st.session_state.forgot_step == "new_password":
            st.subheader("Set New Password")
            new_pass = st.text_input("New Password", type="password", key="forgot_new_pass")
            confirm_pass = st.text_input("Confirm New Password", type="password", key="forgot_confirm_pass")
            if st.button("Update Password"):
                if new_pass == confirm_pass and len(new_pass) >= 4:
                    st.session_state.users[st.session_state.forgot_user]["password"] = new_pass
                    with open('users.json', 'w') as f:
                        json.dump(st.session_state.users, f)
                    st.success("Password updated successfully!")
                    del st.session_state.forgot_step
                    del st.session_state.forgot_user
                else:
                    st.error("Passwords do not match or too short")
    
    with tab2:
        st.subheader("Admin Login")
        with st.form("admin_login_form"):
            admin_username = st.text_input("Admin Username", key="admin_login_user")
            admin_password = st.text_input("Password", type="password", key="admin_login_pass")
            if st.form_submit_button("Admin Login"):
                if admin_username in st.session_state.users and st.session_state.users[admin_username]["password"] == admin_password and st.session_state.users[admin_username].get("is_admin", False):
                    st.session_state.logged_in = True
                    st.session_state.current_user = admin_username
                    st.session_state.is_admin = True
                    st.session_state.is_super_admin = False
                    # Save session state for persistence across browser refreshes
                    save_session_state(admin_username, True, False)
                    # Update URL with session info for additional persistence
                    update_session_url(admin_username, True, False)
                    st.success("Admin login successful!")
                    st.rerun()
                else:
                    st.error("Invalid admin credentials")
    
    with tab3:
        st.subheader("Super Admin Login")
        with st.form("super_admin_login_form"):
            super_username = st.text_input("Super Admin Username", key="super_login_user")
            super_password = st.text_input("Password", type="password", key="super_login_pass")
            if st.form_submit_button("Super Admin Login"):
                if super_username in st.session_state.users and st.session_state.users[super_username]["password"] == super_password and st.session_state.users[super_username].get("is_super_admin", False):
                    st.session_state.logged_in = True
                    st.session_state.current_user = super_username
                    st.session_state.is_admin = False
                    st.session_state.is_super_admin = True
                    # Save session state for persistence across browser refreshes
                    save_session_state(super_username, False, True)
                    # Update URL with session info for additional persistence
                    update_session_url(super_username, False, True)
                    st.success("Super Admin login successful!")
                    st.rerun()
                else:
                    st.error("Invalid super admin credentials")
    
    with tab4:
        st.subheader("Create New Account")
        with st.form("register_form"):
            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Password", type="password", key="reg_new_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", key="reg_confirm_pass")
            
            # Security question with custom option
            question_options = ["What is your favorite color?", "What is your pet's name?", "What city were you born in?", "Custom Question"]
            security_question_choice = st.selectbox("Security Question", question_options)
            
            if security_question_choice == "Custom Question":
                security_question = st.text_input("Enter your custom security question", key="custom_security_question")
            else:
                security_question = security_question_choice
            
            security_answer = st.text_input("Security Answer", key="reg_security_answer")
            
            if st.form_submit_button("Register"):
                if new_user in st.session_state.users:
                    st.error("Username already exists")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match")
                elif len(new_pass) < 4:
                    st.error("Password must be at least 4 characters")
                elif security_question_choice == "Custom Question" and not security_question:
                    st.error("Please enter your custom security question")
                elif not security_answer:
                    st.error("Please provide a security answer")
                else:
                    st.session_state.users[new_user] = {"password": new_pass, "is_admin": False, "is_super_admin": False, "security_question": security_question, "security_answer": security_answer.lower()}
                    with open('users.json', 'w') as f:
                        json.dump(st.session_state.users, f)
                    st.session_state.logged_in = True
                    st.session_state.current_user = new_user
                    # Save session state for persistence across browser refreshes
                    save_session_state(new_user, False, False)
                    # Update URL with session info for additional persistence
                    update_session_url(new_user, False, False)
                    st.success("Registration successful! Welcome!")
                    st.rerun()

else:
    if st.session_state.get('is_super_admin', False):
        st.sidebar.write(f"Super Admin: {st.session_state.current_user}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            # Clear session from users data
            if st.session_state.current_user in users:
                users[st.session_state.current_user].pop('session_token', None)
                users[st.session_state.current_user].pop('token_timestamp', None)
                with open('users.json', 'w') as f:
                    json.dump(users, f)
            # Clear session state file
            clear_session_state(st.session_state.current_user)
            # Clear URL parameters
            try:
                st.query_params.clear()
            except:
                pass
            st.rerun()
        
        # Add daily mood check-in and mental health tips in sidebar
        st.sidebar.subheader("Quick Actions")
        if st.sidebar.button("📊 Daily Mood Check-in"):
            st.session_state.quick_action = "mood_check"
        if st.sidebar.button("💡 Mental Health Tips"):
            st.session_state.quick_action = "tips"
        if st.sidebar.button("🚨 Emergency Resources"):
            st.session_state.quick_action = "emergency"
        
        # Handle quick actions
        if 'quick_action' in st.session_state:
            if st.session_state.quick_action == "mood_check":
                st.subheader("📊 Daily Mood Check-in")
                mood = st.select_slider("How are you feeling today?", 
                                      options=["😢 Very Sad", "😞 Sad", "😐 Neutral", "😊 Happy", "😄 Very Happy"],
                                      value="😐 Neutral")
                if st.button("Save Mood"):
                    # Save mood to a simple log
                    mood_data = {
                        'date': pd.Timestamp.now().strftime('%Y-%m-%d'),
                        'username': st.session_state.current_user,
                        'mood': mood
                    }
                    mood_df = pd.DataFrame([mood_data])
                    mood_file = "mood_log.csv"
                    if os.path.exists(mood_file):
                        existing_mood = pd.read_csv(mood_file)
                        updated_mood = pd.concat([existing_mood, mood_df], ignore_index=True)
                    else:
                        updated_mood = mood_df
                    updated_mood.to_csv(mood_file, index=False)
                    st.success("Mood logged! Check back to see your mood trends.")
                    del st.session_state.quick_action
                    st.rerun()
            
            elif st.session_state.quick_action == "tips":
                st.subheader("💡 Daily Mental Health Tips")
                tips = [
                    "Practice deep breathing: Inhale for 4 counts, hold for 4, exhale for 4.",
                    "Take a 10-minute walk outside to boost your mood and reduce stress.",
                    "Write down three things you're grateful for each day.",
                    "Set boundaries: Learn to say 'no' to things that drain your energy.",
                    "Connect with someone: Call a friend or family member for support.",
                    "Get enough sleep: Aim for 7-9 hours per night for optimal mental health."
                ]
                st.info(random.choice(tips))
                if st.button("Get Another Tip"):
                    st.rerun()
                if st.button("Back to Menu"):
                    del st.session_state.quick_action
                    st.rerun()
            
            elif st.session_state.quick_action == "emergency":
                st.subheader("🚨 Emergency Resources")
                st.error("**If you're in crisis or having thoughts of self-harm, seek help immediately:**")
                st.write("• **National Suicide Prevention Lifeline:** Call or text 988 (24/7)")
                st.write("• **Crisis Text Line:** Text HOME to 741741")
                st.write("• **Emergency Services:** Call 911")
                st.write("• **Your campus counseling center** - most offer free services")
                st.info("Remember: Asking for help is a sign of strength, not weakness.")
                if st.button("Back to Menu"):
                    del st.session_state.quick_action
                    st.rerun()
        
        option = st.sidebar.selectbox("Super Admin Options", ["Manage Admins", "Manage Users", "View Student Responses"])
        
        if option == "View Student Responses":
            st.subheader("Student Survey Responses")
            
            # Load existing data or create empty dataframe
            if os.path.exists("student_survey_results.csv"):
                df = pd.read_csv("student_survey_results.csv")
            else:
                # Create empty dataframe with proper columns and dtypes
                df = pd.DataFrame({
                    "Username": pd.Series(dtype="string"),
                    "Name": pd.Series(dtype="string"),
                    "Age": pd.Series(dtype="int64"),
                    "Stress_Level": pd.Series(dtype="int64"),
                    "Sleep_Hours": pd.Series(dtype="float64"),
                    "Exercise_Hours": pd.Series(dtype="float64"),
                    "Academic_Workload": pd.Series(dtype="int64"),
                    "Anxiety_Level": pd.Series(dtype="int64"),
                    "Social_Support": pd.Series(dtype="int64"),
                    "Depression_Level": pd.Series(dtype="int64"),
                    "Financial_Stress": pd.Series(dtype="int64"),
                    "Relationship_Stress": pd.Series(dtype="int64"),
                    "Coping_Frequency": pd.Series(dtype="int64"),
                    "Screen_Time": pd.Series(dtype="int64"),
                    "Nutrition_Quality": pd.Series(dtype="int64"),
                    "Self_Esteem": pd.Series(dtype="int64"),
                    "Work_Life_Balance": pd.Series(dtype="int64"),
                    "Future_Optimism": pd.Series(dtype="int64"),
                    "Recommendation": pd.Series(dtype="string")
                })
            
            # Select relevant columns for display
            display_cols = ['Username', 'Name', 'Age', 'Stress_Level', 'Sleep_Hours', 'Exercise_Hours', 'Recommendation']
            # Include model risk if available
            if 'Risk_Probability' in df.columns:
                display_cols.insert(6, 'Risk_Probability')
            if 'Academic_Workload' in df.columns:
                display_cols.extend(['Academic_Workload', 'Anxiety_Level', 'Depression_Level', 'Social_Support'])
            
            if not df.empty:
                st.dataframe(df[display_cols])
            else:
                st.info("No student responses available yet. You can add new responses below.")
            
            st.subheader("Edit/Add Responses")
            st.info("You can edit existing responses or add new ones directly in the table below. Click 'Save Changes' to update the data.")
            
            # Create editable dataframe (always show, even if empty)
            edited_df = st.data_editor(
                df,
                column_config={
                    "Username": st.column_config.TextColumn("Username", width="medium"),
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "Age": st.column_config.NumberColumn("Age", min_value=10, max_value=100),
                    "Stress_Level": st.column_config.NumberColumn("Stress Level", min_value=1, max_value=10),
                    "Sleep_Hours": st.column_config.NumberColumn("Sleep Hours", min_value=0.0, max_value=24.0),
                    "Exercise_Hours": st.column_config.NumberColumn("Exercise Hours", min_value=0.0, max_value=168.0),
                    "Academic_Workload": st.column_config.NumberColumn("Academic Workload", min_value=1, max_value=10),
                    "Anxiety_Level": st.column_config.NumberColumn("Anxiety Level", min_value=1, max_value=10),
                    "Depression_Level": st.column_config.NumberColumn("Depression Level", min_value=1, max_value=10),
                    "Social_Support": st.column_config.NumberColumn("Social Support", min_value=1, max_value=10),
                    "Financial_Stress": st.column_config.NumberColumn("Financial Stress", min_value=1, max_value=10),
                    "Relationship_Stress": st.column_config.NumberColumn("Relationship Stress", min_value=1, max_value=10),
                    "Coping_Frequency": st.column_config.NumberColumn("Coping Frequency", min_value=1, max_value=10),
                    "Screen_Time": st.column_config.NumberColumn("Screen Time", min_value=1, max_value=10),
                    "Nutrition_Quality": st.column_config.NumberColumn("Nutrition Quality", min_value=1, max_value=10),
                    "Self_Esteem": st.column_config.NumberColumn("Self Esteem", min_value=1, max_value=10),
                    "Work_Life_Balance": st.column_config.NumberColumn("Work Life Balance", min_value=1, max_value=10),
                    "Future_Optimism": st.column_config.NumberColumn("Future Optimism", min_value=1, max_value=10),
                    "Recommendation": st.column_config.TextColumn("Recommendation", width="large"),
                },
                hide_index=True,
                use_container_width=True,
                num_rows="dynamic"  # Allow adding new rows
            )
            
            if st.button("Save Changes", type="primary"):
                try:
                    # Remove empty rows before saving
                    edited_df = edited_df.dropna(how='all')
                    edited_df.to_csv("student_survey_results.csv", index=False)
                    st.success("Changes saved successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving changes: {str(e)}")
            
            # Download options
            if not df.empty:
                st.subheader("Download Data")
                col1, col2 = st.columns(2)
                with col1:
                    csv_data = df.to_csv(index=False)
                    st.download_button("Download as CSV", csv_data, file_name="student_responses.csv", mime="text/csv")
                with col2:
                    # For Excel, need to use BytesIO
                    from io import BytesIO
                    buffer = BytesIO()
                    df.to_excel(buffer, index=False, engine='openpyxl')
                    buffer.seek(0)
                    st.download_button("Download as Excel", buffer, file_name="student_responses.xlsx", mime="application/vnd.openpyxlformats-officedocument.spreadsheetml.sheet")
            else:
                st.info("Add some responses above to enable download options.")
        
        elif option == "Manage Admins":
            st.subheader("Admin User Management")
            
            # List all admin users
            admin_users = {k: v for k, v in st.session_state.users.items() if v.get('is_admin', False)}
            if admin_users:
                st.write("Current Admin Users:")
                for username, data in admin_users.items():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"{username}")
                    with col2:
                        if st.button(f"Edit {username}", key=f"edit_{username}"):
                            st.session_state.edit_admin = username
                            st.rerun()
                    with col3:
                        if st.button(f"Delete {username}", key=f"delete_{username}"):
                            # Remove admin status
                            st.session_state.users[username]['is_admin'] = False
                            with open('users.json', 'w') as f:
                                json.dump(st.session_state.users, f)
                            st.success(f"Admin privileges removed from '{username}'")
                            st.rerun()
            else:
                st.info("No admin users found.")
            
            # Edit admin section
            if 'edit_admin' in st.session_state and st.session_state.edit_admin in st.session_state.users:
                edit_user = st.session_state.edit_admin
                st.subheader(f"Edit Admin: {edit_user}")
                
                new_password = st.text_input("New Password", type="password", key="edit_admin_pass")
                confirm_password = st.text_input("Confirm New Password", type="password", key="edit_admin_confirm")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update Password"):
                        if new_password == confirm_password and len(new_password) >= 4:
                            st.session_state.users[edit_user]['password'] = new_password
                            with open('users.json', 'w') as f:
                                json.dump(st.session_state.users, f)
                            st.success(f"Password updated for '{edit_user}'")
                            del st.session_state.edit_admin
                            st.rerun()
                        else:
                            st.error("Passwords do not match or too short")
                
                with col2:
                    if st.button("Cancel Edit"):
                        del st.session_state.edit_admin
                        st.rerun()
            
            # Add new admin
            st.subheader("Add New Admin")
            new_admin_user = st.text_input("New Admin Username", key="new_admin_user")
            new_admin_pass = st.text_input("New Admin Password", type="password", key="new_admin_pass")
            if st.button("Create Admin"):
                if new_admin_user in st.session_state.users:
                    st.error("Username already exists")
                elif len(new_admin_pass) < 4:
                    st.error("Password must be at least 4 characters")
                else:
                    st.session_state.users[new_admin_user] = {"password": new_admin_pass, "is_admin": True, "is_super_admin": False, "security_question": "", "security_answer": ""}
                    with open('users.json', 'w') as f:
                        json.dump(st.session_state.users, f)
                    st.success(f"Admin user '{new_admin_user}' created successfully!")
        
        elif option == "Manage Users":
            st.subheader("User Management")
            
            # List all regular users (not admins or super admins)
            regular_users = {k: v for k, v in st.session_state.users.items() if not v.get('is_admin', False) and not v.get('is_super_admin', False)}
            
            if regular_users:
                st.write("Current Users:")
                for username, data in regular_users.items():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"{username}")
                    with col2:
                        if st.button(f"Remove {username}", key=f"remove_user_{username}"):
                            del st.session_state.users[username]
                            with open('users.json', 'w') as f:
                                json.dump(st.session_state.users, f)
                            st.success(f"User '{username}' removed successfully!")
                            st.rerun()
            else:
                st.info("No regular users found.")
            
            # Add new user
            st.subheader("Add New User")
            new_username = st.text_input("New Username", key="new_user_username")
            new_user_pass = st.text_input("New Password", type="password", key="new_user_pass")
            if st.button("Create User"):
                if new_username in st.session_state.users:
                    st.error("Username already exists")
                elif len(new_user_pass) < 4:
                    st.error("Password must be at least 4 characters")
                else:
                    st.session_state.users[new_username] = {"password": new_user_pass, "is_admin": False, "is_super_admin": False, "security_question": "", "security_answer": ""}
                    with open('users.json', 'w') as f:
                        json.dump(st.session_state.users, f)
                    st.success(f"User '{new_username}' created successfully!")
        
    elif st.session_state.get('is_admin', False):
        st.sidebar.write(f"Admin: {st.session_state.current_user}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            # Clear session from users data
            if st.session_state.current_user in users:
                users[st.session_state.current_user].pop('session_token', None)
                users[st.session_state.current_user].pop('token_timestamp', None)
                with open('users.json', 'w') as f:
                    json.dump(users, f)
            # Clear session state file
            clear_session_state(st.session_state.current_user)
            # Clear URL parameters
            try:
                st.query_params.clear()
            except:
                pass
            st.rerun()
        
        # Add daily mood check-in and mental health tips in sidebar
        st.sidebar.subheader("Quick Actions")
        if st.sidebar.button("📊 Daily Mood Check-in"):
            st.session_state.quick_action = "mood_check"
        if st.sidebar.button("💡 Mental Health Tips"):
            st.session_state.quick_action = "tips"
        if st.sidebar.button("🚨 Emergency Resources"):
            st.session_state.quick_action = "emergency"
        
        # Handle quick actions
        if 'quick_action' in st.session_state:
            if st.session_state.quick_action == "mood_check":
                st.subheader("📊 Daily Mood Check-in")
                mood = st.select_slider("How are you feeling today?", 
                                      options=["😢 Very Sad", "😞 Sad", "😐 Neutral", "😊 Happy", "😄 Very Happy"],
                                      value="😐 Neutral")
                if st.button("Save Mood"):
                    # Save mood to a simple log
                    mood_data = {
                        'date': pd.Timestamp.now().strftime('%Y-%m-%d'),
                        'username': st.session_state.current_user,
                        'mood': mood
                    }
                    mood_df = pd.DataFrame([mood_data])
                    mood_file = "mood_log.csv"
                    if os.path.exists(mood_file):
                        existing_mood = pd.read_csv(mood_file)
                        updated_mood = pd.concat([existing_mood, mood_df], ignore_index=True)
                    else:
                        updated_mood = mood_df
                    updated_mood.to_csv(mood_file, index=False)
                    st.success("Mood logged! Check back to see your mood trends.")
                    del st.session_state.quick_action
                    st.rerun()
            
            elif st.session_state.quick_action == "tips":
                st.subheader("💡 Daily Mental Health Tips")
                tips = [
                    "Practice deep breathing: Inhale for 4 counts, hold for 4, exhale for 4.",
                    "Take a 10-minute walk outside to boost your mood and reduce stress.",
                    "Write down three things you're grateful for each day.",
                    "Set boundaries: Learn to say 'no' to things that drain your energy.",
                    "Connect with someone: Call a friend or family member for support.",
                    "Get enough sleep: Aim for 7-9 hours per night for optimal mental health."
                ]
                st.info(random.choice(tips))
                if st.button("Get Another Tip"):
                    st.rerun()
                if st.button("Back to Menu"):
                    del st.session_state.quick_action
                    st.rerun()
            
            elif st.session_state.quick_action == "emergency":
                st.subheader("🚨 Emergency Resources")
                st.error("**If you're in crisis or having thoughts of self-harm, seek help immediately:**")
                st.write("• **National Suicide Prevention Lifeline:** Call or text 988 (24/7)")
                st.write("• **Crisis Text Line:** Text HOME to 741741")
                st.write("• **Emergency Services:** Call 911")
                st.write("• **Your campus counseling center** - most offer free services")
                st.info("Remember: Asking for help is a sign of strength, not weakness.")
                if st.button("Back to Menu"):
                    del st.session_state.quick_action
                    st.rerun()
        
        option = st.sidebar.selectbox("Admin Options", ["View Student Responses"])
        
        if option == "View Student Responses":
            st.subheader("Student Survey Responses")
            
            # Load existing data or create empty dataframe
            if os.path.exists("student_survey_results.csv"):
                df = pd.read_csv("student_survey_results.csv")
                # Ensure Name column is string type for data_editor compatibility
                if 'Name' in df.columns:
                    df['Name'] = df['Name'].astype(str)
            else:
                # Create empty dataframe with proper columns and dtypes
                df = pd.DataFrame({
                    "Username": pd.Series(dtype="string"),
                    "Name": pd.Series(dtype="string"),
                    "Age": pd.Series(dtype="int64"),
                    "Stress_Level": pd.Series(dtype="int64"),
                    "Sleep_Hours": pd.Series(dtype="float64"),
                    "Exercise_Hours": pd.Series(dtype="float64"),
                    "Academic_Workload": pd.Series(dtype="int64"),
                    "Anxiety_Level": pd.Series(dtype="int64"),
                    "Social_Support": pd.Series(dtype="int64"),
                    "Depression_Level": pd.Series(dtype="int64"),
                    "Financial_Stress": pd.Series(dtype="int64"),
                    "Relationship_Stress": pd.Series(dtype="int64"),
                    "Coping_Frequency": pd.Series(dtype="int64"),
                    "Screen_Time": pd.Series(dtype="int64"),
                    "Nutrition_Quality": pd.Series(dtype="int64"),
                    "Self_Esteem": pd.Series(dtype="int64"),
                    "Work_Life_Balance": pd.Series(dtype="int64"),
                    "Future_Optimism": pd.Series(dtype="int64"),
                    "Recommendation": pd.Series(dtype="string")
                })
            
            # Select relevant columns for display
            display_cols = ['Username', 'Name', 'Age', 'Stress_Level', 'Sleep_Hours', 'Exercise_Hours', 'Recommendation']
            # Include model risk if available
            if 'Risk_Probability' in df.columns:
                display_cols.insert(6, 'Risk_Probability')
            if 'Academic_Workload' in df.columns:
                display_cols.extend(['Academic_Workload', 'Anxiety_Level', 'Depression_Level', 'Social_Support'])
            
            if not df.empty:
                st.dataframe(df[display_cols])
            else:
                st.info("No student responses available yet. You can add new responses below.")
            
            st.subheader("Edit/Add Responses")
            st.info("You can edit existing responses or add new ones directly in the table below. Click 'Save Changes' to update the data.")
            
            # Create editable dataframe (always show, even if empty)
            edited_df = st.data_editor(
                df,
                column_config={
                    "Username": st.column_config.TextColumn("Username", width="medium"),
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "Age": st.column_config.NumberColumn("Age", min_value=10, max_value=100),
                    "Stress_Level": st.column_config.NumberColumn("Stress Level", min_value=1, max_value=10),
                    "Sleep_Hours": st.column_config.NumberColumn("Sleep Hours", min_value=0.0, max_value=24.0),
                    "Exercise_Hours": st.column_config.NumberColumn("Exercise Hours", min_value=0.0, max_value=168.0),
                    "Academic_Workload": st.column_config.NumberColumn("Academic Workload", min_value=1, max_value=10),
                    "Anxiety_Level": st.column_config.NumberColumn("Anxiety Level", min_value=1, max_value=10),
                    "Depression_Level": st.column_config.NumberColumn("Depression Level", min_value=1, max_value=10),
                    "Social_Support": st.column_config.NumberColumn("Social Support", min_value=1, max_value=10),
                    "Financial_Stress": st.column_config.NumberColumn("Financial Stress", min_value=1, max_value=10),
                    "Relationship_Stress": st.column_config.NumberColumn("Relationship Stress", min_value=1, max_value=10),
                    "Coping_Frequency": st.column_config.NumberColumn("Coping Frequency", min_value=1, max_value=10),
                    "Screen_Time": st.column_config.NumberColumn("Screen Time", min_value=1, max_value=10),
                    "Nutrition_Quality": st.column_config.NumberColumn("Nutrition Quality", min_value=1, max_value=10),
                    "Self_Esteem": st.column_config.NumberColumn("Self Esteem", min_value=1, max_value=10),
                    "Work_Life_Balance": st.column_config.NumberColumn("Work Life Balance", min_value=1, max_value=10),
                    "Future_Optimism": st.column_config.NumberColumn("Future Optimism", min_value=1, max_value=10),
                    "Recommendation": st.column_config.TextColumn("Recommendation", width="large"),
                },
                hide_index=True,
                use_container_width=True,
                num_rows="dynamic"  # Allow adding new rows
            )
            
            if st.button("Save Changes", type="primary"):
                try:
                    # Remove empty rows before saving
                    edited_df = edited_df.dropna(how='all')
                    edited_df.to_csv("student_survey_results.csv", index=False)
                    st.success("Changes saved successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving changes: {str(e)}")
            
            # Download options
            if not df.empty:
                st.subheader("Download Data")
                col1, col2 = st.columns(2)
                with col1:
                    csv_data = df.to_csv(index=False)
                    st.download_button("Download as CSV", csv_data, file_name="student_responses.csv", mime="text/csv")
                with col2:
                    # For Excel, need to use BytesIO
                    from io import BytesIO
                    buffer = BytesIO()
                    df.to_excel(buffer, index=False, engine='openpyxl')
                    buffer.seek(0)
                    st.download_button("Download as Excel", buffer, file_name="student_responses.xlsx", mime="application/vnd.openpyxlformats-officedocument.spreadsheetml.sheet")
            else:
                st.info("Add some responses above to enable download options.")
    else:
        st.sidebar.write(f"Welcome, {st.session_state.current_user}!")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            # Clear session from users data
            if st.session_state.current_user in users:
                users[st.session_state.current_user].pop('session_token', None)
                users[st.session_state.current_user].pop('token_timestamp', None)
                with open('users.json', 'w') as f:
                    json.dump(users, f)
            # Clear session state file
            clear_session_state(st.session_state.current_user)
            # Clear URL parameters
            try:
                st.query_params.clear()
            except:
                pass
            st.rerun()
        
        # Add daily mood check-in and mental health tips in sidebar
        st.sidebar.subheader("Quick Actions")
        if st.sidebar.button("📊 Daily Mood Check-in"):
            st.session_state.quick_action = "mood_check"
        if st.sidebar.button("💡 Mental Health Tips"):
            st.session_state.quick_action = "tips"
        if st.sidebar.button("🚨 Emergency Resources"):
            st.session_state.quick_action = "emergency"
        
        # Handle quick actions
        if 'quick_action' in st.session_state:
            if st.session_state.quick_action == "mood_check":
                st.subheader("📊 Daily Mood Check-in")
                mood = st.select_slider("How are you feeling today?", 
                                      options=["😢 Very Sad", "😞 Sad", "😐 Neutral", "😊 Happy", "😄 Very Happy"],
                                      value="😐 Neutral")
                if st.button("Save Mood"):
                    # Save mood to a simple log
                    mood_data = {
                        'date': pd.Timestamp.now().strftime('%Y-%m-%d'),
                        'username': st.session_state.current_user,
                        'mood': mood
                    }
                    mood_df = pd.DataFrame([mood_data])
                    mood_file = "mood_log.csv"
                    if os.path.exists(mood_file):
                        existing_mood = pd.read_csv(mood_file)
                        updated_mood = pd.concat([existing_mood, mood_df], ignore_index=True)
                    else:
                        updated_mood = mood_df
                    updated_mood.to_csv(mood_file, index=False)
                    st.success("Mood logged! Check back to see your mood trends.")
                    del st.session_state.quick_action
                    st.rerun()
            
            elif st.session_state.quick_action == "tips":
                st.subheader("💡 Daily Mental Health Tips")
                tips = [
                    "Practice deep breathing: Inhale for 4 counts, hold for 4, exhale for 4.",
                    "Take a 10-minute walk outside to boost your mood and reduce stress.",
                    "Write down three things you're grateful for each day.",
                    "Set boundaries: Learn to say 'no' to things that drain your energy.",
                    "Connect with someone: Call a friend or family member for support.",
                    "Get enough sleep: Aim for 7-9 hours per night for optimal mental health."
                ]
                st.info(random.choice(tips))
                if st.button("Get Another Tip"):
                    st.rerun()
                if st.button("Back to Menu"):
                    del st.session_state.quick_action
                    st.rerun()
            
            elif st.session_state.quick_action == "emergency":
                st.subheader("🚨 Emergency Resources")
                st.error("**If you're in crisis or having thoughts of self-harm, seek help immediately:**")
                st.write("• **National Suicide Prevention Lifeline:** Call or text 988 (24/7)")
                st.write("• **Crisis Text Line:** Text HOME to 741741")
                st.write("• **Emergency Services:** Call 911")
                st.write("• **Your campus counseling center** - most offer free services")
                st.info("Remember: Asking for help is a sign of strength, not weakness.")
                if st.button("Back to Menu"):
                    del st.session_state.quick_action
                    st.rerun()
        
        option = st.sidebar.selectbox("Choose Feature", ["Upload CSV for Batch Analysis", "Take Individual Survey", "Chat with Mental Health Assistant"])
        
        if option == "Upload CSV for Batch Analysis":
            st.subheader("Batch Analysis")
            uploaded_file = st.file_uploader("Upload student_survey.csv", type="csv")
            if uploaded_file is not None:
                df = pd.read_csv(uploaded_file)
                st.write("Uploaded Data:")
                st.dataframe(df)
                if st.button("Analyze Data"):
                    analyzed_df = analyze_data(df)
                    st.write("Analyzed Results:")
                    st.dataframe(analyzed_df)
                    # Save results
                    output_path = "student_survey_results.csv"
                    save_results(analyzed_df, output_path)
                    # Generate charts
                    plot_stress_distribution(analyzed_df, "stress_distribution.png")
                    plot_sleep_distribution(analyzed_df, "sleep_distribution.png")
                    plot_recommendation_summary(analyzed_df, "recommendations_summary.png")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.image("stress_distribution.png", caption="Stress Distribution")
                    with col2:
                        st.image("sleep_distribution.png", caption="Sleep Distribution")
                    with col3:
                        st.image("recommendations_summary.png", caption="Recommendations")
                    with open(output_path, "rb") as f:
                        st.download_button("Download Results CSV", f, file_name=output_path)
        
        elif option == "Take Individual Survey":
            st.subheader("Personal Wellness Survey")
            age = st.number_input("Age", min_value=10, max_value=100, value=20)
            
            col1, col2 = st.columns(2)
            with col1:
                stress = st.slider("General Stress Level (1-10)", 1, 10, 5, help="Rate your overall stress from daily life pressures")
                academic_workload = st.slider("Academic Workload (1-10)", 1, 10, 5, help="How demanding is your academic workload?")
                anxiety = st.slider("Anxiety Level (1-10)", 1, 10, 5, help="How often do you feel anxious or worried?")
                depression = st.slider("Depression Level (1-10)", 1, 10, 5, help="How frequently do you feel sad or low?")
                social_support = st.slider("Social Support (1-10)", 1, 10, 5, help="How much support do you receive from friends/family?")
                self_esteem = st.slider("Self-Esteem Level (1-10)", 1, 10, 5, help="How confident and positive do you feel about yourself?")
                work_life_balance = st.slider("Work-Life Balance (1-10)", 1, 10, 5, help="How well do you balance academic/work with personal life?")
            with col2:
                financial_stress = st.slider("Financial Stress (1-10)", 1, 10, 5, help="How stressed are you about money/finances?")
                relationship_stress = st.slider("Relationship Stress (1-10)", 1, 10, 5, help="How much stress from personal relationships?")
                coping_frequency = st.slider("Healthy Coping Frequency (1-10)", 1, 10, 5, help="How often do you use healthy coping strategies?")
                future_optimism = st.slider("Future Optimism (1-10)", 1, 10, 5, help="How hopeful are you about your future?")
                screen_time = st.slider("Daily Screen Time (1-10 scale)", 1, 10, 5, help="Rate your daily screen time: 1=minimal, 10=excessive")
                nutrition = st.slider("Nutrition Quality (1-10)", 1, 10, 5, help="How healthy is your diet?")
            
            sleep = st.number_input("Average Sleep Hours per night", min_value=0.0, max_value=24.0, value=7.0)
            exercise = st.number_input("Weekly Exercise Hours", min_value=0.0, max_value=168.0, value=2.0)
            
            if st.button("Get My Recommendation"):
                df = pd.DataFrame([{
                    "Username": st.session_state.current_user,
                    "Age": age,
                    "Stress_Level": stress, "Sleep_Hours": sleep, "Exercise_Hours": exercise,
                    "Academic_Workload": academic_workload, "Anxiety_Level": anxiety, "Social_Support": social_support,
                    "Depression_Level": depression, "Financial_Stress": financial_stress, "Relationship_Stress": relationship_stress,
                    "Coping_Frequency": coping_frequency, "Screen_Time": screen_time, "Nutrition_Quality": nutrition,
                    "Self_Esteem": self_esteem, "Work_Life_Balance": work_life_balance, "Future_Optimism": future_optimism
                }])
                analyzed_df = analyze_data(df)
                # Show model risk if computed
                if 'Risk_Probability' in analyzed_df.columns:
                    risk = float(analyzed_df.iloc[0]['Risk_Probability'])
                    st.metric(label="Estimated Risk (Logistic Regression)", value=f"{risk*100:.1f}%")
                recommendation = analyzed_df.iloc[0]['Recommendation']
                st.success(f"**{recommendation}**")
                # Append to results csv
                if os.path.exists("student_survey_results.csv"):
                    existing_df = pd.read_csv("student_survey_results.csv")
                    updated_df = pd.concat([existing_df, analyzed_df], ignore_index=True)
                else:
                    updated_df = analyzed_df
                save_results(updated_df, "student_survey_results.csv")
                st.info("Your response has been saved.")

        elif option == "Chat with Mental Health Assistant":
            st.subheader("🤖 Sujixh - Your Mental Health Companion")
            st.write("Hi! I'm Sujixh, your AI mental health companion. I'm here to listen, understand, and support you. Feel free to share how you're feeling or ask me anything!")

            # Initialize chat history in session state
            if 'chat_messages' not in st.session_state:
                st.session_state.chat_messages = []

            # Get user's recent survey data for context
            user_data = None
            if os.path.exists("student_survey_results.csv"):
                try:
                    survey_df = pd.read_csv("student_survey_results.csv")
                    user_surveys = survey_df[survey_df['Username'] == st.session_state.current_user]
                    if not user_surveys.empty:
                        user_data = user_surveys.iloc[-1].to_dict()
                except:
                    pass

            # Chat container
            chat_container = st.container()
            with chat_container:
                st.markdown('<div class="chat-container">', unsafe_allow_html=True)

                # Display chat history
                for message in st.session_state.chat_messages:
                    if message['role'] == 'user':
                        st.markdown(f'<div class="chat-message user-message">{message["content"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-message bot-message">{message["content"]}</div>', unsafe_allow_html=True)

                        # Show suggestions if available
                        if 'suggestions' in message and message['suggestions']:
                            with st.expander("💡 Coping Strategies"):
                                for suggestion in message['suggestions']:
                                    st.write(f"• {suggestion}")

                        # Show resources if available
                        if 'resources' in message and message['resources']:
                            with st.expander("📚 Resources"):
                                for resource in message['resources']:
                                    st.write(f"• {resource}")

                        # Show emotional validation if available
                        if 'emotional_validation' in message and message['emotional_validation']:
                            st.info(f"🤝 {message['emotional_validation']}")

                        # Show action items if available
                        if 'action_items' in message and message['action_items']:
                            with st.expander("📋 Action Items"):
                                for action in message['action_items']:
                                    st.write(f"• {action}")

                st.markdown('</div>', unsafe_allow_html=True)

            # Quick action buttons for common interactions
            st.markdown('<div class="quick-actions">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("😊 I'm feeling good", key="mood_good"):
                    response = chatbot.get_response("I'm feeling good today", user_data, st.session_state.current_user, [msg['content'] for msg in st.session_state.chat_messages if msg['role'] == 'user'])
                    st.session_state.chat_messages.append({'role': 'user', 'content': "I'm feeling good today"})
                    st.session_state.chat_messages.append({'role': 'bot', 'content': response['message'], 'suggestions': response.get('suggestions', []), 'resources': response.get('resources', []), 'emotional_validation': response.get('emotional_validation', ''), 'action_items': response.get('action_items', [])})
                    st.rerun()

            with col2:
                if st.button("😰 I'm stressed", key="mood_stressed"):
                    response = chatbot.get_response("I'm feeling stressed", user_data, st.session_state.current_user, [msg['content'] for msg in st.session_state.chat_messages if msg['role'] == 'user'])
                    st.session_state.chat_messages.append({'role': 'user', 'content': "I'm feeling stressed"})
                    st.session_state.chat_messages.append({'role': 'bot', 'content': response['message'], 'suggestions': response.get('suggestions', []), 'resources': response.get('resources', []), 'emotional_validation': response.get('emotional_validation', ''), 'action_items': response.get('action_items', [])})
                    st.rerun()

            with col3:
                if st.button("😟 I need help", key="need_help"):
                    response = chatbot.get_response("I need help with my mental health", user_data, st.session_state.current_user, [msg['content'] for msg in st.session_state.chat_messages if msg['role'] == 'user'])
                    st.session_state.chat_messages.append({'role': 'user', 'content': "I need help with my mental health"})
                    st.session_state.chat_messages.append({'role': 'bot', 'content': response['message'], 'suggestions': response.get('suggestions', []), 'resources': response.get('resources', []), 'emotional_validation': response.get('emotional_validation', ''), 'action_items': response.get('action_items', [])})
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

            # Show conversation insights if available
            insights = chatbot.get_user_insights(st.session_state.current_user)
            if insights and insights['total_conversations'] > 5:
                with st.expander("🧠 Conversation Insights"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Conversations", insights['total_conversations'])
                        st.write(f"**Most Common Topic:** {insights['most_common_intent'].title()}")
                    with col2:
                        st.metric("Overall Mood Trend", insights['overall_sentiment'].title())
                        if insights['recent_trends']:
                            st.write(f"**Recent Focus:** {insights['recent_trends'][0][0].title()}")

            # Chat input
            user_input = st.chat_input("How are you feeling? Or ask me anything about mental health...")
            if user_input:
                response = chatbot.get_response(user_input, user_data, st.session_state.current_user, [msg['content'] for msg in st.session_state.chat_messages if msg['role'] == 'user'])
                chatbot.save_conversation(st.session_state.current_user, user_input, response)
                st.session_state.chat_messages.append({'role': 'user', 'content': user_input})
                st.session_state.chat_messages.append({'role': 'bot', 'content': response['message'], 'suggestions': response.get('suggestions', []), 'resources': response.get('resources', []), 'emotional_validation': response.get('emotional_validation', ''), 'action_items': response.get('action_items', [])})
                st.rerun()

            # Clear chat button
            if st.button("Clear Chat History"):
                st.session_state.chat_messages = []
                st.rerun()
