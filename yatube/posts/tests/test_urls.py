from http import HTTPStatus

from django.test import Client, TestCase
from mixer.backend.django import mixer

from ..models import Group, Post, User


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author_url(self):
        """Проверка доступности адреса /about/author/."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech_url(self):
        """Проверка доступности адреса /about/tech/."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='auth')
        group = mixer.blend(Group)
        cls.group = group
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
        )

    def setUp(self):
        self.anon = Client()
        self.auth = Client()
        self.auth.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблоны."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/1': 'core/404.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.auth.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_all_users(self):
        """URL-адреса доступны всем пользователям."""
        url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }
        for address in url_names:
            with self.subTest(address=address):
                response = self.anon.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_authorized_client(self):
        """URL-адрес /create/ доступен авторизованому пользователю."""
        response = self.auth.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_guest_client(self):
        """URL-адрес /create/ перенаправит анонимного
        пользователя на /auth/login/."""
        response = self.anon.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=%2Fcreate%2F'
        )

    def test_urls_author_client(self):
        """URL-адрес /edit/ доступен автору."""
        response = self.auth.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_unexisting_page(self):
        """Страница /unexisting_page/ не существует."""
        response = self.anon.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
