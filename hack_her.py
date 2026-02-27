import streamlit as st
import pandas as pd
import difflib
from geopy.distance import geodesic
from datetime import datetime
import streamlit.components.v1 as components
import calendar

# ────────────────────────────────────────────────
# CONFIG & SHARED CATALOG
# ────────────────────────────────────────────────
st.set_page_config(page_title="LowKey Deals", layout="wide", page_icon="✨")

@st.cache_resource
def get_shared_catalog():
    return {}

GLOBAL_CATALOG = get_shared_catalog()

def apply_theme():
    st.markdown("""
        <style>
        html, body, [data-testid="stHeader"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, span, .stRadio p {
            color: #000000 !important;
            font-weight: 500;
        }
        .stApp { background-color: #FFFFFF; }
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
        .price-tag { color: #8B4513; font-size: 1.4rem; font-weight: bold; }
        .badge {
            padding: 4px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold;
            text-transform: uppercase; background-color: #FFE4B5; color: #8B4513;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
        input, textarea { color: #000 !important; background: #fff !important; border: 2px solid #8B4513 !important; }
        div.stButton > button {
            background-color: #8B4513 !important; color: #FFFFFF !important;
            border-radius: 20px; font-weight: bold; transition: 0.3s; width: 100%;
        }
        div.stButton > button:hover { background-color: #A0522D !important; transform: scale(1.05); }
        </style>
    """, unsafe_allow_html=True)

# ────────────────────────────────────────────────
# INIT DATA
# ────────────────────────────────────────────────
def init_data():
    if "users" not in st.session_state:
        st.session_state.users = {"user1": "pass1"}
    if "sellers" not in st.session_state:
        st.session_state.sellers = {
            "seller1": {
                "password": "pass1",
                "store_name": "Appliance World",
                "loc": (9.95, 76.29),
                "open_hours": (9, 21),
                "open_days": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],
                "address": "123 Kochi St, Kerala"
            },
            "seller2": {
                "password": "pass2",
                "store_name": "Home Mart",
                "loc": (9.93, 76.27),
                "open_hours": (10, 22),
                "open_days": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
                "address": "456 Ernakulam Rd, Kerala"
            }
        }
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_location" not in st.session_state:
        st.session_state.user_location = (9.9312, 76.2673)
    if "role" not in st.session_state:
        st.session_state.role = None

