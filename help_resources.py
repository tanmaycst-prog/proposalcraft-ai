# help_resources.py
import streamlit as st


def display_help_resources():
    """Display comprehensive help resources for ProposalCraft AI"""

    # Custom CSS for help resources
    st.markdown("""
    <style>
    .help-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
    }
    .resource-section {
        background: white;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 20px 0;
        border-left: 5px solid #667eea;
    }
    .quick-link-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    .quick-link-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        text-decoration: none;
        color: #333;
        border: 2px solid #e9ecef;
        transition: all 0.3s;
    }
    .quick-link-card:hover {
        background: #667eea;
        color: white;
        transform: translateY(-3px);
        text-decoration: none;
    }
    .step-number {
        background: #667eea;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
        font-weight: bold;
    }
    .video-container {
        position: relative;
        padding-bottom: 56.25%;
        height: 0;
        margin: 20px 0;
    }
    .video-container iframe {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border-radius: 10px;
    }
    .tip-card {
        background: #e7f3ff;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #1f77b4;
    }
    .platform-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 15px 0;
    }
    .contact-banner {
        background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%);
        color: white;
        padding: 25px;
        border-radius: 10px;
        text-align: center;
        margin: 30px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="help-header">
        <h1>📚 ProposalCraft AI Help Center</h1>
        <p>Everything you need to create winning proposals and grow your freelance business</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick Links
    st.markdown("### 🚀 Quick Links")
    st.markdown("""
    <div class="quick-link-grid">
        <a href="#getting-started" class="quick-link-card">🚀 Getting Started</a>
        <a href="#best-practices" class="quick-link-card">💡 Best Practices</a>
        <a href="#platform-tips" class="quick-link-card">🎯 Platform Tips</a>
        <a href="#faq" class="quick-link-card">❓ FAQ</a>
        <a href="#troubleshooting" class="quick-link-card">🔧 Troubleshooting</a>
        <a href="#contact" class="quick-link-card">📞 Contact</a>
    </div>
    """, unsafe_allow_html=True)

    # Getting Started Section
    st.markdown('<div id="getting-started"></div>', unsafe_allow_html=True)
    st.markdown("## 🚀 Getting Started Guide")

    with st.expander("### Step-by-Step Guide", expanded=True):
        st.markdown("""
            <h4><span class="step-number">1</span> Set Up Your OpenAI API Key</h4>
            <p><strong>Why you need it:</strong> ProposalCraft AI uses your OpenAI API key to generate proposals. This keeps our costs low so we can offer free daily proposals.</p>
            <p><strong>How to get it:</strong></p>
            <ul>
                <li>Go to <a href="https://platform.openai.com/api-keys" target="_blank">OpenAI API Keys</a></li>
                <li>Create an account or sign in</li>
                <li>Click "Create new secret key"</li>
                <li>Copy the key and paste it in the app</li>
            </ul>

            <h4><span class="step-number">2</span> Understand Your Free Tier</h4>
            <p><strong>5 free proposals per day</strong> - enough to experience the quality difference</p>
            <p><strong>Unlimited with premium</strong> - upgrade for unlimited proposals and advanced features</p>

            <h4><span class="step-number">3</span> Upload Your Resume (Optional but Recommended)</h4>
            <p>Upload your resume or paste the text to enable hyper-personalized proposals that reference your actual experience.</p>

            <h4><span class="step-number">4</span> Generate Your First Proposal</h4>
            <p>Fill in the job posting, your skills, and unique advantage, then click "Generate Winning Proposal".</p>
            
        """, unsafe_allow_html=True)

    # Best Practices Section
    st.markdown('<div id="best-practices"></div>', unsafe_allow_html=True)
    st.markdown("## 💡 Best Practices for Winning Proposals")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <h4>🎯 What Makes a Proposal Stand Out</h4>

            <div class="tip-card">
                <strong>✅ Address Specific Pain Points</strong>
                <p>Read the job description carefully and address the client's specific problems.</p>
            </div>

            <div class="tip-card">
                <strong>✅ Show, Don't Just Tell</strong>
                <p>Instead of "I'm a great developer," say "I built a similar e-commerce site that increased sales by 40%."</p>
            </div>

            <div class="tip-card">
                <strong>✅ Be Specific About Results</strong>
                <p>Use numbers and metrics: "reduced load time by 2 seconds," "increased conversions by 25%."</p>
            </div>

            <div class="tip-card">
                <strong>✅ Keep it Client-Focused</strong>
                <p>Focus on how you can help THEM, not just listing your skills.</p>
            </div>
            
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <h4>⏱️ Time-Saving Strategies</h4>

            <div class="tip-card">
                <strong>💡 Use Resume Integration</strong>
                <p>Upload your resume once and let the AI reference your specific experience in every proposal.</p>
            </div>

            <div class="tip-card">
                <strong>💡 Save Successful Templates</strong>
                <p>When you get a positive response, save that proposal style in your history for similar jobs.</p>
            </div>

            <div class="tip-card">
                <strong>💡 Batch Your Proposals</strong>
                <p>Set aside 30 minutes daily to send 5-10 proposals rather than one at a time.</p>
            </div>

            <div class="tip-card">
                <strong>💡 Track What Works</strong>
                <p>Use the proposal history to see which approaches get the best responses.</p>
            </div>
        """, unsafe_allow_html=True)

    # Platform-Specific Tips
    st.markdown('<div id="platform-tips"></div>', unsafe_allow_html=True)
    st.markdown("## 🎯 Platform-Specific Tips")

    platforms = {
        "Upwork": {
            "tips": [
                "Keep proposals concise (2-3 paragraphs max)",
                "Address the client by name if possible",
                "Focus on specific deliverables mentioned in the job post",
                "Include a clear call-to-action",
                "Mention relevant Upwork hours or completed jobs"
            ],
            "character": "Professional, direct, results-focused"
        },
        "Fiverr": {
            "tips": [
                "Friendly and conversational tone",
                "Highlight package options and quick delivery",
                "Emphasize customer satisfaction and revisions",
                "Mention similar gigs you've completed",
                "Focus on solving their immediate problem"
            ],
            "character": "Friendly, solution-oriented, package-driven"
        },
        "LinkedIn": {
            "tips": [
                "More professional and relationship-focused",
                "Highlight networking potential",
                "Reference mutual connections if any",
                "Focus on long-term collaboration",
                "Include industry insights"
            ],
            "character": "Professional, conversational, relationship-building"
        },
        "Direct Client": {
            "tips": [
                "More formal and detailed",
                "Include project methodology",
                "Focus on building trust and long-term relationships",
                "Provide comprehensive solutions",
                "Include next steps and timeline"
            ],
            "character": "Formal, detailed, trust-building"
        }
    }

    for platform, info in platforms.items():
        with st.expander(f"### {platform} Proposals"):
            st.markdown(f"**Character:** {info['character']}")
            st.markdown("**Key Tips:**")
            for tip in info['tips']:
                st.markdown(f"• {tip}")

    # Video Tutorials Section
    st.markdown("## 🎥 Video Tutorials")

    st.markdown("""
    <div class="resource-section">
        <p><strong>Coming Soon!</strong> We're creating detailed video tutorials to help you get the most out of ProposalCraft AI.</p>
        <p>In the meantime, here's what we'll cover:</p>
        <ul>
            <li>🚀 Getting started in 5 minutes</li>
            <li>💡 Advanced proposal strategies</li>
            <li>🎯 Platform-specific deep dives</li>
            <li>📈 How to increase your response rates</li>
            <li>⚡ Time-saving workflows</li>
        </ul>
        <p><em>Sign up for our newsletter to be notified when tutorials are released!</em></p>
    </div>
    """, unsafe_allow_html=True)

    # FAQ Section
    st.markdown('<div id="faq"></div>', unsafe_allow_html=True)
    st.markdown("## ❓ Frequently Asked Questions")

    faq_items = [
        {
            "question": "How many free proposals do I get per day?",
            "answer": "Free users get 5 proposals per day. This is enough to experience the quality difference from generic AI tools. Premium users get unlimited proposals."
        },
        {
            "question": "Why do I need my own OpenAI API key?",
            "answer": "Using your own API key keeps our costs low, allowing us to offer free daily proposals. It also ensures you have control over your usage and costs."
        },
        {
            "question": "How do I get a premium license?",
            "answer": "Purchase a license through Buy Me a Coffee. You'll receive your license key via email, which you can enter in the sidebar to activate premium features."
        },
        {
            "question": "Is my data safe?",
            "answer": "Yes! We don't store your job postings, resume data, or generated proposals. Your OpenAI API key is used only for generating proposals and isn't stored by us."
        },
        {
            "question": "Can I use this for multiple freelance platforms?",
            "answer": "Absolutely! We have optimized templates for Upwork, Fiverr, LinkedIn, direct clients, and generic proposals."
        },
        {
            "question": "What makes ProposalCraft better than ChatGPT?",
            "answer": "We provide specialized templates optimized for freelance platforms, proven formulas that get 4x higher response rates, resume integration, and platform-specific best practices that generic AI tools don't offer."
        },
        {
            "question": "How does the resume integration work?",
            "answer": "When you upload your resume or paste the text, our AI references your specific experience, skills, and achievements to create hyper-personalized proposals that stand out from generic applications."
        },
        {
            "question": "What if I need technical support?",
            "answer": "Contact us at support@proposalcraft.com. Premium users receive priority support with faster response times."
        }
    ]

    for i, faq in enumerate(faq_items):
        with st.expander(f"**Q: {faq['question']}**"):
            st.markdown(faq['answer'])

    # Troubleshooting Section
    st.markdown('<div id="troubleshooting"></div>', unsafe_allow_html=True)
    st.markdown("## 🔧 Troubleshooting")

    troubleshooting_items = [
        {
            "issue": "Proposal generation fails",
            "solution": "Check your OpenAI API key is valid and has sufficient credits. Make sure all required fields are filled."
        },
        {
            "issue": "API key errors",
            "solution": "Ensure your OpenAI API key is correct and active. You can generate a new key at https://platform.openai.com/api-keys"
        },
        {
            "issue": "License key not working",
            "solution": "Make sure you're entering the exact license key received via email. Contact support@proposalcraft.com if issues persist."
        },
        {
            "issue": "Proposal quality concerns",
            "solution": "Try being more specific in your skills and advantages. Use resume integration for better personalization. The AI works best with detailed inputs."
        },
        {
            "issue": "Browser issues",
            "solution": "Try refreshing the page or using a different browser. Clear your browser cache if problems persist."
        }
    ]

    for issue in troubleshooting_items:
        with st.expander(f"**Issue: {issue['issue']}**"):
            st.markdown(f"**Solution:** {issue['solution']}")

    # Contact Section
    st.markdown('<div id="contact"></div>', unsafe_allow_html=True)
    st.markdown("""
        <h3>📞 Still Need Help?</h3>
        <p>We're here to support your success! Reach out to us through any of these channels:</p>

        <div style="margin: 20px 0;">
            <strong>📧 Email Support:</strong> support@proposalcraft.com<br>
            <strong>🐦 Twitter:</strong> @ProposalCraftAI<br>
            <strong>💼 LinkedIn:</strong> ProposalCraft AI<br>
            <strong>📘 Facebook:</strong> @ProposalCraftAI
        </div>

        <p><strong>Response Times:</strong><br>
        • Premium Users: 4-6 hours<br>
        • Free Users: Within 24 hours</p>

        <p>Don't forget to check our FAQ section above for quick answers!</p>
    """, unsafe_allow_html=True)

    # Success Stories
    st.markdown("## 🏆 Success Stories")

    success_stories = [
        {
            "name": "Sarah, Web Developer",
            "story": "I was using ChatGPT for proposals with a 10% response rate. With ProposalCraft AI, I'm now at 40% and won 3 new clients in 2 weeks! The platform-specific templates made all the difference."
        },
        {
            "name": "Mike, UX Designer",
            "story": "The resume integration is a game-changer. My proposals now reference my actual portfolio projects, and clients notice the personalization. My response rate tripled!"
        },
        {
            "name": "Alex, Content Writer",
            "story": "I was spending 20+ minutes on each proposal. Now I can send 10 quality proposals in the time it used to take for 2. The time savings alone is worth the premium license."
        },
        {
            "name": "Jessica, Digital Marketer",
            "story": "The Upwork-specific templates helped me stand out in a crowded marketplace. I went from getting ignored to landing my highest-paying client ever."
        }
    ]

    for story in success_stories:
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 15px 0; border-left: 4px solid #28a745;">
            <strong>"{story['story']}"</strong><br>
            <em>— {story['name']}</em>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main function to run the help resources as a standalone app"""
    st.set_page_config(
        page_title="ProposalCraft AI - Help Resources",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    display_help_resources()


if __name__ == "__main__":
    main()
