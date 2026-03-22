import torch
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

text_summary = None


def get_text_summary_pipeline():
    global text_summary
    if text_summary is None:
        kwargs = {"model": "sshleifer/distilbart-cnn-12-6"}
        if torch.cuda.is_available():
            kwargs["torch_dtype"] = torch.bfloat16
        text_summary = pipeline("summarization", **kwargs)
    return text_summary

def extract_video_id(youtube_url):
    """Extracts YouTube video ID from URL."""
    query = urlparse(youtube_url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    elif query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            return parse_qs(query.query).get('v', [None])[0]
        elif query.path.startswith('/embed/'):
            return query.path.split('/')[2]
        elif query.path.startswith('/v/'):
            return query.path.split('/')[2]
    return None

def get_transcript(video_id):
    """Fetches the transcript using YouTube Transcript API."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([t['text'] for t in transcript])
        return full_text
    except Exception as e:
        return f"Error fetching transcript: {e}"

def summarize_from_url(youtube_url, api_key=None):
    """Main function to summarize YouTube video."""
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return "Invalid YouTube URL."

    transcript = get_transcript(video_id)
    if transcript.startswith("Error"):
        return transcript

    try:
        if len(transcript) > 4000:
            transcript = transcript[:4000]
        summary = get_text_summary_pipeline()(transcript, min_length=100, max_length=300, do_sample=False)[0]['summary_text']
        return summary
    except Exception as e:
        return f"Error during summarization: {e}"

