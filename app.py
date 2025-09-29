import streamlit as st
import pandas as pd
from analysis import load_data, analyze_data, save_results, plot_stress_distribution, plot_sleep_distribution, plot_recommendation_summary
import os
import json

st.title("A Data-Driven Mental Health Monitoring and Recommendation System for Students")

st.set_page_config(page_title="Mental Health Monitoring System", page_icon="🧠", layout="wide")

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
        animation: fadeIn 2s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .stButton>button {
        background: linear-gradient(45deg, #1e3c72, #2a5298);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease;
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
        background: linear-gradient(45deg, #1e3c72, #2a5298);
        color: #ffffff;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2E86AB 0%, #A23B72 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🧠 Mental Health Monitoring & Recommendation System</div>', unsafe_allow_html=True)

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

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    tab1, tab2, tab3, tab4 = st.tabs(["👤 User Login", "👑 Admin Login", "🎯 Super Admin Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.session_state.is_admin = st.session_state.users[username]["is_admin"]
                st.session_state.is_super_admin = st.session_state.users[username].get("is_super_admin", False)
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
        admin_username = st.text_input("Admin Username", key="admin_login_user")
        admin_password = st.text_input("Password", type="password", key="admin_login_pass")
        if st.button("Admin Login"):
            if admin_username in st.session_state.users and st.session_state.users[admin_username]["password"] == admin_password and st.session_state.users[admin_username].get("is_admin", False):
                st.session_state.logged_in = True
                st.session_state.current_user = admin_username
                st.session_state.is_admin = True
                st.session_state.is_super_admin = False
                st.success("Admin login successful!")
                st.rerun()
            else:
                st.error("Invalid admin credentials")
    
    with tab3:
        st.subheader("Super Admin Login")
        super_username = st.text_input("Super Admin Username", key="super_login_user")
        super_password = st.text_input("Password", type="password", key="super_login_pass")
        if st.button("Super Admin Login"):
            if super_username in st.session_state.users and st.session_state.users[super_username]["password"] == super_password and st.session_state.users[super_username].get("is_super_admin", False):
                st.session_state.logged_in = True
                st.session_state.current_user = super_username
                st.session_state.is_admin = False
                st.session_state.is_super_admin = True
                st.success("Super Admin login successful!")
                st.rerun()
            else:
                st.error("Invalid super admin credentials")
    
    with tab4:
        st.subheader("Create New Account")
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password", key="reg_new_pass")
        confirm_pass = st.text_input("Confirm Password", type="password", key="reg_confirm_pass")
        security_question = st.selectbox("Security Question", ["What is your favorite color?", "What is your pet's name?", "What city were you born in?"])
        security_answer = st.text_input("Security Answer", key="reg_security_answer")
        is_admin = st.checkbox("Register as Admin")
        if st.button("Register"):
            if new_user in st.session_state.users:
                st.error("Username already exists")
            elif new_pass != confirm_pass:
                st.error("Passwords do not match")
            elif len(new_pass) < 4:
                st.error("Password must be at least 4 characters")
            else:
                st.session_state.users[new_user] = {"password": new_pass, "is_admin": is_admin, "is_super_admin": False, "security_question": security_question, "security_answer": security_answer.lower()}
                with open('users.json', 'w') as f:
                    json.dump(st.session_state.users, f)
                st.session_state.logged_in = True
                st.session_state.current_user = new_user
                st.success("Registration successful! Welcome!")
                st.rerun()

else:
    if st.session_state.get('is_super_admin', False):
        st.sidebar.write(f"👑 Super Admin: {st.session_state.current_user}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
        
        option = st.sidebar.selectbox("Super Admin Options", ["👥 Manage Admins"])
        
        if option == "👥 Manage Admins":
            st.subheader("Admin User Management")
            
            # List all admin users
            admin_users = {k: v for k, v in st.session_state.users.items() if v.get('is_admin', False)}
            if admin_users:
                st.write("Current Admin Users:")
                for username, data in admin_users.items():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"👑 {username}")
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
        
    elif st.session_state.get('is_admin', False):
        st.sidebar.write(f"👑 Admin: {st.session_state.current_user}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
        
        option = st.sidebar.selectbox("Admin Options", ["📊 View Student Responses"])
        
        if option == "📊 View Student Responses":
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
            if 'Academic_Workload' in df.columns:
                display_cols.extend(['Academic_Workload', 'Anxiety_Level', 'Depression_Level', 'Social_Support'])
            
            if not df.empty:
                st.dataframe(df[display_cols])
            else:
                st.info("No student responses available yet. You can add new responses below.")
            
            st.subheader("Edit/Add Responses")
            st.info("📝 You can edit existing responses or add new ones directly in the table below. Click 'Save Changes' to update the data.")
            
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
            
            if st.button("💾 Save Changes", type="primary"):
                try:
                    # Remove empty rows before saving
                    edited_df = edited_df.dropna(how='all')
                    edited_df.to_csv("student_survey_results.csv", index=False)
                    st.success("✅ Changes saved successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error saving changes: {str(e)}")
            
            # Download options
            if not df.empty:
                st.subheader("Download Data")
                col1, col2 = st.columns(2)
                with col1:
                    csv_data = df.to_csv(index=False)
                    st.download_button("📥 Download as CSV", csv_data, file_name="student_responses.csv", mime="text/csv")
                with col2:
                    # For Excel, need to use BytesIO
                    from io import BytesIO
                    buffer = BytesIO()
                    df.to_excel(buffer, index=False, engine='openpyxl')
                    buffer.seek(0)
                    st.download_button("📊 Download as Excel", buffer, file_name="student_responses.xlsx", mime="application/vnd.openpyxlformats-officedocument.spreadsheetml.sheet")
            else:
                st.info("Add some responses above to enable download options.")
    else:
        st.sidebar.write(f"👤 Welcome, {st.session_state.current_user}!")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
        
        option = st.sidebar.selectbox("Choose Feature", ["📊 Upload CSV for Batch Analysis", "📝 Take Individual Survey"])
        
        if option == "📊 Upload CSV for Batch Analysis":
            st.subheader("Batch Analysis")
            uploaded_file = st.file_uploader("Upload student_survey.csv", type="csv")
            if uploaded_file is not None:
                df = pd.read_csv(uploaded_file)
                st.write("📋 Uploaded Data:")
                st.dataframe(df)
                if st.button("🔍 Analyze Data"):
                    analyzed_df = analyze_data(df)
                    st.write("📈 Analyzed Results:")
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
                        st.download_button("📥 Download Results CSV", f, file_name=output_path)
        
        elif option == "📝 Take Individual Survey":
            st.subheader("Personal Wellness Survey")
            name = st.text_input("Full Name")
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
            
            if st.button("💡 Get My Recommendation"):
                if not name:
                    st.error("Please enter your name")
                else:
                    df = pd.DataFrame([{
                        "Username": st.session_state.current_user,
                        "Name": name, "Age": age, 
                        "Stress_Level": stress, "Sleep_Hours": sleep, "Exercise_Hours": exercise, 
                        "Academic_Workload": academic_workload, "Anxiety_Level": anxiety, "Social_Support": social_support,
                        "Depression_Level": depression, "Financial_Stress": financial_stress, "Relationship_Stress": relationship_stress,
                        "Coping_Frequency": coping_frequency, "Screen_Time": screen_time, "Nutrition_Quality": nutrition,
                        "Self_Esteem": self_esteem, "Work_Life_Balance": work_life_balance, "Future_Optimism": future_optimism
                    }])
                    analyzed_df = analyze_data(df)
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
