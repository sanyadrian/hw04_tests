from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовая группа',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Tecтовая группа 2'
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        tempplates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts', kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': PostPagesTests.user.username
            }): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.pk
            }): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.pk
            }): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for reverse_name, template in tempplates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        post_obj_page = response.context['page_obj'][0]
        post_text = post_obj_page.text
        post_group = post_obj_page.group
        post_author = post_obj_page.author
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_group, self.group)
        self.assertEqual(post_author, self.user)

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts', kwargs={'slug': PostPagesTests.group.slug}
            )
        )
        first_object_group = response.context['group']
        first_object_page_obj = response.context['page_obj'][0]
        post_text_0 = first_object_page_obj.text
        post_author_0 = first_object_page_obj.author.username
        post_group_0 = first_object_page_obj.group.title
        group_title_0 = first_object_group.title
        group_slug_0 = first_object_group.slug
        group_description_0 = first_object_group.description
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, PostPagesTests.user.username)
        self.assertEqual(post_group_0, PostPagesTests.group.title)
        self.assertEqual(group_title_0, PostPagesTests.group.title)
        self.assertEqual(group_slug_0, PostPagesTests.group.slug)
        self.assertEqual(group_description_0, PostPagesTests.group.description)
        print(first_object_group)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={
                    'username': PostPagesTests.user.username,
                })
        )
        author = response.context['author']
        self.assertEqual(author, PostPagesTests.user)
        post_object = response.context['page_obj'][0]
        test_author = post_object.author.username
        test_text = post_object.text
        test_post_count = Post.objects.filter(
            author=PostPagesTests.user
        ).count()
        self.assertEqual(test_author, PostPagesTests.user.username)
        self.assertEqual(test_text, PostPagesTests.post.text)
        self.assertEqual(test_post_count, 1)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': PostPagesTests.post.pk,
                }
            )
        )
        post_test = response.context['post']
        self.assertEqual(post_test, PostPagesTests.post)

    def test_post_edit_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit', kwargs={'post_id': PostPagesTests.post.pk}
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_create_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_show_correct_group_index_profile(self):
        group_count = Post.objects.filter(group=self.group).count()
        self.assertEqual(Post.objects.count(), group_count)
        Post.objects.create(
            text='Тестовый пост',
            author=self.user,
            group=self.group,
        )
        self.assertEqual(Post.objects.count(), group_count + 1)
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 2)
        response_1 = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={
                'slug': PostPagesTests.group.slug
            })
        )
        self.assertEqual(len(response_1.context['page_obj']), 2)
        response_2 = self.authorized_client.get(reverse(
            'posts:profile', kwargs={
                'username': PostPagesTests.user.username,
            })
        )
        self.assertEqual(len(response_2.context['page_obj']), 2)

    def test_group_2_have_no_post(self):
        response = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={
                'slug': PostPagesTests.group_2.slug
            })
        )
        self.assertEqual(len(response.context['page_obj']), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовая группа',
        )

        cls.post = 13
        for cls.post in range(13):
            cls.post = Post.objects.create(
                text='Тестовая запись',
                author=cls.user,
                group=cls.group
            )

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_first_page_contains_ten_records(self):
        response = self.client.get(reverse(
            'posts:group_posts', kwargs={
                'slug': PaginatorViewsTest.group.slug
            })
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_second_page_contains_three_records(self):
        response = self.client.get(reverse(
            'posts:group_posts', kwargs={
                'slug': PaginatorViewsTest.group.slug
            }) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        response = self.client.get(reverse(
            'posts:profile', kwargs={
                'username': PaginatorViewsTest.user.username,
            })
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_three_records(self):
        response = self.client.get(reverse(
            'posts:profile', kwargs={
                'username': PaginatorViewsTest.user.username,
            }) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)
