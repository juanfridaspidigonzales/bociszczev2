# Discord Bot z obsługą AI
Projekt bota Discord z wykorzystaniem AI do generowania treningów zaklęć na serwerze RolePlay hapel.pl oraz zarządzania profilami postaci.

## Funkcjonalności
- Tworzenie i zarządzanie profilami postaci.
- Generowanie opisów treningów zaklęć za pomocą AI.
- Wyświetlanie profilu postaci z zaklęciami i ich treningami.

## Wymagania
- Python 3.8+
- Discord API Token
- Klucz API Gemini

## Struktura projektu
bot.py - Główna logika bota.
db.py - Obsługa bazy danych SQLite.
query.py - Integracja z modelem AI.

## Instalacja
1.Zainstaluj wymagane biblioteki:
pip install -r requirements.txt

2.Utwórz plik .env i dodaj swoje klucze API:
DISCORD_BOT_TOKEN=twoj_token
GEMINI_API_KEY=twoj_klucz_api

3. Uruchom main.py
   
## Przykładowy plik .env z kluczami środowiskowymi:
DISCORD_BOT_TOKEN=your_discord_token
GEMINI_API_KEY=your_api_key
