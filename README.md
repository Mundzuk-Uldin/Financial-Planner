# 💰 AI-Powered Financial Simulator

An interactive tool that helps users visualize their financial future based on current habits and demonstrates how small changes can lead to significant improvements over time.

## 🌟 Features

- **Synthetic Data Generation**: Create realistic financial profiles for demonstration or testing
- **Financial Health Analysis**: Get AI-powered assessment of your financial situation
- **Smart Recommendations**: Receive personalized tips to improve your finances
- **Future Simulation**: Compare two scenarios:
  - **Current Path**: Projection if you continue current habits
  - **Improved Path**: Projection if you implement recommended changes
- **Interactive Visualizations**: See your financial journey through intuitive charts and graphs
- **Custom Data Input**: Import your own financial data via manual entry or CSV upload

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## 🚀 Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/financial-simulator.git
cd financial-simulator
```

2. **Create and activate a virtual environment**

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install pandas numpy faker scikit-learn streamlit plotly
pip freeze > requirements.txt
```

## 🔧 Usage

1. **Run the Streamlit app**

```bash
streamlit run app.py
```

2. **Access the web interface**

Open your browser and go to `http://localhost:8501`



## 🛠️ Core Components

### 1. Data Generator (src/data_generator.py)
- Generates realistic financial profiles with random variations
- Creates different debt types, expense patterns, and savings behaviors
- Outputs data in a format ready for analysis

### 2. Financial Analyzer (src/analyzer.py)
- Detects financial issues like:
  - Insufficient emergency funds
  - High debt-to-income ratio
  - Excessive expenses
  - Low savings rate
  - High-interest debt
- Rates issues by severity (high/medium)
- Provides an overall financial health score
- Generates personalized recommendations

### 3. Future Simulator (src/simulator.py)
- Projects financial metrics month-by-month over 5 years
- Models two scenarios:
  - Current path: continuing current financial behavior
  - Improved path: implementing recommended changes
- Calculates key metrics like:
  - Net worth growth
  - Debt reduction timeline
  - Savings accumulation
  - Financial milestones (e.g., debt-free date)

### 4. Web Application (app.py)
- Streamlit-based user interface with:
  - Multi-page navigation
  - Interactive data input forms
  - Visual financial health assessment
  - Dynamic charts and projections
- Features for exporting results and recommendations

## 🔍 How It Works

1. **Data Generation/Input**: The application either generates synthetic financial profiles or accepts user input.
2. **Financial Analysis**: The system analyzes the profile to identify issues like high debt-to-income ratio or insufficient emergency funds.
3. **Recommendation Engine**: Based on the analysis, the system generates actionable financial advice.
4. **Future Projection**: The application simulates two financial futures:
   - Continuing with current financial habits
   - Implementing the recommended improvements
5. **Visualization**: Results are displayed through intuitive charts showing the impact of changes over time.