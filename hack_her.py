import streamlit as st
import pandas as pd
import difflib
from geopy.distance import geodesic
from datetime import datetime
import streamlit.components.v1 as components
import calendar

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="LowKey Deals", layout="wide", page_icon="✨")

# ─────────────────────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────────────────────
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
            margin-bottom: 16px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.08);
            transition: all 0.25s ease;
        }
        .deal-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.12);
        }
        .price-tag {
            color: #8B4513;
            font-size: 1.5rem;
            font-weight: 700;
        }
        .badge {
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            background: #FFE4B5;
            color: #8B4513;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%,100% { transform: scale(1); }
            50%     { transform: scale(1.04); }
        }
        input, textarea {
            color: #000 !important;
            background: #fff !important;
            border: 2px solid #8B4513 !important;
            border-radius: 8px !important;
        }
        div.stButton > button {
            background: #8B4513 !important;
            color: white !important;
            border-radius: 999px !important;
            font-weight: 600;
            padding: 0.6rem 1.4rem !important;
            transition: all 0.2s;
        }
        div.stButton > button:hover {
            background: #A0522D !important;
            transform: scale(1.04);
        }
        </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DATA INIT & HELPERS
# ─────────────────────────────────────────────────────────────
def init_data():
    if 'item_offers' not in st.session_state:
        st.session_state.item_offers = {}

    if 'users' not in st.session_state:
        st.session_state.users = {"user1": "pass1"}

    if 'sellers' not in st.session_state:
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

    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if 'user_location' not in st.session_state:
        st.session_state.user_location = (9.9312, 76.2673)

    if 'catalog_version' not in st.session_state:
        st.session_state.catalog_version = 0

def refresh_catalog():
    st.session_state.catalog_version += 1
    # Force rerun helps in some cases
    st.rerun()

def normalize_name(name: str) -> str:
    return name.strip().lower()

# ─────────────────────────────────────────────────────────────
# SELLER — MANAGE INVENTORY
# ─────────────────────────────────────────────────────────────
def admin_page():
    st.title("📦 Manage Your Inventory")

    store = st.session_state.store_info
    st.markdown(f"**Store:** {store['store_name']}  •  {store['address']}")

    # ───── CSV Bulk Upload ─────
    with st.expander("Bulk upload via CSV", expanded=False):
        st.caption("Columns: name, desc, price, sale_price (optional)")
        uploaded = st.file_uploader("Choose CSV file", type="csv", key="csv_upload")

        if uploaded:
            try:
                df = pd.read_csv(uploaded)
                count = 0
                for _, row in df.iterrows():
                    raw_name = str(row.get("name", "")).strip()
                    if not raw_name:
                        continue
                    name = normalize_name(raw_name)

                    price = float(row.get("price", 0))
                    sale_price_val = float(row.get("sale_price", 0))
                    is_sale = sale_price_val > 0 and sale_price_val < price

                    offer = {
                        "seller_username": st.session_state.username,
                        "store": store["store_name"],
                        "address": store["address"],
                        "loc": store["loc"],
                        "price": price,
                        "sale_price": sale_price_val if is_sale else None,
                        "is_sale": is_sale,
                        "desc": str(row.get("desc", "")).strip(),
                        "reviews": [],
                        "open_hours": store["open_hours"],
                        "open_days": store["open_days"]
                    }

                    if name not in st.session_state.item_offers:
                        st.session_state.item_offers[name] = []

                    # Replace only own previous entry
                    replaced = False
                    for i, ex in enumerate(st.session_state.item_offers[name]):
                        if ex.get("seller_username") == st.session_state.username:
                            st.session_state.item_offers[name][i] = offer
                            replaced = True
                            break
                    if not replaced:
                        st.session_state.item_offers[name].append(offer)

                    count += 1

                if count > 0:
                    refresh_catalog()
                    st.success(f"Processed {count} item{'s' if count > 1 else ''}")
                else:
                    st.info("No valid items found in CSV")

            except Exception as e:
                st.error(f"CSV processing error: {e}")

    st.divider()

    # ───── Single item form ─────
    st.subheader("Add or update single product")

    with st.form("single_item_form"):
        c1, c2 = st.columns([3,2])
        raw_name = c1.text_input("Product name", placeholder="e.g. Samsung Double Door Refrigerator")
        price     = c2.number_input("Regular price (₹)", min_value=0.0, step=100.0)
        sale_price_input = c2.number_input("Sale price (optional)", min_value=0.0, step=100.0)

        description = st.text_area("Description", height=110)

        submitted = st.form_submit_button("Save Product", use_container_width=True)

        if submitted and raw_name.strip():
            name = normalize_name(raw_name)

            is_sale = sale_price_input > 0 and sale_price_input < price

            offer = {
                "seller_username": st.session_state.username,
                "store": store["store_name"],
                "address": store["address"],
                "loc": store["loc"],
                "price": price,
                "sale_price": sale_price_input if is_sale else None,
                "is_sale": is_sale,
                "desc": description.strip(),
                "reviews": [],
                "open_hours": store["open_hours"],
                "open_days": store["open_days"]
            }

            if name not in st.session_state.item_offers:
                st.session_state.item_offers[name] = []

            updated = False
            for i, ex in enumerate(st.session_state.item_offers[name]):
                if ex.get("seller_username") == st.session_state.username:
                    st.session_state.item_offers[name][i] = offer
                    updated = True
                    break
            if not updated:
                st.session_state.item_offers[name].append(offer)

            refresh_catalog()
            st.success(f"✓ Product **{raw_name}** saved / updated")
        elif submitted:
            st.error("Product name is required")

