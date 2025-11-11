import os
import pickle
import time

import filetype
import mutagen
import xxhash
from tqdm import tqdm

MUSIC_LIBRARY_PATH = r"C:\Users\bofeh\Dev\tmp\citrus_test_collection"


class AlbumListing:
    def __init__(self, name):
        self.name = name
        self.track_ids = []

    def add_track(self, track_hash):
        self.track_ids.append(track_hash)


class ArtistListing:
    def __init__(self, name):
        self.name = name
        self.albums = {}

    def check_add_album(self, album):
        if album not in self.albums:
            self.albums[album] = AlbumListing(album)

    def check_add_track(self, album, track_hash):
        self.check_add_album(album)
        self.albums[album].add_track(track_hash)


class LibraryDb:
    def __init__(self):
        self.artists = {}
        self.hash_db = {}

    def __getitem__(self, track_hash):
        return self.hash_db.get(track_hash)

    def clear(self):
        self.artists.clear()
        self.hash_db = {}

    def check_add_track(self, artist, album, track, track_hash):
        self.check_add_album_(artist, album)
        self.artists[artist].check_add_track(album, track_hash)

        if track_hash not in self.hash_db:
            self.hash_db[track_hash] = (artist, album, track)
            return True
        else:
            return False

    def check_add_artist_(self, artist):
        if artist not in self.artists:
            self.artists[artist] = ArtistListing(artist)

    def check_add_album_(self, artist, album):
        self.check_add_artist_(artist)
        self.artists[artist].check_add_album(album)


def iterate_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)


def get_hash(path):
    with open(path, "rb") as f:
        return xxhash.xxh64(f.read()).intdigest()


class Citrus:
    def __init__(self):
        if os.path.isfile("db.pickle"):
            with open("db.pickle", "rb") as f:
                self.db = pickle.load(f)
        else:
            self.db = LibraryDb()
            self.regenerate_db()

    def regenerate_db(self):
        self.db.clear()

        file_count = sum(1 for _ in iterate_files(MUSIC_LIBRARY_PATH))
        with tqdm(desc=f"{MUSIC_LIBRARY_PATH}", total=file_count) as pbar:
            for file in iterate_files(MUSIC_LIBRARY_PATH):
                if filetype.is_audio(file):
                    tags = dict(mutagen.File(file).tags)

                    artist = tags.get("artist")
                    if artist is not None:
                        artist = artist[0]

                    album = tags.get("album")
                    if album is not None:
                        album = album[0]

                    track_hash = get_hash(file)
                    if not self.db.check_add_track(artist, album, file, track_hash):
                        print(f"\nDuplicate file hash: {file}, {self.db[track_hash][2]}")

                pbar.update()

        with open("db.pickle", "wb") as f:
            pickle.dump(self.db, f)


if __name__ == "__main__":
    t1 = time.time()
    Citrus()
    t2 = time.time()
    print(f"Took {t2 - t1} seconds")
