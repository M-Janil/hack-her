import streamlit as st
import pandas as pd
import difflib
from geopy.distance import geodesic

# --- CONFIGURATION ---
st.set_page_config(page_title="LowKey Deals", layout="wide", page_icon="✨")

# --- 1. THEME: MODERN & ACCESSIBLE ---
def apply_theme():
    st.markdown("""
        <style>
        /* Global Text & Label Colors */
        html, body, [data-testid="stHeader"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, span, .stRadio p {
            color: #000000 !important;
            font-weight: 500;
        }

        /* Set Background to White */
        .stApp {
            background-color: #FFFFFF;
        }

        /* Card Styling for "Life" */
        .deal-card {
            background-color: #F8F9FA;
            padding: 20px;
            border-radius: 12px;
            border-left: 5px solid #8B4513;
            margin-bottom: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        }

        /* Input Box Visibility */
        input {
            color: #000000 !important;
            background-color: #F0F2F6 !important;
            border: 2px solid #8B4513 !important;
        }

        /* Button Styling */
        div.stButton > button {
            background-color: #8B4513 !important;
            color: #FFFFFF !important;
            border-radius: 8px;
            font-weight: bold;
            transition: 0.3s;
        }
        
        div.stButton > button:hover {
            background-color: #A0522D !important;
            border: 1px solid #8B4513 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. DATA INITIALIZATION ---
def init_data():
    if 'items' not in st.session_state:
        # Default starting items
        st.session_state.items = {
            "Refrigerator": {"desc": "Double door, 250L", "price": 25000},
            "Washing Machine": {"desc": "Front load, 7kg", "price": 18000},
            "Microwave Oven": {"desc": "Convection, 20L", "price": 8500}
        }
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = ""

# --- 3. UI PAGES ---

def admin_page():
    st.title("📦 Inventory Manager")
    st.info("Upload a CSV file to add multiple items at once.")
    
    # CSV Uploader
    uploaded_file = st.file_uploader("Choose a CSV file (Columns: name, desc, price)", type="csv")
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            for _, row in df.iterrows():
                st.session_state.items[row['name']] = {
                    "desc": row['desc'], 
                    "price": row['price']
                }
            st.success(f"Successfully imported {len(df)} items!")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

    st.divider()
    st.subheader("Add Single Item")
    with st.form("manual_add"):
        name = st.text_input("Product Name")
        desc = st.text_area("Description")
        price = st.number_input("Price (₹)", min_value=0)
        if st.form_submit_button("Add to Catalog"):
            st.session_state.items[name] = {"desc": desc, "price": price}
            st.toast(f"Added {name}!")

def home_page():
    st.title("✨ LowKey Deals")
    st.markdown("### *Highkey savings on local appliances.*")
    
    # Safety check for the AttributeError you saw
    if 'items' not in st.session_state:
        init_data()

    # Search Logic
    search_input = st.text_input("🔍 Search for appliances...", placeholder="Type 'Fridge'...", key="main_search")
    
    if search_input:
        all_items = list(st.session_state.items.keys())
        suggestions = difflib.get_close_matches(search_input, all_items, n=3, cutoff=0.3)
        if suggestions:
            st.write("Did you mean:")
            cols = st.columns(len(suggestions))
            for i, sug in enumerate(suggestions):
                if cols[i].button(f"👉 {sug}", key=f"sug_{sug}"):
                    st.session_state.selected_item = sug
                    st.rerun()

    st.divider()
    
    if 'selected_item' in st.session_state:
        item_name = st.session_state.selected_item
        item = st.session_state.items[item_name]
        
        c1, c2 = st.columns(2)
        with c1:
            st.image("https://via.placeholder.com/400x300.png?text=Product+Image", use_container_width=True)
        with c2:
            st.subheader(item_name)
            st.write(item['desc'])
            st.metric("Price", f"₹{item['price']:,}")
            if st.button("Reserve Deal"):
                st.balloons()
            if st.button("Back to Browse"):
                del st.session_state.selected_item
                st.rerun()
    else:
        # Product Grid
        items = st.session_state.items
        cols = st.columns(3)
        for i, (name, info) in enumerate(items.items()):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="deal-card">
                    <h4>{name}</h4>
                    <p style="font-size: 0.9rem;">{info['desc']}</p>
                    <p style="font-weight: bold; font-size: 1.1rem;">₹{info['price']:,}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Details: {name}", key=f"btn_{name}"):
                    st.session_state.selected_item = name
                    st.rerun()

def login_page():
    st.title("Welcome to LowKey Deals")
    role = st.radio("Select Role", ["User", "Seller"], key="role_selection")
    user = st.text_input("Username")
    if st.button("Login"):
        if user:
            st.session_state.authenticated = True
            st.session_state.username = user
            st.session_state.role = role
            st.rerun()

# --- 4. EXECUTION FLOW ---
apply_theme()
init_data()

if not st.session_state.authenticated:
    login_page()
else:
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.username}")
        # Navigation based on Role
        if st.session_state.role == "Seller":
            nav = st.radio("Dashboard", ["View Store", "Manage Inventory"])
        else:
            nav = "View Store"
            
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()
            
    if nav == "Manage Inventory":
        admin_page()
    else:
        home_page()
