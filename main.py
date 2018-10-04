""" DOES STUFF """

import os
import shutil
from glob import glob
import scipy.io.wavfile
from pydub import AudioSegment

SONGS = []
TMP_FOL = "./tmp/"
MIX_FOL = "../mix/"


def load_songs(song_list, ext):
    """Load songs from mix folder and convert to AudioSegments + data"""
    print("Loading songs as AudioSegments...")
    for file in glob("../mix/*" + ext)[0:3]:  # if !dev remove 0:3
        audio_data = {
            "name": file.replace("../mix/", "").replace(ext, ""),
            "path:": file,
            "mp3": AudioSegment.from_mp3(file),
            "wav_path": "",
        }
        song_list.append(audio_data)


def setup():
    """set up temp folder, convert to wav"""
    if not os.path.exists(TMP_FOL):
        os.makedirs(TMP_FOL)

    load_songs(SONGS, ".mp3")
    mp3_list_to_wav(SONGS)


def mp3_list_to_wav(lst):
    """Convert list of mp3s to wavs. Adds wav path to the SONGS list."""
    for file in lst:
        wav_path = TMP_FOL + file["name"] + ".wav"
        print("f item is", file["name"])
        with open(wav_path, "wb") as ftwo:
            file["mp3"].export(ftwo, format="wav")
            file["wav_path"] = wav_path


def analysis():
    """Do that thing"""
    rate, aud_data = scipy.io.wavfile.read(SONGS[0]["wav_path"])
    print(rate)
    print(aud_data)
    # print("song length is of", SONGS[0]['name'], (aud_data.shape[0] / rate) / 60)

def teardown():
    """Remove temporary files"""
    shutil.rmtree("./tmp")


def main():
    """sing some songs"""
    setup()
    analysis()
    # teardown()


if __name__ == "__main__":
    main()