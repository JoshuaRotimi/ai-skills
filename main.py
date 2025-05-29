import streamlit as st
import openai

# Initialize OpenAI API (replace with your keys)
openai.api_key = "sk-..."  # Replace with your real key

# Simulate transaction history (in-memory)
if "transaction_history" not in st.session_state:
    st.session_state.transaction_history = []

def classify_transaction(amount, history):
    # Repeated transaction check
    repeated_count = history.count(amount)

    if amount >= 1_000_000 or repeated_count >= 2:
        return "Abnormal"
    elif 500_000 <= amount < 1_000_000:
        return "New"
    else:
        return "Normal"

def ai_classify(amount, history):
    prompt = f"""
You are a financial transaction classifier.

Rules:
- "Normal": if amount is below 500000 Naira.
- "New": if amount is 500000 or more but less than 1000000 Naira.
- "Abnormal": if amount is 1000000 or more OR if the same amount has been sent 3 times or more.

Transaction History: {history}
New Transaction Amount: {amount}

Classify the transaction strictly as one of: Normal, New, Abnormal.
Category:
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a financial transaction classifier."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )
    return response.choices[0].message["content"].strip()

# --- Streamlit UI ---
st.title("🏦 AI Bank Transaction Agent")

bank = st.text_input("Bank Name", placeholder="e.g., GTBank")
account = st.text_input("Account Number")
amount = st.number_input("Amount to Send (₦)", min_value=0.0, step=1000.0)
pin = st.text_input("Enter your PIN", type="password")

if st.button("Send Money"):
    if not all([bank, account, amount, pin]):
        st.warning("Please fill in all fields.")
    else:
        history = st.session_state.transaction_history
        classification = classify_transaction(amount, history)
        # Alternatively: classification = ai_classify(amount, history)

        if classification == "Abnormal":
            st.error(f"❌ Transaction BLOCKED as {classification}.")
        else:
            history.append(amount)
            st.success(f"✅ Transaction ALLOWED as {classification}. ₦{amount} sent to {bank} ({account})")

        st.write("📜 Transaction History:", history)