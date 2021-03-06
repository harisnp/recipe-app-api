from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """
    Test the publicly available Tags API.
    """
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
        Test for checking login required for accessing the
        Tags API
        """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """
    Test the authorized API of Tags.
    """
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'haris@baabte.com', '12345'
            )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """
        Test retrieving the tags
        """
        Tag.objects.create(user=self.user, name='Chicken')
        Tag.objects.create(user=self.user, name='Icecream')
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_tag_for_user(self):
        """
        Tag retrieved for specific to a user
        """
        user2 = get_user_model().objects.create_user(
            'harisnew@baabte.com',
            '12345')
        Tag.objects.create(user=user2, name='Beef')
        tag = Tag.objects.create(user=self.user, name='Icecream')
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_valid(self):
        """
        Test for creating a tag
        """
        payload = {
            'name': 'Test tag'
        }
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res1 = self.client.get(TAGS_URL)
        self.assertEqual(len(res1.data), 1)
        self.assertEqual(res1.data[0]['name'], payload['name'])

    def test_create_tag_invalid(self):
        """
        Test to see that empty string should not be allowed.
        """
        payload = {
            'name': ''
        }
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
