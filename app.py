import os
import io
import json
import time
import re
from datetime import datetime, date, timedelta
import streamlit as st

# -------------------------------
# Conditional Imports (Robust Check)
# -------------------------------
PYPDF_AVAILABLE = False
try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    pass

DOCX_AVAILABLE = False
try:
    import docx

    DOCX_AVAILABLE = True
except ImportError:
    pass

OPENAI_SDK_AVAILABLE = False
try:
    from openai import OpenAI

    OPENAI_SDK_AVAILABLE = True
except ImportError:
    pass

MONGODB_AVAILABLE = False
try:
    import pymongo

    MONGODB_AVAILABLE = True
except ImportError:
    pass

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="ProposalCraft AI - Win More Projects",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------
# Modern CSS Styling (Updated Footer Fix)
# -------------------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght+400;500;600;700&display=swap" rel="stylesheet">
<style>
    /* Global Styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide Streamlit branding and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp > footer {visibility: hidden !important;}

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #8b5cf6, #06b6d4);
        border-radius: 10px;
    }

    /* Logo Styles */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }

    .logo-icon {
        width: 56px;
        height: 56px;
        background: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 50%, #10b981 100%);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        color: white;
        font-weight: 800;
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.35);
        animation: pulse-glow 3s ease-in-out infinite;
    }

    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 8px 32px rgba(139, 92, 246, 0.35); }
        50% { box-shadow: 0 8px 48px rgba(6, 182, 212, 0.45); }
    }

    .logo-text {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 26px;
        font-weight: 700;
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .logo-tagline {
        font-size: 13px;
        color: #64748b;
        font-weight: 500;
        letter-spacing: 0.5px;
    }

    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, 
            rgba(139, 92, 246, 0.08) 0%, 
            rgba(6, 182, 212, 0.06) 50%,
            rgba(16, 185, 129, 0.04) 100%);
        border-radius: 24px;
        padding: 32px;
        margin-bottom: 24px;
        border: 1px solid rgba(139, 92, 246, 0.15);
        position: relative;
        overflow: hidden;
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(6, 182, 212, 0.1) 0%, transparent 70%);
        animation: float 8s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% { transform: translate(0, 0); }
        50% { transform: translate(-20px, 20px); }
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 36px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 12px;
        line-height: 1.2;
    }

    .hero-subtitle {
        font-size: 18px;
        color: #475569;
        margin-bottom: 24px;
        line-height: 1.6;
    }

    .hero-stats {
        display: flex;
        gap: 32px;
        margin-top: 24px;
    }

    .stat-item {
        text-align: center;
    }

    .stat-number {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 28px;
        font-weight: 700;
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .stat-label {
        font-size: 13px;
        color: #64748b;
        font-weight: 500;
    }

    /* Glass Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }

    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
    }

    /* Premium Card */
    .premium-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border-radius: 20px;
        padding: 24px;
        color: white;
        position: relative;
        overflow: hidden;
    }

    .premium-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.4) 0%, transparent 70%);
    }

    /* Feature Badge */
    .feature-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(6, 182, 212, 0.1));
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        color: #7c3aed;
        border: 1px solid rgba(139, 92, 246, 0.2);
    }

    /* CTA Button */
    .cta-button {
        background: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%);
        color: white;
        padding: 14px 28px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 15px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.35);
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }

    .cta-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(139, 92, 246, 0.45);
    }

    /* Secondary Button */
    .secondary-button {
        background: white;
        color: #7c3aed;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 14px;
        border: 2px solid #e9d5ff;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .secondary-button:hover {
        background: #faf5ff;
        border-color: #c4b5fd;
    }

    /* Pricing Cards */
    .pricing-card {
        background: white;
        border-radius: 20px;
        padding: 28px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
        position: relative;
    }

    .pricing-card:hover {
        border-color: #c4b5fd;
        transform: translateY(-4px);
        box-shadow: 0 20px 40px rgba(139, 92, 246, 0.15);
    }

    .pricing-card.popular {
        border-color: #8b5cf6;
        box-shadow: 0 20px 40px rgba(139, 92, 246, 0.2);
    }

    .popular-badge {
        position: absolute;
        top: -12px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .price-amount {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 42px;
        font-weight: 700;
        color: #0f172a;
    }

    .price-period {
        font-size: 16px;
        color: #64748b;
        font-weight: 500;
    }

    /* Testimonial Card */
    .testimonial-card {
        background: linear-gradient(135deg, #faf5ff 0%, #f0f9ff 100%);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #e9d5ff;
    }

    .testimonial-text {
        font-size: 15px;
        color: #334155;
        line-height: 1.7;
        font-style: italic;
    }

    .testimonial-author {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 16px;
    }

    .author-avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 16px;
    }

    /* Email Capture */
    .email-capture {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #0f172a 100%);
        border-radius: 24px;
        padding: 40px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .email-capture::before {
        content: '';
        position: absolute;
        top: -100px;
        right: -100px;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.3) 0%, transparent 70%);
    }

    .email-capture::after {
        content: '';
        position: absolute;
        bottom: -100px;
        left: -100px;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(6, 182, 212, 0.3) 0%, transparent 70%);
    }

    /* Progress Bar */
    .usage-progress {
        height: 8px;
        background: #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
        margin: 8px 0;
    }

    .usage-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #8b5cf6, #06b6d4);
        border-radius: 10px;
        transition: width 0.5s ease;
    }

    /* Sidebar Styles */
    .sidebar-section {
        background: rgba(255, 255, 255, 0.6);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 16px;
        border: 1px solid #e2e8f0;
    }

    .sidebar-title {
        font-size: 13px;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
    }

    /* Urgency Banner */
    .urgency-banner {
        background: linear-gradient(90deg, #fef3c7, #fde68a);
        border: 1px solid #f59e0b;
        border-radius: 12px;
        padding: 12px 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .urgency-text {
        color: #92400e;
        font-weight: 600;
        font-size: 14px;
    }

    /* Success Message */
    .success-message {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        border: 1px solid #10b981;
        border-radius: 12px;
        padding: 16px 20px;
        color: #065f46;
        font-weight: 500;
    }

    /* Tab Styles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f1f5f9;
        padding: 6px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    /* Input Styles */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 12px 16px;
        font-size: 15px;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
    }

    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 12px 16px;
        font-size: 15px;
    }

    .stTextArea > div > div > textarea:focus {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
    }

    /* Select Box */
    .stSelectbox > div > div {
        border-radius: 12px;
    }

    /* Button Styles */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        border: none;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #f8fafc;
        border-radius: 12px;
        font-weight: 600;
    }

    /* Metric Styles */
    [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Footer Styles - Custom */
    .custom-footer {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 16px;
        padding: 24px;
        margin-top: 40px;
        text-align: center;
        border: 1px solid #e2e8f0;
        position: relative;
        z-index: 100;
    }

    .footer-links {
        display: flex;
        justify-content: center;
        gap: 24px;
        margin-top: 12px;
    }

    .footer-link {
        color: #64748b;
        text-decoration: none;
        font-size: 14px;
        font-weight: 500;
        transition: color 0.3s ease;
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 6px;
    }

    .footer-link:hover {
        color: #8b5cf6;
        background-color: rgba(139, 92, 246, 0.1);
    }

    /* Plan Activation Styles */
    .plan-feature-list {
        list-style: none;
        padding: 0;
        margin: 20px 0;
    }

    .plan-feature-list li {
        padding: 8px 0;
        color: #475569;
        display: flex;
        align-items: flex-start;
        gap: 8px;
        font-size: 15px;
    }

    .plan-feature-list li:before {
        content: "✓";
        color: #10b981;
        font-weight: bold;
        font-size: 18px;
    }
    /* Affiliate Link Styles */
    .affiliate-guidelines-link {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 8px 16px;
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.1), rgba(2, 132, 199, 0.1));
        border-radius: 10px;
        color: #0ea5e9;
        text-decoration: none;
        font-weight: 500;
        font-size: 14px;
        border: 1px solid rgba(14, 165, 233, 0.2);
        transition: all 0.3s ease;
    }

    .affiliate-guidelines-link:hover {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.2), rgba(2, 132, 199, 0.2));
        border-color: rgba(14, 165, 233, 0.4);
        color: #0284c7;
    }
