import streamlit as st
import requests
import io
import base64
from PIL import Image

# 1. Page Config loaded at the very top for search discoverability!
st.set_page_config(
    page_title="Pro AI Image Generator Agent - Create Art with FLUX",
    page_icon="🎨",
    layout="centered"
)

# App UI Header
st.title("🎨 Pro AI Image Generator Agent")
st.write("Powered by the hyper-accurate **FLUX.1-schnell** model on Cloudflare.")

# 2. Pull Cloudflare configuration safely from Streamlit Secrets
try:
    ACCOUNT_ID = st.secrets["CLOUDFLARE_ACCOUNT_ID"]
    API_TOKEN = st.secrets["CLOUDFLARE_API_TOKEN"]
except KeyError:
    st.error("Missing credentials! Please configure your Cloudflare secrets in the Streamlit dashboard.")
    st.stop()

# Cloudflare API endpoint for FLUX
API_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# 3. Sidebar Configuration 
st.sidebar.header("⚙️ Generation Settings")
use_enhancer = st.sidebar.toggle("✨ Auto-Enhance Prompt (Highly Recommended)", value=True, help="Automatically rewrites your prompt to force maximum realism, sharp details, and clean lighting.")
steps = st.sidebar.slider("Detail Steps (FLUX optimal is 4-8)", min_value=4, max_value=8, value=4, step=1)

# 4. User Prompt Input
prompt = st.text_area(
    label="What do you want the AI to create?",
    placeholder="Type something here (e.g., 'Elon Musk wearing a leather jacket' or 'a cute orange kitten')...",
    height=100
)

# 5. The "Magic Enhancer" Engine
def enhance_prompt(original_prompt):
    """
    Translates simple user descriptions into rich, photographic terms
    that FLUX understands perfectly for maximum realism and accuracy.
    """
    clean_prompt = original_prompt.strip()
    
    # If the user is looking to generate a specific person/celebrity
    if any(name in clean_prompt.lower() for name in ["elon", "musk", "jeff", "bezos", "mark", "zuckerberg", "man", "woman", "person", "portrait"]):
        return f"A crisp, sharp-focus professional 85mm lens portrait of {clean_prompt}. Cinematic studio lighting, deep textures, natural skin details, highly detailed background, realistic photo style."
    
    # If it is a cinematic/scenic prompt
    return f"A cinematic, breathtaking shot of {clean_prompt}. Beautiful lighting, realistic reflections, detailed environmental storytelling, shot on high-end camera lens, sharp, crisp details."

# Generate Button
generate_btn = st.button("Generate Masterpiece ✨", type="primary")

if generate_btn:
    if not prompt.strip():
        st.warning("Please enter a prompt description first!")
    else:
        # Determine whether to inject the magic camera configurations
        final_prompt = enhance_prompt(prompt) if use_enhancer else prompt
        
        # Display the prompt being sent to the AI for clarity
        if use_enhancer:
            st.info(f"✨ **Enhanced prompt used behind the scenes:**\n*{final_prompt}*")
            
        with st.spinner("FLUX is rendering your high-accuracy image..."):
            try:
                # Payload designed specifically for FLUX's API requirements
                payload = {
                    "prompt": final_prompt,
                    "steps": steps
                }
                
                response = requests.post(API_URL, headers=headers, json=payload)
                
                if response.status_code == 200:
                    json_data = response.json()
                    
                    # Extract and decode the base64 image data string
                    base64_image_string = json_data["result"]["image"]
                    image_bytes = base64.b64decode(base64_image_string)
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # Display the beautiful output!
                    st.success("Done!")
                    st.image(image, caption="Your Generated Art", use_container_width=True)
                else:
                    st.error(f"Cloudflare API Error (Status {response.status_code}): {response.text}")
                    
            except Exception as e:
                st.error(f"An error occurred while rendering: {e}")
