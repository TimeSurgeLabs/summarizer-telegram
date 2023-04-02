import re

def get_youtube_video_id(url: str) -> str:
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|v\/)|youtu\.be\/|youtube\.com\/(?:user\/.*\/|playlist\?list=))?(?P<id>[A-Za-z0-9_-]{11})'
    match = re.search(pattern, url)

    if match:
        return match.group('id')
    else:
        return None

def split_string_on_space(s: str, n: int) -> list[str]:
    words = s.split(' ')
    result = []
    current_line = ''

    for word in words:
        if len(current_line) + len(word) + 1 > n:
            result.append(current_line.strip())
            current_line = ''

        current_line += ' ' + word

    if current_line.strip():
        result.append(current_line.strip())

    return result

if __name__=='__main__':
    # Test cases
    url1 = 'This is a test case for a youtube video message! https://www.youtube.com/watch?v=abcdefghijk'
    url2 = 'https://youtu.be/abcdefghijk'
    url3 = 'https://www.youtube.com/embed/abcdefghijk'
    url4 = "There is no content here."

    assert get_youtube_video_id(url1) == "abcdefghijk"  # Output: abcdefghijk
    assert get_youtube_video_id(url2) == "abcdefghijk"  # Output: abcdefghijk
    assert get_youtube_video_id(url3) == "abcdefghijk"  # Output: abcdefghijk
    assert get_youtube_video_id(url4) == None  # Output: None
