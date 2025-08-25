# LittleLemon

A full-featured restaurant application with a Django REST API backend and a Next.js frontend.

## Tech Stack

- **Backend:** Django 5, Django REST Framework, JWT (Simple JWT), Djoser  
- **Frontend:** Next.js (TypeScript)  
- **Database:** SQLite by default (can be replaced)  

## Project Structure

```text
apps/               – business logic (accounts, cart, menu, orders, etc.)
littlelemon/        – Django project configuration
littlelemon-next/   – frontend built with Next.js
requirements.txt    – backend dependencies
manage.py           – Django entry point
Getting Started
1. Backend (Django)
Install Python 3.10+
```
Create a .env file in the project root and add:

```ini
SECRET_KEY=<your secret>
DEBUG=True
ALLOWED_HOSTS=localhost 127.0.0.1
Install dependencies and run migrations:
```
```bash
pip install -r requirements.txt
python manage.py migrate
(Optional) create a superuser:
```
```bash
python manage.py createsuperuser
```
Start the development server:
```bash
python manage.py runserver
```
2. Frontend (Next.js)
Install Node.js 18+

Install dependencies and run the dev server:

```bash
cd littlelemon-next
npm install
npm run dev
```
Open http://localhost:3000 in your browser.

Running Tests
```bash
python manage.py test        # backend tests
```
# frontend tests depend on your chosen framework (e.g., Jest)
License
Open license of your choice (specify if needed).

```arduino
Feel free to adapt this text for the repository’s `README.md`.
```