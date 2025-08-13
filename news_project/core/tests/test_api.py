from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from core.models import CustomUser, Publisher, Article


class SubscribedArticlesAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.reader = CustomUser.objects.create_user(
            username='reader',
            password='testpass',
            role='reader'
        )
        self.journalist = CustomUser.objects.create_user(
            username='journalist',
            password='testpass',
            role='journalist'
        )
        self.editor = CustomUser.objects.create_user(
            username='editor',
            password='testpass',
            role='editor'
        )

        # Create publisher
        self.publisher = Publisher.objects.create(name='Tech News')
        self.publisher.journalists.add(self.journalist)

        # Create article
        self.article = Article.objects.create(
            title='Exclusive: AI Update',
            content='Some content',
            journalist=self.journalist,
            publisher=self.publisher,
            approved=True
        )

        # Reader subscribes to journalist
        self.reader.subscribed_journalists.add(self.journalist)

    def test_reader_can_access_subscribed_articles(self):
        self.client.login(username='reader', password='testpass')
        url = reverse('subscribed_articles_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Exclusive: AI Update')

    def test_non_reader_user_cannot_access_endpoint(self):
        self.client.login(username='journalist', password='testpass')
        url = reverse('subscribed_articles_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
