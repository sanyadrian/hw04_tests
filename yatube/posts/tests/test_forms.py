import tempfile

from posts.forms import PostForm
from posts.models import Post, Group
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_create_post(self):
        post_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый заголовок',
            'group': 1,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(self.post.text, 'Тестовый пост')
        self.assertEqual(self.group, PostCreateFormTests.post.group)
        self.assertEqual(self.post.author, PostCreateFormTests.post.author)
        self.assertEqual(response.status_code, 200)

    def test_post_edit(self):
        form_data = {
            'text': 'Редактирования',
            'group': 1,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': PostCreateFormTests.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text']
            ).exists()
        )
        self.assertTrue(
            Post.objects.filter(
                group=self.group
            ).exists()
        )
        self.assertTrue(
            Post.objects.filter(
                id=PostCreateFormTests.post.pk
            )
        )

        self.assertEqual(response.status_code, 200)
        
    def test_guest_client_create_post(self):
        authorized_url = reverse('posts:post_create')
        post_count = Post.objects.count()
        form_data = {
            'text': 'Редактирования',
            'group': 1,
        }
        response = self.guest_client.post(
            reverse('post:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertRedirects(response, f'/auth/login/?next={authorized_url}')