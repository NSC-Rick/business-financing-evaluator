"""
UI Components module for Business Financing Readiness Tool
Reusable UI elements, metric cards, and information panels
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Optional
from config import COLORS


def render_metric_card(label: str, value: str, delta: Optional[str] = None, 
                       help_text: Optional[str] = None, color: str = 'primary'):
    """
    Render a styled metric card
    
    Args:
        label: Metric label
        value: Metric value (formatted string)
        delta: Optional delta/change indicator
        help_text: Optional help text
        color: Color theme ('primary', 'success', 'warning', 'danger')
    """
    st.metric(
        label=label,
        value=value,
        delta=delta,
        help=help_text
    )


def render_lender_metrics_info_panel():
    """Render sidebar information panel explaining key lender metrics"""
    st.sidebar.markdown("---")
    st.sidebar.header("📚 Lender Metrics Guide")
    
    with st.sidebar.expander("💰 Debt Service Coverage Ratio (DSCR)", expanded=False):
        st.markdown("""
        **What it is:**  
        Measures your ability to cover debt payments with cash flow.
        
        **Formula:**  
        `DSCR = Cash Flow ÷ Annual Debt Payments`
        
        **Lender Standards:**
        - **< 1.0**: Cannot cover debt (high risk)
        - **1.0 - 1.25**: Marginal coverage
        - **1.25 - 1.5**: Acceptable
        - **> 1.5**: Strong coverage
        
        **Why it matters:**  
        Lenders want to see you can comfortably pay debts even if business slows down.
        """)
    
    with st.sidebar.expander("📊 Current Ratio", expanded=False):
        st.markdown("""
        **What it is:**  
        Measures your ability to pay short-term obligations.
        
        **Formula:**  
        `Current Ratio = Current Assets ÷ Current Liabilities`
        
        **Lender Standards:**
        - **< 1.0**: Liquidity concerns
        - **1.0 - 1.2**: Minimal cushion
        - **1.2 - 2.0**: Healthy liquidity
        - **> 2.0**: Strong liquidity
        
        **Why it matters:**  
        Shows you can handle unexpected expenses or revenue dips.
        """)
    
    with st.sidebar.expander("⏱️ Cash Conversion Cycle (CCC)", expanded=False):
        st.markdown("""
        **What it is:**  
        Days between paying suppliers and collecting from customers.
        
        **Formula:**  
        `CCC = Receivable Days + Inventory Days - Payable Days`
        
        **Interpretation:**
        - **< 30 days**: Excellent working capital efficiency
        - **30 - 60 days**: Good management
        - **60 - 90 days**: Moderate needs
        - **> 90 days**: Significant working capital needs
        
        **Why it matters:**  
        Determines how much working capital you need to operate.
        """)
    
    with st.sidebar.expander("🏦 Borrowing Base", expanded=False):
        st.markdown("""
        **What it is:**  
        Maximum loan amount based on collateral value.
        
        **Formula:**  
        `Borrowing Base = (AR × 80%) + (Inventory × 50%)`
        
        **Advance Rates:**
        - **Accounts Receivable**: 70-85%
        - **Inventory**: 40-60%
        - Rates vary by lender risk tolerance
        
        **Why it matters:**  
        Your LOC cannot exceed the value of your collateral.
        """)


def render_assumptions_panel(ar_rate: float, inv_rate: float, revenue_pct: float):
    """
    Render assumptions transparency panel
    
    Args:
        ar_rate: Accounts receivable advance rate
        inv_rate: Inventory advance rate
        revenue_pct: Revenue LOC baseline percentage
    """
    with st.expander("📋 Analysis Assumptions", expanded=False):
        st.markdown("### Key Assumptions Used in This Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("AR Advance Rate", f"{ar_rate*100:.0f}%")
            st.metric("Revenue LOC Range", f"{revenue_pct*100:.0f}-{revenue_pct*3*100:.0f}%")
        
        with col2:
            st.metric("Inventory Advance Rate", f"{inv_rate*100:.0f}%")
            st.metric("Days in Year", "365")
        
        st.info("""
        **Note:** These assumptions are based on typical lender standards. 
        Actual terms may vary based on your specific lender, industry, and business profile.
        """)


def render_readiness_status_badge(score: float) -> str:
    """
    Render a colored status badge based on readiness score
    
    Args:
        score: Readiness score (0-100)
        
    Returns:
        HTML string for colored badge
    """
    if score >= 75:
        color = "#28a745"  # Green
        status = "Strong"
        icon = "✅"
    elif score >= 50:
        color = "#ffc107"  # Yellow
        status = "Moderate"
        icon = "⚠️"
    else:
        color = "#dc3545"  # Red
        status = "Weak"
        icon = "❌"
    
    return f"{icon} **{status}**"


def create_enhanced_ccc_chart(receivable_days: float, inventory_days: float, 
                               payable_days: float, ccc: float, 
                               business_type: str = 'Product'):
    """
    Create enhanced cash conversion cycle bar chart
    
    Args:
        receivable_days: Days sales outstanding
        inventory_days: Days inventory outstanding
        payable_days: Days payable outstanding
        ccc: Cash conversion cycle
        business_type: 'Service' or 'Product'
    """
    fig = go.Figure()
    
    # Receivable Days
    fig.add_trace(go.Bar(
        name='Receivable Days (DSO)',
        x=['Cash Conversion Cycle'],
        y=[receivable_days],
        marker_color=COLORS['primary'],
        text=[f'{receivable_days:.0f} days'],
        textposition='inside',
        hovertemplate='<b>Receivable Days</b><br>%{y:.0f} days<extra></extra>'
    ))
    
    # Inventory Days (only for Product businesses)
    if business_type == 'Product' and inventory_days > 0:
        fig.add_trace(go.Bar(
            name='Inventory Days (DIO)',
            x=['Cash Conversion Cycle'],
            y=[inventory_days],
            marker_color=COLORS['info'],
            text=[f'{inventory_days:.0f} days'],
            textposition='inside',
            hovertemplate='<b>Inventory Days</b><br>%{y:.0f} days<extra></extra>'
        ))
    
    # Payable Days (negative)
    fig.add_trace(go.Bar(
        name='Payable Days (DPO)',
        x=['Cash Conversion Cycle'],
        y=[-payable_days],
        marker_color=COLORS['success'],
        text=[f'{payable_days:.0f} days'],
        textposition='inside',
        hovertemplate='<b>Payable Days</b><br>%{text}<extra></extra>'
    ))
    
    # Determine CCC status color
    if ccc < 30:
        ccc_color = COLORS['success']
        status = "Excellent"
    elif ccc < 60:
        ccc_color = COLORS['primary']
        status = "Good"
    elif ccc < 90:
        ccc_color = COLORS['warning']
        status = "Moderate"
    else:
        ccc_color = COLORS['danger']
        status = "High"
    
    fig.update_layout(
        title=f'Cash Conversion Cycle: {ccc:.0f} days ({status})',
        yaxis_title='Days',
        barmode='relative',
        height=450,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        annotations=[
            dict(
                x=0,
                y=ccc + 5,
                text=f'<b>Net CCC: {ccc:.0f} days</b>',
                showarrow=True,
                arrowhead=2,
                arrowcolor=ccc_color,
                ax=60,
                ay=-40,
                font=dict(size=14, color=ccc_color),
                bgcolor='white',
                bordercolor=ccc_color,
                borderwidth=2,
                borderpad=4
            )
        ]
    )
    
    return fig


def create_enhanced_readiness_gauge(score: float):
    """
    Create enhanced financing readiness indicator gauge
    
    Args:
        score: Readiness score (0-100)
    """
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
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>Financing Readiness</b><br><span style='font-size:0.8em'>{label}</span>"},
        number={'suffix': "/100", 'font': {'size': 48}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#ffebee'},
                {'range': [50, 75], 'color': '#fff9e6'},
                {'range': [75, 100], 'color': '#e8f5e9'}
            ],
            'threshold': {
                'line': {'color': color, 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=80, b=20)
    )
    
    return fig


def render_metric_cards_row(metrics: Dict):
    """
    Render a row of metric cards
    
    Args:
        metrics: Dictionary with metric data
            {
                'DSCR': {'value': 2.33, 'status': 'Strong'},
                'Current Ratio': {'value': 2.0, 'status': 'Healthy'},
                ...
            }
    """
    num_metrics = len(metrics)
    cols = st.columns(num_metrics)
    
    for idx, (label, data) in enumerate(metrics.items()):
        with cols[idx]:
            value = data.get('value', 0)
            status = data.get('status', '')
            help_text = data.get('help', None)
            
            # Format value
            if isinstance(value, float):
                if value >= 1000:
                    formatted_value = f"${value:,.0f}"
                else:
                    formatted_value = f"{value:.2f}"
            else:
                formatted_value = str(value)
            
            st.metric(
                label=label,
                value=formatted_value,
                delta=status if status else None,
                help=help_text
            )


def render_lender_view_section(section_title: str, content: Dict):
    """
    Render a section in lender view mode
    
    Args:
        section_title: Title of the section
        content: Dictionary of content items to display
    """
    st.subheader(section_title)
    
    # Create a clean table-like display
    for label, value in content.items():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"**{label}:**")
        with col2:
            st.markdown(value)
    
    st.markdown("---")


def render_reset_button():
    """Render a reset/new analysis button"""
    if st.button("🔄 Start New Analysis", type="secondary", use_container_width=True):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


def render_financing_summary_block(results: Dict):
    """
    Render enhanced financing summary block
    
    Args:
        results: Dictionary of calculation results
    """
    st.markdown("### 💼 Financing Summary")
    
    # Create summary box
    summary_html = f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid {COLORS['primary']};">
        <h4 style="margin-top: 0;">Recommended Line of Credit Range</h4>
        <h2 style="color: {COLORS['primary']}; margin: 10px 0;">${results['loc_low']:,.0f} - ${results['loc_high']:,.0f}</h2>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px;">
            <div>
                <p style="margin: 5px 0; color: #666;"><strong>Readiness Score:</strong></p>
                <p style="margin: 5px 0; font-size: 1.2em;">{results['readiness_score']:.1f}/100</p>
            </div>
            <div>
                <p style="margin: 5px 0; color: #666;"><strong>Confidence Level:</strong></p>
                <p style="margin: 5px 0; font-size: 1.2em;">{results['confidence_level']}</p>
            </div>
            <div>
                <p style="margin: 5px 0; color: #666;"><strong>Primary Constraint:</strong></p>
                <p style="margin: 5px 0; font-size: 1.2em;">{results['primary_constraint']}</p>
            </div>
            <div>
                <p style="margin: 5px 0; color: #666;"><strong>Cash Conversion Cycle:</strong></p>
                <p style="margin: 5px 0; font-size: 1.2em;">{results['ccc']:.0f} days</p>
            </div>
        </div>
    </div>
    """
    
    st.markdown(summary_html, unsafe_allow_html=True)
