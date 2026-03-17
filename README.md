# Business Financing Readiness Tool

A comprehensive Streamlit application that evaluates small business financing readiness and estimates an appropriate line-of-credit range using financial inputs, borrowing base analysis, and cash conversion cycle calculations.

## 🎯 Overview

This tool helps small business owners, lenders, and advisors:
- Estimate an appropriate working capital line of credit
- Understand the financial factors lenders consider when evaluating business financing
- Calculate key financial metrics (DSCR, Current Ratio, Cash Conversion Cycle)
- Assess financing readiness with a comprehensive scoring system
- Identify areas for improvement in business finances

## � LOC Sizing Tool (NEW)

A standalone **cash-flow-first** line of credit sizing tool that estimates LOC needs based on cash flow timing, cash trough analysis, and risk buffering — not flat revenue percentages.

### Three Analysis Modes

1. **Quick Estimate** - Rapid timing gap analysis for users with limited data
2. **Guided Estimate** - Synthetic 12-month cash curve generation (recommended)
3. **Full Monthly Cash Flow** - Detailed analysis using actual monthly projections

### Key Features

- **Cash Flow Timing Analysis**: Models collection delays and payment terms
- **Seasonal Weakness Modeling**: Adjusts for weak revenue months
- **Risk Buffering**: Conservative/Moderate/Aggressive buffer profiles
- **Visual Analytics**: Interactive charts showing cash balance trends and funding gaps
- **LOC Gap Analysis**: Compares recommended LOC to existing credit lines
- **Export Functionality**: Download JSON summary of analysis

### Running the LOC Sizing Tool

```bash
streamlit run loc_sizing_tool.py
```

See `docs/windsurf_reports/LOC_Sizing_Tool_Report.md` for detailed documentation.

## �🚀 Features

### Core Functionality
- **Business Profile Analysis**: Revenue, industry, business type, and history evaluation
- **Financial Snapshot**: Net income, cash flow, debt service coverage analysis
- **Collateral Assessment**: Borrowing base calculation using accounts receivable and inventory
- **Working Capital Timing**: Cash conversion cycle analysis
- **Readiness Scoring**: 0-100 scale with weighted factors
- **Confidence Indicator**: Multi-factor assessment of financing approval likelihood

### Calculations
- Adjusted Cash Flow
- Debt Service Coverage Ratio (DSCR)
- Current Ratio (Liquidity)
- Borrowing Base (80% AR + 50% Inventory)
- Revenue-based LOC Range (5-15% of revenue)
- Cash Conversion Cycle (DSO + DIO - DPO)
- Working Capital Gap
- Final LOC Range (constrained by multiple factors)

### Visualizations
- Cash Conversion Cycle Bar Chart
- Financing Readiness Gauge
- Interactive metrics dashboard

### Project Management
- Save/Load projects as JSON
- Export analysis results
- Project notes and documentation
- Timestamped project history

## 📋 Requirements

- Python 3.8+
- Streamlit 1.31.0
- Pandas 2.2.0
- NumPy 1.26.3
- Plotly 5.18.0

## 🛠️ Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🎮 Usage

### Running Locally

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Using the Application

1. **Enter Business Information**:
   - Fill in business profile (revenue, years in business, industry)
   - Enter financial snapshot (income, assets, liabilities)
   - Provide collateral details (AR, inventory)
   - Input working capital timing (days metrics)

2. **Calculate Analysis**:
   - Click "Calculate Financing Analysis" button
   - Review validation messages if any errors occur

3. **Review Results**:
   - View LOC range recommendation
   - Check readiness score and confidence level
   - Analyze key metrics and visualizations
   - Read personalized recommendations

4. **Save Your Work**:
   - Name your project in the sidebar
   - Click "Save" to store analysis
   - Use "Load" to retrieve previous analyses
   - Download JSON export for external use

## 📁 Project Structure

```
business-financing-evaluator/
├── app.py                  # Main Streamlit application
├── calculations.py         # Financial formulas and business logic
├── json_io.py             # Save/load functionality
├── config.py              # Configuration and constants
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── saved_projects/       # Directory for saved analyses (auto-created)
└── docs/
    └── windsurf_reports/ # Report output directory
```

## 🔢 Key Formulas

### Adjusted Cash Flow
```
Cash Flow = Net Income + Owner Addbacks
```

### Debt Service Coverage Ratio (DSCR)
```
DSCR = Cash Flow / Annual Debt Payments
```

### Current Ratio
```
Current Ratio = Current Assets / Current Liabilities
```

### Borrowing Base
```
Borrowing Base = (Accounts Receivable × 0.80) + (Inventory × 0.50)
```

### Cash Conversion Cycle
```
CCC = Receivable Days + Inventory Days - Payable Days
```

### Working Capital Gap
```
Working Capital Gap = (Annual Revenue / 365) × CCC
```

### Final LOC Range
```
LOC Low = min(Revenue × 0.05, Borrowing Base, Working Capital Gap)
LOC High = min(Revenue × 0.15, Borrowing Base, Working Capital Gap)
```

## 📊 Readiness Score Weights

The financing readiness score (0-100) is calculated using weighted factors:

- **Revenue Strength**: 20%
- **Cash Flow**: 20%
- **DSCR**: 20%
- **Liquidity**: 15%
- **Collateral**: 15%
- **Business History**: 10%

## 🎯 Confidence Level Criteria

The confidence indicator evaluates 5 conditions:

1. Years in Business > 3
2. Net Income > 0
3. DSCR > 1.25
4. Current Ratio > 1.2
5. Accounts Receivable > 20% of Annual Revenue

**Scoring**:
- 0-1 conditions met: Low confidence
- 2-3 conditions met: Moderate confidence
- 4-5 conditions met: High confidence

## ✅ Input Validation

The application validates:
- Revenue must be greater than 0
- Accounts Receivable cannot exceed Annual Revenue
- Days fields must be between 0 and 365
- Liabilities must be non-negative

## 🚀 Deployment

### Render Deployment

1. Create a new Web Service on Render
2. Connect your repository
3. Configure build settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

### Other Platforms

The application can be deployed on:
- Streamlit Cloud
- Heroku
- AWS/GCP/Azure
- Any platform supporting Python web applications

## 🤝 Target Users

- **Small Business Owners**: Assess financing readiness and understand LOC options
- **Lenders**: Quickly evaluate business financing applications
- **Business Advisors**: Provide data-driven recommendations to clients

## 📝 Notes

- All calculations use safe division to prevent errors
- Projects are saved locally in JSON format
- Best scores are tracked across sessions
- The tool provides educational recommendations, not financial advice

## 🔒 Data Privacy

- All data is processed locally
- No data is transmitted to external servers (when running locally)
- Saved projects are stored on your local machine
- JSON exports contain all input and calculated data

## 📄 License

This project is provided as-is for educational and business evaluation purposes.

## 🆘 Support

For issues or questions:
1. Check input validation messages
2. Review the "How to Use This Tool" section in the app
3. Ensure all required fields are filled with valid data
4. Verify calculations match expected business logic

## 🔄 Version History

- **v1.0.0**: Initial release with full feature set
  - Business profile and financial analysis
  - Borrowing base and CCC calculations
  - Readiness scoring and confidence indicators
  - Save/load functionality
  - Interactive visualizations

---

**Disclaimer**: This tool provides estimates and educational information only. Consult with qualified financial professionals for actual financing decisions.
