from flask import Flask, request, render_template, Response
import pandas as pd
import smtplib
from email.message import EmailMessage
import os
import queue
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '.'

message_queue = queue.Queue()
email_thread_done = threading.Event()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send_emails():
    from_email = request.form.get('from_email')
    from_password = request.form.get('from_password')

    if not from_email or not from_password:
        return 'Missing sender email or password', 400

    excel_file = request.files['excel']
    resume_file = request.files['resume']

    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], "Mailss.xlsx")
    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], "JayaniAbhiram_Resume.pdf")

    excel_file.save(excel_path)
    resume_file.save(resume_path)

    def process_emails():
        df = pd.read_excel(excel_path)
        emails = df[['Mail', 'Company Name']]

        for index, row in emails.iterrows():
            email = row['Mail']
            company = row['Company Name']

            if pd.notna(email) and pd.notna(company):
                subject = f"Seeking Opportunities to Contribute at {company}"

                message_body = f"""\
                <html>
                  <body style="font-family:Arial, sans-serif; line-height:1.6; color:black;">
                    <p>Respected Team,</p>
                    <p>I’m <strong>Jayani Abhiram</strong>, a Computer Science Engineering graduate... [Truncated for brevity]</p>
                    <p>Best regards,<br>
                    <strong>Jayani Abhiram</strong><br>
                    📞 +91 85209 97742<br>
                    ✉️ jayaniabhiram@gmail.com</p>
                  </body>
                </html>
                """

                msg = EmailMessage()
                msg['Subject'] = subject
                msg['From'] = from_email
                msg['To'] = email
                msg.add_alternative(message_body, subtype='html')

                try:
                    with open(resume_path, 'rb') as f:
                        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename="JayaniAbhiram_Resume.pdf")
                except Exception as e:
                    message_queue.put(f"⚠️ Could not attach resume for {email}: {e}")
                    continue

                try:
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login(from_email, from_password)
                        smtp.send_message(msg)
                        message_queue.put(f"✅ Sent to {email} ({company})")
                except Exception as e:
                    message_queue.put(f"❌ Failed to send to {email} ({company}): {e}")

        message_queue.put("✅✅ All mails have been sent successfully. The stream will now stop.")
        email_thread_done.set()

    email_thread_done.clear()
    threading.Thread(target=process_emails).start()
    return '', 204

@app.route('/stream')
def stream():
    def event_stream():
        while not email_thread_done.is_set() or not message_queue.empty():
            try:
                message = message_queue.get(timeout=1)
                yield f"data: {message}\n\n"
            except queue.Empty:
                continue
        yield f"data: !!__END_STREAM__!!\n\n"
    return Response(event_stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
