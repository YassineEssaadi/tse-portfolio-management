# REQUIRED PACKAGES
# pip install pandas
# pip install numpy
# pip install plotly
# pip install openpyxl


import pandas as pd
import numpy as np
import re
from unicodedata import normalize as uni_normalize
import plotly.graph_objects as go
from datetime import datetime


def norm(s):
    if not isinstance(s, str):
        return s
    s2 = uni_normalize('NFKD', s).encode('ascii','ignore').decode('ascii')
    s2 = re.sub(r'\s+', ' ', s2).strip().lower()
    return s2

def find_in_sheet(df, patterns):
    norm_map = {c: norm(c) for c in df.columns}
    for c, n in norm_map.items():
        if any(p == n for p in patterns):
            return c
    return None

def get_date_col(df):
    return find_in_sheet(df, ['date', 'time', 'datetime'])

def parse_date_robust(date_series):
    try:
        return pd.to_datetime(date_series, errors='coerce')
    except:
        pass
    
    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y.%m.%d', '%d-%m-%Y', '%d.%m.%Y']:
        try:
            return pd.to_datetime(date_series, format=fmt, errors='coerce')
        except:
            continue
    
    return pd.to_datetime(date_series, errors='coerce')

def clean_numeric_column(series):
    series_numeric = pd.to_numeric(series, errors='coerce')
    
    if series_numeric.isna().sum() > len(series) * 0.5:
        def extract_number(x):
            if isinstance(x, str):
                numbers = re.findall(r'[-+]?\d*\.\d+|\d+', x)
                if numbers:
                    return float(numbers[0])
            return x
        
        series = series.apply(extract_number)
        series_numeric = pd.to_numeric(series, errors='coerce')
    
    return series_numeric


xl_path = 'POULINA GH.xlsx'
all_sheets = pd.read_excel(xl_path, sheet_name=None, engine='openpyxl')


print("\n=== DATE DIAGNOSTICS ===")
for sheet_name, df in all_sheets.items():
    date_col = get_date_col(df)
    if date_col:
        sample_dates = df[date_col].head(3).tolist()
        print(f"Sheet: {sheet_name}")
        print(f"  Date column: '{date_col}'")
        print(f"  Sample raw values: {sample_dates}")
        print(f"  Data types of sample: {[type(d) for d in sample_dates]}")
        print(f"  Unique types in column: {df[date_col].apply(type).unique()}")
        
        
        parsed = parse_date_robust(df[date_col].head(3))
        print(f"  Parsed dates: {parsed.tolist()}")
        print("-" * 50)

FIELDS = {
    'Price':        ['cours ajuste'],
    'RSI':          ['14-day rsi'],
    'MACD':         ['macd line'],
    'MACD_Signal':  ['signal line'],
    'MACD_Hist':    ['macd histogram'],
    'OBV':          ['obv'],
    'MA_5':         ['simple moving avg (5)'],
    'MA_10':        ['simple moving avg (10)'],
    'MA_20':        ['simple moving avg (20)'],
    'MA_50':        ['simple moving avg (50)'],
    'MA_200':       ['simple moving avg (200)'],
    'EMA_20':       ['exp moving avg (20)'],
    'EMA_50':       ['exp moving avg (50)'],
}


found = {k: None for k in FIELDS}
sheet_order = sorted(all_sheets.keys(), key=lambda s: 0 if 'scoring' in norm(s) else 1)

print("Scanning for columns...")
for sh in sheet_order:
    df = all_sheets[sh]
    date_col = get_date_col(df)
    if date_col is None:
        continue
    
    print(f"  Sheet: {sh}")
    print(f"    Date column: {date_col}")
    
    for field, patterns in FIELDS.items():
        if found[field] is not None:
            continue
        col = find_in_sheet(df, patterns)
        if col:
            found[field] = (sh, date_col, col)
            print(f"    Found {field} at column: {col}")
            preview_vals = df[col].head(5).tolist()
            print(f"      Preview: {preview_vals}")

print("\n" + "="*50)
print("Summary of found columns:")
for field, info in found.items():
    if info:
        sh, date_col, value_col = info
        print(f"  {field}: Sheet='{sh}', Date='{date_col}', Value='{value_col}'")
    else:
        print(f"  {field}: NOT FOUND")

if found['Price'] is None:
    raise ValueError("Price column not found.")


anchor_sh, anchor_date, anchor_col = found['Price']
anchor_df = all_sheets[anchor_sh].copy()


anchor_df['Date'] = parse_date_robust(anchor_df[anchor_date])
anchor_df[anchor_col] = clean_numeric_column(anchor_df[anchor_col])
anchor_df = anchor_df[['Date', anchor_col]].dropna()
anchor_df.rename(columns={anchor_col: 'Price'}, inplace=True)

print(f"\nPrice data shape: {anchor_df.shape}")
print(f"Price date range: {anchor_df['Date'].min()} to {anchor_df['Date'].max()}")

master = (
    anchor_df
    .sort_values('Date')
    .drop_duplicates('Date')
    .set_index('Date')
)

for field, info in found.items():
    if field == 'Price' or info is None:
        continue

    sh, date_col, value_col = info
    temp = all_sheets[sh].copy()
    temp['Date'] = parse_date_robust(temp[date_col])
    
    temp[value_col] = clean_numeric_column(temp[value_col])
    
    if field.startswith('EMA_'):
        print(f"\n⚠️ Special handling for {field}: Removing initial 0/NaN values")
        valid_mask = (temp[value_col].notna()) & (temp[value_col] != 0)
        if valid_mask.any():
            first_valid_idx = valid_mask[valid_mask].index[0]
            mask_before_valid = temp.index < first_valid_idx
            temp.loc[mask_before_valid, value_col] = np.nan
            print(f"  First valid EMA value starts at index {first_valid_idx}")
            
            ema_values = temp[value_col].dropna()
            if len(ema_values) > 1:
                ema_array = ema_values.values
                if len(ema_array) > 5:
                    first_5_values = ema_array[:5]  
                    diffs = np.diff(first_5_values)  
                    pct_changes = np.abs(diffs / first_5_values[:-1])  
                    
                    stable_idx = np.where(pct_changes < 0.05)[0]
                    if len(stable_idx) > 0:
                        stable_start = stable_idx[0] + 1  
                        if stable_start > 0 and stable_start < len(ema_values):
                            stable_date = ema_values.index[stable_start]
                            mask_before_stable = temp.index < stable_date
                            temp.loc[mask_before_stable, value_col] = np.nan
                            print(f"  Stable EMA starts at {stable_date}")
    

    if field.startswith('MA_'):
        print(f"\n⚠️ Special handling for {field}: Removing initial 0/NaN values")
        valid_mask = (temp[value_col].notna()) & (temp[value_col] != 0)
        if valid_mask.any():
            first_valid_idx = valid_mask[valid_mask].index[0]
            mask_before_valid = temp.index < first_valid_idx
            temp.loc[mask_before_valid, value_col] = np.nan
            print(f"  First valid MA value starts at index {first_valid_idx}")
    
    temp = temp[['Date', value_col]].dropna()
    temp.rename(columns={value_col: field}, inplace=True)
    
    print(f"\nMerging {field}:")
    print(f"  Shape before merge: {temp.shape}")
    print(f"  Date range: {temp['Date'].min()} to {temp['Date'].max()}")
    print(f"  Non-null values: {temp[field].notna().sum()}/{len(temp)}")
    if len(temp) > 0:
        print(f"  First 3 values: {temp[field].head(3).tolist()}")
        print(f"  Last 3 values: {temp[field].tail(3).tolist()}")

    master = master.merge(
        temp.set_index('Date'),
        left_index=True,
        right_index=True,
        how='left'
    )

