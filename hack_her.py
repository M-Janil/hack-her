def auth_page():
    apply_theme()

    # Extra styling for auth page (reduced top margin)
    st.markdown("""
        <style>
        .auth-wrapper {
            max-width: 520px;
            margin: 2rem auto 4rem;          /* ← reduced from 5rem to 2rem */
            padding: 2.8rem 2.5rem;
            background: linear-gradient(135deg, #ffffff 0%, #fffaf5 100%);
            border-radius: 24px;
            box-shadow: 0 16px 50px rgba(139, 69, 19, 0.10);
            border: 1px solid #f0e4d9;
        }
        .auth-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .auth-header h1 {
            font-size: 3rem;
            color: #8B4513;
            margin: 0.3rem 0 0.6rem;
        }
        .auth-header p {
            color: #6b4e31;
            font-size: 1.1rem;
            margin: 0;
        }
        /* Make tabs look nicer and centered */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            justify-content: center;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 24px !important;
            border-radius: 10px !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #8B4513 !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Make sure users & sellers dicts exist BEFORE any check
    if 'users' not in st.session_state:
        st.session_state.users = {}
    if 'sellers' not in st.session_state:
        st.session_state.sellers = {}

    st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)

    st.markdown("""
        <div class="auth-header">
            <h1>LowKey Deals</h1>
            <p>Discover real local appliance deals near you</p>
        </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

    with tab_login:
        role = st.radio("Sign in as", ["User", "Seller"], horizontal=True)
        username = st.text_input("Username", placeholder="yourname", key="login_user")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")

        if st.button("Sign In", use_container_width=True):
            if not username or not password:
                st.warning("Please enter username and password.")
            elif role == "User":
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
                    st.error("Invalid seller credentials.")

    with tab_signup:
        role = st.radio("Create account as", ["User", "Seller"], horizontal=True)
        username = st.text_input("Choose Username", key="signup_user")
        password = st.text_input("Choose Password", type="password", key="signup_pass")

        store_name = address = lat = lon = open_from = open_to = open_days = None
        if role == "Seller":
            st.markdown("---")
            store_name = st.text_input("Store Name")
            address = st.text_input("Store Address")
            c1, c2 = st.columns(2)
            with c1:
                lat = st.number_input("Latitude", value=9.931245, format="%.6f")
                open_from = st.number_input("Opening Hour (0-23)", 0, 23, 9)
            with c2:
                lon = st.number_input("Longitude", value=76.2673, format="%.6f")
                open_to = st.number_input("Closing Hour (0-23)", 0, 23, 21)
            open_days = st.multiselect(
                "Open Days",
                list(calendar.day_name),
                default=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
            )

        if st.button("Create Account", use_container_width=True):
            if not username or not password:
                st.warning("Username and password are required.")
            elif role == "User":
                if username in st.session_state.users:
                    st.error("Username already taken.")
                else:
                    st.session_state.users[username] = password
                    st.success("Account created! You can now sign in.")
                    st.rerun()  # optional: auto-refresh
            else:
                if username in st.session_state.sellers:
                    st.error("Username already taken.")
                elif not all([store_name, address, open_days]):
                    st.error("Please complete all store details.")
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
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
