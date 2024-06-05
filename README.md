# 📚 Quikz

A web-based quiz application built with Django and FaunaDB. Users can register, login, create quizzes, answer questions, and view their results.

## 🚀 Features

- 🔐 User Registration and Authentication
- 📝 Create and Manage Quizzes
- ❓ Add Questions to Quizzes
- 📊 View Quiz Results
- 🔄 Pagination for Quizzes

## 🛠️ Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/quiz-app.git
    cd quiz-app
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up FaunaDB:**
    - Create a FaunaDB account and a database.
    - Get the secret key for your database and update the `FAUNA_SECRET` variable in your Django settings.

5. **Apply the migrations:**
    ```bash
    python manage.py migrate
    ```

6. **Run the development server:**
    ```bash
    python manage.py runserver
    ```

## 📷 Screenshots

![Zrzut ekranu 2024-06-04 223812](https://github.com/justynaswierczek/Quiz/assets/105491587/e1875d5a-e1ae-4487-99b5-f9d22718be97)




