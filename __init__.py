import os
from aqt import mw
from aqt.utils import showInfo, askUser, getText
from aqt.qt import *
import urllib.parse
from pathlib import Path

# Hardcoded Obsidian directory path
OB_DIRECTORY = "C:/Users/ganesh.nr/Documents/Obsidian Vault/Personal"  # Change this to your Obsidian directory path

def get_obsidian_dir():
    dir_path = OB_DIRECTORY

    # Check if directory exists
    if not os.path.isdir(dir_path):
        showInfo(f'The directory {dir_path} does not exist.')
        return None

    return dir_path

def get_vocab_files(dir_path):
    dir_path = Path(dir_path)
    vocab_dir = dir_path / "Vocabulary"
    # The vault name is just the last part of the directory path
    vault_name = dir_path.name

    if not vocab_dir.exists() or not vocab_dir.is_dir():
        showInfo(f'No "Vocabulary" directory found at {dir_path}.')
        return

    file_urls = {}

    # Iterate over the markdown files in the directory
    for file in vocab_dir.glob("*.md"):
        # File paths in the Obsidian URL should use forward slashes
        file_path = f"Vocabulary/{file.stem}"
        # The Obsidian URL format is obsidian://open?vault=[vault]&file=[file]
        obsidian_url = f"obsidian://open?vault={vault_name}&file={file_path}"
        # The key is the file name without the .md extension
        key = file.stem
        file_urls[key] = obsidian_url

    return file_urls


def update_cards(deck, file_urls):
    
    # Set the 'Obsidian Link' field to empty for all cards in the current deck
    card_ids = mw.col.findCards(f'deck:"{deck["name"]}"')
    for card_id in card_ids:
        card = mw.col.getCard(card_id)
        note = card.note()
        if "Obsidian Link" in note:
            file_name = note["Back"] + ".md"  # Assuming card_id can be used as the file name, adjust this accordingly
            note["Obsidian Link"] = f'Obsidian://open?vault=Personal&file={urllib.parse.quote(file_name)}'
        note.flush()
        
    for file_name, obsidian_url in file_urls.items():
        # Get all card ids in the current deck
        card_ids = mw.col.findCards(f'deck:"{deck["name"]}" {file_name}', order=None)
    
        for card_id in card_ids:
            card = mw.col.getCard(card_id)
            note = card.note()
            # Update the field named 'Obsidian Link'
            if "Obsidian Link" in note:
                obsidian_url = f'Obsidian://open?vault=Personal&file={urllib.parse.quote(file_name)}'
                note["Obsidian Link"] = obsidian_url
            note.flush()

            

def update_obsidian_links():
    dir_path = get_obsidian_dir()
    if not dir_path:
        return

    file_urls = get_vocab_files(dir_path)
    if not file_urls:
        return

    # Get the current deck
    deck = mw.col.decks.current()

    update_cards(deck, file_urls)

    # Show a completion message
    showInfo(f'Updated {len(file_urls)} Obsidian URLs in deck {deck["name"]}.')

# Add menu item
action = QAction("Sync With Obsidian", mw)
action.triggered.connect(update_obsidian_links)
mw.form.menuTools.addAction(action)
