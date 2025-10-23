# Mental Health Monitoring and Recommendation System for Students

A comprehensive Python-based platform for monitoring student mental health, providing personalized recommendations, and offering interactive support through a chatbot. Built with Streamlit for an intuitive web interface.

## Features

- **User Authentication**: Secure login and registration system with password recovery.
- **Mood Tracking**: Daily mood logging with optional journaling.
- **Wellness Survey**: Comprehensive assessment of mental health and well-being.
- **Personalized Recommendations**: AI-powered suggestions based on survey responses.
- **Interactive Chatbot**: 24/7 emotional support and guidance.
- **Admin Dashboard**: For managing users and viewing analytics.
- **Data Visualization**: Interactive charts for mood trends and wellness metrics.
- **Secure & Private**: All user data is encrypted and stored securely.

## Requirements

- Python 3.8+
- Required packages (see `requirements.txt`):
  - streamlit
  - pandas
  - matplotlib
  - seaborn
  - numpy
  - scikit-learn
  - nltk
  - transformers
  - torch

Install dependencies:
```bash
pip install -r requirements.txt
```

## Getting Started

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd MINIPROJECT2
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

4. Open your browser and navigate to `http://localhost:8501`

## Key Components

- `app.py`: Main application with Streamlit interface
- `chatbot.py`: AI-powered chatbot implementation
- `analysis.py`: Data analysis and visualization functions
- `users.json`: User database (automatically created)
- `mood_log.csv`: Stores mood tracking data
- `student_survey_results.csv`: Survey responses and recommendations
- `requirements.txt`: Project dependencies

## User Guide

### For Students:
1. **Register/Login**: Create an account or log in to access your dashboard
2. **Mood Tracker**: Log your daily mood and journal entries
3. **Wellness Survey**: Complete the comprehensive mental health assessment
4. **Chatbot**: Get instant support and guidance
5. **View Insights**: Track your mood trends and survey results

### For Administrators:
1. **User Management**: View, add, edit, or remove user accounts
2. **Analytics Dashboard**: Monitor overall system usage and trends
3. **Survey Results**: Access and export survey data
4. **System Settings**: Configure application parameters

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

## Data Privacy & Security

- All user data is encrypted at rest
- Passwords are hashed using secure algorithms
- Personal information is never shared with third parties
- Users can request data deletion at any time

## Support

For support or to report issues, please contact [your-email@example.com]

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) before submitting pull requests.

## Acknowledgments

- Built with ❤️ using Streamlit
- Special thanks to all contributors and testers
