from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL


def get_video_id(url: str) -> str:
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]

    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]

    raise ValueError("Invalid YouTube URL")


def get_transcript(video_id: str):
    api = YouTubeTranscriptApi()

    transcript_list = api.list(video_id)

    transcripts = list(transcript_list)

    if not transcripts:
        raise ValueError("No transcript available for this video.")

    # Prefer manually created transcripts
    manual = [t for t in transcripts if not t.is_generated]

    if manual:
        transcript = manual[0]
    else:
        transcript = transcripts[0]

    print("Transcript language:", transcript.language)
    print("Transcript language code:", transcript.language_code)
    print("Auto-generated:", transcript.is_generated)

    return transcript.fetch()


def get_playlist_videos(playlist_url: str):
    options = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
    }

    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(
            playlist_url,
            download=False,
        )

    playlist_id = info.get("id")

    videos = []

    for entry in info.get("entries", []):
        if not entry:
            continue

        videos.append(
            {
                "video_id": entry.get("id"),
                "video_title": entry.get("title"),
            }
        )

    return playlist_id, videos