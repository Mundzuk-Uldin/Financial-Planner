import pandas as pd
import numpy as np

class TaxCalculator:
    """
    Calculates tax implications on income, savings, and investments 
    to provide a more realistic financial projection.
    """
    
    def __init__(self):
        """Initialize the tax calculator with default tax brackets and rates."""
        # Federal income tax brackets (2023, single filer)
        self.federal_brackets = [
            (0, 11000, 0.10),        # 10% on income up to $11,000
            (11000, 44725, 0.12),    # 12% on income from $11,000 to $44,725
            (44725, 95375, 0.22),    # 22% on income from $44,725 to $95,375
            (95375, 182100, 0.24),   # 24% on income from $95,375 to $182,100
            (182100, 231250, 0.32),  # 32% on income from $182,100 to $231,250
            (231250, 578125, 0.35),  # 35% on income from $231,250 to $578,125
            (578125, float('inf'), 0.37)  # 37% on income above $578,125
        ]
        
        # Standard deduction (2023, single filer)
        self.standard_deduction = 13850
        
        # FICA taxes
        self.social_security_rate = 0.062  # 6.2%
        self.social_security_cap = 160200  # Cap for Social Security taxes (2023)
        self.medicare_rate = 0.0145  # 1.45%
        self.additional_medicare_rate = 0.009  # 0.9% additional for high earners
        self.additional_medicare_threshold = 200000  # Threshold for additional Medicare tax
        
        # Capital gains tax rates (2023, single filer)
        self.capital_gains_brackets = [
            (0, 44625, 0.0),          # 0% on capital gains if income up to $44,625
            (44625, 492300, 0.15),    # 15% on capital gains if income from $44,625 to $492,300
            (492300, float('inf'), 0.20)  # 20% on capital gains if income above $492,300
        ]
        
        # Net Investment Income Tax (NIIT)
        self.niit_rate = 0.038  # 3.8%
        self.niit_threshold = 200000  # Threshold for NIIT (2023, single filer)
        
        # State income tax (default rate, override for specific states)
        self.state_tax_rate = 0.05  # 5% flat rate as default
        
        # Retirement account limits (2023)
        self.retirement_limits = {
            "401k": 22500,         # 401(k) contribution limit
            "ira": 6500,           # IRA contribution limit
            "catch_up_401k": 7500, # 401(k) catch-up contribution (age 50+)
            "catch_up_ira": 1000,  # IRA catch-up contribution (age 50+)
            "roth_ira_limit": 153000,  # Income limit for full Roth IRA contribution
            "roth_ira_phaseout": 228000  # Income limit after which no Roth IRA contribution allowed
        }
    
    def set_state_tax_rate(self, rate):
        """
        Set state income tax rate.
        
        Args:
            rate (float): State income tax rate (e.g., 0.06 for 6%)
        """
        self.state_tax_rate = rate
    
    def calculate_federal_income_tax(self, annual_income, deductions=None):
        """
        Calculate federal income tax based on progressive tax brackets.
        
        Args:
            annual_income (float): Gross annual income
            deductions (float, optional): Itemized deductions. If None, standard deduction is used.
            
        Returns:
            float: Federal income tax amount
        """
        # Apply standard deduction if no itemized deductions provided
        if deductions is None:
            deductions = self.standard_deduction
        
        # Calculate taxable income
        taxable_income = max(0, annual_income - deductions)
        
        # Calculate tax based on brackets
        tax = 0
        for lower, upper, rate in self.federal_brackets:
            if taxable_income > lower:
                bracket_income = min(taxable_income - lower, upper - lower)
                tax += bracket_income * rate
            else:
                break
        
        return tax
    
    def calculate_fica_taxes(self, annual_income):
        """
        Calculate FICA taxes (Social Security and Medicare).
        
        Args:
            annual_income (float): Gross annual income
            
        Returns:
            dict: FICA tax breakdown
        """
        # Social Security tax (capped)
        ss_taxable_income = min(annual_income, self.social_security_cap)
        social_security_tax = ss_taxable_income * self.social_security_rate
        
        # Medicare tax (no cap, additional rate for high earners)
        basic_medicare_tax = annual_income * self.medicare_rate
        
        additional_medicare_tax = 0
        if annual_income > self.additional_medicare_threshold:
            additional_medicare_tax = (annual_income - self.additional_medicare_threshold) * self.additional_medicare_rate
        
        total_medicare_tax = basic_medicare_tax + additional_medicare_tax
        
        return {
            "social_security": social_security_tax,
            "medicare": total_medicare_tax,
            "total_fica": social_security_tax + total_medicare_tax
        }
    
    def calculate_capital_gains_tax(self, capital_gains, annual_income):
        """
        Calculate capital gains tax.
        
        Args:
            capital_gains (float): Amount of capital gains
            annual_income (float): Ordinary income
            
        Returns:
            float: Capital gains tax amount
        """
        # Find applicable capital gains rate based on income
        applicable_rate = 0
        for lower, upper, rate in self.capital_gains_brackets:
            if annual_income > lower:
                applicable_rate = rate
            else:
                break
        
        # Calculate capital gains tax
        capital_gains_tax = capital_gains * applicable_rate
        
        # Net Investment Income Tax (NIIT)
        niit = 0
        if annual_income > self.niit_threshold:
            niit = capital_gains * self.niit_rate
        
        return capital_gains_tax + niit
    
    def calculate_state_income_tax(self, annual_income, deductions=0):
        """
        Calculate state income tax using flat rate.
        
        Args:
            annual_income (float): Gross annual income
            deductions (float, optional): State-specific deductions
            
        Returns:
            float: State income tax amount
        """
        taxable_income = max(0, annual_income - deductions)
        return taxable_income * self.state_tax_rate
    
    def calculate_tax_impact_on_investments(self, investment_growth, dividend_income, annual_income, is_retirement_account=False):
        """
        Calculate tax impact on investment gains and dividends.
        
        Args:
            investment_growth (float): Unrealized gains in investments
            dividend_income (float): Dividend income received
            annual_income (float): Ordinary income
            is_retirement_account (bool): Whether the investment is in a tax-advantaged retirement account
            
        Returns:
            dict: Tax implications
        """
        if is_retirement_account:
            # No immediate tax impact for retirement accounts
            return {
                "taxable_amount": 0,
                "tax_due": 0,
                "effective_tax_rate": 0,
                "after_tax_value": investment_growth + dividend_income
            }
        
        # For taxable accounts
        taxable_dividends = dividend_income
        capital_gains_tax = self.calculate_capital_gains_tax(investment_growth, annual_income)
        dividend_tax = self.calculate_capital_gains_tax(taxable_dividends, annual_income)
        
        total_tax = capital_gains_tax + dividend_tax
        total_gain = investment_growth + dividend_income
        
        if total_gain > 0:
            effective_tax_rate = total_tax / total_gain
        else:
            effective_tax_rate = 0
        
        return {
            "taxable_amount": total_gain,
            "tax_due": total_tax,
            "effective_tax_rate": effective_tax_rate,
            "after_tax_value": total_gain - total_tax
        }
    
    def calculate_retirement_contribution_tax_savings(self, annual_income, contribution, retirement_account_type="traditional"):
        """
        Calculate tax savings from retirement account contributions.
        
        Args:
            annual_income (float): Gross annual income
            contribution (float): Amount contributed to retirement account
            retirement_account_type (str): "traditional" or "roth"
            
        Returns:
            dict: Tax savings information
        """
        if retirement_account_type.lower() == "roth":
            # Roth contributions are made with after-tax dollars
            return {
                "current_year_tax_savings": 0,
                "contribution_allowed": self._check_roth_contribution_limit(annual_income, contribution)
            }
        
        # For traditional retirement accounts
        tax_without_contribution = self.calculate_federal_income_tax(annual_income)
        tax_with_contribution = self.calculate_federal_income_tax(annual_income - contribution)
        tax_savings = tax_without_contribution - tax_with_contribution
        
        return {
            "current_year_tax_savings": tax_savings,
            "effective_contribution_cost": contribution - tax_savings,
            "tax_savings_rate": tax_savings / contribution if contribution > 0 else 0
        }
    
    def _check_roth_contribution_limit(self, annual_income, proposed_contribution):
        """
        Check if Roth IRA contribution is allowed based on income limits.
        
        Args:
            annual_income (float): Modified adjusted gross income
            proposed_contribution (float): Desired contribution amount
            
        Returns:
            float: Allowed contribution amount
        """
        if annual_income <= self.retirement_limits["roth_ira_limit"]:
            # Full contribution allowed
            return min(proposed_contribution, self.retirement_limits["ira"])
        elif annual_income < self.retirement_limits["roth_ira_phaseout"]:
            # Partial contribution in phase-out range
            phase_out_range = self.retirement_limits["roth_ira_phaseout"] - self.retirement_limits["roth_ira_limit"]
            phase_out_percent = (self.retirement_limits["roth_ira_phaseout"] - annual_income) / phase_out_range
            allowed = phase_out_percent * self.retirement_limits["ira"]
            return min(proposed_contribution, allowed)
        else:
            # No contribution allowed
            return 0
    
    def calculate_monthly_take_home_pay(self, annual_income, retirement_contribution=0, other_pretax_deductions=0):
        """
        Calculate monthly take-home pay after taxes and deductions.
        
        Args:
            annual_income (float): Gross annual income
            retirement_contribution (float): Annual retirement contribution
            other_pretax_deductions (float): Other pre-tax deductions (health insurance, etc.)
            
        Returns:
            dict: Take-home pay breakdown
        """
        # Calculate taxable income after pre-tax deductions
        pretax_deductions = retirement_contribution + other_pretax_deductions
        taxable_income = annual_income - pretax_deductions
        
        # Calculate taxes
        federal_tax = self.calculate_federal_income_tax(taxable_income)
        fica_taxes = self.calculate_fica_taxes(annual_income)  # FICA is calculated on gross income
        state_tax = self.calculate_state_income_tax(taxable_income)
        
        # Calculate annual take-home pay
        annual_take_home = annual_income - federal_tax - fica_taxes["total_fica"] - state_tax - pretax_deductions
        monthly_take_home = annual_take_home / 12
        
        # Calculate effective tax rate
        total_tax = federal_tax + fica_taxes["total_fica"] + state_tax
        effective_tax_rate = total_tax / annual_income if annual_income > 0 else 0
        
        return {
            "annual_gross_income": annual_income,
            "pretax_deductions": pretax_deductions,
            "federal_income_tax": federal_tax,
            "social_security_tax": fica_taxes["social_security"],
            "medicare_tax": fica_taxes["medicare"],
            "state_income_tax": state_tax,
            "total_tax": total_tax,
            "effective_tax_rate": effective_tax_rate,
            "annual_take_home": annual_take_home,
            "monthly_take_home": monthly_take_home
        }
    
    def simulate_tax_impact_on_financial_path(self, 
                                             annual_income, 
                                             yearly_income_growth=0.03, 
                                             retirement_contribution_percent=0.05,
                                             years=5,
                                             investment_return_rate=0.07,
                                             initial_investment=0):
        """
        Simulate the impact of taxes on financial growth over time.
        
        Args:
            annual_income (float): Starting annual income
            yearly_income_growth (float): Annual income growth rate
            retirement_contribution_percent (float): Percent of income contributed to retirement
            years (int): Number of years to simulate
            investment_return_rate (float): Annual investment return rate
            initial_investment (float): Initial investment amount
            
        Returns:
            DataFrame: Year-by-year tax and investment impacts
        """
        results = {
            'year': [],
            'annual_income': [],
            'retirement_contribution': [],
            'federal_tax': [],
            'fica_tax': [],
            'state_tax': [],
            'take_home_pay': [],
            'taxable_investment_value': [],
            'tax_advantaged_value': [],
            'taxes_on_investments': [],
            'total_net_worth': []
        }
        
        current_income = annual_income
        taxable_investment = initial_investment
        tax_advantaged = 0
        
        for year in range(1, years + 1):
            results['year'].append(year)
            results['annual_income'].append(current_income)
            
            # Calculate retirement contribution
            retirement_contribution = current_income * retirement_contribution_percent
            results['retirement_contribution'].append(retirement_contribution)
            
            # Calculate taxes and take-home pay
            take_home_details = self.calculate_monthly_take_home_pay(
                current_income, 
                retirement_contribution=retirement_contribution
            )
            
            results['federal_tax'].append(take_home_details['federal_income_tax'])
            results['fica_tax'].append(take_home_details['social_security_tax'] + take_home_details['medicare_tax'])
            results['state_tax'].append(take_home_details['state_income_tax'])
            results['take_home_pay'].append(take_home_details['annual_take_home'])
            
            # Simulate investment growth
            # Assume 50% of savings (take_home - expenses) goes to taxable investments
            annual_savings = take_home_details['annual_take_home'] * 0.2  # Assume 20% savings rate
            taxable_investment_contribution = annual_savings * 0.5
            
            # Taxable investment growth
            taxable_investment_growth = taxable_investment * investment_return_rate
            dividend_income = taxable_investment * 0.02  # Assume 2% dividend yield
            
            tax_impact = self.calculate_tax_impact_on_investments(
                taxable_investment_growth - dividend_income,  # Unrealized gains
                dividend_income,
                current_income
            )
            
            taxable_investment = (
                taxable_investment + 
                taxable_investment_growth + 
                taxable_investment_contribution - 
                tax_impact['tax_due']
            )
            
            # Tax-advantaged investment growth
            tax_advantaged_growth = tax_advantaged * investment_return_rate
            tax_advantaged = tax_advantaged + tax_advantaged_growth + retirement_contribution
            
            results['taxable_investment_value'].append(taxable_investment)
            results['tax_advantaged_value'].append(tax_advantaged)
            results['taxes_on_investments'].append(tax_impact['tax_due'])
            results['total_net_worth'].append(taxable_investment + tax_advantaged)
            
            # Increase income for next year
            current_income *= (1 + yearly_income_growth)
        
        return pd.DataFrame(results)

