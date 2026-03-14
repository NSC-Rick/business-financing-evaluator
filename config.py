"""
Configuration file for Business Financing Readiness Tool
Contains constants, weights, and configuration parameters
"""

# Borrowing Base Percentages (Default - Balanced)
BORROWING_BASE_AR_PERCENT = 0.80
BORROWING_BASE_INVENTORY_PERCENT = 0.50

# Lender Risk Tolerance Scenarios
RISK_TOLERANCE_SCENARIOS = {
    'Conservative': {
        'ar_advance': 0.70,
        'inventory_advance': 0.40,
        'description': 'Lower advance rates, higher collateral requirements'
    },
    'Balanced': {
        'ar_advance': 0.80,
        'inventory_advance': 0.50,
        'description': 'Standard advance rates, typical lending terms'
    },
    'Aggressive': {
        'ar_advance': 0.85,
        'inventory_advance': 0.60,
        'description': 'Higher advance rates, more flexible terms'
    }
}

# Revenue-based LOC Range
REVENUE_LOC_LOW_PERCENT = 0.05
REVENUE_LOC_HIGH_PERCENT = 0.15

# Days in Year
DAYS_IN_YEAR = 365

# Readiness Score Weights (must sum to 100)
READINESS_WEIGHTS = {
    'revenue_strength': 20,
    'cash_flow': 20,
    'dscr': 20,
    'liquidity': 15,
    'collateral': 15,
    'business_history': 10
}

# Confidence Indicator Thresholds
CONFIDENCE_THRESHOLDS = {
    'years_in_business': 3,
    'min_net_income': 0,
    'min_dscr': 1.25,
    'min_current_ratio': 1.2,
    'min_ar_percent': 0.2
}

# Confidence Level Labels
CONFIDENCE_LABELS = {
    (0, 1): 'Low',
    (2, 3): 'Moderate',
    (4, 5): 'High'
}

# Cash Conversion Cycle Threshold
CCC_THRESHOLD = 30

# Industry Options
INDUSTRIES = [
    'Retail',
    'Manufacturing',
    'Professional Services',
    'Construction',
    'Healthcare',
    'Technology',
    'Hospitality',
    'Transportation',
    'Wholesale',
    'Other'
]

# Business Type Options
BUSINESS_TYPES = ['Service', 'Product']

# Validation Ranges
VALIDATION = {
    'min_revenue': 0,
    'min_days': 0,
    'max_days': 365,
    'min_liabilities': 0
}

# Report Output Path
REPORT_OUTPUT_PATH = "docs/windsurf_reports/"

# Streamlit Page Configuration
PAGE_CONFIG = {
    'page_title': 'Business Financing Readiness Tool',
    'page_icon': '💼',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Color Scheme for Visualizations
COLORS = {
    'primary': '#1f77b4',
    'success': '#2ca02c',
    'warning': '#ff7f0e',
    'danger': '#d62728',
    'info': '#17becf'
}
