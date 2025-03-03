from youtube_transcript_api import YouTubeTranscriptApi
import json

import os
from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import time
from settings import (
    TRANSCRIPTS_DIR, 
    OUTPUTS_DIR,
    GEMINI_MODEL,
    GPT_MODEL,
    CLAUDE_MODEL
)

def get_youtube_transcript(video_id, suffix="transcript"):
    """
    Get transcript for a YouTube video, storing in transcripts folder if not available.
    Returns the transcript data as JSON.
    
    Args:
        video_id (str): YouTube video ID
        suffix (str, optional): Suffix to append to filename. Defaults to "transcript"
    Returns:
        list: Transcript data as JSON
    """
    # Create transcripts directory if it doesn't exist
    transcripts_dir = Path(TRANSCRIPTS_DIR)
    
    # Check if any transcript exists for this video_id
    existing_files = list(transcripts_dir.glob(f"{video_id}_*.json"))
    if existing_files:
        # Use first found transcript file
        with open(existing_files[0]) as f:
            return json.load(f)
            
    # Get new transcript and save with requested suffix
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    filename = transcripts_dir / f"{video_id}_{suffix}.json"
    with open(filename, "w") as f:
        json.dump(transcript, f)
        
    return transcript

def create_transcript_summary(video_id, transcript_data, suffix="transcript", force=False):
    """Create summaries of the transcript using multiple LLMs"""
    # Combine transcript text
    full_text = " ".join([entry['text'] for entry in transcript_data])
    
    # Initialize LLM models using settings
    gemini = ChatGoogleGenerativeAI(model=GEMINI_MODEL)
    gpt = ChatOpenAI(model=GPT_MODEL) 
    claude = ChatAnthropic(model=CLAUDE_MODEL)
    
    # Prompt template for blog-style summary
    prompt_template = """
    You are a technical writer specializing in creating clear, comprehensive blog posts about complex topics. Your task is to analyze and summarize the following transcript into an engaging technical blog post.

    Important: If any part of the transcript is unclear, ambiguous, or seems to be missing context, mark it with [UNCLEAR: your observation] in your summary.

    Structure your blog post with the following sections:

    # Introduction
    - Brief overview of the topic and its significance
    - Core problem or technology being discussed

    # Technical Overview
    - Key concepts and terminology explained
    - System architecture or methodology breakdown
    - Create a mermaid diagram showing the system architecture
    - Technical diagrams or flowcharts (if described in transcript)

    # Deep Dive Analysis
    - Detailed examination of main technical components
    - Implementation challenges and solutions
    - Performance considerations and trade-offs
    - Include mermaid sequence diagrams showing component interactions
    - Add mermaid flowcharts for key processes

    # Practical Implementation
    - Step-by-step technical walkthrough (if provided)
    - Code examples or pseudocode (if mentioned)
    - Best practices and recommendations
    - Use mermaid diagrams to illustrate implementation steps

    # Discussion Points
    - Technical limitations and constraints
    - Future improvements or research directions
    - Industry implications
    - Include mermaid mindmaps for related concepts

    # Key Takeaways
    - Technical insights
    - Practical applications
    - Important considerations

    Use markdown formatting and include:
    - Technical definitions in `code blocks` where appropriate
    - Bullet points for lists
    - ### Subheadings for clear section breaks
    - > Blockquotes for important quotes from the transcript
    - Mermaid diagrams using ```mermaid syntax for:
      - System architecture (flowchart)
      - Component interactions (sequence)
      - Process flows (flowchart)
      - Implementation steps (flowchart)
      - Concept relationships (mindmap)

    Transcript to analyze:
    {text}
    """
    
    # Generate summaries from different models
    summaries = {}
    output_files = []
    
    # Helper function to check if summary exists and generate if not
    def get_model_summary(model_name, model, file_prefix, force=False):
        output_file = OUTPUTS_DIR / f"{video_id}_{suffix}_{file_prefix}_summary.md"
        if output_file.exists() and not force:
            with open(output_file, "r", encoding="utf-8") as f:
                return f.read(), output_file
                
        try:
            summary = model.invoke(prompt_template.format(text=full_text)).content
            markdown = f"""# {model_name} Summary for Video: {video_id}

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}

Model: {model_name}

{summary}"""
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown)
            return summary, output_file
        except Exception as e:
            error_msg = f"Error generating {model_name} summary: {str(e)}"
            return error_msg, None
    
    # Generate individual summaries
    gemini_summary, gemini_file = get_model_summary(GEMINI_MODEL, gemini, GEMINI_MODEL.lower(), force)
    gpt_summary, gpt_file = get_model_summary(GPT_MODEL, gpt, GPT_MODEL.lower(), force)
    claude_summary, claude_file = get_model_summary(CLAUDE_MODEL, claude, CLAUDE_MODEL.lower(), force)
    
    # Add successful files to output list
    output_files.extend([f for f in [gemini_file, gpt_file, claude_file] if f])
    
    # Create or update combined summary file
    combined_file = OUTPUTS_DIR / f"{video_id}_{suffix}_combined_summary.md"
    combined_content = f"""# Combined Video Summary: {video_id}

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Model Information
- Gemini Model: {GEMINI_MODEL}
- GPT Model: {GPT_MODEL}
- Claude Model: {CLAUDE_MODEL}

## Summaries from Different Models

### Gemini Summary
{gemini_summary}

### GPT-4 Summary
{gpt_summary}

### Claude Summary
{claude_summary}
"""
    with open(combined_file, "w", encoding="utf-8") as f:
        f.write(combined_content)
    
    output_files.append(combined_file)
    return output_files
def process_video_transcript(video_id, suffix="transcript", force=False):
    """Process a video: get transcript and generate summaries"""
    transcript_data = get_youtube_transcript(video_id, suffix)
    summary_file = create_transcript_summary(video_id, transcript_data, suffix, force)
    return summary_file

