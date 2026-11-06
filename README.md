# TasteSaver Backend API

> **Platforma zapobiegania marnowaniu żywności – API REST & Zarządzanie Spiżarnią**  
> **Autorzy projektu:**  
> - **Stanisław Gołębiewski** – Architektura backendu, API REST, autoryzacja JWT, baza danych, Docker  
> - **Kacper Kozłowski** ([@KacperK2003](https://github.com/KacperK2003)) – Aplikacja mobilna Android, skaner kodów kreskowych  
> **Przedmiot:** Inżynieria Oprogramowania / Aplikacje Mobilne, WAT (Grupa WCY22IJ3S1)  
> **Stos:** Python 3, Django, Django REST Framework, SimpleJWT, PostgreSQL / SQLite, Docker  

---

## 📌 O Projekcie

**TasteSaver** to zintegrowany ekosystem mobilno-serwerowy przeciwdziałający marnowaniu żywności w gospodarstwach domowych. System składa się z dwóch współpracujących komponentów:
1. **Backend API (niniejsze repozytorium):** Serwer REST odpowiedzialny za uwierzytelnianie użytkowników, katalog produktów po kodach EAN, synchronizację spiżarni i logikę terminów ważności.
2. **Aplikacja Mobilna Android:** Natywny klient smartfonowy z wbudowanym skanerem kodów kreskowych aparatem.  
   👉 [**Repozytorium Aplikacji Android (KacperK2003/TasteSaver)**](https://github.com/KacperK2003/TasteSaver)

---

## 👥 Podział Ról w Zespole

- **Stanisław Gołębiewski (Backend Lead):**
  - Projekt bazy danych: modele `Product`, `PantryPosition`, rozszerzony użytkownik `CustomUser`.
  - Implementacja API w Django REST Framework oraz bezpiecznej autoryzacji tokenowej **JWT** (SimpleJWT: logowanie, rejestracja, odświeżanie tokenów).
  - Skonteneryzowanie serwera i bazy danych przy użyciu **Dockera** (`docker-compose.yml`, `Dockerfile`).
  - Testy automatyczne API (`pytest`).
- **Kacper Kozłowski (Mobile Lead):**
  - Implementacja interfejsu aplikacji mobilnej Android (Material Design, RecyclerView).
  - Integracja biblioteki skanera kodów kreskowych **ZXing Embedded** z kamerą telefonu.
  - Klient sieciowy **Retrofit 2** do asynchronicznej komunikacji z backendem.

---

## 🛠️ Funkcjonalności API

- **Uwierzytelnianie JWT (`/api/token/`, `/api/token/refresh/`):** Bezpieczny dostęp z mechanizmem odświeżania tokenów.
- **Katalog Produktów (`/api/products/`):** Wyszukiwanie produktów po unikalnym kodzie kreskowym zintegrowanym ze skanerem aparatu w telefonie.
- **Wirtualna Spiżarnia (`/api/pantry/`):** Dodawanie, edycja i usuwanie produktów ze spiżarni użytkownika z powiadomieniami o zbliżającym się terminie przydatności.
- **Panel Administracyjny Django (`/admin/`):** Pełne zarządzanie bazą produktów i użytkowników z poziomu panelu webowego.

---

## 🚀 Uruchomienie

### Opcja A: Docker Compose (Zalecane)
```bash
docker-compose up -d --build
docker-compose exec web python manage.py migrate
```

### Opcja B: Uruchomienie Lokalne
```bash
# 1. Środowisko wirtualne
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 2. Instalacja zależności
pip install -r requirements.txt

# 3. Migracje i start
python manage.py migrate
python manage.py runserver
```

---

## 🧪 Testy
```bash
pytest
```
