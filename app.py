import streamlit as st
from openai import OpenAI
import os

# Page config
st.set_page_config(page_title="ProposalCraft AI", page_icon="🚀")

# Header
st.title("🚀 ProposalCraft AI")
st.markdown("Get more freelance clients with AI-powered proposals")

# Input section
st.subheader("📝 Tell me about the job")

job_post = st.text_area("Paste the job posting here:", height=150)

col1, col2 = st.columns(2)

with col1:
    skills = st.text_input("Your top 3 relevant skills:")
    advantage = st.text_input("Your unique advantage:")

with col2:
    requirements = st.text_input("Specific requirements to highlight:")
    #openai_key = st.text_input("Your OpenAI API key:", type="password", placeholder="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")

# Add model selection
model_choice = st.selectbox(
    "Select AI Model:",
    ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
    index=0,
    help="GPT-3.5 is cheapest, GPT-4 is highest quality"
)

# Generate button
if st.button("✨ Generate Proposal", type="primary"):
    if not all([job_post, skills, advantage]):
        st.error("Please fill in all fields!")
    else:
        try:
            # Initialize OpenAI client with user's API key
            client = OpenAI(api_key="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")

            # System prompt
            system_prompt = """You are an expert freelance proposal writer. Your goal is to help freelancers win more projects by creating compelling, personalized proposals that stand out."""

            # User prompt
            user_prompt = f"""
            JOB POSTING:
            {job_post}

            FREELANCER INFORMATION:
            - Relevant Skills: {skills}
            - Unique Advantage: {advantage}  
            - Key Requirements: {requirements}

            Please generate:
            1. A COMPELLING PROPOSAL that addresses the client's needs and highlights the freelancer's specific qualifications
            2. TWO FOLLOW-UP EMAIL templates (3-5 days after no response, 7-10 days after no response)
            3. THREE PORTFOLIO BULLET SUGGESTIONS that would be most relevant to this client

            Format the response clearly with headings for each section.

            Make it personal, specific, and focused on client results.
            """

            with st.spinner("Crafting your winning proposal..."):
                response = client.chat.completions.create(
                    model=model_choice,  # Use the selected model
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )

                content = response.choices[0].message.content

                # Display results
                st.success("✅ Proposal generated!")

                st.subheader("📄 Your Custom Proposal")
                st.write(content)

                # Copy to clipboard functionality
                st.code(content, language=None)

        except Exception as e:
            error_msg = str(e)
            if "invalid model ID" in error_msg:
                st.error(f"""
                **Model Error**: The selected model '{model_choice}' is not available.

                **Quick Fixes:**
                - Try selecting 'gpt-3.5-turbo' (most reliable)
                - Check if your API key has access to the selected model
                - Some models like GPT-4 require manual approval

                **Available Models for Most Accounts:**
                - `gpt-3.5-turbo` ✅ (recommended)
                - `gpt-4` ⚠️ (may require approval)
                - `gpt-4-turbo-preview` ⚠️ (may require approval)
                """)
            elif "quota" in error_msg or "429" in error_msg or "insufficient_quota" in error_msg:
                st.error("""
                **API Key Issue Detected**

                This usually means:
                - Your OpenAI account has no credits left
                - You haven't set up billing
                - You've exceeded usage limits

                **How to fix:**
                1. Go to https://platform.openai.com/account/billing/overview
                2. Set up billing and add payment method
                3. Generate a new API key at https://platform.openai.com/api-keys
                4. Try again with the new key
                """)
            else:
                st.error(f"Error generating proposal: {error_msg}")

# Footer with expanded instructions
st.markdown("---")
st.markdown("### 🔧 Setup Instructions")

with st.expander("How to get and set up your OpenAI API key"):
    st.markdown("""
    1. **Create account** at https://platform.openai.com/
    2. **Set up billing** at https://platform.openai.com/account/billing/overview
    3. **Add payment method** (required - costs are minimal)
    4. **Create API key** at https://platform.openai.com/api-keys
    5. **Copy and paste** your key above (starts with `sk-`)

    **Cost Note:** Each proposal costs ~$0.002 with GPT-3.5 Turbo
    """)

with st.expander("Model Access Information"):
    st.markdown("""
    **Model Availability:**
    - **GPT-3.5 Turbo**: Available to all accounts ✅
    - **GPT-4**: May require manual approval and higher usage limits
    - **GPT-4 Turbo**: Same as GPT-4 access requirements

    **For testing, use GPT-3.5 Turbo** - it's fast, cheap, and works great for proposals.
    """)