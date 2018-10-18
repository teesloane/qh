# QH

`QH` is a utility for building playlists from a folder of mp3s. Basically it:

- Grabs mp3 in a folder, sorts by name, and joins them into a playlist; and
- exports that as a single mp3.

QH also creates a little "sample" playlist that grabs a snippet of each song in the playlist and joins them together with crossfades to give you an mp3 snapshop of how the mix might sound. Currently this behaviour happens by default, but will eventually be optional.

## Usage

- Download or build the executable and place in your path (ex, `/usr/local/bin`)
- create a folder called `mix` with mp3's in it. The playlist will order the songs based on filenames like so:

```
# You can name songs however you like, but use 
# `01, 02, ...` ordering if you want that order in the mix.

01 - The Artist - The Song Name
02 - Another Artist - Another Song Name
```

- Run `QH` in a directory with the `mix` folder.
- Head to the newly created `export` folder to grab your mix.


## Advanced Usage

You can add id3 tags to the mix by adding command line flags when you run `QH`.

```sh
QH --artist="SurfMaster Mixes" --title="Set Waves Forever"

## run help to see possible commands:

QH --help

```


## Development

- QH uses `pipenv` in development. 
- The project is used with `pyinstaller` to create executables.
- `make` commands assume you have [trash](https://github.com/sindresorhus/trash) installed. ¯\\_(ツ)_/¯ 
