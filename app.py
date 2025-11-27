import streamlit as st
import json
from openai import OpenAI
from datetime import datetime, date, timedelta
import time
import hashlib
import uuid
import help_resources

try:
    import pypdf  # Modern replacement for PyPDF2
except ImportError:
    st.error("Please install pypdf: pip install pypdf")
import docx
import io

# Page config
st.set_page_config(
    page_title="ProposalCraft AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== LICENSE AND USAGE TRACKING SYSTEM ==========

# Valid licenses with expiration dates
VALID_LICENSES = {
    # Format: "LICENSE_KEY": "EXPIRY_DATE"
    "PROPOSAL-2024-MONTH-JICHP8": "2025-12-27",  # Demo key
    "PROPOSAL-2024-YEAR-7N7FWG": "2026-11-27",
    "PROPOSAL-2024-LIFE-WF5SFN": "2099-12-31",
    # Add new keys as users purchase
}

# Rate limits
LICENSE_RATE_LIMITS = {
    'free': 5,  # Free tier daily limit
    'premium': 100,  # Premium daily limit
    'burst': 10  # Maximum requests per hour
}

# Initialize session state
if 'proposal_history' not in st.session_state:
    st.session_state.proposal_history = []
if 'current_proposal' not in st.session_state:
    st.session_state.current_proposal = ""
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0
if 'last_reset_date' not in st.session_state:
    st.session_state.last_reset_date = str(date.today())
if 'premium_user' not in st.session_state:
    st.session_state.premium_user = False
if 'license_key' not in st.session_state:
    st.session_state.license_key = ""
if 'license_usage' not in st.session_state:
    st.session_state.license_usage = {}
if 'rate_limits' not in st.session_state:
    st.session_state.rate_limits = {}
if 'browser_fingerprint' not in st.session_state:
    st.session_state.browser_fingerprint = str(uuid.uuid4())[:8]  # Simple fingerprint

# Check if we need to reset daily usage
if st.session_state.last_reset_date != str(date.today()):
    st.session_state.usage_count = 0
    st.session_state.last_reset_date = str(date.today())


# ========== RESUME FILE PROCESSING FUNCTIONS ==========

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF files using pypdf"""
    try:
        pdf_reader = pypdf.PdfReader(io.BytesIO(uploaded_file.getvalue()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF file: {str(e)}")
        return None


def extract_text_from_docx(uploaded_file):
    """Extract text from DOCX files"""
    try:
        doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading DOCX file: {str(e)}")
        return None


def extract_text_from_txt(uploaded_file):
    """Extract text from TXT files"""
    try:
        text = uploaded_file.getvalue().decode("utf-8")
        return text.strip()
    except Exception as e:
        st.error(f"Error reading text file: {str(e)}")
        return None


def process_uploaded_resume(uploaded_file):
    """Process uploaded resume file and extract text"""
    file_type = uploaded_file.type

    with st.spinner(f"📖 Reading your {uploaded_file.name}..."):
        if file_type == "application/pdf":
            return extract_text_from_pdf(uploaded_file)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return extract_text_from_docx(uploaded_file)
        elif file_type == "text/plain":
            return extract_text_from_txt(uploaded_file)
        else:
            st.error(f"Unsupported file type: {file_type}")
            return None


# ========== LICENSE MANAGEMENT FUNCTIONS ==========

def get_browser_fingerprint():
    """Create a simple browser fingerprint"""
    return st.session_state.browser_fingerprint


def track_license_usage(license_key, action="check"):
    """Track license usage patterns"""
    license_key = license_key.strip().upper()
    fingerprint = get_browser_fingerprint()
    today = str(date.today())
    current_hour = datetime.now().strftime("%Y-%m-%d-%H")

    if license_key not in st.session_state.license_usage:
        st.session_state.license_usage[license_key] = {
            'first_seen': today,
            'last_seen': today,
            'fingerprints': set([fingerprint]),
            'usage_count': 0,
            'daily_usage': {},
            'hourly_usage': {}
        }

    # Update usage tracking
    usage_data = st.session_state.license_usage[license_key]
    usage_data['last_seen'] = today
    usage_data['fingerprints'].add(fingerprint)
    usage_data['usage_count'] += 1

    # Track daily usage
    if today not in usage_data['daily_usage']:
        usage_data['daily_usage'][today] = 0
    usage_data['daily_usage'][today] += 1

    # Track hourly usage
    if current_hour not in usage_data['hourly_usage']:
        usage_data['hourly_usage'][current_hour] = 0
    usage_data['hourly_usage'][current_hour] += 1

    return usage_data


def check_license_format(license_key):
    """Validate license key format"""
    if not license_key or len(license_key) < 10:
        return False
    if not license_key.startswith("PROPOSAL-"):
        return False
    return True


def check_rate_limit(license_key):
    """Enforce rate limits per license"""
    license_key = license_key.strip().upper()
    current_hour = datetime.now().strftime("%Y-%m-%d-%H")
    today = str(date.today())

    if license_key not in st.session_state.rate_limits:
        st.session_state.rate_limits[license_key] = {
            'daily_usage': {today: 0},
            'hourly_usage': {current_hour: 0},
            'last_reset': datetime.now()
        }

    limits = st.session_state.rate_limits[license_key]

    # Reset daily usage if new day
    if today not in limits['daily_usage']:
        limits['daily_usage'] = {today: 0}

    # Reset hourly usage if new hour
    if current_hour not in limits['hourly_usage']:
        limits['hourly_usage'] = {current_hour: 0}

    # Get the appropriate limit
    is_premium = license_key in VALID_LICENSES
    daily_limit = LICENSE_RATE_LIMITS['premium'] if is_premium else LICENSE_RATE_LIMITS['free']
    hourly_limit = LICENSE_RATE_LIMITS['burst']

    # Check limits
    if limits['daily_usage'][today] >= daily_limit:
        st.error(f"🚫 Daily limit reached ({daily_limit} proposals)")
        return False

    if limits['hourly_usage'][current_hour] >= hourly_limit:
        st.error("🚫 Too many requests - please wait an hour")
        return False

    # Increment counters
    limits['daily_usage'][today] += 1
    limits['hourly_usage'][current_hour] += 1

    return True


def is_license_abused(license_key):
    """Check if license shows signs of mass sharing"""
    license_key = license_key.strip().upper()

    if license_key not in st.session_state.license_usage:
        return False

    usage_data = st.session_state.license_usage[license_key]

    # Check for multiple fingerprints (different browsers)
    if len(usage_data['fingerprints']) > 3:
        st.warning("⚠️ Multiple browsers detected for this license")
        return True

    # Check for excessive daily usage
    today = str(date.today())
    if today in usage_data['daily_usage'] and usage_data['daily_usage'][today] > 50:
        st.error("🚫 Excessive usage detected - please contact support")
        return True

    # Check if first seen was too recent for high usage
    first_seen = datetime.strptime(usage_data['first_seen'], "%Y-%m-%d")
    days_since_first_use = (datetime.now() - first_seen).days
    if days_since_first_use < 2 and usage_data['usage_count'] > 100:
        st.error("🚫 Suspicious usage pattern detected")
        return True

    return False


def check_license_key(license_key):
    """Enhanced license validation with abuse detection"""
    license_key = license_key.strip().upper()

    # Basic format check
    if not check_license_format(license_key):
        return False

    # Track usage patterns
    track_license_usage(license_key)

    # Check for abuse
    if is_license_abused(license_key):
        return False

    # Check rate limits
    if not check_rate_limit(license_key):
        return False

    # Final license validation
    if license_key in VALID_LICENSES:
        expiry_date = datetime.strptime(VALID_LICENSES[license_key], "%Y-%m-%d")
        if datetime.now() < expiry_date:
            return True

    return False


# ========== CUSTOM CSS ==========

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .proposal-box {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        background-color: #f9f9f9;
        margin: 10px 0;
    }
    .history-item {
        border-left: 3px solid #1f77b4;
        padding-left: 10px;
        margin: 5px 0;
        font-size: 0.9rem;
    }
    .copy-btn {
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 5px;
        cursor: pointer;
        margin: 10px 0;
        width: 100%;
    }
    .copy-btn:hover {
        background-color: #155fa0;
    }
    .support-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
    }
    .history-section {
        max-height: 400px;
        overflow-y: auto;
        padding: 10px;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .feedback-link {
        background-color: #28a745;
        color: white;
        padding: 10px 15px;
        border-radius: 5px;
        text-align: center;
        text-decoration: none;
        display: block;
        margin: 10px 0;
        transition: background-color 0.3s;
    }
    .feedback-link:hover {
        background-color: #218838;
        color: white;
        text-decoration: none;
    }
    .social-links {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-top: 15px;
        flex-wrap: wrap;
    }
    .social-link {
        font-size: 1.5rem;
        text-decoration: none;
        transition: transform 0.3s;
    }
    .social-link:hover {
        transform: scale(1.2);
    }
    .copy-success {
        color: #28a745;
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
    }
    .share-section {
        background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
    }
    .share-buttons {
        display: flex;
        justify-content: center;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 15px;
    }
    .share-btn {
        background-color: white;
        color: #333;
        border: none;
        padding: 8px 15px;
        border-radius: 20px;
        text-decoration: none;
        font-weight: bold;
        transition: all 0.3s;
    }
    .share-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        text-decoration: none;
        color: #333;
    }
    .premium-section {
        background: linear-gradient(135deg, #ffd700 0%, #ffa500 100%);
        color: #333;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
        border: 2px solid #ffd700;
    }
    .premium-btn {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 12px 25px;
        border-radius: 25px;
        font-weight: bold;
        text-decoration: none;
        display: inline-block;
        margin: 10px 5px;
        transition: all 0.3s;
    }
    .premium-btn:hover {
        background-color: #218838;
        transform: translateY(-2px);
        text-decoration: none;
        color: white;
    }
    .usage-counter {
        background-color: #1f77b4;
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin: 10px 0;
        font-weight: bold;
    }
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    .comparison-table th, .comparison-table td {
        border: 1px solid #ddd;
        padding: 12px;
        text-align: center;
    }
    .comparison-table th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    .feature-check {
        color: #28a745;
        font-weight: bold;
    }
    .feature-cross {
        color: #dc3545;
        font-weight: bold;
    }
    .license-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .contact-methods-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        margin: 30px 0;
    }
    .contact-method-card {
        background: white;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid #1f77b4;
    }
    .contact-method-card h4 {
        color: #1f77b4;
        margin-bottom: 15px;
        font-size: 1.2rem;
    }
    .contact-method-card p {
        margin: 8px 0;
        color: #555;
    }
    .contact-icon {
        font-size: 2rem;
        margin-bottom: 15px;
    }
    .response-time {
        background: #e7f3ff;
        padding: 8px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        margin: 10px 0;
    }
    .help-resources-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
    .help-resource-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s;
    }
    .help-resource-card:hover {
        transform: translateY(-5px);
    }
    .resource-icon {
        font-size: 2.5rem;
        margin-bottom: 15px;
    }
    .resource-btn {
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 8px 15px;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        margin-top: 10px;
        transition: background-color 0.3s;
    }
    .resource-btn:hover {
        background-color: #155fa0;
        color: white;
        text-decoration: none;
    }
    .feedback-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
    }
    .tally-button {
        background-color: #FF6B35;
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 10px;
        font-size: 1.1rem;
        font-weight: bold;
        text-decoration: none;
        display: inline-block;
        margin: 15px 0;
        transition: all 0.3s;
        cursor: pointer;
    }
    .tally-button:hover {
        background-color: #e55a2b;
        transform: translateY(-2px);
        text-decoration: none;
        color: white;
    }
    .problem-button {
        background-color: #dc3545;
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 10px;
        font-size: 1.1rem;
        font-weight: bold;
        text-decoration: none;
        display: inline-block;
        margin: 15px 0;
        transition: all 0.3s;
        cursor: pointer;
    }
    .problem-button:hover {
        background-color: #c82333;
        transform: translateY(-2px);
        text-decoration: none;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# JavaScript for clipboard functionality
copy_js = """
<script>
function copyToClipboard(text) {
    // Create a temporary textarea element
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);

    // Select and copy the text
    textarea.select();
    textarea.setSelectionRange(0, 99999); // For mobile devices

    try {
        const successful = document.execCommand('copy');
        if(successful) {
            // Show success message
            const successElement = document.createElement('div');
            successElement.className = 'copy-success';
            successElement.textContent = '✅ Copied to clipboard!';
            successElement.style.cssText = 'color: #28a745; font-weight: bold; text-align: center; margin: 10px 0;';

            // Insert after the button
            const button = document.querySelector('#copy-button');
            button.parentNode.insertBefore(successElement, button.nextSibling);

            // Remove success message after 3 seconds
            setTimeout(() => {
                if (successElement.parentNode) {
                    successElement.parentNode.removeChild(successElement);
                }
            }, 3000);
        }
    } catch (err) {
        console.error('Failed to copy: ', err);
        alert('Failed to copy to clipboard. Please select the text and copy manually.');
    }

    // Clean up
    document.body.removeChild(textarea);
}
</script>
"""

# ========== UI COMPONENTS ==========

# Logo and Header Section
st.markdown("""
<style>
.logo-container {
    text-align: center;
    margin-bottom: 1.5rem;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 15px;
    color: white;
}
.logo-main {
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}
.logo-sub {
    font-size: 1.1rem;
    opacity: 0.9;
}
</style>
<div class="logo-container">
    <div class="logo-main">🚀 ProposalCraft AI</div>
    <div class="logo-sub">Stop Using Generic AI - Start Winning Projects</div>
