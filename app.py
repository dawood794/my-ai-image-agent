import streamlit as st
import requests
import io
import base64  # Added to decode the FLUX text string
from PIL import Image

st.set_page_config(page_title="Pro AI Image Agent", page_icon="🎨", layout="centered")

st.title("🎨 Pro AI Image Generator Agent")
st.write("Powered by the hyper-accurate FLUX.1-schnell model on Cloudflare.")

# Pull Cloudflare configuration safely from Streamlit Secrets
try:
    ACCOUNT_ID = st.secrets["CLOUDFLARE_ACCOUNT_ID"]
    API_TOKEN = st.secrets["CLOUDFLARE_API_TOKEN"]
except KeyError:
    st.error("Missing credentials! Please configure your Cloudflare secrets in the Streamlit dashboard.")
    st.stop()

# FLUX Endpoint
API_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# User Inputs
prompt = st.text_area(
    label="What do you want the AI to create? (Be highly descriptive)",
    placeholder="A majestic cinematic shot of a futuristic cybernetic tiger running through a neon street, 4k resolution, hyper-detailed...",
    height=120
)

# FLUX works best between 4 and 8 steps
steps = st.slider("Detail Steps (FLUX is optimized for 4-8)", min_value=4, max_value=8, value=4, step=1)

generate_btn = st.button("Generate Masterpiece ✨", type="primary")

if generate_btn:
    if not prompt.strip():
        st.warning("Please enter a prompt description first!")
    else:
        with st.spinner("FLUX Engine is rendering your image text..."):
            try:
                # Send clean payload optimized for FLUX
                payload = {
                    "prompt": prompt,
                    "steps": steps
                }
                
                response = requests.post(API_URL, headers=headers, json=payload)
                
                if response.status_code == 200:
                    # Cloudflare returns a JSON dictionary for FLUX
                    json_data = response.json()
                    
                    # Extract the Base64 image string from the result
                    base64_image_string = json_data["result"]["image"]
                    
                    # Convert the Base64 text back into raw image bytes
                    image_bytes = base64.b64decode(base64_image_string)
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # Display the final piece
                    st.success("Done!")
                    st.image(image, caption=f"Prompt: {prompt}", use_container_width=True)
                else:
                    st.error(f"Cloudflare API Error (Status {response.status_code}): {response.text}")
                    
            except Exception as e:
                st.error(f"An error occurred while rendering: {e}")