</style>
""", unsafe_allow_html=True)

PAYMENT_LINKS = {
    "monthly": "https://buymeacoffee.com/karmyt007/membership",
    "yearly": "https://buymeacoffee.com/karmyt007/membership",
    "lifetime": "https://buymeacoffee.com/karmyt007/membership",
    "coffee": "https://buymeacoffee.com/karmyt007",
    "donate": "https://buymeacoffee.com/karmyt007"
}

# Tally form URL - replace with your actual Tally form
TALLY_CONTACT_FORM = "https://tally.so/r/kddPqj"

# Awin affiliate links
AWIN_AFFILIATE_LINKS = {
    "NordVPN": "http://www.awin1.com/cread.php?awinmid=15132&awinaffid=2668764&clickref="
}

# Affiliate Marketing Guidelines Link
AFFILIATE_GUIDELINES_LINK = "http://paidforadvertising.com/"

# -------------------------------
# MongoDB Connection Setup
# -------------------------------
def init_mongodb_connection():
    """Initialize MongoDB connection using Streamlit secrets"""
    try:
        if not MONGODB_AVAILABLE:
            st.warning("MongoDB not available. Install: `pip install pymongo`")
            return None

        # Check if secrets are configured
        if "mongo" in st.secrets:
            mongo_secrets = st.secrets["mongo"]
            connection_string = f"mongodb+srv://{mongo_secrets['username']}:{mongo_secrets['password']}@{mongo_secrets['host']}/?retryWrites=true&w=majority"
            client = pymongo.MongoClient(connection_string)

            # Test connection
            client.admin.command('ping')
            return client
        else:
            # For local development without secrets
            st.info("MongoDB secrets not configured. Using local session storage.")
            return None
    except Exception as e:
        st.warning(f"MongoDB connection failed: {e}. Using session storage.")
        return None


# Initialize MongoDB client
mongo_client = init_mongodb_connection()


def save_email_to_mongodb(email_data):
    """Save email data to MongoDB collection"""
    try:
        if mongo_client:
            db = mongo_client["proposalcraft_db"]
            collection = db["leads"]

            # Insert the document
            result = collection.insert_one(email_data)
            return result.inserted_id
        else:
            # Fallback to session state
            if 'leads_collected' not in st.session_state:
                st.session_state.leads_collected = []
            st.session_state.leads_collected.append(email_data)
            return f"session_{len(st.session_state.leads_collected)}"
    except Exception as e:
        st.error(f"Error saving to MongoDB: {e}")
        # Fallback to session state
        if 'leads_collected' not in st.session_state:
            st.session_state.leads_collected = []
        st.session_state.leads_collected.append(email_data)
        return f"session_{len(st.session_state.leads_collected)}"


# -------------------------------
# Constants and Configuration
# -------------------------------
VALID_LICENSES = {
    "TRIAL-7DAY-DEMO": "2026-01-05",
    "MONTHLY-2025-JICHP8": "2026-01-27",
    "YEARLY-2025-7N7FWG": "2026-12-27",
    "LIFETIME-2025-WF5SFN": "2099-12-31",
}

LICENSE_TIERS = {
    'free': {
        'daily_limit': 3,
        'features': ['Basic proposals', 'Platform templates', '3 proposals/day', 'Export options'],
        'price': 'Free',
        'price_value': 0,
        'button_text': 'Start Free',
        'button_action': 'activate_free'
    },
    'trial': {
        'daily_limit': 10,
        'features': ['All free features', 'Resume integration', 'Proposal history', '10 proposals/day'],
        'price': 'Free 7-day trial',
        'price_value': 0,
        'button_text': 'Start Trial',
        'button_action': 'activate_trial'
    },
    'monthly': {
        'daily_limit': 100,
        'features': ['Unlimited proposals', 'Resume library', 'Proposal analytics', 'Priority support',
                     'Export options', 'API access'],
        'price': '$9.99/month',
        'price_value': 9.99,
        'button_text': 'Get Monthly',
        'button_action': 'upgrade_monthly'
    },
    'yearly': {
        'daily_limit': 100,
        'features': ['All monthly features', 'Save 23%', 'Advanced templates', 'A/B testing', 'API access'],
        'price': '$99/year',
        'price_value': 99,
        'button_text': 'Get Yearly',
        'button_action': 'upgrade_yearly'
    },
    'lifetime': {
        'daily_limit': 1000,
        'features': ['Everything included', 'Lifetime updates', 'White-label option', 'API access',
                     'Priority support forever', 'Unlimited everything'],
        'price': '$199/Lifetime',
        'price_value': 199,
        'button_text': 'Get Lifetime',
        'button_action': 'upgrade_lifetime'
    }
}

PLATFORM_PROMPTS = {
    "Upwork": "You are an expert in crafting Upwork proposals optimized for conversions, brevity, and clarity. Focus on addressing the client's specific needs, showcasing relevant experience, and including a clear call-to-action.",
    "Fiverr": "You specialize in Fiverr gig proposals that are concise, benefit-driven, and tailored to client needs. Emphasize quick delivery, value, and your unique selling points.",
    "Direct Client": "You write direct client outreach proposals that build trust, show results, and offer clear next steps. Focus on ROI, case studies, and professional tone.",
    "LinkedIn": "You craft LinkedIn outreach messages and proposals with a professional, warm tone and a clear CTA. Keep it conversational yet business-focused.",
    "Generic": "You write winning proposals for freelance jobs with concrete examples, quantified results, and client-centric framing. Be specific, professional, and persuasive.",
}

# -------------------------------
# Session State Initialization
# -------------------------------
default_state = {
    'proposal_history': [],
    'current_proposal': "",
    'resume_text': "",
    'usage_count': 0,
    'last_reset_date': str(date.today()),
    'premium_user': False,
    'license_key': "",
    'license_tier': 'free',
    'success_metrics': {
        'proposals_generated': 0,
        'time_saved_minutes': 0,
        'first_use_date': str(date.today())
    },
    'onboarding_complete': False,
    'show_upgrade_modal': False,
    'show_privacy': False,
    'show_terms': False,
    'show_contact': False,
    'cookie_consent': False,
    'cookie_preferences': {
        'essential': True,
        'analytics': False,
        'preferences': False
    },
    'show_cookie_settings': False,
    'terms_accepted': False,
    'show_data_export': False,
    'show_delete_account': False,
    'show_resume_manager': False,
    'resume_library': {},
    'active_resume_id': None,
    'resume_counter': 0,
    'user_email': "",
    'email_verified': False,
    'show_email_capture': True,
    'leads_collected': [],
    'plan_activation_status': 'free',  # Track current active plan
    'plan_expiry_date': None,  # For trial/paid plans
}

for k, v in default_state.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Reset daily usage
if st.session_state.last_reset_date != str(date.today()):
    st.session_state.usage_count = 0
    st.session_state.last_reset_date = str(date.today())


# -------------------------------
# Utility Functions
# -------------------------------
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def add_resume_to_library(name, text):
    st.session_state.resume_counter += 1
    resume_id = f"resume_{st.session_state.resume_counter}"
    st.session_state.resume_library[resume_id] = {
        'id': resume_id,
        'name': name,
        'text': text,
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'character_count': len(text)
    }
    st.session_state.active_resume_id = resume_id
    return resume_id


def get_active_resume():
    rid = st.session_state.active_resume_id
    if rid and rid in st.session_state.resume_library:
        return st.session_state.resume_library[rid]
    return None


def delete_resume_from_library(resume_id):
    if resume_id in st.session_state.resume_library:
        del st.session_state.resume_library[resume_id]
        if st.session_state.active_resume_id == resume_id:
            st.session_state.active_resume_id = next(iter(st.session_state.resume_library), None)


def extract_text_from_pdf(uploaded_file):
    if not PYPDF_AVAILABLE:
        st.error("📦 Please install pypdf: `pip install pypdf`")
        return None
    try:
        pdf_reader = pypdf.PdfReader(io.BytesIO(uploaded_file.getvalue()))
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text() or ""
            text += extracted + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"❌ Error reading PDF: {str(e)}")
        return None


def extract_text_from_docx(uploaded_file):
    if not DOCX_AVAILABLE:
        st.error("📦 Please install python-docx: `pip install python-docx`")
        return None
    try:
        doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        st.error(f"❌ Error reading DOCX: {str(e)}")
        return None


def extract_text_from_txt(uploaded_file):
    try:
        return uploaded_file.getvalue().decode("utf-8").strip()
    except Exception as e:
        st.error(f"❌ Error reading text: {str(e)}")
        return None


def process_uploaded_resume(uploaded_file):
    file_type = uploaded_file.type
    with st.spinner(f"📄 Processing {uploaded_file.name}..."):
        if file_type == "application/pdf":
            return extract_text_from_pdf(uploaded_file)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return extract_text_from_docx(uploaded_file)
        elif file_type == "text/plain":
            return extract_text_from_txt(uploaded_file)
        else:
            st.error(f"❌ Unsupported file type: {file_type}")
            return None


def determine_license_tier(license_key):
    if not license_key:
        return 'free'
    k = license_key.strip().upper()
    if k.startswith("TRIAL-"): return 'trial'
    if k.startswith("MONTHLY-"): return 'monthly'
    if k.startswith("YEARLY-"): return 'yearly'
    if k.startswith("LIFETIME-"): return 'lifetime'
    return 'free'


def check_license_key(license_key):
    if not license_key:
        return False
    key = license_key.strip().upper()
    if key in VALID_LICENSES:
        try:
            expiry = datetime.strptime(VALID_LICENSES[key], "%Y-%m-%d")
            if datetime.now() < expiry:
                st.session_state.license_tier = determine_license_tier(key)
                st.session_state.premium_user = st.session_state.license_tier in ['trial', 'monthly', 'yearly',
                                                                                  'lifetime']
                st.session_state.license_key = key
                st.session_state.plan_activation_status = st.session_state.license_tier
                st.session_state.plan_expiry_date = VALID_LICENSES[key]
                return True
        except ValueError:
            return False
    return False


def get_current_limit():
    return LICENSE_TIERS.get(st.session_state.license_tier, LICENSE_TIERS['free'])['daily_limit']


def can_generate_proposal():
    return st.session_state.usage_count < get_current_limit()


def track_success_metrics():
    st.session_state.success_metrics['proposals_generated'] += 1
    st.session_state.success_metrics['time_saved_minutes'] += 15


def generate_pdf_content(content, title, content_type):
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ 
            font-family: 'Inter', 'Segoe UI', Arial, sans-serif; 
            color: #1e293b; 
            padding: 48px; 
            max-width: 800px; 
            margin: auto; 
            line-height: 1.7;
        }}
        .header {{ 
            text-align: center; 
            border-bottom: 3px solid #8b5cf6; 
            padding-bottom: 24px; 
            margin-bottom: 32px; 
        }}
        .header h1 {{ 
            color: #0f172a; 
            margin: 0; 
            font-size: 28px;
            font-weight: 700;
        }}
        .content {{ 
            white-space: pre-wrap; 
            font-size: 15px; 
            line-height: 1.8; 
            color: #334155; 
        }}
        .metadata {{ 
            background: linear-gradient(135deg, #f5f3ff, #ecfeff); 
            padding: 16px 20px; 
            border-radius: 12px; 
            margin-bottom: 24px; 
            color: #475569;
            border: 1px solid #e9d5ff;
        }}
        .footer {{ 
            margin-top: 40px; 
            font-size: 13px; 
            color: #94a3b8; 
            text-align: center;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>✨ {title}</h1>
        <p style="color:#64748b; margin-top:8px;">Generated by ProposalCraft AI</p>
    </div>
    <div class="metadata">
        <strong>Type:</strong> {content_type} &nbsp;•&nbsp; <strong>Generated:</strong> {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
    </div>
    <div class="content">{content}</div>
    <div class="footer">
        <p>🚀 Created with ProposalCraft AI — Win more projects faster</p>
    </div>
</body>
</html>
"""
    return html_content


