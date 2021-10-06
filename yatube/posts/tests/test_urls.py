from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовая группа',
        )

        Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            id=129,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='No')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            '/posts/129/': 'posts/post_detail.html',
            '/posts/129/edit/': 'posts/create_post.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/No/': 'posts/profile.html'
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