print(f"\nMaster DataFrame shape: {master.shape}")
print(f"Master DataFrame columns: {list(master.columns)}")
print(f"Master date range: {master.index.min()} to {master.index.max()}")


print("\n" + "="*50)
print("CHECKING FOR MISSING MOVING AVERAGES")
print("="*50)


missing_mas = []
for ma_field in ['MA_5', 'MA_10', 'MA_20', 'MA_50', 'MA_200']:
    if ma_field in master.columns and master[ma_field].notna().sum() > 0:
        non_null_pct = master[ma_field].notna().sum() / len(master) * 100
        print(f"✓ {ma_field}: Found in data ({non_null_pct:.1f}% non-null)")
    else:
        print(f"✗ {ma_field}: NOT FOUND in data")
        missing_mas.append(ma_field)


print("\n" + "="*50)
print("FINAL CLEANING OF MA AND EMA DATA")
print("="*50)

def clean_trend_column(series, column_name, is_ema=False):
    """Clean MA/EMA columns by removing initial NaN/zero values and ensuring smooth start"""
    if series is None or len(series) == 0:
        return series
    
    series_clean = series.copy()
    
    non_nan_mask = series_clean.notna()
    
    if non_nan_mask.any():
        first_non_nan_idx = series_clean[non_nan_mask].index[0]
        first_non_nan_val = series_clean.loc[first_non_nan_idx]
        
        print(f"\n  Cleaning {column_name}:")
        print(f"    First non-NaN value at {first_non_nan_idx.date()}: {first_non_nan_val}")
        

        if abs(first_non_nan_val) < 0.001:
            print(f"    Warning: First value is near zero ({first_non_nan_val})")
            reasonable_mask = (series_clean.notna()) & (abs(series_clean) > 0.001)
            if reasonable_mask.any():
                first_reasonable_idx = series_clean[reasonable_mask].index[0]
                mask_before_reasonable = series_clean.index < first_reasonable_idx
                series_clean.loc[mask_before_reasonable] = np.nan
                print(f"    Set values before {first_reasonable_idx.date()} to NaN")
        
        
        if is_ema and series_clean.notna().sum() > 5:
            ema_values = series_clean.dropna()
            ema_array = ema_values.values[:10] 
            
            if len(ema_array) > 3:
                diffs = np.diff(ema_array[:5])  
                if len(diffs) > 0:
                    pct_changes = np.abs(diffs / ema_array[:4])  
                    large_jumps = pct_changes > 0.1
                    if large_jumps.any():
                        stable_mask = pct_changes < 0.05
                        if stable_mask.any():
                            first_stable = np.where(stable_mask)[0]
                            if len(first_stable) > 0:
                                stable_start = first_stable[0] + 1 
                                if stable_start < len(ema_values):
                                    stable_date = ema_values.index[stable_start]
                                    mask_before_stable = series_clean.index < stable_date
                                    series_clean.loc[mask_before_stable] = np.nan
                                    print(f"    EMA stabilized at {stable_date.date()}")
    
    return series_clean


print("\nCleaning EMA columns:")
for ema_col in ['EMA_20', 'EMA_50']:
    if ema_col in master.columns:
        master[ema_col] = clean_trend_column(master[ema_col], ema_col, is_ema=True)
        
        
        ema_data = master[ema_col].dropna()
        if len(ema_data) > 0:
            print(f"  {ema_col}: {len(ema_data)} data points")
            print(f"    Starts at: {ema_data.index[0].date()} (value: {ema_data.iloc[0]:.2f})")
            print(f"    Ends at: {ema_data.index[-1].date()} (value: {ema_data.iloc[-1]:.2f})")


print("\nCleaning MA columns:")
for ma_col in ['MA_5', 'MA_10', 'MA_20', 'MA_50', 'MA_200']:
    if ma_col in master.columns:
        master[ma_col] = clean_trend_column(master[ma_col], ma_col, is_ema=False)
        
        
        ma_data = master[ma_col].dropna()
        if len(ma_data) > 0:
            print(f"  {ma_col}: {len(ma_data)} data points")
            print(f"    Starts at: {ma_data.index[0].date()} (value: {ma_data.iloc[0]:.2f})")


print("\n" + "="*50)
print("INTERPOLATING DATA")
print("="*50)

num_cols = master.select_dtypes(include='number').columns
for col in num_cols:
    non_null_pct = master[col].notna().sum() / len(master) * 100
    
    
    if col.startswith('EMA_'):
        print(f"Skipping interpolation for {col}: EMA should not be interpolated")
        continue
    
    if non_null_pct > 10:  
        
        if col not in ['EMA_20', 'EMA_50', 'MA_200', 'MA_50']:
            master[col] = master[col].interpolate(limit_direction='both')
            print(f"Interpolated {col}: {non_null_pct:.1f}% non-null before interpolation")
        else:
           
            master[col] = master[col].interpolate(limit_direction='forward')
            print(f"Forward interpolated {col}: {non_null_pct:.1f}% non-null before interpolation")


fig_price = go.Figure()


price_trace = go.Scatter(
    x=master.index,
    y=master['Price'],
    mode='lines',
    name='Price',
    line=dict(color='#00BFFF', width=3)
)
fig_price.add_trace(price_trace)

ema_colors = {
    'EMA_20': '#FF4D4D',  
    'EMA_50': '#00FF7F'    
}


