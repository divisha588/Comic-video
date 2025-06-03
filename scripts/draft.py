# === Document to Comic-Video AI Pipeline ===
# Libraries Needed
import fitz  # PyMuPDF for PDF reading
import openai
from  Pillow import Image, ImageDraw, ImageFont
import os
import uuid
import pyttsx3
import subprocess

# === Step 1: Extract Text from PDF ===
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = "".join(page.get_text() for page in doc)
    return text

# === Step 2: Summarize and Convert to Comic Dialogue ===
def summarize_and_convert_to_comic(text):
    prompt = f"""
    You are a smart AI that converts research papers into comic-style educational dialogues.
    Given the following text:

    {text[:4000]}  # Truncated for token limits

    Step 1: Summarize the main ideas in 5 bullet points.
    Step 2: Convert those ideas into a short comic-style dialogue between two characters:
    - AI Expert
    - Curious Hacker

    Include humor, clarity, and educational tone.
    Format:
    [AI Expert]: "..."
    [Curious Hacker]: "..."
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

# === Step 3: Generate Comic Panels as Images ===
def create_comic_panel(dialogue_text, output_folder="panels"):
    os.makedirs(output_folder, exist_ok=True)
    lines = dialogue_text.split("\n")
    panel_paths = []
    
    for i, line in enumerate(lines):
        if line.strip():
            img = Image.new("RGB", (800, 400), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()
            draw.text((10, 10), line, fill=(0, 0, 0), font=font)
            panel_path = os.path.join(output_folder, f"panel_{i}.png")
            img.save(panel_path)
            panel_paths.append(panel_path)
    return panel_paths

# === Step 4: Convert Dialogue to Speech ===
def convert_to_audio(dialogue_text, output_path="output_audio.mp3"):
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    engine.save_to_file(dialogue_text, output_path)
    engine.runAndWait()
    return output_path

# === Step 5: Combine Panels + Audio into Video ===
def create_video_from_panels(panel_paths, audio_path, output_video="final_video.mp4"):
    list_file = "panel_list.txt"
    with open(list_file, 'w') as f:
        for panel in panel_paths:
            f.write(f"file '{os.path.abspath(panel)}'\n")
            f.write("duration 2\n")
        f.write(f"file '{os.path.abspath(panel_paths[-1])}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
        "-i", audio_path, "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", output_video
    ])

    return output_video

# === Full Pipeline ===
def process_document_to_comic_video(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    dialogue = summarize_and_convert_to_comic(text)
    panel_paths = create_comic_panel(dialogue)
    audio_path = convert_to_audio(dialogue)
    video_path = create_video_from_panels(panel_paths, audio_path)
    return video_path

# === Example Run ===
# result_video = process_document_to_comic_video("sample_research_paper.pdf")
# print("Video created:", result_video)