def export_user_data_json():
    user_data = {
        'export_date': str(datetime.now()),
        'account_info': {
            'email': st.session_state.user_email,
            'license_tier': st.session_state.license_tier,
            'license_key': st.session_state.license_key if st.session_state.premium_user else None,
            'first_use_date': st.session_state.success_metrics['first_use_date'],
            'plan_activation_status': st.session_state.plan_activation_status,
            'plan_expiry_date': st.session_state.plan_expiry_date,
        },
        'usage_statistics': {
            'proposals_generated': st.session_state.success_metrics['proposals_generated'],
            'time_saved_minutes': st.session_state.success_metrics['time_saved_minutes'],
            'usage_count_today': st.session_state.usage_count,
        },
        'proposal_history': st.session_state.proposal_history,
        'resume_library': st.session_state.resume_library,
        'active_resume_id': st.session_state.active_resume_id,
        'cookie_preferences': st.session_state.cookie_preferences,
    }
    return json.dumps(user_data, indent=2)


def delete_all_user_data():
    keys_to_keep = ['show_privacy', 'show_terms', 'show_contact']
    keys_to_delete = [key for key in list(st.session_state.keys()) if key not in keys_to_keep]

    for key in keys_to_delete:
        del st.session_state[key]

    for k, v in default_state.items():
        st.session_state[k] = v


def activate_plan(plan_type):
    """Activate a specific plan"""
    if plan_type == 'free':
        st.session_state.license_tier = 'free'
        st.session_state.premium_user = False
        st.session_state.plan_activation_status = 'free'
        st.session_state.plan_expiry_date = None
        return "free_activated"

    elif plan_type == 'trial':
        # For demo purposes - in real app, this would check Stripe/backend
        st.session_state.license_tier = 'trial'
        st.session_state.premium_user = True
        st.session_state.plan_activation_status = 'trial'
        st.session_state.plan_expiry_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        return "trial_activated"

    elif plan_type == 'lifetime':
        # For demo purposes - in real app, this would require payment
        st.session_state.license_tier = 'lifetime'
        st.session_state.premium_user = True
        st.session_state.plan_activation_status = 'lifetime'
        st.session_state.plan_expiry_date = "2099-12-31"
        return "lifetime_activated"

    elif plan_type == 'monthly':
        st.session_state.license_tier = 'monthly'
        st.session_state.premium_user = True
        st.session_state.plan_activation_status = 'monthly'
        st.session_state.plan_expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        return "monthly_activated"

    elif plan_type == 'yearly':
        st.session_state.license_tier = 'yearly'
        st.session_state.premium_user = True
        st.session_state.plan_activation_status = 'yearly'
        st.session_state.plan_expiry_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        return "yearly_activated"

    return None


