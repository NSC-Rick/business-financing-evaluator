"""
Financial calculations module for Business Financing Readiness Tool
Contains all formulas and business logic for financial analysis
"""

import numpy as np
from typing import Dict, Tuple, Optional
from config import (
    BORROWING_BASE_AR_PERCENT,
    BORROWING_BASE_INVENTORY_PERCENT,
    REVENUE_LOC_LOW_PERCENT,
    REVENUE_LOC_HIGH_PERCENT,
    DAYS_IN_YEAR,
    READINESS_WEIGHTS,
    CONFIDENCE_THRESHOLDS,
    CONFIDENCE_LABELS,
    CCC_THRESHOLD
)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero
    
    Args:
        numerator: The numerator
        denominator: The denominator
        default: Value to return if denominator is zero
        
    Returns:
        Result of division or default value
    """
    if denominator == 0 or denominator is None:
        return default
    return numerator / denominator


def calculate_adjusted_cash_flow(net_income: float, owner_addbacks: float) -> float:
    """
    Calculate adjusted cash flow
    
    Args:
        net_income: Annual net income
        owner_addbacks: Owner addbacks (non-recurring expenses, owner salary adjustments)
        
    Returns:
        Adjusted cash flow
    """
    return net_income + owner_addbacks


def calculate_dscr(cash_flow: float, annual_debt_payments: float) -> float:
    """
    Calculate Debt Service Coverage Ratio (DSCR)
    
    Args:
        cash_flow: Adjusted cash flow
        annual_debt_payments: Total annual debt payments
        
    Returns:
        DSCR value
    """
    return safe_divide(cash_flow, annual_debt_payments, 0.0)


def calculate_current_ratio(current_assets: float, current_liabilities: float) -> float:
    """
    Calculate Current Ratio (Liquidity Ratio)
    
    Args:
        current_assets: Total current assets
        current_liabilities: Total current liabilities
        
    Returns:
        Current ratio
    """
    return safe_divide(current_assets, current_liabilities, 0.0)


def calculate_borrowing_base(accounts_receivable: float, inventory_value: float,
                            ar_advance_rate: Optional[float] = None,
                            inventory_advance_rate: Optional[float] = None) -> float:
    """
    Calculate borrowing base using advance rates (supports dynamic rates for scenario testing)
    
    Args:
        accounts_receivable: Total accounts receivable
        inventory_value: Total inventory value
        ar_advance_rate: Optional AR advance rate (defaults to config value)
        inventory_advance_rate: Optional inventory advance rate (defaults to config value)
        
    Returns:
        Borrowing base amount
    """
    ar_rate = ar_advance_rate if ar_advance_rate is not None else BORROWING_BASE_AR_PERCENT
    inv_rate = inventory_advance_rate if inventory_advance_rate is not None else BORROWING_BASE_INVENTORY_PERCENT
    
    ar_component = accounts_receivable * ar_rate
    inventory_component = inventory_value * inv_rate
    return ar_component + inventory_component


def calculate_revenue_loc_range(annual_revenue: float) -> Tuple[float, float]:
    """
    Calculate revenue-based LOC range
    
    Args:
        annual_revenue: Annual revenue
        
    Returns:
        Tuple of (low_range, high_range)
    """
    low = annual_revenue * REVENUE_LOC_LOW_PERCENT
    high = annual_revenue * REVENUE_LOC_HIGH_PERCENT
    return low, high


def calculate_cash_conversion_cycle(
    receivable_days: float,
    inventory_days: float,
    payable_days: float,
    business_type: str = 'Product'
) -> float:
    """
    Calculate Cash Conversion Cycle (CCC)
    For service businesses, inventory days is excluded from calculation
    
    Args:
        receivable_days: Days sales outstanding (DSO)
        inventory_days: Days inventory outstanding (DIO)
        payable_days: Days payable outstanding (DPO)
        business_type: 'Service' or 'Product' (default: 'Product')
        
    Returns:
        Cash conversion cycle in days
    """
    if business_type == 'Service':
        return receivable_days - payable_days
    return receivable_days + inventory_days - payable_days


def calculate_daily_revenue(annual_revenue: float) -> float:
    """
    Calculate daily revenue
    
    Args:
        annual_revenue: Annual revenue
        
    Returns:
        Daily revenue
    """
    return safe_divide(annual_revenue, DAYS_IN_YEAR, 0.0)


def calculate_working_capital_gap(daily_revenue: float, ccc: float) -> float:
    """
    Calculate working capital gap based on cash conversion cycle
    
    Args:
        daily_revenue: Daily revenue
        ccc: Cash conversion cycle in days
        
    Returns:
        Working capital gap amount
    """
    return daily_revenue * ccc


def calculate_final_loc_range(
    revenue_low: float,
    revenue_high: float,
    borrowing_base: float,
    working_capital_gap: float
) -> Tuple[float, float]:
    """
    Calculate final LOC range constrained by multiple factors
    
    Args:
        revenue_low: Low end of revenue-based range
        revenue_high: High end of revenue-based range
        borrowing_base: Borrowing base amount
        working_capital_gap: Working capital gap
        
    Returns:
        Tuple of (final_low, final_high)
    """
    # LOC should not exceed any of the constraining factors
    final_low = min(revenue_low, borrowing_base, working_capital_gap)
    final_high = min(revenue_high, borrowing_base, working_capital_gap)
    
    # Ensure low is not greater than high
    if final_low > final_high:
        final_low = final_high
    
    return max(0, final_low), max(0, final_high)


def determine_primary_constraint(
    revenue_high: float,
    borrowing_base: float,
    working_capital_gap: float
) -> str:
    """
    Determine which factor is the primary constraint on LOC
    
    Args:
        revenue_high: High end of revenue-based range
        borrowing_base: Borrowing base amount
        working_capital_gap: Working capital gap
        
    Returns:
        Name of primary constraint
    """
    constraints = {
        'Revenue': revenue_high,
        'Borrowing Base': borrowing_base,
        'Working Capital Gap': working_capital_gap
    }
    
    return min(constraints, key=constraints.get)


def calculate_readiness_score(
    annual_revenue: float,
    cash_flow: float,
    dscr: float,
    current_ratio: float,
    borrowing_base: float,
    years_in_business: float
) -> float:
    """
    Calculate overall financing readiness score (0-100)
    
    Args:
        annual_revenue: Annual revenue
        cash_flow: Adjusted cash flow
        dscr: Debt service coverage ratio
        current_ratio: Current ratio
        borrowing_base: Borrowing base amount
        years_in_business: Years in business
        
    Returns:
        Readiness score (0-100)
    """
    scores = {}
    
    # Revenue strength (0-100 scale)
    if annual_revenue >= 5_000_000:
        scores['revenue_strength'] = 100
    elif annual_revenue >= 1_000_000:
        scores['revenue_strength'] = 80
    elif annual_revenue >= 500_000:
        scores['revenue_strength'] = 60
    elif annual_revenue >= 250_000:
        scores['revenue_strength'] = 40
    else:
        scores['revenue_strength'] = 20
    
    # Cash flow (0-100 scale)
    if cash_flow >= 200_000:
        scores['cash_flow'] = 100
    elif cash_flow >= 100_000:
        scores['cash_flow'] = 80
    elif cash_flow >= 50_000:
        scores['cash_flow'] = 60
    elif cash_flow > 0:
        scores['cash_flow'] = 40
    else:
        scores['cash_flow'] = 0
    
    # DSCR (0-100 scale)
    if dscr >= 2.0:
        scores['dscr'] = 100
    elif dscr >= 1.5:
        scores['dscr'] = 80
    elif dscr >= 1.25:
        scores['dscr'] = 60
    elif dscr >= 1.0:
        scores['dscr'] = 40
    else:
        scores['dscr'] = 20
    
    # Liquidity (0-100 scale)
    if current_ratio >= 2.0:
        scores['liquidity'] = 100
    elif current_ratio >= 1.5:
        scores['liquidity'] = 80
    elif current_ratio >= 1.2:
        scores['liquidity'] = 60
    elif current_ratio >= 1.0:
        scores['liquidity'] = 40
    else:
        scores['liquidity'] = 20
    
    # Collateral (0-100 scale)
    if borrowing_base >= 500_000:
        scores['collateral'] = 100
    elif borrowing_base >= 250_000:
        scores['collateral'] = 80
    elif borrowing_base >= 100_000:
        scores['collateral'] = 60
    elif borrowing_base >= 50_000:
        scores['collateral'] = 40
    else:
        scores['collateral'] = 20
    
    # Business history (0-100 scale)
    if years_in_business >= 10:
        scores['business_history'] = 100
    elif years_in_business >= 5:
        scores['business_history'] = 80
    elif years_in_business >= 3:
        scores['business_history'] = 60
    elif years_in_business >= 2:
        scores['business_history'] = 40
    else:
        scores['business_history'] = 20
    
    # Calculate weighted score
    total_score = 0
    for factor, weight in READINESS_WEIGHTS.items():
        total_score += scores[factor] * (weight / 100)
    
    return round(total_score, 1)


def calculate_confidence_level(
    years_in_business: float,
    net_income: float,
    dscr: float,
    current_ratio: float,
    accounts_receivable: float,
    annual_revenue: float
) -> Tuple[str, int]:
    """
    Calculate confidence level based on key indicators
    
    Args:
        years_in_business: Years in business
        net_income: Net income
        dscr: Debt service coverage ratio
        current_ratio: Current ratio
        accounts_receivable: Accounts receivable
        annual_revenue: Annual revenue
        
    Returns:
        Tuple of (confidence_label, conditions_met)
    """
    conditions_met = 0
    
    if years_in_business > CONFIDENCE_THRESHOLDS['years_in_business']:
        conditions_met += 1
    
    if net_income > CONFIDENCE_THRESHOLDS['min_net_income']:
        conditions_met += 1
    
    if dscr > CONFIDENCE_THRESHOLDS['min_dscr']:
        conditions_met += 1
    
    if current_ratio > CONFIDENCE_THRESHOLDS['min_current_ratio']:
        conditions_met += 1
    
    ar_threshold = annual_revenue * CONFIDENCE_THRESHOLDS['min_ar_percent']
    if accounts_receivable > ar_threshold:
        conditions_met += 1
    
    # Determine label
    for (min_val, max_val), label in CONFIDENCE_LABELS.items():
        if min_val <= conditions_met <= max_val:
            return label, conditions_met
    
    return 'Low', conditions_met


def get_financing_recommendation(
    ccc: float,
    inventory_value: float,
    loc_high: float
) -> str:
    """
    Generate financing recommendation based on business characteristics
    
    Args:
        ccc: Cash conversion cycle
        inventory_value: Inventory value
        loc_high: High end of LOC range
        
    Returns:
        Recommendation string
    """
    recommendations = []
    
    if ccc < CCC_THRESHOLD:
        recommendations.append("⚠️ **LOC may not be necessary** - Your cash conversion cycle is short, indicating efficient working capital management.")
    elif inventory_value > 0:
        recommendations.append("✅ **Working Capital LOC Appropriate** - Your inventory and receivables support a revolving line of credit.")
    
    if loc_high > 0:
        recommendations.append(f"💡 Consider a line of credit up to ${loc_high:,.0f} to support working capital needs.")
    
    return " ".join(recommendations) if recommendations else "Consult with a financial advisor for personalized recommendations."


def get_improvement_suggestions(
    dscr: float,
    current_ratio: float,
    ccc: float,
    receivable_days: float
) -> list:
    """
    Generate improvement suggestions based on financial metrics
    
    Args:
        dscr: Debt service coverage ratio
        current_ratio: Current ratio
        ccc: Cash conversion cycle
        receivable_days: Days sales outstanding
        
    Returns:
        List of suggestion strings
    """
    suggestions = []
    
    if receivable_days > 45:
        suggestions.append("📊 **Improve Receivable Collections** - Your DSO is high. Consider tightening credit terms or improving collection processes.")
    
    if current_ratio < 1.2:
        suggestions.append("💰 **Increase Working Capital** - Your current ratio is below ideal levels. Focus on building cash reserves or reducing short-term liabilities.")
    
    if dscr < 1.25:
        suggestions.append("📈 **Improve Debt Service Coverage** - Increase cash flow or reduce debt obligations to improve your DSCR.")
    
    if ccc > 60:
        suggestions.append("⏱️ **Reduce Cash Conversion Cycle** - Optimize inventory management, speed up collections, or negotiate better payment terms with suppliers.")
    
    return suggestions


def validate_inputs(inputs: Dict) -> Tuple[bool, list]:
    """
    Validate all input values
    
    Args:
        inputs: Dictionary of input values
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Revenue must be positive
    if inputs.get('annual_revenue', 0) <= 0:
        errors.append("Annual revenue must be greater than 0")
    
    # AR cannot exceed revenue
    if inputs.get('accounts_receivable', 0) > inputs.get('annual_revenue', 0):
        errors.append("Accounts receivable cannot exceed annual revenue")
    
    # Days fields must be between 0 and 365
    for field in ['receivable_days', 'inventory_days', 'payable_days']:
        value = inputs.get(field, 0)
        if value < 0 or value > 365:
            errors.append(f"{field.replace('_', ' ').title()} must be between 0 and 365")
    
    # Liabilities must be non-negative
    if inputs.get('current_liabilities', 0) < 0:
        errors.append("Current liabilities must be non-negative")
    
    return len(errors) == 0, errors
