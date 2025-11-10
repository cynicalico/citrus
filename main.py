import json
import os
import time

import filetype
import mutagen
import xxhash

MUSIC_LIBRARY_PATH = r"C:\Users\bofeh\Dev\tmp\citrus_test_collection"


class LibraryDb:
    def __init__(self):
        self.data = {
            "lookup_artist": {},
            "lookup_hash": {}
        }

    def check_add_artist(self, artist):
        if artist not in self.data["lookup_artist"]:
            self.data["lookup_artist"][artist] = {
                "albums": {},
                "tracks": [],
            }

    def check_add_album(self, artist, album):
        self.check_add_artist(artist)

        if album not in self.data["lookup_artist"][artist]["albums"]:
            self.data["lookup_artist"][artist]["albums"][album] = {
                "tracks": [],
            }

    def check_add_track(self, artist, album, track, md5):
        if album is None:
            self.check_add_artist(artist)
            self.data["lookup_artist"][artist]["tracks"].append((track, md5))

        else:
            self.check_add_album(artist, album)
            self.data["lookup_artist"][artist]["albums"][album]["tracks"].append((track, md5))

        # TODO: log collisions
        self.data["lookup_hash"][md5] = (artist, album, track)


def get_hash(path):
    with open(path, 'rb') as f:
        return xxhash.xxh64(f.read()).intdigest()


class Citrus:
    def __init__(self):
        self.db = LibraryDb()

        for root, dirs, files in os.walk(MUSIC_LIBRARY_PATH):
            for file in files:
                path = os.path.join(root, file)
                if filetype.is_audio(path):
                    tags = dict(mutagen.File(path).tags)
                    artist = tags.get("artist", None)
                    if artist is not None:
                        artist = artist[0]
                    album = tags.get("album", None)
                    if album is not None:
                        album = album[0]
                    self.db.check_add_track(artist, album, path, get_hash(path))

        json.dump(self.db.data, open("db.json", "w"), indent=4)


if __name__ == '__main__':
    t1 = time.time()
    Citrus()
    t2 = time.time()
    print(f"Took {t2 - t1} seconds")
