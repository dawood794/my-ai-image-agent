import streamlit as st
import requests
import io
from PIL import Image

st.set_page_config(page_title="AI Image Agent", page_icon="🎨", layout="centered")

st.title("🎨 My AI Image Generator Agent")
st.write("This app uses Cloudflare's edge network GPUs to instantly turn your text into artwork.")

# Setup Cloudflare configuration pulling safely from Streamlit Secrets
try:
    ACCOUNT_ID = st.secrets["CLOUDFLARE_ACCOUNT_ID"]
    API_TOKEN = st.secrets["CLOUDFLARE_API_TOKEN"]
except KeyError:
    st.error("Missing credentials! Please configure your Cloudflare secrets in the Streamlit dashboard.")
    st.stop()

# API configuration
API_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# User Interaction Zone
prompt = st.text_area(
    label="What do you want the AI to create?",
    placeholder="A detailed cyberpunk city with neon street signs, raining, highly detailed 4k...",
    height=100
)

if st.button("Generate Image ✨", type="primary"):
    if not prompt.strip():
        st.warning("Please enter a prompt description first!")
    else:
        with st.spinner("Cloudflare GPUs are creating your image..."):
            try:
                # Send request to Cloudflare's AI endpoint
                response = requests.post(API_URL, headers=headers, json={"prompt": prompt})
                
                if response.status_code == 200:
                    # Read the binary image data received
                    image_bytes = response.content
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # Display the image on screen
                    st.success("Done!")
                    st.image(image, caption=f"Prompt: {prompt}", use_container_width=True)
                else:
                    st.error(f"Cloudflare API Error (Status {response.status_code}): {response.text}")
                    
            except Exception as e:
                st.error(f"An error occurred while connecting to the server: {e}")