# ────────────────────────────────────────────────
# SELLER INVENTORY PAGE
# ────────────────────────────────────────────────
def admin_page():
    st.title("📦 Manage Inventory")
    if 'store_info' not in st.session_state or not st.session_state.store_info:
        st.error("Store info missing. Please log out and log in again.")
        return

    store_name = st.session_state.store_info["store_name"]
    st.subheader(f"Your store: {store_name}")

    with st.expander("CSV Bulk Upload"):
        st.caption("Expected columns: name, desc, price, sale_price (optional)")
        uploaded = st.file_uploader("Upload CSV", type="csv")
        if uploaded:
            try:
                df = pd.read_csv(uploaded)
                count = 0
                for _, row in df.iterrows():
                    name = str(row.get('name','')).strip()
                    if not name: continue
                    price = float(row.get('price', 0))
                    sale_price = float(row.get('sale_price', 0))
                    is_sale = sale_price > 0 and sale_price < price
                    offer = {
                        "seller_username": st.session_state.username,
                        "store": store_name,
                        "address": st.session_state.store_info["address"],
                        "loc": st.session_state.store_info["loc"],
                        "price": price,
                        "sale_price": sale_price if is_sale else None,
                        "is_sale": is_sale,
                        "desc": str(row.get('desc','')).strip(),
                        "reviews": [],
                        "open_hours": st.session_state.store_info["open_hours"],
                        "open_days": st.session_state.store_info["open_days"]
                    }
                    if name not in GLOBAL_CATALOG:
                        GLOBAL_CATALOG[name] = []
                    # Update only own entry
                    for i, ex in enumerate(GLOBAL_CATALOG[name]):
                        if ex.get("seller_username") == st.session_state.username:
                            GLOBAL_CATALOG[name][i] = offer
                            break
                    else:
                        GLOBAL_CATALOG[name].append(offer)
                    count += 1
                if count > 0:
                    st.success(f"Added/updated {count} items")
                    st.rerun()
            except Exception as e:
                st.error(f"CSV error: {e}")

    st.divider()

    st.subheader("Add / Update Single Item")
    with st.form("manual_add"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Product Name")
        price = c2.number_input("Regular Price (₹)", min_value=0.0, step=100.0)
        sale_price = c2.number_input("Sale Price (optional)", min_value=0.0, step=100.0)
        desc = st.text_area("Description")

        if st.form_submit_button("Save Item"):
            if not name.strip():
                st.error("Product name required")
            else:
                is_sale = sale_price > 0 and sale_price < price
                offer = {
                    "seller_username": st.session_state.username,
                    "store": store_name,
                    "address": st.session_state.store_info["address"],
                    "loc": st.session_state.store_info["loc"],
                    "price": price,
                    "sale_price": sale_price if is_sale else None,
                    "is_sale": is_sale,
                    "desc": desc.strip(),
                    "reviews": [],
                    "open_hours": st.session_state.store_info["open_hours"],
                    "open_days": st.session_state.store_info["open_days"]
                }
                if name not in GLOBAL_CATALOG:
                    GLOBAL_CATALOG[name] = []
                for i, ex in enumerate(GLOBAL_CATALOG[name]):
                    if ex.get("seller_username") == st.session_state.username:
                        GLOBAL_CATALOG[name][i] = offer
                        break
                else:
                    GLOBAL_CATALOG[name].append(offer)
                st.success(f"Item '{name}' saved/updated")
                st.rerun()

# ────────────────────────────────────────────────
# USER HOME PAGE
# ────────────────────────────────────────────────
def home_page():
    st.subheader("🗺️ Your Location")
    components.html("""
        <button onclick="getLocation()" style="background:#8B4513;color:white;padding:10px 20px;border:none;border-radius:20px;cursor:pointer;">
            Get My Location
        </button>
        <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(p => {
                    const url = new URL(window.parent.location);
                    url.searchParams.set('lat', p.coords.latitude);
                    url.searchParams.set('lon', p.coords.longitude);
                    window.parent.location = url;
                }, e => alert(e.message));
            }
        }
        </script>
    """, height=70)

    q = st.query_params
    if 'lat' in q and 'lon' in q:
        try:
            st.session_state.user_location = (float(q['lat'][0]), float(q['lon'][0]))
            st.success("Location updated")
        except:
            st.warning("Invalid location parameters")

    with st.expander("Manual location"):
        lat = st.number_input("Latitude", value=st.session_state.user_location[0], step=0.0001)
        lon = st.number_input("Longitude", value=st.session_state.user_location[1], step=0.0001)
        if st.button("Save"):
            st.session_state.user_location = (lat, lon)
            st.rerun()

    st.divider()

    col1, col2 = st.columns([4,1])
    with col1:
        st.title("✨ LowKey Deals")
        st.markdown("### Find the best local appliance prices near you")
    with col2:
        st.caption("📍 Your location")
        st.code(f"{st.session_state.user_location[0]:.4f}, {st.session_state.user_location[1]:.4f}")

    # Sales section
    st.subheader("🔥 Hot Sales")
    sales = []
    for item, offers in GLOBAL_CATALOG.items():
        for o in offers:
            if o.get("is_sale"):
                sales.append((item, o))

    if sales:
        cols = st.columns(3)
        for idx, (name, o) in enumerate(sales):
            dist = geodesic(st.session_state.user_location, o["loc"]).km
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="deal-card">
                    <span class="badge">SALE</span>
                    <h4>{name}</h4>
                    <p>{o['desc'][:50]}{'...' if len(o['desc'])>50 else ''}</p>
                    <del>₹{o['price']:,}</del> <span class="price-tag">₹{o['sale_price']:,}</span>
                    <div style="color:#666; font-size:0.85rem;">~{dist:.1f} km</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View", key=f"sale_{idx}"):
                    st.session_state.selected_item = name
                    st.rerun()
    else:
        st.info("No sales right now")

    # Search & grid
    search_term = st.text_input("Search appliances...")
    items = list(GLOBAL_CATALOG.keys())
    if search_term:
        items = difflib.get_close_matches(search_term, items, n=5, cutoff=0.5)

    if 'selected_item' in st.session_state:
        name = st.session_state.selected_item
        offers = GLOBAL_CATALOG.get(name, [])
        if offers:
            st.header(name)
            # ... (you can copy-paste your full detailed view here: effort score, open status, reviews, directions, etc.)
            # For brevity I left a simple version below
            for o in offers:
                dist = geodesic(st.session_state.user_location, o["loc"]).km
                price = o["sale_price"] if o.get("is_sale") else o["price"]
                st.markdown(f"""
                <div class="deal-card">
                    <h4>{o['store']}</h4>
                    <p>{o['desc']}</p>
                    <p class="price-tag">₹{price:,}</p>
                    <div>Distance: {dist:.1f} km</div>
                </div>
                """, unsafe_allow_html=True)

            if st.button("Back"):
                if 'selected_item' in st.session_state:
                    del st.session_state.selected_item
                st.rerun()
        else:
            st.info("No offers for this item")
    else:
        st.subheader("Available Appliances")
        cols = st.columns(3)
        for i, name in enumerate(items):
            offers = GLOBAL_CATALOG[name]
            min_price = min(o["sale_price"] if o.get("is_sale") else o["price"] for o in offers)
            min_dist = min(geodesic(st.session_state.user_location, o["loc"]).km for o in offers)
            with cols[i % 3]:
                st.markdown(f"""
                <div class="deal-card">
                    <h4>{name}</h4>
                    <p class="price-tag">From ₹{min_price:,}</p>
                    <div style="color:#666;">Closest ≈ {min_dist:.1f} km</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View offers", key=f"view_{i}"):
                    st.session_state.selected_item = name
                    st.rerun()

# ────────────────────────────────────────────────
# AUTHENTICATION
# ────────────────────────────────────────────────
def auth_page():
    st.title("Welcome to LowKey Deals")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        role = st.radio("I am a", ["User", "Seller"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if role == "User":
                if username in st.session_state.users and st.session_state.users[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.role = "User"
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            else:
                if username in st.session_state.sellers and st.session_state.sellers[username]["password"] == password:
                    st.session_state.authenticated = True
                    st.session_state.role = "Seller"
                    st.session_state.username = username
                    st.session_state.store_info = st.session_state.sellers[username]
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    with tab2:
        role = st.radio("Sign up as", ["User", "Seller"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        store_data = {}
        if role == "Seller":
            store_data["store_name"] = st.text_input("Store Name")
            store_data["address"] = st.text_input("Address")
            store_data["loc"] = (
                st.number_input("Latitude", value=9.93),
                st.number_input("Longitude", value=76.27)
            )
            store_data["open_hours"] = (
                st.number_input("Open hour", 0, 23, 9),
                st.number_input("Close hour", 0, 23, 21)
            )
            store_data["open_days"] = st.multiselect(
                "Open days", list(calendar.day_name),
                default=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
            )
        if st.button("Sign Up"):
            if role == "User":
                if username in st.session_state.users:
                    st.error("Username taken")
                else:
                    st.session_state.users[username] = password
                    st.success("Account created – please login")
            else:
                if username in st.session_state.sellers:
                    st.error("Username taken")
                elif not store_data.get("store_name"):
                    st.error("Store name required")
                else:
                    st.session_state.sellers[username] = {
                        "password": password,
                        **store_data
                    }
                    st.success("Seller account created – please login")

# ────────────────────────────────────────────────
# MAIN FLOW
# ────────────────────────────────────────────────
apply_theme()
init_data()

if not st.session_state.get("authenticated", False):
    auth_page()
else:
    with st.sidebar:
        st.markdown(f"**{st.session_state.username}**  •  {st.session_state.role}")
        if st.session_state.role == "Seller":
            page = st.radio("Menu", ["Home", "Manage Inventory"])
        else:
            page = "Home"
        st.divider()
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    if page == "Manage Inventory" and st.session_state.role == "Seller":
        admin_page()
    else:
        home_page()
