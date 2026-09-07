from youtube import get_video_id, get_transcript
from chunking import create_chunks


url = input("Enter YouTube URL: ")

video_id = get_video_id(url)

print("Video ID:", video_id)

transcript = get_transcript(video_id)

print("Number of transcript segments:", len(transcript))

chunks = create_chunks(transcript)

print("Number of chunks:", len(chunks))

for i, chunk in enumerate(chunks[:3]):
    print(f"\n--- CHUNK {i + 1} ---")
    print("Start:", chunk["start_time"])
    print("End:", chunk["end_time"])
    print("Text:", chunk["text"])