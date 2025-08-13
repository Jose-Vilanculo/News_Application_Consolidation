from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Article model.

    This serializer converts Article model instances to and from JSON
    representations, which are used in the API.

    Fields:
        - id: Unique identifier for the article
        - title: Title of the article
        - content: Full text of the article
        - created_at: Timestamp when the article was created
        - approved: Boolean indicating whether the article was approved by an editor
        - journalist: The user who authored the article
        - publisher: The publisher (if any) associated with the article
    """
    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'content',
            'created_at',
            'approved',
            'journalist',
            'publisher'
        ]
