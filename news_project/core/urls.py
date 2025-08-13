from django.urls import path
from .api_views import subscribed_articles
from . import views
from .views import logout_view, create_newsletter


urlpatterns = [

    path('', views.home_view, name='home'),

    path('logout/', logout_view, name='logout'),

    path('register/', views.register_view, name='register'),

    path('login/', views.login_view, name='login'),


    path(
        'dashboard/',
        views.dashboard_view,
        name='dashboard'),

    path(
        'subscriptions/',
        views.manage_subscriptions,
        name='manage_subscriptions'
    ),

    path(
        'approve/article/<int:article_id>/',
        views.approve_article,
        name='approve_article'
    ),

    path(
        'api/articles/',
        subscribed_articles,
        name='subscribed_articles_api'
    ),

    path('articles/new/', views.create_article, name='create_article'),

    path('articles/edit/<int:pk>/', views.edit_article, name='edit_article'),

    path(
        'articles/<int:pk>/delete/',
        views.delete_article,
        name='delete_article'
    ),

    path(
        'articles/<int:pk>/',
        views.article_detail,
        name='article_detail'
    ),

    path(
        'approve/newsletter/<int:newsletter_id>/',
        views.approve_newsletter,
        name='approve_newsletter'
    ),

    path('newsletters/new/', create_newsletter, name='create_newsletter'),

    path(
        'newsletter/<int:pk>/',
        views.newsletter_detail,
        name='newsletter_detail'
    ),

    path(
        'newsletter/edit/<int:pk>/',
        views.edit_newsletter,
        name='edit_newsletter'
    ),

    path(
        'newsletter/<int:pk>/delete/',
        views.delete_newsletter,
        name='delete_newsletter'
    ),

]
