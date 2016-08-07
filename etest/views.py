# -*- coding: utf-8 -*-

import datetime
import json
import socket

from django.db import models
from django.template.response import TemplateResponse
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView, View
from django.views.decorators.http import last_modified, require_GET, require_POST
from django.contrib.auth.mixins import LoginRequiredMixin


from models import Student, Test, Question, Answer, TestLog, QuestionLog, AnswerLog
from utils import normalize


class StudentStatsView(LoginRequiredMixin, DetailView):
    """ A particular test statistics view """
    context_object_name = 'student'
    queryset = Student.objects.all()
    template_name = 'etest/student_stats.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        context['courses'] = self.object.courses.all()
        return self.render_to_response(context)


def get_student_data(request):

    student_id = int(request.GET['id'])
    student = Student.objects.get(id=student_id)
    courses = []

    for course in student.courses.all():
        crs = {'course': course.name, 'tests': []}
        for test in course.test_set.all():
            tst = {
                'test': test.name,
                'avg': TestLog.objects.filter(test=test, student=student).aggregate(models.Avg('result'))['result__avg'],
                'count': TestLog.objects.filter(test=test, student=student).count()
            }
            crs['tests'].append(tst)

        courses.append(crs)

    return HttpResponse(json.dumps(courses))


class TestStatsView(LoginRequiredMixin, DetailView):
    """ A particular student statistics view """
    context_object_name = 'test'
    queryset = Test.objects.all()
    template_name = 'etest/test_stats.html'

    def get(self, request, *args, **kwargs):

        self.object = self.get_object()
        context = self.get_context_data()
        context['testlogs'] = TestLog.objects.filter(test=self.object)
        return self.render_to_response(context)

        
class StudentDetailView(LoginRequiredMixin, DetailView):
    context_object_name = 'student'
    queryset = Student.objects.all()


class TestLogDetailView(LoginRequiredMixin, DetailView):
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

        if socket.gethostname() == 'hrutr':
            local = True
        else:
            local = False

        if not local:
            if request.user.is_authenticated():
                if hasattr(request.user, 'student'):
                    if request.user.student:
                        return redirect(request.user.student) # HttpResponseRedirect('/students/' + str(request.user.student.id))

        return render(request, self.template_name, {'local': local})


class TestDetailView(LoginRequiredMixin, DetailView):
    
    """ A particular test view """
    
    context_object_name = 'test'
    queryset = Test.objects.all()


class TestLogList(LoginRequiredMixin, ListView):
    
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
                    t = Test.objects.get(pk=int(test['test']['id']))

                    # create and save test log
                    tlog = TestLog(test=t, student=Student.objects.get(user=request.user),
                                   total_questions=t.actualNumberOfQuestions, correct_answers=0)
                    tlog.save()

                except: 
                    pass
                else:
                    # create logs for answers and questions
                    true_answers = 0
                    questions = test['test']['questions']
                    for question in questions:
                        try:
                            q = Question.objects.get(pk=int(question['id']))
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

                                answers = [Answer.objects.get(pk=int(i)) for i in question['answers']]
                                          
                                all_correct = True

                                for answer in answers:
                                    if not answer.is_correct:
                                        all_correct = False
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
                    tlog.result = 100 * tlog.correct_answers / tlog.total_questions
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
    return redirect(student)

