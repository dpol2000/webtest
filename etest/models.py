# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.html import format_html

QUESTION_TYPE = ((u'Один', u'Один правильный ответ'), (u'Несколько', u'Несколько правильных ответов'), (u'Свой', 'Свой ответ'))


class Student(models.Model):
    
    courses = models.ManyToManyField('Course', null=True)
    croco = models.BooleanField(default=True)
    facebook_id = models.BigIntegerField(null=True, blank=True)
    user = models.OneToOneField(User)
    photo = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self): 
        return self.user.get_full_name()

    def get_absolute_url(self):
        return '/students/%i' % self.id
    
    def get_courses_and_testlogs(self):

        ctl = []

        for course in self.courses.all():
            tat = []    
            for test in course.test_set.all():
                tat.append({'test': test, 
                    'testlogs': test.get_testlogs_by_student(self), 
                    'best_result': TestLog.objects.filter(test=test, student=self).aggregate(models.Max('result'))['result__max'],
                    'mean_result': TestLog.objects.filter(test=test, student=self).aggregate(models.Avg('result'))['result__avg'],
                    'last_result': test.get_last_result_by_student(self),
                })
            
            ctl.append({'course': course, 'tests_and_testlogs': tat})

        return ctl


class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    author = models.ForeignKey(User)

    def __unicode__(self):  
        return self.name

    def XML(self):
        return format_html('<a href="/get_xml?course_id=%s">Сохранить XML</a>' % self.id)

    XML.allow_tags = True


class Test(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    author = models.ForeignKey(User)
    course = models.ForeignKey(Course, null=True)
    position = models.PositiveIntegerField(null=True)
    actualNumberOfQuestions = models.PositiveIntegerField(null=True)
    totalNumberOfQuestions = models.PositiveIntegerField(null=True)

    class Meta:
        ordering = ['position']

    def __unicode__(self): 
        return self.name

    def XML(self):
        return format_html('<a href="/get_xml?test_id=%s">Сохранить XML</a>' % self.id)

    XML.allow_tags = True

    def get_questions(self):
        return Question.objects.filter(test=self).order_by('?')

    def get_actual_questions(self):
        questions = Question.objects.filter(test=self).order_by('?')
        qq = questions[0:self.actualNumberOfQuestions]

        answers = Answer.objects.filter(question__id__in=[q.id for q in qq]).order_by('?').values()
        for q in qq:
            q.answers = [answer for answer in answers if answer['question_id'] == q.id]

        return qq

    def get_testlogs(self):
        return TestLog.objects.filter(test=self)

    def get_testlogs_by_student(self, student):
        return list(TestLog.objects.filter(test=self, student=student))

#    def get_best_result_by_student(self, student):
#        return TestLog.objects.filter(test=self, student = student).aggregate(models.Max('result'))['result__max']

#    def get_mean_result_by_student(self, student):
#        return TestLog.objects.filter(test=self, student = student).aggregate(models.Avg('result'))['result__avg']

    def get_last_result_by_student(self, student):

        testlogs = TestLog.objects.filter(test=self, student=student).order_by('-time')

        if testlogs:
            return testlogs[0].result
        else:
            return None


class Question(models.Model):
    qbody = models.TextField()
    test = models.ForeignKey(Test)
    qtype = models.CharField(max_length=30, choices=QUESTION_TYPE)
    image = models.ImageField(blank=True, upload_to='images')
    position = models.PositiveIntegerField(null=True)

    def __unicode__(self): 
        return self.qbody

    class Meta:
        ordering = ['position']

    def get_answers(self):
        return list(Answer.objects.filter(question=self).order_by('?').values())
#        kkd = Answer.objects.raw("SELECT id, body, question_id FROM etest_answer WHERE question_id=%s ORDER BY RANDOM()", [self.id])
    
#        cursor = connection.cursor()
#        cursor.execute("SELECT id, body, question_id FROM etest_answer WHERE question_id=%s ORDER BY RANDOM()", [self.id])
#        res = list(cursor.fetchall())
#        return res


class Answer(models.Model):
    body = models.TextField()
    is_correct = models.BooleanField()
    question = models.ForeignKey(Question)
    position = models.PositiveIntegerField(null=True)

    def __unicode__(self):
        return self.body

    class Meta:
        ordering = ['position']


class TestLog(models.Model):
    test = models.ForeignKey(Test)
    time = models.DateTimeField(auto_now_add=True, db_index=True)
    student = models.ForeignKey(Student)
    total_questions = models.PositiveIntegerField()
    correct_answers = models.PositiveIntegerField(null=True)
    result = models.PositiveIntegerField(null=True)

    def __unicode__(self): 
        return self.test.name + ' - ' + self.student.user.get_full_name()

    class Meta:
        ordering = ['-time']

    def get_qlogs(self):
        return list(QuestionLog.objects.filter(tlog=self))


class QuestionLog(models.Model):
    question = models.ForeignKey(Question)
    tlog = models.ForeignKey(TestLog)
    result = models.BooleanField()

    def __unicode__(self):  
        return self.question.qbody

    def get_alogs(self):
        return list(AnswerLog.objects.filter(qlog=self))

    def get_alog_answers(self):
        return [alog.answer.id for alog in AnswerLog.objects.filter(qlog=self)]
#        return AnswerLog.objects.filter(qlog=self)


class AnswerLog(models.Model):
    answer = models.ForeignKey(Answer)
    qlog = models.ForeignKey(QuestionLog)

    def __unicode__(self): 
        return self.answer.body