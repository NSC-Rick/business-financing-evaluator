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

from config import (
    PAGE_CONFIG,
    INDUSTRIES,
    BUSINESS_TYPES,
    COLORS
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
    get_improvement_suggestions,
    validate_inputs
)
from json_io import (
    create_project_data,
    save_project,
    load_project,
    list_saved_projects,
    export_to_json_string
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


def create_ccc_chart(receivable_days, inventory_days, payable_days, ccc):
    """Create cash conversion cycle bar chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Receivable Days',
        x=['Days'],
        y=[receivable_days],
        marker_color=COLORS['primary'],
        text=[f'{receivable_days:.0f}'],
        textposition='inside'
    ))
    
    fig.add_trace(go.Bar(
        name='Inventory Days',
        x=['Days'],
        y=[inventory_days],
        marker_color=COLORS['info'],
        text=[f'{inventory_days:.0f}'],
        textposition='inside'
    ))
    
    fig.add_trace(go.Bar(
        name='Payable Days',
        x=['Days'],
        y=[-payable_days],
        marker_color=COLORS['success'],
        text=[f'{payable_days:.0f}'],
        textposition='inside'
    ))
    
    fig.update_layout(
        title='Cash Conversion Cycle Components',
        yaxis_title='Days',
        barmode='relative',
        height=400,
        showlegend=True,
        annotations=[
            dict(
                x=0,
                y=ccc,
                text=f'CCC: {ccc:.0f} days',
                showarrow=True,
                arrowhead=2,
                ax=40,
                ay=-40,
                font=dict(size=14, color=COLORS['danger'])
            )
        ]
    )
    
    return fig


def create_readiness_gauge(score):
    """Create financing readiness indicator gauge"""
    if score >= 75:
        color = COLORS['success']
        label = 'Strong'
    elif score >= 50:
        color = COLORS['warning']
        label = 'Moderate'
    else:
        color = COLORS['danger']
        label = 'Weak'
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Readiness: {label}"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 75], 'color': "gray"},
                {'range': [75, 100], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig


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
    
    # Main content tabs
    tab1, tab2 = st.tabs(["📊 Analysis", "📝 Results & Recommendations"])
    
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
            
            # Validate inputs
            is_valid, errors = validate_inputs(inputs)
            
            if not is_valid:
                st.error("**Validation Errors:**")
                for error in errors:
                    st.error(f"• {error}")
            else:
                # Perform calculations
                cash_flow = calculate_adjusted_cash_flow(net_income, owner_addbacks)
                dscr = calculate_dscr(cash_flow, annual_debt_payments)
                current_ratio = calculate_current_ratio(current_assets, current_liabilities)
                borrowing_base = calculate_borrowing_base(accounts_receivable, inventory_value)
                revenue_low, revenue_high = calculate_revenue_loc_range(annual_revenue)
                ccc = calculate_cash_conversion_cycle(receivable_days, inventory_days, payable_days)
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
                confidence_level, conditions_met = calculate_confidence_level(
                    years_in_business, net_income, dscr, current_ratio, accounts_receivable, annual_revenue
                )
                
                # Store results
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
                    'conditions_met': conditions_met
                }
                
                st.session_state.inputs = inputs
                st.session_state.results = results
                
                st.success("✅ Analysis complete! View results in the 'Results & Recommendations' tab.")
    
    with tab2:
        if st.session_state.results:
            results = st.session_state.results
            inputs = st.session_state.inputs
            
            # Summary Panel
            st.header("📊 Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "LOC Range",
                    f"${results['loc_low']:,.0f} - ${results['loc_high']:,.0f}"
                )
            
            with col2:
                st.metric(
                    "Readiness Score",
                    f"{results['readiness_score']:.1f}/100"
                )
            
            with col3:
                st.metric(
                    "Confidence Level",
                    results['confidence_level'],
                    f"{results['conditions_met']}/5 conditions"
                )
            
            with col4:
                st.metric(
                    "Cash Conversion Cycle",
                    f"{results['ccc']:.0f} days"
                )
            
            st.info(f"**Primary Constraint:** {results['primary_constraint']}")
            
            st.markdown("---")
            
            # Visualizations
            st.header("📈 Visualizations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(
                    create_ccc_chart(
                        inputs['receivable_days'],
                        inputs['inventory_days'],
                        inputs['payable_days'],
                        results['ccc']
                    ),
                    use_container_width=True
                )
            
            with col2:
                st.plotly_chart(
                    create_readiness_gauge(results['readiness_score']),
                    use_container_width=True
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


if __name__ == "__main__":
    main()
