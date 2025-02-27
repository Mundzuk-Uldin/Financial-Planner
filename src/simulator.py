import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class FinancialSimulator:
    def __init__(self, profile, simulation_years=5):
        """Initialize the simulator with a user profile and simulation duration."""
        self.profile = profile
        self.simulation_years = simulation_years
        self.months = simulation_years * 12
        self.current_month = datetime.now().replace(day=1)
    
    def _calculate_monthly_results(self, scenario, params):
        """Calculate financial metrics for each month in the simulation."""
        results = {
            'date': [],
            'income': [],
            'expenses': [],
            'savings': [],
            'debt': [],
            'net_worth': []
        }
        
        monthly_income = self.profile['monthly_income']
        monthly_expenses = sum([v for k, v in self.profile.items() if k.startswith('expense_')])
        
        # Calculate monthly_savings if not provided
        if 'monthly_savings' in self.profile:
            monthly_savings = self.profile['monthly_savings']
        else:
            monthly_savings = monthly_income - monthly_expenses
            
        current_savings = self.profile['current_savings']
        current_debt = self.profile.get('total_debt', 0)
        
        # Apply scenario adjustments
        if scenario == 'improved':
            # Adjust based on params
            income_growth = params.get('income_growth', 0.02)  # 2% annual income growth
            expense_reduction = params.get('expense_reduction', 0.1)  # 10% expense reduction
            extra_debt_payment = params.get('extra_debt_payment', 0.1) * monthly_income  # 10% of income to extra debt
            
            # Apply immediate changes
            monthly_expenses = monthly_expenses * (1 - expense_reduction)
            monthly_savings = monthly_income - monthly_expenses
            
        else:  # current path
            income_growth = 0.02  # 2% annual income growth
            extra_debt_payment = 0
        
        # Initialize running totals
        total_savings = current_savings
        total_debt = current_debt
        
        # Run simulation month by month
        for i in range(self.months):
            # Apply income growth (annually)
            if i > 0 and i % 12 == 0:
                monthly_income *= (1 + income_growth)
            
            # Calculate date
            current_date = self.current_month + timedelta(days=30*i)
            results['date'].append(current_date)
            
            # Record income
            results['income'].append(monthly_income)
            
            # Record expenses
            results['expenses'].append(monthly_expenses)
            
            # Calculate this month's savings
            this_month_savings = monthly_income - monthly_expenses
            
            # Apply debt payments and interest
            if total_debt > 0:
                # Get weighted average APR
                avg_apr = self.profile.get('primary_debt_apr', 15) / 100
                monthly_interest_rate = avg_apr / 12
                
                # Calculate interest for this month
                interest_amount = total_debt * monthly_interest_rate
                
                # Determine debt payment (minimum + extra)
                min_payment = max(total_debt * 0.02, 25)  # 2% of balance or $25 minimum
                total_payment = min(min_payment + extra_debt_payment, total_debt + interest_amount)
                
                # Apply payment and interest
                total_debt = total_debt + interest_amount - total_payment
                
                # Adjust savings by payment amount
                this_month_savings -= total_payment
            
            # Apply savings interest (simple monthly interest)
            savings_interest_rate = 0.02 / 12  # 2% APY
            interest_earned = total_savings * savings_interest_rate
            total_savings += this_month_savings + interest_earned
            
            # Record savings and debt
            results['savings'].append(total_savings)
            results['debt'].append(max(0, total_debt))
            
            # Calculate net worth
            net_worth = total_savings - max(0, total_debt)
            results['net_worth'].append(net_worth)
    
        return pd.DataFrame(results)
    
    def simulate_current_path(self):
        """Simulate financial future with current behavior."""
        return self._calculate_monthly_results('current', {})
    
    def simulate_improved_path(self, params=None):
        """Simulate financial future with improved behavior."""
        if params is None:
            params = {
                'expense_reduction': 0.1,  # Reduce expenses by 10%
                'income_growth': 0.03,     # Grow income by 3% annually
                'extra_debt_payment': 0.1  # Allocate 10% of income to debt
            }
        
        return self._calculate_monthly_results('improved', params)
    
    def compare_scenarios(self):
        """Compare current path vs. improved path scenarios."""
        current = self.simulate_current_path()
        improved = self.simulate_improved_path()
        
        comparison = {
            'end_date': current['date'].iloc[-1],
            'current_path': {
                'final_savings': current['savings'].iloc[-1],
                'final_debt': current['debt'].iloc[-1],
                'final_net_worth': current['net_worth'].iloc[-1]
            },
            'improved_path': {
                'final_savings': improved['savings'].iloc[-1],
                'final_debt': improved['debt'].iloc[-1],
                'final_net_worth': improved['net_worth'].iloc[-1]
            },
            'difference': {
                'savings_diff': improved['savings'].iloc[-1] - current['savings'].iloc[-1],
                'debt_diff': current['debt'].iloc[-1] - improved['debt'].iloc[-1],
                'net_worth_diff': improved['net_worth'].iloc[-1] - current['net_worth'].iloc[-1]
            }
        }
        
        # Calculate potential financial milestones
        debt_free_month_current = current[current['debt'] <= 0]['date'].min() if (current['debt'] <= 0).any() else None
        debt_free_month_improved = improved[improved['debt'] <= 0]['date'].min() if (improved['debt'] <= 0).any() else None
        
        if debt_free_month_current is not None:
            comparison['current_path']['debt_free_date'] = debt_free_month_current
        
        if debt_free_month_improved is not None:
            comparison['improved_path']['debt_free_date'] = debt_free_month_improved
        
        return current, improved, comparison

# Example usage
if __name__ == "__main__":
    import pandas as pd
    
    # Load sample profile data
    try:
        df = pd.read_csv("data/sample_profiles.csv")
        sample_profile = df.iloc[0].to_dict()
        
        simulator = FinancialSimulator(sample_profile, simulation_years=5)
        current, improved, comparison = simulator.compare_scenarios()
        
        print(f"Final Net Worth (Current Path): ${comparison['current_path']['final_net_worth']:,.2f}")
        print(f"Final Net Worth (Improved Path): ${comparison['improved_path']['final_net_worth']:,.2f}")
        print(f"Difference: ${comparison['difference']['net_worth_diff']:,.2f}")
        
        if 'debt_free_date' in comparison['improved_path']:
            print(f"Debt-free date (Improved Path): {comparison['improved_path']['debt_free_date'].strftime('%B %Y')}")
        
    except FileNotFoundError:
        print("Sample profiles not found. Run data_generator.py first.")