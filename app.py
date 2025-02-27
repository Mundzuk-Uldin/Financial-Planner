import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
import json
import base64
import uuid
from io import BytesIO

# Import our core modules
from src.data_generator import FinancialDataGenerator
from src.analyzer import FinancialAnalyzer
from src.simulator import FinancialSimulator

# Import enhancement modules
from src.investment_simulator import InvestmentSimulator
from src.tax_calculator import TaxCalculator
from src.pdf_generator import FinancialReportGenerator
from src.user_accounts import UserDatabase
from src.gamification import AchievementSystem

# Set up Streamlit configuration
st.set_page_config(
    page_title="Financial Future Simulator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Initialize user database
@st.cache_resource
def initialize_database():
    return UserDatabase()

user_db = initialize_database()

# Initialize Achievement System
@st.cache_resource
def initialize_achievement_system():
    return AchievementSystem(user_db)

achievement_system = initialize_achievement_system()

# Initialize Tax Calculator
@st.cache_resource
def initialize_tax_calculator():
    return TaxCalculator()

tax_calculator = initialize_tax_calculator()

# Initialize session state
if 'is_guest' not in st.session_state:
    st.session_state.is_guest = False
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None
if 'investment_results' not in st.session_state:
    st.session_state.investment_results = None
if 'tax_analysis' not in st.session_state:
    st.session_state.tax_analysis = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_achievements' not in st.session_state:
    st.session_state.user_achievements = []
if 'simulation_count' not in st.session_state:
    st.session_state.simulation_count = 0
if 'profile_history' not in st.session_state:
    st.session_state.profile_history = []
if 'login_history' not in st.session_state:
    st.session_state.login_history = []

def login_page():
    st.title("💰 Financial Future Simulator - Login")
    
    st.markdown("""
    ### Welcome to the Financial Future Simulator
    
    This tool helps you visualize your financial future and explore how different decisions 
    impact your long-term financial health.
    """)
    
    # Add a prominent guest access button
    if st.button("👉 Continue Without an Account", use_container_width=True, type="primary"):
        # Set a guest user ID and continue
        st.session_state.user_id = "guest-" + str(uuid.uuid4())
        st.session_state.is_guest = True
        st.session_state.login_history.append(datetime.now().isoformat())
        st.rerun()
    
    # Divider
    st.markdown("---")
    
    # Login form in columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                success, message, user_id = user_db.authenticate_user(username, password)
                if success:
                    st.session_state.user_id = user_id
                    st.session_state.is_guest = False
                    st.session_state.login_history.append(datetime.now().isoformat())
                    
                    # Load user's saved profiles
                    profiles = user_db.get_financial_profiles(user_id)
                    if profiles:
                        st.session_state.user_profile = profiles[0]["data"]
                        st.session_state.profile_history.append(profiles[0]["data"])
                    
                    # Load achievements
                    st.session_state.user_achievements = user_db.get_user_achievements(user_id)
                    
                    # Check for app usage achievements
                    achievement_system.check_app_usage_achievements(
                        user_id=user_id,
                        profile_saved=bool(profiles),
                        simulation_run=st.session_state.simulation_count > 0,
                        login_history=st.session_state.login_history
                    )
                    
                    st.success(f"Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error(message)
    
    with col2:
        st.subheader("New User?")
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register = st.form_submit_button("Register", use_container_width=True)
            
            if register:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message, user_id = user_db.create_user(new_username, new_email, new_password)
                    if success:
                        st.session_state.user_id = user_id
                        st.session_state.is_guest = False
                        st.session_state.login_history.append(datetime.now().isoformat())
                        st.success(f"Welcome, {new_username}! Your account has been created.")
                        st.rerun()
                    else:
                        st.error(message)
    
    # App features preview
    st.markdown("---")
    st.subheader("Features")
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("### 📊 Financial Analysis")
        st.write("Get insights into your financial health and customized recommendations.")
    
    with feature_col2:
        st.markdown("### 📈 Future Projections")
        st.write("See how your decisions today impact your financial future.")
    
    with feature_col3:
        st.markdown("### 🏆 Achievement System")
        st.write("Track your progress and earn rewards for good financial habits.")

# Sidebar with navigation and user info
def sidebar_navigation():
    with st.sidebar:
        if st.session_state.user_id:
            st.title("Navigation")
            
            # Display user info
            if st.session_state.get('is_guest', False):
                st.info("Using as guest (data won't be saved)")
                if st.button("Sign in / Register"):
                    # Clear session state except for certain keys
                    for key in list(st.session_state.keys()):
                        if key not in ['user_profile', 'analysis_results', 'simulation_results']:
                            del st.session_state[key]
                    st.rerun()
            else:
                st.info(f"Logged in as user")
                if st.button("Log Out"):
                    # Clear session state
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
            
            # Show achievement count if not guest
            if not st.session_state.get('is_guest', False) and st.session_state.user_achievements:
                st.success(f"Achievements: {len(st.session_state.user_achievements)}")
            
            # Navigation options
            pages = ["Home", "Data Input", "Analysis", "Future Simulation", 
                     "Investment Planner", "Tax Analysis"]
            
            # Add achievements and reports only for registered users
            if not st.session_state.get('is_guest', False):
                pages.extend(["Achievements", "Reports"])
                
            page = st.radio("Go to", pages)
            
            # Show profile selector if user has saved profiles and is not a guest
            if not st.session_state.get('is_guest', False):
                profiles = user_db.get_financial_profiles(st.session_state.user_id)
                if profiles:
                    st.subheader("Your Profiles")
                    profile_names = [p["name"] for p in profiles]
                    selected_profile = st.selectbox("Load Profile", profile_names)
                    
                    if st.button("Load Selected Profile"):
                        for profile in profiles:
                            if profile["name"] == selected_profile:
                                st.session_state.user_profile = profile["data"]
                                
                                # Add to profile history
                                st.session_state.profile_history.append(profile["data"])
                                if len(st.session_state.profile_history) > 12:  # Keep last 12 months
                                    st.session_state.profile_history.pop(0)
                                
                                st.success(f"Loaded profile: {selected_profile}")
                                
                                # Check for achievements
                                if not st.session_state.get('is_guest', False):
                                    achievement_system.check_emergency_fund_achievements(
                                        profile["data"], st.session_state.user_id)
                                
                                # Load associated analysis and simulation results
                                analysis = user_db.get_analysis_results(profile["id"])
                                if analysis:
                                    st.session_state.analysis_results = analysis["data"]
                                
                                simulation = user_db.get_simulation_results(profile["id"])
                                if simulation:
                                    st.session_state.simulation_results = simulation["data"]
                                
                                st.rerun()
            else:
                st.warning("Create an account to save your profiles and track achievements!")
        else:
            st.title("Financial Simulator")
            st.write("Please log in to use all features.")
            page = "Login"
        
        return page

# Download link for PDF reports
def get_pdf_download_link(pdf_path, filename="financial_report.pdf"):
    with open(pdf_path, "rb") as file:
        encoded_file = base64.b64encode(file.read()).decode()
    
    href = f'<a href="data:application/pdf;base64,{encoded_file}" download="{filename}">Download PDF Report</a>'
    return href

# Main application
def main():
    if 'user_id' not in st.session_state or st.session_state.user_id is None:
        page = "Login"
    else:
        page = sidebar_navigation()
    
    # Page routing
    if page == "Login":
        login_page()
    
    elif page == "Home":
        st.title("💰 AI-Powered Financial Future Simulator")
        
        # Show guest mode notice
        if st.session_state.get('is_guest', False):
            st.warning("You are using guest mode. Your data won't be saved between sessions. Create an account to save your progress and unlock achievements!")
        
        st.write("""
        Welcome to the enhanced Financial Future Simulator! This tool helps you visualize your financial future
        based on your current habits and shows how small changes can lead to significant improvements.
        
        ### Key Features:
        1. **Financial Analysis**: Get AI-powered assessment of your financial health
        2. **Future Simulation**: See two possible financial futures based on your decisions
        3. **Investment Planning**: Optimize your investment strategy based on your risk profile
        4. **Tax Analysis**: Understand tax implications on your financial growth
        """)
        
        # Only show achievements for registered users
        if not st.session_state.get('is_guest', False):
            st.write("""
            5. **Achievement System**: Track your financial progress with badges and milestones
            6. **PDF Reports**: Generate comprehensive financial reports to save or share
            """)
        
        st.write("""
        ### Get started:
        Choose "Data Input" from the sidebar to begin your financial journey!
        """)
        
        st.image("https://images.unsplash.com/photo-1579621970588-a35d0e7ab9b6?auto=format&fit=crop&w=800&q=80", 
                 caption="Plan your financial future today")
        
        # Display recent achievements if any and not guest
        if st.session_state.user_achievements and not st.session_state.get('is_guest', False):
            st.subheader("Your Recent Achievements")
            
            # Show the most recent 3 achievements
            recent_achievements = st.session_state.user_achievements[:3]
            
            cols = st.columns(min(3, len(recent_achievements)))
            for i, achievement in enumerate(recent_achievements):
                with cols[i]:
                    st.markdown(f"### 🏆 {achievement['data']['title']}")
                    st.write(achievement['data']['description'])
                    st.info(f"Achieved: {achievement['achieved_at'][:10]}")
    
    elif page == "Data Input":
        st.title("Step 1: Financial Data Input")
        
        input_method = st.radio(
            "Choose an input method:",
            ["Generate Sample Profile", "Enter My Own Data", "Upload CSV"]
        )
        
        if st.button("Generate Random Profile"):
            generator = FinancialDataGenerator()
            profile = generator.generate_user()
            
            # Convert to flat dictionary for session state
            flat_profile = {
                "monthly_income": profile["monthly_income"],
                "current_savings": profile["current_savings"],
                "total_debt": sum(profile["debt_amounts"]) if profile["debt_amounts"] else 0
            }
            
            # Add expenses
            for category, amount in profile["expenses"].items():
                flat_profile[f"expense_{category.lower().replace('/', '_')}"] = amount
            
            # Calculate and add monthly_savings
            total_expenses = sum(flat_profile[k] for k in flat_profile if k.startswith('expense_'))
            flat_profile["monthly_savings"] = flat_profile["monthly_income"] - total_expenses
            
            # Add debt info
            if profile["debt_amounts"]:
                max_debt_idx = np.argmax(profile["debt_amounts"])
                flat_profile["primary_debt_type"] = profile["debt_types"][max_debt_idx]
                flat_profile["primary_debt_apr"] = profile["debt_aprs"][max_debt_idx]
            else:
                flat_profile["primary_debt_type"] = "None"
                flat_profile["primary_debt_apr"] = 0.0
            
            # Add age and risk tolerance
            flat_profile["age"] = profile["age"]
            flat_profile["risk_tolerance"] = profile["risk_tolerance"]
            
            st.session_state.user_profile = flat_profile
            
            # Add to profile history
            st.session_state.profile_history.append(flat_profile)
            if len(st.session_state.profile_history) > 12:  # Keep last 12 months
                st.session_state.profile_history.pop(0)
            
            st.success("Sample profile generated! Go to Analysis to see results.")
            
            # Display profile summary
            col1, col2 = st.columns(2)
            # ... (display code remains the same)
            
            # Save to database if logged in AND not a guest
            if st.session_state.user_id and not st.session_state.get('is_guest', False):
                success, message, profile_id = user_db.save_financial_profile(
                    st.session_state.user_id,
                    "Generated Profile",
                    flat_profile
                )
                if success:
                    st.info("Profile saved to your account")
                    
                    # Check for achievement
                    achievement_system.check_app_usage_achievements(
                        st.session_state.user_id,
                        profile_saved=True,
                        simulation_run=st.session_state.simulation_count > 0,
                        login_history=st.session_state.login_history
                    )
            elif st.session_state.get('is_guest', False):
                st.info("Create an account to save this profile!")
        
        elif input_method == "Enter My Own Data":
            st.info("Enter your financial information below.")
            
            with st.form("financial_form"):
                st.subheader("Basic Information")
                col1, col2 = st.columns(2)
                
                with col1:
                    age = st.number_input("Age", min_value=18, max_value=100, value=35)
                    risk_tolerance = st.selectbox("Risk Tolerance", ["Low", "Medium", "High"])
                
                with col2:
                    monthly_income = st.number_input("Monthly Income ($)", min_value=0.0, value=4000.0, step=100.0)
                    current_savings = st.number_input("Current Savings ($)", min_value=0.0, value=10000.0, step=100.0)
                
                st.subheader("Monthly Expenses")
                col1, col2 = st.columns(2)
                
                with col1:
                    expense_rent = st.number_input("Rent/Mortgage ($)", min_value=0.0, value=1200.0, step=50.0)
                    expense_utilities = st.number_input("Utilities ($)", min_value=0.0, value=200.0, step=10.0)
                    expense_groceries = st.number_input("Groceries ($)", min_value=0.0, value=400.0, step=50.0)
                    expense_dining = st.number_input("Dining Out ($)", min_value=0.0, value=300.0, step=50.0)
                
                with col2:
                    expense_transport = st.number_input("Transportation ($)", min_value=0.0, value=150.0, step=50.0)
                    expense_healthcare = st.number_input("Healthcare ($)", min_value=0.0, value=100.0, step=50.0)
                    expense_entertainment = st.number_input("Entertainment ($)", min_value=0.0, value=200.0, step=50.0)
                    expense_other = st.number_input("Other Expenses ($)", min_value=0.0, value=500.0, step=50.0)
                
                st.subheader("Debt Information")
                has_debt = st.checkbox("I have debt")
                
                total_debt = 0.0
                primary_debt_type = "None"
                primary_debt_apr = 0.0
                expense_debt = 0.0
                
                if has_debt:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        total_debt = st.number_input("Total Debt Amount ($)", min_value=0.0, value=5000.0, step=100.0)
                        primary_debt_type = st.selectbox(
                            "Primary Debt Type", 
                            ["Credit Card", "Student Loan", "Car Loan", "Personal Loan", "Mortgage", "Other"]
                        )
                    
                    with col2:
                        primary_debt_apr = st.number_input("Interest Rate (APR %)", min_value=0.0, value=15.0, step=0.1)
                        expense_debt = st.number_input("Monthly Debt Payments ($)", min_value=0.0, value=200.0, step=50.0)
                
                # Optional investment information
                st.subheader("Investment Information (Optional)")
                has_investments = st.checkbox("I have investments")
                
                current_investments = 0.0
                monthly_contributions = 0.0
                retirement_contributions = 0.0
                
                if has_investments:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        current_investments = st.number_input("Current Investment Value ($)", min_value=0.0, value=0.0, step=1000.0)
                        monthly_contributions = st.number_input("Monthly Investment Contribution ($)", min_value=0.0, value=0.0, step=50.0)
                    
                    with col2:
                        retirement_contributions = st.number_input("Annual Retirement Contributions ($)", min_value=0.0, value=0.0, step=500.0)
                        investment_strategy = st.selectbox(
                            "Current Investment Strategy", 
                            ["Conservative", "Moderate", "Aggressive", "Not Sure"]
                        )
                
                # Profile name
                profile_name = st.text_input("Profile Name", "My Financial Profile")
                
                submit = st.form_submit_button("Save Financial Data")
                
                if submit:
                    profile = {
                        "age": age,
                        "risk_tolerance": risk_tolerance,
                        "monthly_income": monthly_income,
                        "current_savings": current_savings,
                        "expense_rent_mortgage": expense_rent,
                        "expense_utilities": expense_utilities,
                        "expense_groceries": expense_groceries,
                        "expense_dining_out": expense_dining,
                        "expense_transportation": expense_transport,
                        "expense_healthcare": expense_healthcare,
                        "expense_entertainment": expense_entertainment,
                        "expense_other": expense_other,
                        "expense_debt_payments": expense_debt,
                        "total_debt": total_debt,
                        "primary_debt_type": primary_debt_type,
                        "primary_debt_apr": primary_debt_apr
                    }
                    
                    # Add investment data if provided
                    if has_investments:
                        profile["current_investments"] = current_investments
                        profile["monthly_investment_contribution"] = monthly_contributions
                        profile["annual_retirement_contribution"] = retirement_contributions
                        profile["investment_strategy"] = investment_strategy
                    
                    # Calculate monthly savings
                    total_expenses = sum([
                        expense_rent, expense_utilities, expense_groceries, expense_dining,
                        expense_transport, expense_healthcare, expense_entertainment, 
                        expense_other, expense_debt
                    ])
                    profile["monthly_savings"] = monthly_income - total_expenses
                    
                    st.session_state.user_profile = profile
                    
                    # Add to profile history
                    st.session_state.profile_history.append(profile)
                    if len(st.session_state.profile_history) > 12:  # Keep last 12 months
                        st.session_state.profile_history.pop(0)
                    
                    st.success("Your financial data has been saved! Go to Analysis to see results.")
                    
                    # Save to database if logged in
                    if st.session_state.user_id:
                        success, message, profile_id = user_db.save_financial_profile(
                            st.session_state.user_id,
                            profile_name,
                            profile
                        )
                        if success:
                            st.info(f"Profile '{profile_name}' saved to your account")
                            
                            # Check for achievement
                            achievement_system.check_app_usage_achievements(
                                st.session_state.user_id,
                                profile_saved=True,
                                simulation_run=st.session_state.simulation_count > 0,
                                login_history=st.session_state.login_history
                            )
        
        elif input_method == "Upload CSV":
            st.info("""
            Upload a CSV file with your financial data. The file should have the following columns:
            - monthly_income
            - current_savings
            - expense_* (for each expense category)
            - total_debt
            - primary_debt_type
            - primary_debt_apr
            """)
            
            uploaded_file = st.file_uploader("Upload your financial data CSV", type="csv")
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    if len(df) > 0:
                        profile = df.iloc[0].to_dict()
                        
                        # Ensure monthly_savings is calculated
                        if 'monthly_savings' not in profile:
                            monthly_income = profile.get('monthly_income', 0)
                            expenses = sum([v for k, v in profile.items() if k.startswith('expense_')])
                            profile['monthly_savings'] = monthly_income - expenses
                        
                        st.session_state.user_profile = profile
                        
                        # Add to profile history
                        st.session_state.profile_history.append(profile)
                        if len(st.session_state.profile_history) > 12:  # Keep last 12 months
                            st.session_state.profile_history.pop(0)
                        
                        st.success("CSV data loaded successfully! Go to Analysis to see results.")
                        
                        # Show sample of loaded data
                        st.subheader("Loaded Data Preview")
                        st.write(pd.DataFrame([profile]).T)
                        
                        # Save to database if logged in
                        if st.session_state.user_id:
                            profile_name = st.text_input("Profile Name", "Imported Profile")
                            if st.button("Save to My Account"):
                                success, message, profile_id = user_db.save_financial_profile(
                                    st.session_state.user_id,
                                    profile_name,
                                    profile
                                )
                                if success:
                                    st.info(f"Profile '{profile_name}' saved to your account")
                    else:
                        st.error("Uploaded CSV appears to be empty.")
                except Exception as e:
                    st.error(f"Error loading CSV: {e}")
                    st.write("Please make sure your CSV is properly formatted.")
    
    elif page == "Analysis":
        st.title("Step 2: Financial Health Analysis")
        
        if st.session_state.user_profile is None:
            st.warning("No financial data available. Please go to Data Input first.")
        else:
            # Run analysis if not already done
            if st.session_state.analysis_results is None:
                analyzer = FinancialAnalyzer()
                st.session_state.analysis_results = analyzer.analyze_profile(st.session_state.user_profile)
                
                # Save analysis to database if logged in
                if st.session_state.user_id:
                    profiles = user_db.get_financial_profiles(st.session_state.user_id)
                    if profiles:
                        # Find the most recently updated profile
                        current_profile = max(profiles, key=lambda p: p["updated_at"])
                        user_db.save_analysis_results(current_profile["id"], st.session_state.analysis_results)
            
            results = st.session_state.analysis_results
            
            # Display financial health overview
            st.subheader("Financial Health Overview")
            
            health_color = {
                "Excellent": "green",
                "Good": "lightgreen",
                "Fair": "orange",
                "Poor": "red"
            }
            
            health_score = results["financial_health"]
            st.markdown(f"<h1 style='color: {health_color[health_score]};'>{health_score}</h1>", unsafe_allow_html=True)
            
            # Display issues
            if results["issues"]:
                st.subheader("Identified Issues")
                
                for issue in results["issues"]:
                    severity_color = "red" if issue["severity"] == "high" else "orange"
                    
                    with st.expander(f"🔍 {issue['issue']} ({issue['severity'].upper()})"):
                        st.write(issue["details"])
                        st.markdown(f"**Recommendation:** {issue['recommendation']}")
            else:
                st.success("No financial issues detected. Great job managing your finances!")
            
            # Display action plan
            if results["action_plan"]:
                st.subheader("Recommended Action Plan")
                
                for i, action in enumerate(results["action_plan"], 1):
                    st.write(f"{i}. {action}")
                
                # Button to simulate with recommendations
                if st.button("Simulate with Recommendations"):
                    simulator = FinancialSimulator(st.session_state.user_profile)
                    current, improved, comparison = simulator.compare_scenarios()
                    
                    st.session_state.simulation_results = {
                        "current": current,
                        "improved": improved,
                        "comparison": comparison
                    }
                    
                    # Increment simulation count
                    st.session_state.simulation_count += 1
                    
                    # Check for simulation achievement
                    if st.session_state.user_id:
                        achievement_system.check_app_usage_achievements(
                            st.session_state.user_id,
                            profile_saved=True,
                            simulation_run=True,
                            login_history=st.session_state.login_history
                        )
                    
                    # Save simulation to database if logged in
                    if st.session_state.user_id:
                        profiles = user_db.get_financial_profiles(st.session_state.user_id)
                        if profiles:
                            # Find the most recently updated profile
                            current_profile = max(profiles, key=lambda p: p["updated_at"])
                            user_db.save_simulation_results(current_profile["id"], st.session_state.simulation_results)
                    
                    st.success("Simulation complete! Go to Future Simulation to see results.")
            
            # Financial metrics
            st.subheader("Key Financial Metrics")
            
            # Extract metrics from profile
            profile = st.session_state.user_profile
            income = profile["monthly_income"]
            expenses = sum([v for k, v in profile.items() if k.startswith('expense_')])
            savings = income - expenses
            savings_rate = (savings / income) * 100 if income > 0 else 0
            debt = profile.get("total_debt", 0)
            
            # Create metrics visualization
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Monthly Savings", f"${savings:.2f}", f"{savings_rate:.1f}% of income")
            
            with col2:
                debt_to_income = (debt / (income * 12)) * 100 if income > 0 else 0
                st.metric("Debt-to-Annual-Income Ratio", f"{debt_to_income:.1f}%", 
                          "Good" if debt_to_income < 36 else "High")
            
            with col3:
                expense_ratio = (expenses / income) * 100 if income > 0 else 0
                st.metric("Expense-to-Income Ratio", f"{expense_ratio:.1f}%", 
                         "Low" if expense_ratio < 70 else "High")
            
            # Create a pie chart of expenses
            expense_dict = {k.replace('expense_', '').replace('_', ' ').title(): v 
                          for k, v in profile.items() if k.startswith('expense_') and v > 0}
            
            if expense_dict:
                fig = px.pie(
                    values=list(expense_dict.values()),
                    names=list(expense_dict.keys()),
                    title="Monthly Expenses Breakdown",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig)
            
            # Check for achievements if logged in
            if st.session_state.user_id:
                # Check emergency fund achievements
                emergency_achievements = achievement_system.check_emergency_fund_achievements(
                    profile, st.session_state.user_id)
                
                # Check savings rate achievements
                savings_achievements = achievement_system.check_savings_rate_achievements(
                    profile, st.session_state.profile_history, st.session_state.user_id)
                
                # Check debt achievements
                debt_achievements = achievement_system.check_debt_achievements(
                    profile, st.session_state.profile_history, st.session_state.user_id)
                
                # If any new achievements were earned, show a notification
                new_achievements = emergency_achievements + savings_achievements + debt_achievements
                if new_achievements:
                    # Update achievements in session state
                    st.session_state.user_achievements = user_db.get_user_achievements(st.session_state.user_id)
                    
                    st.success(f"You've earned {len(new_achievements)} new achievement(s)! Check the Achievements page.")
    
    elif page == "Future Simulation":
        st.title("Step 3: Financial Future Simulation")
        
        if st.session_state.user_profile is None:
            st.warning("No financial data available. Please go to Data Input first.")
        else:
            # Check if we already have simulation results
            if st.session_state.simulation_results is None:
                simulator = FinancialSimulator(st.session_state.user_profile)
                current, improved, comparison = simulator.compare_scenarios()
                
                st.session_state.simulation_results = {
                    "current": current,
                    "improved": improved,
                    "comparison": comparison
                }
                
                # Increment simulation count
                st.session_state.simulation_count += 1
                
                # Check for simulation achievement
                if st.session_state.user_id:
                    achievement_system.check_app_usage_achievements(
                        st.session_state.user_id,
                        profile_saved=True,
                        simulation_run=True,
                        login_history=st.session_state.login_history
                    )
                
                # Save simulation to database if logged in
                if st.session_state.user_id:
                    profiles = user_db.get_financial_profiles(st.session_state.user_id)
                    if profiles:
                        # Find the most recently updated profile
                        current_profile = max(profiles, key=lambda p: p["updated_at"])
                        user_db.save_simulation_results(current_profile["id"], st.session_state.simulation_results)
            
            results = st.session_state.simulation_results
            current = results["current"]
            improved = results["improved"]
            comparison = results["comparison"]
            
            # Display comparison summary
            st.subheader("5-Year Financial Outlook")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Current Path")
                st.metric(
                    "Net Worth in 5 Years", 
                    f"${comparison['current_path']['final_net_worth']:,.2f}",
                    f"${comparison['current_path']['final_net_worth'] - (st.session_state.user_profile['current_savings'] - st.session_state.user_profile.get('total_debt', 0)):,.2f}"
                )
                st.metric("Final Savings", f"${comparison['current_path']['final_savings']:,.2f}")
                st.metric("Final Debt", f"${comparison['current_path']['final_debt']:,.2f}")
                
                if 'debt_free_date' in comparison['current_path']:
                    debt_free = comparison['current_path']['debt_free_date'].strftime('%B %Y')
                    st.success(f"Debt-free by {debt_free}")
            
            with col2:
                st.markdown("### Improved Path")
                st.metric(
                    "Net Worth in 5 Years", 
                    f"${comparison['improved_path']['final_net_worth']:,.2f}",
                    f"+${comparison['difference']['net_worth_diff']:,.2f} compared to current path"
                )
                st.metric("Final Savings", f"${comparison['improved_path']['final_savings']:,.2f}")
                st.metric("Final Debt", f"${comparison['improved_path']['final_debt']:,.2f}")
                
                if 'debt_free_date' in comparison['improved_path']:
                    debt_free = comparison['improved_path']['debt_free_date'].strftime('%B %Y')
                    st.success(f"Debt-free by {debt_free}")
            
            # Visualization of net worth over time
            st.subheader("Net Worth Projection")
            
            # Format dates for display
            current_dates = [d.strftime('%b %Y') for d in current['date']]
            
            # Create net worth chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=current_dates,
                y=current['net_worth'],
                mode='lines',
                name='Current Path',
                line=dict(color='#1f77b4', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=current_dates,
                y=improved['net_worth'],
                mode='lines',
                name='Improved Path',
                line=dict(color='#2ca02c', width=2)
            ))
            
            fig.update_layout(
                title="Net Worth Over Time",
                xaxis_title="Date",
                yaxis_title="Net Worth ($)",
                legend_title="Scenario",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig)
            
            # Show savings vs. debt charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Savings chart
                fig_savings = go.Figure()
                
                fig_savings.add_trace(go.Scatter(
                    x=current_dates,
                    y=current['savings'],
                    mode='lines',
                    name='Current Path',
                    line=dict(color='#1f77b4', width=2)
                ))
                
                fig_savings.add_trace(go.Scatter(
                    x=current_dates,
                    y=improved['savings'],
                    mode='lines',
                    name='Improved Path',
                    line=dict(color='#2ca02c', width=2)
                ))
                
                fig_savings.update_layout(
                    title="Savings Growth",
                    xaxis_title="Date",
                    yaxis_title="Savings ($)",
                    legend_title="Scenario",
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig_savings)
            
            with col2:
                # Debt chart
                fig_debt = go.Figure()
                
                fig_debt.add_trace(go.Scatter(
                    x=current_dates,
                    y=current['debt'],
                    mode='lines',
                    name='Current Path',
                    line=dict(color='#1f77b4', width=2)
                ))
                
                fig_debt.add_trace(go.Scatter(
                    x=current_dates,
                    y=improved['debt'],
                    mode='lines',
                    name='Improved Path',
                    line=dict(color='#2ca02c', width=2)
                ))
                
                fig_debt.update_layout(
                    title="Debt Reduction",
                    xaxis_title="Date",
                    yaxis_title="Debt ($)",
                    legend_title="Scenario",
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig_debt)
            
            # Impact of changes
            st.subheader("Impact of Recommended Changes")
            
            impact_data = {
                "Metric": ["Net Worth", "Savings", "Debt Reduction"],
                "Improvement": [
                    comparison['difference']['net_worth_diff'],
                    comparison['difference']['savings_diff'],
                    comparison['difference']['debt_diff']
                ]
            }
            
            impact_df = pd.DataFrame(impact_data)
            
            fig_impact = px.bar(
                impact_df,
                x="Metric",
                y="Improvement",
                title="5-Year Financial Improvement ($)",
                color="Metric",
                text_auto='.2s'
            )
            
            fig_impact.update_layout(
                xaxis_title="",
                yaxis_title="Improvement ($)",
                showlegend=False
            )
            
            st.plotly_chart(fig_impact)
            
            # Show specific tips
            if st.session_state.analysis_results and st.session_state.analysis_results["action_plan"]:
                st.subheader("Key Actions for Improvement")
                
                for i, action in enumerate(st.session_state.analysis_results["action_plan"], 1):
                    st.write(f"{i}. {action}")
            
            # Export options
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="Download Simulation Results (CSV)",
                    data=current.to_csv(index=False),
                    file_name="financial_simulation.csv",
                    mime="text/csv"
                )
            
            with col2:
                if st.button("Generate PDF Report"):
                    # Generate PDF report
                    report_generator = FinancialReportGenerator()
                    
                    # Set up tax analysis if not already done
                    if st.session_state.tax_analysis is None:
                        # Calculate tax impact
                        annual_income = st.session_state.user_profile.get('monthly_income', 0) * 12
                        tax_calculator = TaxCalculator()
                        tax_analysis = tax_calculator.calculate_monthly_take_home_pay(annual_income)
                        st.session_state.tax_analysis = tax_analysis
                    
                    # Set up investment profile if not already done
                    investment_profile = None
                    if st.session_state.investment_results is None:
                        # Create basic investment profile
                        investment_simulator = InvestmentSimulator(st.session_state.user_profile)
                        recommended_profile = investment_simulator.recommend_risk_profile(st.session_state.user_profile)
                        
                        investment_profile = {
                            "recommended_profile": recommended_profile,
                            "profile_description": "This investment profile is based on your age, risk tolerance, and financial situation."
                        }
                    else:
                        investment_profile = st.session_state.investment_results
                    
                    # Generate the report
                    output_file = report_generator.generate_financial_report(
                        st.session_state.user_profile,
                        st.session_state.analysis_results,
                        st.session_state.simulation_results,
                        investment_profile,
                        st.session_state.tax_analysis
                    )
                    
                    # Create download link
                    st.markdown(get_pdf_download_link(output_file), unsafe_allow_html=True)
    
    elif page == "Investment Planner":
        st.title("Investment Strategy Planner")
        
        if st.session_state.user_profile is None:
            st.warning("No financial data available. Please go to Data Input first.")
        else:
            profile = st.session_state.user_profile
            
            # Initialize investment simulator
            investment_simulator = InvestmentSimulator(profile)
            
            # Get recommended risk profile
            recommended_profile = investment_simulator.recommend_risk_profile(profile)
            
            st.subheader("Investment Recommendation")
            
            # Display recommended risk profile
            risk_profile_names = {
                "very_conservative": "Very Conservative",
                "conservative": "Conservative",
                "moderate": "Moderate",
                "aggressive": "Aggressive",
                "very_aggressive": "Very Aggressive"
            }
            
            recommended_name = risk_profile_names.get(recommended_profile, recommended_profile.replace("_", " ").title())

            st.markdown(f"### Based on your profile, we recommend a **{recommended_name}** investment strategy.")
            
            # Risk profile descriptions
            risk_descriptions = {
                "very_conservative": "This strategy prioritizes capital preservation with minimal risk. It's suitable for those close to retirement or with a very low risk tolerance.",
                "conservative": "This strategy focuses on stability with some growth potential. It's suitable for those who want to protect their capital but also achieve modest growth.",
                "moderate": "This balanced strategy aims for growth while managing volatility. It's suitable for those with a medium-term investment horizon (5-10 years).",
                "aggressive": "This strategy prioritizes growth with higher volatility. It's suitable for those with a long-term investment horizon who can tolerate market fluctuations.",
                "very_aggressive": "This strategy maximizes growth potential with significant volatility. It's suitable for young investors with a very long-term horizon who can tolerate substantial market fluctuations."
            }
            
            st.write(risk_descriptions.get(recommended_profile, ""))
            
            # Show why this recommendation was made
            st.subheader("Factors Influencing This Recommendation")
            
            factors = []
            
            # Age factor
            age = profile.get('age', 35)
            if age < 30:
                factors.append("You're young and have time to weather market volatility")
            elif age < 45:
                factors.append("You're in your prime earning years with time to grow investments")
            elif age < 60:
                factors.append("You're approaching retirement planning stage")
            else:
                factors.append("You're near or in retirement, requiring more capital preservation")
            
            # Risk tolerance factor
            risk_tolerance = profile.get('risk_tolerance', 'Medium')
            factors.append(f"You've indicated a {risk_tolerance} risk tolerance")
            
            # Emergency fund factor
            monthly_expenses = sum([v for k, v in profile.items() if k.startswith('expense_')])
            current_savings = profile.get('current_savings', 0)
            if monthly_expenses > 0:
                months_saved = current_savings / monthly_expenses
                if months_saved < 3:
                    factors.append("Your emergency fund is below the recommended 3-6 months")
                elif months_saved >= 6:
                    factors.append("You have a solid emergency fund (6+ months)")
                else:
                    factors.append("Your emergency fund is adequate (3-6 months)")
            
            # Debt factor
            total_debt = profile.get('total_debt', 0)
            if total_debt > 0:
                debt_apr = profile.get('primary_debt_apr', 0)
                if debt_apr > 8:
                    factors.append(f"You have high-interest debt ({debt_apr}% APR) that should be prioritized")
                else:
                    factors.append(f"You have manageable low-interest debt ({debt_apr}% APR)")
            else:
                factors.append("You're debt-free, which allows for more aggressive investing")
            
            # Display factors
            for factor in factors:
                st.write(f"• {factor}")
            
            # Show asset allocation
            st.subheader("Recommended Asset Allocation")
            
            # Get allocation for the recommended profile
            asset_classes = {
                "savings_account": "Savings Account",
                "bonds": "Bonds",
                "index_funds": "Index Funds",
                "stocks": "Stocks",
                "crypto": "Crypto"
            }
            
            allocation = investment_simulator.risk_profiles.get(recommended_profile, {})
            
            # Create allocation chart
            allocation_data = []
            for asset_code, percentage in allocation.items():
                if percentage > 0:
                    allocation_data.append({
                        "Asset": asset_classes.get(asset_code, asset_code),
                        "Percentage": percentage * 100
                    })
            
            if allocation_data:
                allocation_df = pd.DataFrame(allocation_data)
                fig = px.pie(
                    allocation_df,
                    values="Percentage",
                    names="Asset",
                    title=f"Asset Allocation - {recommended_name} Profile",
                    hole=0.4
                )
                st.plotly_chart(fig)
            
            # Simulation options
            st.subheader("Investment Growth Simulation")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_profile = st.selectbox(
                    "Select Risk Profile", 
                    list(risk_profile_names.keys()),
                    index=list(risk_profile_names.keys()).index(recommended_profile) if recommended_profile in risk_profile_names else 2
                )
            
            with col2:
                monthly_contribution = st.number_input(
                    "Monthly Contribution ($)",
                    min_value=0.0,
                    value=max(profile.get('monthly_savings', 0) * 0.5, 100),
                    step=25.0
                )
            
            with col3:
                initial_investment = st.number_input(
                    "Initial Investment ($)",
                    min_value=0.0,
                    value=float(profile.get('current_investments', 0.0)),  # Convert to float
                    step=1000.0
                )

            
            simulation_years = st.slider("Simulation Years", 1, 30, 10)
            
            if st.button("Run Investment Simulation"):
                # Run simulations for different risk profiles
                profile_results, summary = investment_simulator.compare_risk_profiles(
                    monthly_contribution=monthly_contribution,
                    initial_investment=initial_investment
                )
                
                # Store selected profile simulation in session state
                selected_data = profile_results.get(selected_profile)
                
                if selected_data is not None:
                    # Store investment results
                    st.session_state.investment_results = {
                        "recommended_profile": recommended_profile,
                        "selected_profile": selected_profile,
                        "monthly_contribution": monthly_contribution,
                        "initial_investment": initial_investment,
                        "simulation_years": simulation_years,
                        "final_value": summary[selected_profile]["final_value"],
                        "total_growth": summary[selected_profile]["total_growth"],
                        "cagr": summary[selected_profile]["cagr"],
                        "max_drawdown": summary[selected_profile]["max_drawdown"],
                        "allocation": investment_simulator.risk_profiles.get(selected_profile, {})
                    }
                    
                    # Display results
                    st.subheader(f"Projected Investment Growth ({risk_profile_names[selected_profile]} Profile)")
                    
                    # Create growth chart
                    fig = go.Figure()
                    
                    dates = [d.strftime('%Y-%m') for d in selected_data['date']]
                    
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=selected_data['total_value'],
                        mode='lines',
                        name='Portfolio Value',
                        line=dict(color='#1f77b4', width=2)
                    ))
                    
                    # Add contribution line (cumulative)
                    contributions = [initial_investment + monthly_contribution * i for i in range(len(dates))]
                    
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=contributions,
                        mode='lines',
                        name='Total Contributions',
                        line=dict(color='#7f7f7f', width=2, dash='dash')
                    ))
                    
                    fig.update_layout(
                        title=f"Investment Growth Over {simulation_years} Years",
                        xaxis_title="Date",
                        yaxis_title="Value ($)",
                        legend_title="",
                        hovermode="x unified"
                    )
                    
                    st.plotly_chart(fig)
                    
                    # Display summary statistics
                    st.subheader("Investment Summary")
                    
                    stats = summary[selected_profile]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            "Final Portfolio Value", 
                            f"${stats['final_value']:,.2f}",
                            f"+${stats['total_growth']:,.2f}"
                        )
                        st.metric(
                            "Total Contributions", 
                            f"${stats['total_contributions'] + stats['initial_investment']:,.2f}"
                        )
                    
                    with col2:
                        st.metric(
                            "Compound Annual Growth Rate", 
                            f"{stats['cagr']:.2f}%"
                        )
                        st.metric(
                            "Maximum Drawdown", 
                            f"{abs(stats['max_drawdown']):.2f}%"
                        )
                    
                    # Compare different risk profiles
                    st.subheader("Risk Profile Comparison")
                    
                    comparison_data = []
                    for profile_name, profile_stats in summary.items():
                        comparison_data.append({
                            "Risk Profile": risk_profile_names[profile_name],
                            "Final Value": profile_stats["final_value"],
                            "CAGR": profile_stats["cagr"],
                            "Max Drawdown": abs(profile_stats["max_drawdown"])
                        })
                    
                    comparison_df = pd.DataFrame(comparison_data)
                    
                    # Display comparison bar chart
                    fig = px.bar(
                        comparison_df,
                        x="Risk Profile",
                        y="Final Value",
                        color="Risk Profile",
                        title="Final Value by Risk Profile",
                        text_auto='.2s'
                    )
                    
                    fig.update_layout(
                        xaxis_title="",
                        yaxis_title="Final Value ($)",
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig)
                    
                    # Display comparison table
                    st.write(comparison_df.style.format({
                        "Final Value": "${:,.2f}",
                        "CAGR": "{:.2f}%",
                        "Max Drawdown": "{:.2f}%"
                    }))
                    
                    # Investment tips based on selected profile
                    st.subheader("Investment Tips")
                    
                    tips = {
                        "very_conservative": [
                            "Focus on high-yield savings accounts and CDs for stability",
                            "Consider short-term government bonds for slightly higher yields with minimal risk",
                            "Maintain adequate liquidity for emergency expenses",
                            "Review your allocation annually to ensure it still matches your goals"
                        ],
                        "conservative": [
                            "Consider a mix of bond funds (government and high-quality corporate)",
                            "Add a small allocation to broad market index funds for growth",
                            "Implement dollar-cost averaging to reduce timing risk",
                            "Rebalance your portfolio annually to maintain target allocation"
                        ],
                        "moderate": [
                            "Use index funds for cost-effective diversification",
                            "Balance between growth (stocks) and income (bonds) investments",
                            "Consider target-date funds if you prefer a hands-off approach",
                            "Rebalance your portfolio 1-2 times per year"
                        ],
                        "aggressive": [
                            "Emphasize stock index funds for long-term growth",
                            "Consider international exposure for diversification",
                            "Don't panic sell during market downturns - stick to your strategy",
                            "Maintain a small bond allocation to reduce overall volatility"
                        ],
                        "very_aggressive": [
                            "Focus on high-growth sectors and small-cap stocks for maximum growth potential",
                            "Consider a small allocation to alternative investments like REITs",
                            "Only use this strategy for long-term goals (10+ years)",
                            "Don't invest money you might need in the near future"
                        ]
                    }
                    
                    selected_tips = tips.get(selected_profile, ["Diversify your investments", "Invest regularly", "Focus on low-fee options"])
                    
                    for tip in selected_tips:
                        st.write(f"• {tip}")
                    
                    # Check for investment achievements
                    if st.session_state.user_id:
                        investment_data = {
                            "total_invested": initial_investment + monthly_contribution * 12 * simulation_years,
                            "asset_allocation": investment_simulator.risk_profiles.get(selected_profile, {}),
                            "retirement_investing_years": profile.get("retirement_investing_years", 0)
                        }
                        
                        investment_achievements = achievement_system.check_investment_achievements(
                            profile, investment_data, st.session_state.user_id)
                        
                        if investment_achievements:
                            st.success(f"You've earned {len(investment_achievements)} investment achievement(s)! Check the Achievements page.")
                            
                            # Update achievements in session state
                            st.session_state.user_achievements = user_db.get_user_achievements(st.session_state.user_id)
    
    elif page == "Tax Analysis":
        st.title("Tax Impact Analysis")
        
        if st.session_state.user_profile is None:
            st.warning("No financial data available. Please go to Data Input first.")
        else:
            profile = st.session_state.user_profile
            
            # Extract income information
            monthly_income = profile.get('monthly_income', 0)
            annual_income = monthly_income * 12
            
            st.subheader("Income and Tax Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                annual_income_input = st.number_input(
                    "Annual Gross Income ($)",
                    min_value=0.0,
                    value=float(annual_income),
                    step=1000.0
                )
                
                filing_status = st.selectbox(
                    "Filing Status",
                    ["Single", "Married Filing Jointly", "Married Filing Separately", "Head of Household"]
                )
            
            with col2:
                state_tax_rate = st.slider(
                    "State Income Tax Rate (%)",
                    min_value=0.0,
                    max_value=13.0,
                    value=5.0,
                    step=0.1
                )
                
                retirement_contribution_pct = st.slider(
                    "Retirement Contribution (% of income)",
                    min_value=0.0,
                    max_value=20.0,
                    value=5.0,
                    step=0.5
                )
            
            # Advanced options
            with st.expander("Advanced Tax Options"):
                col1, col2 = st.columns(2)
                
                with col1:
                    other_pretax_deductions = st.number_input(
                        "Other Pre-tax Deductions ($)",
                        min_value=0.0,
                        value=0.0,
                        step=100.0,
                        help="Examples: Health insurance premiums, HSA contributions, FSA contributions"
                    )
                    
                    itemized_deductions = st.number_input(
                        "Itemized Deductions ($)",
                        min_value=0.0,
                        value=0.0,
                        step=500.0,
                        help="Leave at 0 to use standard deduction"
                    )
                
                with col2:
                    has_investments = st.checkbox("I have investment income")
                    
                    investment_income = 0.0
                    capital_gains = 0.0
                    
                    if has_investments:
                        investment_income = st.number_input(
                            "Dividend Income ($)",
                            min_value=0.0,
                            value=0.0,
                            step=100.0
                        )
                        
                        capital_gains = st.number_input(
                            "Capital Gains ($)",
                            min_value=0.0,
                            value=0.0,
                            step=100.0
                        )
            
            # Calculate taxes when button is pressed
            if st.button("Calculate Tax Impact"):
                # Configure tax calculator
                tax_calc = TaxCalculator()
                tax_calc.set_state_tax_rate(state_tax_rate / 100)
                
                # Calculate retirement contribution
                retirement_contribution = annual_income_input * (retirement_contribution_pct / 100)
                
                # Calculate take-home pay
                take_home_results = tax_calc.calculate_monthly_take_home_pay(
                    annual_income_input,
                    retirement_contribution=retirement_contribution,
                    other_pretax_deductions=other_pretax_deductions
                )
                
                # Store in session state
                st.session_state.tax_analysis = take_home_results
                
                # Display results
                st.subheader("Tax Breakdown")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "Annual Gross Income", 
                        f"${annual_income_input:,.2f}"
                    )
                    st.metric(
                        "Federal Income Tax", 
                        f"${take_home_results['federal_income_tax']:,.2f}",
                        f"{take_home_results['federal_income_tax'] / annual_income_input * 100:.1f}% of income"
                    )
                    st.metric(
                        "Social Security", 
                        f"${take_home_results['social_security_tax']:,.2f}",
                        f"{take_home_results['social_security_tax'] / annual_income_input * 100:.1f}% of income"
                    )
                    st.metric(
                        "Medicare", 
                        f"${take_home_results['medicare_tax']:,.2f}",
                        f"{take_home_results['medicare_tax'] / annual_income_input * 100:.1f}% of income"
                    )
                
                with col2:
                    st.metric(
                        "State Income Tax", 
                        f"${take_home_results['state_income_tax']:,.2f}",
                        f"{take_home_results['state_income_tax'] / annual_income_input * 100:.1f}% of income"
                    )
                    st.metric(
                        "Retirement Contribution", 
                        f"${retirement_contribution:,.2f}",
                        f"{retirement_contribution_pct:.1f}% of income"
                    )
                    st.metric(
                        "Total Tax Burden", 
                        f"${take_home_results['total_tax']:,.2f}",
                        f"{take_home_results['effective_tax_rate'] * 100:.1f}% effective rate"
                    )
                    st.metric(
                        "Monthly Take-Home Pay", 
                        f"${take_home_results['monthly_take_home']:,.2f}"
                    )
                
                # Create pie chart of income distribution
                income_distribution = [
                    {"Category": "Take-Home Pay", "Amount": take_home_results['annual_take_home']},
                    {"Category": "Federal Tax", "Amount": take_home_results['federal_income_tax']},
                    {"Category": "FICA Taxes", "Amount": take_home_results['social_security_tax'] + take_home_results['medicare_tax']},
                    {"Category": "State Tax", "Amount": take_home_results['state_income_tax']},
                    {"Category": "Retirement", "Amount": retirement_contribution}
                ]
                
                income_df = pd.DataFrame(income_distribution)
                
                fig = px.pie(
                    income_df,
                    values="Amount",
                    names="Category",
                    title="Annual Income Distribution",
                    hole=0.4
                )
                
                st.plotly_chart(fig)
                
                # Tax saving opportunities
                st.subheader("Tax Saving Opportunities")
                
                # Calculate traditional retirement account savings
                retirement_tax_savings = tax_calc.calculate_retirement_contribution_tax_savings(
                    annual_income_input, retirement_contribution)
                
                st.write(f"By contributing ${retirement_contribution:,.2f} to a traditional retirement account, you save ${retirement_tax_savings['current_year_tax_savings']:,.2f} in taxes this year.")
                
                # Calculate long-term impact
                st.subheader("Long-Term Tax Impact")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    projection_years = st.slider("Projection Years", 1, 30, 10)
                
                with col2:
                    income_growth = st.slider("Annual Income Growth (%)", 0.0, 10.0, 3.0, 0.1)
                
                # Run tax impact simulation
                tax_simulation = tax_calc.simulate_tax_impact_on_financial_path(
                    annual_income=annual_income_input,
                    yearly_income_growth=income_growth / 100,
                    retirement_contribution_percent=retirement_contribution_pct / 100,
                    years=projection_years,
                    investment_return_rate=0.07,
                    initial_investment=profile.get('current_investments', 0)
                )
                
                # Display tax impact over time
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=tax_simulation['year'],
                    y=tax_simulation['federal_tax'],
                    mode='lines+markers',
                    name='Federal Tax',
                    line=dict(color='#ef553b', width=2)
                ))
                
                fig.add_trace(go.Scatter(
                    x=tax_simulation['year'],
                    y=tax_simulation['state_tax'],
                    mode='lines+markers',
                    name='State Tax',
                    line=dict(color='#636efa', width=2)
                ))
                
                fig.add_trace(go.Scatter(
                    x=tax_simulation['year'],
                    y=tax_simulation['fica_tax'],
                    mode='lines+markers',
                    name='FICA Taxes',
                    line=dict(color='#00cc96', width=2)
                ))
                
                fig.update_layout(
                    title="Tax Projection Over Time",
                    xaxis_title="Year",
                    yaxis_title="Annual Tax Amount ($)",
                    legend_title="Tax Type",
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig)
                
                # Show investment growth with tax implications
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=tax_simulation['year'],
                    y=tax_simulation['tax_advantaged_value'],
                    mode='lines',
                    name='Tax-Advantaged Investments',
                    line=dict(color='#2ca02c', width=2)
                ))
                
                fig.add_trace(go.Scatter(
                    x=tax_simulation['year'],
                    y=tax_simulation['taxable_investment_value'],
                    mode='lines',
                    name='Taxable Investments',
                    line=dict(color='#1f77b4', width=2)
                ))
                
                fig.update_layout(
                    title="Investment Growth With Tax Implications",
                    xaxis_title="Year",
                    yaxis_title="Value ($)",
                    legend_title="",
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig)
                
                # Tax optimization tips
                st.subheader("Tax Optimization Tips")
                
                tax_tips = [
                    "**Maximize tax-advantaged accounts** like 401(k)s, IRAs, and HSAs to reduce taxable income.",
                    "**Consider Roth vs. Traditional** retirement accounts based on your current and expected future tax brackets.",
                    "**Tax-loss harvesting** can offset capital gains with losses in taxable investment accounts.",
                    "**Hold tax-efficient investments** like index funds and ETFs in taxable accounts.",
                    "**Consider municipal bonds** for tax-free income if you're in a high tax bracket.",
                    "**Bunching itemized deductions** in alternate years may help exceed the standard deduction threshold.",
                    "**Review your W-4 withholding** to ensure you're not over or under-withholding."
                ]
                
                for tip in tax_tips:
                    st.markdown(f"• {tip}")
                
                # Check for tax achievements
                if st.session_state.user_id:
                    tax_data = {
                        "tax_advantaged_contributions": retirement_contribution,
                        "tax_loss_harvesting": False,
                        "backdoor_roth": False,
                        "mega_backdoor_roth": False,
                        "hsa_contributions": 0
                    }
                    
                    tax_achievements = achievement_system.check_tax_achievements(
                        profile, tax_data, st.session_state.user_id)
                    
                    if tax_achievements:
                        st.success(f"You've earned {len(tax_achievements)} tax optimization achievement(s)! Check the Achievements page.")
                        
                        # Update achievements in session state
                        st.session_state.user_achievements = user_db.get_user_achievements(st.session_state.user_id)
    
    elif page == "Achievements":
        st.title("Financial Achievements")
        
        if not st.session_state.user_id:
            st.warning("Please log in to track achievements.")
        else:
            # Get latest achievements
            achievements = user_db.get_user_achievements(st.session_state.user_id)
            st.session_state.user_achievements = achievements
            
            # Group achievements by level
            achievement_levels = {
                "bronze": [],
                "silver": [],
                "gold": [],
                "platinum": []
            }
            
            for achievement in achievements:
                level = achievement["data"].get("level", "bronze")
                achievement_levels[level].append(achievement)
            
            # Count achievements by level
            level_counts = {level: len(achievements) for level, achievements in achievement_levels.items()}
            total_achievements = sum(level_counts.values())
            
            # Show achievement progress
            st.subheader("Achievement Progress")
            
            # Get all possible achievements
            all_achievement_defs = achievement_system.get_all_achievement_definitions()
            total_possible = len(all_achievement_defs)
            
            # Get counts by level
            bronze_possible = len([a for a in all_achievement_defs.values() if a.get("level") == "bronze"])
            silver_possible = len([a for a in all_achievement_defs.values() if a.get("level") == "silver"])
            gold_possible = len([a for a in all_achievement_defs.values() if a.get("level") == "gold"])
            platinum_possible = len([a for a in all_achievement_defs.values() if a.get("level") == "platinum"])
            
            # Create progress bars
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Bronze", f"{level_counts['bronze']}/{bronze_possible}")
                st.progress(level_counts['bronze'] / bronze_possible if bronze_possible > 0 else 0)
            
            with col2:
                st.metric("Silver", f"{level_counts['silver']}/{silver_possible}")
                st.progress(level_counts['silver'] / silver_possible if silver_possible > 0 else 0)
            
            with col3:
                st.metric("Gold", f"{level_counts['gold']}/{gold_possible}")
                st.progress(level_counts['gold'] / gold_possible if gold_possible > 0 else 0)
            
            with col4:
                st.metric("Platinum", f"{level_counts['platinum']}/{platinum_possible}")
                st.progress(level_counts['platinum'] / platinum_possible if platinum_possible > 0 else 0)
            
            # Overall progress
            st.metric("Overall Achievement Progress", f"{total_achievements}/{total_possible}")
            st.progress(total_achievements / total_possible if total_possible > 0 else 0)
            
            # Achievement display by level
            st.subheader("Your Achievements")
            
            # Display platinum achievements first (if any)
            if achievement_levels["platinum"]:
                st.markdown("### 🏆 Platinum Achievements")
                
                for achievement in achievement_levels["platinum"]:
                    with st.expander(f"🏆 {achievement['data']['title']}"):
                        st.write(achievement["data"]["description"])
                        st.info(f"Achieved on: {achievement['achieved_at'][:10]}")
            
            # Display gold achievements
            if achievement_levels["gold"]:
                st.markdown("### 🥇 Gold Achievements")
                
                achievement_cols = st.columns(3)
                col_idx = 0
                
                for achievement in achievement_levels["gold"]:
                    with achievement_cols[col_idx]:
                        st.markdown(f"#### 🥇 {achievement['data']['title']}")
                        st.write(achievement["data"]["description"])
                        st.info(f"Achieved on: {achievement['achieved_at'][:10]}")
                    
                    col_idx = (col_idx + 1) % 3
            
            # Display silver achievements
            if achievement_levels["silver"]:
                st.markdown("### 🥈 Silver Achievements")
                
                achievement_cols = st.columns(3)
                col_idx = 0
                
                for achievement in achievement_levels["silver"]:
                    with achievement_cols[col_idx]:
                        st.markdown(f"#### 🥈 {achievement['data']['title']}")
                        st.write(achievement["data"]["description"])
                        st.info(f"Achieved on: {achievement['achieved_at'][:10]}")
                    
                    col_idx = (col_idx + 1) % 3
            
            # Display bronze achievements
            if achievement_levels["bronze"]:
                st.markdown("### 🥉 Bronze Achievements")
                
                achievement_cols = st.columns(3)
                col_idx = 0
                
                for achievement in achievement_levels["bronze"]:
                    with achievement_cols[col_idx]:
                        st.markdown(f"#### 🥉 {achievement['data']['title']}")
                        st.write(achievement["data"]["description"])
                        st.info(f"Achieved on: {achievement['achieved_at'][:10]}")
                    
                    col_idx = (col_idx + 1) % 3
            
            # Available achievements
            with st.expander("Available Achievements"):
                st.write("Complete these financial milestones to earn more achievements:")
                
                # Get earned achievement IDs
                earned_ids = [a["type"] for a in achievements]
                
                # Show unearned achievements grouped by category
                categories = {
                    "Emergency Fund": ["emergency_starter", "emergency_builder", "emergency_master"],
                    "Debt Reduction": ["debt_tackler", "debt_crusher", "debt_eliminator"],
                    "Savings Rate": ["savings_starter", "savings_builder", "super_saver"],
                    "Financial Planning": ["planner_novice", "planner_adept", "master_planner"],
                    "Investing": ["investor_starter", "investor_builder", "investor_master"],
                    "Tax Optimization": ["tax_aware", "tax_optimizer", "tax_master"],
                    "App Usage": ["first_simulation", "profile_creator", "consistent_user"],
                    "Master Achievement": ["financial_master"]
                }
                
                for category, achievement_ids in categories.items():
                    # Filter to unearned achievements
                    unearned = [a_id for a_id in achievement_ids if a_id not in earned_ids]
                    
                    if unearned:
                        st.markdown(f"**{category}**")
                        
                        for a_id in unearned:
                            definition = achievement_system.get_achievement_definition(a_id)
                            if definition:
                                level_emoji = "🥉" if definition["level"] == "bronze" else "🥈" if definition["level"] == "silver" else "🥇" if definition["level"] == "gold" else "🏆"
                                st.write(f"{level_emoji} **{definition['title']}**: {definition['description']}")
    
    elif page == "Reports":
        st.title("Financial Reports")
        
        if st.session_state.user_profile is None:
            st.warning("No financial data available. Please go to Data Input first.")
        else:
            st.subheader("Generate Custom Financial Report")
            
            # Report options
            include_investment = st.checkbox("Include Investment Analysis", value=True)
            include_tax = st.checkbox("Include Tax Analysis", value=True)
            include_recommendations = st.checkbox("Include Detailed Recommendations", value=True)
            
            if st.button("Generate PDF Report"):
                # Generate PDF report
                report_generator = FinancialReportGenerator()
                
                # Check if we have all necessary data
                if st.session_state.analysis_results is None:
                    analyzer = FinancialAnalyzer()
                    st.session_state.analysis_results = analyzer.analyze_profile(st.session_state.user_profile)
                
                if st.session_state.simulation_results is None:
                    simulator = FinancialSimulator(st.session_state.user_profile)
                    current, improved, comparison = simulator.compare_scenarios()
                    st.session_state.simulation_results = {
                        "current": current,
                        "improved": improved,
                        "comparison": comparison
                    }
                
                # Tax analysis
                tax_analysis = None
                if include_tax:
                    if st.session_state.tax_analysis is None:
                        # Calculate tax impact
                        annual_income = st.session_state.user_profile.get('monthly_income', 0) * 12
                        tax_calculator = TaxCalculator()
                        tax_analysis = tax_calculator.calculate_monthly_take_home_pay(annual_income)
                    else:
                        tax_analysis = st.session_state.tax_analysis
                
                # Investment profile
                investment_profile = None
                if include_investment:
                    if st.session_state.investment_results is None:
                        # Create basic investment profile
                        investment_simulator = InvestmentSimulator(st.session_state.user_profile)
                        recommended_profile = investment_simulator.recommend_risk_profile(st.session_state.user_profile)
                        
                        investment_profile = {
                            "recommended_profile": recommended_profile,
                            "profile_description": "This investment profile is based on your age, risk tolerance, and financial situation."
                        }
                    else:
                        investment_profile = st.session_state.investment_results
                
                # Generate the report
                output_file = report_generator.generate_financial_report(
                    st.session_state.user_profile,
                    st.session_state.analysis_results,
                    st.session_state.simulation_results,
                    investment_profile if include_investment else None,
                    tax_analysis if include_tax else None
                )
                
                # Create download link
                st.markdown(get_pdf_download_link(output_file), unsafe_allow_html=True)
                
                # Show success message
                st.success("Report generated successfully! Click the link above to download.")
                
                # Preview
                st.subheader("Report Preview")
                st.write("Your report includes:")
                
                report_sections = [
                    "Financial Health Overview",
                    "Current Financial Metrics",
                    "5-Year Financial Projections",
                    "Recommended Action Plan"
                ]
                
                if include_investment:
                    report_sections.append("Investment Recommendations")
                
                if include_tax:
                    report_sections.append("Tax Impact Analysis")
                
                for section in report_sections:
                    st.write(f"✅ {section}")

# Run the main application
if __name__ == "__main__":
    main()