import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import shutil
import os

# Initialize session state FIRST
if 'show_add_form' not in st.session_state:
    st.session_state.show_add_form = False

if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = False

# Page configuration
st.set_page_config(
    page_title="BharatPest Control Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🐛"
)

# Database setup with demo data preservation
@st.cache_resource
def init_database_with_demo_data():
    """Initialize database, preserving demo data from repo"""
    
    # Check if we need to restore demo data
    demo_db_path = 'pestcontrol_demo.db'  # Your original DB renamed
    active_db_path = 'pestcontrol.db'
    
    # If active DB doesn't exist and demo DB does, copy it
    if not os.path.exists(active_db_path) and os.path.exists(demo_db_path):
        shutil.copy2(demo_db_path, active_db_path)
        st.toast("📊 Demo database loaded successfully!", icon="✅")
    
    # Connect to database
    conn = sqlite3.connect(active_db_path, check_same_thread=False)
    c = conn.cursor()
    
    # Create table if it doesn't exist
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
    
    # Update old status values for compatibility
    try:
        c.execute("UPDATE customers SET service_status = 'Completed' WHERE service_status = 'Finished'")
        conn.commit()
    except:
        pass
    
    return conn, c

# Initialize database
conn, c = init_database_with_demo_data()

# Custom CSS (same as before)
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
        margin-bottom: 1rem;
    }
    
    .demo-info {
        text-align: center;
        background: rgba(76, 175, 80, 0.2);
        color: #81c784;
        padding: 0.8rem;
        border-radius: 10px;
        font-size: 0.9rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(129, 199, 132, 0.3);
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
    
    /* Form styling */
    .stSelectbox label, .stTextInput label, .stTextArea label, 
    .stNumberInput label, .stDateInput label, .stCheckbox label {
        color: white !important;
        font-weight: 500;
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
    
    /* Add Customer Section */
    .add-customer-section {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Load data function
@st.cache_data
def load_data():
    """Load data from SQLite database"""
    try:
        df = pd.read_sql_query("SELECT * FROM customers ORDER BY id DESC", conn)
        if not df.empty:
            df["visit_date"] = pd.to_datetime(df["visit_date"], errors='coerce')
            df["month"] = df["visit_date"].dt.month
            df["year"] = df["visit_date"].dt.year
            df["day_name"] = df["visit_date"].dt.day_name()
        return df
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return pd.DataFrame()

# Main header
st.markdown('''
<div class="main-header">BharatPest Control</div>
<div class="sub-header">Business Performance Dashboard</div>
''', unsafe_allow_html=True)

# Demo info banner
st.markdown('''
<div class="demo-info">
    🎯 <strong>Live Demo Dashboard</strong> • Real business data included • Add new customers to test functionality
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div class="last-updated">Last Updated: {} 00:01 (IST)</div>
'''.format(datetime.now().strftime("%B %d, %Y")), unsafe_allow_html=True)

# Add/Hide Customer Form Toggle
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("➕ Add New Customer" if not st.session_state.show_add_form else "❌ Hide Form", 
                 use_container_width=True, type="primary"):
        st.session_state.show_add_form = not st.session_state.show_add_form

# Show Add Customer Form
if st.session_state.show_add_form:
    st.markdown('<div class="add-customer-section">', unsafe_allow_html=True)
    st.markdown("### ➕ Add New Service Record")
    
    with st.form("add_customer_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Customer Information**")
            name = st.text_input("Customer Name", placeholder="Enter customer name")
            phone = st.text_input("Phone", placeholder="+91 XXXXX XXXXX")
            address = st.text_area("Address", placeholder="Enter full address", height=80)
        
        with col2:
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
        
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("**Payment Information**")
            paid = st.checkbox("Payment Received")
            payment_method = st.selectbox("Payment Method", ["Cash", "UPI", "Bank Transfer", "Credit Card", "Pending"])
        
        with col4:
            st.markdown("**Service Status**")
            service_status = st.selectbox("Service Status", ["Ongoing", "Completed", "Cancelled", "Scheduled"])
        
        # Form buttons
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("💾 Save Record", use_container_width=True)
        with col_btn2:
            if st.form_submit_button("🔄 Reset Form", use_container_width=True):
                st.rerun()

        if submitted:
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
                    st.balloons()
                    load_data.clear()  # Clear cache to refresh data
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error saving record: {str(e)}")
            else:
                st.error("❌ Please enter customer name")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Load and display data
df = load_data()

# Rest of your dashboard code (KPIs, charts, customer records, etc.)
# [Include all the existing dashboard code from the previous version]

if df.empty:
    st.markdown("""
    <div style='text-align: center; padding: 3rem; color: rgba(255,255,255,0.8);'>
        <h2>📊 Welcome to BharatPest Control Dashboard</h2>
        <p>Click "Add New Customer" above to get started!</p>
        <p><em>Database is ready - your data will be saved during this session</em></p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Calculate metrics
total_contracts = len(df)
total_revenue = df['amount'].sum()
total_paid = df.loc[df['paid'] == 1, 'amount'].sum()
total_pending = df.loc[df['paid'] == 0, 'amount'].sum()
completed_count = len(df[df['service_status'] == 'Completed'])

# Key Performance Indicators
st.markdown('<div class="section-header">📊 Business Overview</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Contracts</div>
        <div class="metric-value metric-total">{total_contracts:,}</div>
        <div class="metric-change">Active business records</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Revenue</div>
        <div class="metric-value metric-revenue">₹{total_revenue:,.0f}</div>
        <div class="metric-change">Lifetime earnings</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Pending Payments</div>
        <div class="metric-value metric-pending">₹{total_pending:,.0f}</div>
        <div class="metric-change">Outstanding amount</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Completed Jobs</div>
        <div class="metric-value metric-completed">{completed_count:,}</div>
        <div class="metric-change">Successful services</div>
    </div>
    """, unsafe_allow_html=True)

# Charts section
st.markdown('<div class="section-header">📈 Performance Analytics</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Service Distribution</div>', unsafe_allow_html=True)
    
    service_counts = df['service'].value_counts()
    
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
    
    fig_donut.add_annotation(
        text=f"<b>Total</b><br>{len(df):,}",
        x=0.5, y=0.5,
        font_size=16,
        font_color='white',
        showarrow=False
    )
    
    fig_donut.update_layout(
        showlegend=True,
        legend=dict(font=dict(color='white', size=10)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=350,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig_donut, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Payment Status Overview</div>', unsafe_allow_html=True)
    
    payment_counts = df['paid'].value_counts()
    payment_labels = ['Paid' if x == 1 else 'Unpaid' for x in payment_counts.index]
    
    fig_payment = go.Figure(data=[go.Bar(
        x=payment_labels,
        y=payment_counts.values,
        marker_color=['#81c784', '#f06292'],
        text=payment_counts.values,
        textposition='auto',
        textfont=dict(color='white', size=14, family="Arial Black")
    )])
    
    fig_payment.update_layout(
        xaxis=dict(title='Payment Status', color='white'),
        yaxis=dict(title='Number of Customers', color='white'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=350,
        showlegend=False
    )
    
    st.plotly_chart(fig_payment, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Customer Records Management
st.markdown('<div class="section-header">📋 Recent Customer Records</div>', unsafe_allow_html=True)

# Show top 10 most recent records
recent_records = df.head(10)

if not recent_records.empty:
    for idx, row in recent_records.iterrows():
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
                st.info("👁️ **Demo Mode**\n\nRecord updates available in full version")

# Sidebar with stats
with st.sidebar:
    st.markdown('<div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin-bottom: 1rem; text-align: center; color: white; font-weight: 600;">📊 Quick Stats</div>', unsafe_allow_html=True)
    
    if not df.empty:
        pending_payments = df[df['paid'] == 0]['amount'].sum()
        recent_customers = len(df[df['visit_date'] >= (datetime.now() - timedelta(days=7))])
        
        st.metric("💰 Pending Payments", f"₹{pending_payments:,.0f}")
        st.metric("📅 This Week's Customers", f"{recent_customers}")
        st.metric("🎯 Completion Rate", f"{(completed_count/total_contracts*100):.1f}%" if total_contracts > 0 else "0%")
        
        # Export functionality
        if st.button("📊 Export Database", use_container_width=True):
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f'pest_control_backup_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                use_container_width=True
            )

# Footer
st.markdown("""
<div style='text-align: center; color: rgba(255,255,255,0.6); padding: 2rem; margin-top: 3rem; border-top: 1px solid rgba(255,255,255,0.2);'>
    <p>🐛 <strong>BharatPest Control Dashboard</strong> • Live Demo Version</p>
    <p>Your real business data • Professional analytics • Modern interface</p>
    <p><em>Ready for production deployment with persistent database solutions</em></p>
</div>
""", unsafe_allow_html=True)
