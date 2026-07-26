
"""
Portfolio Performance Dashboard

This Streamlit app visualizes portfolio performance metrics, geometric returns,
stock trends, and portfolio composition using data from Excel.
# Make sure you open the folder containing this file before doing the installation and running steps.
# ✅ How to Install Required Libraries:
Run the following command in your terminal or command prompt:
    pip install streamlit pandas numpy plotly

# ✅ How to Run the Dashboard:
1. Open your terminal and navigate to the folder where the file is saved.
2. Run the Streamlit app using:
    streamlit run portfolio_dashboard.py
3. The dashboard will open in your default web browser.

# ✅ Requirements:
- Python 3.8 or higher
- Internet browser for viewing the dashboard
"""



import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')


st.set_page_config(
    page_title="Portfolio Return Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3B82F6;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1rem;
        text-align: center;
    }
    .metric-card h3 {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 0.5rem;
    }
    .metric-card h2 {
        font-size: 2rem;
        color: #1E40AF;
        margin: 0;
    }
    .comparison-positive {
        color: #10B981;
        font-weight: bold;
    }
    .comparison-negative {
        color: #EF4444;
        font-weight: bold;
    }
    .data-table {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


st.markdown("<h1 class='main-header'>📊 Portfolio Performance Dashboard</h1>", unsafe_allow_html=True)


with st.sidebar:
    st.markdown("## 🔍 Filters & Controls")
    
   
    st.markdown("### Stock Selection")
    all_stocks = ["One Tech Holding", "POULINA", "UNIMED", "AMV", "Attijari Bank", "ESSOUKNA", "SMART TUNISIE"]
    selected_stocks = st.multiselect(
        "Select stocks to display:",
        options=all_stocks,
        default=all_stocks[:3]
    )
    
    
    st.markdown("### Pie Chart Controls")
    show_pie_chart = st.checkbox("Show Portfolio Composition Pie Chart", value=True)
    
   
    st.markdown("### Display Options")
    show_daily_geometric = st.checkbox("Show Daily Geometric Returns Table", value=True)
    show_stock_performance = st.checkbox("Show Stock Performance", value=True)


@st.cache_data
def create_data():
    """Create data with exact values from Excel files."""
    
    dates = pd.to_datetime([
        '2025-12-15', '2025-12-16', '2025-12-17', '2025-12-18', '2025-12-19',
        '2025-12-22', '2025-12-23', '2025-12-24', '2025-12-25', '2025-12-26',
        '2025-12-29'
    ])
    
    
    portfolio_data = pd.DataFrame({
        'Date': dates,
        'Beginning_Value': [373.62, 372.68, 372.28, 372.28, 373.95, 373.7, 373.06, 372.52, 371.98, 372.93, 374.48],
        'Ending_Value': [372.68, 372.28, 372.28, 373.95, 373.7, 373.06, 372.52, 371.98, 372.93, 374.48, 376.50],
    })
    
    portfolio_data['Daily_Return'] = (portfolio_data['Ending_Value'] / portfolio_data['Beginning_Value']) - 1
    
    
    daily_returns_excel = [-0.0025, -0.0011, 0.0000, 0.0045, -0.0007, -0.0017, -0.0014, -0.0014, 0.0025, 0.0041, 0.0054]
    
    
    geometric_portfolio = [0.9975, 0.9964, 0.9964, 1.0009, 1.0002, 0.9985, 0.9971, 0.9957, 0.9982, 1.0023, 1.0076]
    geometric_tunindex = [0.9973, 0.9965, 0.9957, 0.9987, 1.0014, 1.0027, 1.0016, 1.0042, 1.0013, 1.0017, 1.0027]
    
    
    tunindex_returns = [-0.0027, -0.0008, -0.0008, 0.0030, 0.0027, 0.0013, -0.0011, 0.0026, -0.0029, 0.0004, 0.0010]
    
    geometric_data = pd.DataFrame({
        'Date': dates,
        'Portfolio_Geometric': geometric_portfolio,
        'TUNINDEX_Geometric': geometric_tunindex,
        'TUNINDEX_Return': tunindex_returns
    })
    
    
    stock_data = {}
    stock_prices = {
        "One Tech Holding": [79.65, 79.2, 79.2, 80.1, 79.83, 79.65, 79.38, 78.75, 78.66, 77.85, 78.66],
        "POULINA": [90.0, 89.9, 89.9, 89.75, 90.0, 90.0, 90.45, 90.0, 91.25, 91.95, 92.25],
        "UNIMED": [9.0, 8.9, 8.9, 8.98, 8.9, 9.06, 9.0, 8.9, 8.9, 8.89, 9.14],
        "AMV": [40.38, 39.9, 39.9, 40.2, 40.8, 40.8, 40.2, 40.5, 40.26, 40.26, 40.8],
        "Attijari Bank": [132.0, 132.98, 132.98, 132.78, 131.98, 131.4, 131.4, 131.78, 131.78, 133.3, 133.58],
        "ESSOUKNA": [3.07, 3.09, 3.09, 3.15, 3.29, 3.15, 3.09, 3.1, 3.18, 3.28, 3.14],
        "SMART TUNISIE": [18.58, 18.31, 18.31, 18.99, 18.9, 19.0, 19.0, 18.95, 18.9, 18.95, 18.93]
    }
    
    for stock, prices in stock_prices.items():
        stock_df = pd.DataFrame({
            'Date': dates,
            'Close_Price': prices
        })
        stock_df['Daily_Return'] = stock_df['Close_Price'].pct_change().fillna(0)
        stock_data[stock] = stock_df
    

    portfolio_weights = {}
    

    weights_summary = {
        "One Tech Holding": [21.25147579693034, 21.39518641882454, 21.27430965939616, 21.17930204572804, 21.43430559272143, 
                           21.39870262156222, 21.38140234081392, 21.33985698155815, 21.11656343013434, 21.00512710959196, 20.67729083665338],
        "POULINA": [24.00182462165933, 24.17535188567745, 24.14849038358225, 24.04064714534029, 24.01659084827402, 
                   24.12480566128773, 24.15977665628691, 24.31582343136728, 24.13321534872496, 24.36712240974151, 24.42231075697211],
        "UNIMED": [2.420306965761511, 2.417535188567745, 2.390673686472548, 2.379997325845701, 2.402997056462403, 
                  2.38567522650512, 2.432084183399549, 2.419484918544008, 2.386506851151691, 2.376628925443281, 2.361221779548472],
        "AMV": [10.86723194161211, 10.84667454604062, 10.71773933598367, 10.66987565182511, 10.75729194541076, 
               10.93657856645044, 10.9524320841834, 10.80703263616323, 10.85994690692623, 10.75090792565691, 10.69322709163346],
        "Attijari Bank": [35.90211441451111, 35.45718276566026, 35.72042548619319, 35.56090386415296, 35.53117473909553, 
                        35.37768723529727, 35.27327391817889, 35.32447981074252, 35.33639020727751, 35.19013031403546, 35.40504648074369],
        "ESSOUKNA": [0.8237630138456584, 0.8246481143225528, 0.8300204147415924, 0.8263136782992379, 0.8429221300508429, 
                   0.8818956736181848, 0.8455921829700419, 0.8306898220334427, 0.8312551953449709, 0.8491775261696218, 0.8711819389110224],
        "SMART TUNISIE": [4.985510357411183, 4.990867089287633, 4.9183410336306, 4.896376520925258, 5.081616269735082, 
                        5.066209188870423, 5.100397294105015, 5.107801494704016, 5.081382565092644, 5.046998504593035, 5.033200531208498]
    }
    
    for stock, weight_values in weights_summary.items():
        portfolio_weights[stock] = pd.DataFrame({
            'Date': dates,
            'Weight': [w / 100 for w in weight_values]  # Convert percentage to decimal
        })
    
    return portfolio_data, geometric_data, stock_data, portfolio_weights


portfolio_data, geometric_data, stock_data, portfolio_weights = create_data()


st.markdown("## 📈 Portfolio Performance Metrics")


portfolio_geometric_final = geometric_data['Portfolio_Geometric'].iloc[-1]
tunindex_geometric_final = geometric_data['TUNINDEX_Geometric'].iloc[-1]


portfolio_geometric_return = (portfolio_geometric_final - 1) * 100
tunindex_geometric_return = (tunindex_geometric_final - 1) * 100


outperformance = portfolio_geometric_return - tunindex_geometric_return


initial_value = portfolio_data['Beginning_Value'].iloc[0]
final_value = portfolio_data['Ending_Value'].iloc[-1]
cumulative_return_simple = ((final_value - initial_value) / initial_value) * 100
avg_daily_return = portfolio_data['Daily_Return'].mean() * 100
daily_volatility = portfolio_data['Daily_Return'].std() * 100


cumulative_returns = (1 + portfolio_data['Daily_Return']).cumprod()
running_max = cumulative_returns.expanding().max()
drawdown = (cumulative_returns - running_max) / running_max
max_drawdown = drawdown.min() * 100


st.markdown("### Geometric Returns Comparison (From Excel Columns J & P)")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <h3>Portfolio Geometric Return</h3>
        <h2>{portfolio_geometric_return:.4f}%</h2>
        <small>From Excel Column J</small>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <h3>TUNINDEX Geometric Return</h3>
        <h2>{tunindex_geometric_return:.4f}%</h2>
        <small>From Excel Column P</small>
    </div>
    """, unsafe_allow_html=True)

with col3:
    outperformance_class = "comparison-positive" if outperformance > 0 else "comparison-negative"
    outperformance_text = f"+{outperformance:.4f}%" if outperformance > 0 else f"{outperformance:.4f}%"
    st.markdown(f"""
    <div class='metric-card'>
        <h3>Outperformance</h3>
        <h2 class="{outperformance_class}">{outperformance_text}</h2>
        <small>Portfolio vs Benchmark</small>
    </div>
    """, unsafe_allow_html=True)

with col4:
    if outperformance > 0:
        result_text = "✓ Outperformed"
        result_color = "#10B981"
    else:
        result_text = "✗ Underperformed"
        result_color = "#EF4444"
    
    st.markdown(f"""
    <div class='metric-card'>
        <h3>Result</h3>
        <h2 style="color: {result_color}">{result_text}</h2>
        <small>vs TUNINDEX Benchmark</small>
    </div>
    """, unsafe_allow_html=True)


st.markdown("### Other Performance Metrics")

col5, col6, col7, col8 = st.columns(4)

with col5:
    st.markdown(f"""
    <div class='metric-card'>
        <h3>Simple Cumulative Return</h3>
        <h2>{cumulative_return_simple:.4f}%</h2>
        <small>(End - Start) / Start</small>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div class='metric-card'>
        <h3>Avg Daily Return</h3>
        <h2>{avg_daily_return:.4f}%</h2>
        <small>Arithmetic mean</small>
    </div>
    """, unsafe_allow_html=True)

with col7:
    st.markdown(f"""
    <div class='metric-card'>
        <h3>Daily Volatility</h3>
        <h2>{daily_volatility:.4f}%</h2>
        <small>Standard deviation</small>
    </div>
    """, unsafe_allow_html=True)

with col8:
    st.markdown(f"""
    <div class='metric-card'>
        <h3>Max Drawdown</h3>
        <h2>{max_drawdown:.4f}%</h2>
        <small>Maximum loss from peak</small>
    </div>
    """, unsafe_allow_html=True)


if show_daily_geometric:
    st.markdown("<h2 class='sub-header'>📋 Daily Geometric Returns from Excel</h2>", unsafe_allow_html=True)
    
    
    daily_geometric_table = pd.DataFrame({
        'Date': geometric_data['Date'].dt.strftime('%Y-%m-%d'),
        'Portfolio (1+Return)': geometric_data['Portfolio_Geometric'].round(6),
        'Portfolio Cumul Return %': ((geometric_data['Portfolio_Geometric'] - 1) * 100).round(4),
        'TUNINDEX (1+Return)': geometric_data['TUNINDEX_Geometric'].round(6),
        'TUNINDEX Cumul Return %': ((geometric_data['TUNINDEX_Geometric'] - 1) * 100).round(4),
        'TUNINDEX Daily Return %': (geometric_data['TUNINDEX_Return'] * 100).round(4)
    })
    
    
    st.markdown('<div class="data-table">', unsafe_allow_html=True)
    st.dataframe(daily_geometric_table, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    
    st.markdown("""
    **Table Explanation:**
    - **Portfolio (1+Return)**: Cumulative product of (1 + daily return) from Excel Column J
    - **Portfolio Cumul Return %**: Cumulative geometric return percentage = (1+Return - 1) * 100
    - **TUNINDEX (1+Return)**: Cumulative product of (1 + TUNINDEX return) from Excel Column P
    - **TUNINDEX Cumul Return %**: Cumulative geometric return percentage for TUNINDEX
    - **TUNINDEX Daily Return %**: Daily TUNINDEX returns from Excel Column N
    """)


st.markdown("<h2 class='sub-header'>📊 Portfolio Value Over Time</h2>", unsafe_allow_html=True)

fig_value = go.Figure()
fig_value.add_trace(go.Scatter(
    x=portfolio_data['Date'],
    y=portfolio_data['Ending_Value'],
    mode='lines+markers',
    name='Portfolio Value',
    line=dict(color='#3B82F6', width=3),
    marker=dict(size=8),
    hovertemplate='Date: %{x|%Y-%m-%d}<br>Value: %{y:.2f} TND<extra></extra>'
))

fig_value.update_layout(
    title='Portfolio Value Trend',
    xaxis_title='Date',
    yaxis_title='Portfolio Value (TND)',
    height=400,
    template='plotly_white',
    xaxis=dict(tickformat='%Y-%m-%d', tickangle=45)
)
st.plotly_chart(fig_value, use_container_width=True)


st.markdown("<h2 class='sub-header'>📈 Geometric Returns Comparison</h2>", unsafe_allow_html=True)

fig_geometric = go.Figure()
fig_geometric.add_trace(go.Scatter(
    x=geometric_data['Date'],
    y=(geometric_data['Portfolio_Geometric'] - 1) * 100,
    mode='lines+markers',
    name='Portfolio',
    line=dict(color='#3B82F6', width=3),
    marker=dict(size=8),
    hovertemplate='Date: %{x|%Y-%m-%d}<br>Return: %{y:.4f}%<extra></extra>'
))

fig_geometric.add_trace(go.Scatter(
    x=geometric_data['Date'],
    y=(geometric_data['TUNINDEX_Geometric'] - 1) * 100,
    mode='lines+markers',
    name='TUNINDEX',
    line=dict(color='#10B981', width=3, dash='dash'),
    marker=dict(size=8),
    hovertemplate='Date: %{x|%Y-%m-%d}<br>Return: %{y:.4f}%<extra></extra>'
))

fig_geometric.update_layout(
    title='Cumulative Geometric Returns',
    xaxis_title='Date',
    yaxis_title='Cumulative Return (%)',
    height=400,
    template='plotly_white',
    xaxis=dict(tickformat='%Y-%m-%d', tickangle=45)
)
st.plotly_chart(fig_geometric, use_container_width=True)


if show_pie_chart:
    st.markdown("<h2 class='sub-header'>🥧 Interactive Portfolio Composition</h2>", unsafe_allow_html=True)
    
    
    col9, col10 = st.columns(2)
    
    with col9:
        
        pie_stocks = st.multiselect(
            "Select stocks for portfolio composition:",
            options=all_stocks,
            default=all_stocks,
            key="pie_stocks"
        )
    
    with col10:
        
        available_dates = portfolio_data['Date'].dt.strftime('%Y-%m-%d').tolist()
        selected_date = st.selectbox(
            "Select date for portfolio composition:",
            options=available_dates,
            index=len(available_dates)-1,  
            key="pie_date"
        )
    
    
    selected_date_dt = pd.to_datetime(selected_date)
    
    if pie_stocks:
        
        col11, col12 = st.columns([2, 1])
        
        with col11:
            
            pie_data = []
            colors = ['#3B82F6', '#10B981', '#EF4444', '#F59E0B', '#8B5CF6', '#EC4899', '#14B8A6']
            
            for i, stock in enumerate(pie_stocks):
                if stock in portfolio_weights:
                    
                    weight_df = portfolio_weights[stock]
                    weight_row = weight_df[weight_df['Date'] == selected_date_dt]
                    
                    if not weight_row.empty:
                        weight = weight_row['Weight'].iloc[0] * 100  
                        color_idx = i % len(colors)
                        pie_data.append({
                            'Stock': stock,
                            'Weight': weight,
                            'Color': colors[color_idx]
                        })
            
            if pie_data:
                
                labels = [item['Stock'] for item in pie_data]
                values = [item['Weight'] for item in pie_data]
                colors_list = [item['Color'] for item in pie_data]
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.3,
                    marker=dict(colors=colors_list),
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>Weight: %{value:.2f}%<br>Percentage: %{percent}<extra></extra>'
                )])
                
                fig_pie.update_layout(
                    title=f"Portfolio Composition on {selected_date}",
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.warning(f"No weight data available for {selected_date}")
        
        with col12:
            
            if pie_data:
                weight_df = pd.DataFrame({
                    'Stock': [item['Stock'] for item in pie_data],
                    'Weight (%)': [f"{item['Weight']:.2f}" for item in pie_data]
                })
                
                st.markdown("### Portfolio Weights")
                st.markdown('<div class="data-table">', unsafe_allow_html=True)
                st.dataframe(weight_df, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                
                total_weight = sum([item['Weight'] for item in pie_data])
                st.metric("Total Portfolio Weight", f"{total_weight:.2f}%")
    
    
    if pie_stocks:
        st.markdown("### Portfolio Composition Over Time")
        
        
        fig_weights = go.Figure()
        
        for i, stock in enumerate(pie_stocks[:5]):  
            if stock in portfolio_weights:
                weight_df = portfolio_weights[stock]
                color_idx = i % len(colors)
                fig_weights.add_trace(go.Scatter(
                    x=weight_df['Date'],
                    y=weight_df['Weight'] * 100,  
                    mode='lines+markers',
                    name=stock,
                    line=dict(color=colors[color_idx], width=2),
                    marker=dict(size=6),
                    hovertemplate=f'{stock}<br>Date: %{{x|%Y-%m-%d}}<br>Weight: %{{y:.2f}}%<extra></extra>'
                ))
        
        fig_weights.update_layout(
            title='Portfolio Weight Evolution (Actual Weights from Excel)',
            xaxis_title='Date',
            yaxis_title='Weight (%)',
            height=400,
            template='plotly_white',
            xaxis=dict(tickformat='%Y-%m-%d', tickangle=45),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_weights, use_container_width=True)


if show_stock_performance and selected_stocks:
    st.markdown(f"<h2 class='sub-header'>📊 Selected Stocks Performance</h2>", unsafe_allow_html=True)
    
    
    tab1, tab2 = st.tabs(["Price Trends", "Performance Summary"])
    
    with tab1:
        fig_stocks = go.Figure()
        colors = ['#3B82F6', '#10B981', '#EF4444', '#F59E0B', '#8B5CF6', '#EC4899', '#14B8A6']
        
        for i, stock in enumerate(selected_stocks):
            if stock in stock_data and 'Close_Price' in stock_data[stock].columns:
                color_idx = i % len(colors)
                fig_stocks.add_trace(go.Scatter(
                    x=stock_data[stock]['Date'],
                    y=stock_data[stock]['Close_Price'],
                    mode='lines+markers',
                    name=stock,
                    line=dict(color=colors[color_idx], width=2),
                    marker=dict(size=6),
                    hovertemplate=f'{stock}<br>Date: %{{x|%Y-%m-%d}}<br>Price: %{{y:.2f}} TND<extra></extra>'
                ))
        
        fig_stocks.update_layout(
            title='Stock Price Trends',
            xaxis_title='Date',
            yaxis_title='Price (TND)',
            hovermode='x unified',
            height=400,
            template='plotly_white',
            showlegend=True,
            xaxis=dict(tickformat='%Y-%m-%d', tickangle=45)
        )
        st.plotly_chart(fig_stocks, use_container_width=True)
    
    with tab2:
        
        summary_data = []
        for stock in selected_stocks:
            if stock in stock_data:
                stock_df = stock_data[stock]
                if len(stock_df) > 0:
                    initial_price = stock_df['Close_Price'].iloc[0]
                    final_price = stock_df['Close_Price'].iloc[-1]
                    total_return = ((final_price - initial_price) / initial_price) * 100
                    
                    if 'Daily_Return' in stock_df.columns:
                        avg_return = stock_df['Daily_Return'].mean() * 100
                        volatility = stock_df['Daily_Return'].std() * 100
                    else:
                        avg_return = 0
                        volatility = 0
                    
                    summary_data.append({
                        'Stock': stock,
                        'Start Price (TND)': f"{initial_price:.2f}",
                        'End Price (TND)': f"{final_price:.2f}",
                        'Total Return %': f"{total_return:.2f}",
                        'Avg Daily %': f"{avg_return:.2f}",
                        'Volatility %': f"{volatility:.2f}"
                    })
        
        if summary_data:
            st.markdown('<div class="data-table">', unsafe_allow_html=True)
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No stock data available for selected stocks")


st.markdown("<h2 class='sub-header'>📊 Summary Statistics</h2>", unsafe_allow_html=True)

col13, col14, col15, col16 = st.columns(4)

with col13:
    st.metric("Initial Value", f"{initial_value:.2f} TND")
    
with col14:
    st.metric("Final Value", f"{final_value:.2f} TND")

with col15:
    absolute_gain = final_value - initial_value
    st.metric("Absolute Gain", f"{absolute_gain:.2f} TND")

with col16:
    st.metric("Trading Days", len(portfolio_data))


st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; padding: 2rem;'>
    <p><strong>Portfolio Performance Dashboard</strong> • Using Exact Values from Excel</p>
    <p>Geometric Returns from Columns J & P • Actual Weights from Portfolio_Data_Corrected.xlsx</p>
</div>
""", unsafe_allow_html=True)