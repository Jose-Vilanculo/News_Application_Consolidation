from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import ArticleSerializer
from .models import Article


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscribed_articles(request):
    """
    Retrieve approved articles from a reader's subscribed publishers
    and journalists.

    This API endpoint is accessible only to authenticated users
    with the Reader role.
    It returns a list of distinct, approved articles authored by:
    - Journalists the reader is subscribed to
    - Publishers the reader is subscribed to

    Returns:
        Response: JSON serialized list of articles or a 403 error
        if the user is not a reader.
    """
    user = request.user

    # Readers only
    if not user.is_reader():
        return Response({'detail': 'Only readers can access this endpoint.'},
                        status=403)

    # Get subscribed sources
    publishers = user.subscribed_publishers.all()
    journalists = user.subscribed_journalists.all()

    # Filter approved articles
    articles = Article.objects.filter(
        approved=True
    ).filter(
        publisher__in=publishers
    ) | Article.objects.filter(
        approved=True,
        journalist__in=journalists
    )

    # Remove duplicates and serialize
    articles = articles.distinct()
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)