for ema_key, color in ema_colors.items():
    if ema_key in master.columns:
        
        ema_data = master[ema_key].dropna()
        if len(ema_data) > 0:
            trace = go.Scatter(
                x=ema_data.index,
                y=ema_data.values,
                mode='lines',
                name=ema_key.replace('_', ' '),
                line=dict(color=color, width=2),
                visible=True
            )
            fig_price.add_trace(trace)
            print(f"✅ Added {ema_key}: {len(ema_data)} data points (starting from {ema_data.index[0].date()})")


ema_buttons = []


all_visibility = [True] + [True] * (len(fig_price.data) - 1)  
ema_buttons.append(
    dict(
        label="All EMAs",
        method="update",
        args=[{"visible": all_visibility}]
    )
)


price_only_visibility = [True] + [False] * (len(fig_price.data) - 1) 
ema_buttons.append(
    dict(
        label="Price Only",
        method="update",
        args=[{"visible": price_only_visibility}]
    )
)


for i in range(1, len(fig_price.data)):  
    trace = fig_price.data[i]
    visibility = [True] + [False] * (len(fig_price.data) - 1)  
    visibility[i] = True  
    
    ema_buttons.append(
        dict(
            label=f"Price + {trace.name}",
            method="update",
            args=[{"visible": visibility}]
        )
    )

fig_price.update_layout(
    title='Price + EMAs (Use dropdown to toggle EMAs)',
    plot_bgcolor='rgb(40,40,40)',
    paper_bgcolor='rgb(40,40,40)',
    font=dict(color='white'),
    xaxis=dict(
        rangeslider=dict(visible=True),
        type='date',
        title='Date',
        gridcolor='rgba(255,255,255,0.1)'
    ),
    yaxis=dict(
        title='Price',
        gridcolor='rgba(255,255,255,0.1)'
    ),
    hovermode='x unified',
    showlegend=True,
    height=600,
    updatemenus=[
        dict(
            type="dropdown",
            direction="down",
            buttons=ema_buttons,
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.02,  
            xanchor="left",
            y=1.02,  
            yanchor="bottom",
            bgcolor='rgba(0,0,0,0.7)',
            bordercolor='white',
            borderwidth=1,
            font=dict(color='white')
        ),
    ]
)


fig_price.update_xaxes(
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
        ]),
        bgcolor='rgba(0,0,0,0.7)',
        activecolor='rgba(0,150,255,0.7)',
        bordercolor='white',
        borderwidth=1,
        font=dict(color='white'),
        x=0.75,  
        xanchor="left",
        y=0.99,  
        yanchor="bottom"
    )
)

fig_price.show()
print("\n✅ Price + EMAs chart created with dropdown toggle buttons (Price always shown)")


fig_ma = go.Figure()


price_trace_ma = go.Scatter(
    x=master.index,
    y=master['Price'],
    mode='lines',
    name='Price',
    line=dict(color='#00BFFF', width=3)
)
fig_ma.add_trace(price_trace_ma)

ma_colors = {
    'MA_5':   '#FFD700',   
    'MA_10':  '#FF69B4',   
    'MA_20':  '#00FFFF',   
    'MA_50':  '#7CFC00',   
    'MA_200': '#FFA500'    
}

ma_traces_list = []


for ma_key, color in ma_colors.items():
    if ma_key in master.columns and master[ma_key].notna().sum() > 0:
        
        ma_data = master[ma_key].dropna()
        if len(ma_data) > 0:
            trace = go.Scatter(
                x=ma_data.index,
                y=ma_data.values,
                mode='lines',
                name=ma_key.replace('_', ' '),
                line=dict(color=color, width=2),
                visible=True,
                connectgaps=False
            )
            fig_ma.add_trace(trace)
            ma_traces_list.append(trace)
            print(f"✅ Added {ma_key}: {len(ma_data)} data points (starting from {ma_data.index[0].date()})")

print(f"\n✅ Added {len(ma_traces_list)} MA traces to the chart")


if len(ma_traces_list) == 0:
    print("⚠️ No MA data found for chart. Check if MA columns exist in your Excel file.")
else:
    
    ma_buttons = []

    
    all_ma_visibility = [True] + [True] * len(ma_traces_list)  
    ma_buttons.append(
        dict(
            label="All MAs",
            method="update",
            args=[{"visible": all_ma_visibility}]
        )
    )


    price_only_ma_visibility = [True] + [False] * len(ma_traces_list)  
    ma_buttons.append(
        dict(
            label="Price Only",
            method="update",
            args=[{"visible": price_only_ma_visibility}]
        )
    )

    
    for i in range(1, len(fig_ma.data)):  
        trace = fig_ma.data[i]
        visibility = [True] + [False] * len(ma_traces_list)  
        visibility[i] = True  
        
        ma_buttons.append(
            dict(
                label=f"Price + {trace.name}",
                method="update",
                args=[{"visible": visibility}]
            )
        )

    
    common_combinations = [
        ("Price + Short-term (5,10)", [1, 2]),  
        ("Price + Medium-term (20,50)", [3, 4]),  
        ("Price + Long-term (50,200)", [4, 5]),  
        ("Price + All Short (5,10,20)", [1, 2, 3]),  
    ]

    for label, indices in common_combinations:
        if all(idx < len(fig_ma.data) for idx in indices):
            visibility = [True] + [False] * len(ma_traces_list)  
            for idx in indices:
                if idx < len(visibility):
                    visibility[idx] = True
            ma_buttons.append(
                dict(
                    label=label,
                    method="update",
                    args=[{"visible": visibility}]
                )
            )

    fig_ma.update_layout(
        title=f'Price + Moving Averages (Use dropdown to toggle MAs)',
        plot_bgcolor='rgb(40,40,40)',
        paper_bgcolor='rgb(40,40,40)',
        font=dict(color='white'),
        xaxis=dict(
            rangeslider=dict(visible=True),
            type='date',
            title='Date',
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title='Value',
            gridcolor='rgba(255,255,255,0.1)'
        ),
        hovermode='x unified',
        showlegend=True,
        height=600,
        updatemenus=[
            dict(
                type="dropdown",
                direction="down",
                buttons=ma_buttons,
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.02,  
                xanchor="left",
                y=1.02,  
                yanchor="bottom",
                bgcolor='rgba(0,0,0,0.7)',
                bordercolor='white',
                borderwidth=1,
                font=dict(color='white')
            ),
        ]
    )

    
    fig_ma.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ]),
            bgcolor='rgba(0,0,0,0.7)',
            activecolor='rgba(0,150,255,0.7)',
            bordercolor='white',
            borderwidth=1,
            font=dict(color='white'),
            x=0.75,  
            xanchor="left",
            y=0.99,  
            yanchor="bottom"
        )
    )

    fig_ma.show()
    print("✅ Price + Moving Averages chart created with dropdown toggle buttons (Price always shown)")