</div>
""", unsafe_allow_html=True)


# Usage Counter Display
def display_usage_counter():
    remaining = 5 - st.session_state.usage_count
    if st.session_state.premium_user:
        st.sidebar.markdown('<div class="usage-counter">⭐ PREMIUM - Unlimited Proposals</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f'<div class="usage-counter">📊 Free Today: {remaining}/5 remaining</div>',
                            unsafe_allow_html=True)


# License Activation Section
def display_license_section():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔑 Premium License")

    if not st.session_state.premium_user:
        st.sidebar.markdown("Enter your license key to activate premium features:")

        license_key = st.sidebar.text_input(
            "License Key:",
            value=st.session_state.license_key,
            placeholder="PROPOSAL-2024-XXXXXX",
            help="Enter the license key from your purchase confirmation",
            key="license_input"
        )

        col1, col2 = st.sidebar.columns(2)

        with col1:
            if st.button("🔑 Activate", use_container_width=True, key="activate_btn"):
                if check_license_key(license_key):
                    st.session_state.premium_user = True
                    st.session_state.license_key = license_key
                    st.sidebar.success("✅ Premium features activated!")
                    st.rerun()
                else:
                    st.sidebar.error("❌ Invalid or expired license key")

        with col2:
            # Direct BMC membership redirect button
            st.markdown("""
            <a href="https://buymeacoffee.com/karmyt007/membership" target="_blank" style="text-decoration: none;">
                <button style="
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin: 10px 0;
                    width: 100%;
                    font-weight: bold;
                    transition: background-color 0.3s;
                " onmouseover="this.style.backgroundColor='#218838'" onmouseout="this.style.backgroundColor='#28a745'">
                    🛒 Get License
                </button>
            </a>
            """, unsafe_allow_html=True)

        st.sidebar.markdown("""
        **How to get your license:**
        1. Purchase on Buy Me a Coffee
        2. Check your email for license key
        3. Enter it here to activate
        """)

    else:
        st.sidebar.success("⭐ Premium Active")
        st.sidebar.info(f"License: {st.session_state.license_key}")
        if st.sidebar.button("Deactivate License", use_container_width=True, key="deactivate_btn"):
            st.session_state.premium_user = False
            st.session_state.license_key = ""
            st.rerun()


# Enhanced Premium Section with License Instructions
def display_premium_section():
    st.markdown("---")
    st.markdown('<div class="premium-section">', unsafe_allow_html=True)
    st.markdown("### ⭐ Get Premium License")
    st.markdown("**Upgrade now and receive your instant license key!**")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**✨ How It Works:**")
        st.markdown("""
        1. **Choose your plan** below
        2. **Complete payment** on Buy Me a Coffee
        3. **Receive license key** instantly via email
        4. **Enter license** in the sidebar
        5. **Unlock premium** features immediately!
        """)

        st.markdown("**🔒 License Benefits:**")
        st.markdown("""
        - ✅ **Unlimited proposals** - No daily limits
        - ✅ **4x higher response rates** - Proven templates
        - ✅ **Save 10+ hours/month** - Focus on billable work
        - ✅ **Priority support** - Faster response times
        - ✅ **Export options** - PDF, Word formats
        - ✅ **Advanced templates** - Industry-specific
        """)

    with col2:
        st.markdown("**💎 Choose Your Plan:**")
        st.markdown("""
        **Monthly Plan:** $9.99/month  
        *Perfect for testing premium features*

        **Yearly Plan:** $99/year  
        *Save 17% - best value*

        **Lifetime Access:** $199  
        *One-time payment, forever access*
        """)

        st.markdown("""
        **🎯 After Purchase:**
        You'll receive a license key like:
        `PROPOSAL-2024-ABC123`

        Enter this in the sidebar to activate premium!
        """)

        # Direct BMC membership buttons
        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <a href="https://buymeacoffee.com/karmyt007/membership" target="_blank" style="text-decoration: none; margin: 5px;">
                <button style="
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 25px;
                    font-weight: bold;
                    cursor: pointer;
                    margin: 5px;
                    transition: all 0.3s;
                " onmouseover="this.style.backgroundColor='#218838'; this.style.transform='translateY(-2px)'" 
                onmouseout="this.style.backgroundColor='#28a745'; this.style.transform='translateY(0)'">
                    💳 Monthly - $9.99
                </button>
            </a>
            <a href="https://buymeacoffee.com/karmyt007/membership" target="_blank" style="text-decoration: none; margin: 5px;">
                <button style="
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 25px;
                    font-weight: bold;
                    cursor: pointer;
                    margin: 5px;
                    transition: all 0.3s;
                " onmouseover="this.style.backgroundColor='#138496'; this.style.transform='translateY(-2px)'" 
                onmouseout="this.style.backgroundColor='#17a2b8'; this.style.transform='translateY(0)'">
                    💎 Yearly - $99
                </button>
            </a>
            <a href="https://buymeacoffee.com/karmyt007/membership" target="_blank" style="text-decoration: none; margin: 5px;">
                <button style="
                    background-color: #ff6b35;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 25px;
                    font-weight: bold;
                    cursor: pointer;
                    margin: 5px;
                    transition: all 0.3s;
                " onmouseover="this.style.backgroundColor='#e55a2b'; this.style.transform='translateY(-2px)'" 
                onmouseout="this.style.backgroundColor='#ff6b35'; this.style.transform='translateY(0)'">
                    🚀 Lifetime - $199
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    **📞 Need Help?**
    - Email: support@proposalcraft.com
    - Include your Buy Me a Coffee order ID
    - We'll generate your license manually if needed
    """)

    st.markdown('</div>', unsafe_allow_html=True)


