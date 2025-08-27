import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Initialize session state FIRST (before anything else)
if 'customers_df' not in st.session_state:
    st.session_state.customers_df = pd.DataFrame()

if 'show_add_form' not in st.session_state:
    st.session_state.show_add_form = False

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

# Sample data function
@st.cache_data
def load_sample_data():
    """Load sample data for demonstration"""
    sample_data = []
    services = ["General Pest Control", "Termite Treatment", "Rodent Control", "Mosquito Control", "Cockroach Treatment"]
    addresses = ["Andheri, Mumbai", "Bandra, Mumbai", "Thane", "Pune", "Nashik", "Aurangabad"]
    
    for i in range(1, 26):  # 25 sample records
        sample_data.append({
            'id': i,
            'name': f'Customer {i}',
            'phone': f'+91 98765 {43210 + i}',
            'address': f'Plot {i}, {addresses[i % len(addresses)]}',
            'service': services[i % len(services)],
            'visit_date': datetime.now() - timedelta(days=25-i),
            'amount': 500 + (i * 200),
            'paid': 1 if i % 3 != 0 else 0,
            'payment_method': 'UPI' if i % 2 == 0 else 'Cash',
            'service_status': 'Completed' if i % 4 == 0 else 'Ongoing',
            'created_at': datetime.now() - timedelta(days=25-i)
        })
    return pd.DataFrame(sample_data)

# Initialize data if empty
if st.session_state.customers_df.empty:
    st.session_state.customers_df = load_sample_data()

def add_customer(customer_data):
    """Add new customer to session state"""
    new_id = st.session_state.customers_df['id'].max() + 1 if not st.session_state.customers_df.empty else 1
    customer_data['id'] = new_id
    customer_data['created_at'] = datetime.now()
    
    # Convert to DataFrame and append
    new_row = pd.DataFrame([customer_data])
    st.session_state.customers_df = pd.concat([st.session_state.customers_df, new_row], ignore_index=True)

def update_customer(customer_id, updates):
    """Update customer record in session state"""
    idx = st.session_state.customers_df[st.session_state.customers_df['id'] == customer_id].index
    if not idx.empty:
        for key, value in updates.items():
            st.session_state.customers_df.at[idx[0], key] = value

