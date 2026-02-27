import streamlit as st
import pandas as pd
import difflib
from geopy.distance import geodesic
from datetime import datetime
import streamlit.components.v1 as components

# ────────────────────────────────────────────────
#  PAGE CONFIG & PROFESSIONAL THEME
# ────────────────────────────────────────────────
st.set_page_config(page_title="LowKey Deals", layout="wide", page_icon="🛍️", initial_sidebar_state="expanded")

def apply_professional_theme():
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* ── Global ── */
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
            background: #FFFFFF;
            color: #1F1F1F;
        }
        .stApp { background: #FFFFFF !important; }

        /* ── Typography Hierarchy ── */
        h1, h2, h3, h4 {
            font-family: 'Playfair Display', serif !important;
            color: #2C1608;
            letter-spacing: -0.5px;
        }
        h1 { font-size: 3.8rem; font-weight: 700; margin: 0.4rem 0; }
        h2 { font-size: 2.4rem; font-weight: 600; }
        h3 { font-size: 1.8rem; font-weight: 600; }
        p, div, label, span { font-size: 1.05rem; line-height: 1.6; }

        /* ── Hero Section ── */
        .hero {
            text-align: center;
            padding: 4rem 1rem 5rem;
            background: linear-gradient(135deg, #FFF8F2 0%, #FFFFFF 100%);
            border-bottom: 1px solid #EDE0D4;
        }
        .hero-title {
            font-size: 5.2rem !important;
            color: #8B4513;
            margin: 0;
            text-shadow: 0 3px 12px rgba(139,69,19,0.15);
        }
        .hero-subtitle {
            font-size: 1.65rem;
            color: #5A5A5A;
            font-weight: 500;
            margin-top: 0.8rem;
            max-width: 720px;
            margin-left: auto;
            margin-right: auto;
        }

        /* ── Auth Card ── */
        .auth-card {
            max-width: 520px;
            margin: 6rem auto 4rem;
            padding: 3rem 2.8rem;
            background: white;
            border-radius: 20px;
            box-shadow: 0 16px 48px rgba(0,0,0,0.08);
            border: 1px solid #F0E4D9;
        }
        .auth-header {
            text-align: center;
            margin-bottom: 2.5rem;
        }
        .auth-header h1 {
            font-size: 3.2rem;
            margin: 0 0 0.6rem;
        }
        .auth-header p {
            color: #6B6B6B;
            font-size: 1.15rem;
        }

        /* ── Inputs & Buttons ── */
        input, textarea, [data-testid="stNumberInput"] input, [data-testid="stSelectbox"] > div > div {
            border: 2px solid #B36F3F !important;
            border-radius: 12px !important;
            padding: 0.9rem 1.2rem !important;
            background: #FFF9F5 !important;
            font-size: 1.05rem !important;
        }
        div.stButton > button {
            background: linear-gradient(90deg, #8B4513, #A0522D) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.95rem !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(139,69,19,0.2);
        }
        div.stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 28px rgba(139,69,19,0.3);
        }

        /* ── Deal Cards ── */
        .deal-card {
            background: white;
            border-radius: 16px;
            border: 1px solid #F0E4D9;
            padding: 1.8rem;
            margin-bottom: 1.6rem;
            transition: all 0.35s ease;
            box-shadow: 0 6px 20px rgba(0,0,0,0.05);
        }
        .deal-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 16px 40px rgba(139,69,19,0.15);
        }
        .price-tag {
            color: #8B4513;
            font-size: 1.8rem;
            font-weight: 700;
        }
        .badge {
            background: #FFE8CC;
            color: #8B4513;
            padding: 0.45rem 1rem;
            border-radius: 50px;
            font-size: 0.9rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 1rem;
        }

        /* ── Sidebar Polish ── */
        section[data-testid="stSidebar"] {
            background: #FDF8F2 !important;
            border-right: 1px solid #F0E4D9 !important;
        }
        .sidebar .stRadio > div > label {
            font-size: 1.1rem !important;
            padding: 0.8rem 1rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

# ────────────────────────────────────────────────
#  DATA INITIALIZATION (your original mock data)
# ────────────────────────────────────────────────
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
                    "desc": "Double door, 250L energy efficient",
                    "reviews": [{"user": "user1", "rating": 4, "text": "Good product"}],
                    "open_hours": (9, 21)
                },
                {
                    "store": "Home Mart",
                    "address": "456 Ernakulam Rd, Kerala",
                    "loc": (9.93, 76.27),
                    "price": 26000,
                    "sale_price": 24000,
                    "is_sale": True,
                    "desc": "Double door, 260L with inverter",
                    "reviews": [],
                    "open_hours": (10, 22)
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
                    "desc": "Front load, 7kg with steam wash",
                    "reviews": [],
                    "open_hours": (9, 21)
                },
                {
                    "store": "Home Mart",
                    "address": "456 Ernakulam Rd, Kerala",
                    "loc": (9.93, 76.27),
                    "price": 17000,
                    "sale_price": None,
                    "is_sale": False,
                    "desc": "Front load, 6kg inverter motor",
                    "reviews": [{"user": "user1", "rating": 5, "text": "Excellent"}],
                    "open_hours": (10, 22)
                }
            ]
        }

    if 'users' not in st.session_state:
        st.session_state.users = {"user1": "pass1", "test": "1234"}

    if 'sellers' not in st.session_state:
        st.session_state.sellers = {
            "seller1": {
                "password": "pass1",
                "store_name": "Appliance World",
                "loc": (9.95, 76.29),
                "open_hours": (9, 21),
                "address": "123 Kochi St, Kerala"
            },
            "seller2": {
                "password": "pass2",
                "store_name": "Home Mart",
                "loc": (9.93, 76.27),
                "open_hours": (10, 22),
                "address": "456 Ernakulam Rd, Kerala"
            }
        }

    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_location' not in st.session_state:
        st.session_state.user_location = (9.9312, 76.2673)  # Kochi default

