import streamlit as st
import pyrebase
import json
from utils import manipulate_and_zip, send_email_notification

# Firebase init
with open("firebase_config.json") as f:
    config = json.load(f)

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

# Auth UI
if 'user' not in st.session_state:
    st.session_state.user = None

def auth_ui():
    choice = st.radio("Login or Signup", ["Login", "Signup"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Submit"):
        try:
            if choice == "Signup":
                user = auth.create_user_with_email_and_password(email, password)
                db.child("licenses").child(user['localId']).set({"status": "inactive"})
            else:
                user = auth.sign_in_with_email_and_password(email, password)

            st.session_state.user = user
            st.success("Logged in!")
        
        except Exception as e:
            try:
                error_json = e.args[1] if isinstance(e.args[1], str) else e.args[1].response.json()
                error_msg = error_json['error']['message']
            except:
                error_msg = str(e)

            if 'EMAIL_EXISTS' in error_msg:
                st.error("This email is already registered. Please log in.")
            elif 'INVALID_PASSWORD' in error_msg or 'INVALID_LOGIN_CREDENTIALS' in error_msg:
                st.error("Invalid email or password.")
            elif 'EMAIL_NOT_FOUND' in error_msg:
                st.error("Email not found. Try signing up.")
            else:
                st.error(f"Authentication error: {error_msg}")     

if not st.session_state.user:
    auth_ui()
    st.stop()

uid = st.session_state.user['localId']
print(uid)
email = st.session_state.user['email']
license_status = db.child("licenses").child(uid).get().val()
print (license_status)

# 2. Check for missing license data
if not license_status or license_status.get("status") != "active":
    st.warning("Your license is inactive or missing. Please purchase one.")
    st.stop()

# Upload images
st.header("Upload Images to Generate Variations")
uploaded_files = st.file_uploader("Upload", type=["jpg", "png"], accept_multiple_files=True)

if uploaded_files and st.button("Process Images"):
    zip_file = manipulate_and_zip(uploaded_files)
    st.success("Done! Download your images below:")
    st.download_button("Download ZIP", zip_file, file_name="images.zip")
    send_email_notification(email)
