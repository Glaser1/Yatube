import tempfile
import shutil

from django.contrib.auth import get_user_model
from posts.models import Post, Group, Comment
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group1 = Group.objects.create(
            title='TestGroup1',
            slug='test_slug_1',
            description='Test_description_1'
        )
        cls.group2 = Group.objects.create(
            title='TestGroup2',
            slug='test_slug_2',
            description='Test_description_2'
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'TestText',
            'group': self.group1.id,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.filter(
            text='TestText',
            group=self.group1.id,
            image='posts/small_gif.gif'
        )
        self.assertTrue(post.exists())
        post.delete()

    def test_post_edit(self):
        post = Post.objects.create(
            text='TestText',
            group=self.group1,
            author=self.user
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'CorrectedTestText',
            'group': self.group2.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(post.id,))
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='CorrectedTestText',
                group=self.group2.id,

            ).exists()
        )

    def test_post_detail(self):
        post = Post.objects.create(
            text='TestText',
            group=self.group1,
            author=self.user,
        )
        comment = Comment.objects.create(
            text='TestComment',
            author=self.user,
            post=post
        )
        form_data = {
            'comment': comment
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail', args=(post.id,)))
        self.assertTrue(Comment.objects.filter(text='TestComment').exists())