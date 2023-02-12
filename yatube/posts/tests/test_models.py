from django.test import TestCase
from mixer.backend.django import mixer

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        group = mixer.blend(Group)
        cls.group = group
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        results = {
            self.post: 'Тестовый пост',
        }
        for field, expected_value in results.items():
            with self.subTest(field=field):
                self.assertEqual(
                    str(object=field), expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        group = mixer.blend(Group, title='Тестовая группа')
        cls.group = group

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        results = {
            self.group: 'Тестовая группа',
        }
        for field, expected_value in results.items():
            with self.subTest(field=field):
                self.assertEqual(
                    str(object=field), expected_value)
