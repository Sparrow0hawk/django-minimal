from __future__ import annotations
import json
from dataclasses import dataclass, asdict

import inject
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from polls.domain.questions import Question, QuestionRepository


def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("<h1>Hello world!</h1>")


@dataclass
class QuestionRepr:
    id: int
    question_text: str

    def to_domain(self) -> Question:
        return Question(id_=self.id, question_text=self.question_text)


@csrf_exempt
@inject.autoparams("questions_repository")
def add_questions(request: HttpRequest, questions_repository: QuestionRepository) -> HttpResponse:
    if request.method == "POST":
        payload = json.loads(request.body)
        questions_repr = [QuestionRepr(**element) for element in payload]
        questions_repository.add(*[question_repr.to_domain() for question_repr in questions_repr])
        return HttpResponse(status=201)
    else:
        return HttpResponse(status=405)


@dataclass(frozen=True)
class QuestionDetailContext:
    question_text: str

    @classmethod
    def from_domain(cls, question: Question) -> QuestionDetailContext:
        return cls(question_text=question.question_text)


@inject.autoparams("question_repository")
def question_details(request: HttpRequest, question_id: int, question_repository: QuestionRepository) -> HttpResponse:
    question = question_repository.get(question_id)
    assert question

    context = QuestionDetailContext.from_domain(question)
    return render(request, "polls/details.html", asdict(context))
