import streamlit as st
import pandas as pd
from datetime import datetime
import difflib
from geopy.distance import geodesic

# --- CONFIGURATION & THEME ---
st.set_page_config(page_title="LowKey Deals", page_icon="🏷️", layout="wide")

def apply_custom_theme():
    st.markdown("""
        <style>
        /* Main background and text */
        .stApp {
            background-color: #FFFFFF;
            color: #000000;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #8B4513 !0important;
        }
        
        /* Buttons */
        div.stButton > button {
            background-color: #8B4513;
            color: #FFFFFF;
            border-radius: 5px;
            border: none;
        }
        div.stButton > button:hover {
            background-color: #A0522D;
            color: #FFFFFF;
            border: 1px solid #000000;
        }
        
        /* Input fields */
        .stTextInput > div > div > input {
            border-color: #8B4513;
        }
        
        /* Badges/Sales Highlight */
        .sale-badge {
            background-color: #8B4513;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #f4ece1;
        }
        </style>
    """, unsafe_allow_html=True)

# --- MOCK DATA INITIALIZATION ---
def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.role = None
        st.session_state.username = None

    # Fixed User Location (Kochi, Kerala)
    st.session_state.user_coords = (9.9312, 76.2673)

    if 'items' not in st.session_state:
        st.session_state.items = {
            "Refrigerator": {"desc": "Double door, 250L", "category": "Kitchen"},
            "Washing Machine": {"desc": "Front load, 7kg", "category": "Laundry"},
            "Microwave Oven": {"desc": "Convection, 20L", "category": "Kitchen"},
            "Air Conditioner": {"desc": "1.5 Ton, 5 Star", "category": "Living"},
            "Vacuum Cleaner": {"desc": "Handheld, Cordless", "category": "Cleaning"},
            "Dishwasher": {"desc": "12 Place Settings", "category": "Kitchen"}
        }

    if 'stores' not in st.session_state:
        st.session_state.stores = [
            {"id": 1, "name": "Brown's Appliances", "lat": 9.9400, "lon": 76.2600, "open": "09:00", "close": "21:00", "rating": 4.5, "seller": "seller1"},
            {"id": 2, "name": "City Electronics", "lat": 9.9200, "lon": 76.2800, "open": "10:00", "close": "22:00", "rating": 3.8, "seller": "admin"},
            {"id": 3, "name": "Vintage Tech", "lat": 9.9500, "lon": 76.2400, "open": "08:00", "close": "20:00", "rating": 4.2, "seller": "seller2"},
        ]

    if 'inventory' not in st.session_state:
        st.session_state.inventory = [
            {"store_id": 1, "item": "Refrigerator", "price": 25000, "on_sale": True},
            {"store_id": 2, "item": "Refrigerator", "price": 27000, "on_sale": False},
            {"store_id": 1, "item": "Washing Machine", "price": 18000, "on_sale": False},
            {"store_id": 3, "item": "Washing Machine", "price": 17500, "on_sale": True},
            {"store_id": 2, "item": "Microwave Oven", "price": 8000, "on_sale": False},
            {"store_id": 1, "item": "Microwave Oven", "price": 7500, "on_sale": True},
        ]

    if 'reviews' not in st.session_state:
        st.session_state.reviews = [
            {"store_id": 1, "user": "user1", "text": "Great prices!", "rating": 5},
            {"store_id": 2, "user": "user1", "text": "A bit far, but good stock.", "rating": 4},
        ]

# --- UTILITY FUNCTIONS ---
def get_distance(coords1, coords2):
    return round(geodesic(coords1, coords2).km, 2)

def is_store_open(open_t, close_t):
    now = datetime.now().time()
    open_time = datetime.strptime(open_t, "%H:%M").time()
    close_time = datetime.strptime(close_t, "%H:%M").time()
    return open_time <= now <= close_time

def calculate_effort(price, distance, rating):
    # Effort Score = (price / 100) + (distance * 0.5) + (5 - rating)
    return round((price / 100) + (distance * 0.5) + (5 - rating), 2)

# --- PAGE COMPONENTS ---
def login_page():
    st.title("Welcome to LowKey Deals")
    role = st.radio("Select Role", ["User", "Seller"])
    
    with st.container():
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            # Mock authentication
            if (role == "User" and username in ["user1", "admin"]) or \
               (role == "Seller" and username in ["seller1", "seller2", "admin"]):
                st.session_state.authenticated = True
                st.session_state.role = role
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid credentials. Try 'user1' or 'seller1'.")

def logout():
    st.session_state.authenticated = False
    st.session_state.role = None
    st.rerun()

