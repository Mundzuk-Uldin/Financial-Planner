# Financial Analyzer Module

import pandas as pd
import numpy as np

class FinancialAnalyzer:
    """A class to analyze financial profiles and provide insights."""
    
    def __init__(self):
        """Initialize the financial analyzer with analysis rules."""
        self.issue_detectors = [
            self._check_emergency_fund,
            self._check_debt_to_income,
            self._check_expense_ratio,
            self._check_savings_rate,
            self._check_high_interest_debt
        ]
    
    def _check_emergency_fund(self, profile):
        """Check if emergency fund is adequate (3-6 months of expenses)."""
        monthly_expenses = sum([v for k, v in profile.items() if k.startswith('expense_')])
        current_savings = profile.get('current_savings', 0)
        min_recommended = monthly_expenses * 3
        
        if current_savings < min_recommended:
            months_saved = round(current_savings / monthly_expenses, 1) if monthly_expenses > 0 else 0
            return {
                "issue": "Insufficient emergency fund",
                "severity": "high" if months_saved < 1 else "medium",
                "details": f"Current savings cover only {months_saved} months of expenses instead of recommended 3-6 months",
                "recommendation": "Increase monthly savings allocation until emergency fund reaches 3-6 months of expenses"
            }
        return None
    
    def _check_debt_to_income(self, profile):
        """Check if debt-to-income ratio is too high."""
        monthly_income = profile.get("monthly_income", 0)
        debt_payments = profile.get('expense_debt_payments', 0)
        
        # Calculate debt-to-income ratio
        if monthly_income > 0:
            dti_ratio = (debt_payments / monthly_income) * 100
            
            if dti_ratio > 36:
                return {
                    "issue": "High debt-to-income ratio",
                    "severity": "high" if dti_ratio > 50 else "medium",
                    "details": f"Debt payments consume {dti_ratio:.1f}% of income (recommended: <36%)",
                    "recommendation": "Focus on paying down high-interest debt and avoid taking on new debt"
                }
        return None
    
    def _check_expense_ratio(self, profile):
        """Check if total expenses are too high relative to income."""
        monthly_expenses = sum([v for k, v in profile.items() if k.startswith('expense_')])
        monthly_income = profile.get("monthly_income", 0)
        
        if monthly_income == 0:
            return {
                "issue": "Missing income information",
                "severity": "high",
                "details": "No monthly income data provided",
                "recommendation": "Ensure accurate monthly income is entered to assess financial health"
            }
        
        expense_ratio = (monthly_expenses / monthly_income) * 100
        
        if expense_ratio > 90:
            return {
                "issue": "Excessive expenses",
                "severity": "high",
                "details": f"Expenses consume {expense_ratio:.1f}% of income, leaving little room for savings",
                "recommendation": "Review budget to identify areas for reduction, especially discretionary spending"
            }
        elif expense_ratio > 80:
            return {
                "issue": "High expenses",
                "severity": "medium",
                "details": f"Expenses consume {expense_ratio:.1f}% of income",
                "recommendation": "Consider the 50/30/20 rule: 50% needs, 30% wants, 20% savings/debt repayment"
            }
        return None
    
    def _check_savings_rate(self, profile):
        """Check if savings rate is too low."""
        monthly_income = profile['monthly_income']
        
        # Calculate monthly_savings if not provided
        if 'monthly_savings' in profile:
            monthly_savings = profile['monthly_savings']
        else:
            monthly_expenses = sum([v for k, v in profile.items() if k.startswith('expense_')])
            monthly_savings = monthly_income - monthly_expenses
        
        savings_rate = (monthly_savings / monthly_income) * 100 if monthly_income > 0 else 0
        
        if savings_rate < 10:
            return {
                "issue": "Low savings rate",
                "severity": "medium" if savings_rate > 0 else "high",
                "details": f"Current savings rate is {savings_rate:.1f}% (recommended: at least 15-20%)",
                "recommendation": "Aim to increase savings rate by reducing discretionary spending"
            }
        return None
    
    def _check_high_interest_debt(self, profile):
        """Check for high-interest debt."""
        primary_debt_type = profile.get('primary_debt_type', 'None')
        primary_debt_apr = profile.get('primary_debt_apr', 0)
        
        if primary_debt_type != "None" and primary_debt_apr > 10:
            return {
                "issue": "High-interest debt",
                "severity": "high" if primary_debt_apr > 20 else "medium",
                "details": f"Your {primary_debt_type} has a high APR of {primary_debt_apr}%",
                "recommendation": "Prioritize paying off high-interest debt before focusing on other financial goals"
            }
        return None
    
    def analyze_profile(self, profile):
        """Analyze a user profile and return issues and recommendations."""
        # Ensure profile is not None and is a dictionary
        if not profile or not isinstance(profile, dict):
            return {
                "financial_health": "Poor",
                "issues": [{
                    "issue": "Invalid Profile Data",
                    "severity": "high",
                    "details": "Unable to analyze profile due to missing or invalid data",
                    "recommendation": "Re-enter financial data and verify all inputs are correct"
                }],
                "action_plan": ["Re-enter financial data", "Verify all inputs are correct"]
            }
        
        issues = []
        
        for detector in self.issue_detectors:
            issue = detector(profile)
            if issue:
                issues.append(issue)
        
        # Determine overall financial health
        if len(issues) == 0:
            financial_health = "Excellent"
        elif len([i for i in issues if i['severity'] == 'high']) > 0:
            financial_health = "Poor"
        elif len(issues) <= 2:
            financial_health = "Good"
        else:
            financial_health = "Fair"
        
        # Generate prioritized action plan
        high_priority = [i['recommendation'] for i in issues if i['severity'] == 'high']
        medium_priority = [i['recommendation'] for i in issues if i['severity'] == 'medium']
        
        action_plan = high_priority + medium_priority
        
        return {
            "financial_health": financial_health,
            "issues": issues,
            "action_plan": action_plan
        }

# Ensure the class is directly importable
__all__ = ['FinancialAnalyzer']

# Optional: Example usage script
def main():
    """Example of how to use the FinancialAnalyzer."""
    try:
        # Load sample profile data
        df = pd.read_csv("data/sample_profiles.csv")
        sample_profile = df.iloc[0].to_dict()
        
        analyzer = FinancialAnalyzer()
        results = analyzer.analyze_profile(sample_profile)
        
        print(f"Financial Health: {results['financial_health']}")
        print("\nIdentified Issues:")
        for issue in results["issues"]:
            print(f"- {issue['issue']} ({issue['severity']}): {issue['details']}")
        
        print("\nRecommended Action Plan:")
        for i, action in enumerate(results['action_plan'], 1):
            print(f"{i}. {action}")
    
    except FileNotFoundError:
        print("Sample profiles not found. Make sure to run data_generator.py first.")

# This allows the script to be run directly or imported
if __name__ == "__main__":
    main()
    print(profile)  # Check what keys and values are present