# TasteSaver Backend API

> **Platforma zapobiegania marnowaniu żywności – API REST & Zarządzanie Spiżarnią**  
> **Autor:** Stanisław Gołębiewski  
> **Stos:** Python 3, Django, Django REST Framework, SimpleJWT, PostgreSQL / SQLite, Docker  

---

## 📌 O Projekcie

**TasteSaver Backend** to serwerowa warstwa ekosystemu mobilnego TasteSaver (antidotum na marnowanie żywności w gospodarstwach domowych). Udostępnia bezpieczne API REST do:
- Rejestracji i uwierzytelniania użytkowników za pomocą tokenów **JWT** (JSON Web Tokens).
- Katalogowania produktów spożywczych na podstawie globalnych kodów kreskowych (EAN / Barcode).
- Indywidualnego zarządzania pozycjami w spiżarni (**PantryPosition**): śledzenie ilości, dat ważności i statusu przydatności do spożycia.

Serwer współpracuje bezpośrednio z aplikacją mobilną na system Android (**TasteSaver Android App**).

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
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate

# 2. Instalacja zależności
pip install -r requirements.txt

# 3. Migracje i start
python manage.py migrate
python manage.py runserver
```

---

## 🧪 Testy
W projekcie zaimplementowano testy jednostkowe i integracyjne:
```bash
pytest
```