def home_page():
    st.markdown("<h1 style='color: #8B4513;'>LowKey Deals</h1>", unsafe_allow_html=True)
    st.markdown("<h5>Lowkey the best prices near you.</h5>", unsafe_allow_html=True)
    
    # --- Search Bar with Fuzzy Matching ---
    search_query = st.text_input("🔍 Search for appliances (e.g., Fridge, Microwave)...")
    if search_query:
        matches = difflib.get_close_matches(search_query, st.session_state.items.keys(), n=3, cutoff=0.3)
        if matches:
            st.write("Suggestions:")
            cols = st.columns(len(matches))
            for i, match in enumerate(matches):
                if cols[i].button(match):
                    st.session_state.search_selection = match
                    st.rerun()

    # --- Sales Section ---
    st.markdown("### 🔥 Ongoing Sales")
    sale_items = [inv for inv in st.session_state.inventory if inv['on_sale']]
    if sale_items:
        cols = st.columns(4)
        for i, sale in enumerate(sale_items[:4]):
            with cols[i]:
                st.markdown(f"**{sale['item']}**")
                st.markdown(f"<span class='sale-badge'>Price: ₹{sale['price']}</span>", unsafe_allow_html=True)
    
    st.divider()

    # --- All Items Grid ---
    st.markdown("### Browse Categories")
    items_list = list(st.session_state.items.keys())
    cols = st.columns(3)
    for i, item in enumerate(items_list):
        with cols[i % 3]:
            st.info(f"**{item}**")
            st.write(st.session_state.items[item]['desc'])
            if st.button(f"View Deals for {item}", key=f"btn_{item}"):
                st.session_state.search_selection = item
                st.rerun()

def item_details_page(item_name):
    st.button("← Back to Home", on_click=lambda: st.session_state.pop('search_selection'))
    st.header(f"Deals for {item_name}")
    
    # Filter stores that have this item
    results = []
    for inv in st.session_state.inventory:
        if inv['item'] == item_name:
            store = next(s for s in st.session_state.stores if s['id'] == inv['store_id'])
            dist = get_distance(st.session_state.user_coords, (store['lat'], store['lon']))
            effort = calculate_effort(inv['price'], dist, store['rating'])
            is_open = is_store_open(store['open'], store['close'])
            
            results.append({
                "Store": store['name'],
                "Price": inv['price'],
                "Distance (km)": dist,
                "Rating": store['rating'],
                "Effort Score": effort,
                "Status": "Open Now" if is_open else "Closed",
                "id": store['id']
            })

    if not results:
        st.warning("No stores found for this item.")
        return

    # Sorting
    df = pd.DataFrame(results).sort_values("Effort Score")
    
    for _, row in df.iterrows():
        with st.expander(f"{row['Store']} - ₹{row['Price']} (Effort Score: {row['Effort Score']})"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Distance", f"{row['Distance (km)']} km")
            c2.metric("Rating", f"{row['Rating']} / 5")
            c3.metric("Status", row['Status'])
            
            st.markdown("---")
            st.subheader("Reviews")
            store_reviews = [r for r in st.session_state.reviews if r['store_id'] == row['id']]
            for rev in store_reviews:
                st.markdown(f"**{rev['user']}**: {rev['text']} ({rev['rating']}⭐)")
            
            # Add Review
            if st.session_state.role == "User":
                with st.form(key=f"rev_form_{row['id']}"):
                    new_rev = st.text_area("Add a review")
                    new_rat = st.slider("Rating", 1, 5, 5)
                    if st.form_submit_button("Submit Review"):
                        st.session_state.reviews.append({
                            "store_id": row['id'],
                            "user": st.session_state.username,
                            "text": new_rev,
                            "rating": new_rat
                        })
                        st.success("Review added!")
                        st.rerun()

def seller_dashboard():
    st.header(f"Seller Dashboard: {st.session_state.username}")
    
    # Get seller's store
    seller_stores = [s for s in st.session_state.stores if s['seller'] == st.session_state.username]
    
    if not seller_stores:
        st.error("No store associated with this account.")
        return

    store = seller_stores[0]
    st.subheader(f"Manage Inventory for {store['name']}")

    with st.form("add_item"):
        item_name = st.selectbox("Select Item", list(st.session_state.items.keys()))
        price = st.number_input("Price (₹)", min_value=0)
        is_sale = st.checkbox("Mark as Sale")
        if st.form_submit_button("Update/Add Item"):
            # Update existing or add new
            st.session_state.inventory = [i for i in st.session_state.inventory 
                                          if not (i['store_id'] == store['id'] and i['item'] == item_name)]
            st.session_state.inventory.append({
                "store_id": store['id'],
                "item": item_name,
                "price": price,
                "on_sale": is_sale
            })
            st.success(f"Updated {item_name}!")

# --- MAIN APP LOGIC ---
apply_custom_theme()
init_session_state()

if not st.session_state.authenticated:
    login_page()
else:
    # Sidebar Navigation
    st.sidebar.title(f"Hello, {st.session_state.username}")
    if st.sidebar.button("Logout"):
        logout()
    
    if st.session_state.role == "Seller":
        seller_dashboard()
        st.sidebar.divider()
    
    # Routing
    if 'search_selection' in st.session_state:
        item_details_page(st.session_state.search_selection)
    else:
        home_page()
