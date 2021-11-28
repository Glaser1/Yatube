from django.test import TestCase
from django.contrib.auth import get_user_model
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текстовая группа'
        )

    def test_post_model_has_correct_object_names(self):
        post = PostModelTest.post
        self.assertEqual(post.text[:15], str(post))
        verbose = post._meta.get_field('text').verbose_name
        help_text = post._meta.get_field('text').help_text
        self.assertEqual(verbose, 'Текст записи')
        self.assertEqual(help_text, 'Введите текст')

    def test_post_help_text(self):
        post = PostModelTest.post
        field_help_text = {
            'text': 'Введите текст',
            'author': 'Укажите автора',
            'group': 'Выберите группу'
        }
        for field, expected in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected)

    def test_post_verboses(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст записи',
            'author': 'Автор записи',
            'group': 'Группа'
        }
        for field, expected in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )

    def test_group_model_has_correct_object_names(self):
        group = GroupModelTest.group
        self.assertEqual(group.title, str(group))

    def test_group_verboses(self):
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Группа',
            'slug': 'Идентификатор',
            'description': 'Описание группы'
        }
        for field, expected in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name,
                    expected
                )

    def test_group_help_text(self):
        group = GroupModelTest.group
        field_help_text = {
            'title': 'Заполните название группы',
            'slug': 'Строка или число',
            'description': 'Заполните описание группы'
        }
        for field, expected in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text,
                    expected
                )
