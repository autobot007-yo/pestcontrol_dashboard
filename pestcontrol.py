import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import altair as alt

# Page configuration
st.set_page_config(
    page_title="BharatPest Control Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🐛"
)

# Custom CSS for COVID-19 dashboard style
st.markdown("""
<style>
    /* Global dark theme */
    .main {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: transparent;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main header */
    .main-header {
        text-align: center;
        color: white;
        font-size: 2.5rem;
        font-weight: 300;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .sub-header {
        text-align: center;
        color: #ffa726;
        font-size: 1.2rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    .last-updated {
        text-align: right;
        color: #ffa726;
        font-size: 0.9rem;
        margin-bottom: 2rem;
    }
    
    /* KPI Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 2rem 1rem;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
        height: 140px;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    }
    
    .metric-title {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 0.5rem;
        font-weight: 400;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0.5rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .metric-change {
        font-size: 0.85rem;
        margin-top: 0.5rem;
        opacity: 0.8;
    }
    
    /* Different colors for metrics */
    .metric-total { color: #ffb74d; }
    .metric-revenue { color: #81c784; }
    .metric-pending { color: #f06292; }
    .metric-completed { color: #64b5f6; }
    
    /* Chart containers */
    .chart-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .chart-title {
        color: white;
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Form styling */
    .stSelectbox label, .stTextInput label, .stTextArea label, 
    .stNumberInput label, .stDateInput label, .stCheckbox label {
        color: white !important;
        font-weight: 500;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    /* Section headers */
    .section-header {
        color: white;
        font-size: 1.3rem;
        font-weight: 500;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        color: white;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: rgba(76, 175, 80, 0.2);
        border-left: 4px solid #4caf50;
    }
    
    .stError {
        background: rgba(244, 67, 54, 0.2);
        border-left: 4px solid #f44336;
    }
</style>
""", unsafe_allow_html=True)

# Database setup
def init_database():
    conn = sqlite3.connect('pestcontrol.db', check_same_thread=False)
    c = conn.cursor()
    
    # Create the customers table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            service TEXT,
            visit_date TEXT,
            amount REAL,
            paid INTEGER DEFAULT 0,
            payment_method TEXT,
            service_status TEXT DEFAULT 'Ongoing',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Update old "Finished" status to "Completed" for consistency
    try:
        c.execute("UPDATE customers SET service_status = 'Completed' WHERE service_status = 'Finished'")
        conn.commit()
    except:
        pass  # Ignore errors if table doesn't exist or no records to update
    
    return conn, c

# Initialize database connection
conn, c = init_database()

# Main header
st.markdown('''
<div class="main-header">BharatPest Control</div>
<div class="sub-header">Business Performance Dashboard</div>
<div class="last-updated">Last Updated: {} 00:01 (IST)</div>
'''.format(datetime.now().strftime("%B %d, %Y")), unsafe_allow_html=True)

