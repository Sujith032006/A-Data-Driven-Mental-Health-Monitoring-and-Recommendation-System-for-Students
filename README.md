# Mental Health Monitoring and Recommendation System for Students

This is a Python-based project that analyzes student wellness survey data and provides personalized recommendations. It includes a Streamlit web app for easy interaction.

## Features

- **Batch Analysis**: Upload a CSV file with student survey data to analyze and generate recommendations.
- **Individual Survey**: Take a personal survey to get tailored recommendations.
- **Data Visualization**: View charts for stress distribution, sleep distribution, and recommendation summary.
- **Download Results**: Export analyzed data as CSV.
- **User Authentication**: Simple login and registration system.

## Requirements

- Python 3.x
- Libraries: pandas, matplotlib, seaborn, streamlit

Install dependencies:
```
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Login or register a new account.

3. Choose between uploading a CSV for batch analysis or taking an individual survey.

## Files

- `app.py`: Main Streamlit application code.
- `analysis.py`: Functions for data analysis and chart generation.
- `student_survey.csv`: Sample input CSV file.
- `student_survey_results.csv`: Output CSV with recommendations.
- `stress_distribution.png`: Chart for stress levels.
- `sleep_distribution.png`: Chart for sleep hours.
- `recommendations_summary.png`: Chart for recommendation counts.
- `requirements.txt`: Python dependencies.

## Data Format

Input CSV should have columns: Name, Age, Stress_Level, Sleep_Hours, Exercise_Hours.

- Stress_Level: 1-10 scale
- Sleep_Hours: hours per night
- Exercise_Hours: hours per week

## Recommendation Rules

- High stress & low sleep: “Practice relaxation & improve sleep routine.”
- High stress only: “Try stress management or seek support.”
- Low sleep: “Increase rest for better focus.”
- Low exercise: “Add regular physical activity.”
- Else: “Good balance – Keep it up!”

Thresholds: Stress >7 (high), Sleep <6 (low), Exercise <1 (low).
