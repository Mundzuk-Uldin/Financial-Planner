import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

class FinancialDataGenerator:
    def __init__(self, seed=None):
        """Initialize the data generator with optional seed for reproducibility."""
        if seed:
            Faker.seed(seed)
            random.seed(seed)
            np.random.seed(seed)
        
        self.expense_categories = [
            "Rent/Mortgage", "Utilities", "Groceries", "Dining Out", 
            "Transportation", "Healthcare", "Entertainment", "Shopping",
            "Subscriptions", "Debt Payments", "Savings", "Miscellaneous"
        ]
    
    def generate_user(self):
        """Generate a single user profile with financial data."""
        # Basic demographics
        age = random.randint(22, 65)
        
        # Income based on age and random factors
        base_income = np.random.normal(
            loc=3000 + (age * 100), 
            scale=1500
        )
        monthly_income = max(round(base_income, 2), 2000)
        
        # Expense model - distribute total expenses based on income
        expense_ratio = np.random.uniform(0.6, 0.95)  # Spend 60-95% of income
        total_expenses = monthly_income * expense_ratio
        
        # Distribute expenses across categories
        expense_weights = np.random.dirichlet(np.ones(len(self.expense_categories)))
        expenses = {cat: round(total_expenses * weight, 2) 
                   for cat, weight in zip(self.expense_categories, expense_weights)}
        
        # Calculate savings
        savings = monthly_income - sum(expenses.values())
        current_savings = round(savings * np.random.randint(1, 24), 2)  # 1-24 months of savings
        
        # Debt profile
        has_debt = random.random() < 0.7  # 70% chance of having debt
        debt_types = []
        debt_amounts = []
        debt_aprs = []
        
        if has_debt:
            num_debts = np.random.randint(1, 4)
            
            for _ in range(num_debts):
                debt_type = random.choice(["Credit Card", "Student Loan", "Car Loan", "Personal Loan"])
                
                # Different debt amounts based on type
                if debt_type == "Credit Card":
                    amount = round(np.random.uniform(500, 15000), 2)
                    apr = round(np.random.uniform(14, 25), 2)
                elif debt_type == "Student Loan":
                    amount = round(np.random.uniform(5000, 80000), 2)
                    apr = round(np.random.uniform(3, 7), 2)
                elif debt_type == "Car Loan":
                    amount = round(np.random.uniform(5000, 50000), 2)
                    apr = round(np.random.uniform(3, 8), 2)
                else:  # Personal Loan
                    amount = round(np.random.uniform(1000, 20000), 2)
                    apr = round(np.random.uniform(6, 15), 2)
                
                debt_types.append(debt_type)
                debt_amounts.append(amount)
                debt_aprs.append(apr)
        
        # Financial goals - randomly assign 1-2 goals
        possible_goals = [
            "Build emergency fund", "Pay off debt", "Save for home", 
            "Save for vacation", "Save for retirement", "Save for education"
        ]
        num_goals = np.random.randint(1, 3)
        goals = random.sample(possible_goals, num_goals)
        
        # Assemble user profile
        user = {
            "user_id": fake.uuid4(),
            "name": fake.name(),
            "age": age,
            "occupation": fake.job(),
            "monthly_income": round(monthly_income, 2),
            "expenses": expenses,
            "monthly_savings": round(savings, 2),
            "current_savings": current_savings,
            "debt_types": debt_types,
            "debt_amounts": debt_amounts, 
            "debt_aprs": debt_aprs,
            "financial_goals": goals,
            "risk_tolerance": random.choice(["Low", "Medium", "High"]),
        }
        
        return user
    
    def generate_users(self, num_users=100):
        """Generate multiple user profiles."""
        users = [self.generate_user() for _ in range(num_users)]
        return users
    
    def generate_dataframe(self, num_users=100):
        """Generate user profiles and convert to pandas DataFrame."""
        users = self.generate_users(num_users)
        
        # Flatten the nested dictionaries and lists for DataFrame representation
        flat_users = []
        for user in users:
            flat_user = {
                "user_id": user["user_id"],
                "name": user["name"],
                "age": user["age"],
                "occupation": user["occupation"],
                "monthly_income": user["monthly_income"],
                "monthly_savings": user["monthly_savings"],
                "current_savings": user["current_savings"],
                "risk_tolerance": user["risk_tolerance"],
            }
            
            # Add expense categories
            for category, amount in user["expenses"].items():
                flat_user[f"expense_{category.lower().replace('/', '_')}"] = amount
            
            # Add debt information
            total_debt = sum(user["debt_amounts"]) if user["debt_amounts"] else 0
            flat_user["total_debt"] = total_debt
            
            # Add primary debt type and its APR (if any)
            if user["debt_types"]:
                max_debt_idx = np.argmax(user["debt_amounts"])
                flat_user["primary_debt_type"] = user["debt_types"][max_debt_idx]
                flat_user["primary_debt_apr"] = user["debt_aprs"][max_debt_idx]
            else:
                flat_user["primary_debt_type"] = "None"
                flat_user["primary_debt_apr"] = 0.0
            
            # Add goals as comma-separated string
            flat_user["financial_goals"] = ", ".join(user["financial_goals"])
            
            flat_users.append(flat_user)
        
        df = pd.DataFrame(flat_users)
        return df
    
    def save_to_csv(self, num_users=100, filename="sample_profiles.csv"):
        """Generate user profiles and save to CSV."""
        df = self.generate_dataframe(num_users)
        df.to_csv(f"data/{filename}", index=False)
        return df

# Example usage
if __name__ == "__main__":
    generator = FinancialDataGenerator(seed=42)
    df = generator.save_to_csv(num_users=50)
    print(f"Generated {len(df)} user profiles.")
    print(df.head())