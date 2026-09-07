def create_chunks(transcript, max_chars=1200, overlap_segments=2):
    chunks = []

    current_segments = []
    current_length = 0

    for segment in transcript:
        current_segments.append(segment)
        current_length += len(segment.text)

        if current_length >= max_chars:
            chunk = build_chunk(current_segments)
            chunks.append(chunk)

            # Keep the last few transcript segments as overlap
            current_segments = current_segments[-overlap_segments:]
            current_length = sum(
                len(segment.text) for segment in current_segments
            )

    # Add remaining segments
    if current_segments:
        chunks.append(build_chunk(current_segments))

    return chunks


def build_chunk(segments):
    return {
        "text": " ".join(segment.text for segment in segments),
        "start_time": segments[0].start,
        "end_time": segments[-1].start + segments[-1].duration,
    }