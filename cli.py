import click
from main import process_video_transcript
import re

def validate_youtube_url(ctx, param, value):
    """Extract video ID from YouTube URL or return the ID if directly provided."""
    if not value:
        return None
        
    # Try to extract video ID from various YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\?\/]+)',
        r'^([a-zA-Z0-9_-]{11})$'  # Direct video ID format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, value)
        if match:
            return match.group(1)
            
    raise click.BadParameter('Invalid YouTube URL or video ID')

@click.command()
@click.argument('video_url', callback=validate_youtube_url)
@click.option('--suffix', '-s', default='transcript',
              help='Suffix to append to output files (default: transcript)')
@click.option('--force', '-f', is_flag=True, default=False,
              help='Force rewrite existing summaries')
def process_video(video_url, suffix, force):
    """Process a YouTube video to generate blog-style summaries using multiple LLMs.
    
    VIDEO_URL can be a full YouTube URL or just the video ID.
    
    Example usage:
    
    \b
    # Using full URL
    python cli.py https://www.youtube.com/watch?v=dQw4w9WgXcQ
    
    \b
    # Using just the video ID
    python cli.py dQw4w9WgXcQ
    
    \b
    # Using custom suffix
    python cli.py dQw4w9WgXcQ -s custom_name
    
    \b
    # Force rewrite existing summaries
    python cli.py dQw4w9WgXcQ --force
    """
    try:
        output_file = process_video_transcript(video_url, suffix, force)
        click.echo(f"✅ Successfully processed video! Output saved to: {output_file}")
    except Exception as e:
        click.echo(f"❌ Error processing video: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    process_video() 