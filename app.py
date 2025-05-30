import streamlit as st
import requests
import json

API_URL = "https://riskiq-ai-kyc-sentinel-2.onrender.com/api/Transactions/process-natural"
USERS_API_URL = "https://riskiq-ai-kyc-sentinel-2.onrender.com/api/Transactions/users"
PATTERNS_API_URL = "https://riskiq-ai-kyc-sentinel-2.onrender.com/api/Transactions/patterns"
TRANSFER_API_URL = "https://riskiq-ai-kyc-sentinel-2.onrender.com/api/Transactions/process"

# Page config for better appearance
st.set_page_config(
    page_title="KYC Risk Assessment",
    page_icon="🛡️",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container styling */
    .main > div {
        padding-top: 2rem;
    }

    /* Header styling */
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
    }

    /* Card-like containers */
    .user-section {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }

    .user-profile-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(240, 147, 251, 0.3);
    }

    .user-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }

    .user-details h3 {
        margin: 0;
        font-size: 1.2rem;
    }

    .user-details p {
        margin: 0.2rem 0;
        opacity: 0.9;
    }

    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }

    /* Chat section styling */
    .chat-header {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: 600;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    .transfer-btn {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.7rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    .transfer-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(86, 171, 47, 0.4) !important;
    }

    /* Modal styling */
    .modal-content {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        max-width: 500px;
        width: 100%;
    }

    /* Success/Error message styling */
    .success-msg {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #065f46;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .error-msg {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        color: #991b1b;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    /* Selectbox styling */
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }

    /* Remove default streamlit styling */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🛡️ KYC Risk Assessment Agent</h1>
    <p style="margin: 0; opacity: 0.9; font-size: 1.1rem;">AI-powered transaction risk analysis and compliance checking</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for modal
if "show_transfer_modal" not in st.session_state:
    st.session_state.show_transfer_modal = False


# Function to fetch users
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_users():
    try:
        response = requests.get(USERS_API_URL, timeout=60)
        if response.status_code == 200:
            users_data = response.json()
            # Return the full user data instead of just emails
            if isinstance(users_data, list):
                return users_data
            else:
                return []
        else:
            st.error(f"Failed to fetch users: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching users: {str(e)}")
        return []


# Function to fetch user patterns
@st.cache_data(ttl=300)
def fetch_user_patterns(user_id):
    try:
        response = requests.get(f"{PATTERNS_API_URL}/{user_id}", timeout=60)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch user patterns: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching user patterns: {str(e)}")
        return None


# Function to process transfer
def process_transfer(transfer_data):
    print('Data', transfer_data)
    try:
        response = requests.post(
            TRANSFER_API_URL,
            json=transfer_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        return response
    except Exception as e:
        st.error(f"Transfer error: {str(e)}")
        return None


# Fetch users
users_list = fetch_users()

# User Selection Section
st.markdown("### 👤 User Selection")

col1, col2 = st.columns([3, 1])

with col1:
    if users_list:
        # Create options for selectbox with user emails
        user_options = [f"{user.get('email', 'Unknown')} - {user.get('name', 'No Name')}" for user in users_list]
        selected_user_index = st.selectbox(
            "Select User Email",
            options=range(len(user_options)),
            format_func=lambda x: user_options[x],
            help="Choose a user from the available list",
            label_visibility="collapsed"
        )
        selected_user = users_list[selected_user_index]
        selected_email = selected_user.get('email', '')
    else:
        st.warning("⚠️ No users available. Please check your connection.")
        selected_email = st.text_input(
            "Email Address",
            placeholder="user@example.com",
            help="Enter email address manually",
            label_visibility="collapsed"
        )
        selected_user = {"email": selected_email, "name": "Manual Entry", "id": None}

with col2:
    if st.button("🔄 Refresh", help="Reload user list", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# User Profile Section
if selected_email and users_list:
    user_id = selected_user.get('id')
    if user_id:
        # Fetch user patterns
        user_patterns = fetch_user_patterns(user_id)

        # Display user profile card
        st.markdown(f"""
        <div class="user-profile-card">
            <div class="user-info">
                <div class="user-details">
                    <h3>👤 {selected_user.get('name', 'Unknown User')}</h3>
                    <p>📧 {selected_user.get('email', 'No Email')}</p>
                    <p>🆔 ID: {selected_user.get('id', 'No ID')}</p>
                </div>
                <div class="status-badge">
                    KYC Status: {selected_user.get('kycStatus', 'Active')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Transfer button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("💸 Transfer", key="transfer_btn", use_container_width=True):
                st.session_state.show_transfer_modal = True

# Transfer Modal
if st.session_state.show_transfer_modal:
    st.markdown("---")
    st.markdown("### 💸 Transfer Funds")

    with st.form("transfer_form"):
        st.markdown("#### Transfer Details")

        col1, col2 = st.columns(2)

        with col1:
            transfer_amount = st.number_input(
                "Amount",
                min_value=0.01,
                value=500.0,
                step=10.0,
                help="Enter the amount to transfer"
            )

            currency = st.selectbox(
                "Currency",
                options=["naira", "dollar", "euro", "pound"],
                index=0,
                help="Select the currency"
            )

        with col2:
            destination_account = st.text_input(
                "Destination Account",
                value="2098093020",
                help="Enter the destination account number"
            )

            country_code = st.selectbox(
                "Country Code",
                options=["NG", "US", "UK", "EU"],
                index=0,
                help="Select the country code"
            )

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.form_submit_button("✅ Process Transfer", use_container_width=True):
                # Prepare transfer data
                transfer_data = {
                    "email": selected_email,
                    "amount": transfer_amount,
                    "type": 0,
                    "currency": currency,
                    "countryCode": country_code,
                    "sourceAccount": "2345678902",
                    "destinationAccount": destination_account
                }

                # Process transfer
                with st.spinner("Processing transfer..."):
                    response = process_transfer(transfer_data)

                    if response and response.status_code == 200:
                        try:
                            response_data = response.json()
                            print('Response', response_data)
                            # Extract statusMessage from the response
                            if "message" in response_data:
                                status_message = response_data["message"]
                                st.success(f"✅ {status_message}")
                            else:
                                st.success("✅ Transfer processed successfully!")
                        except json.JSONDecodeError:
                            st.success("✅ Transfer processed successfully!")

                        st.session_state.show_transfer_modal = False
                    elif response:
                        try:
                            error_data = response.json()
                            if "message" in error_data:
                                st.error(f"❌ {error_data['message']}")
                            else:
                                st.error(f"❌ Transfer failed: {response.status_code} - {response.text}")
                        except json.JSONDecodeError:
                            st.error(f"❌ Transfer failed: {response.status_code} - {response.text}")
                    else:
                        st.error("❌ Transfer failed due to connection error")

        with col3:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state.show_transfer_modal = False
                st.rerun()

# Chat Section
if not st.session_state.show_transfer_modal:
    # st.markdown("""
    # <div class="chat-header">
    #     💬 Risk Assessment Chat
    # </div>
    # """, unsafe_allow_html=True)

    # Initialize chat messages
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{
            "role": "assistant",
            "content": "👋 Hello! I'm your KYC Risk Assessment Agent. "
                       "Please select a user above and ask me anything "
                       "about risk analysis, compliance, or potential concerns."
        }]

    # Display chat messages
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("💭 Ask about transaction risk, compliance, or any concerns..."):
        # Validate required fields
        if not selected_email or not prompt:
            st.error("⚠️ Please select a user above before asking questions.")
        else:
            # Add user message
            st.session_state["messages"].append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("🔍 Analyzing transaction risk..."):
                    try:
                        payload = {
                            "email": selected_email,
                            "description": prompt,
                            "request": prompt,
                        }

                        response = requests.post(
                            API_URL,
                            json=payload,
                            headers={"Content-Type": "application/json"},
                            timeout=30
                        )

                        if response.status_code == 200:
                            response_data = response.json()

                            # Extract statusMessage from the response
                            if "statusMessage" in response_data:
                                reply = response_data["statusMessage"]
                            else:
                                # Fallback to other possible response fields
                                if "response" in response_data:
                                    reply = response_data["response"]
                                elif "message" in response_data:
                                    reply = response_data["message"]
                                elif "reply" in response_data:
                                    reply = response_data["reply"]
                                elif "result" in response_data:
                                    reply = response_data["result"]
                                else:
                                    reply = f"✅ Analysis complete: {response_data}"
                        else:
                            reply = f"❌ Error {response.status_code}: {response.text}"

                    except requests.exceptions.Timeout:
                        reply = "⏱️ Request timed out. Please try again."
                    except requests.exceptions.ConnectionError:
                        reply = "🔌 Connection error. Check your internet connection and try again."
                    except Exception as e:
                        reply = f"❌ Unexpected error: {str(e)}"

                    # Add AI response
                    st.session_state["messages"].append({"role": "assistant", "content": reply})
                    st.markdown(reply)

    # Reset button at the bottom
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    # with col2:
    #     if st.button("🔄 Start New Analysis", type="secondary", use_container_width=True):
    #         st.session_state["messages"] = [{
    #             "role": "assistant",
    #             "content": "👋 Ready for a new transaction analysis! Please select a user and ask your questions."
    #         }]
    #         st.rerun()