# ─────────────────────────────────────────────────────────────
# USER — HOME / BROWSING PAGE
# ─────────────────────────────────────────────────────────────
def home_page():
    st.title("✨ LowKey Deals")
    st.caption("Discover the best local appliance prices near you")

    # ───── Location ─────
    st.subheader("📍 Your Location")
    colA, colB = st.columns([1,3])

    with colA:
        if st.button("Get my location", type="primary"):
            components.html("""
            <script>
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(pos => {
                    const url = new URL(window.location);
                    url.searchParams.set('lat', pos.coords.latitude);
                    url.searchParams.set('lon', pos.coords.longitude);
                    window.location = url;
                }, err => alert("Location access denied or unavailable"));
            } else {
                alert("Geolocation not supported");
            }
            </script>
            """, height=0)

    with colB:
        lat = st.number_input("Latitude", value=st.session_state.user_location[0], step=0.00001, format="%.6f")
        lon = st.number_input("Longitude", value=st.session_state.user_location[1], step=0.00001, format="%.6f")

        if st.button("Update location"):
            st.session_state.user_location = (lat, lon)
            st.success("Location updated", icon="✅")

    st.divider()

    # ───── Catalog debug (remove later) ─────
    if len(st.session_state.item_offers) == 0:
        st.warning("Catalog is currently empty")
    else:
        st.caption(f"Showing {len(st.session_state.item_offers)} product type{'s' if len(st.session_state.item_offers)>1 else ''}")

    # ───── Search ─────
    search = st.text_input("Search appliances...", "").strip()
    if search:
        keys = list(st.session_state.item_offers.keys())
        suggestions = difflib.get_close_matches(normalize_name(search), [normalize_name(k) for k in keys], n=6, cutoff=0.5)
        if suggestions:
            st.write("Did you mean:")
            cols = st.columns(min(4, len(suggestions)))
            for i, sug_norm in enumerate(suggestions):
                # find original case
                orig = next(k for k in keys if normalize_name(k) == sug_norm)
                if cols[i].button(orig):
                    st.session_state.selected = orig
                    st.rerun()

    # ───── Main grid / detail ─────
    if 'selected' in st.session_state:
        item_name = st.session_state.selected
        offers = st.session_state.item_offers.get(item_name, [])

        st.header(item_name.title())
        if st.button("← Back to list"):
            del st.session_state.selected
            st.rerun()

        if offers:
            min_price = min(o["sale_price"] if o["is_sale"] else o["price"] for o in offers)
            best_store = next(o["store"] for o in offers if (o["sale_price"] if o["is_sale"] else o["price"]) == min_price)

            st.info(f"Lowest price found: **₹{min_price:,}** at **{best_store}**")

            for offer in sorted(offers, key=lambda o: geodesic(st.session_state.user_location, o["loc"]).km):
                dist = geodesic(st.session_state.user_location, offer["loc"]).km
                price_disp = f"₹{offer['sale_price']:,} (sale)" if offer["is_sale"] else f"₹{offer['price']:,}"

                with st.container():
                    st.markdown(f"""
                    <div class="deal-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <h4>{offer['store']}</h4>
                            <div class="price-tag">{price_disp}</div>
                        </div>
                        <div>{offer['desc']}</div>
                        <div style="margin-top:12px;color:#555;font-size:0.95rem;">
                            📍 {dist:.1f} km  •  {offer['address']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No offers for this product yet.")

    else:
        # Grid view
        cols = st.columns(3)
        for i, name in enumerate(sorted(st.session_state.item_offers.keys())):
            offers = st.session_state.item_offers[name]
            if not offers:
                continue
            min_p = min(o["sale_price"] if o["is_sale"] else o["price"] for o in offers)
            min_dist = min(geodesic(st.session_state.user_location, o["loc"]).km for o in offers)

            with cols[i % 3]:
                st.markdown(f"""
                <div class="deal-card">
                    <h4>{name.title()}</h4>
                    <div class="price-tag">from ₹{min_p:,}</div>
                    <div style="color:#666; font-size:0.9rem;">closest ≈ {min_dist:.1f} km</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("View offers", key=f"view_{i}_{name}"):
                    st.session_state.selected = name
                    st.rerun()

# ─────────────────────────────────────────────────────────────
# AUTHENTICATION
# ─────────────────────────────────────────────────────────────
def auth_page():
    st.title("LowKey Deals")
    tab_login, tab_signup = st.tabs(["Login", "Sign up"])

    with tab_login:
        role = st.radio("Role", ["User", "Seller"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if role == "User":
                if username in st.session_state.users and st.session_state.users[username] == password:
                    st.session_state.update(authenticated=True, username=username, role="User")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            else:  # Seller
                if username in st.session_state.sellers and st.session_state.sellers[username]["password"] == password:
                    st.session_state.update(
                        authenticated=True,
                        username=username,
                        role="Seller",
                        store_info=st.session_state.sellers[username]
                    )
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    with tab_signup:
        role = st.radio("Sign up as", ["User", "Seller"])
        username = st.text_input("Choose username")
        password = st.text_input("Choose password", type="password")

        seller_data = {}
        if role == "Seller":
            seller_data["store_name"] = st.text_input("Store name")
            seller_data["address"]   = st.text_input("Store address")
            seller_data["loc"] = (
                st.number_input("Latitude", 8.0, 13.0, 9.93),
                st.number_input("Longitude", 74.0, 78.0, 76.27)
            )
            seller_data["open_hours"] = (
                st.number_input("Opens (hour)", 0, 23, 9),
                st.number_input("Closes (hour)", 0, 23, 21)
            )
            seller_data["open_days"] = st.multiselect(
                "Open days",
                list(calendar.day_name),
                default=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
            )

        if st.button("Create account"):
            if not username or not password:
                st.error("Username & password required")
            elif role == "User":
                if username in st.session_state.users:
                    st.error("Username taken")
                else:
                    st.session_state.users[username] = password
                    st.success("Account created. Please log in.")
            else:
                if username in st.session_state.sellers:
                    st.error("Username taken")
                elif not seller_data.get("store_name"):
                    st.error("Store name required")
                else:
                    st.session_state.sellers[username] = {
                        "password": password,
                        **seller_data
                    }
                    st.success("Seller account created. Please log in.")

# ─────────────────────────────────────────────────────────────
# MAIN FLOW
# ─────────────────────────────────────────────────────────────
apply_theme()
init_data()

if not st.session_state.get("authenticated", False):
    auth_page()
else:
    with st.sidebar:
        st.markdown(f"**{st.session_state.username}** • {st.session_state.role}")
        if st.session_state.role == "Seller":
            page = st.radio("Seller menu", ["Manage Inventory"])
        else:
            page = st.radio("Shopper menu", ["Home"])

        st.divider()
        if st.button("Sign out"):
            st.session_state.clear()
            st.rerun()

    if st.session_state.role == "User" and page == "Home":
        home_page()
    elif st.session_state.role == "Seller" and page == "Manage Inventory":
        admin_page()
