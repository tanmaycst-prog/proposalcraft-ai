import streamlit as st
from openai import OpenAI

# Page config
st.set_page_config(
    page_title="ProposalCraft AI",
    page_icon="🚀",
    layout="centered"
)

# Header
st.title("🚀 ProposalCraft AI")
st.markdown("Generate winning freelance proposals in seconds")

# Input section
job_post = st.text_area("Paste the job posting:", height=120,
                        placeholder="Copy and paste the entire job description here...")
job_req = st.text_area("Paste the Skills Required:", height=30,
                        placeholder="Copy and paste the entire Skills Required here...")
skills = st.text_input("Your top 3 relevant skills:", placeholder="e.g., Python, React, UI/UX Design")
advantage = st.text_input("Your unique advantage:", placeholder="What makes you stand out from other applicants?")
openai_key = "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"

# Add some styling
st.markdown("""
<style>
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

if st.button("✨ Generate Proposal", type="primary", use_container_width=True):
    if not all([job_post, job_req, skills, advantage, openai_key]):
        st.error("Please fill in all fields above!")
    else:
        try:
            client = OpenAI(api_key=openai_key)

            with st.spinner("🤖 AI is crafting your perfect proposal..."):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system",
                         "content": "You are an expert freelance proposal writer. Create compelling, personalized proposals that help freelancers win projects."},
                        {"role": "user", "content": f"""
                        JOB POSTING: {job_post}
                        Skills Required: {job_req}
                        FREELANCER SKILLS: {skills}
                        UNIQUE ADVANTAGE: {advantage}

                        Create:
                        1. A personalized proposal addressing the client's needs
                        2. Two follow-up email templates
                        3. Three relevant portfolio bullet points

                        Make it specific, professional, and results-focused.
                        """}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )

                content = response.choices[0].message.content

            st.success("✅ Proposal Generated!")
            st.subheader("Your Custom Proposal")
            st.write(content)

            # Copy button functionality
            st.code(content, language=None)

        except Exception as e:
            error_msg = str(e)
            if "invalid api key" in error_msg.lower():
                st.error("❌ Invalid API key. Please check and try again.")
            elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
                st.error("💳 API quota exceeded. Please set up billing at https://platform.openai.com/billing")
            else:
                st.error(f"⚠️ Error: {error_msg}")

# Footer with instructions
st.markdown("---")
with st.expander("📚 How to get started"):
    st.markdown("""
    1. **Use the tool:**
       - Paste any freelance job posting along with required skills
       - Fill in your skills and advantage
       - Paste your API key
       - Click "Generate Proposal"

    2. Proposal is generated with GPT-3.5 Turbo
    """)

st.caption("Built with ❤️ for freelancers | v1.0")