import streamlit as st
import requests
from dotenv import load_dotenv
import os
import io
import base64
from PIL import Image
import logging
import time

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="5K Car Care Assistant",
    page_icon="🚗",
    layout="centered",
    initial_sidebar_state="auto",
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Function to interact with the Google Generative AI API (or any future ZAi-Fi API integration)
def get_zai_fi_response(question, context, max_retries=3, retry_delay=2):
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 250,
    }

    # Include user context in the instruction to the assistant
    system_instruction = f"""You are an AI assistant for 5K Car Care. Provide concise, accurate information about our services and products in a polite, friendly, and professional manner. Always stay focused on 5K Car Care offerings and adhere to the following guidelines:

Key Information
1. Services:
Car Wash: RO Water Wash, Exterior Car Spa, Sanitizer Foam Car Spa
Anti-Bacteria Treatment: Interior cleaning, Odor removal, AC disinfection
Teflon Coating: Protects paint, prevents rust
Ceramic Coating: Long-lasting paint protection
Interior Enrichment: Seat cover customization, dashboard cleaning
Car AC Services: Gas refilling, cooling restoration
Car Detailing: Exterior/interior services, underbody coating
Special Treatments: Engine room cleaning, rat repellent, wiper smoother
2. Booking:
Gather details: preferred date, time, location, service type, and vehicle information.
Confirm availability for the Electronic City branch or nearest location.
3. Franchise Information:
Explain the franchise-based business model.
Highlight benefits like potential profits, brand reputation, and support provided by 5K Car Care.
Outline steps to apply for a franchise (contact details, application form, etc.).
4. Contact:
Phone: +91 91500 78405 (Electronic City branch)
Email: 5kcc.bangaloreec@gmail.com
Address: 15th Cross, Behind Village Hyper Market, Neeladri Road, Electronic City
5. About Us:
Founded: 2012 in Coimbatore
Branches: 150+ across Tamil Nadu, Karnataka, Kerala
Customers: Over 30 million served
Awards: "IKON of Bangalore City 2019", "ISO 9001:2015 Certification"
Working Hours: Open 365 days, 10 AM to 7 PM
6. Locations:
Provide the nearest branch based on user location ({context.get('location', 'unspecified')}).
Mention any special offers or promotions based on the location ({context.get('promotion', 'not available')}).
If information isn't available, offer alternatives or assistance.
Additional Features
Offer customer reviews/testimonials if requested.
Mention any ongoing promotions/offers where applicable.
Provide emergency assistance details for breakdowns or urgent inquiries.
Offer to connect users with a live agent for complex queries.
Important Notes
Focus exclusively on 5K Car Care services and offerings.
For unrelated queries, politely inform users:
"I can assist only with 5K Car Care-related questions. Is there anything else you'd like to know about our services?"
Handle ambiguous queries by requesting clarification, e.g., "Could you please provide more details?"
Use a polite and professional tone consistently.

"""



    # Build the conversation history
    contents = []

    # Start with the system instruction
    contents.append({
        "role": "user",
        "parts": [{"text": system_instruction}]
    })
    contents.append({
        "role": "model",
        "parts": [{"text": "Understood. I'm ready to assist with Greenfuturz information."}]
    })

    # Include conversation history
    # Only include the last 10 messages to keep the payload size reasonable
    history = st.session_state.messages[-10:] if len(st.session_state.messages) > 10 else st.session_state.messages
    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    # Add the current question
    contents.append({
        "role": "user",
        "parts": [{"text": question}]
    })

    payload = {
        "contents": contents,
        "generationConfig": generation_config
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=AIzaSyBPIt2Or0wKOxjyqtre4bhTJkL1ZgQyhhE"
    headers = {"Content-Type": "application/json"}

    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            logger.info(f"API Response Status Code: {response.status_code}")
            logger.info(f"API Response Content: {response.text[:500]}...")

            if response.status_code == 200:
                response_data = response.json()
                if response_data and "candidates" in response_data and len(response_data["candidates"]) > 0:
                    # Extract the assistant's reply
                    assistant_reply = response_data["candidates"][0]["content"]["parts"][0]["text"]
                    return assistant_reply
                else:
                    logger.warning("No valid response in API result")
                    return "I'm unable to generate a specific response at the moment. Could you please clarify your question?"
            else:
                logger.error(f"API Error: Status Code {response.status_code}, Response: {response.text}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return "I'm having trouble connecting to the service. Please try again later."

        except requests.RequestException as e:
            logger.error(f"Request Exception: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                return "I'm currently unable to process your request due to a technical issue. Please try again later."


# Utility to resize image
def resize_image(image_path, max_size=(1000, 1000)):
    with Image.open(image_path) as img:
        img.thumbnail(max_size)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()


# Hides Streamlit menu
def hide_streamlit_menu():
    st.markdown(
        """
<style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
</style>
        """,
        unsafe_allow_html=True
    )


def add_custom_css():
    st.markdown("""
        <style>
        /* App-wide Background Styling */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            height: 100%;
            width: 100%;
            background: linear-gradient(135deg, #0B204C, #FFFFFF);
        }
        .stApp {
            margin: 0;
            padding: 0;
            height: 100vh;
        }
        /* Header Section */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            padding: 10px 20px;
            position: fixed; /* Keep header fixed at the top */
            top: 0;
            left: 0;
            background-color: #0B204C; /* Semi-transparent background */
            z-index: 1000; /* Ensure it stays above other content */
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
        }
        .header .logo-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
        }
        .header .logo-container img {
            height: 40px; /* Logo height */
            width: auto;
        }
        .header .tagline {
            font-size: 11px;
            color: #ffffff;
            font-style: italic;
        }
        .header .title {
            font-size: 24px;
            color: #ffffff;
            font-weight: bold;
            text-align: center;
        }
        .header .title .subtitle {
            font-size: 16px;
            font-style: italic;
            color: #ffffff;
            margin-top: 5px;
        }
        .header .right-logo img {
            height: 60px; /* Adjust logo size */
            width: 120px;
        }
        /* Push Content Below Header */
        .content {
            margin-top: 80px; /* Offset to avoid overlap with the header */
        }
        /* Chat Styling */
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-bottom: 20px;
        }
        .chat-bubble {
            padding: 10px 15px;
            border-radius: 20px;
            display: inline-block;
            margin-bottom: 10px;
            max-width: 70%;
            color: #000000;
            word-wrap: break-word;
        }
        .user-bubble {
            background-color: #e6f3ff;
            align-self: flex-start;
            margin-right: 0;
            margin-bottom: 20px;
            text-align: left;
            border-radius: 20px 20px 0px 20px; /* Optional: Rounded corners with sharper top-left */
            max-width: 70%; /* Prevent the bubble from becoming too wide */
            word-wrap: break-word; /* Allow text wrapping inside the bubble */
            padding: 10px 15px;
            color: #000000; /* Text color */
        }
        .assistant-bubble {
            background-color: #f0f0f0;
            align-self: flex-start;
            margin-right: auto;
            margin-top: 10px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
# Function to encode an image to Base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Main function that runs the Streamlit app
def main():
    add_custom_css()
    hide_streamlit_menu()

    if "context" not in st.session_state:
        st.session_state.context = {}

    # Load logo images
    zai_fi_logo_path = "zaifilogo.png"
    car_care_logo_path = "download.png"
    zai_fi_logo_b64 = encode_image_to_base64(zai_fi_logo_path)
    car_care_logo_b64 = encode_image_to_base64(car_care_logo_path)

    # Render the header section
    st.markdown(f"""
        <div class="header">
            <!-- Left Section: ZAi-Fi Logo and Tagline -->
            <div class="logo-container">
                <div style="text-align: center;">
                    <img src="data:image/png;base64,{zai_fi_logo_b64}" alt="ZAi-Fi Logo">
                    <div class="tagline">
                        Empowering Intelligence, everywhere
                    </div>
                </div>
            </div>
            <!-- Center Section: Title -->
            <div class="title">
                5k Car Care
                <div class="subtitle">
                    Welcome to 5k Car Care's AI Assistant
                </div>
            </div>
            <!-- Right Section: Car Care Logo -->
            <div class="right-logo">
                <img src="data:image/png;base64,{car_care_logo_b64}" alt="Car Care Logo">
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Push content below the header
    st.markdown("<div class='content'>", unsafe_allow_html=True)

    # Initialize chat messages

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Create a placeholder for the chat container
    chat_container = st.empty()

    # Function to display all messages
    def display_messages():
        with chat_container.container():
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for message in st.session_state.messages:
                bubble_class = "user-bubble" if message["role"] == "user" else "assistant-bubble"
                st.markdown(f'<div class="chat-bubble {bubble_class}">{message["content"]}</div>',
                            unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Display initial messages
    display_messages()

    if prompt := st.chat_input("What is your question?"):
        # Add the user message to the session state
        st.session_state.messages.append({"role": "user", "content": prompt})

        # If the user provides location or other information, store it in session state
        if "location" in prompt.lower():
            st.session_state.context["location"] = prompt
        if "promotion" in prompt.lower():
            st.session_state.context["promotion"] = prompt

        # Update the display with the new user message
        display_messages()

        loading_placeholder = st.empty()
        with loading_placeholder:
            st.markdown('<div class="loading"><div class="loading-spinner"></div></div>', unsafe_allow_html=True)
            response = get_zai_fi_response(prompt, st.session_state.context)

        # Remove the loading spinner
        loading_placeholder.empty()

        # Add the assistant's response to the session state
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Update the display with the new assistant message
        display_messages()


if __name__ == "__main__":
    main()
