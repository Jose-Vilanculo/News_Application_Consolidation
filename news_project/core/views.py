from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, login, authenticate
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from .models import Article, Publisher, Newsletter
from .forms import (
    SubscriptionForm, ArticleForm, UserRegistrationForm, NewsletterForm
)
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q


def home_view(request):
    """
    Render the home page or redirect authenticated users.

    :param request: HTTP request with authentication data.
    :type request: HttpRequest
    :return: Redirect to dashboard or render home page.
    :rtype: HttpResponse
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')


def login_view(request):
    """
    Authenticate user and log them in.

    :param request: HTTP request with login credentials.
    :type request: HttpRequest
    :return: Redirect to dashboard or render login form.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request,
                          'core/login.html',
                          {'error': 'Invalid credentials'}
                          )
    return render(request, 'core/login.html')


def register_view(request):
    """
    Register a new user and log them in.

    :param request: HTTP request with registration data.
    :type request: HttpRequest
    :return: Redirect to dashboard or render registration form.
    :rtype: HttpResponse
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if form.cleaned_data['role'] == 'publisher':
                name = form.cleaned_data['username']
                print(name)
                Publisher.objects.get_or_create(name=name)
            login(request, user)  # auto-login after register
            messages.success(request, "Registration successful.")
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def logout_view(request):
    """
    Log out the current user.

    :param request: HTTP request with session data.
    :type request: HttpRequest
    :return: Redirect to home page.
    :rtype: HttpResponseRedirect
    """
    logout(request)
    return redirect('home')


@login_required
def dashboard_view(request):
    """
    Display dashboard for the user's role.

    :param request: HTTP request with user data.
    :type request: HttpRequest
    :return: Rendered dashboard page.
    :rtype: HttpResponse
    """
    user = request.user
    pending_articles = Article.objects.filter(approved=False)
    approved_articles = Article.objects.filter(approved=True)
    pending_newsletters = Newsletter.objects.filter(approved=False)
    approved_newsletters = Newsletter.objects.filter(approved=True)

    if user.is_reader():
        # get articles based on users subscriptions
        subscribed_articles = Article.objects.filter(
            approved=True).filter(
                Q(journalist__in=user.subscribed_journalists.all()) |
                Q(publisher__in=user.subscribed_publishers.all())
                ).order_by('-created_at')
        subscribed_newsletter = Newsletter.objects.filter(
            approved=True).filter(
                Q(journalist__in=user.subscribed_journalists.all()) |
                Q(publisher__in=user.subscribed_publishers.all())
                ).order_by('-created_at')
        return render(
                    request,
                    'core/reader_dashboard.html',
                    {"articles": subscribed_articles,
                     "newsletters": subscribed_newsletter}
                )
    elif user.is_journalist():
        user = request.user
        approved_articles = Article.objects.filter(
            journalist=user, approved=True
        )
        pending_articles = Article.objects.filter(
            journalist=user, approved=False
        )
        approved_newsletters = Newsletter.objects.filter(
            journalist=user, approved=True
        )
        pending_newsletters = Newsletter.objects.filter(
            journalist=user, approved=False
        )

        return render(request, 'core/journalist_dashboard.html', {
            'approved_articles': approved_articles,
            'pending_articles': pending_articles,
            'approved_newsletters': approved_newsletters,
            'pending_newsletters': pending_newsletters
        })
    elif user.is_editor():
        return render(
            request,
            'core/editor_dashboard.html',
            {'approved_articles': approved_articles,
             'pending_articles': pending_articles,
             'approved_newsletters': approved_newsletters,
             'pending_newsletters': pending_newsletters}
        )
    elif user.is_publisher():
        publisher = Publisher.objects.get(name=request.user)
        approved_articles = Article.objects.filter(
            publisher=publisher, approved=True
        )
        pending_articles = Article.objects.filter(
            publisher=publisher, approved=False
        )
        return render(
            request,
            'core/publisher_dashboard.html', {
                'approved_articles': approved_articles,
                'pending_articles': pending_articles,
            }
        )
    else:
        return redirect('login')


def is_journalist(user):
    """
    Check if user is a journalist.

    :param user: User instance.
    :type user: User
    :return: True if authenticated journalist.
    :rtype: bool
    """
    return user.is_authenticated and user.is_journalist()


def is_editor(user):
    """
    Check if user is an editor.

    :param user: User instance.
    :type user: User
    :return: True if authenticated editor.
    :rtype: bool
    """
    return user.is_authenticated and user.is_editor()


def is_editor_or_journalist(user):
    """
    Check if user is an editor or journalist.

    :param user: User instance.
    :type user: User
    :return: True if editor or journalist.
    :rtype: bool
    """
    return user.is_authenticated and (user.is_editor() or user.is_journalist())


@login_required
@user_passes_test(lambda u: u.is_reader())
def manage_subscriptions(request):
    """
    Manage reader subscriptions.

    :param request: HTTP request with subscription data.
    :type request: HttpRequest
    :return: Redirect to dashboard or render subscriptions page.
    :rtype: HttpResponse
    """
    user = request.user

    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            publishers = form.cleaned_data['publishers']
            journalists = form.cleaned_data['journalists']

            # Clear previous and set new subscriptions
            user.subscribed_publishers.set(publishers)
            user.subscribed_journalists.set(journalists)

            user.save()
            messages.success(request, "Subscriptions updated!")
            return redirect('dashboard')
    else:
        form = SubscriptionForm(initial={
            'publishers': user.subscribed_publishers.all(),
            'journalists': user.subscribed_journalists.all(),
        })

    return render(request, 'core/manage_subscriptions.html', {'form': form})


@login_required
@user_passes_test(is_editor)
def approve_article(request, article_id):
    """
    Approve an article.

    :param request: HTTP request by an editor.
    :type request: HttpRequest
    :param article_id: Article ID.
    :type article_id: int
    :return: Redirect to dashboard.
    :rtype: HttpResponseRedirect
    :raises Http404: If article not found.
    """
    article = get_object_or_404(Article, id=article_id)
    article.approved = True
    article.save()
    return HttpResponseRedirect('/dashboard/')


@login_required
@user_passes_test(is_journalist)
def create_article(request):
    """
    Create a new article.

    :param request: HTTP request with article data.
    :type request: HttpRequest
    :return: Redirect to dashboard or render form.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.journalist = request.user
            article.approved = False
            article.save()
            messages.success(request, "Article created and awaiting approval.")
            return redirect('dashboard')
        else:
            messages.error(request, "There's a problem with your submission.")
            print(form.errors)

    else:
        form = ArticleForm()

    return render(request, 'core/create_article.html', {'form': form})


