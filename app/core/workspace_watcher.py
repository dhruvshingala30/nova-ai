import hashlib
import sys
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Ensure Python can find the 'rag' module
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.ingest_pdf import chunk_documents, extract_pdf_pages, ingest_to_chromadb

# Simple memory cache to avoid re-ingesting the exact same file
processed_hashes = {}

def get_file_hash(filepath: str):
    """
    Returns the MD5 hash of a file to detect true modifications.
    """
    hasher = hashlib.md5()
    with open(filepath, 'rb') as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()


class PDFIngestionHandler(FileSystemEventHandler):
    def process_pdf(self, file_path: str):
        if not file_path.lower().endswith('.pdf'):
            return

        try:
            current_hash = get_file_hash(filepath=file_path)
            if processed_hashes.get(file_path) == current_hash:
                return # Skip if file hasn't actually changed

            print(f"\n [Workspace Watcher] Detected new/modified PDF: {Path(file_path).name}")
            pages = extract_pdf_pages(file_path=file_path)
            chunks = chunk_documents(pages_data=pages)
            ingest_to_chromadb(chunks=chunks)

            processed_hashes[file_path] = current_hash
            print(f" [Workspace Watcher] successfully indexed {Path(file_path).name} into ChromaDB.\n")

        except Exception as e:  # noqa: BLE001
            print(f" [Workspace Watcher] Error processing {file_path}: {e}")

    def on_created(self, event):
        if not event.is_directory:
            self.process_pdf(str(event.src_path))

    def on_modified(self, event):
        if not event.is_directory:
            self.process_pdf(str(event.src_path))


def start_workspace_watcher(workspace_dir: str):
    """
    Initializes and starts the background directory observer.
    """
    event_handler = PDFIngestionHandler()
    observer = Observer()
    observer.schedule(event_handler, workspace_dir, recursive=False)
    observer.start()
    print(f" [Workspace Watcher] Auto-ingestion active on: {workspace_dir}")
    return observer