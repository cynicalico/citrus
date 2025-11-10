import os
import time
import pickle

import filetype
import mutagen
import xxhash

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

    def check_add_artist(self, artist):
        if artist not in self.artists:
            self.artists[artist] = ArtistListing(artist)

    def check_add_album(self, artist, album):
        self.check_add_artist(artist)
        self.artists[artist].check_add_album(album)

    def check_add_track(self, artist, album, track, track_hash):
        self.check_add_album(artist, album)
        self.artists[artist].check_add_track(album, track_hash)

        # TODO: log collisions
        self.hash_db[track_hash] = (artist, album, track)


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

        for artist in self.db.artists.values():
            print(f"Artist: {artist.name}")
            for album in artist.albums.values():
                print(f"\tAlbum: {album.name}")
                for track in album.track_ids:
                    print(f"\t\tTrack: {self.db.hash_db[track]}")

        with open("db.pickle", "wb") as f:
            pickle.dump(self.db, f)


if __name__ == '__main__':
    t1 = time.time()
    Citrus()
    t2 = time.time()
    print(f"Took {t2 - t1} seconds")
