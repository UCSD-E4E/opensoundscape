"""test for opensoundscape.audiomoth module"""
from datetime import datetime
import pytz
import pytest
from opensoundscape import audiomoth


@pytest.fixture()
def veryshort_wav_str():
    return "tests/audio/veryshort.wav"


@pytest.fixture()
def silence_10s_mp3_str():
    return "tests/audio/silence_10s.mp3"


def test_audiomoth_start_time():
    filename = "20191219_123300.WAV"
    dt = datetime.strptime("20191219 12:33:00", "%Y%m%d %H:%M:%S")
    dt = pytz.utc.localize(dt)
    assert audiomoth.audiomoth_start_time(filename, filename_timezone="UTC") == dt


def test_audiomoth_start_time_hex_format():
    filename = "5DFB6DFC.WAV"
    dt = datetime.strptime("20191219 12:33:00", "%Y%m%d %H:%M:%S")
    dt = pytz.utc.localize(dt)
    assert audiomoth.audiomoth_start_time(filename, filename_timezone="UTC") == dt


def test_audiomoth_start_time_other_timezone():
    """test behavior when filename timezone is not UTC

    - should read the file name assuming it was written based on US/Eastern
    """
    filename = "20191219_073300.WAV"  # written in EST rather than UTC
    dt = datetime.strptime("20191219 12:33:00", "%Y%m%d %H:%M:%S")
    dt = pytz.utc.localize(dt)
    dt_read = audiomoth.audiomoth_start_time(
        filename, filename_timezone="US/Eastern", to_utc=False
    )
    assert dt_read == dt
    assert dt_read.tzname() == "EST"

    # should also work if we convert to UTC
    dt_read = audiomoth.audiomoth_start_time(
        filename, filename_timezone="US/Eastern", to_utc=True
    )
    assert dt_read == dt


def test_parse_audiomoth_metadata():
    metadata = {
        "filesize": 115200360,
        "album": None,
        "albumartist": None,
        "artist": "AudioMoth 24526B065D325963",
        "audio_offset": None,
        "bitrate": 500.0,
        "channels": 1,
        "comment": "Recorded at 10:25:00 04/04/2020 (UTC) by AudioMoth 24526B065D325963 at gain setting 2 while battery state was 4.7V.",
        "composer": None,
        "disc": None,
        "disc_total": None,
        "duration": 1800.0,
        "extra": {},
        "genre": None,
        "samplerate": 32000,
        "title": None,
        "track": None,
        "track_total": None,
        "year": None,
        "audio_offest": 352,
    }
    new_metadata = audiomoth.parse_audiomoth_metadata(metadata)
    assert new_metadata["audiomoth_id"] == "24526B065D325963"
    assert new_metadata["gain_setting"] == 2
    assert new_metadata["battery_state"] == 4.7
    assert new_metadata["recording_start_time"] == pytz.utc.localize(
        datetime(2020, 4, 4, 10, 25)
    )


def test_parse_audiomoth_from_path_wrong_metadata(veryshort_wav_str):
    with pytest.raises(ValueError):
        audiomoth.parse_audiomoth_metadata_from_path(veryshort_wav_str)