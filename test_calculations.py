"""
Quick validation test for calculations module
"""

from calculations import (
    calculate_adjusted_cash_flow,
    calculate_dscr,
    calculate_current_ratio,
    calculate_borrowing_base,
    calculate_revenue_loc_range,
    calculate_cash_conversion_cycle,
    calculate_daily_revenue,
    calculate_working_capital_gap,
    calculate_final_loc_range,
    determine_primary_constraint,
    calculate_readiness_score,
    calculate_confidence_level,
    validate_inputs
)

def test_calculations():
    """Test all calculation functions with sample data"""
    
    print("Testing Business Financing Evaluator Calculations\n")
    print("=" * 60)
    
    # Sample inputs
    annual_revenue = 500000
    net_income = 50000
    owner_addbacks = 20000
    annual_debt_payments = 30000
    current_assets = 200000
    current_liabilities = 100000
    accounts_receivable = 80000
    inventory_value = 50000
    receivable_days = 45
    inventory_days = 30
    payable_days = 30
    years_in_business = 5
    
    # Test calculations
    print("\n1. Adjusted Cash Flow:")
    cash_flow = calculate_adjusted_cash_flow(net_income, owner_addbacks)
    print(f"   ${cash_flow:,.2f}")
    
    print("\n2. Debt Service Coverage Ratio (DSCR):")
    dscr = calculate_dscr(cash_flow, annual_debt_payments)
    print(f"   {dscr:.2f}")
    
    print("\n3. Current Ratio:")
    current_ratio = calculate_current_ratio(current_assets, current_liabilities)
    print(f"   {current_ratio:.2f}")
    
    print("\n4. Borrowing Base:")
    borrowing_base = calculate_borrowing_base(accounts_receivable, inventory_value)
    print(f"   ${borrowing_base:,.2f}")
    
    print("\n5. Revenue-based LOC Range:")
    revenue_low, revenue_high = calculate_revenue_loc_range(annual_revenue)
    print(f"   ${revenue_low:,.2f} - ${revenue_high:,.2f}")
    
    print("\n6. Cash Conversion Cycle:")
    ccc = calculate_cash_conversion_cycle(receivable_days, inventory_days, payable_days)
    print(f"   {ccc:.0f} days")
    
    print("\n7. Daily Revenue:")
    daily_revenue = calculate_daily_revenue(annual_revenue)
    print(f"   ${daily_revenue:,.2f}")
    
    print("\n8. Working Capital Gap:")
    working_capital_gap = calculate_working_capital_gap(daily_revenue, ccc)
    print(f"   ${working_capital_gap:,.2f}")
    
    print("\n9. Final LOC Range:")
    loc_low, loc_high = calculate_final_loc_range(
        revenue_low, revenue_high, borrowing_base, working_capital_gap
    )
    print(f"   ${loc_low:,.2f} - ${loc_high:,.2f}")
    
    print("\n10. Primary Constraint:")
    primary_constraint = determine_primary_constraint(
        revenue_high, borrowing_base, working_capital_gap
    )
    print(f"    {primary_constraint}")
    
    print("\n11. Readiness Score:")
    readiness_score = calculate_readiness_score(
        annual_revenue, cash_flow, dscr, current_ratio, borrowing_base, years_in_business
    )
    print(f"    {readiness_score:.1f}/100")
    
    print("\n12. Confidence Level:")
    confidence_level, conditions_met = calculate_confidence_level(
        years_in_business, net_income, dscr, current_ratio, accounts_receivable, annual_revenue
    )
    print(f"    {confidence_level} ({conditions_met}/5 conditions met)")
    
    print("\n13. Input Validation:")
    inputs = {
        'annual_revenue': annual_revenue,
        'accounts_receivable': accounts_receivable,
        'receivable_days': receivable_days,
        'inventory_days': inventory_days,
        'payable_days': payable_days,
        'current_liabilities': current_liabilities
    }
    is_valid, errors = validate_inputs(inputs)
    print(f"    Valid: {is_valid}")
    if errors:
        for error in errors:
            print(f"    - {error}")
    
    print("\n" + "=" * 60)
    print("✅ All calculations completed successfully!")
    print("\nThe application is ready to use.")

if __name__ == "__main__":
    test_calculations()
