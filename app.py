"""
UX Heuristics Analyzer - Streamlit Web Application
Interactive webapp for analyzing images, videos, and websites against UX principles
"""

import streamlit as st
import json
import os
import tempfile
from typing import Dict, Any
import time
from PIL import Image # Add missing import
from ux_analyzer import UXAnalyzer
from website_capture import WebsiteCapture

# Page configuration
st.set_page_config(
    page_title="UX Heuristics Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .analysis-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .score-display {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    
    .score-excellent { color: #28a745; }
    .score-good { color: #17a2b8; }
    .score-fair { color: #ffc107; }
    .score-poor { color: #dc3545; }
    
    .category-header {
        background: #e9ecef;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        font-weight: bold;
    }
    
    .checkpoint-pass { color: #28a745; }
    .checkpoint-fail { color: #dc3545; }
    .checkpoint-attention { color: #ffc107; }
    
    .recommendation-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = UXAnalyzer()
    if 'analyzing' not in st.session_state:
        st.session_state.analyzing = False

def display_header():
    """Display the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 UX Heuristics Analyzer</h1>
        <p>Analyze your designs against proven UX principles</p>
    </div>
    """, unsafe_allow_html=True)

def get_score_class(score: int) -> str:
    """Get CSS class based on score"""
    if score >= 85:
        return "score-excellent"
    elif score >= 70:
        return "score-good"
    elif score >= 50:
        return "score-fair"
    else:
        return "score-poor"

def display_overall_score(result: Dict[str, Any]):
    """Display the overall UX score"""
    score = result.get('overall_score', 0)
    score_class = get_score_class(score)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="score-display {score_class}">
            {score}/100
        </div>
        <p style="text-align: center; font-size: 1.2rem;">Overall UX Score</p>
        """, unsafe_allow_html=True)

def display_category_breakdown(result: Dict[str, Any]):
    """Display category-wise breakdown"""
    categories = result.get('categories', {})
    
    if not categories:
        st.warning("No detailed category analysis available.")
        return
    
    st.subheader("📊 Category Breakdown")
    
    for category_id, category_data in categories.items():
        title = category_data.get('title', f'Category {category_id}')
        score = category_data.get('score', 0)
        checkpoints = category_data.get('checkpoints', {})
        
        # Category header with score
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{category_id}. {title}**")
        with col2:
            score_class = get_score_class(score)
            st.markdown(f'<span class="{score_class}">**{score}%**</span>', unsafe_allow_html=True)
        
        # Progress bar
        st.progress(score / 100)
        
        # Checkpoints details in expander
        with st.expander(f"View {len(checkpoints)} checkpoints"):
            for checkpoint_id, checkpoint_data in checkpoints.items():
                status = checkpoint_data.get('status', 'UNKNOWN')
                text = checkpoint_data.get('text', '')
                reasoning = checkpoint_data.get('reasoning', '')
                recommendation = checkpoint_data.get('recommendation', '')
                
                # Status icon and color
                if status == 'PASS':
                    icon = "✅"
                    css_class = "checkpoint-pass"
                elif status == 'FAIL':
                    icon = "❌"
                    css_class = "checkpoint-fail"
                else:
                    icon = "⚠️"
                    css_class = "checkpoint-attention"
                
                st.markdown(f'{icon} **{checkpoint_id}**: {text}')
                if reasoning:
                    st.markdown(f'<small class="{css_class}">💭 {reasoning}</small>', unsafe_allow_html=True)
                if recommendation:
                    st.markdown(f"""
                    <div class="recommendation-box">
                        <strong>💡 Recommendation:</strong> {recommendation}
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("---")

def display_priority_issues(result: Dict[str, Any]):
    """Display priority issues and strengths"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚨 Priority Issues")
        issues = result.get('priority_issues', [])
        if issues:
            for i, issue in enumerate(issues[:5], 1):
                st.markdown(f"{i}. {issue}")
        else:
            st.success("No critical issues found!")
    
    with col2:
        st.subheader("✨ Strengths")
        strengths = result.get('strengths', [])
        if strengths:
            for strength in strengths[:5]:
                st.markdown(f"• {strength}")
        else:
            st.info("Analysis completed - check detailed results above.")

def analyze_image_upload():
    """Handle image upload and analysis"""
    if 'analyzing' not in st.session_state:
        st.session_state.analyzing = False
        
    st.subheader("📷 Upload Image")
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a screenshot or image of your interface"
    )
    
    if uploaded_file is not None and not st.session_state.analyzing:
        # Display uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        
        if st.button("Analyze Image", type="primary"):
            st.session_state.analyzing = True
            with st.spinner("Analyzing image against UX heuristics..."):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                try:
                    # Analyze the image
                    result = st.session_state.analyzer.analyze_image(tmp_path)
                    st.session_state.analysis_result = result
                    
                    # Clean up temporary file
                    os.unlink(tmp_path)
                    
                    st.session_state.analyzing = False
                    st.success("Analysis completed!")
                    st.rerun()
                    
                except Exception as e:
                    st.session_state.analyzing = False
                    st.error(f"Analysis failed: {str(e)}")
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

def analyze_video_upload():
    """Handle video upload and analysis"""
    st.subheader("🎥 Upload Video")
    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=['mp4', 'mov', 'avi'],
        help="Upload a video of your interface or user interaction"
    )
    
    if uploaded_file is not None:
        st.video(uploaded_file)
        
        if st.button("Analyze Video", type="primary"):
            with st.spinner("Extracting frames and analyzing video..."):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                try:
                    # Analyze the video
                    result = st.session_state.analyzer.analyze_video(tmp_path)
                    st.session_state.analysis_result = result
                    
                    # Clean up temporary file
                    os.unlink(tmp_path)
                    
                    st.success("Video analysis completed!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Video analysis failed: {str(e)}")
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

def analyze_website_url():
    """Handle website URL analysis"""
    st.subheader("🌐 Website URL")
    url = st.text_input(
        "Enter website URL",
        placeholder="https://example.com",
        help="Enter the URL of the website you want to analyze"
    )
    
    if url:
        # Validate URL format
        if not url.strip():
            st.error("Please enter a valid URL")
            return
            
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        if st.button("Analyze Website", type="primary"):
            with st.spinner(f"Capturing screenshot and analyzing {url}..."):
                try:
                    # Analyze the website
                    result = st.session_state.analyzer.analyze_website(url)
                    st.session_state.analysis_result = result
                    
                    if 'error' in result:
                        st.error(result['error'])
                    else:
                        st.success("Website analysis completed!")
                        st.rerun()
                    
                except Exception as e:
                    st.error(f"Website analysis failed: {str(e)}")

def display_analysis_results():
    """Display the analysis results"""
    result = st.session_state.analysis_result
    
    if result is None:
        return
    
    # Check for errors
    if 'error' in result:
        st.error(f"Analysis Error: {result['error']}")
        return
    
    # Display results
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
    
    # Overall score
    display_overall_score(result)
    
    # Summary
    summary = result.get('summary', '')
    if summary:
        st.markdown(f"**Summary:** {summary}")
    
    # Category breakdown
    display_category_breakdown(result)
    
    # Priority issues and strengths
    display_priority_issues(result)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📄 Generate Report"):
            st.info("Report generation feature coming soon!")
    with col2:
        if st.button("🔗 Share Analysis"):
            st.info("Share feature coming soon!")
    with col3:
        if st.button("🔄 New Analysis"):
            st.session_state.analysis_result = None
            st.rerun()

def main():
    """Main application function"""
    initialize_session_state()
    display_header()
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Analysis Options")
        analysis_type = st.radio(
            "Choose analysis method:",
            ["📷 Image Upload", "🎥 Video Upload", "🌐 Website URL"]
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This tool analyzes digital interfaces against 10 comprehensive UX heuristic categories:
        
        1. **People Don't Want to Work** - Minimize user effort
        2. **People Have Limitations** - Respect cognitive limits
        3. **People Make Mistakes** - Error prevention & recovery
        4. **Human Memory Is Complicated** - Don't rely on memory
        5. **People are Social** - Leverage social behaviors
        6. **Attention** - Manage focus effectively
        7. **People Crave Information** - Provide appropriate feedback
        8. **Unconscious Processing** - Consider subconscious factors
        9. **People Create Mental Models** - Match user expectations
        10. **Visual System** - Optimize visual design
        """)
    
    # Main content area
    if analysis_type == "📷 Image Upload":
        analyze_image_upload()
    elif analysis_type == "🎥 Video Upload":
        analyze_video_upload()
    else:  # Website URL
        analyze_website_url()
    
    # Display results if available
    if st.session_state.analysis_result:
        st.markdown("---")
        st.header("📊 Analysis Results")
        display_analysis_results()

if __name__ == "__main__":
    main()

