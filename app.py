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
    excel_file = request.files['excel']
    resume_file = request.files['resume']

    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], "Mailss.xlsx")
    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], "JayaniAbhiram_Resume.pdf")

    excel_file.save(excel_path)
    resume_file.save(resume_path)

    def process_emails():
        your_email = "jayaniabhiram@gmail.com"
        your_password = "djhe nloo okca bojs"

        df = pd.read_excel(excel_path)
        emails = df[['Mail', 'Company Name']]

        for index, row in emails.iterrows():
            email = row['Mail']
            company = row['Company Name']

            if pd.notna(email) and pd.notna(company):
                subject = f"Seeking Opportunities to Contribute at {company}"

                message_body = f"""
                <html>
  <body style="font-family:Arial, sans-serif; line-height:1.6; color:black;">
    <p style="font-size:16px;">Respected Team</strong>,</p>

    <p style="font-size:15px;">
      I hope you're doing well. I’m <strong>Jayani Abhiram</strong>, a Computer Science Engineering graduate from JK Lakshmipat University, Jaipur, with a CGPA of 8.1. I’m reaching out with great enthusiasm to explore the possibility of contributing to <strong>{company}</strong> in a role where I can merge innovation with meaningful impact.
    </p>

    <p style="font-size:15px;">
      Over the past few years, I have honed my skills in Data analysis, Data Science, Web Development and creative solution design. My background blends technical expertise with a proactive mindset to solve real-world challenges.
    </p>

    <h3 style="color:#2c3e50;">🚀 Key Projects:</h3>
<ul>
  <li><strong>Shiksha Shastra</strong>: A volunteer-community platform awarded 3rd in a national hackathon for social innovation and impact.</li>
  <li><strong>Data Analysis Tool</strong>: An intelligent web app for data cleaning, filtering, visualizing, and exporting insights.</li>
  <li><strong>Student Scores Management</strong>: A comprehensive data analysis project examining the influence of personal environment and parental support on academic outcomes.</li>
  <li><strong>E-waste Recycling System</strong>: A digital initiative promoting sustainable electronics waste disposal and traceability.</li>
</ul>

    <h3 style="color:#2c3e50;">🧠 Technical Proficiency:</h3>
    <ul>
      <li><strong>Programming:</strong> PHP, Python (Pandas, NumPy),Java, JavaScript, SQL</li>
      <li><strong>Web Technologies:</strong> PHP Laravel, Core PHP, HTML5, CSS3, Bootstrap, React.js, REST APIs</li>
      <li><strong>Developer Tools:</strong> Git, GitHub, VS Code, XAMPP, PowerBI, phpMyAdmin, MS Excel</li>
      <li><strong>Database Systems:</strong> MySQL</li>
    </ul>

    <h3 style="color:#2c3e50;">📌 Roles & Responsibilities:</h3>
    <ul>
      <li><strong>Coursera Campus Ambassador</strong>: Led tech skill-building campaigns and workshops at campus level.</li>
      <li><strong>Campus Placement Coordinator</strong>: Bridged communication between students and recruiters and organized placement drives.</li>
    </ul>

    <h3 style="color:#2c3e50;">🏆 Achievements:</h3>
    <ul>
      <li><strong>2nd Runner-Up at HACK-JKLU 2024</strong>: For developing an ed-tech prototype with societal value.</li>
      <li><strong>GATE 2024 Qualified</strong>: Demonstrated proficiency in core computing and problem-solving.</li>
    </ul>

    <p style="font-size:15px;">
      I’m deeply inspired by the work being done at <strong>{company}</strong> and am eager to contribute with a problem-solving mindset, creative thinking, and relentless curiosity. I've attached my resume and would love to connect further to discuss potential collaborations.
    </p>

    <p style="font-size:15px;">
  I sincerely thank you for taking the time to read my message and consider my application. I would be truly honored to contribute to <strong>{company}</strong>'s vision with my enthusiasm, adaptability, and strong foundation in both development and data-driven problem solving. I believe my ability to lead, learn quickly, and take ownership of impactful work makes me a strong candidate for a role in your esteemed organization.
</p>

<p style="font-size:15px;">
  I respectfully request your kind consideration for any suitable job within your team. I am eager to bring my dedication, skillset, and a genuine passion for building meaningful tech solutions to <strong>{company}</strong>. I would be grateful for a chance to discuss how I can contribute value and grow as a part of your innovative environment.
</p>

<p style="font-size:15px;">Looking forward to hearing from you, and once again, thank you so much for your valuable time and consideration.</p>

    <p style="font-size:15px;">
      Best regards,<br>
      <strong>Jayani Abhiram</strong><br>
      📞 +91 85209 97742<br>
      ✉️ jayaniabhiram@gmail.com
    </p>

    <p style="margin-top:20px;">
      <a href="https://www.linkedin.com/in/jayaniabhiram" style="background-color:#0e76a8;color:white;padding:10px 15px;text-decoration:none;border-radius:5px;">LinkedIn</a>
      &nbsp;
      <a href="https://jayaniabhiram.vercel.app" style="background-color:#4CAF50;color:white;padding:10px 15px;text-decoration:none;border-radius:5px;">Portfolio</a>
      &nbsp;
      <a href="https://github.com/jayaniabhiram" style="background-color:black;color:white;padding:10px 15px;text-decoration:none;border-radius:5px;">GitHub</a>
    </p>
  </body>
</html>
                """

                msg = EmailMessage()
                msg['Subject'] = subject
                msg['From'] = your_email
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
                        smtp.login(your_email, your_password)
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
    app.run(debug=True, port=5050)