# Example usage
if __name__ == "__main__":
    calculator = TaxCalculator()
    
    # Test federal income tax calculation
    annual_income = 75000
    federal_tax = calculator.calculate_federal_income_tax(annual_income)
    print(f"Federal Income Tax on ${annual_income:,.2f}: ${federal_tax:,.2f}")
    
    # Test FICA taxes
    fica_taxes = calculator.calculate_fica_taxes(annual_income)
    print(f"FICA Taxes: ${fica_taxes['total_fica']:,.2f}")
    print(f"  Social Security: ${fica_taxes['social_security']:,.2f}")
    print(f"  Medicare: ${fica_taxes['medicare']:,.2f}")
    
    # Test take-home pay calculation
    take_home = calculator.calculate_monthly_take_home_pay(annual_income, retirement_contribution=7500)
    print(f"\nTake-Home Pay Breakdown:")
    print(f"  Monthly Income: ${take_home['annual_gross_income']/12:,.2f}")
    print(f"  Monthly Take-Home: ${take_home['monthly_take_home']:,.2f}")
    print(f"  Effective Tax Rate: {take_home['effective_tax_rate']*100:.2f}%")
    
    # Test tax impact simulation
    simulation = calculator.simulate_tax_impact_on_financial_path(
        annual_income=75000,
        retirement_contribution_percent=0.10,
        years=10,
        initial_investment=50000
    )
    
    print("\nTax Impact Over Time:")
    print(f"Starting Income: ${annual_income:,.2f}")
    print(f"Final Income (Year 10): ${simulation['annual_income'].iloc[-1]:,.2f}")
    print(f"Final Net Worth: ${simulation['total_net_worth'].iloc[-1]:,.2f}")
    print(f"  Taxable Investments: ${simulation['taxable_investment_value'].iloc[-1]:,.2f}")
    print(f"  Tax-Advantaged: ${simulation['tax_advantaged_value'].iloc[-1]:,.2f}")
    print(f"Total Taxes Paid on Investments: ${simulation['taxes_on_investments'].sum():,.2f}")