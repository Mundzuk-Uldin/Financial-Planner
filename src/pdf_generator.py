import os
import tempfile
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from io import BytesIO
import base64

class FinancialReportGenerator:
    """
    Generates a PDF report of financial analysis and projections.
    """
    
    def __init__(self):
        """Initialize the report generator with default styles."""
        self.styles = getSampleStyleSheet()
        
        # Create custom styles with unique names - don't try to iterate through self.styles
        # Remove this line: existing_styles = [style.name for style in self.styles]
        
        # Create custom styles with unique names
        self.styles.add(ParagraphStyle(
            name='ReportTitle',  # Changed from 'Title'
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReportSubtitle',  # Changed from 'Subtitle'
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReportSectionHeader',  # Changed from 'SectionHeader'
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReportBodyText',  # Changed from 'BodyText'
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='FinancialMetric',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='FinancialWarning',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.red,
            fontName='Helvetica-Bold'
        ))
    
    def _format_currency(self, value):
        """Format a value as currency."""
        return f"${value:,.2f}"
    
    def _format_percentage(self, value):
        """Format a value as a percentage."""
        return f"{value:.2f}%"
    
    def _create_financial_summary_table(self, profile):
        """Create a table with financial summary data."""
        # Extract key metrics
        monthly_income = profile.get('monthly_income', 0)
        monthly_expenses = sum([v for k, v in profile.items() if k.startswith('expense_')])
        monthly_savings = monthly_income - monthly_expenses
        current_savings = profile.get('current_savings', 0)
        total_debt = profile.get('total_debt', 0)
        
        # Calculate additional metrics
        savings_rate = (monthly_savings / monthly_income) * 100 if monthly_income > 0 else 0
        expense_ratio = (monthly_expenses / monthly_income) * 100 if monthly_income > 0 else 0
        net_worth = current_savings - total_debt
        
        # Format the data
        data = [
            ["Metric", "Value", "Status"],
            ["Monthly Income", self._format_currency(monthly_income), ""],
            ["Monthly Expenses", self._format_currency(monthly_expenses), ""],
            ["Monthly Savings", self._format_currency(monthly_savings), 
             "Low" if savings_rate < 10 else "Good" if savings_rate < 20 else "Excellent"],
            ["Savings Rate", self._format_percentage(savings_rate), 
             "Low" if savings_rate < 10 else "Good" if savings_rate < 20 else "Excellent"],
            ["Current Savings", self._format_currency(current_savings), ""],
            ["Total Debt", self._format_currency(total_debt), 
             "High" if total_debt > monthly_income * 12 else "Moderate" if total_debt > monthly_income * 6 else "Low"],
            ["Net Worth", self._format_currency(net_worth), ""],
            ["Expense Ratio", self._format_percentage(expense_ratio), 
             "High" if expense_ratio > 90 else "Moderate" if expense_ratio > 75 else "Good"]
        ]
        
        # Create the table
        table = Table(data, colWidths=[2*inch, 1.5*inch, 1*inch])
        
        # Style the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (2, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (2, 0), colors.darkblue),
            ('ALIGN', (0, 0), (2, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (2, 0), 12),
            ('BOTTOMPADDING', (0, 0), (2, 0), 8),
            ('TOPPADDING', (0, 0), (2, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        # Color code the status column
        for i in range(1, len(data)):
            status = data[i][2]
            if status in ["Low", "High"]:
                style.add('TEXTCOLOR', (2, i), (2, i), colors.red)
            elif status in ["Good", "Moderate"]:
                style.add('TEXTCOLOR', (2, i), (2, i), colors.orange)
            elif status == "Excellent":
                style.add('TEXTCOLOR', (2, i), (2, i), colors.darkgreen)
            
            # Alternate row colors
            if i % 2 == 1:
                style.add('BACKGROUND', (0, i), (2, i), colors.whitesmoke)
        
        table.setStyle(style)
        return table
    
    def _create_recommendations_section(self, analysis_results):
        """Create a section with financial recommendations."""
        elements = []
        
        elements.append(Paragraph("Recommended Action Plan", self.styles['ReportSubtitle']))
        elements.append(Spacer(1, 0.1*inch))
        
        if not analysis_results.get('action_plan'):
            elements.append(Paragraph(
                "No specific actions needed. You're on a great financial path!",
                self.styles['ReportBodyText']
            ))
            return elements
        
        # Add each recommendation
        for i, action in enumerate(analysis_results['action_plan'], 1):
            elements.append(Paragraph(
                f"{i}. {action}",
                self.styles['ReportBodyText']
            ))
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_projection_chart(self, current_path, improved_path):
        """Create a chart comparing the two financial paths."""
        plt.figure(figsize=(8, 4))
        
        # Format x-axis labels for readability
        x_labels = [d.strftime('%b %Y') for d in current_path['date']]
        
        # Plot data
        plt.plot(x_labels, current_path['net_worth'], label='Current Path', color='#1f77b4')
        plt.plot(x_labels, improved_path['net_worth'], label='Improved Path', color='#2ca02c')
        
        # Add labels and title
        plt.title('Net Worth Projection', fontsize=14)
        plt.xlabel('Date', fontsize=10)
        plt.ylabel('Net Worth ($)', fontsize=10)
        plt.legend()
        
        # Adjust x-axis to show fewer labels
        plt.xticks(range(0, len(x_labels), max(1, len(x_labels) // 6)), rotation=45)
        
        # Format y-axis with dollar amounts
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"${x:,.0f}"))
        
        # Ensure clean layout
        plt.tight_layout()
        
        # Save chart to a BytesIO object
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    def _create_investment_allocation_chart(self, risk_profile):
        """Create a pie chart showing investment allocation."""
        # Get allocation for the selected risk profile
        asset_classes = {
            "savings_account": "Savings Account",
            "bonds": "Bonds",
            "index_funds": "Index Funds",
            "stocks": "Stocks",
            "crypto": "Crypto"
        }
        
        # Sample allocations (in a real app, get these from the investment simulator)
        allocations = {
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
        
        # Get allocation for the selected profile
        allocation = allocations.get(risk_profile, allocations["moderate"])
        
        # Create labels and values for the pie chart
        labels = []
        values = []
        
        for asset_code, percentage in allocation.items():
            if percentage > 0:
                labels.append(asset_classes.get(asset_code, asset_code))
                values.append(percentage * 100)  # Convert to percentage
        
        # Create pie chart
        plt.figure(figsize=(6, 4))
        plt.pie(values, labels=labels, autopct='%1.1f%%', 
                startangle=90, shadow=False)
        plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
        plt.title(f'Recommended Asset Allocation - {risk_profile.replace("_", " ").title()} Profile')
        
        # Save chart to a BytesIO object
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    def _create_comparison_table(self, comparison):
        """Create a table comparing the two financial scenarios."""
        # Extract data
        current_path = comparison['current_path']
        improved_path = comparison['improved_path']
        difference = comparison['difference']
        
        # Format the data
        data = [
            ["Metric", "Current Path", "Improved Path", "Difference"],
            ["Final Savings", 
             self._format_currency(current_path['final_savings']),
             self._format_currency(improved_path['final_savings']),
             self._format_currency(difference['savings_diff'])],
            ["Final Debt", 
             self._format_currency(current_path['final_debt']),
             self._format_currency(improved_path['final_debt']),
             self._format_currency(difference['debt_diff'])],
            ["Final Net Worth", 
             self._format_currency(current_path['final_net_worth']),
             self._format_currency(improved_path['final_net_worth']),
             self._format_currency(difference['net_worth_diff'])],
        ]
        
        # Add debt-free date if available
        if 'debt_free_date' in current_path:
            current_debt_free = current_path['debt_free_date'].strftime('%B %Y')
        else:
            current_debt_free = "Not within simulation"
            
        if 'debt_free_date' in improved_path:
            improved_debt_free = improved_path['debt_free_date'].strftime('%B %Y')
        else:
            improved_debt_free = "Not within simulation"
            
        data.append(["Debt-free Date", current_debt_free, improved_debt_free, ""])
        
        # Create the table
        table = Table(data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        
        # Style the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (3, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (3, 0), colors.darkblue),
            ('ALIGN', (0, 0), (3, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (3, 0), 12),
            ('BOTTOMPADDING', (0, 0), (3, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (3, -1), 'RIGHT'),
        ])
        
        # Alternate row colors
        for i in range(1, len(data)):
            if i % 2 == 1:
                style.add('BACKGROUND', (0, i), (3, i), colors.whitesmoke)
        
        # Highlight differences
        for i in range(1, 4):  # Only rows with monetary differences
            style.add('TEXTCOLOR', (3, i), (3, i), colors.darkgreen)
        
        table.setStyle(style)
        return table
    
    def generate_financial_report(self, 
                                 user_profile, 
                                 analysis_results, 
                                 simulation_results,
                                 investment_profile=None,
                                 tax_analysis=None,
                                 output_path=None):
        """
        Generate a comprehensive financial report in PDF format.
        
        Args:
            user_profile (dict): User's financial profile
            analysis_results (dict): Results of financial analysis
            simulation_results (dict): Results of financial simulations
            investment_profile (dict, optional): Investment profile and recommendations
            tax_analysis (dict, optional): Tax analysis results
            output_path (str, optional): Path to save the PDF file
            
        Returns:
            str: Path to the generated PDF file
        """
        # Create a temporary file if no output path is provided
        if output_path is None:
            temp_dir = tempfile.mkdtemp()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(temp_dir, f"Financial_Report_{timestamp}.pdf")
        
        # Create the document
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                              rightMargin=0.5*inch, leftMargin=0.5*inch,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Container for elements
        elements = []
        
        # Add title and date
        title = "Financial Future Simulator Report"
        date_str = datetime.now().strftime("%B %d, %Y")
        
        elements.append(Paragraph(title, self.styles['ReportTitle']))
        elements.append(Paragraph(f"Generated on {date_str}", self.styles['ReportBodyText']))
        elements.append(Spacer(1, 0.25*inch))
        
        # Financial Health Overview
        elements.append(Paragraph("Financial Health Overview", self.styles['ReportSubtitle']))
        
        health_score = analysis_results.get("financial_health", "Not Assessed")
        health_style = self.styles['FinancialMetric'] if health_score in ["Excellent", "Good"] else self.styles['FinancialWarning']
        
        elements.append(Paragraph(f"Financial Health Score: {health_score}", health_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Financial Summary Table
        elements.append(self._create_financial_summary_table(user_profile))
        elements.append(Spacer(1, 0.25*inch))
        
        # Recommendations
        elements.extend(self._create_recommendations_section(analysis_results))
        elements.append(Spacer(1, 0.25*inch))
        
        # Future Projections
        elements.append(Paragraph("5-Year Financial Projections", self.styles['ReportSubtitle']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Net Worth Chart
        if simulation_results:
            current = simulation_results.get("current")
            improved = simulation_results.get("improved")
            comparison = simulation_results.get("comparison")
            
            if current is not None and improved is not None:
                chart_buffer = self._create_projection_chart(current, improved)
                chart_img = Image(chart_buffer, width=6*inch, height=3*inch)
                elements.append(chart_img)
                elements.append(Spacer(1, 0.1*inch))
            
            if comparison is not None:
                elements.append(Paragraph("Comparison of Financial Paths", self.styles['ReportSectionHeader']))
                elements.append(self._create_comparison_table(comparison))
                elements.append(Spacer(1, 0.25*inch))
        
        # Investment Recommendations (if provided)
        if investment_profile:
            elements.append(Paragraph("Investment Recommendations", self.styles['ReportSubtitle']))
            elements.append(Spacer(1, 0.1*inch))
            
            risk_profile = investment_profile.get("recommended_profile", "moderate")
            elements.append(Paragraph(
                f"Recommended Risk Profile: {risk_profile.replace('_', ' ').title()}",
                self.styles['ReportSectionHeader']
            ))
            
            elements.append(Paragraph(
                investment_profile.get("profile_description", ""),
                self.styles['ReportBodyText']
            ))
            elements.append(Spacer(1, 0.1*inch))
            
            # Asset Allocation Chart
            chart_buffer = self._create_investment_allocation_chart(risk_profile)
            chart_img = Image(chart_buffer, width=5*inch, height=3*inch)
            elements.append(chart_img)
            elements.append(Spacer(1, 0.25*inch))
        
        # Tax Analysis (if provided)
        if tax_analysis:
            elements.append(Paragraph("Tax Impact Analysis", self.styles['ReportSubtitle']))
            elements.append(Spacer(1, 0.1*inch))
            
            monthly_income = user_profile.get('monthly_income', 0) 
            annual_income = monthly_income * 12
            
            elements.append(Paragraph(
                f"Based on your annual income of {self._format_currency(annual_income)}, "
                f"your tax obligations are:",
                self.styles['ReportBodyText']
            ))
            elements.append(Spacer(1, 0.1*inch))
            
            # Create tax breakdown table
            tax_data = [
                ["Tax Category", "Amount", "% of Income"],
                ["Federal Income Tax", 
                 self._format_currency(tax_analysis.get('federal_income_tax', 0)),
                 self._format_percentage(tax_analysis.get('federal_income_tax', 0) / annual_income * 100 if annual_income > 0 else 0)],
                ["Social Security Tax", 
                 self._format_currency(tax_analysis.get('social_security_tax', 0)),
                 self._format_percentage(tax_analysis.get('social_security_tax', 0) / annual_income * 100 if annual_income > 0 else 0)],
                ["Medicare Tax", 
                 self._format_currency(tax_analysis.get('medicare_tax', 0)),
                 self._format_percentage(tax_analysis.get('medicare_tax', 0) / annual_income * 100 if annual_income > 0 else 0)],
                ["State Income Tax", 
                 self._format_currency(tax_analysis.get('state_income_tax', 0)),
                 self._format_percentage(tax_analysis.get('state_income_tax', 0) / annual_income * 100 if annual_income > 0 else 0)],
                ["Total Tax Burden", 
                 self._format_currency(tax_analysis.get('total_tax', 0)),
                 self._format_percentage(tax_analysis.get('effective_tax_rate', 0) * 100)],
            ]
            
            tax_table = Table(tax_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            
            style = TableStyle([
                ('BACKGROUND', (0, 0), (2, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (2, 0), colors.darkblue),
                ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (1, 1), (2, -1), 'RIGHT'),
                ('FONTNAME', (0, -1), (2, -1), 'Helvetica-Bold'),
            ])
            
            # Alternate row colors
            for i in range(1, len(tax_data)):
                if i % 2 == 1:
                    style.add('BACKGROUND', (0, i), (2, i), colors.whitesmoke)
            
            tax_table.setStyle(style)
            elements.append(tax_table)
            elements.append(Spacer(1, 0.1*inch))
            
            # Add tax-efficient investing tips
            elements.append(Paragraph("Tax-Efficient Investing Tips:", self.styles['ReportSectionHeader']))
            
            tax_tips = [
                "Maximize contributions to tax-advantaged accounts like 401(k)s and IRAs.",
                "Consider Roth options for tax-free growth if you expect to be in a higher tax bracket in retirement.",
                "Hold tax-efficient investments like index funds in taxable accounts.",
                "Use tax-loss harvesting to offset capital gains.",
                "Consider municipal bonds for tax-free income in taxable accounts."
            ]
            
            for tip in tax_tips:
                elements.append(Paragraph(f"• {tip}", self.styles['ReportBodyText']))
                
            elements.append(Spacer(1, 0.25*inch))
        
        # Disclaimer
        elements.append(Paragraph("Disclaimer", self.styles['ReportSectionHeader']))
        elements.append(Paragraph(
            "This report is for educational purposes only and does not constitute financial advice. "
            "Projections are based on assumptions and historical data, and actual results may vary. "
            "Please consult with a qualified financial advisor before making investment decisions.",
            self.styles['ReportBodyText']
        ))
        
        # Build the document
        doc.build(elements)
        
        return output_path

# Example usage
if __name__ == "__main__":
    # Sample data for testing
    test_profile = {
        "monthly_income": 5000,
        "current_savings": 15000,
        "expense_rent_mortgage": 1500,
        "expense_utilities": 200,
        "expense_groceries": 400,
        "expense_dining_out": 300,
        "expense_transportation": 200,
        "total_debt": 20000,
        "primary_debt_type": "Credit Card",
        "primary_debt_apr": 18.0
    }
    
    test_analysis = {
        "financial_health": "Fair",
        "issues": [
            {
                "issue": "High-interest debt",
                "severity": "high",
                "details": "Your Credit Card has a high APR of 18.0%",
                "recommendation": "Prioritize paying off high-interest debt before other financial goals"
            },
            {
                "issue": "Insufficient emergency fund",
                "severity": "medium",
                "details": "Current savings cover only 2.5 months of expenses instead of recommended 3-6 months",
                "recommendation": "Increase monthly savings allocation until emergency fund reaches 3-6 months of expenses"
            }
        ],
        "action_plan": [
            "Prioritize paying off high-interest debt before other financial goals",
            "Increase monthly savings allocation until emergency fund reaches 3-6 months of expenses"
        ]
    }
    
    # Generate sample simulation data
    import numpy as np
    from datetime import datetime, timedelta
    
    # Simple function to create sample simulation data
    def create_sample_simulation():
        current_month = datetime.now().replace(day=1)
        months = 5 * 12
        
        current_path = {
            'date': [current_month + timedelta(days=30*i) for i in range(months)],
            'net_worth': [15000 - 20000 + i * 300 for i in range(months)],
            'savings': [15000 + i * 300 for i in range(months)],
            'debt': [20000 - i * 150 for i in range(months)]
        }
        
        improved_path = {
            'date': [current_month + timedelta(days=30*i) for i in range(months)],
            'net_worth': [15000 - 20000 + i * 450 for i in range(months)],
            'savings': [15000 + i * 350 for i in range(months)],
            'debt': [20000 - i * 300 for i in range(months)]
        }
        
        comparison = {
            'end_date': current_month + timedelta(days=30*(months-1)),
            'current_path': {
                'final_savings': current_path['savings'][-1],
                'final_debt': current_path['debt'][-1],
                'final_net_worth': current_path['net_worth'][-1],
                'debt_free_date': current_month + timedelta(days=30*134)  # Some future date
            },
            'improved_path': {
                'final_savings': improved_path['savings'][-1],
                'final_debt': improved_path['debt'][-1],
                'final_net_worth': improved_path['net_worth'][-1],
                'debt_free_date': current_month + timedelta(days=30*67)  # Some earlier future date
            },
            'difference': {
                'savings_diff': improved_path['savings'][-1] - current_path['savings'][-1],
                'debt_diff': current_path['debt'][-1] - improved_path['debt'][-1],
                'net_worth_diff': improved_path['net_worth'][-1] - current_path['net_worth'][-1]
            }
        }
        
        return {
            'current': pd.DataFrame(current_path),
            'improved': pd.DataFrame(improved_path),
            'comparison': comparison
        }
    
    # Sample investment profile
    test_investment = {
        "recommended_profile": "moderate",
        "profile_description": "A moderate risk profile balances growth with safety. It's suitable for investors with a medium-term horizon (5-10 years) who can tolerate some market volatility."
    }
    
    # Sample tax analysis
    test_tax = {
        "federal_income_tax": 7200,
        "social_security_tax": 3720,
        "medicare_tax": 870,
        "state_income_tax": 3000,
        "total_tax": 14790,
        "effective_tax_rate": 0.247
    }
    
    # Generate the report
    report_generator = FinancialReportGenerator()
    output_file = report_generator.generate_financial_report(
        test_profile,
        test_analysis,
        create_sample_simulation(),
        test_investment,
        test_tax
    )
    
    print(f"Report generated at: {output_file}")