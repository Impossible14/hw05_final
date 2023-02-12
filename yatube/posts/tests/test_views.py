import shutil
import tempfile

from django.conf import settings
from django import forms
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core.cache import cache
from mixer.backend.django import mixer

from ..constants import MAX_POSTS
from ..models import Group, Post, Follow, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='gif',
            content=gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create(username='auth')
        group = mixer.blend(Group)
        cls.group = group
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
            image=cls.uploaded,
        )
        cls.pages_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug':
                    cls.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username':
                    cls.user}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id':
                    cls.post.id}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id':
                    cls.post.id}): 'posts/create_post.html',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.anon = Client()
        self.auth = Client()
        self.auth.force_login(self.user)
        cache.clear()

    def test_view_uses_correct_template(self):
        """View функции использует соответствующий шаблон."""
        for reverse_name, template in self.pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check(self, context):
        self.assertEqual(context.id, self.post.id)
        self.assertEqual(context.text, self.post.text)
        self.assertEqual(context.group, self.post.group)
        self.assertEqual(context.author, self.post.author)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        img = Post.objects.first().image
        response = self.auth.get(reverse('posts:index'))
        self.check(response.context['page_obj'][0])
        self.assertEqual(img, 'posts/gif')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        img = Post.objects.first().image
        response = self.auth.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        self.check(response.context['page_obj'][0])
        self.assertEqual(img, 'posts/gif')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        img = Post.objects.first().image
        response = self.auth.get(reverse(
            'posts:profile', kwargs={'username': self.user}))
        self.check(response.context['page_obj'][0])
        self.assertEqual(img, 'posts/gif')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        img = Post.objects.first().image
        response = self.auth.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context['post'].text, self.post.text)
        self.assertEqual(response.context['post'].author, self.post.author)
        self.assertEqual(img, 'posts/gif')

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.auth.get(reverse(
            'posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.auth.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PostPaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        group = mixer.blend(Group)
        cls.group = group
        posts = [Post(text=f'Тестовый пост{i}',
                      author=cls.user,
                      group=cls.group,)
                 for i in range(13)]
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.auth = Client()
        self.auth.force_login(self.user)

    def test_paginator(self):
        """Количества постов на одной странице 10."""
        list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug
            }),
            reverse('posts:profile', kwargs={
                'username': self.user.username
            }),
        ]

        for reverse_name in list:
            response = self.auth.get(reverse_name)
            self.assertEqual(len(response.context['page_obj']), MAX_POSTS)


class PostCacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='gif',
            content=gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='user')
        group = mixer.blend(Group)
        cls.group = group
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
            image=cls.uploaded,
        )

    def setUp(self):
        self.anon = Client()
        cache.clear()

    def test_index_cache(self):
        """проверка кэша на index"""
        response = self.anon.get(reverse('posts:index'))
        self.assertContains(response, 'Тестовый пост')
        Post.objects.all().delete()
        self.assertNotEqual(response, 'Тестовый пост')
        cache.clear()
        self.assertNotEqual(response, 'Тестовый пост')


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.fol = User.objects.create(username='fol')
        cls.unfol = User.objects.create(username='unfol')
        group = mixer.blend(Group)
        cls.group = group
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.unfol
        )

    def setUp(self):
        self.guest_client = Client()
        self.follower = Client()
        self.follower.force_login(self.fol)
        self.unfollower = Client()
        self.unfollower.force_login(self.unfol)
        cache.clear()

    def test_follow(self):
        """Тест работы подписки на автора."""
        self.unfollower.get(reverse(
            'posts:profile_follow', args=[self.user.username]))
        follow = Follow.objects.filter(
            user=self.unfol, author=self.user).exists()
        self.assertTrue(follow, 'Подписка не работает')

    def test_unfollow(self):
        """Тест работы отписки от автора."""
        Follow.objects.create(user=self.fol, author=self.user)
        follow = Follow.objects.filter(
            user=self.unfol, author=self.user).exists()
        self.assertFalse(follow, 'отписка не работает')

    def test_new_post(self):
        """Новый пост появляеться у подписчика."""
        Follow.objects.create(user=self.fol, author=self.unfol)
        response = self.follower.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_no_post(self):
        """Новый пост не появляеться у не подписчика."""
        Follow.objects.create(user=self.unfol, author=self.fol)
        response = self.follower.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)
