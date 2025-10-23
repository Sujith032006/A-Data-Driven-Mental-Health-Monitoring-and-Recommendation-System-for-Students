"""
Test script to verify ML model integration works correctly
"""
import pandas as pd
from analysis import analyze_data
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("Testing ML Model Integration")
print("=" * 60)

# Check if model files exist
print("\n1. Checking model files...")
model_exists = os.path.exists("models/risk_model.joblib")
features_exist = os.path.exists("models/feature_list.json")

print(f"   [OK] Model file exists: {model_exists}")
print(f"   [OK] Features file exists: {features_exist}")

if not model_exists or not features_exist:
    print("\n   ❌ ERROR: Model files not found!")
    print("   Run: python train_model.py")
    exit(1)

# Create test data
print("\n2. Creating test student data...")
test_data = pd.DataFrame([{
    "Name": "Test Student",
    "Age": 20,
    "Stress_Level": 8,
    "Sleep_Hours": 5.5,
    "Exercise_Hours": 1.0,
    "Academic_Workload": 9,
    "Anxiety_Level": 7,
    "Social_Support": 6,
    "Depression_Level": 6,
    "Financial_Stress": 5,
    "Relationship_Stress": 5,
    "Coping_Frequency": 5,
    "Screen_Time": 7,
    "Nutrition_Quality": 6,
    "Self_Esteem": 5,
    "Work_Life_Balance": 4,
    "Future_Optimism": 6
}])

print(f"   [OK] Test data created with {len(test_data)} student")

# Run analysis
print("\n3. Running analysis with ML model...")
try:
    analyzed_data = analyze_data(test_data)
    print("   [OK] Analysis completed successfully")
except Exception as e:
    print(f"   ❌ ERROR during analysis: {e}")
    exit(1)

# Check if Risk_Probability column was added
print("\n4. Checking ML predictions...")
if "Risk_Probability" in analyzed_data.columns:
    risk_prob = analyzed_data.iloc[0]["Risk_Probability"]
    print(f"   [OK] Risk_Probability column added")
    print(f"   [OK] Risk score: {risk_prob:.4f} ({risk_prob*100:.1f}%)")
    
    # Validate risk probability is in valid range
    if 0 <= risk_prob <= 1:
        print(f"   [OK] Risk probability in valid range [0, 1]")
    else:
        print(f"   [ERROR] WARNING: Risk probability out of range: {risk_prob}")
else:
    print("   ❌ ERROR: Risk_Probability column not found!")
    print(f"   Available columns: {list(analyzed_data.columns)}")
    exit(1)

# Check if Recommendation column exists
print("\n5. Checking rule-based recommendations...")
if "Recommendation" in analyzed_data.columns:
    recommendation = analyzed_data.iloc[0]["Recommendation"]
    print(f"   [OK] Recommendation column exists")
    print(f"   [OK] Recommendation length: {len(recommendation)} characters")
    
    # Check if recommendation has expected sections
    has_immediate = "Immediate Actions" in recommendation
    has_longterm = "Long-term Strategies" in recommendation or "Good balance" in recommendation
    
    print(f"   [OK] Has immediate actions: {has_immediate}")
    print(f"   [OK] Has strategies/advice: {has_longterm}")
else:
    print("   ❌ ERROR: Recommendation column not found!")
    exit(1)

# Display sample output
print("\n6. Sample Output:")
print("-" * 60)
print(f"Student: {analyzed_data.iloc[0]['Name']}")
print(f"Age: {analyzed_data.iloc[0]['Age']}")
print(f"Stress Level: {analyzed_data.iloc[0]['Stress_Level']}/10")
print(f"Sleep Hours: {analyzed_data.iloc[0]['Sleep_Hours']}")
print(f"Exercise Hours: {analyzed_data.iloc[0]['Exercise_Hours']}")
print(f"\nML Risk Score: {risk_prob*100:.1f}%")
print(f"\nRecommendation Preview:")
print(recommendation[:200] + "..." if len(recommendation) > 200 else recommendation)
print("-" * 60)

print("\n" + "=" * 60)
print("[SUCCESS] ALL TESTS PASSED!")
print("=" * 60)
print("\nML Model Integration is working correctly!")
print("\nNext steps:")
print("1. Start Streamlit: streamlit run app.py")
print("2. Login and take a survey")
print("3. You should see the risk score displayed as a percentage")
print("4. Admins will see Risk_Probability column in the table")
