#!/usr/bin/env python3
import plistlib
import random
import os
import sys
import base64
import json
import urllib.request
import urllib.parse
import argparse
from urllib.parse import unquote, urlparse

# Prova a importare mutagen per le copertine incorporate nei file audio locali
try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None

def get_local_path(file_url):
    if not file_url: return None
    parsed = urlparse(file_url)
    return unquote(parsed.path)

def print_iterm_image(image_data):
    b64_img = base64.b64encode(image_data).decode('utf-8')
    sys.stdout.write(f"\033]1337;File=inline=1:{b64_img}\a\n")

def find_local_artwork(track_path):
    if not track_path or not os.path.exists(track_path): return None
    folder_path = os.path.dirname(track_path)
    
    common_names = ['cover.jpg', 'cover.png', 'folder.jpg', 'artwork.jpg', 'front.jpg']
    for name in common_names:
        img_path = os.path.join(folder_path, name)
        if os.path.exists(img_path):
            with open(img_path, 'rb') as f: return f.read()

    if MutagenFile:
        try:
            audio = MutagenFile(track_path)
            if audio:
                if hasattr(audio, 'tags') and audio.tags:
                    for tag in audio.tags.values():
                        if tag.__class__.__name__ == 'APIC': return tag.data
                if 'covr' in audio: return audio['covr'][0]
        except Exception: pass 
    return None

def fetch_artwork_from_api(album, artist):
    print("☁️ Cerco la copertina sui server Apple...")
    query = f"{album} {artist}"
    url = f"https://itunes.apple.com/search?term={urllib.parse.quote(query)}&entity=album&limit=1"
    print (f"🔗 URL API: {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data['resultCount'] > 0:
                img_url = data['results'][0]['artworkUrl100'].replace('100x100bb', '600x600bb')
                with urllib.request.urlopen(img_url) as img_response:
                    return img_response.read()
    except Exception as e: pass
    return None

def main(xml_file_path, min_official, min_saved):
    print(f"Lettura della libreria di iTunes in corso... (Filtri: >= {min_official} tracce ufficiali, >= {min_saved} salvate)\n")
    try:
        with open(xml_file_path, 'rb') as f:
            data = plistlib.load(f)
    except Exception as e:
        print(f"Errore nella lettura del file XML: {e}")
        return

    tracks = data.get("Tracks", {})
    if not tracks: return

    # Raggruppa le tracce per Album
    albums = {}
    for track_id, track_info in tracks.items():
        album_name = track_info.get("Album")
        artist_name = track_info.get("Album Artist") or track_info.get("Artist", "Sconosciuto")
        if not album_name: continue
            
        key = (album_name, artist_name)
        if key not in albums:
            albums[key] = []
        albums[key].append(track_info)

    # --- LOGICA DI FILTRAGGIO DINAMICA ---
    target_albums = {}
    for key, track_list in albums.items():
        official_track_count = track_list[0].get("Track Count", len(track_list))
        saved_track_count = len(track_list)
        
        # Filtra usando i parametri passati da linea di comando
        if official_track_count >= min_official and saved_track_count >= min_saved: 
            target_albums[key] = track_list

    if not target_albums:
        print(f"Non ho trovato nessun album con almeno {min_official} tracce ufficiali e {min_saved} salvate in libreria.")
        return

    # Scegli a caso tra quelli filtrati
    chosen_key = random.choice(list(target_albums.keys()))
    chosen_tracks = target_albums[chosen_key]
    album_name, artist_name = chosen_key
    
    official_count = chosen_tracks[0].get("Track Count", len(chosen_tracks))
    saved_count = len(chosen_tracks)
    
    print(f"🎵 Album selezionato: **{album_name}**")
    print(f"🎸 Artista: {artist_name}")
    print(f"💿 Tracce Ufficiali: {official_count} (Minimo richiesto: {min_official})")
    print(f"📥 Tracce Salvate: {saved_count} (Minimo richiesto: {min_saved})\n")

    # Logica Copertina
    artwork_data = None
    for track in chosen_tracks:
        location = track.get("Location")
        if location:
            track_path = get_local_path(location)
            artwork_data = find_local_artwork(track_path)
            if artwork_data: break

    if not artwork_data:
        artwork_data = fetch_artwork_from_api(album_name, artist_name)

    if artwork_data:
        print_iterm_image(artwork_data)
    else:
        print("❌ Impossibile recuperare la copertina.")

if __name__ == "__main__":
    # Imposta il parser degli argomenti da riga di comando
    parser = argparse.ArgumentParser(description="Estrai un album casuale dalla tua libreria iTunes.")
    
    # Argomento -t / --tracks
    parser.add_argument("-t", "--tracks", type=int, default=1, 
                        help="Numero minimo di tracce UFFICIALI che l'album deve avere (default: 1)")
    
    # Argomento -s / --saved
    parser.add_argument("-s", "--saved", type=int, default=1, 
                        help="Numero minimo di tracce SALVATE nella tua libreria per quell'album (default: 1)")
    
    parser.add_argument("-l", "--library", type=str, default="~/Music/Libreria.xml",
                        help="Percorso del file XML della libreria iTunes (default: ~/Music/Libreria.xml)")
    
    args = parser.parse_args()

    # Percorso del file XML (usando expanduser per gestire la tilde)
    raw_path = args.library
    ITUNES_XML_PATH = os.path.expanduser(raw_path)
    
    if not os.path.exists(ITUNES_XML_PATH):
        print(f"Modifica lo script e inserisci il percorso corretto: {ITUNES_XML_PATH}")
    else:
        # Passa i parametri presi dal terminale alla funzione principale
        main(ITUNES_XML_PATH, args.tracks, args.saved)