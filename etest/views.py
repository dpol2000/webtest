# -*- coding: utf-8 -*-

import datetime
import json
import socket

from django.db import models
from django.template.response import TemplateResponse
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django import VERSION as django_version
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView, View
from django.views.decorators.http import last_modified, require_GET, require_POST

from models import Student, Test, Question, Answer, TestLog, QuestionLog, AnswerLog

class StudentStatsView(DetailView):
    """ A particular test statistics view """
    context_object_name = 'student'
    queryset = Student.objects.all()
    template_name = 'etest/student_stats.html'

    def get(self, request, *args, **kwargs):

        self.object = self.get_object()
        context = self.get_context_data()
        context['courses'] = self.object.courses.all()
        return self.render_to_response(context)


@csrf_exempt
def getstudentdata(request):

    id = int(request.GET['id'])
    student = Student.objects.get(id=id)
    courses = []

    for course in student.courses.all():
        crs = {'course': course.name, 'tests': []}
        for test in course.test_set.all():
            tst = {'test': test.name,
                   'avg': TestLog.objects.filter(test=test, student=student).aggregate(models.Avg('result'))['result__avg'],
                   'count': TestLog.objects.filter(test=test, student=student).count()}
            crs['tests'].append(tst)

        courses.append(crs)

    return HttpResponse(json.dumps(courses))


class TestStatsView(DetailView):
    """ A particular student statistics view """
    context_object_name = 'test'
    queryset = Test.objects.all()
    template_name = 'etest/test_stats.html'

    def get(self, request, *args, **kwargs):

        self.object = self.get_object()
        context = self.get_context_data()
        context['testlogs'] = TestLog.objects.filter(test=self.object)
        return self.render_to_response(context)

        
class StudentDetailView(DetailView):
    context_object_name = 'student'
    queryset = Student.objects.all()

class TestLogDetailView(DetailView):
    context_object_name = 'testlog'
    queryset = TestLog.objects.all()

class IndexView(View):
    """ The index view """
    
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        """ 
        If user is logged in, take him to his personal page,
        to index otherwise
        """

        if (socket.gethostbyname(socket.gethostname()) == '127.0.1.1'):
            local = True
        else:
            local = False

        if not local:
            if request.user.is_authenticated():
                if hasattr(request.user, 'student'):
                    if request.user.student:
                        return redirect(request.user.student) # HttpResponseRedirect('/students/' + str(request.user.student.id))

        return render(request, self.template_name, {'local': local})


class TestDetailView(DetailView):
    
    """ A particular test view """
    
    context_object_name = 'test'
    queryset = Test.objects.all()

class TestLogList(ListView):
    
    """ List of testlogs, for admin """
    
    model = TestLog
    context_object_name = 'testlogs'

    def get_last_testlog(self, latest_entry):
        testlogs = TestLog.objects.all()
        if testlogs:
            return testlogs[0].time
        return None

    def dispatch(self, request, *args, **kwargs):
        """ Cache lists of tests """
        
        @last_modified(self.get_last_testlog)
        def _dispatch(request, *args, **kwargs):
            return super(TestLogList, self).dispatch(request, *args, **kwargs)
        return _dispatch(request, *args, **kwargs)

@require_GET
def logout(request):
    """ Logs the user out """
    if request.user.is_authenticated():
        auth.logout(request)
    return HttpResponseRedirect('/')


def normalize(string):
    """ Deletes spaces and uppercases the string """
    if string[-1] == '.':
        string2 = string[:-1]
    else:
        string2 = string
    return string2.replace(" ", "").upper()

@csrf_exempt
def getdata(request):

    test = Test.objects.get(id=23)
    testlogs = TestLog.objects.filter(test=test)

    results = [testlog.result for testlog in testlogs if testlog.result != None]

    return HttpResponse(results)