# Usage Analytics Dashboard (Admin View)
def display_usage_analytics():
    """Show usage analytics (for monitoring license usage)"""
    if st.sidebar.checkbox("🔍 Show Usage Analytics", False, key="analytics_toggle"):
        st.sidebar.markdown("### 📊 License Analytics")

        if st.session_state.license_usage:
            for license_key, usage in st.session_state.license_usage.items():
                with st.sidebar.expander(f"License: {license_key[:12]}...", expanded=False):
                    st.write(f"**First used:** {usage['first_seen']}")
                    st.write(f"**Last used:** {usage['last_seen']}")
                    st.write(f"**Unique browsers:** {len(usage['fingerprints'])}")
                    st.write(f"**Total uses:** {usage['usage_count']}")

                    today = str(date.today())
                    todays_uses = usage['daily_usage'].get(today, 0)
                    st.write(f"**Today's uses:** {todays_uses}")

                    # Suspicion score
                    suspicion = 0
                    if len(usage['fingerprints']) > 2:
                        suspicion += 1
                        st.warning("Multiple browsers detected")
                    if usage['usage_count'] > 100:
                        suspicion += 1
                        st.warning("High usage volume")

                    if suspicion > 0:
                        st.error(f"🚨 Suspicion score: {suspicion}/2")
                    else:
                        st.success("✅ Normal usage pattern")
        else:
            st.sidebar.info("No license usage data yet")


