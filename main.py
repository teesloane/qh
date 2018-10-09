""" Sing that song. 
- TODO - Make runnable from anywhere 
"""
import os
import shutil
from glob import glob
from pydub import AudioSegment
from halo import Halo
import argparse

SONGS = []

TMP_FOL = "./tmp/"  # DO NOT TOUCH, gets RECURSIVELY DELETED
MIX_FOL = "../mix/"  # FIXME should be "where the cmd is run."  Currently hardcoded.
EXPORT_FOL = "./export/"  # DO NOT TOUCH, can get RECURSIVELY DELETED
TRACKLIST = EXPORT_FOL + "./tracklist.txt"
CROSSFADE_TIME = 3500
SAMPLE_SIZE = 5000  # Changes based on num songs passed in.


@Halo(text="Loading songs as AudioSegments", spinner="arrow3")
def load_songs(song_list, ext):
    """Load songs from mix folder and convert to AudioSegments + data"""

    songs = glob(MIX_FOL + "*" + ext)
    global SAMPLE_SIZE
    num_songs = len(songs)
    SAMPLE_SIZE = (60 / len(songs) * 1000 ) + CROSSFADE_TIME
    

    for file in songs:
        song = AudioSegment.from_mp3(file)

        audio_data = {
            "name": file.replace("../mix/", "").replace(ext, ""),
            "path:": file,
            "mp3": song,
            "sample": sample_song(song),
            "wav_path": "",
            "rate": None,
            "aud_data": None,
            "amp_x_time": None,
        }
        song_list.append(audio_data)


def setup():
    """Check for/remove/setup necessary folders"""

    if os.path.exists(EXPORT_FOL):
        choice = input("Export folder already exists, proceed and overwrite? [Y/n]: ")
        if choice == "Y":
            shutil.rmtree(EXPORT_FOL)
        else:
            print("Exiting!")
            exit()

    if not os.path.exists(MIX_FOL):
        print("No 'mix' folder found.")
        exit()

    if glob(MIX_FOL + "*.mp3") == []:
        print("No mp3 files found in 'mix' folder")
        exit()

    if not os.path.exists(TMP_FOL):
        os.makedirs(TMP_FOL)

    if not os.path.exists(EXPORT_FOL):
        os.makedirs(EXPORT_FOL)


@Halo(text="Converting MP3s to WAV for analysis", spinner="bouncingBall")
def mp3_list_to_wav(lst):
    """Convert list of mp3s to wavs. Adds wav path to the SONGS list."""
    for file in lst:
        wav_path = TMP_FOL + file["name"] + ".wav"  # get proper wave file name.
        with open(wav_path, "wb") as ftwo:  # write wavs to temp folder.
            file["mp3"].export(ftwo, format="wav")
            file["wav_path"] = wav_path


def mixdown(is_sample):
    """Creates a playlist and saves to file. Can also make a 'sampler'"""
    # Spinner can't be a decorator or it glitches with export_playlist
    spinner = Halo(text="Building playlist...️", spinner="earth")
    spinner.start()

    s_sorted = sorted(SONGS, key=lambda k: k["name"])
    tracklist = open(TRACKLIST, "a")
    playlist = AudioSegment.empty()

    # Write playlist and tracklist to memory.
    for idx, song in enumerate(s_sorted):  # Concat audio objects into full playlist.
        # If we're just getting a sample , concat a playlist of samples.
        if is_sample:
            if idx == 0:
                playlist = song["sample"][:SAMPLE_SIZE]
            else:
                audio = song["sample"]
                playlist = playlist.append(audio, crossfade=CROSSFADE_TIME)

        # Otherwise, just make the full playlist.
        else:
            audio = song["mp3"]
            playlist = playlist + audio

        tracklist.write(song["name"] + "\n")

    tracklist.close()
    spinner.stop()

    if is_sample:
        export_playlist(playlist.fade_in(2000).fade_out(2000), "sample")
    else:
        export_playlist(playlist)


def sample_song(song):
    """Take song, get it's length, divide by two, subtract half of sampleSize, return audio"""
    song_length = len(song) / 1000 * 60
    song_middle = song_length / 2 - (SAMPLE_SIZE / 2)
    sliced_song = song[song_middle : song_middle + SAMPLE_SIZE]
    return sliced_song


@Halo(text="Saving playlist...", spinner="moon")
def export_playlist(playlist, name="output"):
    """Saves playlist to file"""
    out_f = open(EXPORT_FOL + "/" + name + ".mp3", "wb")
    playlist.export(out_f, format="mp3")


def teardown():
    """Remove temporary files"""
    shutil.rmtree(TMP_FOL)  # This is probaby a bad idea.
    print("Playlist exported to: './export/ folder'")


def main(args):
    """sing some songs"""
    setup()
    load_songs(SONGS, ".mp3")
    mixdown(args.s)
    teardown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", help="Mix down samples of the songs.", action="store_true"
    )
    args = parser.parse_args()
    main(args)
