import streamlit as st
import requests
import json

API_URL = "https://riskiq-ai-kyc-sentinel-2.onrender.com/api/Transactions/process-natural"
USERS_API_URL = "https://riskiq-ai-kyc-sentinel-2.onrender.com/api/Transactions/users"

# Page config for better appearance
st.set_page_config(
    page_title="KYC Risk Assessment",
    page_icon="🛡️",
    layout="centered"
)

st.title("🛡️ KYC Risk Assessment Agent")
st.markdown("*AI-powered transaction risk analysis and compliance checking*")

# Add some spacing
st.markdown("---")


# Function to fetch users
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_users():
    try:
        response = requests.get(USERS_API_URL, timeout=10)
        if response.status_code == 200:
            users_data = response.json()
            # Extract emails from the response
            if isinstance(users_data, list):
                return [user.get('email', 'Unknown') for user in users_data if user.get('email')]
            else:
                return []
        else:
            st.error(f"Failed to fetch users: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching users: {str(e)}")
        return []


# Fetch users
users_list = fetch_users()

# Simplified Transaction Form
st.subheader("📝 Transaction Details")

# Create a clean form layout
with st.container():
    col1, col2 = st.columns([1, 1])

    with col1:
        # User dropdown
        if users_list:
            selected_email = st.selectbox(
                "👤 Select User",
                options=users_list,
                help="Select a user from the list"
            )
        else:
            st.warning("⚠️ No users available. Please check your connection.")
            selected_email = st.text_input(
                "📧 Email Address",
                placeholder="user@example.com",
                help="Fallback email input"
            )

        # Add refresh button for users
        if st.button("🔄 Refresh Users", help="Reload user list"):
            st.cache_data.clear()
            st.rerun()

# Add spacing
st.markdown("---")

# Chat Section
st.subheader("💬 Risk Assessment Chat")

# Initialize chat messages
if "messages" not in st.session_state:
    st.session_state["messages"] = [{
        "role": "assistant",
        "content": "👋 Hello! I'm your KYC Risk Assessment Agent. "
                   "Please provide your transaction details above and ask me"
                   " anything about risk analysis, compliance, or potential concerns."
    }]

# Display chat messages with better styling
chat_container = st.container()
with chat_container:
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("💭 Ask about transaction risk, compliance, or any concerns..."):
    # Validate required fields
    if not selected_email or not prompt:
        st.error("⚠️ Please fill in all transaction details above before asking questions.")
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

# Add footer with helpful information
# st.markdown("---")
# with st.expander("💡 Sample Questions You Can Ask"):
#     st.markdown("""
#     **Try asking:**
#     - "What's the risk level of this transaction?"
#     - "Are there any red flags I should be aware of?"
#     - "Is this transaction compliant with current regulations?"
#     - "What additional verification steps might be needed?"
#     - "How does this transaction compare to typical patterns?"
#     """)

# Quick reset button
if st.button("🔄 Start New Analysis", type="secondary"):
    st.session_state["messages"] = [{
        "role": "assistant",
        "content": "👋 Ready for a new transaction analysis! "
                   "Please update the transaction details above and ask your questions."
    }]
    st.rerun()