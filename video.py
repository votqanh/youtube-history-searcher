import json
import urllib
from http.client import HTTPException
from urllib.error import HTTPError

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptAvailable, TranscriptsDisabled, NoTranscriptFound


def check_transcript(videoid, search, cnt):
    try:
        # list of dictionaries
        transcript = YouTubeTranscriptApi.get_transcript(videoid)
    except (NoTranscriptAvailable, TranscriptsDisabled, NoTranscriptFound, HTTPException):
        store(videoid)
        return [404, cnt]
    # no internet
    except Exception as e:
        return [503, e]

    # return first match in transcript else None
    a = next((i for i, item in enumerate(transcript) if search.lower() in item['text'].lower()), None)

    if a is not None:
        timestamp = int(transcript[a]['start'])
        title = get_title(videoid)
        cnt += 1
        return [True, f"youtube.com/watch?v={videoid}&t={timestamp}\n", title, cnt]
    else:
        return [False, cnt]


def get_title(videoid):
    try:
        params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % videoid}
        url = "https://www.youtube.com/oembed"
        query_string = urllib.parse.urlencode(params)
        url = url + "?" + query_string

        with urllib.request.urlopen(url) as response:
            response_text = response.read()
            data = json.loads(response_text.decode())
            title = data['title']
    except HTTPError:
        return "can't get title of this video. sorry :("

    return title


def store(videoid):
    with open('no_cc_ids.txt', 'a') as f:
        f.write(f'{videoid}\n')
