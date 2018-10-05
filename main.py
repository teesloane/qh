""" Sing that song. """
import os
import shutil
from glob import glob
import argparse
import scipy.io.wavfile
import numpy as np
from pydub import AudioSegment
from halo import Halo


SONGS = []

TMP_FOL    = "./tmp/"       # DO NOT TOUCH, gets RECURSIVELY DELETED
MIX_FOL    = "../mix/"      # FIXME will eventually be "where the cmd is run."  Currently hardcoded.
EXPORT_FOL = "./export/"    # DO NOT TOUCH, can get RECURSIVELY DELETED
TRACKLIST  = EXPORT_FOL + "./tracklist.txt"


@Halo(text="Loading songs as AudioSegments", spinner="arrow3")
def load_songs(song_list, ext):
    """Load songs from mix folder and convert to AudioSegments + data"""
    for file in glob(MIX_FOL + "*" + ext)[:2]:
        audio_data = {
            "name": file.replace("../mix/", "").replace(ext, ""),
            "path:": file,
            "mp3": AudioSegment.from_mp3(file),
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
        wav_path = TMP_FOL + file['name'] + ".wav"  # get proper wave file name.
        with open(wav_path, "wb") as ftwo:          # write wavs to temp folder.
            file["mp3"].export(ftwo, format="wav")
            file["wav_path"] = wav_path


def mixdown():
    """Creates a playlist and saves to file."""
    # Spinner can't be a decorator or it glitches with export_playlist
    spinner = Halo(text="Building playlist...️", spinner="earth")
    spinner.start()

    s_sorted = sorted(SONGS, key=lambda k: k["name"])
    tracklist = open(TRACKLIST, "a")
    playlist = AudioSegment.empty()

    # Write playlist and tracklist to memory.
    for song in s_sorted:  # Concat audio objects into full playlist.
        audio = song["mp3"]
        tracklist.write(song["name"] + "\n")
        playlist = playlist + audio

    tracklist.close()
    spinner.stop()
    export_playlist(playlist)


@Halo(text="Saving playlist...", spinner="moon")
def export_playlist(playlist):
    """Saves playlist to file"""
    out_f = open(EXPORT_FOL + "/output.mp3", "wb")
    playlist.export(out_f, format="mp3")


def analysis():
    """Basic analysis; mutate audio objects to store results
    # TODO properly output a CSV for each song."""

    print("Running Analysis...")
    mp3_list_to_wav(SONGS)
    for audio in SONGS:
        rate, aud_data = scipy.io.wavfile.read(audio["wav_path"])
        audio["rate"] = rate
        audio["aud_data"] = aud_data
        # 1000 == "step" values for the array.
        audio["amp_x_time"] = np.arange(0, float(aud_data.shape[0]), 1000) / rate

    # ch1 = aud_data[:, 0]
    # ch2 = aud_data[:, 1]
    np.savetxt("testfile", SONGS[1]["amp_x_time"], newline="\n")  # makes a giant file.
    # print("song length is", SONGS[0]['name'], (aud_data.shape[0] / rate) / 60)


def teardown():
    """Remove temporary files"""
    shutil.rmtree(TMP_FOL)  # This is probaby a bad idea.
    print("Playlist exported to: './export/ folder'")


def main(args):
    """sing some songs"""
    setup()
    load_songs(SONGS, ".mp3")
    mixdown()
    if args.a:
        analysis()
    teardown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", help="Run audio analysis on file.", action="store_true")
    args = parser.parse_args()
    main(args)
