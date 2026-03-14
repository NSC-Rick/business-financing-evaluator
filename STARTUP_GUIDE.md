# 🚀 Quick Start Guide - Business Financing Evaluator

## Prerequisites

Before running the application, ensure you have:
- Python 3.8 or higher installed
- pip (Python package installer)

## Installation Steps

### 1. Install Dependencies

Open a terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- streamlit
- pandas
- numpy
- plotly

### 2. Verify Installation

Test the calculations module:

```bash
python test_calculations.py
```

You should see output showing all calculations working correctly.

## Running the Application

### Start the Streamlit App

```bash
streamlit run app.py
```

The application will automatically open in your default web browser at:
```
http://localhost:8501
```

## First Time Usage

### Step 1: Enter Business Information

1. Navigate to the **"Analysis"** tab
2. Fill in the **Business Profile** section:
   - Annual Revenue
   - Years in Business
   - Industry
   - Business Type (Service/Product)

### Step 2: Add Financial Data

3. Complete the **Financial Snapshot**:
   - Net Income
   - Owner Addbacks
   - Annual Debt Payments
   - Current Assets
   - Current Liabilities

4. Enter **Collateral** information:
   - Accounts Receivable
   - Inventory Value

5. Input **Working Capital Timing**:
   - Receivable Days (DSO)
   - Inventory Days (DIO)
   - Payable Days (DPO)

### Step 3: Calculate & Review

6. Click **"Calculate Financing Analysis"** button
7. Switch to the **"Results & Recommendations"** tab
8. Review:
   - LOC Range recommendation
   - Readiness Score
   - Confidence Level
   - Key metrics and visualizations
   - Personalized recommendations

### Step 4: Save Your Work

9. In the sidebar, enter a **Project Name**
10. Click **"Save"** to store your analysis
11. Use **"Download JSON"** to export for external use

## Sample Data for Testing

Use these values to test the application:

```
Business Profile:
- Annual Revenue: $500,000
- Years in Business: 5
- Industry: Retail
- Business Type: Product

Financial Snapshot:
- Net Income: $50,000
- Owner Addbacks: $20,000
- Annual Debt Payments: $30,000
- Current Assets: $200,000
- Current Liabilities: $100,000

Collateral:
- Accounts Receivable: $80,000
- Inventory Value: $50,000

Working Capital Timing:
- Receivable Days: 45
- Inventory Days: 30
- Payable Days: 30
```

Expected Results:
- LOC Range: ~$25,000 - $61,644
- Readiness Score: ~60-70/100
- Confidence Level: Moderate
- Cash Conversion Cycle: 45 days

## Troubleshooting

### Application Won't Start

**Issue**: `streamlit: command not found`
**Solution**: Ensure streamlit is installed:
```bash
pip install streamlit
```

**Issue**: Module import errors
**Solution**: Reinstall all dependencies:
```bash
pip install -r requirements.txt --upgrade
```

### Validation Errors

**Issue**: "Revenue must be greater than 0"
**Solution**: Ensure Annual Revenue is a positive number

**Issue**: "Accounts receivable cannot exceed annual revenue"
**Solution**: Check that AR is realistic relative to revenue

**Issue**: "Days fields must be between 0 and 365"
**Solution**: Verify all days inputs are within valid range

### Save/Load Issues

**Issue**: Cannot save project
**Solution**: Check that `saved_projects/` directory exists and has write permissions

**Issue**: Cannot load project
**Solution**: Verify the JSON file is valid and in the correct format

## Features Overview

### 📊 Analysis Tab
- Input all business and financial data
- Real-time validation
- Organized sections with helpful tooltips

### 📝 Results Tab
- Summary metrics dashboard
- Interactive visualizations
- Key metrics table
- Personalized recommendations
- Improvement suggestions

### 💾 Project Management (Sidebar)
- Name and save projects
- Load previous analyses
- Export to JSON
- Add project notes

## Understanding Your Results

### LOC Range
The recommended line of credit range based on:
- Revenue (5-15% of annual revenue)
- Borrowing Base (80% AR + 50% Inventory)
- Working Capital Gap (Daily Revenue × CCC)

The final range is constrained by the lowest limiting factor.

### Readiness Score (0-100)
Weighted score based on:
- Revenue Strength (20%)
- Cash Flow (20%)
- DSCR (20%)
- Liquidity (15%)
- Collateral (15%)
- Business History (10%)

**Interpretation**:
- 75-100: Strong - High likelihood of approval
- 50-74: Moderate - Good chance with some improvements
- 0-49: Weak - Significant improvements needed

### Confidence Level
Based on 5 key conditions:
1. Years in Business > 3
2. Net Income > 0
3. DSCR > 1.25
4. Current Ratio > 1.2
5. AR > 20% of Revenue

**Levels**:
- High (4-5 conditions): Strong approval likelihood
- Moderate (2-3 conditions): Conditional approval likely
- Low (0-1 conditions): Approval unlikely without improvements

### Primary Constraint
Identifies which factor limits your LOC:
- **Revenue**: Business size constrains borrowing
- **Borrowing Base**: Insufficient collateral
- **Working Capital Gap**: Limited working capital needs

## Tips for Best Results

1. **Be Accurate**: Use actual financial data from your books
2. **Be Conservative**: Round down on estimates
3. **Update Regularly**: Recalculate as your business changes
4. **Save Versions**: Track progress over time
5. **Review Recommendations**: Act on improvement suggestions

## Next Steps

After using the tool:
1. Review your readiness score and confidence level
2. Implement suggested improvements
3. Recalculate after making changes
4. Consult with a financial advisor or lender
5. Prepare documentation based on your analysis

## Support & Documentation

- Full documentation: See `README.md`
- Calculation details: See `calculations.py`
- Configuration: See `config.py`

## Deployment

To deploy on Render or similar platforms:

1. Push code to GitHub repository
2. Create new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

---

**Ready to get started?** Run `streamlit run app.py` and begin your financing analysis!
