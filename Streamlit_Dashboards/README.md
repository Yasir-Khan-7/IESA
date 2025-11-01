# IESA (Intelligent Energy System Analytics) Dashboard

A comprehensive energy analytics and visualization platform built with Streamlit, providing insights into energy consumption, predictions, and scenario analysis.

## 🌟 Features

- **Interactive Dashboard**: Real-time energy data visualization
- **Data Planning**: Advanced data management and planning tools
- **Scenario Analysis**: K-means clustering based scenario analysis
- **Wisdom Mining**: Deep insights and pattern recognition
- **Prediction Engine**: AI-powered energy consumption predictions
- **Personalized Recommendations**: Customized energy optimization suggestions

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL Server 8.0 or higher
- Git

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/IESA.git
   cd IESA/Streamlit_Dashboards
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   - Install MySQL Server if not already installed
   - Create a new database named `iesa_db`
   - Update database credentials in `mysql_con.py`:
     ```python
     host="localhost"
     port="3306"
     user="your_username"
     passwd="your_password"
     db="iesa_db"
     ```

## 🏗️ Project Structure

```
IESA/
├── Streamlit_Dashboards/
│   ├── iesa_dashboard.py          # Main dashboard
│   ├── iesa_data_planner.py       # Data planning module
│   ├── iesa_scenerio_analysis.py  # Scenario analysis
│   ├── iesa_wisdom_mining.py      # Wisdom mining module
│   ├── iesa_prediction_engine.py  # Prediction engine
│   ├── mysql_con.py              # Database connectivity
│   ├── utils/                    # Utility functions
│   ├── chart_images/             # Generated charts
│   ├── logs/                     # Application logs
│   └── images/                   # Static images
```

## 🚀 Running the Application

1. **Start the application**
   ```bash
   streamlit run iesa_dashboard.py
   ```

2. **Access the dashboard**
   - Open your web browser
   - Navigate to `http://localhost:8501`

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory with the following variables:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=iesa_db
```

### Logging Configuration
Logs are stored in the `logs/` directory. Configure logging levels in `utils/logger.py`.

## 📊 Features in Detail

### Dashboard
- Real-time energy consumption visualization
- Interactive charts and graphs
- Customizable date ranges
- Export functionality

### Data Planner
- Data import/export capabilities
- Data validation and cleaning
- Custom data transformations

### Scenario Analysis
- K-means clustering for pattern recognition
- Multiple scenario comparison
- What-if analysis

### Wisdom Mining
- Pattern recognition
- Trend analysis
- Anomaly detection

### Prediction Engine
- Machine learning based predictions
- Multiple forecasting models
- Accuracy metrics

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Streamlit team for the amazing framework
- All contributors who have helped shape this project

## 📞 Support

For support, email your-email@example.com or create an issue in the repository.

## 🔄 Updates

### Latest Updates
- Added K-means clustering for scenario analysis
- Implemented new prediction models
- Enhanced dashboard UI/UX

### Planned Features
- Real-time data streaming
- Advanced machine learning models
- Mobile application support

---

⭐ Star this repository if you find it useful! Contribution is also apprecaited 
Long Live Pakistan