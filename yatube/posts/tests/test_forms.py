import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
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
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        group = mixer.blend(Group)
        cls.group = group
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            image=cls.uploaded,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый коментарий',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.auth = Client()
        self.auth.force_login(self.user)

    def test_create_commet(self):
        """Валидна форма создания комментария только автору."""
        Comment.objects.all().delete()
        comment_count = Comment.objects.count()
        response = self.auth.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data={
                'text': 'текстовый comment',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(('posts:post_detail'),
                             kwargs={'post_id': self.post.id}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_create_Post(self):
        """Валидная форма создает запись в Post."""
        Post.objects.all().delete()
        post_count = Post.objects.count()
        response = self.auth.post(
            reverse('posts:post_create'),
            data={
                'text': 'текстовый текст',
                'group': self.group.id,
            },
            follow=True,
        )
        self.assertRedirects(response, reverse(('posts:profile'),
                             kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_Post(self):
        """Валидная форма редактирует запись в Post."""
        post_count = Post.objects.count()
        response = self.auth.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data={
                'text': 'текстовый текст',
                'group': self.group.id,
            },
            follow=True,
        )
        self.assertRedirects(response, f'/posts/{self.post.id}/')
        self.assertEqual(Post.objects.count(), post_count)
