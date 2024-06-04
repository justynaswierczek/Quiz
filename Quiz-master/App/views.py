from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.http import Http404
from django.http import HttpResponseNotFound
from faunadb import query as q
from django.contrib import messages
import pytz
from faunadb.objects import Ref
from faunadb.client import FaunaClient
import hashlib
import datetime

client = FaunaClient(secret="fnAFfiGLTXAA0Bz_4ysTnY9dz1BoSBSclncNY4n9")
indexes = client.query(q.paginate(q.indexes()))



def register(request):
    if request.method == "POST":
        username = request.POST.get("username").strip().lower()
        email = request.POST.get("email").strip().lower()
        password = request.POST.get("password")

        try:
            user = client.query(q.get(q.match(q.index("users_index"), username)))
            messages.add_message(request, messages.INFO, 'User already exists with that username.')
            return redirect("App:register")
        except:
            user = client.query(q.create(q.collection("Users"), {
                "data": {
                    "username": username,
                    "email": email,
                    "password": hashlib.sha512(password.encode()).hexdigest(),
                    "date": datetime.datetime.now(pytz.UTC)
                }
            }))
            messages.add_message(request, messages.INFO, 'Registration successful.')
            return redirect("App:login")
    return render(request, "register.html")

def login(request):
    if request.method == "POST":
        username = request.POST.get("username").strip().lower()
        password = request.POST.get("password")

        try:
            user = client.query(q.get(q.match(q.index("users_index"), username)))
            if hashlib.sha512(password.encode()).hexdigest() == user["data"]["password"]:
                request.session["user"] = {
                    "id": user["ref"].id(),
                    "username": user["data"]["username"]
                }
                return redirect("App:dashboard")
            else:
                raise Exception()
        except:
            messages.add_message(request, messages.INFO,
                                 "You have supplied invalid login credentials, please try again!", "danger")
            return redirect("App:login")
    return render(request, "login.html")

def dashboard(request):
    if "user" in request.session:
        user = request.session["user"]["username"]
        context = {"user": user}
        return render(request, "dashboard.html", context)
    else:
        return HttpResponseNotFound("Page not found")

def create_quiz(request):
    if request.method == "POST":
        name = request.POST.get("quiz_name")
        description = request.POST.get("quiz_description")
        total_questions = request.POST.get("total_questions")
        try:
            quiz = client.query(q.get(q.match(q.index("quiz_index"), name)))
            messages.add_message(request, messages.INFO, 'A Quiz with that name already exists.')
            return redirect("App:create-quiz")
        except:
            quiz = client.query(q.create(q.collection("Quiz"), {
                "data": {
                    "status": "active",
                    "name": name,
                    "description": description,
                    "total_questions": total_questions,
                }
            }))
            messages.add_message(request, messages.INFO, 'Quiz Created Successfully.')
            return redirect("App:create-quiz")
    return render(request, "create_quiz.html")

def quiz(request):
    try:
        all_quiz = client.query(q.paginate(q.match(q.index("quiz_get_index"), "active")))["data"]
        quiz_count = len(all_quiz)
        page_number = int(request.GET.get('page', 1))
        quiz = client.query(q.get(q.ref(q.collection("Quiz"), all_quiz[page_number - 1].id())))["data"]
        context = {"count": quiz_count, "quiz": quiz, "next_page": min(quiz_count, page_number + 1),
                   "prev_page": max(1, page_number - 1)}
        return render(request, "quiz.html", context)
    except:
        return render(request, "quiz.html")

def create_question(request):
    quiz_all = client.query(q.paginate(q.match(q.index("quiz_get_index"), "active")))
    all_quiz = []
    for i in quiz_all["data"]:
        all_quiz.append(q.get(q.ref(q.collection("Quiz"), i.id())))
    context = {"quiz_all": client.query(all_quiz)}
    if request.method == "POST":
        quiz_name = request.POST.get("quiz_name")
        question_asked = request.POST.get("question")
        answer_1 = request.POST.get("answer_1")
        answer_2 = request.POST.get("answer_2")
        answer_3 = request.POST.get("answer_3")
        answer_4 = request.POST.get("answer_4")
        correct_answer = request.POST.get("correct_answer")
        try:
            question_create = client.query(q.get(q.match(q.index("question_index"), question_asked)))
            messages.add_message(request, messages.INFO, 'This question already exists')
            return redirect("App:create-question")
        except:
            question_create = client.query(q.create(q.collection("Question"), {
                "data": {
                    "quiz_name": quiz_name,
                    "question_asked": question_asked,
                    "answer_1": answer_1,
                    "answer_2": answer_2,
                    "answer_3": answer_3,
                    "answer_4": answer_4,
                    "correct_answer": correct_answer,
                }
            }))
            messages.add_message(request, messages.INFO, 'Question Created Successfully.')
            return redirect("App:create-question")
    return render(request, "create_questions.html", context)

def answer_quiz(request, slug):
    try:
        quiz = client.query(q.get(q.match(q.index("quiz_index"), slug)))["data"]
    except Exception as e:
        raise Http404("Quiz not found")

    try:
        questions_refs = client.query(q.paginate(q.match(q.index("questions_quiz_index"), quiz["name"])))["data"]
        questions = [client.query(q.get(ref))["data"] for ref in questions_refs]
    except Exception as e:
        questions = []

    paginator = Paginator(questions, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    question = page_obj.object_list[0] if page_obj.object_list else None

    if request.method == "POST":
        user_answer = request.POST.get("answer")
        question_asked = request.POST.get("question")

        if f"{quiz['name']}_answers" not in request.session:
            request.session[f"{quiz['name']}_answers"] = {}
        request.session[f"{quiz['name']}_answers"][question_asked] = user_answer
        request.session.modified = True

        next_page = page_obj.next_page_number() if page_obj.has_next() else None
        if next_page:
            return redirect(f"{request.path}?page={next_page}")
        else:
            return redirect("App:quiz_result", slug=slug)

    saved_answers = request.session.get(f"{quiz['name']}_answers", {})
    saved_answer = saved_answers.get(question['question_asked'], "") if question else ""

    return render(request, 'answer_quiz.html', {
        'page_obj': page_obj,
        'quiz': quiz,
        'question': question,
        'saved_answer': saved_answer
    })

def quiz_result(request, slug):
    try:
        quiz = client.query(q.get(q.match(q.index("quiz_index"), slug)))["data"]
        questions_refs = client.query(q.paginate(q.match(q.index("questions_quiz_index"), quiz["name"])))["data"]
        questions = [client.query(q.get(ref))["data"] for ref in questions_refs]
    except Exception as e:
        raise Http404("Quiz not found")

    saved_answers = request.session.get(f"{quiz['name']}_answers", {})
    score = 0

    for question in questions:
        correct_answer = question["correct_answer"]
        user_answer = saved_answers.get(question["question_asked"])
        if user_answer == correct_answer:
            score += 1

    request.session.pop(f"{quiz['name']}_answers", None)
    return render(request, 'quiz_result.html', {
        'quiz': quiz,
        'score': score,
        'total_questions': len(questions)
    })

