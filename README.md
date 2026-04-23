# 🎵 iTunes Random Picker

Estrai un album casuale dalla tua libreria di iTunes/Musica e visualizza la copertina direttamente nel terminale iTerm2.

## 🚀 Requisiti
- **[iTerm2](https://iterm2.com)** (per la visualizzazione delle immagini).
- **Python 3.6+**.
- `mutagen` (opzionale): `pip install mutagen`.
- vedere `requirements.txt` file.

## 📂 Configurazione
- Assicurati che il percorso del tuo file XML sia corretto nello script:
```
ITUNES_XML_PATH = os.path.expanduser("~/Music/Libreria.xml")`
```
- Rendi eseguibile
```
chmod +x ./RandomMusic.py
```
- Installare dipendendenze
```
pip install -r requirements.txt
```


## ⌨️ Utilizzo
Puoi usare i parametri per filtrare la selezione:

- **Estrai un album qualsiasi:**
```bash
./RandomMusic.py
```
- **Estrai solo album "veri" (minimo 8 tracce):**
```
./RandomMusic.py -t 8
```
- **Estrai album di cui hai salvato almeno 3 tracce:**
```
./RandomMusic.py -s 3
```
- **Estrai album con almeno 5 preferiti:**
```
./RandomMusic.py -f 5  
```
- **Estrai album interi di cui possiedi la collezione completa:**
```
./RandomMusic.py -t 10 -s 10
```

## 🎶 Come esportare libreria iTunes/Musica

```
File -> Libreria -> Esporta Libreria
```