if 'RSI' in master.columns:
    fig_rsi = go.Figure()
    rsi_data = master['RSI'].dropna()
    
    if len(rsi_data) > 0:
        
        rsi_trace = go.Scatter(
            x=rsi_data.index,
            y=rsi_data.values,
            mode='lines',
            name='RSI',
            line=dict(color='#FF3333', width=2)
        )
        fig_rsi.add_trace(rsi_trace)
        
        
        overbought_trace = go.Scatter(
            x=[rsi_data.index[0], rsi_data.index[-1]],
            y=[70, 70],
            mode='lines',
            name='Overbought (70)',
            line=dict(color='red', width=1, dash='dash'),
            opacity=0.5
        )
        
        oversold_trace = go.Scatter(
            x=[rsi_data.index[0], rsi_data.index[-1]],
            y=[30, 30],
            mode='lines',
            name='Oversold (30)',
            line=dict(color='green', width=1, dash='dash'),
            opacity=0.5
        )
        
        middle_trace = go.Scatter(
            x=[rsi_data.index[0], rsi_data.index[-1]],
            y=[50, 50],
            mode='lines',
            name='Middle (50)',
            line=dict(color='yellow', width=0.5, dash='dot'),
            opacity=0.3
        )
        
        fig_rsi.add_trace(overbought_trace)
        fig_rsi.add_trace(oversold_trace)
        fig_rsi.add_trace(middle_trace)
        
        
        rsi_buttons = [
            dict(
                label="RSI + All Levels",
                method="update",
                args=[{"visible": [True, True, True, True]}]
            ),
            dict(
                label="RSI Only",
                method="update",
                args=[{"visible": [True, False, False, False]}]
            ),
            dict(
                label="RSI + Overbought/Oversold",
                method="update",
                args=[{"visible": [True, True, True, False]}]
            ),
        ]
        
        fig_rsi.update_layout(
            title='RSI (Use dropdown to toggle levels)',
            plot_bgcolor='rgb(40,40,40)',
            paper_bgcolor='rgb(40,40,40)',
            font=dict(color='white'),
            xaxis=dict(
                rangeslider=dict(visible=True),
                type='date',
                title='Date',
                gridcolor='rgba(255,255,255,0.1)'
            ),
            yaxis=dict(
                range=[0,100],
                gridcolor='rgba(255,255,255,0.1)'
            ),
            hovermode='x unified',
            showlegend=True,
            height=500,
            updatemenus=[
                dict(
                    type="dropdown",
                    direction="down",
                    buttons=rsi_buttons,
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.02,  
                    xanchor="left",
                    y=1.02,  
                    yanchor="bottom",
                    bgcolor='rgba(0,0,0,0.7)',
                    bordercolor='white',
                    borderwidth=1,
                    font=dict(color='white')
                ),
            ]
        )
        
        
        fig_rsi.update_xaxes(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ]),
                bgcolor='rgba(0,0,0,0.7)',
                activecolor='rgba(0,150,255,0.7)',
                bordercolor='white',
                borderwidth=1,
                font=dict(color='white'),
                x=0.75,  
                xanchor="left",
                y=0.99,  
                yanchor="bottom"
            )
        )
        fig_rsi.show()
        print("✅ RSI chart created with dropdown toggle buttons")
    else:
        print("⚠️ RSI column exists but has no valid data")


fig_macd = go.Figure()

macd_traces = []
trace_names = []


if 'MACD' in master.columns:
    macd_data = master['MACD'].dropna()
    if len(macd_data) > 0:
        macd_trace = go.Scatter(
            x=macd_data.index,
            y=macd_data.values,
            mode='lines',
            name='MACD',
            line=dict(color='#00BFFF', width=2),
            visible=True
        )
        fig_macd.add_trace(macd_trace)
        macd_traces.append(macd_trace)
        trace_names.append('MACD')


if 'MACD_Signal' in master.columns:
    signal_data = master['MACD_Signal'].dropna()
    if len(signal_data) > 0:
        signal_trace = go.Scatter(
            x=signal_data.index,
            y=signal_data.values,
            mode='lines',
            name='Signal',
            line=dict(color='#FF69B4', width=2),
            visible=True
        )
        fig_macd.add_trace(signal_trace)
        macd_traces.append(signal_trace)
        trace_names.append('Signal')


if 'MACD_Hist' in master.columns:
    hist_data = master['MACD_Hist'].dropna()
    if len(hist_data) > 0:
        hist_trace = go.Bar(
            x=hist_data.index,
            y=hist_data.values,
            name='Histogram',
            marker_color=np.where(hist_data.values >= 0, '#00FF7F', '#FF4D4D'),
            opacity=0.7,
            visible=True
        )
        fig_macd.add_trace(hist_trace)
        macd_traces.append(hist_trace)
        trace_names.append('Histogram')

if len(macd_traces) > 0:
    
    macd_buttons = []
    
    
    macd_buttons.append(
        dict(
            label="All Components",
            method="update",
            args=[{"visible": [True] * len(fig_macd.data)}]
        )
    )
    
    
    for i, name in enumerate(trace_names):
        visibility = [False] * len(fig_macd.data)
        visibility[i] = True
        macd_buttons.append(
            dict(
                label=f"{name} Only",
                method="update",
                args=[{"visible": visibility}]
            )
        )
    
    
    if 'MACD' in trace_names and 'Signal' in trace_names:
        
        macd_idx = trace_names.index('MACD')
        signal_idx = trace_names.index('Signal')
        visibility = [False] * len(fig_macd.data)
        visibility[macd_idx] = True
        visibility[signal_idx] = True
        macd_buttons.append(
            dict(
                label="MACD + Signal",
                method="update",
                args=[{"visible": visibility}]
            )
        )
    
    fig_macd.update_layout(
        title='MACD (Use dropdown to toggle components)',
        plot_bgcolor='rgb(40,40,40)',
        paper_bgcolor='rgb(40,40,40)',
        font=dict(color='white'),
        xaxis=dict(
            rangeslider=dict(visible=True),
            type='date',
            title='Date',
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title='MACD Value',
            gridcolor='rgba(255,255,255,0.1)'
        ),
        hovermode='x unified',
        showlegend=True,
        height=600,
        bargap=0,
        updatemenus=[
            dict(
                type="dropdown",
                direction="down",
                buttons=macd_buttons,
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.02,  
                xanchor="left",
                y=1.02,  
                yanchor="bottom",
                bgcolor='rgba(0,0,0,0.7)',
                bordercolor='white',
                borderwidth=1,
                font=dict(color='white')
            ),
        ]
    )
    
    
    fig_macd.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ]),
            bgcolor='rgba(0,0,0,0.7)',
            activecolor='rgba(0,150,255,0.7)',
            bordercolor='white',
            borderwidth=1,
            font=dict(color='white'),
            x=0.75,  
            xanchor="left",
            y=0.99,  
            yanchor="bottom"
        )
    )
    fig_macd.show()
    print("✅ MACD chart created with dropdown toggle buttons")
