from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Post, Group, Follow
from http import HTTPStatus


User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage_exist_at_desired_location(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_about_author_exist_at_desired_location(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_about_tech_exist_at_desired_location(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_404(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.post_author = User.objects.create_user(username='TestAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.post_author,
            text='Тестовая запись',
            id=0
        )
        cls.follow = Follow.objects.create(
            user=cls.post_author,
            author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author = Client()
        self.author.force_login(self.post_author)

    def test_group_url_exist_at_desired_location(self):
        """Страница /group/<slug:slug>/ доступна любому пользователю"""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_profile_url_exist_at_desired_location(self):
        """Страница /profile/<str:username>/ доступна любому пользователю"""
        response = self.authorized_client.get('/profile/TestAuthor/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_post_detail_url_exist_at_desired_location(self):
        """Страница /posts/<int:post_id>/ доступна любому пользователю"""
        response = self.guest_client.get('/posts/0/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_post_edit_url_exist_at_desired_Location_author(self):
        """Страница /posts/<int:post_id>/edit/ доступна автору записи"""
        response = self.author.get('/posts/0/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_post_create_url_exist_at_desired_location_authorized(self):
        """Страница /create/ доступна авторизованному пользователю"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_unexisting_page(self):
        """Несуществующая страница"""
        response = self.guest_client.get('/not_a_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_post_create_url_redirect_annonymous_on_login(self):
        """Страница /create/ перенаправляет анонимного пользователя"""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_edit_url_redirect_annonymous_on_login(self):
        """Страница /edit/ анонимного пользователя"""
        response = self.guest_client.get('/posts/0/edit/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/0/edit/')

    def test_profile_follow_exists(self):
        response = self.authorized_client.get('/profile/TestAuthor/follow/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_profile_unfollow_exists(self):
        response = self.author.get('/profile/TestUser/unfollow/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_follow_url_exists_at_desired_Location(self):
        response = self.authorized_client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_add_comment(self):
        response = self.authorized_client.get('/posts/0/comment/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_url_uses_correct_template(self):
        template_urls = {
            '/': 'posts/index.html',
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/TestAuthor/': 'posts/profile.html',
            '/posts/0/': 'posts/post_detail.html',
            '/posts/0/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',

        }

        for adress, template in template_urls.items():
            with self.subTest(adress=adress):
                response = self.author.get(adress)
                self.assertTemplateUsed(response, template)
