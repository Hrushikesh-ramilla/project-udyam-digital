import re

def update():
    file_path = "docs/presentation/build_winner_deck.py"
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Update Demo Video link on Slide 0
    old_demo = '<tr><td style="padding: 4px 0; font-weight: 600; color: #8F9094;">Demo Video</td><td><span style="color: #FF7070; font-weight: 800; text-decoration: underline;">Interactive 100-Case Video Proof & Walkthrough</span></td></tr>'
    new_demo = '<tr><td style="padding: 4px 0; font-weight: 600; color: #8F9094;">Demo Video</td><td><a href="https://airtel.hrushikeshramilla.in/demoVideo" style="color: #FF5252; text-decoration: underline; font-weight: 850;">https://airtel.hrushikeshramilla.in/demoVideo</a> <span style="font-size: 12px; color: #8F9094;">(Full HD Walkthrough)</span></td></tr>'

    if old_demo in text:
        text = text.replace(old_demo, new_demo)
        print("Updated Slide 0 Demo Video link.")
    else:
        print("Warning: old_demo not found directly.")

    # Add demo video link to Slide 7 verdict as well
    old_verdict = '<strong style="color: #E40000;">Executive Verdict:</strong> Project Udyam Digital transforms Accel Business from a slow, paper-bound corporate carrier into India\'s default digital operating system for small enterprises—slashing CAC by 78%, lifting non-GST conversions 4.25x, and unlocking ₹1,200 Cr ARR in 12 months.'
    new_verdict = '<strong style="color: #E40000;">Executive Verdict:</strong> Project Udyam Digital transforms Accel Business from a slow, paper-bound corporate carrier into India\'s default digital operating system for small enterprises—slashing CAC by 78%, lifting non-GST conversions 4.25x, and unlocking ₹1,200 Cr ARR in 12 months.<br><span style="font-size: 12px; color: #4A4B4E; margin-top: 4px; display: inline-block;">Official HD Video Walkthrough & Interactive Demo: <a href="https://airtel.hrushikeshramilla.in/demoVideo" style="color: #E40000; font-weight: 800; text-decoration: underline;">https://airtel.hrushikeshramilla.in/demoVideo</a></span>'

    if old_verdict in text:
        text = text.replace(old_verdict, new_verdict)
        print("Updated Slide 7 Verdict with direct demo video link.")
    else:
        print("Warning: old_verdict not found directly.")

    # Update test counts to 62
    text = text.replace('56 Pytest Tests', '62 Pytest Tests')
    text = text.replace('56 / 56 Pytest Tests Passing', '62 / 62 Pytest Tests Passing')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    print("Updated build_winner_deck.py successfully.")

if __name__ == "__main__":
    update()