@csrf_exempt
def check_ajax(request):
    """ Check the test, ajax version """

    if request.is_ajax() and request.method == 'POST':

        # read test info from POST
        test = request.POST.get('test')
        if test:
            # convert from JSON
            test = json.loads(test)
            if test:
                try:
                    
                    # find test object
                    t = Test.objects.get(pk = int(test['test']['id']))

                    # create and save test log
                    tlog = TestLog(test=t, student=Student.objects.get(user=request.user), total_questions = t.actualNumberOfQuestions, correct_answers = 0)
                    tlog.save()

                except: 
                    pass
                else:
                    # create logs for answers and questions
                    true_answers = 0
                    questions = test['test']['questions']
                    for question in questions:
                        try:
                            q = Question.objects.get(pk = int(question['id']))
                        except: 
                            pass
                        else:
                            qlog = QuestionLog(question=q, tlog=tlog, result=False)
                            qlog.save()

                            if q.qtype == u'Один':

                                answer = Answer.objects.get(pk=int(question['answers'][0]))
                                alog = AnswerLog(qlog=qlog, answer=answer)
                                alog.save()
                                if answer.is_correct:
                                    qlog.result = True                
                                    true_answers = true_answers + 1

                            elif q.qtype == u'Несколько':

                                answers = [Answer.objects.get(pk = int(i)) for i in question['answers']]
                                          
                                all_correct = True

                                for answer in answers:
                                    if not answer.is_correct:
                                        all_correct  = False
                                    alog = AnswerLog(qlog=qlog, answer=answer)
                                    alog.save()
 
                                correct_answers = Answer.objects.filter(question=q, is_correct=True)
                             
                                if all_correct and len(answers) == correct_answers.count():
                                    qlog.result = True
                                    true_answers = true_answers + 1


                            elif q.qtype == u'Свой':
                                ans = Answer.objects.filter(question=q, is_correct=True)

                                new_answer = None
                                for an in ans:
                                    if normalize(an.body) == normalize(question['answers'][0]):
                                        new_answer = an
                                        break

                                if new_answer is None:
                                    new_answer = Answer(body=question['answers'][0], question=q, is_correct=False)
                                    new_answer.save()
                    
                                alog = AnswerLog(qlog=qlog, answer=new_answer)
                                alog.save()
                                if new_answer.is_correct:
                                    qlog.result = True                
                                    true_answers = true_answers + 1

                            if qlog:
                                qlog.save()

                    tlog.correct_answers = true_answers
                    tlog.result = 100* tlog.correct_answers / tlog.total_questions
                    tlog.save()

                    return HttpResponse(str(tlog.id))
            else:
                return HttpResponse('Error: cannot convert test info from JSON')
        else:
            return HttpResponse('Error: cannot find test info in POST')
    return HttpResponse('Error: not ajax call or not POST method')


@require_GET
def lts(request):
    """ Test user login """

    username = 'test-student'
    password = '123'

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create_user(username, '', password)
        user.first_name = 'Test'
        user.last_name = 'Student'
        student = Student()
        student.user = user
        user.save()
        student.save()
    else:
        student = Student.objects.get(user=user.id)

    student.facebook_id = '123'
    student.save()

    user = auth.authenticate(username=username, password=password)
    auth.login(request, user)

    return redirect(student) # HttpResponseRedirect('/students/' + str(student.id))

@csrf_exempt
def croco(request):
    """ Delete the croco """
    if request.is_ajax() and request.method == 'POST' and request.user.is_authenticated():
        student = request.user.student
        if student:
            student.croco = False
            student.save()
    return HttpResponse('ok')

@require_POST
def check(request):
    """ Check the test. Old version, not in use now """
    if request.POST:
        if request.method == 'POST':
            if 'test_id' in request.POST:
                test_id = int(request.POST['test_id'])
                if test_id:
                    test = Test.objects.get(pk=test_id)
                    qlogs = []
                    alogs = []
                    true_answers = 0
                    questions = Question.objects.filter(test=test)

                    tlog = TestLog(test=test, student=Student.objects.get(user=request.user), total_questions = test.actualNumberOfQuestions, correct_answers = 0)
                    tlog.save()

                    qlog = None
                    for question in questions:

                        if 'question-'+str(question.id) in request.POST:

                            qlog = QuestionLog(question=question, tlog=tlog, result=False)
                            qlog.save()

                            if question.qtype == u'Один':

                                answer_id = int(request.POST['question-'+str(question.id)])
                                answer = Answer.objects.get(pk=answer_id)
                                alog = AnswerLog(qlog=qlog, answer=answer)
                                alog.save()
    
                                alogs.append(alog)
                                if answer.is_correct:
                                    qlog.result = True                
                                    true_answers = true_answers + 1

            
                            elif question.qtype == u'Несколько':

                                answers_id_list = request.POST.getlist('question-'+str(question.id), -1)
                                answers = [Answer.objects.get(pk=x) for x in answers_id_list]
                                          
                                true_flag = True
                                count = 0 

                                for answer in answers:
                                    if answer.is_correct == False:
                                        true_flag = False
                                    alog = AnswerLog(qlog=qlog, answer=answer)
                                    alog.save()
                                    alogs.append(alog)
                                    count = count + 1
 
                                correct_answers = Answer.objects.filter(question=question, is_correct=True)
                             
                                if true_flag and count == correct_answers.count():
                                    qlog.result = True
                                    true_answers = true_answers + 1


                            elif question.qtype == u'Свой':
                                ans = Answer.objects.filter(question=question, is_correct=True)
                                answer = ans[0]

                                if answer.body == request.POST['question-'+str(question.id)]:
                                    new_answer = answer
                                else:
                                    new_answer = Answer(body=request.POST['question-' + str(question.id)], question = question, is_correct = False)
                                    new_answer.save()
                    
                                alog = AnswerLog(qlog=qlog, answer=new_answer)
                                alog.save()
                                alogs.append(alog)
                                if new_answer.is_correct:
                                    qlog.result = True                
                                    true_answers = true_answers + 1

                        if qlog:
                            qlog.save()
                            qlogs.append(qlog)
            
                        tlog.correct_answers = true_answers
                        tlog.total_questions = test.actualNumberOfQuestions #Question.objects.filter(test=test).count()
                        tlog.result = 100* tlog.correct_answers / tlog.total_questions
                        tlog.save()

    return HttpResponseRedirect('students/results/' + str(tlog.id))