# ────────────────────────────────────────────────
#  AUTHENTICATION PAGE – Professional card layout
# ────────────────────────────────────────────────
def auth_page():
    apply_professional_theme()

    st.markdown('<div class="auth-card">', unsafe_allow_html=True)

    st.markdown('<div class="auth-header">', unsafe_allow_html=True)
    st.markdown('<h1>LowKey Deals</h1>', unsafe_allow_html=True)
    st.markdown('<p>Find the best local appliance prices near you — effortlessly.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Sign In", "Create Account"])

    with tab1:
        role = st.radio("I want to sign in as", ["User", "Seller"], horizontal=True, label_visibility="collapsed")
        username = st.text_input("Username", placeholder="yourname")
        password = st.text_input("Password", type="password", placeholder="••••••••")

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
                else:  # Seller
                    if username in st.session_state.sellers and st.session_state.sellers[username]["password"] == password:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.role = role
                        st.session_state.store_info = st.session_state.sellers[username]
                        st.rerun()
                    else:
                        st.error("Invalid credentials for seller.")
            else:
                st.warning("Please enter username and password.")

    with tab2:
        role = st.radio("I want to create an account as", ["User", "Seller"], horizontal=True, label_visibility="collapsed")
        username = st.text_input("Choose Username", placeholder="yourname")
        password = st.text_input("Choose Password", type="password")

        store_name = address = lat = lon = open_from = open_to = None
        if role == "Seller":
            store_name = st.text_input("Store Name")
            address = st.text_input("Store Address")
            col1, col2 = st.columns(2)
            with col1:
                lat = st.number_input("Store Latitude", value=9.93, format="%.5f")
                open_from = st.number_input("Opening Hour (0-23)", 0, 23, 9)
            with col2:
                lon = st.number_input("Store Longitude", value=76.27, format="%.5f")
                open_to = st.number_input("Closing Hour (0-23)", 0, 23, 21)

        if st.button("Create Account", use_container_width=True):
            if username and password:
                if role == "User":
                    if username in st.session_state.users:
                        st.error("Username already taken.")
                    else:
                        st.session_state.users[username] = password
                        st.success("Account created! You can now sign in.")
                else:
                    if username in st.session_state.sellers:
                        st.error("Username already taken.")
                    elif not (store_name and address):
                        st.error("Store name and address are required for sellers.")
                    else:
                        st.session_state.sellers[username] = {
                            "password": password,
                            "store_name": store_name,
                            "loc": (lat, lon),
                            "open_hours": (open_from, open_to),
                            "address": address
                        }
                        st.success("Seller account created! Please sign in.")
            else:
                st.warning("Username and password are required.")

    st.markdown('</div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────
#  HOME PAGE (you can continue expanding this part)
# ────────────────────────────────────────────────
def home_page():
    apply_professional_theme()

    # Hero Section
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">LowKey Deals</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Lowkey the best prices near you — discover real local savings today.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Your existing location picker, search bar, sales section, item grid, detail view...
    # Paste the rest of your home_page logic here (live location, search, cards, details, etc.)
    # For brevity, I'm leaving a placeholder — replace with your full home_page content

    st.subheader("Featured Categories")
    cols = st.columns(3)
    with cols[0]:
        st.markdown('<div class="deal-card"><h3>Refrigerators</h3><p>Best deals on double-door & side-by-side models</p></div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown('<div class="deal-card"><h3>Washing Machines</h3><p>Front-load & top-load with inverter tech</p></div>', unsafe_allow_html=True)
    with cols[2]:
        st.markdown('<div class="deal-card"><h3>Air Conditioners</h3><p>Inverter & smart ACs at lowest local prices</p></div>', unsafe_allow_html=True)

    # ... add your search bar, item listing, detail view, effort score, reviews, etc.

# ────────────────────────────────────────────────
#  MAIN FLOW
# ────────────────────────────────────────────────
init_data()

if not st.session_state.get('authenticated', False):
    auth_page()
else:
    with st.sidebar:
        st.title("LowKey Deals")
        st.markdown(f"**Welcome, {st.session_state.username}**")
        if st.session_state.role == "Seller":
            page = st.radio("Navigation", ["Home", "Manage Inventory"])
        else:
            page = "Home"

        if st.button("Sign Out", type="primary"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    if page == "Manage Inventory":
        # Your seller inventory management code here...
        st.title("Manage Your Inventory")
        st.write("Add / update products for your store...")
    else:
        home_page()
