"""
Enhanced validation module for Business Financing Readiness Tool
Provides comprehensive input validation with user-friendly error messages
"""

from typing import Dict, List, Tuple


class ValidationError:
    """Represents a validation error with field and message"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
    
    def __str__(self):
        return f"{self.field}: {self.message}"


def validate_annual_revenue(revenue: float) -> List[ValidationError]:
    """Validate annual revenue"""
    errors = []
    if revenue <= 0:
        errors.append(ValidationError(
            'Annual Revenue',
            'Annual revenue must be greater than $0.'
        ))
    return errors


def validate_accounts_receivable(ar: float, revenue: float) -> List[ValidationError]:
    """Validate accounts receivable against revenue"""
    errors = []
    if ar < 0:
        errors.append(ValidationError(
            'Accounts Receivable',
            'Accounts receivable cannot be negative.'
        ))
    if ar > revenue:
        errors.append(ValidationError(
            'Accounts Receivable',
            'Accounts receivable cannot exceed annual revenue.'
        ))
    return errors


def validate_days_field(field_name: str, days: float) -> List[ValidationError]:
    """Validate days fields (DSO, DIO, DPO)"""
    errors = []
    if days < 0 or days > 365:
        errors.append(ValidationError(
            field_name,
            'Days fields must be between 0 and 365.'
        ))
    return errors


def validate_liabilities(liabilities: float) -> List[ValidationError]:
    """Validate current liabilities"""
    errors = []
    if liabilities < 0:
        errors.append(ValidationError(
            'Current Liabilities',
            'Current liabilities cannot be negative.'
        ))
    return errors


def validate_positive_or_zero(field_name: str, value: float) -> List[ValidationError]:
    """Validate that a field is non-negative"""
    errors = []
    if value < 0:
        errors.append(ValidationError(
            field_name,
            f'{field_name} cannot be negative.'
        ))
    return errors


def validate_all_inputs(inputs: Dict, business_type: str = 'Product') -> Tuple[bool, List[ValidationError]]:
    """
    Comprehensive validation of all inputs
    
    Args:
        inputs: Dictionary of input values
        business_type: 'Service' or 'Product' to determine which validations apply
        
    Returns:
        Tuple of (is_valid, list of ValidationError objects)
    """
    errors = []
    
    # Revenue validation
    errors.extend(validate_annual_revenue(inputs.get('annual_revenue', 0)))
    
    # Accounts receivable validation
    errors.extend(validate_accounts_receivable(
        inputs.get('accounts_receivable', 0),
        inputs.get('annual_revenue', 0)
    ))
    
    # Days fields validation
    errors.extend(validate_days_field('Receivable Days', inputs.get('receivable_days', 0)))
    
    # Only validate inventory days for Product businesses
    if business_type == 'Product':
        errors.extend(validate_days_field('Inventory Days', inputs.get('inventory_days', 0)))
    
    errors.extend(validate_days_field('Payable Days', inputs.get('payable_days', 0)))
    
    # Liabilities validation
    errors.extend(validate_liabilities(inputs.get('current_liabilities', 0)))
    
    # Other non-negative validations
    errors.extend(validate_positive_or_zero('Current Assets', inputs.get('current_assets', 0)))
    errors.extend(validate_positive_or_zero('Years in Business', inputs.get('years_in_business', 0)))
    errors.extend(validate_positive_or_zero('Owner Addbacks', inputs.get('owner_addbacks', 0)))
    errors.extend(validate_positive_or_zero('Annual Debt Payments', inputs.get('annual_debt_payments', 0)))
    
    # Inventory validation only for Product businesses
    if business_type == 'Product':
        errors.extend(validate_positive_or_zero('Inventory Value', inputs.get('inventory_value', 0)))
    
    return len(errors) == 0, errors


def get_validation_summary(errors: List[ValidationError]) -> str:
    """
    Generate a formatted validation summary
    
    Args:
        errors: List of ValidationError objects
        
    Returns:
        Formatted error message string
    """
    if not errors:
        return "All inputs are valid."
    
    summary = f"**{len(errors)} Validation Error{'s' if len(errors) > 1 else ''}:**\n\n"
    for error in errors:
        summary += f"• **{error.field}**: {error.message}\n"
    
    return summary


def validate_business_logic(inputs: Dict, business_type: str = 'Product') -> List[ValidationError]:
    """
    Validate business logic rules beyond basic input validation
    
    Args:
        inputs: Dictionary of input values
        business_type: 'Service' or 'Product'
        
    Returns:
        List of ValidationError objects for business logic issues
    """
    warnings = []
    
    # Check if debt payments exceed cash flow
    net_income = inputs.get('net_income', 0)
    owner_addbacks = inputs.get('owner_addbacks', 0)
    annual_debt_payments = inputs.get('annual_debt_payments', 0)
    cash_flow = net_income + owner_addbacks
    
    if annual_debt_payments > 0 and cash_flow < annual_debt_payments:
        warnings.append(ValidationError(
            'Debt Service',
            f'Cash flow (${cash_flow:,.0f}) is less than annual debt payments (${annual_debt_payments:,.0f}). DSCR will be below 1.0.'
        ))
    
    # Check if current liabilities exceed current assets
    current_assets = inputs.get('current_assets', 0)
    current_liabilities = inputs.get('current_liabilities', 0)
    
    if current_liabilities > 0 and current_assets < current_liabilities:
        warnings.append(ValidationError(
            'Liquidity',
            f'Current assets (${current_assets:,.0f}) are less than current liabilities (${current_liabilities:,.0f}). Current ratio will be below 1.0.'
        ))
    
    # Check for unusually high receivable days
    receivable_days = inputs.get('receivable_days', 0)
    if receivable_days > 90:
        warnings.append(ValidationError(
            'Receivable Days',
            f'Receivable days ({receivable_days:.0f}) is unusually high. Consider reviewing collection practices.'
        ))
    
    # Check for inventory days (Product businesses only)
    if business_type == 'Product':
        inventory_days = inputs.get('inventory_days', 0)
        if inventory_days > 120:
            warnings.append(ValidationError(
                'Inventory Days',
                f'Inventory days ({inventory_days:.0f}) is unusually high. This may indicate slow-moving inventory.'
            ))
    
    return warnings
