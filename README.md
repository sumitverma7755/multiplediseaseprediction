HOW TO RUN THE MULTIPLE DISEASE PREDICTION SYSTEM
==============================================

STEP 1: SYSTEM REQUIREMENTS
--------------------------
- Python 3.8 or higher installed on your computer
- Windows 10/11, macOS 10.14+, or Linux
- Minimum 2GB RAM (4GB recommended)
- Internet connection for initial setup
- Modern web browser (Chrome 80+, Firefox 72+, or Edge 80+)

STEP 2: DOWNLOAD THE PROJECT
---------------------------
1. Download the project from GitHub
2. Extract the ZIP file to your desired location
3. Open terminal/command prompt
4. Navigate to the project folder:
   cd path/to/Multiple-Disease-Prediction-System

STEP 3: SET UP PYTHON ENVIRONMENT
--------------------------------
For Windows:
-----------
1. Open Command Prompt as administrator
2. Create virtual environment:
   python -m venv venv
3. Activate virtual environment:
   venv\Scripts\activate

For macOS/Linux:
---------------
1. Open Terminal
2. Create virtual environment:
   python -m venv venv
3. Activate virtual environment:
   source venv/bin/activate

STEP 4: INSTALL DEPENDENCIES
---------------------------
With the virtual environment activated, run:
pip install -r requirements.txt

This will install all required packages:
- streamlit==1.31.0
- pandas==2.2.0
- numpy==1.24.3
- scikit-learn==1.3.0
- plotly==5.18.0
- joblib==1.3.2

STEP 5: RUN THE APPLICATION
--------------------------
1. Make sure you're in the project directory
2. Make sure your virtual environment is activated
3. Run the command:
   streamlit run multiplediseaseprediction.py
4. The application will start and open in your default web browser
5. If it doesn't open automatically, visit:
   http://localhost:8501

USING THE APPLICATION
--------------------
1. Select disease type from the sidebar:
   - Diabetes Prediction
   - Heart Disease Prediction
   - Parkinson's Disease Prediction

2. Enter the required medical parameters

3. Click "Predict" to get results

4. View your prediction history in the History tab

TROUBLESHOOTING
--------------
If you encounter any issues:

1. "Module not found" error:
   - Verify virtual environment is activated
   - Run pip install -r requirements.txt again

2. Port already in use:
   - Try different port: streamlit run multiplediseaseprediction.py --server.port 8502

3. Python version error:
   - Verify Python 3.8+ is installed: python --version
   - Create new virtual environment with correct Python version

4. Application not opening:
   - Check if streamlit is running (terminal should show URLs)
   - Try opening the URL manually in your browser
   - Check if firewall is blocking the application

For additional help:
- Check the project documentation
- Submit an issue on GitHub
- Contact the development team

CLOSING THE APPLICATION
----------------------
1. Return to terminal/command prompt
2. Press Ctrl+C to stop the application
3. Deactivate virtual environment:
   - Windows: deactivate
   - macOS/Linux: deactivate

Remember: This is a prediction tool for educational purposes only. 
Always consult healthcare professionals for medical advice. 
# Multiple Disease Prediction System using Machine Learning 🏥

A sophisticated machine learning-based web application that predicts multiple diseases using medical parameters. Built with Streamlit and scikit-learn, this system provides predictions for Diabetes, Heart Disease, and Parkinson's Disease.

## 🌟 Features

- **Multi-Disease Prediction**: Analyze risk factors for multiple diseases:
  - Diabetes Prediction
  - Heart Disease Prediction
  - Parkinson's Disease Prediction

- **Interactive Interface**: User-friendly web interface with:
  - Clear input parameters
  - Real-time predictions
  - Confidence scores
  - Visual analytics

- **Comprehensive Analysis**:
  - Detailed prediction results
  - Risk factor analysis
  - Health metrics visualization
  - Historical prediction tracking

## 🛠️ Technologies Used

- **Python 3.8+**
- **Key Libraries**:
  - streamlit==1.31.0
  - pandas==2.2.0
  - numpy==1.24.3
  - scikit-learn==1.3.0
  - plotly==5.18.0
  - joblib==1.3.2

## 🚀 Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/Multiple-Disease-Prediction-System.git
   cd Multiple-Disease-Prediction-System
   ```

2. **Set Up Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Unix/macOS
   venv\Scripts\activate     # On Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   streamlit run multiplediseaseprediction.py
   ```

## 📊 Disease Prediction Details

### Diabetes Prediction
- Uses medical indicators like:
  - Glucose Level
  - Blood Pressure
  - BMI
  - Age
  - Other relevant parameters

### Heart Disease Prediction
- Analyzes factors including:
  - Blood Pressure
  - Cholesterol Levels
  - Heart Rate
  - ECG Results
  - Additional cardiovascular parameters

### Parkinson's Disease Prediction
- Evaluates voice parameters:
  - Frequency Measures
  - Amplitude Parameters
  - Voice Fluctuation Metrics
  - Other acoustic characteristics

## 💡 Key Features

1. **User-Friendly Interface**
   - Clean, intuitive design
   - Step-by-step input guidance
   - Clear result presentation

2. **Advanced Analytics**
   - Prediction confidence scores
   - Risk factor analysis
   - Health metrics comparison
   - Trend visualization

3. **History Tracking**
   - Save prediction history
   - View past analyses
   - Track health parameters over time

4. **Data Security**
   - Secure data handling
   - Privacy-focused design
   - No personal data storage

## 🔧 System Requirements

- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **RAM**: 2GB minimum (4GB recommended)
- **Storage**: 1GB free space
- **Browser**: Chrome 80+, Firefox 72+, or Edge 80+

## 📝 Usage Guidelines

1. Select the disease type for prediction
2. Enter required medical parameters
3. Click "Predict" to get results
4. View detailed analysis and recommendations
5. Track predictions in history

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Disclaimer

This application is for educational and research purposes only. It should not be used as a substitute for professional medical diagnosis. Always consult with healthcare professionals for medical advice.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Dataset providers
- Open-source community
- Contributors and testers

## 📞 Contact

For questions and support, please open an issue in the GitHub repository.

---
⭐ Star this repository if you find it helpful! 
