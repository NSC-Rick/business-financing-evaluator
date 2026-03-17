"""
LOC Sizing Tool - Cash-Flow-First MVP
A Streamlit tool for estimating appropriate line of credit based on cash flow timing,
cash trough analysis, and risk buffering.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime
from typing import Dict, List, Tuple
import numpy as np


# ============================================================================
# CORE CALCULATION FUNCTIONS
# ============================================================================

def calculate_quick_estimate(
    monthly_expenses: float,
    days_to_get_paid: float,
    monthly_debt_payments: float,
    payroll_intensity: str,
    seasonality_volatility: str
) -> Dict:
    """
    Calculate LOC estimate using quick method based on timing gap and risk multipliers.
    
    Args:
        monthly_expenses: Average monthly operating expenses
        days_to_get_paid: Average days to receive payment
        monthly_debt_payments: Average monthly debt service
        payroll_intensity: Low/Medium/High
        seasonality_volatility: Low/Medium/High
        
    Returns:
        Dictionary with min_loc, recommended_loc, stress_loc, and explanation
    """
    # Base gap calculation
    base_gap = monthly_expenses * (days_to_get_paid / 30)
    
    # Add debt service
    total_gap = base_gap + monthly_debt_payments
    
    # Risk multiplier based on payroll intensity
    payroll_multipliers = {
        'Low': 1.0,
        'Medium': 1.15,
        'High': 1.25
    }
    
    # Volatility multiplier
    volatility_multipliers = {
        'Low': 1.0,
        'Medium': 1.20,
        'High': 1.35
    }
    
    payroll_mult = payroll_multipliers.get(payroll_intensity, 1.0)
    volatility_mult = volatility_multipliers.get(seasonality_volatility, 1.0)
    
    # Combined risk multiplier
    combined_multiplier = payroll_mult * volatility_mult
    
    # Calculate LOC amounts
    minimum_loc = total_gap
    recommended_loc = total_gap * combined_multiplier
    stress_loc = recommended_loc * 1.15
    
    # Build explanation
    explanation = f"""
    **Quick Estimate Analysis:**
    
    - Base working capital gap: ${base_gap:,.0f} (expenses × payment delay)
    - Monthly debt service: ${monthly_debt_payments:,.0f}
    - Total baseline gap: ${total_gap:,.0f}
    - Risk adjustment: {combined_multiplier:.2f}x (payroll: {payroll_mult:.2f}x, volatility: {volatility_mult:.2f}x)
    
    This estimate assumes you need to cover operating expenses during the payment collection window,
    plus debt obligations, with risk buffers for payroll timing and business volatility.
    """
    
    return {
        'minimum_loc': minimum_loc,
        'recommended_loc': recommended_loc,
        'stress_loc': stress_loc,
        'lowest_cash': -total_gap,
        'explanation': explanation,
        'key_drivers': [
            f"Payment delay: {days_to_get_paid:.0f} days",
            f"Monthly expenses: ${monthly_expenses:,.0f}",
            f"Risk multiplier: {combined_multiplier:.2f}x"
        ]
    }


def calculate_guided_estimate(
    current_cash: float,
    monthly_revenue: float,
    monthly_expenses: float,
    days_to_get_paid: float,
    days_to_pay_vendors: float,
    largest_expense_spike: float,
    seasonal_weak_months: List[int],
    growth_pressure: bool,
    revenue_stability: int,
    expense_predictability: int,
    buffer_profile: str
) -> Dict:
    """
    Generate synthetic 12-month cash curve and calculate LOC based on trough analysis.
    
    Args:
        current_cash: Starting cash position
        monthly_revenue: Average monthly revenue
        monthly_expenses: Average monthly operating expenses
        days_to_get_paid: Average collection period
        days_to_pay_vendors: Average payment period
        largest_expense_spike: Largest expected monthly expense spike
        seasonal_weak_months: List of weak month indices (0-11)
        growth_pressure: Whether business is under growth strain
        revenue_stability: 1-5 scale (1=very unstable, 5=very stable)
        expense_predictability: 1-5 scale (1=very unpredictable, 5=very predictable)
        buffer_profile: Conservative/Moderate/Aggressive
        
    Returns:
        Dictionary with LOC calculations and monthly cash flow data
    """
    # Buffer multipliers
    buffer_multipliers = {
        'Conservative': 1.10,
        'Moderate': 1.20,
        'Aggressive': 1.30
    }
    buffer_mult = buffer_multipliers.get(buffer_profile, 1.20)
    
    # Initialize monthly cash flow
    months = []
    cash_balances = []
    cash_in = []
    cash_out = []
    
    current_balance = current_cash
    
    # Calculate payment timing factors
    inflow_delay_factor = days_to_get_paid / 30
    outflow_delay_benefit = days_to_pay_vendors / 30
    
    # Stability factors affect variance
    revenue_variance = (6 - revenue_stability) * 0.05  # 0-20% variance
    expense_variance = (6 - expense_predictability) * 0.04  # 0-16% variance
    
    for month in range(12):
        # Calculate this month's revenue (with delays and variance)
        base_revenue = monthly_revenue
        
        # Apply seasonal weakness
        if month in seasonal_weak_months:
            base_revenue *= 0.70  # 30% reduction in weak months
        
        # Apply random variance based on stability
        revenue_factor = 1.0 + np.random.uniform(-revenue_variance, revenue_variance)
        month_revenue = base_revenue * revenue_factor
        
        # Apply collection delay - only collect portion of revenue this month
        month_cash_in = month_revenue * (1 - inflow_delay_factor * 0.5)
        
        # Calculate this month's expenses
        base_expenses = monthly_expenses
        
        # Apply expense variance
        expense_factor = 1.0 + np.random.uniform(-expense_variance, expense_variance)
        month_expenses = base_expenses * expense_factor
        
        # Add expense spike if applicable
        if month == 6:  # Mid-year spike
            month_expenses += largest_expense_spike
        
        # Apply growth pressure (10% higher expenses if growing)
        if growth_pressure:
            month_expenses *= 1.10
        
        # Apply payment delay benefit - delay some payments
        month_cash_out = month_expenses * (1 - outflow_delay_benefit * 0.3)
        
        # Calculate ending balance
        net_change = month_cash_in - month_cash_out
        ending_balance = current_balance + net_change
        
        # Store data
        months.append(f"Month {month + 1}")
        cash_balances.append(ending_balance)
        cash_in.append(month_cash_in)
        cash_out.append(month_cash_out)
        
        # Update for next month
        current_balance = ending_balance
    
    # Find the trough (lowest point)
    lowest_cash = min(cash_balances)
    trough_month = cash_balances.index(lowest_cash) + 1
    
    # Calculate LOC amounts
    if lowest_cash < 0:
        minimum_loc = abs(lowest_cash)
    else:
        minimum_loc = 0
    
    recommended_loc = minimum_loc * buffer_mult
    stress_loc = recommended_loc * 1.15
    
    # Build explanation
    avg_monthly_gap = np.mean([out - in_ for in_, out in zip(cash_in, cash_out)])
    
    explanation = f"""
    **Guided Estimate Analysis:**
    
    - Starting cash: ${current_cash:,.0f}
    - Projected lowest cash point: ${lowest_cash:,.0f} (Month {trough_month})
    - Average monthly gap: ${avg_monthly_gap:,.0f}
    - Buffer applied: {buffer_mult:.0%}
    - Weak months modeled: {len(seasonal_weak_months)} months at 70% revenue
    - Collection delay: {days_to_get_paid:.0f} days reduces immediate cash inflow
    - Payment terms: {days_to_pay_vendors:.0f} days provides some cash retention
    
    The recommended LOC provides a cushion for timing gaps, seasonal weakness, and unexpected expenses
    while maintaining operational stability.
    """
    
    key_drivers = [
        f"Cash trough: ${lowest_cash:,.0f} in Month {trough_month}",
        f"Revenue stability: {revenue_stability}/5",
        f"Seasonal weak months: {len(seasonal_weak_months)}",
        f"Buffer profile: {buffer_profile}"
    ]
    
    return {
        'minimum_loc': minimum_loc,
        'recommended_loc': recommended_loc,
        'stress_loc': stress_loc,
        'lowest_cash': lowest_cash,
        'explanation': explanation,
        'key_drivers': key_drivers,
        'monthly_data': {
            'months': months,
            'cash_balances': cash_balances,
            'cash_in': cash_in,
            'cash_out': cash_out
        }
    }


def calculate_full_monthly_flow(
    current_cash: float,
    monthly_data: pd.DataFrame,
    buffer_profile: str
) -> Dict:
    """
    Calculate LOC based on actual 12-month cash flow entries.
    
    Args:
        current_cash: Starting cash position
        monthly_data: DataFrame with columns: cash_in, operating_cash_out, debt_service, owner_draws
        buffer_profile: Conservative/Moderate/Aggressive
        
    Returns:
        Dictionary with LOC calculations and cash flow analysis
    """
    # Buffer multipliers
    buffer_multipliers = {
        'Conservative': 1.10,
        'Moderate': 1.20,
        'Aggressive': 1.30
    }
    buffer_mult = buffer_multipliers.get(buffer_profile, 1.20)
    
    # Calculate running cash balances
    months = []
    beginning_cash = []
    ending_cash = []
    
    current_balance = current_cash
    
    for idx, row in monthly_data.iterrows():
        beginning_balance = current_balance
        
        # Calculate net change
        total_out = row['operating_cash_out'] + row['debt_service'] + row['owner_draws']
        net_change = row['cash_in'] - total_out
        ending_balance = beginning_balance + net_change
        
        # Store data
        months.append(f"Month {idx + 1}")
        beginning_cash.append(beginning_balance)
        ending_cash.append(ending_balance)
        
        # Update for next month
        current_balance = ending_balance
    
    # Find the trough
    lowest_cash = min(ending_cash)
    trough_month = ending_cash.index(lowest_cash) + 1
    
    # Calculate LOC amounts
    if lowest_cash < 0:
        minimum_loc = abs(lowest_cash)
    else:
        minimum_loc = 0
    
    recommended_loc = minimum_loc * buffer_mult
    stress_loc = recommended_loc * 1.15
    
    # Calculate statistics
    total_cash_in = monthly_data['cash_in'].sum()
    total_cash_out = (monthly_data['operating_cash_out'] + 
                      monthly_data['debt_service'] + 
                      monthly_data['owner_draws']).sum()
    avg_monthly_deficit = (total_cash_out - total_cash_in) / 12
    
    negative_months = sum(1 for balance in ending_cash if balance < 0)
    
    explanation = f"""
    **Full Monthly Cash Flow Analysis:**
    
    - Starting cash: ${current_cash:,.0f}
    - Projected lowest cash point: ${lowest_cash:,.0f} (Month {trough_month})
    - Total 12-month cash in: ${total_cash_in:,.0f}
    - Total 12-month cash out: ${total_cash_out:,.0f}
    - Average monthly deficit: ${avg_monthly_deficit:,.0f}
    - Months with negative cash: {negative_months}
    - Buffer applied: {buffer_mult:.0%}
    
    Based on your detailed monthly projections, the recommended LOC covers your deepest cash trough
    plus a safety buffer for unexpected timing issues or expense overruns.
    """
    
    key_drivers = [
        f"Cash trough: ${lowest_cash:,.0f} in Month {trough_month}",
        f"Negative cash months: {negative_months}",
        f"Avg monthly deficit: ${avg_monthly_deficit:,.0f}",
        f"Buffer profile: {buffer_profile}"
    ]
    
    return {
        'minimum_loc': minimum_loc,
        'recommended_loc': recommended_loc,
        'stress_loc': stress_loc,
        'lowest_cash': lowest_cash,
        'explanation': explanation,
        'key_drivers': key_drivers,
        'monthly_data': {
            'months': months,
            'beginning_cash': beginning_cash,
            'ending_cash': ending_cash,
            'cash_in': monthly_data['cash_in'].tolist(),
            'cash_out': (monthly_data['operating_cash_out'] + 
                        monthly_data['debt_service'] + 
                        monthly_data['owner_draws']).tolist()
        }
    }


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_cash_balance_chart(monthly_data: Dict) -> go.Figure:
    """Create cash balance trend chart."""
    fig = go.Figure()
    
    months = monthly_data['months']
    
    # Determine which balance data to use
    if 'ending_cash' in monthly_data:
        balances = monthly_data['ending_cash']
        title = "Projected Cash Balance (12 Months)"
    else:
        balances = monthly_data['cash_balances']
        title = "Projected Cash Balance (12 Months)"
    
    # Add cash balance line
    fig.add_trace(go.Scatter(
        x=months,
        y=balances,
        mode='lines+markers',
        name='Cash Balance',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="red", 
                  annotation_text="Zero Cash Line", annotation_position="right")
    
    # Highlight lowest point
    min_balance = min(balances)
    min_idx = balances.index(min_balance)
    fig.add_trace(go.Scatter(
        x=[months[min_idx]],
        y=[min_balance],
        mode='markers',
        name='Lowest Point',
        marker=dict(size=15, color='red', symbol='star')
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Month",
        yaxis_title="Cash Balance ($)",
        hovermode='x unified',
        showlegend=True,
        height=400
    )
    
    return fig


def create_funding_gap_chart(monthly_data: Dict) -> go.Figure:
    """Create chart showing months with negative cash (funding gaps)."""
    months = monthly_data['months']
    
    # Determine which balance data to use
    if 'ending_cash' in monthly_data:
        balances = monthly_data['ending_cash']
    else:
        balances = monthly_data['cash_balances']
    
    # Calculate funding gaps (only negative values)
    funding_gaps = [abs(bal) if bal < 0 else 0 for bal in balances]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=months,
        y=funding_gaps,
        name='Funding Gap',
        marker_color='#d62728'
    ))
    
    fig.update_layout(
        title="Monthly Funding Gaps (Negative Cash Positions)",
        xaxis_title="Month",
        yaxis_title="Funding Gap Required ($)",
        hovermode='x unified',
        showlegend=False,
        height=350
    )
    
    return fig


def create_cash_flow_waterfall(monthly_data: Dict) -> go.Figure:
    """Create waterfall chart showing cash in vs cash out."""
    months = monthly_data['months']
    cash_in = monthly_data['cash_in']
    cash_out = monthly_data['cash_out']
    
    # Calculate net for each month
    net_flow = [in_ - out for in_, out in zip(cash_in, cash_out)]
    
    fig = go.Figure()
    
    colors = ['green' if net >= 0 else 'red' for net in net_flow]
    
    fig.add_trace(go.Bar(
        x=months,
        y=net_flow,
        name='Net Cash Flow',
        marker_color=colors
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    fig.update_layout(
        title="Monthly Net Cash Flow",
        xaxis_title="Month",
        yaxis_title="Net Cash Flow ($)",
        hovermode='x unified',
        showlegend=False,
        height=350
    )
    
    return fig


# ============================================================================
# STREAMLIT UI
# ============================================================================

def main():
    st.set_page_config(
        page_title="LOC Sizing Tool",
        page_icon="💰",
        layout="wide"
    )
    
    st.title("💰 Line of Credit Sizing Tool")
    st.markdown("**Cash-Flow-First Analysis** — Size your LOC based on actual working capital compression, not revenue percentages")
    
    # Sidebar - Mode Selection and Buffer Profile
    st.sidebar.header("⚙️ Configuration")
    
    mode = st.sidebar.radio(
        "Analysis Mode",
        options=['Quick Estimate', 'Guided Estimate', 'Full Monthly Cash Flow'],
        index=1,
        help="Choose your analysis depth based on available data"
    )
    
    buffer_profile = st.sidebar.selectbox(
        "Buffer Profile",
        options=['Conservative', 'Moderate', 'Aggressive'],
        index=1,
        help="Conservative: 10% buffer | Moderate: 20% buffer | Aggressive: 30% buffer"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    **About This Tool:**
    
    This tool estimates LOC needs based on:
    - Cash flow timing gaps
    - Working capital compression
    - Risk buffering
    
    Not based on % of revenue.
    """)
    
    # Main Content Area
    st.header("📋 Business Snapshot")
    
    # Shared Inputs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        business_name = st.text_input("Business Name", value="My Business")
        industry = st.text_input("Industry / Business Type", value="Professional Services")
    
    with col2:
        current_cash = st.number_input(
            "Current Cash on Hand ($)",
            min_value=0.0,
            value=25000.0,
            step=1000.0,
            help="Your current cash balance"
        )
        
        existing_loc = st.number_input(
            "Existing LOC Limit ($)",
            min_value=0.0,
            value=0.0,
            step=5000.0,
            help="Current line of credit limit (if any)"
        )
    
    with col3:
        revenue_pattern = st.selectbox(
            "Revenue Pattern",
            options=['Steady', 'Seasonal', 'Project-Based', 'Subscription'],
            help="How revenue flows into the business"
        )
    
    st.markdown("---")
    
    # Mode-Specific Inputs and Calculations
    results = None
    
    if mode == 'Quick Estimate':
        st.header("⚡ Quick Estimate")
        st.markdown("*Get a rapid estimate based on key timing and risk factors*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_expenses = st.number_input(
                "Average Monthly Operating Expenses ($)",
                min_value=0.0,
                value=50000.0,
                step=5000.0
            )
            
            days_to_get_paid = st.number_input(
                "Average Days to Get Paid",
                min_value=0.0,
                value=45.0,
                step=5.0,
                help="Average collection period for receivables"
            )
            
            monthly_debt_payments = st.number_input(
                "Average Monthly Debt Payments ($)",
                min_value=0.0,
                value=5000.0,
                step=1000.0
            )
        
        with col2:
            payroll_intensity = st.select_slider(
                "Payroll Intensity",
                options=['Low', 'Medium', 'High'],
                value='Medium',
                help="Low: <30% of expenses | Medium: 30-60% | High: >60%"
            )
            
            seasonality_volatility = st.select_slider(
                "Seasonality / Volatility",
                options=['Low', 'Medium', 'High'],
                value='Medium',
                help="How much revenue varies month-to-month"
            )
        
        if st.button("Calculate Quick Estimate", type="primary"):
            results = calculate_quick_estimate(
                monthly_expenses,
                days_to_get_paid,
                monthly_debt_payments,
                payroll_intensity,
                seasonality_volatility
            )
    
    elif mode == 'Guided Estimate':
        st.header("🎯 Guided Estimate")
        st.markdown("*Generate a synthetic 12-month cash curve based on your business patterns*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Revenue & Expenses")
            
            monthly_revenue = st.number_input(
                "Average Monthly Revenue ($)",
                min_value=0.0,
                value=75000.0,
                step=5000.0
            )
            
            monthly_expenses = st.number_input(
                "Average Monthly Operating Expenses ($)",
                min_value=0.0,
                value=50000.0,
                step=5000.0
            )
            
            st.subheader("Timing Factors")
            
            days_to_get_paid = st.number_input(
                "Average Days to Get Paid",
                min_value=0.0,
                value=45.0,
                step=5.0
            )
            
            days_to_pay_vendors = st.number_input(
                "Average Days to Pay Vendors",
                min_value=0.0,
                value=30.0,
                step=5.0
            )
        
        with col2:
            st.subheader("Risk Factors")
            
            largest_expense_spike = st.number_input(
                "Largest Expected Monthly Expense Spike ($)",
                min_value=0.0,
                value=15000.0,
                step=5000.0,
                help="One-time or irregular large expense"
            )
            
            seasonal_weak_months = st.multiselect(
                "Seasonal Weak Months",
                options=list(range(1, 13)),
                default=[7, 8],
                help="Months with typically lower revenue (1=Jan, 12=Dec)"
            )
            
            growth_pressure = st.checkbox(
                "Under Growth Pressure",
                value=False,
                help="Check if expanding and incurring growth-related costs"
            )
            
            st.subheader("Stability Assessment")
            
            revenue_stability = st.slider(
                "Revenue Stability",
                min_value=1,
                max_value=5,
                value=3,
                help="1=Very Unstable | 5=Very Stable"
            )
            
            expense_predictability = st.slider(
                "Expense Predictability",
                min_value=1,
                max_value=5,
                value=3,
                help="1=Very Unpredictable | 5=Very Predictable"
            )
        
        # Convert month numbers to 0-indexed
        seasonal_weak_months_idx = [m - 1 for m in seasonal_weak_months]
        
        if st.button("Generate Guided Estimate", type="primary"):
            results = calculate_guided_estimate(
                current_cash,
                monthly_revenue,
                monthly_expenses,
                days_to_get_paid,
                days_to_pay_vendors,
                largest_expense_spike,
                seasonal_weak_months_idx,
                growth_pressure,
                revenue_stability,
                expense_predictability,
                buffer_profile
            )
    
    else:  # Full Monthly Cash Flow
        st.header("📊 Full Monthly Cash Flow")
        st.markdown("*Enter your detailed 12-month cash flow projections*")
        
        # Create editable dataframe
        default_data = {
            'Month': [f'Month {i+1}' for i in range(12)],
            'Cash In': [75000.0] * 12,
            'Operating Cash Out': [50000.0] * 12,
            'Debt Service': [5000.0] * 12,
            'Owner Draws': [3000.0] * 12
        }
        
        df = pd.DataFrame(default_data)
        
        st.markdown("**Edit the table below with your projected monthly cash flows:**")
        
        edited_df = st.data_editor(
            df,
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                "Month": st.column_config.TextColumn("Month", disabled=True),
                "Cash In": st.column_config.NumberColumn("Cash In ($)", format="$%.0f"),
                "Operating Cash Out": st.column_config.NumberColumn("Operating Cash Out ($)", format="$%.0f"),
                "Debt Service": st.column_config.NumberColumn("Debt Service ($)", format="$%.0f"),
                "Owner Draws": st.column_config.NumberColumn("Owner Draws ($)", format="$%.0f")
            }
        )
        
        if st.button("Calculate from Monthly Data", type="primary"):
            # Prepare data for calculation
            calc_df = pd.DataFrame({
                'cash_in': edited_df['Cash In'],
                'operating_cash_out': edited_df['Operating Cash Out'],
                'debt_service': edited_df['Debt Service'],
                'owner_draws': edited_df['Owner Draws']
            })
            
            results = calculate_full_monthly_flow(
                current_cash,
                calc_df,
                buffer_profile
            )
    
    # Display Results
    if results:
        st.markdown("---")
        st.header("📈 Results & Recommendations")
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Minimum LOC",
                value=f"${results['minimum_loc']:,.0f}",
                help="Minimum to cover deepest cash trough"
            )
        
        with col2:
            st.metric(
                label="Recommended LOC",
                value=f"${results['recommended_loc']:,.0f}",
                help="Recommended with safety buffer"
            )
        
        with col3:
            st.metric(
                label="Stress-Test LOC",
                value=f"${results['stress_loc']:,.0f}",
                help="Conservative estimate for worst-case"
            )
        
        with col4:
            st.metric(
                label="Lowest Cash Position",
                value=f"${results['lowest_cash']:,.0f}",
                delta=f"${results['lowest_cash'] - current_cash:,.0f}",
                delta_color="inverse"
            )
        
        # LOC Gap Analysis
        if existing_loc > 0:
            st.markdown("---")
            st.subheader("📊 Current LOC Gap Analysis")
            
            gap = results['recommended_loc'] - existing_loc
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    label="Current LOC Limit",
                    value=f"${existing_loc:,.0f}"
                )
            
            with col2:
                if gap > 0:
                    st.metric(
                        label="LOC Gap (Shortfall)",
                        value=f"${gap:,.0f}",
                        delta=f"{(gap/existing_loc)*100:.1f}% increase needed",
                        delta_color="normal"
                    )
                else:
                    st.metric(
                        label="LOC Gap (Surplus)",
                        value=f"${abs(gap):,.0f}",
                        delta="Adequate coverage",
                        delta_color="off"
                    )
        
        # Key Drivers
        st.markdown("---")
        st.subheader("🔑 Key Drivers")
        
        for driver in results['key_drivers']:
            st.markdown(f"- {driver}")
        
        # Explanation
        st.markdown("---")
        st.subheader("📝 Analysis Narrative")
        st.markdown(results['explanation'])
        
        # Visualizations (if monthly data available)
        if 'monthly_data' in results:
            st.markdown("---")
            st.subheader("📊 Cash Flow Visualizations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_balance = create_cash_balance_chart(results['monthly_data'])
                st.plotly_chart(fig_balance, use_container_width=True)
            
            with col2:
                fig_gap = create_funding_gap_chart(results['monthly_data'])
                st.plotly_chart(fig_gap, use_container_width=True)
            
            # Cash flow waterfall
            if 'cash_in' in results['monthly_data'] and 'cash_out' in results['monthly_data']:
                fig_waterfall = create_cash_flow_waterfall(results['monthly_data'])
                st.plotly_chart(fig_waterfall, use_container_width=True)
        
        # Downloadable Summary
        st.markdown("---")
        st.subheader("💾 Export Results")
        
        summary_data = {
            'business_name': business_name,
            'industry': industry,
            'analysis_date': datetime.now().isoformat(),
            'mode': mode,
            'buffer_profile': buffer_profile,
            'current_cash': current_cash,
            'existing_loc': existing_loc,
            'results': {
                'minimum_loc': results['minimum_loc'],
                'recommended_loc': results['recommended_loc'],
                'stress_loc': results['stress_loc'],
                'lowest_cash': results['lowest_cash']
            },
            'key_drivers': results['key_drivers']
        }
        
        json_str = json.dumps(summary_data, indent=2)
        
        st.download_button(
            label="Download Summary (JSON)",
            data=json_str,
            file_name=f"loc_sizing_{business_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )


if __name__ == "__main__":
    main()