# Main header
st.markdown('''
<div class="main-header">BharatPest Control</div>
<div class="sub-header">Business Performance Dashboard</div>
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
                    customer_data = {
                        'name': name.strip(),
                        'phone': phone.strip(),
                        'address': address.strip(),
                        'service': service,
                        'visit_date': pd.to_datetime(visit_date),
                        'amount': amount,
                        'paid': 1 if paid else 0,
                        'payment_method': payment_method,
                        'service_status': service_status
                    }
                    add_customer(customer_data)
                    st.success("✅ Record saved successfully!")
                    st.balloons()  # Celebration effect
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error saving record: {str(e)}")
            else:
                st.error("❌ Please enter customer name")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Load data
df = st.session_state.customers_df.copy()

# Ensure visit_date is datetime
if not df.empty:
    df["visit_date"] = pd.to_datetime(df["visit_date"], errors='coerce')
    df["month"] = df["visit_date"].dt.month
    df["year"] = df["visit_date"].dt.year
    df["day_name"] = df["visit_date"].dt.day_name()

if df.empty:
    st.markdown("""
    <div style='text-align: center; padding: 3rem; color: rgba(255,255,255,0.8);'>
        <h2>📊 Welcome to BharatPest Control Dashboard</h2>
        <p>Click "Add New Customer" above to get started!</p>
        <p><em>Currently showing sample data for demonstration</em></p>
    </div>
    """, unsafe_allow_html=True)

# Calculate metrics
total_contracts = len(df)
total_revenue = df['amount'].sum()
total_paid = df.loc[df['paid'] == 1, 'amount'].sum()
total_pending = df.loc[df['paid'] == 0, 'amount'].sum()
completed_count = len(df[df['service_status'] == 'Completed'])

# Calculate daily changes (mock data for demo)
daily_change_contracts = 15
daily_change_revenue = 2500
daily_change_pending = -800
daily_change_completed = 8

# Key Performance Indicators
st.markdown('<div class="section-header">📊 Business Overview</div>', unsafe_allow_html=True)

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

# Charts section
st.markdown('<div class="section-header">📈 Performance Analytics</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Service Distribution</div>', unsafe_allow_html=True)
    
    # Service distribution donut chart
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
    
    # Add center text
    fig_donut.add_annotation(
        text=f"<b>Active</b><br>{len(df[df['service_status'] != 'Cancelled']):,}",
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
    recent_data = df[df['visit_date'] >= thirty_days_ago]
    
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
            name='Rolling average (7 days)',
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

# Customer Records Management
st.markdown('<div class="section-header">📋 Customer Records Management</div>', unsafe_allow_html=True)

# Filters
col1, col2, col3, col4 = st.columns(4)

with col1:
    status_filter = st.selectbox("Filter by Status", ["All"] + list(df['service_status'].unique()))

with col2:
    payment_filter = st.selectbox("Filter by Payment", ["All", "Paid", "Unpaid"])

with col3:
    service_filter = st.selectbox("Filter by Service", ["All"] + list(df['service'].unique()))

with col4:
    # Export functionality
    if st.button("📊 Export Data", use_container_width=True):
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Download CSV",
            data=csv,
            file_name=f'pest_control_data_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
            use_container_width=True
        )

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
                # Status update
                status_options = ["Ongoing", "Completed", "Cancelled", "Scheduled"]
                
                # Find the index, default to 0 if not found
                try:
                    status_index = status_options.index(row['service_status'])
                except ValueError:
                    status_index = 0  # Default to "Ongoing" if status not found
                
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
                
                if st.button("🔄 Update", key=f"update_{row['id']}", use_container_width=True):
                    try:
                        updates = {
                            'service_status': new_status,
                            'paid': 1 if new_payment else 0
                        }
                        update_customer(row['id'], updates)
                        st.success(f"✅ Updated {row['name']}'s record")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error updating record: {str(e)}")
    
    if len(filtered_records) > 10:
        st.markdown(f"<div style='color: rgba(255,255,255,0.6); text-align: center; margin: 2rem 0;'>Showing first 10 records. Total: {len(filtered_records)} records match your filters.</div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='color: rgba(255,255,255,0.6); text-align: center; margin: 2rem 0;'>📊 No records match the selected filters.</div>", unsafe_allow_html=True)

# Sidebar with quick actions
with st.sidebar:
    st.markdown('<div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin-bottom: 1rem; text-align: center; color: white; font-weight: 600;">📊 Quick Stats</div>', unsafe_allow_html=True)
    
    # Quick stats in sidebar
    if not df.empty:
        pending_payments = df[df['paid'] == 0]['amount'].sum()
        recent_customers = len(df[df['visit_date'] >= (datetime.now() - timedelta(days=7))])
        
        st.metric("💰 Pending Payments", f"₹{pending_payments:,.0f}")
        st.metric("📅 This Week's Customers", f"{recent_customers}")
        st.metric("🎯 Completion Rate", f"{(completed_count/total_contracts*100):.1f}%" if total_contracts > 0 else "0%")
    
    st.markdown("---")
    
    # Unpaid customers quick view
    st.markdown('<div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin-bottom: 1rem; text-align: center; color: white; font-weight: 600;">🔍 Unpaid Customers</div>', unsafe_allow_html=True)
    
    unpaid_customers = df[df['paid'] == 0]
    if not unpaid_customers.empty:
        st.write("**Top 5 Pending:**")
        for _, customer in unpaid_customers.nlargest(5, 'amount').iterrows():
            st.write(f"📞 {customer['name']}: ₹{customer['amount']:,.0f}")
    else:
        st.success("🎉 No pending payments!")

# Footer
st.markdown("""
<div style='text-align: center; color: rgba(255,255,255,0.6); padding: 2rem; margin-top: 3rem; border-top: 1px solid rgba(255,255,255,0.2);'>
    <p>🐛 <strong>BharatPest Control Dashboard</strong> • Professional Business Management</p>
    <p>Track • Analyze • Optimize your pest control operations</p>
    <p><em>Data persists during your session • Add your records to see live updates</em></p>
</div>
""", unsafe_allow_html=True)
