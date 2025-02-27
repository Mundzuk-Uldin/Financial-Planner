import os
import json
from datetime import datetime, timedelta

class AchievementSystem:
    """
    Manages financial achievements and badges to gamify the financial improvement process.
    """
    
    def __init__(self, user_database=None):
        """
        Initialize the achievement system.
        
        Args:
            user_database: Optional UserDatabase instance for saving achievements
        """
        self.user_database = user_database
        
        # Define achievement categories and their criteria
        self.achievement_definitions = {
            # Savings achievements
            "savings_starter": {
                "title": "Savings Starter",
                "description": "Started saving regularly (saved for 3 consecutive months)",
                "badge": "savings_starter.png",
                "level": "bronze"
            },
            "savings_builder": {
                "title": "Savings Builder",
                "description": "Built a solid savings habit (saved >10% of income for 6 months)",
                "badge": "savings_builder.png",
                "level": "silver"
            },
            "super_saver": {
                "title": "Super Saver",
                "description": "Saved more than 20% of income for a full year",
                "badge": "super_saver.png",
                "level": "gold"
            },
            
            # Emergency fund achievements
            "emergency_starter": {
                "title": "Safety Net Starter",
                "description": "Saved one month of expenses in emergency fund",
                "badge": "emergency_starter.png",
                "level": "bronze"
            },
            "emergency_builder": {
                "title": "Safety Net Builder",
                "description": "Saved three months of expenses in emergency fund",
                "badge": "emergency_builder.png",
                "level": "silver"
            },
            "emergency_master": {
                "title": "Safety Net Master",
                "description": "Saved six months of expenses in emergency fund",
                "badge": "emergency_master.png",
                "level": "gold"
            },
            
            # Debt reduction achievements
            "debt_tackler": {
                "title": "Debt Tackler",
                "description": "Made a plan to tackle high-interest debt",
                "badge": "debt_tackler.png",
                "level": "bronze"
            },
            "debt_crusher": {
                "title": "Debt Crusher",
                "description": "Paid off 50% of high-interest debt",
                "badge": "debt_crusher.png",
                "level": "silver"
            },
            "debt_eliminator": {
                "title": "Debt Eliminator",
                "description": "Became completely free of high-interest debt",
                "badge": "debt_eliminator.png",
                "level": "gold"
            },
            
            # Financial planning achievements
            "planner_novice": {
                "title": "Planning Novice",
                "description": "Created your first financial projection",
                "badge": "planner_novice.png",
                "level": "bronze"
            },
            "planner_adept": {
                "title": "Planning Adept",
                "description": "Revisited and revised your financial plan 3 times",
                "badge": "planner_adept.png",
                "level": "silver"
            },
            "master_planner": {
                "title": "Master Planner",
                "description": "Maintained and followed a financial plan for a full year",
                "badge": "master_planner.png",
                "level": "gold"
            },
            
            # Investment achievements
            "investor_starter": {
                "title": "Investor Starter",
                "description": "Made your first investment",
                "badge": "investor_starter.png",
                "level": "bronze"
            },
            "investor_builder": {
                "title": "Investor Builder",
                "description": "Built a diversified portfolio across multiple asset classes",
                "badge": "investor_builder.png",
                "level": "silver"
            },
            "investor_master": {
                "title": "Investor Master",
                "description": "Consistently invested for retirement for over 2 years",
                "badge": "investor_master.png",
                "level": "gold"
            },
            
            # Tax optimization achievements
            "tax_aware": {
                "title": "Tax Aware",
                "description": "Started using tax-advantaged accounts",
                "badge": "tax_aware.png",
                "level": "bronze"
            },
            "tax_optimizer": {
                "title": "Tax Optimizer",
                "description": "Maximized contributions to retirement accounts",
                "badge": "tax_optimizer.png",
                "level": "silver"
            },
            "tax_master": {
                "title": "Tax Master",
                "description": "Implemented advanced tax optimization strategies",
                "badge": "tax_master.png",
                "level": "gold"
            },
            
            # App usage achievements
            "first_simulation": {
                "title": "Future Explorer",
                "description": "Ran your first financial future simulation",
                "badge": "future_explorer.png",
                "level": "bronze"
            },
            "profile_creator": {
                "title": "Profile Creator",
                "description": "Created and saved your financial profile",
                "badge": "profile_creator.png",
                "level": "bronze"
            },
            "consistent_user": {
                "title": "Consistent User",
                "description": "Used the app at least once a week for a month",
                "badge": "consistent_user.png",
                "level": "silver"
            },
            "financial_master": {
                "title": "Financial Master",
                "description": "Earned all gold-level achievements",
                "badge": "financial_master.png",
                "level": "platinum"
            }
        }
    
    def get_achievement_definition(self, achievement_id):
        """
        Get the definition of an achievement.
        
        Args:
            achievement_id (str): ID of the achievement
            
        Returns:
            dict: Achievement definition or None if not found
        """
        return self.achievement_definitions.get(achievement_id)
    
    def get_all_achievement_definitions(self):
        """
        Get all available achievement definitions.
        
        Returns:
            dict: All achievement definitions
        """
        return self.achievement_definitions
    
    def check_emergency_fund_achievements(self, profile, user_id=None):
        """
        Check if the user has earned any emergency fund achievements.
        
        Args:
            profile (dict): User's financial profile
            user_id (str, optional): User ID for saving achievements
            
        Returns:
            list: Earned achievement IDs
        """
        earned_achievements = []
        
        # Calculate how many months of expenses are in savings
        monthly_expenses = sum([v for k, v in profile.items() if k.startswith('expense_')])
        current_savings = profile.get('current_savings', 0)
        
        if monthly_expenses > 0:
            months_saved = current_savings / monthly_expenses
            
            if months_saved >= 1:
                earned_achievements.append("emergency_starter")
            
            if months_saved >= 3:
                earned_achievements.append("emergency_builder")
            
            if months_saved >= 6:
                earned_achievements.append("emergency_master")
        
        # Save achievements to database if provided
        if user_id and self.user_database:
            for achievement_id in earned_achievements:
                achievement_def = self.achievement_definitions.get(achievement_id)
                if achievement_def:
                    self.user_database.save_achievement(user_id, achievement_id, achievement_def)
        
        return earned_achievements
    
    def check_debt_achievements(self, profile, history=None, user_id=None):
        """
        Check if the user has earned any debt reduction achievements.
        
        Args:
            profile (dict): User's financial profile
            history (list, optional): History of financial profiles
            user_id (str, optional): User ID for saving achievements
            
        Returns:
            list: Earned achievement IDs
        """
        earned_achievements = []
        
        # Check if user has a plan to tackle debt
        has_debt_plan = False
        if history and len(history) > 1:
            # Check if there's a decrease in debt over time
            current_debt = profile.get('total_debt', 0)
            previous_debt = history[0].get('total_debt', 0)
            
            if current_debt < previous_debt and current_debt > 0:
                has_debt_plan = True
        
        # If we don't have history, we can still award the bronze achievement
        # if they have high-interest debt and have created a profile
        elif profile.get('primary_debt_apr', 0) > 10 and profile.get('total_debt', 0) > 0:
            has_debt_plan = True
        
        if has_debt_plan:
            earned_achievements.append("debt_tackler")
        
        # Check for debt reduction
        if history and len(history) > 0:
            first_profile = history[0]
            initial_debt = first_profile.get('total_debt', 0)
            current_debt = profile.get('total_debt', 0)
            
            if initial_debt > 0:
                reduction_percentage = (initial_debt - current_debt) / initial_debt * 100
                
                if reduction_percentage >= 50 and reduction_percentage < 100:
                    earned_achievements.append("debt_crusher")
                
                if reduction_percentage >= 100 or current_debt == 0:
                    earned_achievements.append("debt_eliminator")
        
        # Save achievements to database if provided
        if user_id and self.user_database:
            for achievement_id in earned_achievements:
                achievement_def = self.achievement_definitions.get(achievement_id)
                if achievement_def:
                    self.user_database.save_achievement(user_id, achievement_id, achievement_def)
        
        return earned_achievements
    
    def check_savings_rate_achievements(self, profile, history=None, user_id=None):
        """
        Check if the user has earned any savings rate achievements.
        
        Args:
            profile (dict): User's financial profile
            history (list, optional): History of financial profiles over time
            user_id (str, optional): User ID for saving achievements
            
        Returns:
            list: Earned achievement IDs
        """
        earned_achievements = []
        
        # Calculate savings rate
        monthly_income = profile.get('monthly_income', 0)
        monthly_expenses = sum([v for k, v in profile.items() if k.startswith('expense_')])
        monthly_savings = monthly_income - monthly_expenses
        savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
        
        # If we have history, we can check for consistent savings
        consistent_saving = False
        high_saving_rate = False
        super_saving = False
        
        if history and len(history) >= 3:
            # Check last 3 months for consistent saving
            consistent_months = 0
            high_saving_months = 0
            super_saving_months = 0
            
            for past_profile in history[:3]:  # Most recent 3 profiles
                past_income = past_profile.get('monthly_income', 0)
                past_expenses = sum([v for k, v in past_profile.items() if k.startswith('expense_')])
                past_savings = past_income - past_expenses
                past_rate = (past_savings / past_income * 100) if past_income > 0 else 0
                
                if past_savings > 0:
                    consistent_months += 1
                
                if past_rate >= 10:
                    high_saving_months += 1
                
                if past_rate >= 20:
                    super_saving_months += 1
            
            consistent_saving = consistent_months >= 3
            
            # For silver achievement, need 6 months of >10% savings rate
            if len(history) >= 6 and high_saving_months >= 3:
                # Check the next 3 months
                additional_high_months = 0
                for past_profile in history[3:6]:
                    past_income = past_profile.get('monthly_income', 0)
                    past_expenses = sum([v for k, v in past_profile.items() if k.startswith('expense_')])
                    past_savings = past_income - past_expenses
                    past_rate = (past_savings / past_income * 100) if past_income > 0 else 0
                    
                    if past_rate >= 10:
                        additional_high_months += 1
                
                high_saving_rate = additional_high_months + high_saving_months >= 6
            
            # For gold achievement, need 12 months of >20% savings rate
            if len(history) >= 12 and super_saving_months >= 3:
                # Check the next 9 months
                additional_super_months = 0
                for past_profile in history[3:12]:
                    past_income = past_profile.get('monthly_income', 0)
                    past_expenses = sum([v for k, v in past_profile.items() if k.startswith('expense_')])
                    past_savings = past_income - past_expenses
                    past_rate = (past_savings / past_income * 100) if past_income > 0 else 0
                    
                    if past_rate >= 20:
                        additional_super_months += 1
                
                super_saving = additional_super_months + super_saving_months >= 12
        
        # Award achievements
        if consistent_saving:
            earned_achievements.append("savings_starter")
        
        if high_saving_rate:
            earned_achievements.append("savings_builder")
        
        if super_saving:
            earned_achievements.append("super_saver")
        
        # If we don't have history, we can still reward current good behavior
        if not history:
            if savings_rate > 0:
                earned_achievements.append("savings_starter")
            
            if savings_rate >= 10:
                earned_achievements.append("savings_builder")
            
            if savings_rate >= 20:
                earned_achievements.append("super_saver")
        
        # Save achievements to database if provided
        if user_id and self.user_database:
            for achievement_id in earned_achievements:
                achievement_def = self.achievement_definitions.get(achievement_id)
                if achievement_def:
                    self.user_database.save_achievement(user_id, achievement_id, achievement_def)
        
        return earned_achievements
    
    def check_planning_achievements(self, simulations_run=0, plan_revisions=0, plan_age_days=0, user_id=None):
        """
        Check if the user has earned any financial planning achievements.
        
        Args:
            simulations_run (int): Number of simulations the user has run
            plan_revisions (int): Number of times the user has revised their plan
            plan_age_days (int): Age of the plan in days
            user_id (str, optional): User ID for saving achievements
            
        Returns:
            list: Earned achievement IDs
        """
        earned_achievements = []
        
        # Bronze: Created first financial projection
        if simulations_run >= 1:
            earned_achievements.append("planner_novice")
        
        # Silver: Revised plan 3+ times
        if plan_revisions >= 3:
            earned_achievements.append("planner_adept")
        
        # Gold: Maintained plan for a year
        if plan_age_days >= 365:
            earned_achievements.append("master_planner")
        
        # Save achievements to database if provided
        if user_id and self.user_database:
            for achievement_id in earned_achievements:
                achievement_def = self.achievement_definitions.get(achievement_id)
                if achievement_def:
                    self.user_database.save_achievement(user_id, achievement_id, achievement_def)
        
        return earned_achievements
    
    def check_app_usage_achievements(self, user_id=None, profile_saved=False, simulation_run=False, login_history=None):
        """
        Check if the user has earned any app usage achievements.
        
        Args:
            user_id (str, optional): User ID for saving achievements
            profile_saved (bool): Whether the user has saved a profile
            simulation_run (bool): Whether the user has run a simulation
            login_history (list, optional): History of user logins
            
        Returns:
            list: Earned achievement IDs
        """
        earned_achievements = []
        
        # Bronze: Created and saved financial profile
        if profile_saved:
            earned_achievements.append("profile_creator")
        
        # Bronze: Ran first simulation
        if simulation_run:
            earned_achievements.append("first_simulation")
        
        # Silver: Used app consistently for a month
        if login_history and len(login_history) >= 4:
            # Convert login history to dates
            login_dates = []
            for login_time in login_history:
                if isinstance(login_time, str):
                    try:
                        login_date = datetime.fromisoformat(login_time).date()
                        login_dates.append(login_date)
                    except ValueError:
                        continue
            
            # Check if there's at least one login per week for 4 weeks
            if login_dates:
                login_dates.sort(reverse=True)  # Most recent first
                most_recent = login_dates[0]
                
                # Check each of the past 4 weeks
                consistent_weeks = 0
                for week in range(4):
                    week_start = most_recent - timedelta(days=(week+1)*7)
                    week_end = most_recent - timedelta(days=week*7)
                    
                    # Check if there's at least one login in this week
                    week_logins = [date for date in login_dates if week_start <= date <= week_end]
                    if week_logins:
                        consistent_weeks += 1
                
                if consistent_weeks >= 4:
                    earned_achievements.append("consistent_user")
        
        # Save achievements to database if provided
        if user_id and self.user_database:
            for achievement_id in earned_achievements:
                achievement_def = self.achievement_definitions.get(achievement_id)
                if achievement_def:
                    self.user_database.save_achievement(user_id, achievement_id, achievement_def)
        
        return earned_achievements
    
    def check_investment_achievements(self, profile, investment_data=None, user_id=None):
        """
        Check if the user has earned any investment achievements.
        
        Args:
            profile (dict): User's financial profile
            investment_data (dict, optional): User's investment data
            user_id (str, optional): User ID for saving achievements
            
        Returns:
            list: Earned achievement IDs
        """
        earned_achievements = []
        
        # Check if investment data is available
        if not investment_data:
            return earned_achievements
        
        # Bronze: Made first investment
        has_investments = investment_data.get('total_invested', 0) > 0
        if has_investments:
            earned_achievements.append("investor_starter")
        
        # Silver: Diversified portfolio
        asset_classes = investment_data.get('asset_allocation', {})
        diversified = len(asset_classes) >= 3 and all(allocation > 0.05 for allocation in asset_classes.values())
        if diversified:
            earned_achievements.append("investor_builder")
        
        # Gold: Consistent retirement investing
        retirement_duration = investment_data.get('retirement_investing_years', 0)
        if retirement_duration >= 2:
            earned_achievements.append("investor_master")
        
        # Save achievements to database if provided
        if user_id and self.user_database:
            for achievement_id in earned_achievements:
                achievement_def = self.achievement_definitions.get(achievement_id)
                if achievement_def:
                    self.user_database.save_achievement(user_id, achievement_id, achievement_def)
        
        return earned_achievements
    
    def check_tax_achievements(self, profile, tax_data=None, user_id=None):
        """
        Check if the user has earned any tax optimization achievements.
        
        Args:
            profile (dict): User's financial profile
            tax_data (dict, optional): User's tax data
            user_id (str, optional): User ID for saving achievements
            
        Returns:
            list: Earned achievement IDs
        """
        earned_achievements = []
        
        # Check if tax data is available
        if not tax_data:
            return earned_achievements
        
        # Bronze: Using tax-advantaged accounts
        has_tax_advantaged = tax_data.get('tax_advantaged_contributions', 0) > 0
        if has_tax_advantaged:
            earned_achievements.append("tax_aware")
        
        # Silver: Maximizing retirement contributions
        annual_income = profile.get('monthly_income', 0) * 12
        contribution_limit = 22500  # 401(k) contribution limit for 2023
        contribution_percentage = tax_data.get('tax_advantaged_contributions', 0) / contribution_limit
        if contribution_percentage >= 0.9:  # 90% of limit
            earned_achievements.append("tax_optimizer")
        
        # Gold: Advanced tax strategies
        has_advanced_strategies = (
            tax_data.get('tax_loss_harvesting', False) or
            tax_data.get('backdoor_roth', False) or
            tax_data.get('mega_backdoor_roth', False) or
            tax_data.get('hsa_contributions', 0) > 0
        )
        if has_advanced_strategies:
            earned_achievements.append("tax_master")
        
        # Save achievements to database if provided
        if user_id and self.user_database:
            for achievement_id in earned_achievements:
                achievement_def = self.achievement_definitions.get(achievement_id)
                if achievement_def:
                    self.user_database.save_achievement(user_id, achievement_id, achievement_def)
        
        return earned_achievements
    
    def check_all_achievements(self, profile, user_id=None, **kwargs):
        """
        Check for all possible achievements.
        
        Args:
            profile (dict): User's financial profile
            user_id (str, optional): User ID for saving achievements
            **kwargs: Additional data needed for achievement checks
            
        Returns:
            list: All earned achievement IDs
        """
        all_achievements = []
        
        # Get additional data from kwargs
        history = kwargs.get('history', None)
        investment_data = kwargs.get('investment_data', None)
        tax_data = kwargs.get('tax_data', None)
        simulations_run = kwargs.get('simulations_run', 0)
        plan_revisions = kwargs.get('plan_revisions', 0)
        plan_age_days = kwargs.get('plan_age_days', 0)
        profile_saved = kwargs.get('profile_saved', False)
        simulation_run = kwargs.get('simulation_run', False)
        login_history = kwargs.get('login_history', None)
        
        # Check for each type of achievement
        emergency_achievements = self.check_emergency_fund_achievements(profile, user_id)
        debt_achievements = self.check_debt_achievements(profile, history, user_id)
        savings_achievements = self.check_savings_rate_achievements(profile, history, user_id)
        planning_achievements = self.check_planning_achievements(simulations_run, plan_revisions, plan_age_days, user_id)
        app_achievements = self.check_app_usage_achievements(user_id, profile_saved, simulation_run, login_history)
        investment_achievements = self.check_investment_achievements(profile, investment_data, user_id)
        tax_achievements = self.check_tax_achievements(profile, tax_data, user_id)
        
        # Combine all achievements
        all_achievements.extend(emergency_achievements)
        all_achievements.extend(debt_achievements)
        all_achievements.extend(savings_achievements)
        all_achievements.extend(planning_achievements)
        all_achievements.extend(app_achievements)
        all_achievements.extend(investment_achievements)
        all_achievements.extend(tax_achievements)
        
        # Check for master achievement (all gold level)
        gold_achievements = [
            "emergency_master",
            "debt_eliminator",
            "super_saver",
            "master_planner",
            "investor_master",
            "tax_master"
        ]
        
        if all(achievement in all_achievements for achievement in gold_achievements):
            all_achievements.append("financial_master")
            
            # Save master achievement to database if provided
            if user_id and self.user_database:
                achievement_def = self.achievement_definitions.get("financial_master")
                if achievement_def:
                    self.user_database.save_achievement(user_id, "financial_master", achievement_def)
        
        return all_achievements

