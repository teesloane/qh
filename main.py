""" Sing that song:
- loads a folder of MP3s from a 'mix' (required) folder.
- loop over, shove into DS with meta data etc
- Concat into two mixes: a sample mix and a full mix
- export to an /export folder.   


"""
import os
import sys
import shutil
import yaml
import argparse
import eyed3
from glob import glob
import unicodedata
from pydub import AudioSegment

SONGS = []
PWD = os.getcwd()
TMP_FOL = PWD + "/tmp/"  # DO NOT TOUCH, gets RECURSIVELY DELETED
MIX_FOL = PWD + "/mix/"
EXPORT_FOL = PWD + "/export/"  # DO NOT TOUCH, can get RECURSIVELY DELETED
TRACKLIST = EXPORT_FOL + "./tracklist.yml"
CROSSFADE_TIME = 3500
SAMPLE_SIZE = 5000  # Changes based on num songs passed in.
id3 = {}


def load_songs(song_list, ext):
    """Load songs from mix folder and convert to AudioSegments + data"""

    print("Loading songs as audio segments...")
    songs = glob(MIX_FOL + "*" + ext)
    global SAMPLE_SIZE
    SAMPLE_SIZE = (60 / len(songs) * 1000) + CROSSFADE_TIME

    for file in songs:
        song = AudioSegment.from_mp3(file)
        audio_data = {
            "name": file.replace("../mix/", "").replace(ext, ""),
            "path:": file,
            "mp3": song,
            "mp3_eyed3": eyed3.load(file),
            "sample": sample_song(song),
            "wav_path": "",
            "rate": None,
            "aud_data": None,
            "amp_x_time": None,
        }
        song_list.append(audio_data)


def setup():
    """Check for/remove/setup necessary folders"""
    print("Running setup...")
    if os.path.exists(EXPORT_FOL):
        print("Mix 'export' folder exists! Remove it if you wish to create a new mix.")
        sys.exit()

    if not os.path.exists(MIX_FOL):
        print(
            "No 'mix' folder found. Make sure you have a folder named 'mix' with audio files in it."
        )
        sys.exit()

    if glob(MIX_FOL + "*.mp3") == []:
        print("No mp3 files found in 'mix' folder")
        sys.exit()

    if not os.path.exists(TMP_FOL):
        os.makedirs(TMP_FOL)

    if not os.path.exists(EXPORT_FOL):
        os.makedirs(EXPORT_FOL)


def mixdown():
    """Joins audio files into a mix to be exported (full mix and sample mix)"""

    print("Doing mixdown...")
    s_sorted = sorted(SONGS, key=lambda k: k["name"])
    playlist_full = AudioSegment.empty()
    playlist_sample = AudioSegment.empty()

    # Write playlist and tracklist to memory.
    for idx, song in enumerate(s_sorted):  # Concat audio objects into full playlist.
        ### build sample playlist (can't start from AS.empty if using crossfade.)
        if idx == 0:
            playlist_sample = song["sample"]
        else:
            audio = song["sample"]
            playlist_sample = playlist_sample.append(audio, crossfade=CROSSFADE_TIME)

        ### build full playlist
        audio = song["mp3"]
        playlist_full = playlist_full + audio

    export_playlist(
        playlist_sample.fade_in(2000).fade_out(2000), id3["file_name"] + "_sample"
    )
    export_playlist(playlist_full, id3["file_name"])
    tracklist_yaml(s_sorted)


def tracklist_yaml(sorted_songs):
    print("Building tracklist...")
    tracklist = []
    for f in sorted_songs:
        data = dict()
        data["artist"] = unicodedata.normalize("NFKD", f["mp3_eyed3"].tag.artist).encode('ascii', "ignore")
        data["track"] = unicodedata.normalize("NFKD", f["mp3_eyed3"].tag.title).encode('ascii', "ignore")
        tracklist.append(data)

    with open(TRACKLIST, 'w') as outfile:
        yaml.dump(tracklist, outfile, default_flow_style=False)


def sample_song(song):
    """Take song, get it's length, divide by two, subtract half of sampleSize, return audio"""
    song_length = len(song) / 1000 * 60
    song_middle = song_length / 2
    sliced_song = song[song_middle : song_middle + SAMPLE_SIZE]
    return sliced_song


def export_playlist(playlist, name="output"):
    """Saves playlist to file"""
    out_f = open(EXPORT_FOL + "/" + name + ".mp3", "wb")
    playlist.export(
        out_f,
        format="mp3",
        bitrate="192k",
        tags={"artist": id3["artist"], "album": id3["album"], "title": id3["title"]},
    )


def teardown():
    """Remove temporary files"""
    shutil.rmtree(TMP_FOL)  # This is probaby a bad idea.
    print("Playlist exported to: './export/ folder'")


def main(args):
    """sing some songs"""
    setup()
    load_songs(SONGS, ".mp3")
    mixdown()
    teardown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-artist", help="id3 tag for mix artist")
    parser.add_argument("-album", help="id3 tag for mix artist")
    parser.add_argument("-title", help="id3 tag for mix artist")

    args = parser.parse_args()

    u = "Unknown"
    id3["file_name"] = args.title or "mix"
    id3["artist"] = args.artist or u
    id3["album"] = args.album or u
    id3["title"] = args.title or "mix"

    main(args)
