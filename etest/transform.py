# -*- coding: utf-8 -*-

from xml.dom.minidom import parseString

from models import Course, Student, Test, Question, Answer

from django.http import HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.http import require_GET, require_POST

@require_GET
def get_xml(request):
    """ Outputs a course or a test in the XML format """

    if 'course_id' in request.GET:
        course_id = int(request.GET['course_id'])

        try:
            course = Course.objects.get(pk=course_id)
        except:
            return HttpResponse("Error: no course with such id: %i" % course_id)

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
            return HttpResponse("Error: no test with such id: %i" % test_id)

        test.questions = list(Question.objects.filter(test=test))

        for q in test.questions:
            q.answers = list(Answer.objects.filter(question=q))

        response = TemplateResponse(request, 'test-template.xml', {'test': test}, 'application/x-generated-xml-backup')

        response['Content-disposition'] = 'attachment; filename=test-' + str(test_id) + '.xml'

        return response
    
    return HttpResponse("error")

def parseXMLanswer(xmlanswer, question, position=0):

    correct_str = xmlanswer.getAttribute('correct')
    if correct_str == '1':
        correct = True
    else:
        correct = False
    body = xmlanswer.firstChild.nodeValue
    answer = Answer(body=body, position=position, question=question, is_correct=correct)
    answer.save()
    return answer

def parseXMLquestion(xmlquestion, test, position=0):
    qbody = xmlquestion.getAttribute('content')
    qtype = xmlquestion.getAttribute('type')
    questionType = None
    if qtype == '0':
        questionType = u'Один'
    elif qtype == '1':
        questionType = u'Несколько'
    elif qtype == '2':
        questionType = u'Свой'
    question = Question(qbody=qbody, position=position, test=test, qtype=questionType)
    question.save()
    return question

def parseXMLtest(xmltest, user, course=None, num=0):
    testName = xmltest.getAttribute('name')
    desc = xmltest.getAttribute('desc')
    anoq = int(xmltest.getAttribute('anoq'))
    test = Test(name=testName, position=num, description=desc, author=user, course=course, actualNumberOfQuestions=anoq,
                totalNumberOfQuestions=anoq)
    test.save()
    return test

def uploadfile(request, filename):
    """ Returns data from request file """
    try:
        datafile = request.FILES[filename]
        data = datafile.read(datafile.size)
    except:
        return None
    return data

@require_POST
def uploadxmltest(request):
    """ Uploads a test in the XML format and converts it into objects """

    result = ''
    error = ''

    data = uploadfile(request, 'test')
    if not data:
        return HttpResponse('no file data')

    if 'course' in request.POST:
        course_id = request.POST['course']
    else:
        course_id = 0
    try:
       c = parseString(data)
    except:
        error = 'XML parsing error'
        return HttpResponse(error)

    xmltest = c.getElementsByTagName("test")[0]

    test = parseXMLtest(xmltest, request.user)
    if not test:
        error = 'Test reading error'
        return HttpResponse(error)

    result = result + '<p>Got a test: name = %s, actual number of questions = %d, description = %s</p>' % (test.name, test.actualNumberOfQuestions, test.description)

    if course_id:
        course = Course.objects.get(pk = course_id)
    else:
        course = None

    if course:
        from django.db.models import Max
        test.course = course
        test.position = course.get_tests().aggregate(Max('position'))['position__max'] + 1
        result = result + '<p>The test is linked to an existing course: %s</p>' % (course.name)

    j = 0
    for xmlquestion in xmltest.childNodes:
        if xmlquestion.nodeType == xmlquestion.ELEMENT_NODE:
            question = parseXMLquestion(xmlquestion, test, j)
            result = result + '<p>Got a question: body = %s, type = %s</p>' % (question.qbody, question.qtype)
            j = j+1
            k = 0
            for xmlanswer in xmlquestion.childNodes:
                if xmlanswer.nodeName == 'answer':
                    answer = parseXMLanswer(xmlanswer, question, k)
                    result = result + '<p>Got an answer: body = %s, correct = %s</p>' % (answer.body, answer.is_correct)
                    k = k+1
    if test.actualNumberOfQuestions > j:
        result = result + '<p style="color: red">Количество вопросов скорректировано</p>'
        test.actualNumberOfQuestions = j
    else:
        test.totalNumberOfQuestions = j
    test.save()

    return TemplateResponse(request, 'upload.html', {'result': result})

