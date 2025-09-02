#!/usr/bin/env python3
"""
Document to Comic-Video AI Pipeline - Complete from Scratch Implementation
"""

import os
import re
import math
import random
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import textwrap

# PDF processing
try:
    import PyPDF2
except ImportError:
    print("Please install PyPDF2: pip install PyPDF2")
    exit(1)

# Image processing
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    print("Please install Pillow: pip install Pillow")
    exit(1)

# Audio processing
try:
    import wave
    import pyaudio
    import numpy as np
except ImportError:
    print("Please install pyaudio and numpy: pip install pyaudio numpy")
    exit(1)

# Video processing (we'll use basic FFmpeg if available)
import subprocess
import tempfile
import shutil

class TextProcessor:
    """Process and extract text from PDF documents"""
    
    def __init__(self):
        self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
    
    def extract_text_from_pdf(self, pdf_path: str, max_pages: int = 10) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = min(len(pdf_reader.pages), max_pages)
                
                for i in range(num_pages):
                    page = pdf_reader.pages[i]
                    text += page.extract_text() + "\n"
                    
        except Exception as e:
            print(f"Error reading PDF: {e}")
            
        return text
    
    def extract_key_concepts(self, text: str, num_concepts: int = 5) -> List[str]:
        """Extract key concepts from text using basic TF-IDF approach"""
        # Clean text
        text = re.sub(r'[^\w\s]', '', text.lower())
        words = text.split()
        
        # Remove stop words and short words
        words = [word for word in words if word not in self.stop_words and len(word) > 3]
        
        # Calculate word frequencies
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
            
        # Sort by frequency and get top concepts
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:num_concepts]]
    
    def summarize_text(self, text: str, num_sentences: int = 5) -> str:
        """Basic text summarization using sentence scoring"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 0]
        
        # Score sentences based on word frequency
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = {}
        for word in words:
            if word not in self.stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Score each sentence
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            score = 0
            sentence_words = re.findall(r'\b\w+\b', sentence.lower())
            for word in sentence_words:
                if word in word_freq:
                    score += word_freq[word]
            sentence_scores[i] = score / (len(sentence_words) or 1)
        
        # Get top sentences
        top_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
        top_indices.sort()  # Maintain original order
        
        return ' '.join([sentences[i] for i in top_indices])
    
    def generate_dialogue(self, text: str, summary: str, concepts: List[str]) -> str:
        """Generate a comic-style dialogue based on the content"""
        # Simple rule-based dialogue generation
        dialogue = []
        
        # Introduction
        dialogue.append("[AI Expert]: Hey there! I see you're reading about interesting concepts.")
        dialogue.append(f"[Curious Hacker]: Yeah! This document mentions {', '.join(concepts[:3])}.")
        
        # Main content discussion
        dialogue.append("[AI Expert]: Let me break down the main ideas for you.")
        
        # Split summary into points
        summary_points = summary.split('. ')
        for i, point in enumerate(summary_points[:3]):
            if point.strip():
                dialogue.append(f"[AI Expert]: Point {i+1}: {point}.")
                dialogue.append(f"[Curious Hacker]: {self.generate_question_or_comment()}")

        # Conclusion
        dialogue.append("[AI Expert]: That's the gist of it! Want to dive deeper into any specific aspect?")
        dialogue.append("[Curious Hacker]: This is fascinating! Thanks for breaking it down.")
        
        return "\n".join(dialogue)
    
    def generate_question_or_comment(self) -> str:
        """Generate a random question or comment"""
        questions = [
            "That makes sense! How does this apply in practice?",
            "Interesting! What are the implications of this?",
            "I see! Are there any limitations to this approach?",
            "Fascinating! How does this compare to other methods?",
            "Got it! What's the real-world impact of this finding?"
        ]
        return random.choice(questions)


class ComicPanelGenerator:
    """Generate comic panels from dialogue text"""
    
    def __init__(self):
        self.panel_width = 800
        self.panel_height = 400
        self.background_colors = [
            (240, 248, 255),  # AliceBlue
            (255, 250, 240),  # FloralWhite
            (240, 255, 240),  # Honeydew
            (255, 245, 238),  # Seashell
            (245, 245, 245),  # WhiteSmoke
        ]
        
        # Try to find fonts, fall back to default if not available
        try:
            self.title_font = ImageFont.truetype("arial.ttf", 24)
            self.dialogue_font = ImageFont.truetype("arial.ttf", 18)
        except:
            self.title_font = ImageFont.load_default()
            self.dialogue_font = ImageFont.load_default()
    
    def create_panel(self, dialogue: str, panel_num: int, output_dir: str) -> str:
        """Create a single comic panel"""
        # Create background
        bg_color = random.choice(self.background_colors)
        img = Image.new('RGB', (self.panel_width, self.panel_height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Add a border
        draw.rectangle([(10, 10), (self.panel_width-10, self.panel_height-10)], outline=(0, 0, 0), width=2)
        
        # Add panel number
        draw.text((20, 20), f"Panel {panel_num + 1}", fill=(0, 0, 0), font=self.title_font)
        
        # Split dialogue into character and text
        if ':' in dialogue:
            character, text = dialogue.split(':', 1)
            character = character.strip().replace('[', '').replace(']', '')
            text = text.strip().replace('"', '')
        else:
            character = "Narrator"
            text = dialogue
        
        # Draw character name
        draw.text((50, 60), character, fill=(0, 0, 0), font=self.title_font)
        
        # Draw dialogue text with word wrapping
        self.draw_wrapped_text(draw, text, (70, 100), self.panel_width - 140, self.dialogue_font)
        
        # Add some simple comic elements
        self.add_comic_elements(draw)
        
        # Save panel
        panel_path = os.path.join(output_dir, f"panel_{panel_num:03d}.png")
        img.save(panel_path)
        
        return panel_path
    
    def draw_wrapped_text(self, draw, text: str, position: Tuple[int, int], max_width: int, font):
        """Draw text with word wrapping"""
        x, y = position
        lines = textwrap.wrap(text, width=40)  # Simple character-based wrapping
        
        for line in lines:
            draw.text((x, y), line, fill=(0, 0, 0), font=font)
            y += 30  # Line height
    
    def add_comic_elements(self, draw):
        """Add simple comic elements to the panel"""
        # Add some random shapes for visual interest
        for _ in range(3):
            x1 = random.randint(50, self.panel_width - 100)
            y1 = random.randint(150, self.panel_height - 100)
            x2 = x1 + random.randint(50, 150)
            y2 = y1 + random.randint(30, 80)
            
            color = (random.randint(200, 255), 
                    random.randint(200, 255), 
                    random.randint(200, 255), 
                    random.randint(50, 150))
            
            shape_type = random.choice(['rectangle', 'ellipse'])
            if shape_type == 'rectangle':
                draw.rectangle([x1, y1, x2, y2], fill=color, outline=None)
            else:
                draw.ellipse([x1, y1, x2, y2], fill=color, outline=None)


class AudioGenerator:
    """Generate audio from text using basic speech synthesis"""
    
    def __init__(self, sample_rate=44100, chunk_size=1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        
    def text_to_speech(self, text: str, output_path: str) -> bool:
        """Convert text to speech using a simple formant synthesis approach"""
        try:
            # Simple phoneme mapping (very basic)
            phoneme_map = {
                'a': [300, 800, 2400], 'e': [400, 1600, 2400], 
                'i': [300, 2000, 3000], 'o': [400, 800, 2400],
                'u': [300, 800, 2400], ' ': []
            }
            
            # Generate audio data
            audio_data = []
            for char in text.lower():
                if char in phoneme_map:
                    frequencies = phoneme_map[char]
                    # Generate a short tone for each phoneme
                    for freq in frequencies:
                        if freq:  # Skip spaces
                            samples = self.generate_tone(freq, 0.1)
                            audio_data.extend(samples)
                    # Add a short pause
                    audio_data.extend([0] * int(0.05 * self.sample_rate))
            
            # Convert to numpy array and normalize
            audio_array = np.array(audio_data)
            audio_array = audio_array / np.max(np.abs(audio_array)) * 0.8  # Normalize to 80% volume
            
            # Save as WAV file
            with wave.open(output_path, 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes((audio_array * 32767).astype(np.int16).tobytes())
                
            return True
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            return False
    
    def generate_tone(self, frequency: float, duration: float) -> List[float]:
        """Generate a simple tone with the given frequency and duration"""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, endpoint=False)
        wave = 0.5 * np.sin(2 * np.pi * frequency * t)
        
        # Apply a simple envelope to avoid clicks
        envelope = np.ones(samples)
        attack = int(0.1 * samples)
        release = int(0.2 * samples)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        
        return (wave * envelope).tolist()


class VideoGenerator:
    """Combine panels and audio into a video"""
    
    def __init__(self):
        self.check_ffmpeg()
    
    def check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("FFmpeg not found. Video generation will not work.")
            return False
    
    def create_video(self, panel_paths: List[str], audio_path: str, output_path: str) -> bool:
        """Create a video from panels and audio"""
        if not self.check_ffmpeg():
            return False
        
        try:
            # Create a temporary file listing all panels
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                list_file = f.name
                for panel in panel_paths:
                    f.write(f"file '{os.path.abspath(panel)}'\n")
                    f.write("duration 3\n")  # Show each panel for 3 seconds
            
            # Use ffmpeg to create video
            cmd = [
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', list_file,
                '-i', audio_path, '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-shortest', output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Clean up
            os.unlink(list_file)
            
            return True
            
        except Exception as e:
            print(f"Error creating video: {e}")
            return False


class DocumentToComicPipeline:
    """Main pipeline class that coordinates the entire process"""
    
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.text_processor = TextProcessor()
        self.panel_generator = ComicPanelGenerator()
        self.audio_generator = AudioGenerator()
        self.video_generator = VideoGenerator()
    
    def process(self, pdf_path: str, max_pages: int = 5) -> Dict[str, str]:
        """Process a PDF document into a comic video"""
        results = {}
        
        print("Step 1: Extracting text from PDF...")
        text = self.text_processor.extract_text_from_pdf(pdf_path, max_pages)
        results['extracted_text'] = text[:1000] + "..." if len(text) > 1000 else text
        
        print("Step 2: Analyzing content...")
        concepts = self.text_processor.extract_key_concepts(text)
        summary = self.text_processor.summarize_text(text)
        
        print("Step 3: Generating dialogue...")
        dialogue = self.text_processor.generate_dialogue(text, summary, concepts)
        results['dialogue'] = dialogue
        
        # Save dialogue to file
        dialogue_path = os.path.join(self.output_dir, "dialogue.txt")
        with open(dialogue_path, 'w') as f:
            f.write(dialogue)
        results['dialogue_path'] = dialogue_path
        
        print("Step 4: Creating comic panels...")
        panel_paths = []
        dialogue_lines = [line for line in dialogue.split('\n') if line.strip()]
        
        panels_dir = os.path.join(self.output_dir, "panels")
        os.makedirs(panels_dir, exist_ok=True)
        
        for i, line in enumerate(dialogue_lines):
            panel_path = self.panel_generator.create_panel(line, i, panels_dir)
            panel_paths.append(panel_path)
        
        results['panel_paths'] = panel_paths
        
        print("Step 5: Generating audio...")
        audio_path = os.path.join(self.output_dir, "audio.wav")
        success = self.audio_generator.text_to_speech(dialogue, audio_path)
        
        if success:
            results['audio_path'] = audio_path
            
            print("Step 6: Creating video...")
            video_path = os.path.join(self.output_dir, "comic_video.mp4")
            success = self.video_generator.create_video(panel_paths, audio_path, video_path)
            
            if success:
                results['video_path'] = video_path
            else:
                print("Video creation failed")
        else:
            print("Audio generation failed")
        
        return results


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Convert PDF documents to comic videos")
    parser.add_argument("input_pdf", help="Path to the input PDF file")
    parser.add_argument("-o", "--output", default="output", help="Output directory")
    parser.add_argument("-p", "--pages", type=int, default=5, help="Maximum pages to process")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_pdf):
        print(f"Error: File {args.input_pdf} not found")
        return
    
    print("Starting Document to Comic-Video Pipeline...")
    print("=" * 50)
    
    pipeline = DocumentToComicPipeline(args.output)
    results = pipeline.process(args.input_pdf, args.pages)
    
    print("\n" + "=" * 50)
    print("Pipeline completed!")
    
    if 'video_path' in results:
        print(f"Video created: {results['video_path']}")
    else:
        print("Pipeline completed with errors. Check output files.")
    
    print(f"Dialogue saved to: {results.get('dialogue_path', 'N/A')}")
    print(f"Panels saved to: {os.path.join(args.output, 'panels')}")


if __name__ == "__main__":
    main()
