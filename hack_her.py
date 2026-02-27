import streamlit as st
import pandas as pd
import difflib
from geopy.distance import geodesic
from datetime import datetime
import streamlit.components.v1 as components
import calendar

# --- CONFIGURATION ---
st.set_page_config(page_title="LowKey Deals", layout="wide", page_icon="✨")

# --- 1. THEME: BROWN, BLACK, WHITE WITH LIVELINESS ---
def apply_theme():
    st.markdown("""
        <style>
        /* Global Text & Label Colors */
        html, body, [data-testid="stHeader"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, span, .stRadio p {
            color: #000000 !important;
            font-weight: 500;
        }
        .stApp { background-color: #FFFFFF; }
        /* Enhanced Card Styling with Hover Animation */
        .deal-card {
            background-color: #FFFFFF;
            padding: 20px;
            border-radius: 15px;
            border-top: 4px solid #8B4513;
            margin-bottom: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.3s ease-in-out, box-shadow 0.3s;
        }
        .deal-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.1);
        }
        .price-tag {
            color: #8B4513;
            font-size: 1.4rem;
            font-weight: bold;
        }
        /* Status Badge with Pulse Animation */
        .badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: bold;
            text-transform: uppercase;
            background-color: #FFE4B5;
            color: #8B4513;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        input {
            color: #000000 !important;
            background-color: #FFFFFF !important;
            border: 2px solid #8B4513 !important;
        }
        div.stButton > button {
            background-color: #8B4513 !important;
            color: #FFFFFF !important;
            border-radius: 20px;
            font-weight: bold;
            transition: 0.3s;
            width: 100%;
        }
        div.stButton > button:hover {
            background-color: #A0522D !important;
            transform: scale(1.05);
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. DATA INITIALIZATION ---
def init_data():
    if 'item_offers' not in st.session_state or not isinstance(st.session_state.item_offers, dict):
        st.session_state.item_offers = {
            "Refrigerator": [
                {
                    "store": "Appliance World",
                    "address": "123 Kochi St, Kerala",
                    "loc": (9.95, 76.29),
                    "price": 25000,
                    "sale_price": None,
                    "is_sale": False,
                    "desc": "Double door, 250L",
                    "reviews": [{"user": "user1", "rating": 4, "text": "Good product"}],
                    "open_hours": (9, 21),
                    "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                },
                {
                    "store": "Home Mart",
                    "address": "456 Ernakulam Rd, Kerala",
                    "loc": (9.93, 76.27),
                    "price": 26000,
                    "sale_price": 24000,
                    "is_sale": True,
                    "desc": "Double door, 260L",
                    "reviews": [],
                    "open_hours": (10, 22),
                    "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                }
            ],
            "Washing Machine": [
                {
                    "store": "Appliance World",
                    "address": "123 Kochi St, Kerala",
                    "loc": (9.95, 76.29),
                    "price": 18000,
                    "sale_price": None,
                    "is_sale": False,
                    "desc": "Front load, 7kg",
                    "reviews": [],
                    "open_hours": (9, 21),
                    "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                },
                {
                    "store": "Home Mart",
                    "address": "456 Ernakulam Rd, Kerala",
                    "loc": (9.93, 76.27),
                    "price": 17000,
                    "sale_price": None,
                    "is_sale": False,
                    "desc": "Front load, 6kg",
                    "reviews": [{"user": "user1", "rating": 5, "text": "Excellent"}],
                    "open_hours": (10, 22),
                    "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                }
            ]
        }
    if 'users' not in st.session_state:
        st.session_state.users = {"user1": "pass1"}
    if 'sellers' not in st.session_state:
        st.session_state.sellers = {
            "seller1": {
                "password": "pass1",
                "store_name": "Appliance World",
                "loc": (9.95, 76.29),
                "open_hours": (9, 21),
                "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                "address": "123 Kochi St, Kerala"
            },
            "seller2": {
                "password": "pass2",
                "store_name": "Home Mart",
                "loc": (9.93, 76.27),
                "open_hours": (10, 22),
                "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                "address": "456 Ernakulam Rd, Kerala"
            }
        }
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_location' not in st.session_state:
        st.session_state.user_location = (9.9312, 76.2673)  # Kochi, Kerala (default)

# --- AUTH PAGE - Improved look ---
def auth_page():
    apply_theme()

    # Additional styling for auth page
    st.markdown("""
        <style>
        .auth-wrapper {
            max-width: 520px;
            margin: 5rem auto;
            padding: 3rem 2.5rem;
            background: linear-gradient(135deg, #ffffff 0%, #fffaf5 100%);
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(139, 69, 19, 0.12);
            border: 1px solid #f0e4d9;
        }
        .auth-header {
            text-align: center;
            margin-bottom: 2.5rem;
        }
        .auth-header h1 {
            font-size: 3.2rem;
            color: #8B4513;
            margin: 0 0 0.8rem;
            font-weight: 700;
        }
        .auth-header p {
            color: #5c4033;
            font-size: 1.15rem;
            margin: 0;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            justify-content: center;
            background: transparent !important;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            color: #5c4033 !important;
            padding: 0.8rem 2rem !important;
            border-radius: 12px !important;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: #8B4513 !important;
            color: white !important;
        }
        input, textarea {
            border-radius: 12px !important;
            border: 2px solid #a0522d !important;
            padding: 0.8rem 1.2rem !important;
            background: #fffaf5 !important;
        }
        div.stButton > button {
            background: linear-gradient(90deg, #8B4513 0%, #a0522d 100%) !important;
            color: white !important;
            border-radius: 12px !important;
            padding: 0.9rem !important;
            font-weight: 600 !important;
            transition: all 0.3s;
            box-shadow: 0 4px 12px rgba(139,69,19,0.2) !important;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 24px rgba(139,69,19,0.3) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)

    st.markdown("""
        <div class="auth-header">
            <h1>LowKey Deals</h1>
            <p>Find the best local prices on appliances — right near you.</p>
        </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

    with tab_login:
        role = st.radio("Sign in as", ["User", "Seller"], horizontal=True)
        username = st.text_input("Username", placeholder="yourname")
        password = st.text_input("Password", type="password", placeholder="••••••••••")

        if st.button("Sign In", use_container_width=True):
            if username and password:
                if role == "User":
                    if username in st.session_state.users and st.session_state.users[username] == password:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.role = role
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                else:
                    if username in st.session_state.sellers and st.session_state.sellers[username]["password"] == password:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.role = role
                        st.session_state.store_info = st.session_state.sellers[username]
                        st.rerun()
                    else:
                        st.error("Invalid credentials for seller.")
            else:
                st.warning("Please fill in all fields.")

    with tab_signup:
        role = st.radio("Create account as", ["User", "Seller"], horizontal=True)
        username = st.text_input("Choose Username")
        password = st.text_input("Choose Password", type="password")

        store_name = address = lat = lon = open_from = open_to = open_days = None
        if role == "Seller":
            st.markdown("---")
            store_name = st.text_input("Store Name")
            address = st.text_input("Store Address")
            c1, c2 = st.columns(2)
            with c1:
                lat = st.number_input("Latitude", value=9.93, format="%.5f")
                open_from = st.number_input("Opening Hour (0-23)", 0, 23, 9)
            with c2:
                lon = st.number_input("Longitude", value=76.27, format="%.5f")
                open_to = st.number_input("Closing Hour (0-23)", 0, 23, 21)
            open_days = st.multiselect(
                "Open Days",
                list(calendar.day_name),
                default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            )

        if st.button("Create Account", use_container_width=True):
            if username and password:
                if role == "User":
                    if username in st.session_state.users:
                        st.error("Username already taken.")
                    else:
                        st.session_state.users[username] = password
                        st.success("Account created! Now sign in.")
                else:
                    if username in st.session_state.sellers:
                        st.error("Username already taken.")
                    elif not (store_name and address and open_days):
                        st.error("Please fill store details and select open days.")
                    else:
                        st.session_state.sellers[username] = {
                            "password": password,
                            "store_name": store_name,
                            "loc": (lat, lon),
                            "open_hours": (open_from, open_to),
                            "open_days": open_days,
                            "address": address
                        }
                        st.success("Seller account created! Please sign in.")
            else:
                st.warning("Username and password are required.")

    st.markdown('</div>', unsafe_allow_html=True)

# Rest of your code (init_data, admin_page, home_page, execution flow) remains the same
# Paste your full previous home_page(), admin_page(), init_data(), etc. here

# Example placeholder for the rest (replace with your actual code)
def init_data():
    # ... your existing init_data code ...
    pass

def admin_page():
    # ... your existing admin_page code ...
    pass

def home_page():
    # ... your existing home_page code with live location, search, items, details, etc. ...
    pass

# Execution flow
apply_theme()
init_data()

if not st.session_state.get('authenticated', False):
    auth_page()
else:
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.username} 👋")
        if st.session_state.role == "Seller":
            nav = st.radio("Dashboard", ["Home", "Manage Inventory"])
        else:
            nav = "Home"

        st.divider()
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    if nav == "Manage Inventory":
        admin_page()
    else:
        home_page()
