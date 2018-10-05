""" Sing that song. 
- TODO - Make runnable from anywhere 
"""
import os
import shutil
from glob import glob
from pydub import AudioSegment
from halo import Halo

SONGS = []

TMP_FOL = "./tmp/"  # DO NOT TOUCH, gets RECURSIVELY DELETED
MIX_FOL = "../mix/"  # FIXME should be "where the cmd is run."  Currently hardcoded.
EXPORT_FOL = "./export/"  # DO NOT TOUCH, can get RECURSIVELY DELETED
TRACKLIST = EXPORT_FOL + "./tracklist.txt"


@Halo(text="Loading songs as AudioSegments", spinner="arrow3")
def load_songs(song_list, ext):
    """Load songs from mix folder and convert to AudioSegments + data"""
    for file in glob(MIX_FOL + "*" + ext)[:2]:  # DONT YOU, FORGET ABOUT FIXME
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
        wav_path = TMP_FOL + file["name"] + ".wav"  # get proper wave file name.
        with open(wav_path, "wb") as ftwo:  # write wavs to temp folder.
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


def teardown():
    """Remove temporary files"""
    shutil.rmtree(TMP_FOL)  # This is probaby a bad idea.
    print("Playlist exported to: './export/ folder'")


def main():
    """sing some songs"""
    setup()
    load_songs(SONGS, ".mp3")
    mixdown()
    teardown()


if __name__ == "__main__":
    main()