else:
    print("⚠️ No MACD data available for chart")


if 'OBV' in master.columns:
    fig_obv = go.Figure()
    obv_data = master['OBV'].dropna()
    
    if len(obv_data) > 0:
        
        obv_trace = go.Scatter(
            x=obv_data.index,
            y=obv_data.values,
            mode='lines',
            name='OBV',
            line=dict(color='#00E5FF', width=2)
        )
        fig_obv.add_trace(obv_trace)
        
        
        if len(obv_data) > 20:
            obv_ma_20 = obv_data.rolling(window=20).mean()
            obv_ma_trace = go.Scatter(
                x=obv_ma_20.index,
                y=obv_ma_20.values,
                mode='lines',
                name='OBV MA(20)',
                line=dict(color='#FF69B4', width=1, dash='dash'),
                opacity=0.7,
                visible=True
            )
            fig_obv.add_trace(obv_ma_trace)
            
            
            obv_buttons = [
                dict(
                    label="OBV + MA",
                    method="update",
                    args=[{"visible": [True, True]}]
                ),
                dict(
                    label="OBV Only",
                    method="update",
                    args=[{"visible": [True, False]}]
                ),
            ]
            
            fig_obv.update_layout(
                title='On-Balance Volume (OBV)',
                plot_bgcolor='rgb(40,40,40)',
                paper_bgcolor='rgb(40,40,40)',
                font=dict(color='white'),
                xaxis=dict(
                    rangeslider=dict(visible=True),
                    type='date',
                    title='Date',
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                yaxis=dict(
                    title='OBV',
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                hovermode='x unified',
                showlegend=True,
                height=500,
                updatemenus=[
                    dict(
                        type="dropdown",
                        direction="down",
                        buttons=obv_buttons,
                        pad={"r": 10, "t": 10},
                        showactive=True,
                        x=0.02,  
                        xanchor="left",
                        y=1.02,  
                        yanchor="bottom",
                        bgcolor='rgba(0,0,0,0.7)',
                        bordercolor='white',
                        borderwidth=1,
                        font=dict(color='white')
                    ),
                ]
            )
        else:
            fig_obv.update_layout(
                title='On-Balance Volume (OBV)',
                plot_bgcolor='rgb(40,40,40)',
                paper_bgcolor='rgb(40,40,40)',
                font=dict(color='white'),
                xaxis=dict(
                    rangeslider=dict(visible=True),
                    type='date',
                    title='Date',
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                yaxis=dict(
                    title='OBV',
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                hovermode='x unified',
                showlegend=True,
                height=500
            )
        
        
        fig_obv.update_xaxes(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ]),
                bgcolor='rgba(0,0,0,0.7)',
                activecolor='rgba(0,150,255,0.7)',
                bordercolor='white',
                borderwidth=1,
                font=dict(color='white'),
                x=0.75,  
                xanchor="left",
                y=0.99,  
                yanchor="bottom"
            )
        )
        fig_obv.show()
        print("✅ OBV chart created with toggle button for moving average")
    else:
        print("⚠️ OBV column exists but has no valid data")


print("\n" + "="*50)
print("GOLDEN CROSS & DEATH CROSS ANALYSIS")
print("="*50)

if 'MA_50' in master.columns and 'MA_200' in master.columns:
    ma_50_data = master['MA_50'].dropna()
    ma_200_data = master['MA_200'].dropna()
    
    if len(ma_50_data) > 0 and len(ma_200_data) > 0:
        print("✅ Required MAs found for Golden/Death Cross analysis")
        
        
        common_dates = ma_50_data.index.intersection(ma_200_data.index)
        cross_data = master.loc[common_dates, ['Price', 'MA_50', 'MA_200']].copy()
        
       
        cross_data['MA_50_above_MA_200'] = cross_data['MA_50'] > cross_data['MA_200']
        
        
        cross_data['Prev_MA_50_above'] = cross_data['MA_50_above_MA_200'].shift(1)
        
        
        cross_data['Golden_Cross'] = (
            (cross_data['Prev_MA_50_above'] == False) & 
            (cross_data['MA_50_above_MA_200'] == True)
        )
        
        
        cross_data['Death_Cross'] = (
            (cross_data['Prev_MA_50_above'] == True) & 
            (cross_data['MA_50_above_MA_200'] == False)
        )
        
        
        golden_cross_dates = cross_data[cross_data['Golden_Cross']].index
        death_cross_dates = cross_data[cross_data['Death_Cross']].index
        
        print(f"📈 Found {len(golden_cross_dates)} Golden Cross signals")
        print(f"📉 Found {len(death_cross_dates)} Death Cross signals")
        
        if len(golden_cross_dates) > 0:
            print("\nGolden Cross dates:")
            for date in golden_cross_dates[:10]:  
                price_val = cross_data.loc[date, 'Price']
                ma50_val = cross_data.loc[date, 'MA_50']
                ma200_val = cross_data.loc[date, 'MA_200']
                print(f"  {date.date()}: Price={price_val:.2f}, MA50={ma50_val:.2f}, MA200={ma200_val:.2f}")
        
        if len(death_cross_dates) > 0:
            print("\nDeath Cross dates:")
            for date in death_cross_dates[:10]:  
                price_val = cross_data.loc[date, 'Price']
                ma50_val = cross_data.loc[date, 'MA_50']
                ma200_val = cross_data.loc[date, 'MA_200']
                print(f"  {date.date()}: Price={price_val:.2f}, MA50={ma50_val:.2f}, MA200={ma200_val:.2f}")
        
        
        if len(golden_cross_dates) > 0:
            fig_golden = go.Figure()
            
            
            fig_golden.add_trace(go.Scatter(
                x=cross_data.index,
                y=cross_data['Price'],
                mode='lines',
                name='Price',
                line=dict(color='#00BFFF', width=2)
            ))
            
            
            fig_golden.add_trace(go.Scatter(
                x=cross_data.index,
                y=cross_data['MA_50'],
                mode='lines',
                name='MA_50',
                line=dict(color='#7CFC00', width=2)  
            ))
            
            
            fig_golden.add_trace(go.Scatter(
                x=cross_data.index,
                y=cross_data['MA_200'],
                mode='lines',
                name='MA_200',
                line=dict(color='#FFA500', width=2)  
            ))
            
            
            golden_prices = cross_data.loc[golden_cross_dates, 'Price']
            fig_golden.add_trace(go.Scatter(
                x=golden_cross_dates,
                y=golden_prices * 0.98,  
                mode='markers',
                name='Golden Cross',
                marker=dict(
                    symbol='triangle-up',
                    size=12,
                    color='#00FF00',
                    line=dict(width=2, color='white')
                ),
                hovertemplate='<b>Golden Cross</b><br>Date: %{x|%Y-%m-%d}<br>Price: %{y:.2f}<extra></extra>'
            ))
            
            fig_golden.update_layout(
                title=f'Golden Cross Signals (MA_50 crosses above MA_200) - {len(golden_cross_dates)} signals',
                plot_bgcolor='rgb(40,40,40)',
                paper_bgcolor='rgb(40,40,40)',
                font=dict(color='white'),
                xaxis=dict(
                    rangeslider=dict(visible=True),
                    type='date',
                    title='Date',
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                yaxis=dict(
                    title='Price',
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                hovermode='x unified',
                showlegend=True,
                height=600
            )
            
            
            golden_buttons = [
                dict(
                    label="Price + Both MAs",
                    method="update",
                    args=[{"visible": [True, True, True, True]}]
                ),
                dict(
                    label="Price Only",
                    method="update",
                    args=[{"visible": [True, False, False, False]}]
                ),
                dict(
                    label="Price + MA_50",
                    method="update",
                    args=[{"visible": [True, True, False, False]}]
                ),
                dict(
                    label="Price + MA_200",
                    method="update",
                    args=[{"visible": [True, False, True, False]}]
                ),
                dict(
                    label="MAs Only",
                    method="update",
                    args=[{"visible": [False, True, True, True]}]
                ),
            ]
            
            fig_golden.update_layout(
                updatemenus=[
                    dict(
                        type="dropdown",
                        direction="down",
                        buttons=golden_buttons,
                        pad={"r": 10, "t": 10},
                        showactive=True,
                        x=0.02,
                        xanchor="left",
                        y=1.02,
                        yanchor="bottom",
                        bgcolor='rgba(0,0,0,0.7)',
                        bordercolor='white',
                        borderwidth=1,
                        font=dict(color='white')
                    ),
                ]
            )
            
            
            fig_golden.update_xaxes(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ]),
                    bgcolor='rgba(0,0,0,0.7)',
                    activecolor='rgba(0,150,255,0.7)',
                    bordercolor='white',
                    borderwidth=1,
                    font=dict(color='white'),
                    x=0.75,
                    xanchor="left",
                    y=0.99,
                    yanchor="bottom"
                )
            )
            
            fig_golden.show()
            print("\n✅ Golden Cross chart created")
        else:
            print("⚠️ No Golden Cross signals found to plot")
        
        
        if len(death_cross_dates) > 0:
            fig_death = go.Figure()
            
            
            fig_death.add_trace(go.Scatter(
                x=cross_data.index,
                y=cross_data['Price'],
                mode='lines',
                name='Price',
                line=dict(color='#00BFFF', width=2)
            ))
            
            
            fig_death.add_trace(go.Scatter(
                x=cross_data.index,
                y=cross_data['MA_50'],
                mode='lines',
                name='MA_50',
                line=dict(color='#7CFC00', width=2)  
            ))
            
            
            fig_death.add_trace(go.Scatter(
                x=cross_data.index,
                y=cross_data['MA_200'],
                mode='lines',
                name='MA_200',
                line=dict(color='#FFA500', width=2)  
            ))
            
            
            death_prices = cross_data.loc[death_cross_dates, 'Price']
            fig_death.add_trace(go.Scatter(
                x=death_cross_dates,
                y=death_prices * 1.02,  
                mode='markers',
                name='Death Cross',
                marker=dict(
                    symbol='triangle-down',
                    size=12,
                    color='#FF0000',
                    line=dict(width=2, color='white')
                ),
                hovertemplate='<b>Death Cross</b><br>Date: %{x|%Y-%m-%d}<br>Price: %{y:.2f}<extra></extra>'
            ))
            
            fig_death.update_layout(
                title=f'Death Cross Signals (MA_50 crosses below MA_200) - {len(death_cross_dates)} signals',
                plot_bgcolor='rgb(40,40,40)',
                paper_bgcolor='rgb(40,40,40)',
                font=dict(color='white'),
                xaxis=dict(
                    rangeslider=dict(visible=True),
                    type='date',
                    title='Date',
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                yaxis=dict(
                    title='Price',
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                hovermode='x unified',
                showlegend=True,
                height=600
            )
            
            
            death_buttons = [
                dict(
                    label="Price + Both MAs",
                    method="update",
                    args=[{"visible": [True, True, True, True]}]
                ),
                dict(
                    label="Price Only",
                    method="update",
                    args=[{"visible": [True, False, False, False]}]
                ),
                dict(
                    label="Price + MA_50",
                    method="update",
                    args=[{"visible": [True, True, False, False]}]
                ),
                dict(
                    label="Price + MA_200",
                    method="update",
                    args=[{"visible": [True, False, True, False]}]
                ),
                dict(
                    label="MAs Only",
                    method="update",
                    args=[{"visible": [False, True, True, True]}]
                ),
            ]
            
            fig_death.update_layout(
                updatemenus=[
                    dict(
                        type="dropdown",
                        direction="down",
                        buttons=death_buttons,
                        pad={"r": 10, "t": 10},
                        showactive=True,
                        x=0.02,
                        xanchor="left",
                        y=1.02,
                        yanchor="bottom",
                        bgcolor='rgba(0,0,0,0.7)',
                        bordercolor='white',
                        borderwidth=1,
                        font=dict(color='white')
                    ),
                ]
            )
            
            
            fig_death.update_xaxes(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ]),
                    bgcolor='rgba(0,0,0,0.7)',
                    activecolor='rgba(0,150,255,0.7)',
                    bordercolor='white',
                    borderwidth=1,
                    font=dict(color='white'),
                    x=0.75,
                    xanchor="left",
                    y=0.99,
                    yanchor="bottom"
                )
            )
            
            fig_death.show()
            print("✅ Death Cross chart created")
        else:
            print("⚠️ No Death Cross signals found to plot")
        
        
        if len(golden_cross_dates) > 0 or len(death_cross_dates) > 0:
            print("\n" + "="*50)
            print("CREATING COMBINED CROSSOVER CHART")
            print("="*50)
            
            fig_combined = go.Figure()
            
            
            fig_combined.add_trace(go.Scatter(
                x=cross_data.index,
                y=cross_data['Price'],
                mode='lines',
                name='Price',
                line=dict(color='#FFFFFF', width=1.5),
                opacity=0.7
            ))
            
            
            fig_combined.add_trace(go.Scatter(
                x=cross_data.index,
                y=cross_data['MA_50'],
                mode='lines',
                name='MA_50 (Short-term)',
                line=dict(color='#7CFC00', width=2)
            ))
            
            
            fig_combined.add_trace(go.Scatter(
                x=cross_data.index,
                y=cross_data['MA_200'],
                mode='lines',
                name='MA_200 (Long-term)',
                line=dict(color='#FFA500', width=2)
            ))
            
            
            if len(golden_cross_dates) > 0:
                golden_prices = cross_data.loc[golden_cross_dates, 'Price']
                fig_combined.add_trace(go.Scatter(
                    x=golden_cross_dates,
                    y=golden_prices * 0.98,
                    mode='markers',
                    name='Golden Cross',
                    marker=dict(
                        symbol='triangle-up',
                        size=10,
                        color='#00FF00',
                        line=dict(width=1, color='white')
                    ),
                    hovertemplate='<b>Golden Cross</b><br>Date: %{x|%Y-%m-%d}<br>Price: %{y:.2f}<extra></extra>'
                ))
            
    
            if len(death_cross_dates) > 0:
                death_prices = cross_data.loc[death_cross_dates, 'Price']
                fig_combined.add_trace(go.Scatter(
                    x=death_cross_dates,
                    y=death_prices * 1.02,
                    mode='markers',
                    name='Death Cross',
                    marker=dict(
                        symbol='triangle-down',
                        size=10,
                        color='#FF0000',
                        line=dict(width=1, color='white')
                    ),
                    hovertemplate='<b>Death Cross</b><br>Date: %{x|%Y-%m-%d}<br>Price: %{y:.2f}<extra></extra>'
                ))
            
            
            cross_data['MA50_above_MA200'] = cross_data['MA_50'] > cross_data['MA_200']
            
            
            above_periods = []
            current_start = None
            
            for i in range(len(cross_data)):
                if cross_data['MA50_above_MA200'].iloc[i]:
                    if current_start is None:
                        current_start = cross_data.index[i]
                else:
                    if current_start is not None:
                        above_periods.append((current_start, cross_data.index[i]))
                        current_start = None
            
            
            if current_start is not None:
                above_periods.append((current_start, cross_data.index[-1]))
            
            
            for start_date, end_date in above_periods:
                fig_combined.add_vrect(
                    x0=start_date, x1=end_date,
                    fillcolor="rgba(0, 255, 0, 0.1)",
                    layer="below", line_width=0,
                    annotation_text="Golden Zone",
                    annotation_position="top left",
                    annotation_font_size=10,
                    annotation_font_color="green"
                )
            
            fig_combined.update_layout(
                title=f'Combined Crossover Analysis ({len(golden_cross_dates)} Golden, {len(death_cross_dates)} Death)',
                plot_bgcolor='rgb(40,40,40)',
                paper_bgcolor='rgb(40,40,40)',
                font=dict(color='white'),
                xaxis=dict(
                    rangeslider=dict(visible=True),
                    type='date',
                    title='Date',
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                yaxis=dict(
                    title='Price',
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                hovermode='x unified',
                showlegend=True,
                height=600,
                annotations=[
                    dict(
                        x=0.02, y=1.08,
                        xref="paper", yref="paper",
                        text="🎯 <b>Golden Cross</b>: MA_50 crosses above MA_200 (Bullish)",
                        showarrow=False,
                        font=dict(size=12, color="green"),
                        align="left"
                    ),
                    dict(
                        x=0.02, y=1.04,
                        xref="paper", yref="paper",
                        text="💀 <b>Death Cross</b>: MA_50 crosses below MA_200 (Bearish)",
                        showarrow=False,
                        font=dict(size=12, color="red"),
                        align="left"
                    )
                ]
            )
            
            
            combined_buttons = [
                dict(
                    label="All Signals",
                    method="update",
                    args=[{"visible": [True, True, True, True, True]}]
                ),
                dict(
                    label="Price + MAs Only",
                    method="update",
                    args=[{"visible": [True, True, True, False, False]}]
                ),
                dict(
                    label="Signals Only",
                    method="update",
                    args=[{"visible": [False, False, False, True, True]}]
                ),
                dict(
                    label="Golden Cross Only",
                    method="update",
                    args=[{"visible": [True, True, True, True, False]}]
                ),
                dict(
                    label="Death Cross Only",
                    method="update",
                    args=[{"visible": [True, True, True, False, True]}]
                ),
            ]
            
            fig_combined.update_layout(
                updatemenus=[
                    dict(
                        type="dropdown",
                        direction="down",
                        buttons=combined_buttons,
                        pad={"r": 10, "t": 10},
                        showactive=True,
                        x=0.02,
                        xanchor="left",
                        y=1.12,  
                        yanchor="bottom",
                        bgcolor='rgba(0,0,0,0.7)',
                        bordercolor='white',
                        borderwidth=1,
                        font=dict(color='white')
                    ),
                ]
            )
            
            
            fig_combined.update_xaxes(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ]),
                    bgcolor='rgba(0,0,0,0.7)',
                    activecolor='rgba(0,150,255,0.7)',
                    bordercolor='white',
                    borderwidth=1,
                    font=dict(color='white'),
                    x=0.75,
                    xanchor="left",
                    y=0.99,
                    yanchor="bottom"
                )
            )
            
            fig_combined.show()
            print("✅ Combined Crossover chart created")
            
            
            if len(golden_cross_dates) > 0 and len(death_cross_dates) > 0:
                print("\n" + "="*50)
                print("CROSSOVER PERFORMANCE ANALYSIS")
                print("="*50)
                
                
                performance_results = []
                
                for signal_date, signal_type in [(d, 'Golden') for d in golden_cross_dates] + [(d, 'Death') for d in death_cross_dates]:
                    
                    later_signals = [d for d in golden_cross_dates if d > signal_date] + [d for d in death_cross_dates if d > signal_date]
                    
                    if later_signals:
                        end_date = min(later_signals)
                        period_data = cross_data.loc[signal_date:end_date]
                        
                        if len(period_data) > 1:
                            start_price = period_data['Price'].iloc[0]
                            end_price = period_data['Price'].iloc[-1]
                            price_change = ((end_price - start_price) / start_price) * 100
                            
                            performance_results.append({
                                'Signal Date': signal_date,
                                'Signal Type': signal_type,
                                'Start Price': start_price,
                                'End Price': end_price,
                                'Price Change %': price_change,
                                'Duration (days)': len(period_data)
                            })
                
                if performance_results:
                    perf_df = pd.DataFrame(performance_results)
                    
                    print("\n📊 Performance Summary:")
                    print("-" * 70)
                    
                    
                    golden_perf = perf_df[perf_df['Signal Type'] == 'Golden']
                    if len(golden_perf) > 0:
                        avg_golden_return = golden_perf['Price Change %'].mean()
                        avg_golden_duration = golden_perf['Duration (days)'].mean()
                        print(f"\nGolden Cross ({len(golden_perf)} periods):")
                        print(f"  Average Return: {avg_golden_return:.2f}%")
                        print(f"  Average Duration: {avg_golden_duration:.0f} days")
                        
                        
                        best_golden = golden_perf.loc[golden_perf['Price Change %'].idxmax()]
                        worst_golden = golden_perf.loc[golden_perf['Price Change %'].idxmin()]
                        print(f"  Best: {best_golden['Price Change %']:.2f}% from {best_golden['Signal Date'].date()}")
                        print(f"  Worst: {worst_golden['Price Change %']:.2f}% from {worst_golden['Signal Date'].date()}")
                    
                    
                    death_perf = perf_df[perf_df['Signal Type'] == 'Death']
                    if len(death_perf) > 0:
                        avg_death_return = death_perf['Price Change %'].mean()
                        avg_death_duration = death_perf['Duration (days)'].mean()
                        print(f"\nDeath Cross ({len(death_perf)} periods):")
                        print(f"  Average Return: {avg_death_return:.2f}%")
                        print(f"  Average Duration: {avg_death_duration:.0f} days")
                        
                        
                        best_death = death_perf.loc[death_perf['Price Change %'].idxmax()]
                        worst_death = death_perf.loc[death_perf['Price Change %'].idxmin()]
                        print(f"  Best: {best_death['Price Change %']:.2f}% from {best_death['Signal Date'].date()}")
                        print(f"  Worst: {worst_death['Price Change %']:.2f}% from {worst_death['Signal Date'].date()}")
                    
                    
                    if len(golden_perf) > 0 and len(death_perf) > 0:
                        print(f"\n📈 Comparison:")
                        print(f"  Golden Cross vs Death Cross return difference: {avg_golden_return - avg_death_return:.2f}%")
                        print(f"  Golden Cross success rate: {(golden_perf['Price Change %'] > 0).sum()}/{len(golden_perf)} ({(golden_perf['Price Change %'] > 0).sum()/len(golden_perf)*100:.1f}%)")
                        print(f"  Death Cross success rate: {(death_perf['Price Change %'] < 0).sum()}/{len(death_perf)} ({(death_perf['Price Change %'] < 0).sum()/len(death_perf)*100:.1f}%)")
                    
                    
                    perf_df.to_excel('crossover_performance_analysis.xlsx', index=False)
                    print(f"\n✅ Performance analysis saved to 'crossover_performance_analysis.xlsx'")
    else:
        print("❌ Cannot create Golden/Death Cross charts: MA_50 or MA_200 columns exist but have no valid data")
