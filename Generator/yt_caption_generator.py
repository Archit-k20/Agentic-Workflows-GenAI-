from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def extract_video_id(youtube_url):
    try:
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
    except:
        return None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry['text'] for entry in transcript])
        return full_text
    except Exception as e:
        return f"Error fetching transcript: {e}"

def caption_from_youtube_url(url):
    video_id = extract_video_id(url)
    if not video_id:
        return "Invalid YouTube URL."
    return get_transcript(video_id)