# Sidebar for adding new records
with st.sidebar:
    st.markdown('<div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin-bottom: 1rem; text-align: center; color: white; font-weight: 600;">➕ Add New Service Record</div>', unsafe_allow_html=True)

    with st.form("add_form"):
        st.markdown("**Customer Information**")
        name = st.text_input("Customer Name", placeholder="Enter customer name")
        phone = st.text_input("Phone", placeholder="+91 XXXXX XXXXX")
        address = st.text_area("Address", placeholder="Enter full address")
        
        st.markdown("**Service Details**")
        service = st.selectbox("Service Type", [
            "General Pest Control", 
            "Termite Treatment", 
            "Rodent Control", 
            "Mosquito Control", 
            "Cockroach Treatment",
            "Ant Control",
            "Other"
        ])
        visit_date = st.date_input("Visit Date", value=datetime.today())
        amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0, format="%.2f")
        
        st.markdown("**Payment Information**")
        paid = st.checkbox("Payment Received")
        payment_method = st.selectbox("Payment Method", ["Cash", "UPI", "Bank Transfer", "Credit Card", "Pending"])
        service_status = st.selectbox("Service Status", ["Ongoing", "Completed", "Cancelled", "Scheduled"])
        
        submit = st.form_submit_button("💾 Save Record", use_container_width=True)

        if submit:
            if name.strip():
                try:
                    c.execute('''
                        INSERT INTO customers (name, phone, address, service, visit_date, amount, paid, payment_method, service_status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        name.strip(), phone.strip(), address.strip(), service,
                        visit_date.strftime("%Y-%m-%d"),
                        amount, int(paid), payment_method, service_status
                    ))
                    conn.commit()
                    st.success("✅ Record saved successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error saving record: {str(e)}")
            else:
                st.error("❌ Please enter customer name")

# Load data
def load_data():
    try:
        # First check if table exists and has data
        c.execute("SELECT COUNT(*) FROM customers")
        count = c.fetchone()[0]
        
        if count == 0:
            # Return empty DataFrame with correct columns
            return pd.DataFrame(columns=[
                'id', 'name', 'phone', 'address', 'service', 'visit_date', 
                'amount', 'paid', 'payment_method', 'service_status', 'created_at'
            ])
        
        # Load data if table has records
        df = pd.read_sql_query("SELECT * FROM customers ORDER BY id DESC", conn)
        if not df.empty:
            df["visit_date"] = pd.to_datetime(df["visit_date"], errors='coerce')
            df["month"] = df["visit_date"].dt.month
            df["year"] = df["visit_date"].dt.year
            df["day_name"] = df["visit_date"].dt.day_name()
        return df
    except sqlite3.OperationalError as e:
        if "no such table" in str(e).lower():
            st.error("Database table not found. Please restart the application.")
            st.stop()
        else:
            st.error(f"Database error: {str(e)}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.markdown("""
    <div style='text-align: center; padding: 3rem; color: rgba(255,255,255,0.8);'>
        <h2>📊 No data available yet</h2>
        <p>Add your first customer record using the sidebar to get started!</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Calculate metrics
total_contracts = len(df)
total_revenue = df['amount'].sum()
total_paid = df.loc[df['paid'] == 1, 'amount'].sum()
total_pending = df.loc[df['paid'] == 0, 'amount'].sum()
# Handle both "Completed" and "Finished" status
completed_count = len(df[(df['service_status'] == 'Completed') | (df['service_status'] == 'Finished')])

# Calculate daily changes (mock data for demo)
daily_change_contracts = 15
daily_change_revenue = 2500
daily_change_pending = -800
daily_change_completed = 8

# Key Performance Indicators
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Contracts</div>
        <div class="metric-value metric-total">{total_contracts:,}</div>
        <div class="metric-change">new: +{daily_change_contracts} (+2.1%)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Revenue</div>
        <div class="metric-value metric-revenue">₹{total_revenue:,.0f}</div>
        <div class="metric-change">new: +₹{daily_change_revenue:,} (+1.8%)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Pending Payments</div>
        <div class="metric-value metric-pending">₹{total_pending:,.0f}</div>
        <div class="metric-change">new: ₹{daily_change_pending:,} (-2.3%)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Completed Jobs</div>
        <div class="metric-value metric-completed">{completed_count:,}</div>
        <div class="metric-change">new: +{daily_change_completed} (+3.2%)</div>
    </div>
    """, unsafe_allow_html=True)

# Location selector (similar to COVID dashboard)
st.markdown('<div class="section-header">Select Location:</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 3])
with col1:
    locations = ['All Locations'] + list(df['address'].str.split(',').str[-1].str.strip().unique())
    selected_location = st.selectbox("", locations, key="location_filter")

# Filter data by location if not "All Locations"
if selected_location != 'All Locations':
    df_filtered = df[df['address'].str.contains(selected_location, case=False, na=False)]
else:
    df_filtered = df.copy()

# Charts section
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Service Distribution</div>', unsafe_allow_html=True)
    
    # Service distribution donut chart
    service_counts = df_filtered['service'].value_counts()
    
    fig_donut = go.Figure(data=[go.Pie(
        labels=service_counts.index,
        values=service_counts.values,
        hole=0.6,
        marker=dict(
            colors=['#ffb74d', '#f06292', '#64b5f6', '#81c784', '#ba68c8', '#4db6ac', '#ff8a65'],
            line=dict(color='rgba(255,255,255,0.8)', width=2)
        ),
        textfont=dict(color='white', size=12),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    # Add center text
    fig_donut.add_annotation(
        text=f"<b>Active</b><br>{len(df_filtered[df_filtered['service_status'] != 'Cancelled']):,}",
        x=0.5, y=0.5,
        font_size=16,
        font_color='white',
        showarrow=False
    )
    
    fig_donut.update_layout(
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05,
            font=dict(color='white', size=10)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=350,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig_donut, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Last 30 Days Performance</div>', unsafe_allow_html=True)
    
    # Last 30 days performance chart
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_data = df_filtered[df_filtered['visit_date'] >= thirty_days_ago]
    
    if not recent_data.empty:
        daily_stats = recent_data.groupby(recent_data['visit_date'].dt.date).agg({
            'id': 'count',
            'amount': 'sum'
        }).reset_index()
        daily_stats.columns = ['Date', 'Contracts', 'Revenue']
        
        # Calculate rolling average
        daily_stats['Rolling_Avg'] = daily_stats['Contracts'].rolling(window=7, min_periods=1).mean()
        
        fig_trend = go.Figure()
        
        # Add bar chart for daily contracts
        fig_trend.add_trace(go.Bar(
            x=daily_stats['Date'],
            y=daily_stats['Contracts'],
            name='Daily Confirmed',
            marker_color='#ffb74d',
            opacity=0.8
        ))
        
        # Add rolling average line
        fig_trend.add_trace(go.Scatter(
            x=daily_stats['Date'],
            y=daily_stats['Rolling_Avg'],
            mode='lines',
            name='Rolling average of the last seven days',
            line=dict(color='#f06292', width=3),
            yaxis='y'
        ))
        
        fig_trend.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.1,
                xanchor="center",
                x=0.5,
                font=dict(color='white', size=10)
            ),
            xaxis=dict(
                title='Date',
                color='white',
                gridcolor='rgba(255,255,255,0.1)'
            ),
            yaxis=dict(
                title='Number of Contracts',
                color='white',
                gridcolor='rgba(255,255,255,0.1)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=350,
            margin=dict(l=20, r=20, t=20, b=60)
        )
    else:
        # Empty chart placeholder
        fig_trend = go.Figure()
        fig_trend.add_annotation(
            text="No data for the last 30 days",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            font_size=16, font_color='white',
            showarrow=False
        )
        fig_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=350
        )
    
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# New section for today's summary
st.markdown('<div class="section-header">New Records : {}</div>'.format(datetime.now().strftime("%B %d, %Y")), unsafe_allow_html=True)

today = datetime.now().date()
today_data = df[df['visit_date'].dt.date == today]

col1, col2, col3, col4 = st.columns(4)

with col1:
    new_confirmed = len(today_data)
    st.markdown(f"""
    <div style="background: rgba(255, 183, 77, 0.2); padding: 1rem; border-radius: 10px; text-align: center;">
        <div style="color: #ffb74d; font-size: 1.8rem; font-weight: 700;">{new_confirmed}</div>
        <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">▲ 4,432</div>
        <div style="color: white; font-size: 0.85rem; margin-top: 0.5rem;">New Confirmed</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    new_revenue = today_data['amount'].sum() if not today_data.empty else 0
    st.markdown(f"""
    <div style="background: rgba(129, 199, 132, 0.2); padding: 1rem; border-radius: 10px; text-align: center;">
        <div style="color: #81c784; font-size: 1.8rem; font-weight: 700;">₹{new_revenue:,.0f}</div>
        <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">▼ -4</div>
        <div style="color: white; font-size: 0.85rem; margin-top: 0.5rem;">New Revenue</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    new_completed = len(today_data[(today_data['service_status'] == 'Completed') | (today_data['service_status'] == 'Finished')])
    st.markdown(f"""
    <div style="background: rgba(100, 181, 246, 0.2); padding: 1rem; border-radius: 10px; text-align: center;">
        <div style="color: #64b5f6; font-size: 1.8rem; font-weight: 700;">{new_completed}</div>
        <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">▼ -17</div>
        <div style="color: white; font-size: 0.85rem; margin-top: 0.5rem;">New Completed</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    new_active = len(today_data[today_data['service_status'] == 'Ongoing'])
    st.markdown(f"""
    <div style="background: rgba(240, 98, 146, 0.2); padding: 1rem; border-radius: 10px; text-align: center;">
        <div style="color: #f06292; font-size: 1.8rem; font-weight: 700;">{new_active}</div>
        <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">▲ 4,453</div>
        <div style="color: white; font-size: 0.85rem; margin-top: 0.5rem;">New Active</div>
    </div>
    """, unsafe_allow_html=True)

# Customer Records Management
st.markdown('<div class="section-header">📋 Customer Records Management</div>', unsafe_allow_html=True)

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    status_filter = st.selectbox("Filter by Status", ["All"] + list(df['service_status'].unique()))

with col2:
    payment_filter = st.selectbox("Filter by Payment", ["All", "Paid", "Unpaid"])

with col3:
    service_filter = st.selectbox("Filter by Service", ["All"] + list(df['service'].unique()))

# Apply filters
filtered_records = df.copy()

if status_filter != "All":
    filtered_records = filtered_records[filtered_records['service_status'] == status_filter]

if payment_filter == "Paid":
    filtered_records = filtered_records[filtered_records['paid'] == 1]
elif payment_filter == "Unpaid":
    filtered_records = filtered_records[filtered_records['paid'] == 0]

if service_filter != "All":
    filtered_records = filtered_records[filtered_records['service'] == service_filter]

# Display filtered records
if not filtered_records.empty:
    st.markdown(f"<div style='color: rgba(255,255,255,0.8); margin: 1rem 0;'>Showing {len(filtered_records)} of {len(df)} records</div>", unsafe_allow_html=True)
    
    for idx, row in filtered_records.head(10).iterrows():  # Limit to 10 for performance
        with st.expander(f"🏠 {row['name']} • {row['phone']} • ₹{row['amount']:,.0f} • {row['service_status']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                visit_date_str = row['visit_date'].strftime('%Y-%m-%d') if pd.notnull(row['visit_date']) else 'N/A'
                payment_status = "✅ Paid" if row['paid'] else "❌ Unpaid"
                
                st.markdown(f"""
                **🛡️ Service:** {row['service']}  
                **📅 Visit Date:** {visit_date_str}  
                **📍 Address:** {row['address'] or 'Not provided'}  
                **💳 Payment:** {payment_status} via {row['payment_method']}  
                **📊 Status:** `{row['service_status']}`  
                **💰 Amount:** ₹{row['amount']:,.2f}
                """)
            
            with col2:
                # Status update - handle both old and new status values
                status_options = ["Ongoing", "Completed", "Cancelled", "Scheduled"]
                
                # Map old status values to new ones
                status_mapping = {
                    "Finished": "Completed",
                    "Ongoing": "Ongoing", 
                    "Completed": "Completed",
                    "Cancelled": "Cancelled",
                    "Scheduled": "Scheduled"
                }
                
                current_status = status_mapping.get(row['service_status'], row['service_status'])
                
                # Find the index, default to 0 if not found
                try:
                    status_index = status_options.index(current_status)
                except ValueError:
                    status_index = 0
                
                new_status = st.selectbox(
                    "Update Status",
                    status_options,
                    index=status_index,
                    key=f"status_{row['id']}"
                )
                
                # Payment update
                new_payment = st.checkbox(
                    "Mark as Paid",
                    value=bool(row['paid']),
                    key=f"payment_{row['id']}"
                )
                
                if st.button("Update", key=f"update_{row['id']}", use_container_width=True):
                    try:
                        c.execute("""
                            UPDATE customers 
                            SET service_status = ?, paid = ?
                            WHERE id = ?
                        """, (new_status, int(new_payment), row['id']))
                        conn.commit()
                        st.success(f"✅ Updated {row['name']}'s record")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error updating record: {str(e)}")
    
    if len(filtered_records) > 10:
        st.markdown(f"<div style='color: rgba(255,255,255,0.6); text-align: center; margin: 2rem 0;'>Showing first 10 records. Total: {len(filtered_records)} records match your filters.</div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='color: rgba(255,255,255,0.6); text-align: center; margin: 2rem 0;'>📊 No records match the selected filters.</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style='text-align: center; color: rgba(255,255,255,0.6); padding: 2rem; margin-top: 3rem; border-top: 1px solid rgba(255,255,255,0.2);'>
    <p>🐛 <strong>BharatPest Control Dashboard</strong> • Professional Business Management</p>
    <p>Track • Analyze • Optimize your pest control operations</p>
</div>
""", unsafe_allow_html=True)