@login_required
@user_passes_test(is_editor_or_journalist)
def edit_article(request, pk):
    """
    Edit an article.

    :param request: HTTP request with updated data.
    :type request: HttpRequest
    :param pk: Article primary key.
    :type pk: int
    :return: Redirect to dashboard or render edit form.
    :rtype: HttpResponse
    :raises Http404: If article not found.
    """
    article = get_object_or_404(Article, pk=pk)

    # Check ownership/permission manually
    if request.user.is_journalist() and article.journalist != request.user:
        messages.error(request, "You can only edit your own articles.")
        return redirect('dashboard')

    form = ArticleForm(request.POST or None, instance=article)
    if form.is_valid():
        form.save()
        messages.success(request, "Article updated.")
        return redirect('dashboard')

    return render(
        request,
        'core/edit_article.html',
        {'form': form, 'article': article}
    )


@login_required
@user_passes_test(is_editor_or_journalist)
def delete_article(request, pk):
    """
    Delete an article.

    :param request: HTTP request to delete.
    :type request: HttpRequest
    :param pk: Article primary key.
    :type pk: int
    :return: Redirect or render confirmation.
    :rtype: HttpResponse
    :raises HttpResponseForbidden: No permission.
    :raises Http404: If not found.
    """
    article = get_object_or_404(Article, pk=pk)

    # Check if user is allowed to delete
    if request.user == article.journalist or request.user.is_editor():
        if request.method == 'POST':
            article.delete()
            messages.success(request, "🗑️ Article deleted successfully.")
            return redirect('dashboard')
        return render(
            request, 'core/delete_article_confirm.html', {'article': article}
        )
    else:
        return HttpResponseForbidden(
            "You do not have permission to delete this article."
        )


