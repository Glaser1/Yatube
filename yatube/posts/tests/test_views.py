import tempfile
import shutil

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
import datetime as dt
from posts.models import Post, Group, Comment, Follow
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PaginatorTestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='test_slug',
            description='TextDescription'
        )
        for text in range(13):
            Post.objects.create(
                text=f'запись №:{text}',
                group=cls.group,
                author=cls.user,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_first_homepage_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_homepage_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_grouplist_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_grouplist_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_profile_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user}
                    )
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_profile_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_post = User.objects.create_user(username='TestAuthor')
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.group_2 = Group.objects.create(
            title='TestGroup2',
            slug='test_slug_2',
            description='Тестовое описание_2'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small_gif.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            author=cls.author_post,
            text='Тестовая запись',
            id=1,
            pub_date=dt.datetime.today(),
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='TestUser')
        self.author = Client()
        self.author.force_login(self.author_post)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_urls_names_use_correct_templates(self):
        templates = [
            ['posts:index', 'posts/index.html'],
            ['posts:profile', 'posts/profile.html',
             ['username', self.author_post]
             ],
            ['posts:post_detail', 'posts/post_detail.html',
             ['post_id', self.post.id]],
            ['posts:group_list', 'posts/group_list.html',
             ['slug', self.group.slug]
             ],
            ['posts:post_edit', 'posts/create_post.html',
             ['post_id', self.post.id]
             ],
            ['posts:post_create', 'posts/create_post.html']
        ]
        for template in templates:
            name = template[0]
            html = template[1]
            if len(template) == 2:
                with self.subTest(name=name):
                    response = self.author.get(reverse(name))
            else:
                kwargs = template[2]
                with self.subTest(name=name):
                    response = self.author.get(
                        reverse(name, kwargs={kwargs[0]: kwargs[1]})
                    )
            self.assertTemplateUsed(response, html)

    def check_context(self, post_object):
        self.assertEqual(post_object.text, self.post.text)
        self.assertEqual(post_object.author, self.post.author)
        self.assertEqual(post_object.group, self.post.group)
        self.assertEqual(post_object.id, self.post.id)
        self.assertEqual(post_object.image, self.post.image)

    def test_homepage_shows_correct_context(self):
        response = self.client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.check_context(first_object)

    def test_profile_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.author_post})
        )
        first_object = response.context['page_obj'][0]
        self.check_context(first_object)

    def test_create_post_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_shows_correct_context(self):
        response = self.author.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
                self.assertEqual(
                    response.context.get('post').text,
                    self.post.text
                )
                self.assertEqual(
                    response.context.get('post').author,
                    self.post.author
                )
                self.assertEqual(response.context.get('post').id, self.post.id)
                self.assertEqual(
                    response.context.get('post').group,
                    self.post.group
                )

    def test_group_list_shows_correct_context(self):
        response = self.client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        self.check_context(first_object)

    def test_post_detail_shows_correct_context(self):
        comment = Comment.objects.create(
            text='TestComment',
            author=self.user,
            post=self.post
        )
        response = self.author.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id})
        )
        self.assertEqual(self.post, response.context['post'])
        self.assertEqual(self.post.image, response.context['post'].image)
        self.assertEqual(comment, response.context['post'].comments.all()[0])

    def test_post_in_one_group(self):
        response = self.client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id})
        )
        self.assertIsNot(response.context['post'].group.pk, self.group_2.pk)


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(
            text='TestCache',
            author=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_cache_homepage(self):
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        count = Post.objects.count()
        self.post.delete()
        self.assertEqual(len(response.context['page_obj']), count)
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        count2 = Post.objects.count()
        self.assertEqual(len(response.context['page_obj']), count2)


class FollowingTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.author = User.objects.create_user(username='author')
        cls.user2 = User.objects.create_user(username='guest')
        cls.post = Post.objects.create(
            text='TestText',
            author=cls.author
        )

    def setUp(self):
        self.follower_client = Client()
        self.follower_client.force_login(self.user)
        self.unfollower_client = Client()
        self.unfollower_client.force_login(self.user2)
        cache.clear()

    def test_user_follows(self):
        Follow.objects.create(user=self.user, author=self.author)
        self.assertTrue(Follow.objects.filter(
            user=self.user,
            author=self.author).exists()
        )
        self.assertFalse(Follow.objects.filter(
            user=self.user2,
            author=self.author).exists()
        )
        Follow.objects.filter(
            user=self.user,
            author=self.author).delete()
        self.assertFalse(Follow.objects.filter(
            user=self.user,
            author=self.author).exists()
        )

    def test_follower_context(self):
        Follow.objects.create(user=self.user, author=self.author)
        response = self.follower_client.get(reverse('posts:follow_index'))
        before_new_post = len(response.context['page_obj'])
        Post.objects.create(
            text='Test',
            author=self.author
        )
        response = self.follower_client.get(reverse('posts:follow_index'))
        after_new_post = len(response.context['page_obj'])
        self.assertNotEqual(before_new_post, after_new_post)

    def test_unfollower_context(self):
        Follow.objects.create(user=self.user, author=self.author)
        response = self.unfollower_client.get(reverse('posts:follow_index'))
        before_new_post = len(response.context['page_obj'])
        Post.objects.create(
            text='Test',
            author=self.author
        )
        response = self.unfollower_client.get(reverse('posts:follow_index'))
        after_new_post = len(response.context['page_obj'])
        self.assertEqual(before_new_post, after_new_post)
