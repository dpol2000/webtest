# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField()),
                ('is_correct', models.BooleanField()),
                ('position', models.PositiveIntegerField(null=True)),
            ],
            options={
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='AnswerLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.ForeignKey(to='etest.Answer')),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('qbody', models.TextField()),
                ('qtype', models.CharField(max_length=30, choices=[('\u041e\u0434\u0438\u043d', '\u041e\u0434\u0438\u043d \u043f\u0440\u0430\u0432\u0438\u043b\u044c\u043d\u044b\u0439 \u043e\u0442\u0432\u0435\u0442'), ('\u041d\u0435\u0441\u043a\u043e\u043b\u044c\u043a\u043e', '\u041d\u0435\u0441\u043a\u043e\u043b\u044c\u043a\u043e \u043f\u0440\u0430\u0432\u0438\u043b\u044c\u043d\u044b\u0445 \u043e\u0442\u0432\u0435\u0442\u043e\u0432'), ('\u0421\u0432\u043e\u0439', b'\xd0\xa1\xd0\xb2\xd0\xbe\xd0\xb9 \xd0\xbe\xd1\x82\xd0\xb2\xd0\xb5\xd1\x82')])),
                ('image', models.ImageField(upload_to=b'images', blank=True)),
                ('position', models.PositiveIntegerField(null=True)),
            ],
            options={
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='QuestionLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result', models.BooleanField()),
                ('question', models.ForeignKey(to='etest.Question')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('croco', models.BooleanField(default=True)),
                ('facebook_id', models.BigIntegerField(null=True, blank=True)),
                ('photo', models.CharField(max_length=100, null=True, blank=True)),
                ('courses', models.ManyToManyField(to='etest.Course', null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
                ('position', models.PositiveIntegerField(null=True)),
                ('actualNumberOfQuestions', models.PositiveIntegerField(null=True)),
                ('totalNumberOfQuestions', models.PositiveIntegerField(null=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('course', models.ForeignKey(to='etest.Course', null=True)),
            ],
            options={
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='TestLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('total_questions', models.PositiveIntegerField()),
                ('correct_answers', models.PositiveIntegerField(null=True)),
                ('result', models.PositiveIntegerField(null=True)),
                ('student', models.ForeignKey(to='etest.Student')),
                ('test', models.ForeignKey(to='etest.Test')),
            ],
            options={
                'ordering': ['-time'],
            },
        ),
        migrations.AddField(
            model_name='questionlog',
            name='tlog',
            field=models.ForeignKey(to='etest.TestLog'),
        ),
        migrations.AddField(
            model_name='question',
            name='test',
            field=models.ForeignKey(to='etest.Test'),
        ),
        migrations.AddField(
            model_name='answerlog',
            name='qlog',
            field=models.ForeignKey(to='etest.QuestionLog'),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(to='etest.Question'),
        ),
    ]
