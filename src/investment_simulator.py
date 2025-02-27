import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class InvestmentSimulator:
    """
    Simulates different investment strategies and their potential outcomes
    over a specified time period.
    """
    
    def __init__(self, profile, simulation_years=5):
        """Initialize the investment simulator with a user profile and simulation duration."""
        self.profile = profile
        self.simulation_years = simulation_years
        self.months = simulation_years * 12
        self.current_month = datetime.now().replace(day=1)
        
        # Define asset classes and their characteristics
        self.asset_classes = {
            "savings_account": {
                "avg_return": 0.02,      # 2% annual return
                "volatility": 0.002,     # 0.2% standard deviation
                "risk_level": "very_low"
            },
            "bonds": {
                "avg_return": 0.04,      # 4% annual return
                "volatility": 0.05,      # 5% standard deviation
                "risk_level": "low"
            },
            "index_funds": {
                "avg_return": 0.08,      # 8% annual return
                "volatility": 0.15,      # 15% standard deviation
                "risk_level": "medium"
            },
            "stocks": {
                "avg_return": 0.10,      # 10% annual return
                "volatility": 0.20,      # 20% standard deviation
                "risk_level": "high"
            },
            "crypto": {
                "avg_return": 0.15,      # 15% annual return
                "volatility": 0.50,      # 50% standard deviation
                "risk_level": "very_high"
            }
        }
        
        # Define risk profiles with asset allocations
        self.risk_profiles = {
            "very_conservative": {
                "savings_account": 0.70,
                "bonds": 0.30,
                "index_funds": 0.00,
                "stocks": 0.00,
                "crypto": 0.00
            },
            "conservative": {
                "savings_account": 0.40,
                "bonds": 0.40,
                "index_funds": 0.20,
                "stocks": 0.00,
                "crypto": 0.00
            },
            "moderate": {
                "savings_account": 0.20,
                "bonds": 0.30,
                "index_funds": 0.40,
                "stocks": 0.10,
                "crypto": 0.00
            },
            "aggressive": {
                "savings_account": 0.10,
                "bonds": 0.15,
                "index_funds": 0.40,
                "stocks": 0.30,
                "crypto": 0.05
            },
            "very_aggressive": {
                "savings_account": 0.05,
                "bonds": 0.10,
                "index_funds": 0.30,
                "stocks": 0.40,
                "crypto": 0.15
            }
        }
    
    def _generate_monthly_returns(self, asset_class, months):
        """Generate monthly returns for a given asset class with appropriate volatility."""
        asset = self.asset_classes[asset_class]
        annual_return = asset["avg_return"]
        annual_volatility = asset["volatility"]
        
        # Convert annual to monthly metrics
        monthly_return = (1 + annual_return) ** (1/12) - 1
        monthly_volatility = annual_volatility / np.sqrt(12)
        
        # Generate random returns following a normal distribution
        returns = np.random.normal(monthly_return, monthly_volatility, months)
        return returns
    
    def simulate_investment_path(self, risk_profile, monthly_contribution, initial_investment=0):
        """
        Simulate investment growth based on risk profile and contribution amount.
        
        Args:
            risk_profile (str): The risk profile to use ('conservative', 'moderate', 'aggressive', etc.)
            monthly_contribution (float): The amount to invest each month
            initial_investment (float): Starting investment amount
            
        Returns:
            DataFrame: Investment growth by month and asset class
        """
        if risk_profile not in self.risk_profiles:
            raise ValueError(f"Risk profile '{risk_profile}' not recognized")
        
        # Get asset allocation for the chosen risk profile
        allocation = self.risk_profiles[risk_profile]
        
        # Initialize results structure
        results = {
            'date': [],
            'total_value': [],
        }
        
        # Add columns for each asset class
        for asset in allocation.keys():
            if allocation[asset] > 0:
                results[asset] = []
        
        # Generate return series for each asset class
        asset_returns = {}
        for asset in allocation.keys():
            if allocation[asset] > 0:
                asset_returns[asset] = self._generate_monthly_returns(asset, self.months)
        
        # Initialize investment values
        current_values = {}
        for asset, alloc_pct in allocation.items():
            if alloc_pct > 0:
                current_values[asset] = initial_investment * alloc_pct
        
        # Run simulation month by month
        for i in range(self.months):
            current_date = self.current_month + timedelta(days=30*i)
            results['date'].append(current_date)
            
            # Distribute monthly contribution according to allocation
            for asset, alloc_pct in allocation.items():
                if alloc_pct > 0:
                    # Add contribution
                    contribution = monthly_contribution * alloc_pct
                    
                    # Apply return for this month
                    if i < len(asset_returns[asset]):
                        monthly_roi = asset_returns[asset][i]
                        current_values[asset] = current_values[asset] * (1 + monthly_roi) + contribution
                    else:
                        # Fallback if we run out of simulated returns
                        monthly_roi = (1 + self.asset_classes[asset]["avg_return"]) ** (1/12) - 1
                        current_values[asset] = current_values[asset] * (1 + monthly_roi) + contribution
                    
                    # Record asset value
                    results[asset].append(current_values[asset])
            
            # Calculate total portfolio value
            total_value = sum(current_values.values())
            results['total_value'].append(total_value)
        
        return pd.DataFrame(results)
    
    def compare_risk_profiles(self, monthly_contribution, initial_investment=0):
        """
        Compare investment outcomes across different risk profiles.
        
        Returns:
            tuple: (DataFrames for each risk profile, comparison summary)
        """
        profile_results = {}
        summary = {}
        
        for profile in self.risk_profiles.keys():
            results = self.simulate_investment_path(profile, monthly_contribution, initial_investment)
            profile_results[profile] = results
            
            # Calculate summary statistics
            final_value = results['total_value'].iloc[-1]
            total_contributions = monthly_contribution * self.months
            total_invested = initial_investment + total_contributions
            total_growth = final_value - total_invested
            cagr = ((final_value / total_invested) ** (1 / self.simulation_years)) - 1
            
            # Calculate max drawdown
            portfolio_value = results['total_value']
            rolling_max = portfolio_value.cummax()
            drawdown = (portfolio_value - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            summary[profile] = {
                'initial_investment': initial_investment,
                'monthly_contribution': monthly_contribution,
                'total_contributions': total_contributions,
                'final_value': final_value,
                'total_growth': total_growth,
                'growth_percentage': (total_growth / total_invested) * 100,
                'cagr': cagr * 100,  # Convert to percentage
                'max_drawdown': max_drawdown * 100  # Convert to percentage
            }
        
        return profile_results, summary
    
    def recommend_risk_profile(self, user_profile):
        """
        Recommend a risk profile based on user characteristics.
        
        Args:
            user_profile (dict): User's financial profile
            
        Returns:
            str: Recommended risk profile
        """
        # Extract relevant factors
        age = user_profile.get('age', 35)  # Default to 35 if not provided
        years_to_retirement = max(65 - age, 5)  # Assume retirement at 65, min 5 years
        has_emergency_fund = user_profile.get('current_savings', 0) >= sum([v for k, v in user_profile.items() if k.startswith('expense_')]) * 3
        risk_tolerance = user_profile.get('risk_tolerance', 'Medium')
        
        # Score each factor (0-10 scale)
        # Age/Time Horizon: Younger = higher score
        time_score = min(10, years_to_retirement / 4)
        
        # Emergency Fund: Having one = higher score
        emergency_score = 7 if has_emergency_fund else 3
        
        # Stated Risk Tolerance
        risk_score_map = {
            'Low': 3,
            'Medium': 6,
            'High': 9
        }
        risk_score = risk_score_map.get(risk_tolerance, 6)
        
        # Combine scores (weighted average)
        total_score = (time_score * 0.5) + (emergency_score * 0.3) + (risk_score * 0.2)
        
        # Map score to risk profile
        if total_score < 3:
            return "very_conservative"
        elif total_score < 5:
            return "conservative"
        elif total_score < 7:
            return "moderate"
        elif total_score < 8.5:
            return "aggressive"
        else:
            return "very_aggressive"

# Example usage
if __name__ == "__main__":
    # Sample profile for testing
    test_profile = {
        "age": 30,
        "monthly_income": 5000,
        "current_savings": 15000,
        "expense_rent_mortgage": 1500,
        "expense_utilities": 200,
        "expense_groceries": 400,
        "expense_dining_out": 300,
        "expense_transportation": 200,
        "risk_tolerance": "Medium"
    }
    
    simulator = InvestmentSimulator(test_profile, simulation_years=10)
    
    # Test a single risk profile
    moderate_results = simulator.simulate_investment_path("moderate", 500, 10000)
    print(f"Final portfolio value (Moderate): ${moderate_results['total_value'].iloc[-1]:,.2f}")
    
    # Compare across risk profiles
    profile_results, summary = simulator.compare_risk_profiles(500, 10000)
    
    for profile, stats in summary.items():
        print(f"\nRisk Profile: {profile}")
        print(f"Final Value: ${stats['final_value']:,.2f}")
        print(f"Total Growth: ${stats['total_growth']:,.2f} ({stats['growth_percentage']:.2f}%)")
        print(f"CAGR: {stats['cagr']:.2f}%")
        print(f"Max Drawdown: {abs(stats['max_drawdown']):.2f}%")
    
    # Test recommendation engine
    recommended = simulator.recommend_risk_profile(test_profile)
    print(f"\nRecommended Risk Profile: {recommended}")