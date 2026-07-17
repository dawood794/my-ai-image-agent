import streamlit as st
import requests
import io
import base64
from PIL import Image

# 1. Responsive Page Configuration
st.set_page_config(
    page_title="Pro AI Image Generator Agent - Create Art with FLUX",
    page_icon="🎨",
    layout="wide"  # Wide container acts as our responsive viewport
)

# 2. Inject Smart Responsive CSS (Adapts to Mobile and PC)
st.markdown("""
    <style>
        /* Base Page Setup */
        .stApp {
            background-color: #0e1117;
            color: #ffffff;
        }
        
        /* Responsive Gradient Header */
        .gradient-text {
            background: linear-gradient(45deg, #ff4b4b, #ff8f00);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            margin-bottom: 0px;
            text-align: center;
        }
        
        /* Modern Card Containers */
        div[data-testid="stVerticalBlock"] > div {
            background-color: #161a24;
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #262730;
            margin-bottom: 12px;
        }
        
        /* Input Styling */
        .stTextArea textarea {
            background-color: #0e1117 !important;
            color: #ffffff !important;
            border-radius: 10px !important;
            border: 1px solid #4b5563 !important;
        }
        
        /* Action Button */
        .stButton>button {
            background: linear-gradient(135deg, #ff4b4b 0%, #ff8f00 100%) !important;
            color: white !important;
            border: none !important;
            padding: 14px 28px !important;
            font-weight: bold !important;
            font-size: 1.1rem !important;
            border-radius: 12px !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0px 8px 20px rgba(255, 75, 75, 0.4) !important;
        }
        
        /* ==========================================
           RESPONSIVE DESIGN BREAKPOINTS (PC vs Mobile)
           ========================================== */
        
        /* Desktop Screens (PCs and Laptops) */
        @media (min-width: 769px) {
            .gradient-text {
                font-size: 3.5rem;
                text-align: left;
            }
            div[data-testid="stVerticalBlock"] > div {
                padding: 30px;
            }
        }
        
        /* Mobile Screens (Phones and Tablets) */
        @media (max-width: 768px) {
            .gradient-text {
                font-size: 2.2rem;
                text-align: center;
            }
            /* Reduce heavy spacing to save screen room on phones */
            div[data-testid="stVerticalBlock"] > div {
                padding: 15px;
                margin-bottom: 8px;
            }
            .stButton>button {
                padding: 12px 20px !important;
                font-size: 1rem !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Responsive UI Header
st.markdown('<p class="gradient-text">🎨 Pro AI Image Agent</p>', unsafe_allow_html=True)
st.write("Powered by the hyper-accurate **FLUX.1-schnell** engine on Cloudflare.")

# Pull Cloudflare configuration safely from Streamlit Secrets
try:
    ACCOUNT_ID = st.secrets["CLOUDFLARE_ACCOUNT_ID"]
    API_TOKEN = st.secrets["CLOUDFLARE_API_TOKEN"]
except KeyError:
    st.error("Missing credentials! Please configure your Cloudflare secrets in the Streamlit dashboard.")
    st.stop()

# Cloudflare API endpoint for FLUX
API_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Streamlit columns are automatically responsive!
# They sit side-by-side on PC and stack vertically on Mobile.
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("🎛️ Control Panel")
    
    # User Prompt Input
    prompt = st.text_area(
        label="What do you want the AI to create?",
        placeholder="Describe your vision (e.g., 'A professional photo of a red sports car speeding through a wet city street at night')...",
        height=120
    )
    
    use_enhancer = st.toggle("✨ Auto-Enhance Prompt (Recommended)", value=True)
    steps = st.slider("Detail Steps (FLUX optimal is 4-8)", min_value=4, max_value=8, value=4, step=1)
    
    generate_btn = st.button("Generate Masterpiece ✨")

with col2:
    st.subheader("🖼️ Generated Art")
    image_placeholder = st.empty()
    image_placeholder.info("Your beautiful creation will display here once generated.")

# The "Magic Enhancer" Engine
def enhance_prompt(original_prompt):
    clean_prompt = original_prompt.strip()
    if any(name in clean_prompt.lower() for name in ["elon", "musk", "jeff", "bezos", "mark", "zuckerberg", "man", "woman", "person", "portrait", "boy", "girl"]):
        return f"A crisp, sharp-focus professional 85mm lens portrait of {clean_prompt}. Cinematic studio lighting, deep textures, natural skin details, highly detailed background, realistic photo style."
    return f"A cinematic, breathtaking shot of {clean_prompt}. Beautiful lighting, realistic reflections, detailed environmental storytelling, shot on high-end camera lens, sharp, crisp details."

if generate_btn:
    if not prompt.strip():
        st.warning("Please enter a prompt description first!")
    else:
        final_prompt = enhance_prompt(prompt) if use_enhancer else prompt
        
        with col2:
            with st.spinner("Rendering your FLUX art..."):
                try:
                    payload = {
                        "prompt": final_prompt,
                        "steps": steps
                    }
                    
                    response = requests.post(API_URL, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        json_data = response.json()
                        base64_image_string = json_data["result"]["image"]
                        image_bytes = base64.b64decode(base64_image_string)
                        image = Image.open(io.BytesIO(image_bytes))
                        
                        image_placeholder.image(image, caption="Generation Complete", use_container_width=True)
                        st.success("Done!")
                    else:
                        st.error(f"Cloudflare API Error (Status {response.status_code}): {response.text}")
                        
                except Exception as e:
                    st.error(f"An error occurred while rendering: {e}")