# Example usage
if __name__ == "__main__":
    # Create a sample profile
    sample_profile = {
        "monthly_income": 5000,
        "current_savings": 15000,
        "expense_rent_mortgage": 1500,
        "expense_utilities": 200,
        "expense_groceries": 400,
        "expense_dining_out": 300,
        "expense_transportation": 200,
        "total_debt": 5000,
        "primary_debt_type": "Credit Card",
        "primary_debt_apr": 18.0
    }
    
    # Test achievement checking
    achievement_system = AchievementSystem()
    
    emergency_achievements = achievement_system.check_emergency_fund_achievements(sample_profile)
    print("Emergency Fund Achievements:", emergency_achievements)
    
    debt_achievements = achievement_system.check_debt_achievements(sample_profile)
    print("Debt Achievements:", debt_achievements)
    
    savings_achievements = achievement_system.check_savings_rate_achievements(sample_profile)
    print("Savings Achievements:", savings_achievements)
    
    # Get all available achievements
    all_definitions = achievement_system.get_all_achievement_definitions()
    print(f"\nTotal available achievements: {len(all_definitions)}")
    
    # Print bronze level achievements
    bronze_achievements = {k: v for k, v in all_definitions.items() if v.get('level') == 'bronze'}
    print(f"Bronze level achievements: {len(bronze_achievements)}")
    for achievement_id, achievement in bronze_achievements.items():
        print(f"- {achievement['title']}: {achievement['description']}")