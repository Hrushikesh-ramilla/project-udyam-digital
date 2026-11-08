from pathlib import Path
from playwright.sync_api import sync_playwright

html_file = Path("docs/dpdp_privacy_note.html").resolve()
output_pdf = Path("DPDP_Privacy_Note.pdf").resolve()

print(f"Rendering {html_file} -> {output_pdf}")
with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page()
    page.goto(html_file.as_uri())
    page.pdf(
        path=str(output_pdf),
        format="A4",
        print_background=True,
        margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
    )
    browser.close()

print(f"Successfully generated {output_pdf} (Size: {output_pdf.stat().st_size / 1024:.1f} KB)")
