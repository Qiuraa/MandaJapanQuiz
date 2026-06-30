from django.urls import path

from . import views

urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "deck/<int:deck_id>/",
        views.deck_detail,
        name="deck_detail"
    ),

    path(
        "deck/<int:deck_id>/start/",
        views.start_quiz,
        name="start_quiz"
    ),

    path(
        "quiz/",
        views.quiz,
        name="quiz"
    ),

    path(
        "submit/",
        views.submit_answer,
        name="submit_answer"
    ),

    path(
        "feedback/",
        views.feedback,
        name="feedback"
    ),

    path(
        "next/",
        views.next_question,
        name="next_question"
    ),

    path(
        "result/",
        views.result,
        name="result"
    ),

]