# -------------------------------
# Logo Component
# -------------------------------
def render_logo():
    st.markdown("""
    <div class="logo-container">
        <div class="logo-icon">P</div>
        <div>
            <div class="logo-text">ProposalCraft AI</div>
            <div class="logo-tagline">Win more projects, faster</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# -------------------------------
# Email Capture Modal (Updated with MongoDB)
# -------------------------------
def render_email_capture():
    if not st.session_state.email_verified and st.session_state.show_email_capture:
        st.markdown("""
        <div class="email-capture">
            <div style="position: relative; z-index: 1;">
                <h2 style="color: white; font-family: 'Space Grotesk', sans-serif; font-size: 32px; margin-bottom: 12px;">
                    🚀 Accelerate Your Career
                </h2>
                <p style="color: #cbd5e1; font-size: 16px; margin-bottom: 24px;">
                    Get 3 FREE proposals & job applications every day + exclusive tips to boost your success rate
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            email = st.text_input(
                "Email address",
                placeholder="you@example.com",
                key="email_input",
                label_visibility="collapsed"
            )

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🎉 Get Free Access", use_container_width=True, type="primary"):
                    if email and validate_email(email):
                        st.session_state.user_email = email
                        st.session_state.email_verified = True
                        st.session_state.show_email_capture = False

                        # Save to MongoDB
                        email_data = {
                            'email': email,
                            'timestamp': datetime.now().isoformat(),
                            'source': 'email_capture',
                            'plan': 'free',
                            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'user_agent': "Streamlit App"
                        }

                        save_email_to_mongodb(email_data)
                        st.success("✅ Welcome! You now have 3 free proposals per day.")
                        st.rerun()
                    else:
                        st.error("Please enter a valid email address")

            with col_btn2:
                if st.button("I have a license key", use_container_width=True):
                    st.session_state.show_email_capture = False
                    st.session_state.email_verified = True
                    st.rerun()

        st.markdown("""
        <div style="text-align: center; margin-top: 16px;">
            <p style="color: #64748b; font-size: 13px;">
                🔒 We respect your privacy. No spam, ever. Unsubscribe anytime.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return True
    return False


# -------------------------------
# Pricing Section (Updated with working plans)
# -------------------------------
def render_pricing():
    st.markdown("""
    <h2 style="text-align: center; font-family: 'Space Grotesk', sans-serif; font-size: 32px; margin-bottom: 8px;">
        💎 All-in-One Career Platform
    </h2>
    <p style="text-align: center; color: #64748b; margin-bottom: 32px;">
        Get unlimited proposals AND job applications. Join 12,000+ professionals accelerating their careers
    </p>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    plans = [
        ('free', '🆓', '#64748b'),
        ('monthly', '⭐', '#8b5cf6'),
        ('lifetime', '👑', '#f59e0b')
    ]

    for col, (plan, icon, color) in zip(cols, plans):
        details = LICENSE_TIERS[plan]
        is_popular = plan == 'monthly'
        is_current_plan = st.session_state.plan_activation_status == plan

        with col:
            badge_html = '<div class="popular-badge">MOST POPULAR</div>' if is_popular else '<div></div>'

            if is_current_plan:
                badge_html += '<div style="position: absolute; top: 40px; right: 20px; background: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">ACTIVE</div>'

            # --- FEATURES HTML (DEFINE FIRST) ---
            features_html = "".join([
                f"""<li style="padding:8px 0; color:#475569; display:flex; gap:8px;"><span style="color:#10b981;">✓</span>{f}</li>"""
                for f in details["features"]
            ])

            price_text = details["price"]

            if price_text.lower() == "free":
                price_amount_text = "Free"
                price_period_text = ""
            elif "trial" in price_text.lower():
                price_amount_text = "Free"
                price_period_text = "7-day trial"
            elif "Lifetime" in price_text.lower():
                price_amount_text = price_text.split(" ")[0]
                price_period_text = "Lifetime"
            elif "/" in price_text:
                price_amount_text, price_period_text = price_text.split("/", 1)
            else:
                price_amount_text = price_text
                price_period_text = ""

            st.markdown(f"""
            <div class="pricing-card {'popular' if is_popular else ''}">
                {badge_html}
                <div style="text-align:center; margin-bottom:20px;">
                    <span style="font-size:40px;">{icon}</span>
                    <h3 style="margin:12px 0 4px; font-size:22px;">{plan.capitalize()}</h3>
                    <div class="price-amount">{price_amount_text}</div>
                    <div class="price-period">{price_period_text}</div>
                </div>
                <ul style="list-style:none; padding:0; margin:20px 0;">{features_html}</ul>
            </div>
            """, unsafe_allow_html=True)

            btn_type = "primary" if is_popular else "secondary"
            btn_text = "✅ Current Plan" if is_current_plan else details['button_text']

            if not is_current_plan:
                if plan in ['monthly', 'yearly', 'lifetime']:
                    # For paid plans, use external payment link
                    st.markdown(f"""
                    <a href="{PAYMENT_LINKS[plan]}" target="_blank" style="text-decoration: none;">
                        <button style="
                            width: 100%;
                            background: linear-gradient(135deg, #8b5cf6, #06b6d4);
                            color: white;
                            padding: 14px 28px;
                            border-radius: 12px;
                            font-weight: 600;
                            font-size: 15px;
                            border: none;
                            cursor: pointer;
                            transition: all 0.3s ease;
                            box-shadow: 0 4px 20px rgba(139, 92, 246, 0.35);
                            display: inline-flex;
                            align-items: center;
                            justify-content: center;
                            gap: 8px;
                        ">
                            💳 {details['button_text']}
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
                else:
                    # For free and trial plans, use internal activation
                    if st.button(btn_text, key=f"pricing_{plan}", use_container_width=True, type=btn_type):
                        result = activate_plan(plan)
                        if result == "free_activated":
                            st.success("✅ Free plan activated! You now have 3 proposals per day.")
                        elif result == "trial_activated":
                            st.success("🎉 7-day trial activated! You now have 10 proposals per day.")
                        time.sleep(1)
                        st.rerun()
            else:
                st.button(btn_text, key=f"current_{plan}", use_container_width=True, disabled=True)

# -------------------------------
# Affiliate Section
# -------------------------------
def render_affiliate_section():

    st.markdown("""
    <h2 style="text-align: center; font-family: 'Space Grotesk', sans-serif; font-size: 28px; margin: 40px 0 24px 0;">
        🎁 Recommended Tools & Services
    </h2>
    <p style="text-align: center; color: #475569; margin-bottom: 32px; font-size: 16px;">
        Boost your freelance and Job application career with these trusted tools<br>
        <span style="font-size: 14px; color: #64748b;">(We may earn a commission from purchases - supports our free tool!)</span>
    </p>
    """, unsafe_allow_html=True)

    affiliate_products = [
        {
            'name': 'NordVPN',
            'description': 'Secure your internet connection and protect your privacy online',
            'icon': '🛡️',
            'color': '#4c6ef5',  # NordVPN blue
            'link': AWIN_AFFILIATE_LINKS['NordVPN'],
            'discount': '73% OFF'
        }
    ]

    cols = st.columns(2)
    for idx, product in enumerate(affiliate_products):
        with cols[idx % 2]:
            discount_badge = f'<div style="position: absolute; top: 12px; right: 12px; background: linear-gradient(135deg, {product["color"]}, {product["color"]}cc); color: white; padding: 4px 8px; border-radius: 8px; font-size: 11px; font-weight: 600;">{product["discount"]}</div>' if 'discount' in product else ''

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {product['color']}15, {product['color']}05); border-radius: 16px; padding: 20px; border: 1px solid {product['color']}30; margin-bottom: 16px; position: relative;">
                {discount_badge}
                <div style="display: flex; align-items: flex-start; gap: 12px;">
                    <div style="background: linear-gradient(135deg, {product['color']}, {product['color']}cc); color: white; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;">
                        {product['icon']}
                    </div>
                    <div style="flex: 1;">
                        <h4 style="margin: 0; color: #0f172a; font-weight: 600;">{product['name']}</h4>
                        <p style="margin: 4px 0; color: #475569; font-size: 14px;">{product['description']}</p>
                    </div>
                </div>
                <a href="{product['link']}" target="_blank" style="text-decoration: none;">
                    <button style="
                        width: 100%;
                        background: linear-gradient(135deg, {product['color']}, {product['color']}cc);
                        color: white;
                        padding: 10px 16px;
                        border-radius: 10px;
                        font-weight: 600;
                        font-size: 14px;
                        border: none;
                        cursor: pointer;
                        margin-top: 12px;
                        transition: all 0.3s ease;
                    ">
                        Get Deal →
                    </button>
                </a>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin-top: 8px; padding: 12px; background: linear-gradient(135deg, #f8fafc, #f1f5f9); border-radius: 12px; border: 1px solid #e2e8f0;">
        <p style="font-size: 13px; color: #64748b; margin: 0;">
            💡 <strong>Disclaimer:</strong> These are affiliate links. When you purchase through our links, 
            we earn a small commission at no extra cost to you. This helps us keep ProposalCraft AI free for everyone!
        </p>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# Testimonials Section
# -------------------------------
def render_testimonials():
    st.markdown("""
    <h2 style="text-align: center; font-family: 'Space Grotesk', sans-serif; font-size: 28px; margin: 40px 0 24px 0;">
        💬 Loved by Freelancers & Job Seekers
    </h2>
    """, unsafe_allow_html=True)

    testimonials = [
        {
            'text': '"ProposalCraft AI helped me increase my Upwork win rate from 5% to 23%. I went from struggling to getting 3-4 clients per week!"',
            'author': 'Sarah M.',
            'role': 'Web Developer',
            'initials': 'SM',
            'stat': '4.6x more clients',
            'type': 'freelance'
        },
        {
            'text': '"I landed my dream remote job in just 2 weeks using the job application feature! The cover letters were perfectly tailored."',
            'author': 'Michael T.',
            'role': 'Marketing Manager',
            'initials': 'MT',
            'stat': 'Dream job in 2 weeks',
            'type': 'job'
        },
        {
            'text': '"The resume integration is a game changer. My proposals and applications now feel personalized and I\'ve landed my highest-paying client ever!"',
            'author': 'Priya S.',
            'role': 'Content Strategist',
            'initials': 'PS',
            'stat': '$15K project + 6-figure job',
            'type': 'both'
        }
    ]

    cols = st.columns(3)
    for col, t in zip(cols, testimonials):
        type_badge = ""
        if t['type'] == 'freelance':
            type_badge = '<span style="background: #8b5cf6; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; margin-right: 8px;">Freelance</span>'
        elif t['type'] == 'job':
            type_badge = '<span style="background: #06b6d4; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; margin-right: 8px;">Job Hunt</span>'
        else:
            type_badge = '<span style="background: #10b981; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; margin-right: 8px;">Both</span>'

        with col:
            st.markdown(f"""
            <div class="testimonial-card">
                <div style="margin-bottom: 12px;">
                    {type_badge}
                    <span class="feature-badge">
                        📈 {t['stat']}
                    </span>
                </div>
                <p class="testimonial-text">{t['text']}</p>
                <div class="testimonial-author">
                    <div class="author-avatar">{t['initials']}</div>
                    <div>
                        <div style="font-weight: 600; color: #0f172a;">{t['author']}</div>
                        <div style="font-size: 13px; color: #64748b;">{t['role']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# -------------------------------
# Sidebar (Updated)
# -------------------------------
def render_sidebar():
    with st.sidebar:
        render_logo()

        st.markdown("---")

        # User Stats
        st.markdown('<div class="sidebar-title">📊 Your Progress</div>', unsafe_allow_html=True)
        metrics = st.session_state.success_metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Proposals", metrics['proposals_generated'])
        with col2:
            hours = metrics['time_saved_minutes'] // 60
            st.metric("Hours Saved", hours)

        # Usage
        st.markdown("---")
        st.markdown('<div class="sidebar-title">⚡ Today\'s Usage</div>', unsafe_allow_html=True)
        limit = get_current_limit()
        used = st.session_state.usage_count
        remaining = max(0, limit - used)
        pct = min(100, int((used / limit) * 100)) if limit and limit > 0 else 0

        st.markdown(f"""
        <div style="margin-bottom: 8px;">
            <span style="font-weight: 600; color: #0f172a;">{used}</span>
            <span style="color: #64748b;"> / {limit} proposals used</span>
        </div>
        <div class="usage-progress">
            <div class="usage-progress-fill" style="width: {pct}%;"></div>
        </div>
        <div style="font-size: 13px; color: {'#ef4444' if remaining <= 1 else '#10b981'}; font-weight: 500;">
            {remaining} remaining today
        </div>
        """, unsafe_allow_html=True)

        # Resume Library
        st.markdown("---")
        st.markdown('<div class="sidebar-title">📚 Resume Library</div>', unsafe_allow_html=True)

        if st.session_state.resume_library:
            active = get_active_resume()
            if active:
                st.success(f"✅ Active: {active['name'][:20]}...")
            if st.button("📂 Manage Resumes", use_container_width=True, key="manage_resumes_sidebar"):
                st.session_state.show_resume_manager = True
                st.rerun()
        else:
            st.info("No resumes yet. Add one below!")

        # License
        st.markdown("---")
        st.markdown('<div class="sidebar-title">🔐 License</div>', unsafe_allow_html=True)

        tier_colors = {
            'free': '#64748b',
            'trial': '#06b6d4',
            'monthly': '#8b5cf6',
            'yearly': '#8b5cf6',
            'lifetime': '#f59e0b'
        }
        tier_icons = {
            'free': '🆓',
            'trial': '⏱️',
            'monthly': '⭐',
            'yearly': '💫',
            'lifetime': '👑'
        }

        tier = st.session_state.license_tier
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 8px; padding: 12px; background: linear-gradient(135deg, {tier_colors[tier]}15, {tier_colors[tier]}05); border-radius: 12px; border: 1px solid {tier_colors[tier]}30;">
            <span style="font-size: 24px;">{tier_icons[tier]}</span>
            <div>
                <div style="font-weight: 700; color: {tier_colors[tier]};">{tier.upper()}</div>
                <div style="font-size: 12px; color: #64748b;">{LICENSE_TIERS[tier]['price']}</div>
                {f'<div style="font-size: 11px; color: #94a3b8;">Expires: {st.session_state.plan_expiry_date}</div>' if st.session_state.plan_expiry_date else '<div></div>'}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # License Key Input
        with st.expander("🔑 Enter License Key"):
            license_input = st.text_input("License Key", type="password", placeholder="XXXX-XXXX-XXXX",
                                          key="license_input")
            if st.button("Activate", use_container_width=True, key="activate_license"):
                if check_license_key(license_input):
                    st.success(f"✅ {st.session_state.license_tier.upper()} activated!")
                    st.rerun()
                else:
                    st.error("Invalid or expired license key")

        # Buy Me a Coffee / Support
        st.markdown("---")
        st.markdown('<div class="sidebar-title">☕ Support the Project</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align: center; padding: 12px; background: linear-gradient(135deg, #fef3c7, #fde68a); border-radius: 12px; border: 1px solid #f59e0b;">
            <p style="color: #92400e; font-size: 13px; margin-bottom: 8px;">
                Love this tool? Support future development!
            </p>
            <a href="{PAYMENT_LINKS['coffee']}" target="_blank" style="text-decoration: none;">
                <button style="
                    background: linear-gradient(135deg, #f59e0b, #d97706);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 13px;
                    border: none;
                    cursor: pointer;
                    width: 100%;
                ">
                    ☕ Buy Me a Coffee
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        # In the sidebar section, add this after the Buy Me a Coffee section:

        # Affiliate Disclosure
        st.markdown("---")
        st.markdown('<div class="sidebar-title">📢 Transparency</div>', unsafe_allow_html=True)

        st.markdown(f"""
                <div style="text-align: center; padding: 10px; background: linear-gradient(135deg, #f0f9ff, #e0f2fe); border-radius: 10px; border: 1px solid #bae6fd;">
                    <p style="color: #0369a1; font-size: 12px; margin: 0;">
                        Some links are affiliate links<br>
                        <a href="{AFFILIATE_GUIDELINES_LINK}" target="_blank" style="color: #0ea5e9; text-decoration: none; font-weight: 500;">
                            Read our guidelines
                        </a>
                    </p>
                </div>
                """, unsafe_allow_html=True)

        # User email display
        if st.session_state.user_email:
            st.markdown("---")
            st.markdown(f'<div style="font-size: 13px; color: #64748b;">📧 {st.session_state.user_email}</div>',
                        unsafe_allow_html=True)

        # Data Management
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Export", use_container_width=True, key="export_data_sidebar"):
                st.session_state.show_data_export = True
                st.rerun()
        with col2:
            if st.button("🗑️ Delete", use_container_width=True, key="delete_account_sidebar"):
                st.session_state.show_delete_account = True
                st.rerun()


# -------------------------------
# Footer Component (Fixed - Using Streamlit buttons directly)
# -------------------------------
def render_footer():
    st.markdown("""
    <div class="custom-footer">
        <div class="logo-container" style="justify-content: center; margin-bottom: 16px;">
            <div class="logo-icon" style="width: 40px; height: 40px; font-size: 20px;">P</div>
            <div class="logo-text" style="font-size: 20px;">ProposalCraft AI</div>
        </div>
        <p style="color: #64748b; font-size: 14px; margin-bottom: 8px;">
            The all-in-one platform for freelancers and job seekers
        </p>
        <p style="color: #94a3b8; font-size: 13px;">
            © 2024 ProposalCraft AI. Helping professionals win since 2024.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Footer links as Streamlit buttons - these actually work!
    st.markdown("<div style='text-align: center; margin-top: 16px;'>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
    with col2:
        if st.button("🔒 Privacy Policy", key="footer_privacy_btn", use_container_width=True):
            st.session_state.show_privacy = True
            st.rerun()
    with col3:
        if st.button("📜 Terms of Service", key="footer_terms_btn", use_container_width=True):
            st.session_state.show_terms = True
            st.rerun()
    with col4:
        if st.button("📞 Contact / Support", key="footer_contact_btn", use_container_width=True):
            st.session_state.show_contact = True
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------
# Privacy Policy Modal
# -------------------------------
def render_privacy_modal():
    if st.session_state.get('show_privacy', False):
        st.markdown("## 🔒 Privacy Policy")
        st.markdown("""
        **Last updated: December 2025**

        We take your privacy seriously. Here's what you need to know:

        ### Data Collection
        - **Email addresses**: We collect email addresses for account management and communication purposes.
        - **Proposal/Resume data**: We store your proposals and resumes to provide our service functionality.
        - **Usage data**: We track proposal generation statistics to improve our service.

        ### Data Usage
        - Your data is used solely to provide and improve our services.
        - We use aggregated, anonymized data for analytics and service improvements.
        - Your personal information is never sold to third parties.

        ### Data Storage
        - All data is securely stored and encrypted in MongoDB database.
        - We implement industry-standard security measures to protect your data.
        - Data is backed up regularly to prevent loss.

        ### Data Sharing
        - We never sell or share your personal data with third parties.
        - We may share anonymized, aggregated data for research purposes.
        - We may disclose data if required by law or legal process.

        ### Your Rights
        - **Export**: You can export all your data at any time from the sidebar.
        - **Delete**: You can permanently delete your account and all associated data.
        - **Access**: You can view all data we have about you through the export feature.
        - **Correction**: You can update your information at any time.

        ### Cookies
        - We use essential cookies for site functionality.
        - Optional analytics cookies help us improve the service.
        - You can manage your cookie preferences at any time.

        ### Contact
        For questions about our privacy practices, contact us at:
        - **Email**: privacy@careersolutiontools.com
        """)

        if st.button("← Close Privacy Policy", key="close_privacy_modal", use_container_width=True):
            st.session_state.show_privacy = False
            st.rerun()
        st.stop()


# -------------------------------
# Terms of Service Modal
# -------------------------------
def render_terms_modal():
    if st.session_state.get('show_terms', False):
        st.markdown("## 📜 Terms of Service")
        st.markdown("""
        **Last updated: December 2025**

        By using ProposalCraft AI, you agree to these terms:

        ### 1. Service Description
        - We provide AI-powered proposal and cover letter generation tools.
        - The service is designed to help freelancers and jobseekers create professional proposals.
        - AI-generated content should always be reviewed before use.

        ### 2. User Accounts
        - You must provide accurate information when creating an account.
        - You are responsible for maintaining the security of your account.
        - One account per user is permitted.

        ### 3. Content Ownership
        - You retain ownership of all content you create using our service.
        - You grant us a license to store and process your content for service delivery.
        - We do not claim ownership over your generated proposals.

        ### 4. Acceptable Use
        - You agree not to use the service for illegal activities.
        - You will not attempt to circumvent usage limits or security measures.
        - You will not share your account credentials with others.

        ### 5. AI-Generated Content
        - AI-generated content may contain errors or inaccuracies.
        - You are responsible for reviewing and editing all generated content.
        - We are not liable for the consequences of using generated content.

        ### 6. Payments & Refunds
        - License keys are non-refundable after 7 days of purchase.
        - Subscription fees are charged at the beginning of each billing cycle.
        - You may cancel your subscription at any time.

        ### 7. Service Availability
        - We strive for 99.9% uptime but do not guarantee uninterrupted service.
        - We may perform maintenance that temporarily affects availability.
        - We reserve the right to modify or discontinue features.

        ### 8. Termination
        - We reserve the right to terminate accounts violating these terms.
        - You may close your account at any time through the settings.
        - Upon termination, your data will be deleted within 30 days.

        ### 9. Limitation of Liability
        - Our liability is limited to the amount you paid for the service.
        - We are not liable for indirect, incidental, or consequential damages.

        ### 10. Changes to Terms
        - We may update these terms from time to time.
        - Continued use of the service constitutes acceptance of updated terms.

        ### Contact
        For questions about our terms, contact us at:
        - **Email**: legal@careersolutiontools.com
        """)

        if st.button("← Close Terms of Service", key="close_terms_modal", use_container_width=True):
            st.session_state.show_terms = False
            st.rerun()
        st.stop()

# -------------------------------
# Contact Modal (Updated with Tally form)
# -------------------------------
def render_contact_modal():
    if st.session_state.get('show_contact', False):
        st.markdown("## 📞 Contact Us")
        st.markdown("""
        **We're here to help!**

        ### Contact Information
        - **Email**: support@careersolutiontools.com
        - **Response Time**: Within 24 hours on business days
        - **Business Hours**: Monday-Friday, 9AM-5PM EST
        """)

        st.markdown("---")
        st.markdown("### 📧 Contact Form")
        st.markdown("Fill out the form below and we'll get back to you ASAP!")

        # Embed Tally form
        st.markdown(f"""
        <iframe src="{TALLY_CONTACT_FORM}" width="100%" height="600" frameborder="0" marginheight="0" marginwidth="0" title="Contact form"></iframe>
        """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("← Close Contact", key="close_contact_modal", use_container_width=True):
            st.session_state.show_contact = False
            st.rerun()
        st.stop()

# -------------------------------
# Main App Execution
# -------------------------------
render_sidebar()

# Check for modals first (before email capture)
render_privacy_modal()
render_terms_modal()
render_contact_modal()

# Email capture gate
if render_email_capture():
    st.stop()

# Cookie consent
if not st.session_state.cookie_consent:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.info("🍪 We use essential cookies for functionality. Enable analytics to help us improve.")
    with col2:
        if st.button("Accept All", key="accept_all_cookies"):
            st.session_state.cookie_consent = True
            st.session_state.cookie_preferences = {'essential': True, 'analytics': True, 'preferences': True}
            st.rerun()

# Urgency Banner
if st.session_state.license_tier == 'free':
    remaining = get_current_limit() - st.session_state.usage_count
    if remaining <= 1 and remaining >= 0:
        st.markdown(f"""
        <div class="urgency-banner">
            <span style="font-size: 20px;">⚡</span>
            <span class="urgency-text">Only {remaining} free generation{'s' if remaining != 1 else ''} left today! Upgrade for unlimited access.</span>
        </div>
        """, unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-section">
    <div style="position: relative; z-index: 1;">
        <div class="feature-badge">🚀 AI-Powered Proposals & Job Applications</div>
        <h1 class="hero-title">Win More Projects & Land Dream Jobs Faster</h1>
        <p class="hero-subtitle">
            Create platform-optimized proposals for freelancing AND professional job applications. 
            Personalized with your resume, tailored for every opportunity.
        </p>
        <div class="hero-stats">
            <div class="stat-item">
                <div class="stat-number">12K+</div>
                <div class="stat-label">Freelancers & Job Seekers</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">65K+</div>
                <div class="stat-label">Proposals & Applications</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">28%</div>
                <div class="stat-label">Avg. Success Rate</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
# Feature Highlights
st.markdown("""
<div style="text-align: center; margin: 40px 0;">
    <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 28px; margin-bottom: 24px;">
        ✨ Double Your Career Opportunities
    </h2>
    <p style="color: #64748b; font-size: 16px; margin-bottom: 32px;">
        One platform for all your career advancement needs
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <div style="background: linear-gradient(135deg, #8b5cf6, #c4b5fd); color: white; width: 60px; height: 60px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 28px; margin: 0 auto 16px;">
            📝
        </div>
        <h4 style="margin: 0 0 8px; color: #0f172a;">Freelance Proposals</h4>
        <p style="color: #64748b; font-size: 14px; margin: 0;">
            Upwork, Fiverr, LinkedIn, Direct Clients
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <div style="background: linear-gradient(135deg, #06b6d4, #67e8f9); color: white; width: 60px; height: 60px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 28px; margin: 0 auto 16px;">
            💼
        </div>
        <h4 style="margin: 0 0 8px; color: #0f172a;">Job Applications</h4>
        <p style="color: #64748b; font-size: 14px; margin: 0;">
            Cover letters, emails, LinkedIn messages
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <div style="background: linear-gradient(135deg, #10b981, #34d399); color: white; width: 60px; height: 60px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 28px; margin: 0 auto 16px;">
            📚
        </div>
        <h4 style="margin: 0 0 8px; color: #0f172a;">Resume Library</h4>
        <p style="color: #64748b; font-size: 14px; margin: 0;">
            Multiple resumes for different opportunities
        </p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <div style="background: linear-gradient(135deg, #f59e0b, #fbbf24); color: white; width: 60px; height: 60px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 28px; margin: 0 auto 16px;">
            📊
        </div>
        <h4 style="margin: 0 0 8px; color: #0f172a;">Analytics</h4>
        <p style="color: #64748b; font-size: 14px; margin: 0;">
            Track your success rate & time saved
        </p>
    </div>
    """, unsafe_allow_html=True)

# Data Export Modal
if st.session_state.show_data_export:
    st.markdown("## 📥 Export Your Data")
    export_data = export_user_data_json()
    with st.expander("Preview Data", expanded=True):
        st.json(json.loads(export_data))
    st.download_button(
        label="⬇️ Download JSON",
        data=export_data,
        file_name=f"proposalcraft_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True,
    )
    if st.button("← Back", use_container_width=True, key="data_export_back"):
        st.session_state.show_data_export = False
        st.rerun()
    st.stop()

# Account Deletion Modal
if st.session_state.show_delete_account:
    st.markdown("## 🗑️ Delete Account")
    st.error("⚠️ This will permanently delete all your data including proposals, resumes, and preferences.")

    reason = st.selectbox("Reason for leaving (optional)", [
        "Select a reason...", "Too expensive", "Not using it enough",
        "Found another solution", "Quality issues", "Privacy concerns", "Other"
    ], key="delete_reason")

    feedback = st.text_area("Any feedback for us? (optional)", key="delete_feedback")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Export Data First", use_container_width=True, key="delete_export_btn"):
            st.session_state.show_data_export = True
            st.session_state.show_delete_account = False
            st.rerun()
    with col2:
        if st.button("← Cancel", use_container_width=True, key="delete_cancel_btn"):
            st.session_state.show_delete_account = False
            st.rerun()

    st.markdown("---")
    confirm_text = st.text_input('Type "DELETE" to confirm:', key="delete_confirm_input")

    if confirm_text == "DELETE":
        if st.button("🗑️ Permanently Delete Account", type="primary", use_container_width=True, key="delete_final_btn"):
            delete_all_user_data()
            st.success("Account deleted. Refreshing...")
            time.sleep(1)
            st.rerun()
    st.stop()

# Resume Manager Modal
if st.session_state.show_resume_manager:
    st.markdown("## 📚 Resume Library")

    if not st.session_state.resume_library:
        st.info("No resumes in your library yet. Add one to get personalized proposals!")
    else:
        st.markdown(f"**{len(st.session_state.resume_library)} resume(s)** in your library")

        resume_keys = list(st.session_state.resume_library.keys())

        for rid in resume_keys:
            rdata = st.session_state.resume_library[rid]
            is_active = rid == st.session_state.active_resume_id

            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    status = "✅ Active" if is_active else ""
                    st.markdown(f"**{rdata['name']}** {status}")
                    st.caption(f"📅 {rdata['created_at']} • 📝 {rdata['character_count']} chars")

                with col2:
                    if not is_active:
                        if st.button("Set Active", key=f"act_{rid}", use_container_width=True):
                            st.session_state.active_resume_id = rid
                            st.rerun()

                with col3:
                    if st.button("🗑️", key=f"del_{rid}", use_container_width=True):
                        delete_resume_from_library(rid)
                        st.rerun()

                if rid in st.session_state.resume_library:
                    with st.expander("Preview"):
                        display_text = rdata['text'][:500] + "..." if len(rdata['text']) > 500 else rdata['text']
                        st.text_area("", value=display_text, height=150, disabled=True, key=f"preview_{rid}",
                                     label_visibility="collapsed")

            st.markdown("---")

    if st.button("← Back to Generator", use_container_width=True, key="resume_manager_back"):
        st.session_state.show_resume_manager = False
        st.rerun()
    st.stop()

# Main Content Tabs
st.markdown("""
<h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 28px; margin-bottom: 16px;">
    ✨ Two Ways to Accelerate Your Career
</h2>
<p style="color: #64748b; margin-bottom: 24px; font-size: 16px;">
    Whether you're freelancing or job hunting, we've got you covered with AI-powered optimization
</p>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 Freelance Proposal Generator", "💼 Job Application Suite"])

with tab1:
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("### 🎯 Job Details")

        platform = st.selectbox(
            "Platform",
            ["Upwork", "Fiverr", "Direct Client", "LinkedIn", "Generic"],
            help="Select the platform you're applying on"
        )

        job_post = st.text_area(
            "Job Posting",
            height=160,
            placeholder="Paste the complete job description here...\n\nTip: Include all requirements and preferences mentioned by the client.",
            help="The more details you provide, the better your proposal will be"
        )

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            skills = st.text_input(
                "Your Top Skills",
                placeholder="e.g., Python, React, Data Analysis"
            )
        with col_s2:
            advantage = st.text_input(
                "Your Unique Advantage",
                placeholder="e.g., 5 years in fintech"
            )

    with col_right:
        st.markdown("### 📄 Your Resume")

        if st.session_state.resume_library:
            options = {rid: f"{data['name']}" for rid, data in st.session_state.resume_library.items()}

            default_index = 0
            if st.session_state.active_resume_id in options:
                default_index = list(options.keys()).index(st.session_state.active_resume_id)
            elif options:
                st.session_state.active_resume_id = list(options.keys())[0]

            selected = st.selectbox(
                "Select Resume",
                list(options.keys()),
                format_func=lambda x: options[x],
                index=default_index,
                key="proposal_resume_select"
            )
            if selected != st.session_state.active_resume_id:
                st.session_state.active_resume_id = selected
                st.rerun()

            active = get_active_resume()
            if active:
                st.success(f"✅ Using: {active['name']}")
                with st.expander("Preview"):
                    display_text = active['text'][:300] + "..." if len(active['text']) > 300 else active['text']
                    st.text_area("", value=display_text, height=100, disabled=True, label_visibility="collapsed",
                                 key="preview_active_proposal")

        st.markdown("---")
        st.markdown("**➕ Add New Resume**")

        uploaded_resume = st.file_uploader(
            "Upload Resume",
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT",
            key="proposal_uploader"
        )

        if uploaded_resume:
            text = process_uploaded_resume(uploaded_resume)
            if text:
                resume_name = st.text_input("Name this resume", value=uploaded_resume.name.rsplit('.', 1)[0],
                                            key="name_upload_proposal")
                if st.button("💾 Save to Library", use_container_width=True, key="save_upload_proposal"):
                    add_resume_to_library(resume_name, text)
                    st.success("✅ Resume saved!")
                    st.rerun()

        with st.expander("Or paste resume text"):
            new_resume_text = st.text_area("Resume Text", height=100, key="paste_resume_proposal")
            if new_resume_text:
                resume_name_paste = st.text_input("Resume name",
                                                  value=f"Resume {len(st.session_state.resume_library) + 1}",
                                                  key="name_paste_proposal")
                if st.button("💾 Save", key="save_paste_proposal"):
                    add_resume_to_library(resume_name_paste, new_resume_text)
                    st.success("✅ Saved!")
                    st.rerun()

with tab2:
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("### 💼 Job Details")

        job_type = st.selectbox(
            "Application Type",
            ["Full-time", "Part-time", "Contract", "Internship", "Remote"],
            key="job_type_select"
        )

        job_description = st.text_area(
            "Job Description",
            height=140,
            placeholder="Paste the job description here...",
            key="job_description_input"
        )

        qualifications = st.text_input(
            "Key Qualifications",
            placeholder="Your relevant qualifications and experience",
            key="qualifications_input"
        )

        why_interested = st.text_area(
            "Why You're Interested",
            height=80,
            placeholder="What excites you about this role?",
            key="why_interested_input"
        )

        st.markdown("**📋 Components to Generate**")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            gen_cover_letter = st.checkbox("Cover Letter", value=True, key="gen_cover_letter")
            gen_email = st.checkbox("Application Email", value=True, key="gen_email")
        with col_c2:
            gen_follow_up = st.checkbox("Follow-up Email", value=True, key="gen_follow_up")
            gen_linkedin = st.checkbox("LinkedIn Message", value=False, key="gen_linkedin")

    with col_right:
        st.markdown("### 📄 Your Resume")

        if st.session_state.resume_library:
            options_job = {rid: f"{data['name']}" for rid, data in st.session_state.resume_library.items()}

            default_index_job = 0
            if st.session_state.active_resume_id in options_job:
                default_index_job = list(options_job.keys()).index(st.session_state.active_resume_id)
            elif options_job:
                st.session_state.active_resume_id = list(options_job.keys())[0]

            selected_job = st.selectbox(
                "Select Resume",
                list(options_job.keys()),
                format_func=lambda x: options_job[x],
                index=default_index_job,
                key="job_resume_select"
            )
            if selected_job != st.session_state.active_resume_id:
                st.session_state.active_resume_id = selected_job
                st.rerun()

        st.markdown("---")
        uploaded_resume_job = st.file_uploader(
            "Upload Resume",
            type=['pdf', 'docx', 'txt'],
            key="job_uploader"
        )

        if uploaded_resume_job:
            text = process_uploaded_resume(uploaded_resume_job)
            if text:
                resume_name_job = st.text_input("Name", value=uploaded_resume_job.name.rsplit('.', 1)[0],
                                                key="name_job")
                if st.button("💾 Save", key="save_job", use_container_width=True):
                    add_resume_to_library(resume_name_job, text)
                    st.success("✅ Saved!")
                    st.rerun()

# API Configuration
st.markdown("---")
with st.expander("🔑 API Configuration", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        env_openai_key = os.getenv("OPENAI_API_KEY", "")
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=env_openai_key if "openai_key_input" not in st.session_state else st.session_state.openai_key_input,
            help="Enter your OpenAI API key or set OPENAI_API_KEY environment variable",
            key="openai_key_input"
        )
    with col2:
        model_name = st.selectbox(
            "Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            help="Select the AI model to use",
            key="model_name_select"
        )

    final_openai_key = st.session_state.openai_key_input or env_openai_key

    if final_openai_key and OPENAI_SDK_AVAILABLE:
        st.success("✅ API configured and ready")
    elif not OPENAI_SDK_AVAILABLE:
        st.error("❌ OpenAI SDK not installed. Run: `pip install openai`")
    else:
        st.warning("⚠️ Please enter your OpenAI API key to generate content")

# Generate Button
st.markdown("---")

col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
with col_gen2:
    generate_clicked = st.button(
        "✨ Generate Winning Content",
        type="primary",
        use_container_width=True,
        disabled=not (final_openai_key and OPENAI_SDK_AVAILABLE)
    )

if generate_clicked:
    # 1. Input Validation
    is_proposal = bool(job_post and skills and advantage)
    is_job_app = bool(job_description and qualifications and why_interested and (
            gen_cover_letter or gen_email or gen_follow_up or gen_linkedin))

    if not (is_proposal or is_job_app):
        st.error("❌ Please fill in all required fields in the active tab (Freelance Proposal or Job Application).")
        st.stop()

    if not final_openai_key or not OPENAI_SDK_AVAILABLE:
        st.error("❌ Please configure your OpenAI API key in the API Configuration section.")
        st.stop()

    if not can_generate_proposal():
        st.error(f"⚠️ Daily limit reached ({get_current_limit()} proposals). Upgrade for unlimited access!")
        st.stop()

    try:
        # 2. API Setup
        client = OpenAI(api_key=final_openai_key)

        with st.spinner("✨ Crafting your winning content..."):
            # 3. Prompt Construction
            if is_proposal:
                system_prompt = PLATFORM_PROMPTS.get(platform, PLATFORM_PROMPTS["Generic"])
                user_prompt = f"""
PLATFORM: {platform}
JOB POSTING:
{job_post}

CANDIDATE SKILLS: {skills}
UNIQUE ADVANTAGE: {advantage}
"""
                active_resume = get_active_resume()
                if active_resume:
                    user_prompt += f"""
CANDIDATE RESUME:
{active_resume['text']}

Use specific experiences and achievements from the resume to make the proposal more personalized and compelling.
"""
                user_prompt += """
Create a concise, high-converting proposal that:
1. Opens with a hook that shows you understand the client's problem
2. Demonstrates relevant experience with specific examples
3. Provides a brief overview of your approach
4. Includes a clear call-to-action
5. Ends with 2 follow-up message templates (one for no response, one after interview)

Keep the main proposal under 250 words. Be specific, not generic.
"""
                generation_type = "proposal"
                content_title = "Freelance Proposal"
                content_type = platform

            else:  # is_job_app
                system_prompt = "You are an expert career coach and professional writer specializing in job applications."
                components = []
                if gen_cover_letter: components.append("Cover Letter")
                if gen_email: components.append("Application Email")
                if gen_follow_up: components.append("Follow-up Email")
                if gen_linkedin: components.append("LinkedIn Message")

                user_prompt = f"""
JOB TYPE: {job_type}
JOB DESCRIPTION:
{job_description}

QUALIFICATIONS: {qualifications}
WHY INTERESTED: {why_interested}

Generate the following components: {', '.join(components)}. Separate each component with a clear heading (e.g., ## Cover Letter).
"""
                active_resume = get_active_resume()
                if active_resume:
                    user_prompt += f"""
CANDIDATE RESUME:
{active_resume['text']}

Reference specific achievements and experiences from the resume to powerfully match qualifications to the job description.
"""
                generation_type = "job_application"
                content_title = "Job Application Content"
                content_type = job_type

            # 4. API Call
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            content = response.choices[0].message.content

            # 5. Tracking and State Update
            st.session_state.usage_count += 1
            track_success_metrics()

            history_item = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "type": generation_type,
                "platform": platform if generation_type == "proposal" else job_type,
                "content": content,
                "used_resume": bool(get_active_resume()),
                "input_job_post": job_post if generation_type == "proposal" else job_description
            }
            st.session_state.proposal_history.append(history_item)
            st.session_state.current_proposal = content

        # 6. Post-Generation Display
        st.markdown("""
        <div class="success-message">
            ✅ <strong>Content generated successfully!</strong> Your personalized content is ready below.
        </div>
        """, unsafe_allow_html=True)

        remaining = get_current_limit() - st.session_state.usage_count
        if remaining > 0:
            st.info(f"💡 You have {remaining} generation{'s' if remaining != 1 else ''} remaining today.")
        else:
            st.warning("⚠️ You've used all free generations for today. Upgrade for unlimited access!")

        st.markdown("### 📄 Your Generated Content")
        st.code(content, language="markdown")

        # Export Options
        st.markdown("---")
        st.markdown("### 📥 Export Options")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                "📄 Download TXT",
                data=content,
                file_name=f"{generation_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            html_content = generate_pdf_content(
                content.replace('\n', '<br>'),
                content_title,
                content_type
            )
            st.download_button(
                "🌐 Download HTML",
                data=html_content,
                file_name=f"{generation_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                use_container_width=True
            )
        with col3:
            st.download_button(
                "📋 Download JSON",
                data=json.dumps(history_item, indent=2),
                file_name=f"{generation_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

        # Copy text area
        with st.expander("📋 Copy to Clipboard", expanded=True):
            st.text_area(
                "Select and copy:",
                value=content,
                height=300,
                label_visibility="collapsed"
            )

    except Exception as e:
        msg = str(e).lower()
        if "invalid api key" in msg or "invalid_api_key" in msg:
            st.error("❌ Invalid API key. Please check your OpenAI API key.")
        elif "quota" in msg or "billing" in msg or "rate" in msg:
            st.error("❌ API quota exceeded or billing issue. Please check your OpenAI account.")
        else:
            st.error(f"❌ An unexpected error occurred: {str(e)}")

# Testimonials
st.markdown("---")
render_testimonials()

# Pricing
st.markdown("---")
render_pricing()

# FooterS^7980=
render_footer()

# Affiliate Section
st.markdown("---")
render_affiliate_section()
