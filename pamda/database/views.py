from math import ceil

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from database.models import (
    Deck,
    LearningSession,
)

from database.engine.stage_generator import StageGenerator
from database.engine.quiz_engine import QuizEngine
from database.engine.mastery_calculator import MasteryCalculator


def home(request):

    decks = Deck.objects.all()
    return render(request, "home.html", {"decks": decks, "user": request.user})


def language_choice(request):
    return render(request, "language_choice.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if username and password:
            if User.objects.filter(username=username).exists():
                return render(request, "register.html", {"error": "Username sudah dipakai."})
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect("home")
    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        return render(request, "login.html", {"error": "Username atau password salah."})
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect("home")


def deck_detail(request, deck_id):

    deck = get_object_or_404(
        Deck,
        id=deck_id
    )

    total_vocab = deck.vocabularies.count()

    total_stage = ceil(
        total_vocab / deck.stage_size
    )

    user_session = None
    if request.user.is_authenticated:
        user_session = LearningSession.objects.filter(
            user=request.user,
            deck=deck
        ).first()

    session = user_session

    progress_percent = 0

    if session:

        progress_percent = round(
            (
                session.current_stage
                /
                session.total_stage
            ) * 100
        )

    return render(

        request,

        "deck_detail.html",

        {

            "deck": deck,

            "session": session,

            "total_vocab": total_vocab,

            "total_stage": total_stage,

            "progress_percent": progress_percent

        }

    )

def start_quiz(request, deck_id):

    deck = get_object_or_404(
        Deck,
        id=deck_id
    )

    if request.method == "POST":
        mode = request.POST.get("mode", "choice")
        request.session["quiz_mode"] = mode

    generator = StageGenerator(deck, user=request.user if request.user.is_authenticated else None)

    result = generator.generate()
    session = result["session"]
    if request.user.is_authenticated:
        session.user = request.user
        session.save(update_fields=["user"])

    request.session["session_id"] = session.id

    return redirect("quiz")


def quiz(request):

    session_id = request.session.get(
        "session_id"
    )

    if session_id is None:

        return redirect("home")

    session = LearningSession.objects.get(
        id=session_id
    )

    quiz_mode = request.session.get("quiz_mode", "choice")

    engine = QuizEngine(session)

    question = engine.next_question()

    mastery = MasteryCalculator(session)
    progress = mastery.get_stage_progress()

    if question["status"] == "FINISHED":

        return redirect("result")

    if question["status"] == "NEXT_STAGE":

        request.session["stage_message"] = True

    return render(

        request,

        "quiz.html",

        {

            "question": question,

            "stage": session.current_stage,

            "total_stage": session.total_stage,
            "progress": progress,
            "can_next_stage": mastery.can_next_stage(),
            "quiz_mode": quiz_mode,

        }

    )


def submit_answer(request):

    if request.method != "POST":

        return redirect("quiz")

    session_id = request.session.get("session_id")

    if session_id is None:

        return redirect("home")

    session = LearningSession.objects.get(id=session_id)

    engine = QuizEngine(session)

    vocabulary_id = request.POST.get("vocabulary_id", "")
    selected_answer = request.POST.get("selected_answer", "")

    if not vocabulary_id or not selected_answer:

        request.session["feedback"] = {
            "status": "ERROR",
            "message": "Jawaban tidak diterima. Silakan coba lagi.",
        }

        return redirect("feedback")

    try:
        vocabulary_id = int(vocabulary_id)
    except (TypeError, ValueError):
        request.session["feedback"] = {
            "status": "ERROR",
            "message": "ID kata tidak valid.",
        }
        return redirect("feedback")

    quiz_mode = request.session.get("quiz_mode", "choice")

    result = engine.submit_answer(
        vocabulary_id,
        selected_answer,
        quiz_mode=quiz_mode,
    )

    mastery = MasteryCalculator(session)
    progress = mastery.get_stage_progress()
    result.update(progress)
    result["can_next_stage"] = mastery.can_next_stage()

    request.session["feedback"] = result

    return redirect("feedback")


def feedback(request):

    feedback = request.session.get(
        "feedback"
    )

    if feedback is None:

        return redirect("quiz")

    return render(

        request,

        "feedback.html",

        {

            "feedback": feedback

        }

    )


def next_question(request):

    request.session.pop("feedback", None)

    return redirect("quiz")


def result(request):

    session = LearningSession.objects.get(
        id=request.session["session_id"]
    )

    mastery = MasteryCalculator(session)

    progress = mastery.get_stage_progress()

    return render(

        request,

        "result.html",

        {

            "stage": session.current_stage,

            "total_stage": session.total_stage,

            "mastered": progress["mastered"],

            "total": progress["total"],

            "rate": progress["rate"]

            ,"deck_id": session.deck.id

        }

    )

