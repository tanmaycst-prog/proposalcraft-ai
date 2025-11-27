# license_generator.py
import secrets
import string
from datetime import datetime, timedelta


def generate_license_key(tier, quantity=1):
    """Generate unique license keys for each tier"""
    licenses = []

    prefix_map = {
        "monthly": "PROPOSAL-2024-MONTH",
        "yearly": "PROPOSAL-2024-YEAR",
        "lifetime": "PROPOSAL-2024-LIFE"
    }

    expiry_map = {
        "monthly": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "yearly": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
        "lifetime": "2099-12-31"
    }

    for _ in range(quantity):
        # Generate random 6-character suffix
        suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        license_key = f"{prefix_map[tier]}-{suffix}"

        licenses.append({
            'key': license_key,
            'tier': tier,
            'expiry': expiry_map[tier]
        })

    return licenses


def display_license_generator():
    """Standalone license generator for BMC distribution"""
    import streamlit as st

    st.set_page_config(
        page_title="License Generator - ProposalCraft AI",
        page_icon="🔑",
        layout="centered"
    )

    st.title("🔑 ProposalCraft AI License Generator")
    st.markdown("Generate license keys for Buy Me a Coffee distribution")

    col1, col2 = st.columns(2)

    with col1:
        tier = st.selectbox(
            "Select Tier:",
            ["monthly", "yearly", "lifetime"],
            help="Choose the license tier"
        )

    with col2:
        quantity = st.number_input(
            "Number of licenses:",
            min_value=1,
            max_value=50,
            value=5,
            help="How many licenses to generate"
        )

    if st.button("🎯 Generate License Keys", type="primary", use_container_width=True):
        with st.spinner("Generating license keys..."):
            licenses = generate_license_key(tier, quantity)

            st.success(f"✅ Generated {quantity} {tier} license keys!")

            # Display licenses in a nice format
            st.markdown("### 📋 Generated License Keys")
            st.markdown("Copy these and add to the main app's `VALID_LICENSES` dictionary:")

            for i, license_data in enumerate(licenses, 1):
                st.code(f'"{license_data["key"]}": "{license_data["expiry"]}",  # {license_data["tier"].title()}')

            # Show usage instructions
            st.markdown("---")
            st.markdown("### 📝 How to Use:")
            st.markdown(f"""
            1. **Copy the license keys** above
            2. **Add to main app** in the `VALID_LICENSES` dictionary
            3. **Send to BMC customers** via email
            4. **Customers activate** in the app sidebar

            **Example format for BMC email:**
            ```
            Your ProposalCraft AI {tier.title()} License:

            License Key: {licenses[0]['key']}
            Expiry Date: {licenses[0]['expiry']}

            How to activate:
            1. Go to https://job-proposal-craft-ai.streamlit.app/
            2. Find "🔑 Premium License" in sidebar
            3. Enter your license key
            4. Click "Activate"
            ```
            """)

    # Bulk generation section
    st.markdown("---")
    st.markdown("### 🚀 Bulk License Generation")

    bulk_col1, bulk_col2, bulk_col3 = st.columns(3)

    with bulk_col1:
        if st.button("Generate 5 Monthly", use_container_width=True):
            licenses = generate_license_key("monthly", 5)
            st.session_state.bulk_licenses = licenses
            st.success("Generated 5 monthly licenses!")

    with bulk_col2:
        if st.button("Generate 5 Yearly", use_container_width=True):
            licenses = generate_license_key("yearly", 5)
            st.session_state.bulk_licenses = licenses
            st.success("Generated 5 yearly licenses!")

    with bulk_col3:
        if st.button("Generate 5 Lifetime", use_container_width=True):
            licenses = generate_license_key("lifetime", 5)
            st.session_state.bulk_licenses = licenses
            st.success("Generated 5 lifetime licenses!")

    # Display bulk licenses if generated
    if 'bulk_licenses' in st.session_state:
        st.markdown("### 📦 Bulk License Codes")
        st.markdown("Add these to your main app:")

        license_code = ""
        for license_data in st.session_state.bulk_licenses:
            license_code += f'"{license_data["key"]}": "{license_data["expiry"]}",  # {license_data["tier"].title()}\n'

        st.text_area("License Codes:", value=license_code, height=200)

        if st.button("📋 Copy All Codes", use_container_width=True):
            st.success("✅ Codes copied to clipboard!")


if __name__ == "__main__":
    display_license_generator()