else:
    print("❌ Cannot create Golden/Death Cross charts: Missing MA_50 or MA_200 data in Excel file")


master.to_excel('multisheet_indicators.xlsx', engine='openpyxl')
print(f"\n✅ Merged data saved to 'multisheet_indicators.xlsx'")
print(f"Columns: {list(master.columns)}")
print(f"Shape: {master.shape}")
print(f"Date range: {master.index.min()} to {master.index.max()}")


print("\n" + "="*50)
print("COMPLETE TECHNICAL ANALYSIS DASHBOARD")
print("="*50)
print("📊 ALL INTERACTIVE CHARTS CREATED:")
charts_created = []

if 'EMA_20' in master.columns or 'EMA_50' in master.columns:
    charts_created.append("1. Price + EMAs")
if any(ma in master.columns for ma in ['MA_5', 'MA_10', 'MA_20', 'MA_50', 'MA_200']):
    charts_created.append("2. Price + Moving Averages")
if 'RSI' in master.columns:
    charts_created.append("3. RSI")
if any(col in master.columns for col in ['MACD', 'MACD_Signal', 'MACD_Hist']):
    charts_created.append("4. MACD")
if 'OBV' in master.columns:
    charts_created.append("5. OBV")
if 'MA_50' in master.columns and 'MA_200' in master.columns:
    charts_created.append("6-8. Golden Cross & Death Cross Analysis")

