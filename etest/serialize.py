# -*- coding: utf-8 -*-

from models import Course, Student, Test, Question, Answer

from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt


def get_xml(request):

    if 'course_id' in request.GET:
        course_id = int(request.GET['course_id'])

        course = Course.objects.get(pk=course_id)

        course.tests = list(Test.objects.filter(course=course))

        for test in course.tests: 
            test.questions = list(Question.objects.filter(test=test))
            for q in test.questions:
                q.answers = list(Answer.objects.filter(question=q))

        response = TemplateResponse(request, 'course-template.xml', { 'course': course }, 'application/x-generated-xml-backup')

        response['Content-disposition'] = 'attachment; filename=' + course.name + '.xml'

        return response

    elif 'test_id' in request.GET:
        test_id = int(request.GET['test_id'])

        try:
            test = Test.objects.get(pk=test_id)
        except:
            return HttpResponse("error 1")

        test.questions = list(Question.objects.filter(test=test))

        for q in test.questions:
            q.answers = list(Answer.objects.filter(question=q))

        response = TemplateResponse(request, 'test-template.xml', { 'test': test }, 'application/x-generated-xml-backup')
        response['Content-disposition'] = 'attachment; filename=test-' + str(test_id) + '.xml'

        return response

    return HttpResponse("error")


@csrf_exempt
def serialize_ajax(request):

    if request.is_ajax() and request.method == 'GET':

#        if 'id' in request.GET:
#            course_id = int(request.GET['id'])

        courses = Course.objects.all()
        try:
            course = courses[0]
        except:
            return HttpResponse('exception')
#        if courses:
            #course = courses[0]
#            return HttpResponse('error in id')
#            data = serializers.serialize("xml", course)

        return HttpResponse('ok')

    return HttpResponse('error')


def serializecourse(request):

    if 'course' in request.POST:
        course_id = request.POST['course']
        data = serializers.serialize("xml", Course.objects.get(id=course_id))
        return HttpResponse('ok')
    else:
        return HttpResponse('error')


def serializetest(request):

    if 'test' in request.POST:
        test_id = request.POST['test']
        data = serializers.serialize("xml", Course.objects.get(id=test_id))
        return HttpResponse(data)
    else:
        return HttpResponse('error')
