import streamlit as st
import requests
import io
from PIL import Image

st.set_page_config(page_title="Pro AI Image Agent", page_icon="🎨", layout="wide")

st.title("🎨 Pro AI Image Generator Agent")
st.write("Configured with FLUX & advanced generation settings for hyper-accurate results.")

# Pull Cloudflare configuration safely from Streamlit Secrets
try:
    ACCOUNT_ID = st.secrets["CLOUDFLARE_ACCOUNT_ID"]
    API_TOKEN = st.secrets["CLOUDFLARE_API_TOKEN"]
except KeyError:
    st.error("Missing credentials! Please configure your Cloudflare secrets in the Streamlit dashboard.")
    st.stop()

# Switch to the hyper-accurate FLUX.1-schnell model
API_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Create a clean layout with two columns
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("🎛️ Settings & Prompts")
    
    # 1. Main Prompt
    prompt = st.text_area(
        label="What do you want the AI to create? (Be highly descriptive)",
        placeholder="A majestic cinematic shot of a futuristic cybernetic tiger running through a neon Tokyo street, 4k resolution, hyper-detailed...",
        height=100
    )
    
    # 2. Negative Prompt (tells the AI what to exclude)
    negative_prompt = st.text_input(
        label="Negative Prompt (What to exclude)",
        placeholder="blurry, low quality, distorted hands, extra limbs, bad anatomy"
    )
    
    # Advanced Parameters Expander
    with st.expander("⚙️ Advanced AI Fine-Tuning"):
        num_steps = st.slider("Inference Steps (Detail quality)", min_value=4, max_value=20, value=8, step=1)
        guidance = st.slider("Guidance Scale (Prompt adherence)", min_value=1.0, max_value=15.0, value=7.5, step=0.5)
        width = st.select_slider("Image Width", options=[512, 768, 1024], value=1024)
        height = st.select_slider("Image Height", options=[512, 768, 1024], value=1024)

    generate_btn = st.button("Generate Masterpiece ✨", type="primary")

with col2:
    st.subheader("🖼️ Generated Output")
    image_placeholder = st.empty()
    image_placeholder.info("Your masterpiece will appear here once you hit generate.")

if generate_btn:
    if not prompt.strip():
        st.warning("Please enter a prompt description first!")
    else:
        with col2:
            with st.spinner("FLUX Engine is rendering your image..."):
                try:
                    # Construct payload containing advanced accuracy parameters
                    payload = {
                        "prompt": prompt,
                        "negative_prompt": negative_prompt,
                        "num_steps": num_steps,
                        "guidance": guidance,
                        "width": width,
                        "height": height
                    }
                    
                    # Send request to Cloudflare
                    response = requests.post(API_URL, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        # Process and render image
                        image_bytes = response.content
                        image = Image.open(io.BytesIO(image_bytes))
                        
                        image_placeholder.image(image, caption="Generation complete!", use_container_width=True)
                        st.success("Done!")
                    else:
                        st.error(f"Cloudflare API Error (Status {response.status_code}): {response.text}")
                        
                except Exception as e:
                    st.error(f"An error occurred while connecting to the server: {e}")
