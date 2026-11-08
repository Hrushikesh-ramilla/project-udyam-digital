import os
import subprocess
import sys
import re
import shutil
import fitz
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt

# -------------------------------------------------------------
# OFFICIAL SUBMISSION METADATA
# Strict Unstop Naming Convention: TeamName_Campus Name
# -------------------------------------------------------------
TEAM_NAME = "Neural Nexus"
CAMPUS_NAME = "ABV-IIITM Gwalior"
OFFICIAL_PDF_NAME = f"{TEAM_NAME}_{CAMPUS_NAME}.pdf"
OFFICIAL_PPTX_NAME = f"{TEAM_NAME}_{CAMPUS_NAME}.pptx"

def compile_beamer_pdf():
    tex_path = "presentation.tex"
    print("Compiling docs/presentation/presentation.tex with pdflatex...")
    cmd = ["pdflatex", "-interaction=nonstopmode", tex_path]
    res = subprocess.run(cmd, cwd="docs/presentation", capture_output=True, text=True)
    print(f"pdflatex exit code: {res.returncode}")

    with open("docs/presentation/presentation.log", "r", encoding="latin1", errors="replace") as f:
        log_text = f.read()

    errors = re.findall(r'(!.*?)(?=\n\n|\n[A-Z]|\Z)', log_text, re.DOTALL)
    print(f"Total LaTeX errors: {len(errors)}")
    for e in errors[:5]:
        print("ERROR:", e.strip()[:200])

    overfulls = [l.strip() for l in log_text.splitlines() if "Overfull" in l]
    print(f"Total Overfull warnings: {len(overfulls)}")
    for o in overfulls:
        print("OVERFULL:", o)

    if res.returncode != 0:
        raise RuntimeError("pdflatex compilation failed!")

    pdf_src = "docs/presentation/presentation.pdf"
    
    # Save exclusively as the ONE official PDF deliverable in root
    shutil.copy2(pdf_src, OFFICIAL_PDF_NAME)
    print(f"Saved Single Official PDF: {OFFICIAL_PDF_NAME} ({os.path.getsize(OFFICIAL_PDF_NAME)} bytes)")
    return OFFICIAL_PDF_NAME

def generate_4k_beamer_pptx(pdf_src):
    doc = fitz.open(pdf_src)
    print(f"Rendering {len(doc)} slides to 4K UHD PPTX...")

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    hires_dir = "docs/presentation/preview"
    os.makedirs(hires_dir, exist_ok=True)

    for i, page in enumerate(doc):
        # 4K UHD rendering (3840 x 2160)
        scale_x = 3840.0 / page.rect.width
        scale_y = 2160.0 / page.rect.height
        mat = fitz.Matrix(scale_x, scale_y)
        pix = page.get_pixmap(matrix=mat)
        img_path = f"{hires_dir}/page_{i}.png"
        pix.save(img_path)
        
        slide = prs.slides.add_slide(blank_layout)
        slide.shapes.add_picture(img_path, 0, 0, Inches(13.333), Inches(7.5))

    # Save exclusively as the ONE official PPTX deliverable in root
    prs.save(OFFICIAL_PPTX_NAME)
    print(f"Saved Single Official PPTX: {OFFICIAL_PPTX_NAME} ({os.path.getsize(OFFICIAL_PPTX_NAME)} bytes)")

def cleanup_stray_outputs():
    """Removes all stray and redundant PDF/PPTX outputs so only ONE PDF and ONE PPT remain."""
    print("Cleaning up redundant and stray PDF/PPTX files...")
    allowed_root_files = {OFFICIAL_PDF_NAME, OFFICIAL_PPTX_NAME}
    
    # Check root directory
    for item in os.listdir("."):
        if (item.endswith(".pdf") or item.endswith(".pptx") or item.endswith(".ppt")) and item not in allowed_root_files:
            try:
                os.remove(item)
                print(f"Deleted stray file: {item}")
            except Exception as e:
                print(f"Could not delete {item}: {e}")

    # Check docs directory
    if os.path.exists("docs"):
        for item in os.listdir("docs"):
            full_path = os.path.join("docs", item)
            if os.path.isfile(full_path) and (item.endswith(".pptx") or item.endswith(".ppt")):
                try:
                    os.remove(full_path)
                    print(f"Deleted stray docs file: {full_path}")
                except Exception as e:
                    print(f"Could not delete {full_path}: {e}")
            elif os.path.isfile(full_path) and item.endswith(".pdf") and item != "Airtel_SYNC_Case.pdf":
                try:
                    os.remove(full_path)
                    print(f"Deleted stray docs file: {full_path}")
                except Exception as e:
                    print(f"Could not delete {full_path}: {e}")

def main():
    cleanup_stray_outputs()
    pdf_out = compile_beamer_pdf()
    generate_4k_beamer_pptx(pdf_out)
    print("FINISHED: Strictly 1 PDF and 1 PPT exist for submission.")

if __name__ == "__main__":
    main()
