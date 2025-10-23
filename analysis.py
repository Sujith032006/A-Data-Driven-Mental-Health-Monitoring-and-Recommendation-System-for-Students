import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
from joblib import load

def load_data(file_path):
    return pd.read_csv(file_path)

def generate_recommendation(row):
    stress = row['Stress_Level']
    sleep = row['Sleep_Hours']
    exercise = row['Exercise_Hours']
    academic = row.get('Academic_Workload', stress)
    anxiety = row.get('Anxiety_Level', stress)
    social = row.get('Social_Support', 5)
    depression = row.get('Depression_Level', stress)
    financial = row.get('Financial_Stress', stress)
    relationship = row.get('Relationship_Stress', stress)
    coping = row.get('Coping_Frequency', 5)
    screen_time = row.get('Screen_Time', 5)
    nutrition = row.get('Nutrition_Quality', 5)
    self_esteem = row.get('Self_Esteem', 5)
    work_life = row.get('Work_Life_Balance', 5)
    future_opt = row.get('Future_Optimism', 5)
    
    overall_stress = (stress + academic + anxiety + depression + financial + relationship) / 6
    
    recommendations = {
        'immediate_actions': [],
        'long_term_strategies': [],
        'resources': []
    }
    
    # Immediate Actions
    if overall_stress > 8:
        recommendations['immediate_actions'].append("Seek immediate professional help: Contact a counselor or therapist through your school's mental health services.")
        recommendations['resources'].append("National Suicide Prevention Lifeline: 988")
    elif overall_stress > 6:
        recommendations['immediate_actions'].append("Practice deep breathing: 4-7-8 technique (inhale 4s, hold 7s, exhale 8s) for 5 minutes.")
    
    if anxiety > 7:
        recommendations['immediate_actions'].append("Use grounding techniques: 5-4-3-2-1 method (5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste).")
    
    if depression > 7:
        recommendations['immediate_actions'].append("Reach out to a trusted friend or family member for support.")
        recommendations['resources'].append("Depression support: Visit psychologytoday.com or call 1-800-950-NAMI")
    
    # Sleep Recommendations
    if sleep < 6:
        recommendations['immediate_actions'].append("Create a wind-down routine: Dim lights, avoid screens 1 hour before bed, read or meditate.")
        recommendations['long_term_strategies'].append("Maintain consistent sleep schedule, even on weekends. Aim for 7-9 hours nightly.")
    elif sleep < 7:
        recommendations['long_term_strategies'].append("Optimize your sleep environment: Cool, dark, quiet room. Consider a white noise machine.")
    
    # Exercise Recommendations
    if exercise < 1:
        recommendations['immediate_actions'].append("Start small: 10-minute walk today. Build up gradually.")
        recommendations['long_term_strategies'].append("Incorporate daily movement: Walking, yoga, or sports 3-5 times per week.")
    elif exercise < 2:
        recommendations['long_term_strategies'].append("Increase to 150 minutes of moderate aerobic activity per week, plus strength training twice weekly.")
    
    # Social Support
    if social < 5:
        recommendations['immediate_actions'].append("Connect with someone today: Call a friend or join an online community.")
        recommendations['long_term_strategies'].append("Build a support network: Join clubs, study groups, or volunteer organizations.")
    
    # Coping Strategies
    if coping < 5:
        recommendations['immediate_actions'].append("Try one healthy coping skill: Journaling, listening to music, or progressive muscle relaxation.")
        recommendations['long_term_strategies'].append("Develop a coping toolkit: Learn techniques like mindfulness, CBT, or art therapy.")
    
    # Screen Time
    if screen_time > 8:
        recommendations['immediate_actions'].append("Set screen time limits: Use phone settings to track and limit recreational screen use.")
        recommendations['long_term_strategies'].append("Create screen-free zones: No devices in bedroom, establish tech-free hours daily.")
    
    # Nutrition
    if nutrition < 5:
        recommendations['immediate_actions'].append("Eat a balanced meal today: Include protein, vegetables, and whole grains.")
        recommendations['long_term_strategies'].append("Plan meals ahead: Focus on Mediterranean diet with plenty of fruits, vegetables, and omega-3 rich foods.")
    
    # Financial Stress
    if financial > 7:
        recommendations['immediate_actions'].append("Create a basic budget: Track income and expenses for one week.")
        recommendations['resources'].append("Financial aid resources: Contact your school's financial aid office or visit finaid.org")
    
    # Relationship Stress
    if relationship > 7:
        recommendations['immediate_actions'].append("Communicate openly: Express your feelings calmly to the person involved.")
        recommendations['long_term_strategies'].append("Consider counseling: Individual or couples therapy can help resolve conflicts.")
    
    # Academic Workload
    if academic > 8:
        recommendations['immediate_actions'].append("Break tasks down: Use the Pomodoro technique (25 min work, 5 min break).")
        recommendations['long_term_strategies'].append("Develop study skills: Time management workshops, tutoring, or academic coaching.")
    
    # Self-Esteem
    if self_esteem < 5:
        recommendations['immediate_actions'].append("Boost self-esteem: Practice positive affirmations and celebrate small achievements.")
        recommendations['long_term_strategies'].append("Build self-confidence: Set achievable goals and track your progress.")
    
    # Work-Life Balance
    if work_life < 5:
        recommendations['immediate_actions'].append("Set boundaries: Allocate specific times for study and relaxation.")
        recommendations['long_term_strategies'].append("Improve balance: Schedule personal time and hobbies regularly.")
    
    # Future Optimism
    if future_opt < 5:
        recommendations['immediate_actions'].append("Focus on positives: List three things you're grateful for daily.")
        recommendations['long_term_strategies'].append("Build optimism: Visualize positive outcomes and seek mentorship.")
    
    # Overall well-being
    if overall_stress <= 5 and sleep >= 7 and exercise >= 2 and social >= 6:
        recommendations['immediate_actions'].append("Maintain your healthy habits! You're doing great.")
        recommendations['long_term_strategies'].append("Monitor for changes and continue preventive care.")
    
    # Format the recommendation
    rec_text = ""
    if recommendations['immediate_actions']:
        rec_text += "**Immediate Actions:**\n" + "\n".join(f"• {action}" for action in recommendations['immediate_actions']) + "\n\n"
    if recommendations['long_term_strategies']:
        rec_text += "**Long-term Strategies:**\n" + "\n".join(f"• {strategy}" for strategy in recommendations['long_term_strategies']) + "\n\n"
    if recommendations['resources']:
        rec_text += "**Helpful Resources:**\n" + "\n".join(f"• {resource}" for resource in recommendations['resources']) + "\n\n"
    
    if not rec_text:
        rec_text = "Your current wellness indicators look good. Continue monitoring and maintaining healthy habits. If you notice any changes, revisit this assessment."
    
    return rec_text.strip()