@login_required
def article_detail(request, pk):
    """
    Display article details.

    :param request: HTTP request.
    :type request: HttpRequest
    :param pk: Article primary key.
    :type pk: int
    :return: Render article detail page.
    :rtype: HttpResponse
    :raises Http404: If not found.
    """
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'core/article_detail.html', {'article': article})


@login_required
def newsletter_detail(request, pk):
    """
    Display newsletter details.

    :param request: HTTP request.
    :type request: HttpRequest
    :param pk: Newsletter primary key.
    :type pk: int
    :return: Render newsletter detail page.
    :rtype: HttpResponse
    :raises Http404: If not found.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)
    return render(
        request,
        'core/newsletter_detail.html',
        {"newsletter": newsletter}
    )


@login_required
@user_passes_test(is_journalist)
def create_newsletter(request):
    """
    Create a newsletter.

    :param request: HTTP request with data.
    :type request: HttpRequest
    :return: Redirect to dashboard or render form.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.journalist = request.user
            newsletter.save()
            messages.success(
                request, "Newsletter created and awaiting approval."
            )
            return redirect('dashboard')
        else:
            messages.error(request, "There's a problem with your submission.")
            print(form.errors)

    else:
        form = NewsletterForm()
    return render(request, 'core/create_newsletter.html', {'form': form})


@login_required
@user_passes_test(is_editor_or_journalist)
def edit_newsletter(request, pk):
    """
    Edit a newsletter.

    :param request: HTTP request with updated data.
    :type request: HttpRequest
    :param pk: Newsletter primary key.
    :type pk: int
    :return: Redirect to dashboard or render edit form.
    :rtype: HttpResponse
    :raises Http404: If not found.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)

    # Check ownership/permission manually
    if request.user.is_journalist() and newsletter.journalist != request.user:
        messages.error(request, "You can only edit your own Newsletter.")
        return redirect('dashboard')

    form = NewsletterForm(request.POST or None, instance=newsletter)
    if form.is_valid():
        form.save()
        messages.success(request, "Newsletter updated.")
        return redirect('dashboard')

    return render(
        request,
        'core/edit_newsletter.html',
        {'form': form, 'newsletter': newsletter}
    )


@login_required
@user_passes_test(is_editor_or_journalist)
def delete_newsletter(request, pk):
    """
    Delete a newsletter.

    :param request: HTTP request to delete.
    :type request: HttpRequest
    :param pk: Newsletter primary key.
    :type pk: int
    :return: Redirect or render confirmation.
    :rtype: HttpResponse
    :raises HttpResponseForbidden: No permission.
    :raises Http404: If not found.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)

    # Check if user is allowed to delete
    if request.user == newsletter.journalist or request.user.is_editor():
        if request.method == 'POST':
            newsletter.delete()
            messages.success(request, "🗑️ Newsletter deleted successfully.")
            return redirect('dashboard')
        return render(
            request,
            'core/delete_newsletter_confirm.html',
            {'newsletter': newsletter}
        )
    else:
        return HttpResponseForbidden(
            "You do not have permission to delete this newsletter."
        )


@login_required
@user_passes_test(is_editor)
def approve_newsletter(request, newsletter_id):
    """
    Approve a newsletter.

    :param request: HTTP POST request by editor.
    :type request: HttpRequest
    :param newsletter_id: Newsletter ID.
    :type newsletter_id: int
    :return: Redirect to dashboard.
    :rtype: HttpResponseRedirect
    :raises HttpResponseNotAllowed: If method not POST.
    :raises Http404: If not found.
    """
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    print(f"Newsletter Object: {newsletter}")

    if request.method == "POST":
        newsletter.approved = True
        newsletter.save()
        return HttpResponseRedirect('/dashboard/')

    # show a 405 error if someone tries to GET this URL directly
    return HttpResponseNotAllowed(['POST'])