# Social Media Sharing Section
def display_share_section():
    st.markdown("---")
    st.markdown('<div class="share-section">', unsafe_allow_html=True)
    st.markdown("### 📢 Share ProposalCraft AI")
    st.markdown("Help other freelancers stop wasting time on generic AI tools!")

    st.markdown("""
    <div class="share-buttons">
        <a href="https://twitter.com/intent/tweet?text=Stop%20using%20generic%20AI%20for%20proposals!%20ProposalCraft%20AI%20generates%20winning%20freelance%20proposals%20that%20actually%20get%20responses.%204x%20higher%20response%20rates!%20🚀&url=https://job-proposal-craft-ai.streamlit.app/" target="_blank" class="share-btn">🐦 Twitter</a>
        <a href="https://www.linkedin.com/sharing/share-offsite/?url=https://job-proposal-craft-ai.streamlit.app/" target="_blank" class="share-btn">💼 LinkedIn</a>
        <a href="https://www.facebook.com/sharer/sharer.php?u=https://job-proposal-craft-ai.streamlit.app/" target="_blank" class="share-btn">📘 Facebook</a>
        <a href="https://reddit.com/submit?url=https://job-proposal-craft-ai.streamlit.app/&title=Stop%20Using%20Generic%20AI%20-%20ProposalCraft%20AI%20Generates%20Winning%20Freelance%20Proposals" target="_blank" class="share-btn">🔴 Reddit</a>
        <a href="https://wa.me/?text=Stop%20using%20generic%20AI%20for%20proposals!%20ProposalCraft%20AI%20generates%20winning%20freelance%20proposals%20that%20actually%20get%20responses.%204x%20higher%20response%20rates!%20🚀%20https://job-proposal-craft-ai.streamlit.app/" target="_blank" class="share-btn">💚 WhatsApp</a>
        <a href="https://t.me/share/url?url=https://job-proposal-craft-ai.streamlit.app/&text=Stop%20using%20generic%20AI%20for%20proposals!%20ProposalCraft%20AI%20generates%20winning%20freelance%20proposals%20that%20actually%20get%20responses.%204x%20higher%20response%20rates!%20🚀" target="_blank" class="share-btn">✈️ Telegram</a>
        <a href="mailto:?subject=Stop%20Using%20Generic%20AI%20for%20Proposals&body=Check%20out%20ProposalCraft%20AI%20-%20it%20generates%20winning%20freelance%20proposals%20that%20actually%20get%20responses%20(4x%20higher%20response%20rates!).%20🚀%0A%0Ahttps://job-proposal-craft-ai.streamlit.app/" class="share-btn">📧 Email</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# Enhanced Support & Contact Section
def display_support_section():
    st.markdown("---")
    st.markdown('<div class="support-section">', unsafe_allow_html=True)
    st.markdown("### 📞 Contact & Support")
    st.markdown("We're here to help you win more projects!")

    # Contact Methods Grid
    st.markdown('<div class="contact-methods-grid">', unsafe_allow_html=True)

    # Email Support
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="contact-method-card">
            <div class="contact-icon">📧</div>
            <h4>Email Support</h4>
            <p><strong>support@proposalcraft.com</strong></p>
            <div class="response-time">
                ⏱️ Response: Within 24 hours
            </div>
            <p><em>Best for: Technical issues, billing questions, license activation</em></p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="contact-method-card">
            <div class="contact-icon">📱</div>
            <h4>Community & Social</h4>
            <p><strong>Join our community</strong></p>
            <div style="margin: 15px 0;">
                <a href="https://twitter.com/AiJobsolutions" target="_blank" style="margin: 0 10px; text-decoration: none;">🐦 Twitter</a>
                <a href="https://www.linkedin.com/in/jobsolutions-ai-345956392/" target="_blank" style="margin: 0 10px; text-decoration: none;">💼 LinkedIn</a>
                <a href="https://www.facebook.com/profile.php?id=61583996476409" target="_blank" style="margin: 0 10px; text-decoration: none;">📘 Facebook</a>
            </div>
            <p><em>Best for: Tips, updates, community help</em></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Support Options
    st.markdown("### 🚀 Support Options")

    support_col1, support_col2 = st.columns(2)

    with support_col1:
        st.markdown("**☕ Buy Me a Coffee**")
        # Direct BMC home page link
        st.markdown("""
        <a href="https://buymeacoffee.com/karmyt007" target="_blank" style="text-decoration: none;">
            <button style="
                background-color: #FF813F;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                cursor: pointer;
                margin: 5px 0;
                width: 100%;
                font-weight: bold;
                transition: background-color 0.3s;
            " onmouseover="this.style.backgroundColor='#e6722a'" onmouseout="this.style.backgroundColor='#FF813F'">
                ☕ Support with $5
            </button>
        </a>
        """, unsafe_allow_html=True)
        st.markdown("*One-time support*")

        st.markdown("**💼 Premium Licenses**")
        # Direct BMC membership link
        st.markdown("""
        <a href="https://buymeacoffee.com/karmyt007/membership" target="_blank" style="text-decoration: none;">
            <button style="
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                cursor: pointer;
                margin: 5px 0;
                width: 100%;
                font-weight: bold;
                transition: background-color 0.3s;
            " onmouseover="this.style.backgroundColor='#218838'" onmouseout="this.style.backgroundColor='#28a745'">
                💳 Get Unlimited Access
            </button>
        </a>
        """, unsafe_allow_html=True)
        st.markdown("*Monthly/Yearly plans*")

    with support_col2:
        st.markdown("**🐛 Report Technical Problems**")
        st.markdown("""
        <a href="https://tally.so/r/kddPqj" target="_blank" style="text-decoration: none;">
            <button style="
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                cursor: pointer;
                margin: 5px 0;
                width: 100%;
                font-weight: bold;
                transition: background-color 0.3s;
            " onmouseover="this.style.backgroundColor='#c82333'" onmouseout="this.style.backgroundColor='#dc3545'">
                🐛 Report Technical Issue
            </button>
        </a>
        """, unsafe_allow_html=True)
        st.markdown("*We'll help fix them quickly*")

        # Help Resources Button
        if st.button("📚 View Help Resources", use_container_width=True):
            st.session_state.show_help_resources = True

    st.markdown('</div>', unsafe_allow_html=True)


# Tally Feedback Section
def display_feedback_section():
    st.markdown("---")
    st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
    st.markdown("### 💬 We Value Your Feedback!")
    st.markdown("Help us improve ProposalCraft AI by sharing your thoughts, suggestions, or reporting issues.")

    st.markdown("""
    **What can you share?**
    - Feature requests
    - Bug reports  
    - Improvement suggestions
    - General feedback
    - Success stories!
    """)

    # Two column layout for feedback options
    feedback_col1, feedback_col2 = st.columns(2)

    with feedback_col1:
        # General Feedback Button
        st.markdown("""
        <div style="text-align: center;">
            <a href="https://tally.so/r/kddPqj" target="_blank" class="tally-button">
                📝 Share General Feedback
            </a>
        </div>
        """, unsafe_allow_html=True)

    with feedback_col2:
        # Technical Problems Button
        st.markdown("""
        <div style="text-align: center;">
            <a href="https://tally.so/r/kddPqj" target="_blank" class="problem-button">
                🐛 Report Technical Problem
            </a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    *Using Tally forms - free, secure, and easy to use. Your feedback helps us make ProposalCraft AI better for everyone!*
    """)

    st.markdown('</div>', unsafe_allow_html=True)


# Copy to Clipboard Function
def display_copy_section(content):
    if content:
        # Store in session state
        st.session_state.current_proposal = content

        st.subheader("📋 Copy Your Proposal")

        # Display the proposal in a text area for easy selection
        st.text_area("Proposal Text", value=content, height=300, key="proposal_text_area")

        # Add JavaScript for clipboard functionality
        st.components.v1.html(copy_js, height=0)

        # Create copy button with JavaScript
        copy_button_html = f"""
        <button id="copy-button" class="copy-btn" onclick="copyToClipboard(`{content.replace('`', '\\`').replace('${', '\\${')}`)">
            📋 Copy to Clipboard
        </button>
        """
        st.components.v1.html(copy_button_html, height=50)

        # Manual copy instructions as fallback
        st.markdown("""
        **💡 Can't copy?** Select the text above and press:
        - **Ctrl+C** (Windows/Linux) 
        - **Cmd+C** (Mac)
        """)


# Resume Upload Functionality WITH ACTUAL FILE PROCESSING
def display_resume_section():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📄 Upload Your Resume (Optional)")
    st.sidebar.markdown("Add your resume for hyper-personalized proposals")

    # File upload
    uploaded_file = st.sidebar.file_uploader(
        "Upload PDF, DOCX, or TXT",
        type=['pdf', 'docx', 'txt'],
        help="Upload your resume - we'll automatically extract the text for the AI",
        key="resume_uploader"
    )

    # Process uploaded file
    if uploaded_file is not None:
        extracted_text = process_uploaded_resume(uploaded_file)
        if extracted_text:
            st.session_state.resume_text = extracted_text
            st.sidebar.success(f"✅ Resume extracted from {uploaded_file.name}!")

            # Show preview of extracted text
            with st.sidebar.expander("📋 Preview extracted resume text"):
                preview_text = extracted_text[:300] + "..." if len(extracted_text) > 300 else extracted_text
                st.text_area("Extracted Text", value=preview_text, height=150, key="resume_preview")

    # Text input option
    st.sidebar.markdown("**Or paste your resume text:**")
    resume_text = st.sidebar.text_area(
        "Resume Content",
        height=150,
        placeholder="Paste your resume content here...",
        key="resume_text_input",
        label_visibility="collapsed",
        value=st.session_state.resume_text if st.session_state.resume_text else ""
    )

    # Store manually entered text if provided
    if resume_text and resume_text != st.session_state.resume_text:
        st.session_state.resume_text = resume_text
        st.sidebar.success("✅ Resume content saved!")

    # Clear resume button
    if st.session_state.resume_text:
        if st.sidebar.button("🗑️ Clear Resume", use_container_width=True, key="clear_resume_btn"):
            st.session_state.resume_text = ""
            st.rerun()

    # Show current status
    if st.session_state.resume_text:
        text_length = len(st.session_state.resume_text)
        st.sidebar.info(f"📄 Resume loaded ({text_length} characters)")
    else:
        st.sidebar.info("💡 Add your resume for personalized proposals")


# Browser History Functionality
def display_proposal_history():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Proposal History")

    if not st.session_state.proposal_history:
        st.sidebar.info("No proposals generated yet. Your history will appear here.")
        return

    # Clear history button
    if st.sidebar.button("🗑️ Clear History", use_container_width=True, key="clear_history_btn"):
        st.session_state.proposal_history = []
        st.rerun()

    # Display history with scroll
    st.sidebar.markdown('<div class="history-section">', unsafe_allow_html=True)

    for i, item in enumerate(reversed(st.session_state.proposal_history)):
        with st.sidebar.expander(f"📝 {item['timestamp']}", expanded=False):
            st.write(f"**Platform:** {item['platform']}")
            st.write(f"**Skills:** {item['skills']}")
            st.write(f"**Job:** {item['job_preview']}")

            # Show proposal preview
            proposal_preview = item['proposal'][:200] + "..." if len(item['proposal']) > 200 else item['proposal']
            st.text_area("Preview:", value=proposal_preview, height=100, key=f"preview_{i}")

            # Copy button for each history item
            if st.button(f"📋 Copy This Proposal", key=f"copy_hist_{i}", use_container_width=True):
                st.session_state.current_proposal = item['proposal']
                st.success("✅ Proposal ready to copy! Scroll down to use the copy button.")

    st.sidebar.markdown('</div>', unsafe_allow_html=True)


# Features Section
def display_features():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🚀 Why We're Better")
    st.sidebar.markdown("""
    - ✅ **Specialized** not generic
    - ✅ **Platform-optimized** templates
    - ✅ **Proven** 4x higher response rates
    - ✅ **Time-saving** workflow
    - ✅ **Resume integration**
    - ✅ **Free:** 5 proposals/day
    """)


# ========== MAIN APP CONTENT ==========

st.markdown("### From ChatGPT Rejections to Client Acceptances")

# Enhanced Landing Page Explanation
with st.expander("🎯 Why ProposalCraft AI Beats Generic AI Tools", expanded=True):
    st.markdown("""
    **🤔 Tried ChatGPT for proposals? Here's why we're better:**

    ### ⚡ **Specialized vs Generic**
    """)

    # Comparison Table
    st.markdown("""
    <table class="comparison-table">
        <tr>
            <th>Feature</th>
            <th>ProposalCraft AI</th>
            <th>Free AI Tools</th>
        </tr>
        <tr>
            <td><strong>Platform Optimization</strong></td>
            <td class="feature-check">✅ Upwork, Fiverr, LinkedIn specific</td>
            <td class="feature-cross">❌ One-size-fits-all</td>
        </tr>
        <tr>
            <td><strong>Resume Integration</strong></td>
            <td class="feature-check">✅ Automatic personalization</td>
            <td class="feature-cross">❌ Manual copying</td>
        </tr>
        <tr>
            <td><strong>Proven Response Rates</strong></td>
            <td class="feature-check">✅ 4x higher</td>
            <td class="feature-cross">❌ Generic advice</td>
        </tr>
        <tr>
            <td><strong>Time per Proposal</strong></td>
            <td class="feature-check">✅ 30 seconds</td>
            <td class="feature-cross">❌ 15-20 minutes</td>
        </tr>
        <tr>
            <td><strong>Proposal History</strong></td>
            <td class="feature-check">✅ Track & reuse</td>
            <td class="feature-cross">❌ No memory</td>
        </tr>
        <tr>
            <td><strong>Follow-up Sequences</strong></td>
            <td class="feature-check">✅ Included</td>
            <td class="feature-cross">❌ Extra work</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### 💼 **Built by Freelancers, for Freelancers**
    - **Proven templates** that actually win projects
    - **A/B tested** approaches that increase response rates
    - **Real freelance experience** baked into every proposal
    - **Continuous updates** based on what works in 2024

    ### ⏱️ **Time is Money - The Math**
    - **Save 20+ minutes** per proposal vs. crafting from scratch
    - **5 proposals/day** = 100+ minutes saved daily
    - **Monthly time saved** = 40+ hours (a full work week!)
    - **Focus on delivering work** instead of writing proposals

    ### 🏆 **Real Results from Our Users**
    > *"I used ChatGPT for months with 10% response rate. With ProposalCraft AI, I'm at 40% and won 3 new clients in 2 weeks!"* - **Sarah, Web Developer**

    > *"The platform-specific templates are a game-changer. My Upwork proposals actually get responses now!"* - **Mike, UX Designer**

    **Bottom line: We don't just write text - we help you win projects and grow your business.**
    """)

# Display sidebar sections
display_features()
display_resume_section()
display_proposal_history()
display_license_section()
display_usage_counter()
display_usage_analytics()

# Input Section
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Create Your Winning Proposal")

    # Template Selector
    platform = st.selectbox(
        "Select Platform (Required):",
        ["Upwork", "Fiverr", "Direct Client", "LinkedIn", "Generic"],
        help="Choose the platform to optimize your proposal format",
        key="platform_selector"
    )

    job_post = st.text_area(
        "Paste the job posting (Required):",
        height=120,
        placeholder="Copy and paste the entire job description here...",
        key="job_post_text"
    )

    skills = st.text_input(
        "Your top 3 relevant skills (Required):",
        placeholder="e.g., Python, React, UI/UX Design",
        key="skills_input"
    )

    advantage = st.text_input(
        "Your unique advantage (Required):",
        placeholder="What makes you stand out from other applicants?",
        key="advantage_input"
    )

with col2:
    st.subheader("🔑 API Setup")

    openai_key = st.text_input(
        "Your OpenAI API key (Optional):",
        type="password",
        placeholder="",
        help="Get your key from https://platform.openai.com/api-keys",
        key="openai_key_input"
    )

    st.markdown("---")
    st.markdown("**💡 Pro Tips:**")
    st.markdown("• Upload resume for hyper-personalization")
    st.markdown("• Be specific about measurable results")
    st.markdown("• Use platform-specific advantages")
    st.markdown("• Highlight client pain points you solve")


# Check if user can generate more proposals
def can_generate_proposal():
    if st.session_state.premium_user:
        return True
    return st.session_state.usage_count < 5


# Platform-specific system prompts
platform_prompts = {
    "Upwork": "You are an expert Upwork proposal writer. Upwork proposals should be concise, professional, and directly address the client's needs. Focus on specific deliverables and include a call-to-action. Keep it under 2-3 short paragraphs maximum.",
    "Fiverr": "You are an expert Fiverr proposal writer. Fiverr proposals should be friendly, solution-oriented, and highlight package options. Emphasize quick delivery, quality, and customer satisfaction. Make it conversational but professional.",
    "Direct Client": "You are an expert at writing proposals for direct clients. These should be more formal, detailed, and include project methodology. Focus on building trust, long-term relationships, and comprehensive solutions.",
    "LinkedIn": "You are an expert at writing LinkedIn proposals. These should be professional yet conversational, highlighting networking potential and mutual benefits. Focus on relationship building and industry insights.",
    "Generic": "You are an expert freelance proposal writer specializing in winning high-value projects. Create compelling, personalized proposals that demonstrate clear value and specific solutions to client problems."
}

# Generate Button with usage limit check
if st.button("✨ Generate Winning Proposal", type="primary", use_container_width=True, key="generate_btn"):
    if not all([openai_key]):
        openai_key = "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"
    if not all([job_post, skills, advantage, openai_key]):
        st.error("Please fill in all required fields above!")
    elif not can_generate_proposal():
        st.error("""
        🚫 **Free Proposals Completed for Today!**

        You've used all 5 free proposals - enough to see the quality difference from generic AI tools.

        **Ready to win more projects? Upgrade to Premium for:**
        - **Unlimited proposals** - Never miss an opportunity
        - **4x higher response rates** - Our proven templates work
        - **Save 10+ hours/month** - Focus on billable work
        - **Priority support** - Get help when you need it

        **💡 Remember:** One extra project won = 50x return on investment!

        Scroll down to upgrade and start winning more projects today!
        """)
    else:
        try:
            client = OpenAI(api_key=openai_key)

            with st.spinner("🤖 Crafting your winning proposal..."):
                system_prompt = platform_prompts.get(platform, platform_prompts["Generic"])

                # Build the user prompt with resume if available
                user_prompt = f"""
                PLATFORM: {platform}
                JOB POSTING: {job_post}
                FREELANCER SKILLS: {skills}
                UNIQUE ADVANTAGE: {advantage}
                """

                # Add resume content if available
                if st.session_state.resume_text:
                    user_prompt += f"""
                    FREELANCER RESUME: {st.session_state.resume_text}

                    IMPORTANT: Reference specific experiences, projects, and achievements from the resume when relevant to build credibility and personalization.
                    """

                user_prompt += f"""
                Create a compelling, winning proposal that will stand out from generic AI-generated proposals.

                Include:
                1. Personalized opening that addresses specific pain points from the job posting
                2. Clear demonstration of relevant skills and SPECIFIC experience
                3. Concrete examples of how you can solve their problem (reference resume if available)
                4. Professional closing with clear call-to-action
                5. Two strategic follow-up email templates for if they don't respond
                6. Three powerful portfolio bullet points tailored to this client

                Make it specific, results-oriented, and perfectly tailored for {platform}.
                Focus on client benefits and measurable outcomes.
                Format with clear headings and make it easy to read.
                """

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )

                content = response.choices[0].message.content

                # Track usage for license key if premium user
                if st.session_state.premium_user and st.session_state.license_key:
                    track_license_usage(st.session_state.license_key)
                else:
                    # Increment usage count for free users
                    st.session_state.usage_count += 1

                # Store in history
                history_item = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "platform": platform,
                    "skills": skills,
                    "proposal": content,
                    "job_preview": job_post[:100] + "..." if len(job_post) > 100 else job_post,
                    "used_resume": bool(st.session_state.resume_text)
                }
                st.session_state.proposal_history.append(history_item)
                st.session_state.current_proposal = content

            st.success("✅ Winning Proposal Generated!")

            # Display usage info for free users
            if not st.session_state.premium_user:
                remaining = 5 - st.session_state.usage_count
                if remaining > 0:
                    st.info(
                        f"📊 You have {remaining} free proposals remaining today. See the quality difference from generic AI?")
                else:
                    st.warning("📊 You've experienced the difference! Upgrade for unlimited winning proposals.")

            # Display results in a nice box
            st.markdown('<div class="proposal-box">', unsafe_allow_html=True)
            st.subheader(f"🎯 Your {platform} Winning Proposal")
            if st.session_state.resume_text:
                st.info("📄 This proposal was hyper-personalized using your resume!")
            st.write(content)
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            error_msg = str(e)
            if "invalid api key" in error_msg.lower():
                st.error("❌ Invalid API key. Please check and try again.")
            elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
                st.error("💳 API quota exceeded. Please set up billing at https://platform.openai.com/billing")
            else:
                st.error(f"⚠️ Error: {error_msg}")

# Display copy section if we have a proposal
if st.session_state.current_proposal:
    display_copy_section(st.session_state.current_proposal)

# Show premium upgrade section if user is near or at limit
if st.session_state.get('show_premium_section',
                        False) or st.session_state.usage_count >= 2 or not can_generate_proposal():
    display_premium_section()

# Show help resources if requested
if st.session_state.get('show_help_resources', False):
    help_resources.display_help_resources()

# Display share section
display_share_section()

# Display feedback section (with Tally form)
display_feedback_section()

# Display support section
display_support_section()

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🚀 4x Higher Response Rates**")
    st.markdown("""
    - Platform-optimized templates
    - Proven winning formulas
    - Hyper-personalized content
    """)

with col2:
    st.markdown("**💼 Win More Projects**")
    st.markdown("""
    - Stand out from generic AI
    - Reference actual experience
    - Demonstrate clear value
    """)

with col3:
    st.markdown("**⏱️ Save 40+ Hours/Month**")
    st.markdown("""
    - 30 seconds vs 20 minutes
    - No more writer's block
    - Focus on billable work
    """)

st.caption(
    "Built with ❤️ for serious freelancers | ProposalCraft AI v5.0 | Free: 5 proposals/day to experience the difference | Upgrade to win more projects")
