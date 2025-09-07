1. **Clone the repository**
2. Create a virtual environment & activate
```python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```
```3. Install dependencies
pip install -r requirements.txt
```
```4.Apply migrations
python manage.py migrate
```
```5.Create a superuser (admin)
python manage.py createsuperuser
```
```6.python manage.py runserver

Open http://127.0.0.1:8000 in your browser.
