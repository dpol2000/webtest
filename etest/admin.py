from django import VERSION as django_version
from django.contrib import admin

from etest.models import Student, Course, Test, Question, Answer, TestLog, QuestionLog, AnswerLog

class TestInline(admin.TabularInline):
    model = Test


class CourseAdmin(admin.ModelAdmin):
    inlines = [TestInline]
    search_fields = ['name']
    list_display = ('name', 'XML')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['uploadlink'] = '/uploadcourse'
        extra_context['uploadfilename'] = 'course'
        extra_context['uploadtitle'] = 'Upload a new course'
        return super(CourseAdmin, self).changelist_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['uploadlink'] = '/uploadtest'
        extra_context['uploadfilename'] = 'test'
        extra_context['uploadtitle'] = 'Upload a new test'
        extra_context['uploadcourse'] = object_id

        if django_version[1] < 4:
            return super(CourseAdmin, self).change_view(request, object_id, extra_context=extra_context)
        else:
            return super(CourseAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)


class QuestionInline(admin.TabularInline):
    model = Question


class TestAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    change_form_template = 'admin/etest/change_test.html'
    list_display = ('name', 'XML')
    search_fields = ['name']

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['uploadlink'] = '/uploadtest'
        extra_context['uploadfilename'] = 'test'
        extra_context['uploadtitle'] = 'Upload a new test'
        return super(TestAdmin, self).changelist_view(request, extra_context=extra_context)


class AnswerInline(admin.TabularInline):
    model = Answer


class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    search_fields = ['qbody']

# Logs

class QuestionLogInline(admin.TabularInline):
    model = QuestionLog
    readonly_fields = ('question', 'result')


class TestLogAdmin(admin.ModelAdmin):
    inlines = [QuestionLogInline]
    list_display = ('student', 'test', 'time', 'result')
    readonly_fields = ['test', 'time', 'student', 'total_questions', 'correct_answers', 'result']
    list_filter = ['student', 'time']


class AnswerLogInline(admin.TabularInline):
    model = AnswerLog
    readonly_fields = ('answer',)


class QuestionLogAdmin(admin.ModelAdmin):
    inlines = [AnswerLogInline]
    readonly_fields = ('question', 'result', 'tlog')


class AnswerLogAdmin(admin.ModelAdmin):
    readonly_fields = ('answer', 'qlog')


admin.site.register(Student)
admin.site.register(Course, CourseAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Question, QuestionAdmin)
#admin.site.register(Answer)
admin.site.register(TestLog, TestLogAdmin)
#admin.site.register(QuestionLog, QuestionLogAdmin)
#admin.site.register(AnswerLog, AnswerLogAdmin)
