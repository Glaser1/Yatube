from django.test import TestCase
from django.contrib.auth import get_user_model
from posts.models import Group, Post, Comment, Follow

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
        post = self.post
        self.assertEqual(post.text[:15], str(post))
        verbose = post._meta.get_field('text').verbose_name
        help_text = post._meta.get_field('text').help_text
        self.assertEqual(verbose, 'Текст записи')
        self.assertEqual(help_text, 'Введите текст')

    def test_post_help_text(self):
        post = self.post
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
        post = self.post
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
        group = self.group
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
        group = self.group
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


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текстовая группа'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='TestComment'
        )

    def test_comment_objects_has_correct_object_names(self):
        comment = self.comment
        self.assertEqual(comment.text[:15], str(comment))

    def test_comment_verboses(self):
        comment = self.comment
        field_verboses = {
            'text': 'Текст нового комментария',
            'author': 'Автор комментария',
            'post': 'Запись'
        }
        for field, expected in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name,
                    expected
                )

    def test_comment_help_text(self):
        comment = self.comment
        field_help_text = {
            'text': 'Введите текст',
            'post': 'Выберите запись'
        }
        for field, expected in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).help_text,
                    expected
                )


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='follower')
        cls.following = User.objects.create_user(username='following')
        cls.follow = Follow.objects.create(
            user=cls.follower,
            author=cls.following
        )

    def test_follow_objects_has_correct_objects_names(self):
        follow = self.follow
        self.assertEqual(
            f'{self.follower} подписан на {self.following}',
            str(follow)
        )

    def test_follow_verboses(self):
        follow = self.follow
        field_verboses = {
            'author': 'Избранный автор',
            'user': 'Подписчик'
        }
        for field, expected in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).verbose_name,
                    expected
                )

    def test_follow_help_text(self):
        follow = self.follow
        field_help_text = {'author': 'Выберите пользователя'}
        for field, expected in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).help_text,
                    expected
                )