def analyze_data(df):
    # Try to add model-based risk if a trained model is available
    try:
        _load_model()
        if _MODEL is not None:
            df['Risk_Probability'] = _predict_risk(df)
    except Exception:
        # Be resilient; keep app running even if model load/predict fails
        pass

    df['Recommendation'] = df.apply(generate_recommendation, axis=1)
    return df

def save_results(df, output_path):
    df.to_csv(output_path, index=False)

def plot_stress_distribution(df, save_path):
    plt.figure(figsize=(8, 6))
    sns.histplot(df['Stress_Level'], bins=10, kde=True)
    plt.title('Stress Level Distribution')
    plt.xlabel('Stress Level')
    plt.ylabel('Frequency')
    plt.savefig(save_path)
    plt.close()

# ----------------------
# Model loading/inference
# ----------------------

_MODEL = None
_FEATURES = []
_MODEL_PATH = 'models/risk_model.joblib'
_FEATURES_PATH = 'models/feature_list.json'

def _load_model():
    global _MODEL, _FEATURES
    if _MODEL is not None:
        return
    if os.path.exists(_MODEL_PATH):
        _MODEL = load(_MODEL_PATH)
        if os.path.exists(_FEATURES_PATH):
            try:
                with open(_FEATURES_PATH, 'r') as f:
                    data = json.load(f)
                    _FEATURES = data.get('features', [])
            except Exception:
                _FEATURES = []
        else:
            _FEATURES = []
    else:
        _MODEL = None
        _FEATURES = []

def _predict_risk(df: pd.DataFrame):
    """Return risk probabilities for rows in df using trained model.
    If required feature columns are missing, fill with zeros.
    """
    if _MODEL is None:
        raise RuntimeError('Model not loaded')
    cols = _FEATURES if _FEATURES else [c for c in ['Stress_Level','Sleep_Hours','Exercise_Hours'] if c in df.columns]
    X = df.copy()
    # Ensure columns
    for c in cols:
        if c not in X.columns:
            X[c] = 0
    X = X[cols]
    try:
        proba = _MODEL.predict_proba(X)[:, 1]
    except Exception:
        # If model does not support predict_proba, fallback to decision_function if available
        if hasattr(_MODEL, 'decision_function'):
            from sklearn.preprocessing import MinMaxScaler
            scores = _MODEL.decision_function(X).reshape(-1, 1)
            scaler = MinMaxScaler()
            proba = scaler.fit_transform(scores).ravel()
        else:
            # Last resort: zeros
            proba = [0.0] * len(X)
    return proba

def plot_sleep_distribution(df, save_path):
    plt.figure(figsize=(8, 6))
    sns.histplot(df['Sleep_Hours'], bins=10, kde=True)
    plt.title('Sleep Hours Distribution')
    plt.xlabel('Sleep Hours')
    plt.ylabel('Frequency')
    plt.savefig(save_path)
    plt.close()

def plot_recommendation_summary(df, save_path):
    plt.figure(figsize=(10, 6))
    rec_counts = df['Recommendation'].value_counts()
    sns.barplot(x=rec_counts.values, y=rec_counts.index, orient='h')
    plt.title('Recommendation Summary')
    plt.xlabel('Count')
    plt.ylabel('Recommendation')
    plt.savefig(save_path)
    plt.close()