for chart in charts_created:
    print(chart)

print("\n✅ KEY FEATURES:")
print("✓ EMA data cleaned - starts at first valid value (no initial jump)")
print("✓ MA data cleaned - starts at first valid value (no initial jump)")
print("✓ Special handling for EMA stability (removes volatile initial values)")
print("✓ Price always shown in EMA and MA charts")
print("✓ Interactive toggle buttons for all charts")
print("✓ Time range controls (1m, 6m, YTD, 1y, All)")
print("✓ Golden Cross detection (MA_50 > MA_200)")
print("✓ Death Cross detection (MA_50 < MA_200)")
print("✓ Performance analysis for crossovers")
print("✓ Dark theme for all charts")
print("✓ Data saved to Excel for further analysis")
print("\n🖱️ HOW TO USE:")
print("✓ LEFT SIDE: Dropdown to toggle indicators")
print("✓ RIGHT SIDE: Time buttons to zoom (1m, 6m, YTD, 1y, All)")
print("✓ BOTTOM: Range slider for precise zooming")
print("✓ HOVER: Over lines for detailed values")
print("✓ CLICK: Legend items to manually show/hide")
print("✓ DOUBLE-CLICK: Reset zoom")
print("\n🎯 DASHBOARD READY FOR TECHNICAL ANALYSIS!")