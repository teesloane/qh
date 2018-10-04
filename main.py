""" Sing that song. """
import os
import shutil
from glob import glob
import scipy.io.wavfile
import numpy as np
from pydub import AudioSegment

# from prompt_toolkit import prompt
# from prompt_toolkit.validation import Validator, ValidationError

SONGS = []
QH_FOL = MIX_FOL = TMP_FOL = EXPORT_FOL = TRACKLIST = None # haha...


def setup_paths():
    global TMP_FOL, MIX_FOL, EXPORT_FOL, TRACKLIST # bad bad bad probably
    print("QHFOL IS ", QH_FOL)
    TMP_FOL = QH_FOL + "/program/tmp/"
    print("TMP_FOL", TMP_FOL)
    MIX_FOL = QH_FOL + "/mix/"
    EXPORT_FOL = QH_FOL + "/export/"
    TRACKLIST = EXPORT_FOL + "./tracklist.txt"


def load_songs(song_list, ext):
    """Load songs from mix folder and convert to AudioSegments + data"""
    print("Loading songs as AudioSegments...")
    for file in glob(MIX_FOL + "*" + ext)[:3]:
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
    """set up temp folder, convert to wav"""

    setup_paths()

    if not os.path.exists(TMP_FOL):
        os.makedirs(TMP_FOL)

    if not os.path.exists(EXPORT_FOL):
        os.makedirs(EXPORT_FOL)

    load_songs(SONGS, ".mp3")
    # mp3_list_to_wav(SONGS)


def mp3_list_to_wav(lst):
    """Convert list of mp3s to wavs. Adds wav path to the SONGS list."""
    for file in lst:
        wav_path = TMP_FOL + file["name"] + ".wav"
        print("f item is", file["name"])
        with open(wav_path, "wb") as ftwo:
            file["mp3"].export(ftwo, format="wav")
            file["wav_path"] = wav_path


def mixdown():
    songs_sorted = sorted(SONGS, key=lambda k: k["name"])
    tracklist = open(TRACKLIST, "a")
    tracklist.write(songs_sorted[0]["name"] + "\n")
    playlist = songs_sorted[0]["mp3"]
    for song in songs_sorted[1:]:
        print("Appending:", song["name"])
        audio = song["mp3"]
        tracklist.write(song["name"] + "\n")
        # playlist.append(audio, crossfade=2000) # this fails, sadly, so no crossfade .... :
        playlist = playlist + audio

    tracklist.close()

    out_f = open(EXPORT_FOL + "/output.mp3", "wb")
    playlist.export(out_f, format="mp3")


def analysis():
    """Basic analysis; mutate audio objects to store results
    TODO: properly output a CSV for each song."""
    for audio in SONGS:
        rate, aud_data = scipy.io.wavfile.read(audio["wav_path"])
        audio["rate"] = rate
        audio["aud_data"] = aud_data
        # 1000 == "step" values for the array.
        audio["amp_x_time"] = np.arange(0, float(aud_data.shape[0]), 1000) / rate

    # ch1 = aud_data[:, 0]
    # ch2 = aud_data[:, 1]
    # np.savetxt("testfile", SONGS[1]["amp_x_time"], newline="\n")  # makes a giant file.
    # print("song length is of", SONGS[0]['name'], (aud_data.shape[0] / rate) / 60)


def teardown():
    """Remove temporary files"""
    shutil.rmtree(TMP_FOL) # It bad!


def main():
    """sing some songs"""
    setup()
    mixdown()
    # analysis()
    teardown()


if __name__ == "__main__":
    QH_FOL = input("Path to playlist folder: ")
    print(type(QH_FOL))
    main()
