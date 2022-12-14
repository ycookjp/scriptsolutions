# -*- config: utf8 -*-
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from .models import Question, Choice

# Create your views here.

#def index(request):
#    latest_question_list = Question.objects.order_by('-pub_date')[:5]
#    context = {
#        'latest_question_list': latest_question_list
#    }
#    return render(request, 'polls/index.html', context)
class IndexView(generic.ListView):
    '''質問の一覧を表示する汎用ビュー。
    '''
    template_name = 'polls/index.html'
    '''質問一覧表示テンプレートのパス。'''
    context_object_name = 'latest_question_list'
    '''コンテキストのオブジェクト名。
    テンプレートで使用する変数名。テンプレートからこの変数名で質問の一覧を
    参照する。
    '''

    def get_queryset(self):
        '''Return the latest five published questions.
        Return the last five published questions (not including those set to be
        published in the future).
        '''
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]

#def detail(request, question_id):
#    question = get_object_or_404(Question, pk=question_id)
#    context = {'question': question}
#    return render(request, 'polls/detail.html', context)
class DetailView(generic.DetailView):
    '''詳細画面の汎用ビュー。
    
    質問に対する回答の選択画面を表示する。
    
    '''
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        '''
        Excludes any questions that aren\'t published yet.
        '''
        return Question.objects.filter(pub_date__lte=timezone.now())

#def results(request, question_id):
#    question = get_object_or_404(Question, pk=question_id)
#    return render(request, 'polls/results.html', {'question': question})
class ResultsView(generic.DetailView):
    '''回答結果画面の汎用ビュー。
    
    質問に対する回答のリストを表示し、それぞれの回答に対する投票数を表示する。
    
    '''
    model = Question
    template_name = 'polls/results.html'

def vote(request, question_id):
    '''回答の選択結果を処理するビュー関数。
    
    選択された回答の投票数を１つ増やして、その結果をChoiseモデルに保存する。
    その後、回答結果画面を表示する。
    
    例外処理
    * リクエストで受け取った question_id が存在しない場合は 404 エラーを表示
      する。
    * リクエストで送信された回答が未設定のものだった場合は、詳細画面を表示
      してエラーメッセージを表示する。
    
    '''
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
        
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'You did\'nt select a choice.',
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing with
        # POST data. This prevents data from being posted twice if a user
        # hits Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
