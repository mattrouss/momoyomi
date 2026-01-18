import time
import argparse
import subprocess
import re
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

parser = argparse.ArgumentParser(
    description='File watcher to convert manga to EPUB format')
parser.add_argument('--data-path', default=".",
                    help='Path to watch for manga changes (recursively)')

args = parser.parse_args()


class Watcher:

    def __init__(self, directory=".", handler=FileSystemEventHandler()):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory

    def run(self):
        self.observer.schedule(
            self.handler, self.directory, recursive=True)
        self.observer.start()

        print(f"Watcher Running in directory: {self.directory}")
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()
        print("Watcher Terminated")


class MangaHandler(FileSystemEventHandler):
    def __init__(self):
        self.ebook_convert_options = [
            "--output-profile", "tablet", "--no-default-epub-cover"]

    def convert_file_to_epub(self, src_cbz_path: Path, dst_epub_path: Path):
        # Structure: data-path/<Source>/<Manga Title>/<chapter>.cbz
        # Extract manga title from parent folder
        manga_title = src_cbz_path.parent.name.replace("_", " ")

        # Extract chapter number from filename (e.g., Chapter 123)
        match = re.search(r'Chapter\s+(\d+)', src_cbz_path.stem, re.IGNORECASE)
        chapter_number = match.group(1) if match else "0"

        # Build conversion command with metadata
        convert_options = [
            "--output-profile", "tablet",
            "--no-default-epub-cover",
            "--title", f"{src_cbz_path.stem}",
            "--series", manga_title,
            "--series-index", chapter_number,
            "--tags", "Manga",
            "--verbose"
        ]

        print(f"Converting: {src_cbz_path.name} -> {dst_epub_path.name}")
        try:
            subprocess.run(["ebook-convert", str(src_cbz_path), str(dst_epub_path)] + convert_options,
                           check=True)
            print(f"Successfully converted to {dst_epub_path}")
        except:
            print("Error converting ebook to epub, returned with non-zero exit code.")

    def on_created(self, event):
        if event.is_directory:
            return

        cbz_path = Path(event.src_path)

        if cbz_path.suffix != ".cbz":
            return

        print(f"\nNew CBZ file detected: {cbz_path}")

        epub_path = cbz_path.parent / (cbz_path.stem + ".epub")
        self.convert_file_to_epub(cbz_path, epub_path)

        # Delete the original CBZ file after successful conversion
        cbz_path.unlink()
        print(f"Deleted original CBZ file: {cbz_path.name}")


if __name__ == "__main__":
    manga_handler = MangaHandler()
    w = Watcher(args.data_path, manga_handler)

    w.run()
