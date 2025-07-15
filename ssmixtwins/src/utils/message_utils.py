def join_segments(segments: list[str]) -> str:
    """
    Joins multiple HL7 segments into a single string, ensuring each segment is separated by a newline character.

    Args:
        segments (list[str]): List of HL7 segments to be joined.

    Returns:
        str: A single string containing all segments separated by newline characters.
    """
    return "\n".join(segments)


def _join_segments_dict(segments_dict, segments: list[str]) -> list[str]:
    if isinstance(segments_dict, dict):
        for v in segments_dict.values():
            _join_segments_dict(v, segments)
    elif isinstance(segments_dict, list):
        for v in segments_dict:
            if isinstance(v, dict):
                _join_segments_dict(v, segments)
            else:
                segments.append(str(v))
    elif segments_dict:
        segments.append(str(segments_dict))
    return segments


def join_segments_dict(all_segments: dict) -> str:
    segments = []
    _join_segments_dict(all_segments, segments)

    return "\n".join(segments)
