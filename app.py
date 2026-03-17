"""
Business Financing Readiness Tool - Main Streamlit Application
Line of Credit & Working Capital Evaluator
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
import json

from config import (
    PAGE_CONFIG,
    INDUSTRIES,
    BUSINESS_TYPES,
    COLORS,
    RISK_TOLERANCE_SCENARIOS,
    REVENUE_LOC_LOW_PERCENT
)
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
    get_financing_recommendation,
    get_improvement_suggestions
)
from json_io import (
    create_project_data,
    save_project,
    load_project,
    list_saved_projects,
    export_to_json_string
)
from validation import (
    validate_all_inputs,
    get_validation_summary,
    validate_business_logic
)
from ui_components import (
    render_lender_metrics_info_panel,
    render_assumptions_panel,
    render_readiness_status_badge,
    create_enhanced_ccc_chart,
    create_enhanced_readiness_gauge,
    render_metric_cards_row,
    render_lender_view_section,
    render_financing_summary_block,
    render_borrower_strength_panel
)


def initialize_session_state():
    """Initialize session state variables"""
    if 'inputs' not in st.session_state:
        st.session_state.inputs = {}
    if 'results' not in st.session_state:
        st.session_state.results = {}
    if 'project_name' not in st.session_state:
        st.session_state.project_name = "My Business Analysis"
    if 'project_notes' not in st.session_state:
        st.session_state.project_notes = ""
    if 'lender_view_mode' not in st.session_state:
        st.session_state.lender_view_mode = False
    if 'risk_tolerance' not in st.session_state:
        st.session_state.risk_tolerance = 'Balanced'


def reset_analysis():
    """Reset all session state for new analysis"""
    keys_to_keep = ['lender_view_mode', 'risk_tolerance']
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    initialize_session_state()


def main():
    """Main application function"""
    
    # Page configuration
    st.set_page_config(**PAGE_CONFIG)
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("💼 Business Financing Readiness Tool")
    st.subheader("Line of Credit & Working Capital Evaluator")
    
    # Video placeholder
    with st.expander("📹 How to Use This Tool", expanded=False):
        st.info("**Video Tutorial Coming Soon**")
        st.markdown("""
        This tool helps you:
        - Estimate an appropriate working capital line of credit
        - Understand key financial metrics lenders evaluate
        - Identify areas for improvement in your business finances
        - Calculate your cash conversion cycle
        - Assess your financing readiness
        """)
    
    st.markdown("---")
    
    # Sidebar for project management
    with st.sidebar:
        st.header("📁 Project Management")
        
        st.session_state.project_name = st.text_input(
            "Project Name",
            value=st.session_state.project_name
        )
        
        # Save/Load functionality
        st.subheader("Save/Load Project")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save", use_container_width=True):
                if st.session_state.inputs:
                    project_data = create_project_data(
                        st.session_state.project_name,
                        st.session_state.project_notes,
                        st.session_state.inputs,
                        st.session_state.results
                    )
                    success, message = save_project(project_data)
                    if success:
                        st.success(f"Saved to: {message}")
                    else:
                        st.error(message)
                else:
                    st.warning("No data to save. Please fill in the form first.")
        
        with col2:
            if st.button("📂 Load", use_container_width=True):
                st.session_state.show_load = True
        
        # Load project interface
        if st.session_state.get('show_load', False):
            saved_projects = list_saved_projects()
            if saved_projects:
                project_options = {f"{name} ({datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')})": path 
                                 for name, path, mtime in saved_projects}
                
                selected = st.selectbox("Select a project:", list(project_options.keys()))
                
                if st.button("Load Selected Project"):
                    filepath = project_options[selected]
                    success, project_data, message = load_project(filepath)
                    
                    if success:
                        st.session_state.inputs = project_data['inputs']
                        st.session_state.project_name = project_data['project_name']
                        st.session_state.project_notes = project_data.get('project_notes', '')
                        st.session_state.results = project_data.get('results', {})
                        st.success(message)
                        st.session_state.show_load = False
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.info("No saved projects found.")
        
        st.markdown("---")
        
        # Download current analysis
        if st.session_state.inputs:
            st.subheader("📥 Export Analysis")
            project_data = create_project_data(
                st.session_state.project_name,
                st.session_state.project_notes,
                st.session_state.inputs,
                st.session_state.results
            )
            json_str = export_to_json_string(project_data)
            
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"financing_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        st.markdown("---")
        
        # Scenario Testing - Risk Tolerance
        st.subheader("🎯 Scenario Testing")
        st.session_state.risk_tolerance = st.selectbox(
            "Lender Risk Tolerance",
            options=list(RISK_TOLERANCE_SCENARIOS.keys()),
            index=list(RISK_TOLERANCE_SCENARIOS.keys()).index(st.session_state.risk_tolerance),
            help="Adjust advance rates based on lender risk profile"
        )
        
        scenario = RISK_TOLERANCE_SCENARIOS[st.session_state.risk_tolerance]
        st.caption(scenario['description'])
        st.caption(f"AR: {scenario['ar_advance']*100:.0f}% | Inventory: {scenario['inventory_advance']*100:.0f}%")
        
        st.markdown("---")
        
        # Lender View Mode Toggle
        st.subheader("👔 View Mode")
        st.session_state.lender_view_mode = st.toggle(
            "Lender View Mode",
            value=st.session_state.lender_view_mode,
            help="Reorganize results for lender perspective"
        )
        
        st.markdown("---")
        
        # Reset Button
        if st.button("🔄 Start New Analysis", type="secondary", use_container_width=True):
            reset_analysis()
            st.rerun()
        
        # Lender Metrics Information Panel
        render_lender_metrics_info_panel()
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📊 Analysis", "📝 Results & Recommendations", "💧 Cash Flow LOC Analysis"])
    
    with tab1:
        # Input sections
        st.header("Business & Financial Inputs")
        
        # Business Profile
        with st.expander("🏢 Business Profile", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                annual_revenue = st.number_input(
                    "Annual Revenue ($)",
                    min_value=0.0,
                    value=st.session_state.inputs.get('annual_revenue', 500000.0),
                    step=10000.0,
                    format="%.2f"
                )
                
                years_in_business = st.number_input(
                    "Years in Business",
                    min_value=0.0,
                    value=st.session_state.inputs.get('years_in_business', 5.0),
                    step=0.5,
                    format="%.1f"
                )
            
            with col2:
                industry = st.selectbox(
                    "Industry",
                    options=INDUSTRIES,
                    index=INDUSTRIES.index(st.session_state.inputs.get('industry', 'Retail'))
                )
                
                business_type = st.selectbox(
                    "Business Type",
                    options=BUSINESS_TYPES,
                    index=BUSINESS_TYPES.index(st.session_state.inputs.get('business_type', 'Product'))
                )
        
        # Financial Snapshot
        with st.expander("💰 Financial Snapshot", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                net_income = st.number_input(
                    "Net Income ($)",
                    value=st.session_state.inputs.get('net_income', 50000.0),
                    step=5000.0,
                    format="%.2f"
                )
                
                owner_addbacks = st.number_input(
                    "Owner Addbacks ($)",
                    min_value=0.0,
                    value=st.session_state.inputs.get('owner_addbacks', 20000.0),
                    step=5000.0,
                    format="%.2f",
                    help="Non-recurring expenses, owner salary adjustments, etc."
                )
                
                annual_debt_payments = st.number_input(
                    "Annual Debt Payments ($)",
                    min_value=0.0,
                    value=st.session_state.inputs.get('annual_debt_payments', 30000.0),
                    step=5000.0,
                    format="%.2f"
                )
            
            with col2:
                current_assets = st.number_input(
                    "Current Assets ($)",
                    min_value=0.0,
                    value=st.session_state.inputs.get('current_assets', 200000.0),
                    step=10000.0,
                    format="%.2f"
                )
                
                current_liabilities = st.number_input(
                    "Current Liabilities ($)",
                    min_value=0.0,
                    value=st.session_state.inputs.get('current_liabilities', 100000.0),
                    step=10000.0,
                    format="%.2f"
                )
        
        # Collateral
        with st.expander("🏦 Collateral", expanded=True):
            if business_type == 'Service':
                accounts_receivable = st.number_input(
                    "Accounts Receivable ($)",
                    min_value=0.0,
                    value=st.session_state.inputs.get('accounts_receivable', 80000.0),
                    step=5000.0,
                    format="%.2f"
                )
                inventory_value = 0.0
                st.info("💡 Service businesses typically don't carry inventory. Inventory fields are hidden.")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    accounts_receivable = st.number_input(
                        "Accounts Receivable ($)",
                        min_value=0.0,
                        value=st.session_state.inputs.get('accounts_receivable', 80000.0),
                        step=5000.0,
                        format="%.2f"
                    )
                
                with col2:
                    inventory_value = st.number_input(
                        "Inventory Value ($)",
                        min_value=0.0,
                        value=st.session_state.inputs.get('inventory_value', 50000.0),
                        step=5000.0,
                        format="%.2f"
                    )
        
        # Working Capital Timing
        with st.expander("⏱️ Working Capital Timing", expanded=True):
            if business_type == 'Service':
                col1, col2 = st.columns(2)
                
                with col1:
                    receivable_days = st.number_input(
                        "Receivable Days (DSO)",
                        min_value=0.0,
                        max_value=365.0,
                        value=st.session_state.inputs.get('receivable_days', 45.0),
                        step=1.0,
                        format="%.0f",
                        help="Days Sales Outstanding - average days to collect payment"
                    )
                
                with col2:
                    payable_days = st.number_input(
                        "Payable Days (DPO)",
                        min_value=0.0,
                        max_value=365.0,
                        value=st.session_state.inputs.get('payable_days', 30.0),
                        step=1.0,
                        format="%.0f",
                        help="Days Payable Outstanding - average days to pay suppliers"
                    )
                
                inventory_days = 0.0
                st.info("💡 Service businesses don't track inventory days.")
            else:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    receivable_days = st.number_input(
                        "Receivable Days (DSO)",
                        min_value=0.0,
                        max_value=365.0,
                        value=st.session_state.inputs.get('receivable_days', 45.0),
                        step=1.0,
                        format="%.0f",
                        help="Days Sales Outstanding - average days to collect payment"
                    )
                
                with col2:
                    inventory_days = st.number_input(
                        "Inventory Days (DIO)",
                        min_value=0.0,
                        max_value=365.0,
                        value=st.session_state.inputs.get('inventory_days', 30.0),
                        step=1.0,
                        format="%.0f",
                        help="Days Inventory Outstanding - average days inventory is held"
                    )
                
                with col3:
                    payable_days = st.number_input(
                        "Payable Days (DPO)",
                        min_value=0.0,
                        max_value=365.0,
                        value=st.session_state.inputs.get('payable_days', 30.0),
                        step=1.0,
                        format="%.0f",
                        help="Days Payable Outstanding - average days to pay suppliers"
                    )
        
        # Project Notes
        with st.expander("📝 Project Notes", expanded=False):
            st.session_state.project_notes = st.text_area(
                "Notes",
                value=st.session_state.project_notes,
                height=150,
                placeholder="Add any notes about this analysis..."
            )
        
        # Calculate button
        st.markdown("---")
        if st.button("🔍 Calculate Financing Analysis", type="primary", use_container_width=True):
            # Store inputs
            inputs = {
                'annual_revenue': annual_revenue,
                'years_in_business': years_in_business,
                'industry': industry,
                'business_type': business_type,
                'net_income': net_income,
                'owner_addbacks': owner_addbacks,
                'annual_debt_payments': annual_debt_payments,
                'current_assets': current_assets,
                'current_liabilities': current_liabilities,
                'accounts_receivable': accounts_receivable,
                'inventory_value': inventory_value,
                'receivable_days': receivable_days,
                'inventory_days': inventory_days,
                'payable_days': payable_days
            }
            
            # Validate inputs with enhanced validation
            is_valid, errors = validate_all_inputs(inputs, business_type)
            
            if not is_valid:
                st.error(get_validation_summary(errors))
            else:
                # Check for business logic warnings
                warnings = validate_business_logic(inputs, business_type)
                if warnings:
                    with st.expander("⚠️ Business Logic Warnings", expanded=True):
                        for warning in warnings:
                            st.warning(f"**{warning.field}**: {warning.message}")
                
                # Get scenario parameters
                scenario = RISK_TOLERANCE_SCENARIOS[st.session_state.risk_tolerance]
                ar_rate = scenario['ar_advance']
                inv_rate = scenario['inventory_advance']
                
                # Perform calculations
                cash_flow = calculate_adjusted_cash_flow(net_income, owner_addbacks)
                dscr = calculate_dscr(cash_flow, annual_debt_payments)
                current_ratio = calculate_current_ratio(current_assets, current_liabilities)
                borrowing_base = calculate_borrowing_base(
                    accounts_receivable, 
                    inventory_value,
                    ar_advance_rate=ar_rate,
                    inventory_advance_rate=inv_rate
                )
                revenue_low, revenue_high = calculate_revenue_loc_range(annual_revenue)
                ccc = calculate_cash_conversion_cycle(receivable_days, inventory_days, payable_days, business_type)
                daily_revenue = calculate_daily_revenue(annual_revenue)
                working_capital_gap = calculate_working_capital_gap(daily_revenue, ccc)
                loc_low, loc_high = calculate_final_loc_range(
                    revenue_low, revenue_high, borrowing_base, working_capital_gap
                )
                primary_constraint = determine_primary_constraint(
                    revenue_high, borrowing_base, working_capital_gap
                )
                readiness_score = calculate_readiness_score(
                    annual_revenue, cash_flow, dscr, current_ratio, borrowing_base, years_in_business
                )
                
                # Borrower Strength Classification
                if readiness_score >= 80:
                    borrower_strength = "Strong Borrower"
                    risk_level = "Low Risk"
                    gauge_color = "green"
                elif readiness_score >= 60:
                    borrower_strength = "Moderate Borrower"
                    risk_level = "Moderate Risk"
                    gauge_color = "orange"
                else:
                    borrower_strength = "Weak Borrower"
                    risk_level = "High Risk"
                    gauge_color = "red"
                
                confidence_level, conditions_met = calculate_confidence_level(
                    years_in_business, net_income, dscr, current_ratio, accounts_receivable, annual_revenue
                )
                
                # Store results with scenario info
                results = {
                    'cash_flow': cash_flow,
                    'dscr': dscr,
                    'current_ratio': current_ratio,
                    'borrowing_base': borrowing_base,
                    'revenue_low': revenue_low,
                    'revenue_high': revenue_high,
                    'ccc': ccc,
                    'daily_revenue': daily_revenue,
                    'working_capital_gap': working_capital_gap,
                    'loc_low': loc_low,
                    'loc_high': loc_high,
                    'primary_constraint': primary_constraint,
                    'readiness_score': readiness_score,
                    'confidence_level': confidence_level,
                    'conditions_met': conditions_met,
                    'ar_rate': ar_rate,
                    'inv_rate': inv_rate,
                    'borrower_strength': borrower_strength,
                    'risk_level': risk_level,
                    'gauge_color': gauge_color
                }
                
                st.session_state.inputs = inputs
                st.session_state.results = results
                
                st.success("✅ Analysis complete! View results in the 'Results & Recommendations' tab.")
    
    with tab2:
        if st.session_state.results:
            results = st.session_state.results
            inputs = st.session_state.inputs
            business_type = inputs.get('business_type', 'Product')
            
            # Check if lender view mode is enabled
            if st.session_state.lender_view_mode:
                # LENDER VIEW MODE
                st.header("🏦 Lender View - Financing Analysis")
                
                # Business Profile Summary
                render_lender_view_section("Business Profile Summary", {
                    "Business Name": st.session_state.project_name,
                    "Industry": inputs['industry'],
                    "Business Type": business_type,
                    "Years in Business": f"{inputs['years_in_business']:.1f} years",
                    "Annual Revenue": f"${inputs['annual_revenue']:,.0f}"
                })
                
                # Financial Capacity
                render_lender_view_section("Financial Capacity", {
                    "Net Income": f"${inputs['net_income']:,.0f}",
                    "Adjusted Cash Flow": f"${results['cash_flow']:,.0f}",
                    "DSCR": f"{results['dscr']:.2f}" + (" ✅" if results['dscr'] >= 1.25 else " ⚠️"),
                    "Annual Debt Payments": f"${inputs['annual_debt_payments']:,.0f}"
                })
                
                # Collateral Support
                render_lender_view_section("Collateral Support", {
                    "Accounts Receivable": f"${inputs['accounts_receivable']:,.0f}",
                    "Inventory Value": f"${inputs['inventory_value']:,.0f}" if business_type == 'Product' else "N/A (Service Business)",
                    "Borrowing Base": f"${results['borrowing_base']:,.0f}",
                    "AR Advance Rate": f"{results['ar_rate']*100:.0f}%",
                    "Inventory Advance Rate": f"{results['inv_rate']*100:.0f}%" if business_type == 'Product' else "N/A"
                })
                
                # Liquidity Indicators
                render_lender_view_section("Liquidity Indicators", {
                    "Current Assets": f"${inputs['current_assets']:,.0f}",
                    "Current Liabilities": f"${inputs['current_liabilities']:,.0f}",
                    "Current Ratio": f"{results['current_ratio']:.2f}" + (" ✅" if results['current_ratio'] >= 1.2 else " ⚠️"),
                    "Working Capital": f"${inputs['current_assets'] - inputs['current_liabilities']:,.0f}"
                })
                
                # Working Capital Analysis
                render_lender_view_section("Working Capital Analysis", {
                    "Receivable Days (DSO)": f"{inputs['receivable_days']:.0f} days",
                    "Inventory Days (DIO)": f"{inputs['inventory_days']:.0f} days" if business_type == 'Product' else "N/A",
                    "Payable Days (DPO)": f"{inputs['payable_days']:.0f} days",
                    "Cash Conversion Cycle": f"{results['ccc']:.0f} days",
                    "Working Capital Gap": f"${results['working_capital_gap']:,.0f}"
                })
                
                # LOC Recommendation
                render_lender_view_section("Line of Credit Recommendation", {
                    "Recommended LOC Range": f"${results['loc_low']:,.0f} - ${results['loc_high']:,.0f}",
                    "Primary Constraint": results['primary_constraint'],
                    "Financing Readiness Score": f"{results['readiness_score']:.1f}/100 - {render_readiness_status_badge(results['readiness_score'])}",
                    "Confidence Level": f"{results['confidence_level']} ({results['conditions_met']}/5 conditions met)"
                })
                
                # Borrower Strength & Risk Assessment
                render_lender_view_section("Borrower Strength & Risk Assessment", {
                    "Borrower Strength": results['borrower_strength'],
                    "Risk Level": results['risk_level'],
                    "Credit Readiness": f"{results['readiness_score']:.0f}/100"
                })
                
            else:
                # STANDARD VIEW MODE
                # Enhanced Financing Summary Block
                render_financing_summary_block(results)
                
                st.markdown("---")
                
                # Borrower Strength Assessment Panel
                render_borrower_strength_panel(results)
                
                st.markdown("---")
                
                # Metric Cards Row
                st.header("📊 Key Financial Metrics")
                metric_cards_data = {
                    'DSCR': {
                        'value': results['dscr'],
                        'status': 'Strong' if results['dscr'] >= 1.25 else 'Weak',
                        'help': 'Debt Service Coverage Ratio - measures ability to cover debt payments'
                    },
                    'Current Ratio': {
                        'value': results['current_ratio'],
                        'status': 'Healthy' if results['current_ratio'] >= 1.2 else 'Low',
                        'help': 'Current Assets / Current Liabilities - measures liquidity'
                    },
                    'Borrowing Base': {
                        'value': results['borrowing_base'],
                        'status': 'Available',
                        'help': f"Collateral value: AR ({results['ar_rate']*100:.0f}%) + Inventory ({results['inv_rate']*100:.0f}%)"
                    },
                    'WC Gap': {
                        'value': results['working_capital_gap'],
                        'status': f"{results['ccc']:.0f} days",
                        'help': 'Working capital needed based on cash conversion cycle'
                    }
                }
                render_metric_cards_row(metric_cards_data)
                
                st.markdown("---")
                
                # Visualizations
                st.header("📈 Visualizations")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.plotly_chart(
                        create_enhanced_ccc_chart(
                            inputs['receivable_days'],
                            inputs['inventory_days'],
                            inputs['payable_days'],
                            results['ccc'],
                            business_type
                        ),
                        use_container_width=True
                    )
                
                with col2:
                    st.plotly_chart(
                        create_enhanced_readiness_gauge(results['readiness_score']),
                        use_container_width=True
                    )
                
                st.markdown("---")
                
                # Assumptions Panel
                render_assumptions_panel(
                    results['ar_rate'],
                    results['inv_rate'],
                    REVENUE_LOC_LOW_PERCENT
                )
                
                st.markdown("---")
            
            # Key Metrics Table
            st.header("📋 Key Metrics")
            
            metrics_data = {
                'Metric': [
                    'Adjusted Cash Flow',
                    'Debt Service Coverage Ratio (DSCR)',
                    'Current Ratio',
                    'Borrowing Base',
                    'Working Capital Gap',
                    'Cash Conversion Cycle'
                ],
                'Value': [
                    f"${results['cash_flow']:,.2f}",
                    f"{results['dscr']:.2f}",
                    f"{results['current_ratio']:.2f}",
                    f"${results['borrowing_base']:,.2f}",
                    f"${results['working_capital_gap']:,.2f}",
                    f"{results['ccc']:.0f} days"
                ],
                'Status': [
                    '✅ Positive' if results['cash_flow'] > 0 else '⚠️ Negative',
                    '✅ Strong' if results['dscr'] >= 1.25 else '⚠️ Weak',
                    '✅ Healthy' if results['current_ratio'] >= 1.2 else '⚠️ Low',
                    '✅ Available' if results['borrowing_base'] > 0 else 'N/A',
                    f"${results['working_capital_gap']:,.0f}",
                    '✅ Efficient' if results['ccc'] < 45 else '⚠️ Needs Improvement'
                ]
            }
            
            df_metrics = pd.DataFrame(metrics_data)
            st.dataframe(df_metrics, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Recommendations
            st.header("💡 Recommendations")
            
            recommendation = get_financing_recommendation(
                results['ccc'],
                inputs['inventory_value'],
                results['loc_high']
            )
            
            st.markdown(f"### Financing Recommendation")
            st.markdown(recommendation)
            
            st.markdown("### Improvement Suggestions")
            suggestions = get_improvement_suggestions(
                results['dscr'],
                results['current_ratio'],
                results['ccc'],
                inputs['receivable_days']
            )
            
            if suggestions:
                for suggestion in suggestions:
                    st.markdown(f"- {suggestion}")
            else:
                st.success("✅ Your business metrics are in good shape! Continue monitoring these key indicators.")
            
        else:
            st.info("👈 Please complete the analysis in the 'Analysis' tab first.")
    
    with tab3:
        st.header("💧 Cash Flow LOC Analysis")
        st.markdown("""
        **Cash-Flow-Driven LOC Sizing** — Calculate LOC based on your actual projected cash trough, 
        not revenue percentages. This provides a defensible, lender-ready methodology.
        """)
        
        # Initialize cash flow data in session state if not exists
        if 'cash_flow_data' not in st.session_state:
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            st.session_state.cash_flow_data = pd.DataFrame({
                'Month': months,
                'Cash In': [75000.0] * 12,
                'Operating Expenses': [50000.0] * 12,
                'Debt Payments': [5000.0] * 12
            })
        
        # Configuration Section
        st.subheader("⚙️ Configuration")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            starting_cash = st.number_input(
                "Starting Cash Balance ($)",
                min_value=0.0,
                value=25000.0,
                step=5000.0,
                help="Your current cash on hand at the beginning of the projection period"
            )
        
        with col2:
            buffer_percentage = st.slider(
                "Safety Buffer (%)",
                min_value=0,
                max_value=50,
                value=20,
                step=5,
                help="Additional buffer above the minimum LOC requirement"
            )
        
        with col3:
            existing_loc_limit = st.number_input(
                "Existing LOC Limit ($)",
                min_value=0.0,
                value=0.0,
                step=5000.0,
                help="Your current line of credit limit (if any)"
            )
        
        st.markdown("---")
        
        # Monthly Cash Flow Input Table
        st.subheader("📊 12-Month Cash Flow Projection")
        st.markdown("**Edit the table below with your projected monthly cash flows:**")
        
        edited_cash_flow = st.data_editor(
            st.session_state.cash_flow_data,
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                "Month": st.column_config.TextColumn("Month", disabled=True, width="small"),
                "Cash In": st.column_config.NumberColumn(
                    "Cash In ($)",
                    format="$%.0f",
                    help="Total cash received (revenue, collections, etc.)"
                ),
                "Operating Expenses": st.column_config.NumberColumn(
                    "Operating Expenses ($)",
                    format="$%.0f",
                    help="All operating expenses (payroll, rent, supplies, etc.)"
                ),
                "Debt Payments": st.column_config.NumberColumn(
                    "Debt Payments ($)",
                    format="$%.0f",
                    help="Debt service, loan payments, etc."
                )
            }
        )
        
        # Update session state
        st.session_state.cash_flow_data = edited_cash_flow
        
        st.markdown("---")
        
        # Calculate Button
        if st.button("🔍 Calculate Cash Trough & LOC Requirement", type="primary", use_container_width=True):
            # Calculate running cash balances
            months = edited_cash_flow['Month'].tolist()
            cash_in = edited_cash_flow['Cash In'].tolist()
            operating_expenses = edited_cash_flow['Operating Expenses'].tolist()
            debt_payments = edited_cash_flow['Debt Payments'].tolist()
            
            # Calculate monthly net cash flow and running balances
            beginning_balance = []
            ending_balance = []
            net_flow = []
            
            current_balance = starting_cash
            
            for i in range(12):
                beginning_balance.append(current_balance)
                
                total_out = operating_expenses[i] + debt_payments[i]
                monthly_net = cash_in[i] - total_out
                net_flow.append(monthly_net)
                
                current_balance = current_balance + monthly_net
                ending_balance.append(current_balance)
            
            # Find the cash trough (lowest point)
            lowest_cash = min(ending_balance)
            trough_month_idx = ending_balance.index(lowest_cash)
            trough_month = months[trough_month_idx]
            
            # Calculate LOC requirements
            if lowest_cash < 0:
                minimum_loc = abs(lowest_cash)
            else:
                minimum_loc = 0
            
            recommended_loc = minimum_loc * (1 + buffer_percentage / 100)
            stress_loc = recommended_loc * 1.15
            
            # Calculate statistics
            total_cash_in = sum(cash_in)
            total_cash_out = sum(operating_expenses) + sum(debt_payments)
            avg_monthly_net = (total_cash_in - total_cash_out) / 12
            negative_months = sum(1 for balance in ending_balance if balance < 0)
            
            # Store results in session state
            st.session_state.cash_trough_results = {
                'months': months,
                'beginning_balance': beginning_balance,
                'ending_balance': ending_balance,
                'net_flow': net_flow,
                'cash_in': cash_in,
                'cash_out': [operating_expenses[i] + debt_payments[i] for i in range(12)],
                'lowest_cash': lowest_cash,
                'trough_month': trough_month,
                'minimum_loc': minimum_loc,
                'recommended_loc': recommended_loc,
                'stress_loc': stress_loc,
                'total_cash_in': total_cash_in,
                'total_cash_out': total_cash_out,
                'avg_monthly_net': avg_monthly_net,
                'negative_months': negative_months,
                'starting_cash': starting_cash,
                'buffer_percentage': buffer_percentage,
                'existing_loc_limit': existing_loc_limit
            }
            
            st.success("✅ Cash trough analysis complete! See results below.")
        
        # Display Results
        if 'cash_trough_results' in st.session_state:
            results = st.session_state.cash_trough_results
            
            st.markdown("---")
            st.header("📈 Cash Trough Analysis Results")
            
            # Key Metrics Row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Minimum LOC Required",
                    value=f"${results['minimum_loc']:,.0f}",
                    help="Minimum LOC to cover deepest cash trough"
                )
            
            with col2:
                st.metric(
                    label="Recommended LOC",
                    value=f"${results['recommended_loc']:,.0f}",
                    help=f"Minimum LOC + {results['buffer_percentage']}% safety buffer"
                )
            
            with col3:
                st.metric(
                    label="Stress-Test LOC",
                    value=f"${results['stress_loc']:,.0f}",
                    help="Conservative estimate for worst-case scenarios (15% higher)"
                )
            
            with col4:
                st.metric(
                    label="Lowest Cash Position",
                    value=f"${results['lowest_cash']:,.0f}",
                    delta=f"Month: {results['trough_month']}",
                    delta_color="off"
                )
            
            # LOC Gap Analysis
            if results['existing_loc_limit'] > 0:
                st.markdown("---")
                st.subheader("📊 LOC Gap Analysis")
                
                gap = results['recommended_loc'] - results['existing_loc_limit']
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Current LOC Limit",
                        value=f"${results['existing_loc_limit']:,.0f}"
                    )
                
                with col2:
                    if gap > 0:
                        st.metric(
                            label="LOC Shortfall",
                            value=f"${gap:,.0f}",
                            delta=f"{(gap/results['existing_loc_limit'])*100:.1f}% increase needed",
                            delta_color="normal"
                        )
                    else:
                        st.metric(
                            label="LOC Surplus",
                            value=f"${abs(gap):,.0f}",
                            delta="Adequate coverage",
                            delta_color="inverse"
                        )
                
                with col3:
                    coverage_ratio = (results['existing_loc_limit'] / results['recommended_loc'] * 100) if results['recommended_loc'] > 0 else 100
                    st.metric(
                        label="Coverage Ratio",
                        value=f"{coverage_ratio:.1f}%",
                        help="Existing LOC as % of recommended LOC"
                    )
            
            # Cash Flow Statistics
            st.markdown("---")
            st.subheader("📊 Cash Flow Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total 12-Month Cash In",
                    value=f"${results['total_cash_in']:,.0f}"
                )
            
            with col2:
                st.metric(
                    label="Total 12-Month Cash Out",
                    value=f"${results['total_cash_out']:,.0f}"
                )
            
            with col3:
                st.metric(
                    label="Avg Monthly Net Flow",
                    value=f"${results['avg_monthly_net']:,.0f}",
                    delta="Surplus" if results['avg_monthly_net'] > 0 else "Deficit",
                    delta_color="normal" if results['avg_monthly_net'] > 0 else "inverse"
                )
            
            with col4:
                st.metric(
                    label="Negative Cash Months",
                    value=f"{results['negative_months']} of 12",
                    help="Months where ending cash balance is negative"
                )
            
            # Key Insights
            st.markdown("---")
            st.subheader("🔑 Key Insights")
            
            insights = []
            
            # Cash trough insight
            if results['lowest_cash'] < 0:
                insights.append(f"💧 **Cash Trough**: Your lowest projected cash position is **${results['lowest_cash']:,.0f}** in **{results['trough_month']}**. This is the primary driver of your LOC requirement.")
            else:
                insights.append(f"✅ **Positive Cash Flow**: Your cash balance remains positive throughout the 12-month period, with a low of **${results['lowest_cash']:,.0f}** in **{results['trough_month']}**.")
            
            # Monthly flow insight
            if results['avg_monthly_net'] < 0:
                insights.append(f"⚠️ **Cash Burn**: Your average monthly net cash flow is **${results['avg_monthly_net']:,.0f}**, indicating ongoing cash consumption. Consider revenue growth or expense reduction strategies.")
            else:
                insights.append(f"✅ **Cash Generation**: Your average monthly net cash flow is **${results['avg_monthly_net']:,.0f}**, indicating positive cash generation over the period.")
            
            # Negative months insight
            if results['negative_months'] > 0:
                insights.append(f"📉 **Liquidity Pressure**: You have **{results['negative_months']} months** with negative cash balances. The recommended LOC provides a safety net for these periods.")
            
            # Buffer insight
            if results['buffer_percentage'] > 0:
                buffer_amount = results['recommended_loc'] - results['minimum_loc']
                insights.append(f"🛡️ **Safety Buffer**: The {results['buffer_percentage']}% buffer adds **${buffer_amount:,.0f}** to cover unexpected expenses or revenue shortfalls.")
            
            # LOC gap insight
            if results['existing_loc_limit'] > 0:
                if gap > 0:
                    insights.append(f"📊 **LOC Gap**: Your current LOC limit of **${results['existing_loc_limit']:,.0f}** falls short by **${gap:,.0f}**. Consider requesting an increase to ensure adequate liquidity coverage.")
                else:
                    insights.append(f"✅ **Adequate Coverage**: Your current LOC limit of **${results['existing_loc_limit']:,.0f}** provides adequate coverage for your projected cash needs.")
            
            for insight in insights:
                st.markdown(insight)
            
            # Visualizations
            st.markdown("---")
            st.subheader("📊 Cash Flow Visualizations")
            
            # Cash Balance Chart
            fig_balance = go.Figure()
            
            fig_balance.add_trace(go.Scatter(
                x=results['months'],
                y=results['ending_balance'],
                mode='lines+markers',
                name='Ending Cash Balance',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8)
            ))
            
            # Add zero line
            fig_balance.add_hline(y=0, line_dash="dash", line_color="red", 
                                  annotation_text="Zero Cash Line", annotation_position="right")
            
            # Highlight lowest point
            fig_balance.add_trace(go.Scatter(
                x=[results['trough_month']],
                y=[results['lowest_cash']],
                mode='markers',
                name='Cash Trough',
                marker=dict(size=15, color='red', symbol='star')
            ))
            
            fig_balance.update_layout(
                title="12-Month Cash Balance Projection",
                xaxis_title="Month",
                yaxis_title="Cash Balance ($)",
                hovermode='x unified',
                showlegend=True,
                height=400
            )
            
            st.plotly_chart(fig_balance, use_container_width=True)
            
            # Monthly Net Flow Chart
            col1, col2 = st.columns(2)
            
            with col1:
                fig_net = go.Figure()
                
                colors = ['green' if net >= 0 else 'red' for net in results['net_flow']]
                
                fig_net.add_trace(go.Bar(
                    x=results['months'],
                    y=results['net_flow'],
                    name='Net Cash Flow',
                    marker_color=colors
                ))
                
                fig_net.add_hline(y=0, line_dash="dash", line_color="gray")
                
                fig_net.update_layout(
                    title="Monthly Net Cash Flow",
                    xaxis_title="Month",
                    yaxis_title="Net Cash Flow ($)",
                    hovermode='x unified',
                    showlegend=False,
                    height=350
                )
                
                st.plotly_chart(fig_net, use_container_width=True)
            
            with col2:
                # Funding Gap Chart (negative balances only)
                funding_gaps = [abs(bal) if bal < 0 else 0 for bal in results['ending_balance']]
                
                fig_gap = go.Figure()
                
                fig_gap.add_trace(go.Bar(
                    x=results['months'],
                    y=funding_gaps,
                    name='Funding Gap',
                    marker_color='#d62728'
                ))
                
                fig_gap.update_layout(
                    title="Monthly Funding Gaps (LOC Draw Required)",
                    xaxis_title="Month",
                    yaxis_title="Funding Gap ($)",
                    hovermode='x unified',
                    showlegend=False,
                    height=350
                )
                
                st.plotly_chart(fig_gap, use_container_width=True)
            
            # Detailed Monthly Table
            st.markdown("---")
            st.subheader("📋 Detailed Monthly Cash Flow")
            
            detailed_df = pd.DataFrame({
                'Month': results['months'],
                'Beginning Cash': results['beginning_balance'],
                'Cash In': results['cash_in'],
                'Cash Out': results['cash_out'],
                'Net Flow': results['net_flow'],
                'Ending Cash': results['ending_balance']
            })
            
            # Format currency columns
            for col in ['Beginning Cash', 'Cash In', 'Cash Out', 'Net Flow', 'Ending Cash']:
                detailed_df[col] = detailed_df[col].apply(lambda x: f"${x:,.0f}")
            
            st.dataframe(detailed_df, use_container_width=True, hide_index=True)
            
            # Export Functionality
            st.markdown("---")
            st.subheader("💾 Export Analysis")
            
            export_data = {
                'business_name': st.session_state.project_name,
                'analysis_date': datetime.now().isoformat(),
                'starting_cash': results['starting_cash'],
                'buffer_percentage': results['buffer_percentage'],
                'existing_loc_limit': results['existing_loc_limit'],
                'results': {
                    'minimum_loc': results['minimum_loc'],
                    'recommended_loc': results['recommended_loc'],
                    'stress_loc': results['stress_loc'],
                    'lowest_cash': results['lowest_cash'],
                    'trough_month': results['trough_month'],
                    'negative_months': results['negative_months'],
                    'avg_monthly_net': results['avg_monthly_net']
                },
                'monthly_cash_flow': edited_cash_flow.to_dict('records')
            }
            
            json_str = json.dumps(export_data, indent=2)
            
            st.download_button(
                label="📥 Download Cash Trough Analysis (JSON)",
                data=json_str,
                file_name=f"cash_trough_analysis_{st.session_state.project_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        
        else:
            st.info("👆 Configure your parameters and enter your 12-month cash flow projection above, then click 'Calculate' to see results.")


if __name__ == "__main__":
    main()