@require_POST
def uploadxmlcourse(request):
    """ Uploads a course in the XML format and converts it into objects """

    result = ''
    error = ''

    data = uploadfile(request, 'course')
    if not data:
        return 

    try:
       c = parseString(data)
    except:
        error = 'XML parsing error 1'
        return HttpResponse(error)

    try:
       cname = c.getElementsByTagName("course")[0].attributes.item(0).value
    except:
        error = 'XML parsing error 2'
        return HttpResponse(error)

    course_obj = Course(name=cname, author=request.user)
    result = result + '<p>Got course: %s\n</p>' % cname
    course_obj.save()

    xmltests = c.getElementsByTagName("test")
    i = 0
    for xmltest in xmltests:
        test = parseXMLtest(xmltest, request.user, course_obj, i)
        result = result + '<p>Got a test: name = %s, actual number of questions = %d, description = %s</p>' % (test.name, test.actualNumberOfQuestions, test.description)
        i = i+1
        j = 0
        for xmlquestion in xmltest.childNodes:
            if xmlquestion.nodeType == xmlquestion.ELEMENT_NODE:
                question = parseXMLquestion(xmlquestion, test, j)
                result = result + '<p>Got a question: body = %s, type = %s</p>' % (question.qbody, question.qtype)
                j = j+1
                k = 0
                for xmlanswer in xmlquestion.childNodes:
                    if xmlanswer.nodeName == 'answer':
                        answer = parseXMLanswer(xmlanswer, question, k)
                        result = result + '<p>Got an answer: body = %s, correct = %s</p>' % (answer.body, answer.is_correct)
                        k = k+1
        if test.actualNumberOfQuestions > j:
            result = result + '<p style="color: red">Количество вопросов скорректировано</p>'
            test.actualNumberOfQuestions = j
        else:
            test.totalNumberOfQuestions = j
        test.save()

#    return HttpResponseRedirect('/admin')
    return TemplateResponse(request, 'upload.html', {'result': result})

# outdated!
def upload(request):
    
    import StringIO
    import json

    coursefile = request.FILES['course']
    data = coursefile.read(coursefile.size)
    buf = StringIO.StringIO(data)

    cname = str(buf.readline()).decode('utf8')[:-1]
    buf.readline()
    tests = []
    fstr = '\n'
    
    while (1):

        if fstr == '':
            break

        if fstr == '\n':

            fstr = str(buf.readline()).decode('utf-8')

            if fstr == 'test\n':
                tname = str(buf.readline()).decode('utf-8')[:-1]
            else:
                return HttpResponse('error: ' + fstr)
        else:
            tname = str(buf.readline()).decode('utf-8')[:-1]

        questions = []

        while (1):

            fstr = str(buf.readline()).decode('utf-8')

            if fstr != 'question\n':
                if fstr == 'test\n':
                    break
                elif fstr == '\n' or fstr == '':
                    break        
                else:    
                    return HttpResponse('question: ' + fstr)

            qtype = int(buf.readline())
            question = str(buf.readline()).decode('utf-8')[:-1]
            
            answers = []

            while (1):

                fstr = str(buf.readline()).decode('utf-8')

                if fstr == '\n':
                    break

                if fstr=='':
                    break

                if fstr[0] == '-':
                    answers.append({'body': fstr[1:-1], 'correct': False})
                elif fstr[0] == '+':
                    answers.append({'body': fstr[1:-1], 'correct': True})
                else:
                    answers.append({'body': fstr[:-1], 'correct': True})

            questions.append({'qbody': question, 'qtype': qtype, 'answers': answers})

            if fstr == '':
                break

        tests.append({'name': tname, 'questions': questions})

    course = {'course': cname, 'tests': tests}

#    kkd = json.dumps(course, indent=4, separators=(',', ': '))
#    return HttpResponse(kkd)

    course_obj = Course(name=course['course'], author=request.user)
    tests_obj = []
    questions_obj = []
    answers_obj = []
    i = 0

    course_obj.save()

    for test in course['tests']:
        i = i + 1
        test_obj = Test(name=test['name'], position=i, author=request.user, course=course_obj, actualNumberOfQuestions=len(test['questions']), totalNumberOfQuestions=len(test['questions']))
        test_obj.save()
        j = 0
        for question in test['questions']:
            j = j + 1
            if question['qtype'] == 0:
                qqq = u'Один'
            elif question['qtype'] == 1:
                qqq = u'Несколько'
            elif question['qtype'] == 2:
                qqq = u'Свой'
            else:
                return HttpResponse('error with qtype')

            question_obj = Question(qbody=question['qbody'], position=j, test=test_obj, qtype=qqq)
            question_obj.save()
            k = 0
            for answer in question['answers']:
                k= k + 1
                answer_obj = Answer(body=answer['body'], position=k, question=question_obj, is_correct=answer['correct'])
                answer_obj.save()

    return HttpResponse('ok')
