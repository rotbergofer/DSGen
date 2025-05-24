from PIL import Image, ImageEnhance
import os, io, zipfile
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def manipulate_image(img):
    img = img.convert("RGB")
    enhancer = ImageEnhance.Color(img)
    return enhancer.enhance(1.5)

def manipulate_and_zip(uploaded_files):
    os.makedirs("output", exist_ok=True)
    for i, file in enumerate(uploaded_files):
        img = Image.open(file)
        for j in range(5):
            manipulated = manipulate_image(img)
            manipulated.save(f"output/image_{i}_{j}.jpg")
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file in os.listdir("output"):
            zip_file.write(f"output/{file}", arcname=file)
    zip_buffer.seek(0)
    return zip_buffer

def send_email_notification(to_email):
    message = Mail(
        from_email="your@email.com",
        to_emails=to_email,
        subject="Your images are ready!",
        plain_text_content="Your image processing is complete.")
    sg = SendGridAPIClient("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")
    sg.send(message)
