from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Article, Newsletter
from django.contrib.auth import get_user_model
from .functions.tweet import Tweet


@receiver(post_save, sender=Article)
def notify_on_approval(sender, instance, created, **kwargs):
    """
    Signal handler triggered when an Article is saved.

    If the article is approved, this function:
    - Sends an email notification with the article to all users subscribed
    to the journalist or publisher.
    - Posts the article content to X (formerly Twitter) using the Tweet
    class.

    :param sender: The model class (Article).
    :type sender: Model
    :param instance: The Article instance being saved.
    :type instance: Article
    :param created: True if the instance was created, False if updated.
    :type created: bool
    :param kwargs: Additional keyword arguments.
    :type kwargs: dict
    """
    if instance.approved:
        # Collect all subscribers to the journalist and publisher
        journalist = instance.journalist
        publisher = instance.publisher

        # Get emails from both subscriber groups
        journalist_subs = journalist.followers.all()
        publisher_subs = (
            publisher.subscribed_readers.all() if publisher else []
        )

        recipients = set()

        for reader in journalist_subs:
            recipients.add(reader.email)

        for reader in publisher_subs:
            recipients.add(reader.email)

        if recipients:
            subject = f"New Article: {instance.title}"
            message = instance.content
            from_email = settings.DEFAULT_FROM_EMAIL
            send_mail(subject, message, from_email, list(recipients))

        # MOCK sending to X (Twitter)
        text = f'''📰 Article from {journalist.username}: {instance.title}
{instance.content}'''
        try:
            tweet = Tweet()
            tweet.make_tweet(text=text)
        except Exception as e:
            print(f"Error posting to X: {e}")


User = get_user_model()


@receiver(post_save, sender=Newsletter)
def send_newsletter_to_subscribers(sender, instance, created, **kwargs):
    """
    Signal handler that emails a newsletter when it is approved.

    Sends the newsletter body to all readers subscribed to the journalist
    or the selected publisher, if provided.

    :param sender: The model class (Newsletter).
    :type sender: Model
    :param instance: The Newsletter instance being saved.
    :type instance: Newsletter
    :param approved: True if the instance is approved.
    :type approved: bool
    :param kwargs: Additional keyword arguments.
    :type kwargs: dict
    """
    if instance.approved:
        journalist = instance.journalist
        publisher = instance.publisher

        # Readers subscribed to the journalist
        journalist_subs = User.objects.filter(
            subscribed_journalists=journalist
        )

        # Readers subscribed to the publisher (if any)
        if publisher:
            publisher_subs = User.objects.filter(
                subscribed_publishers=publisher
            )
        else:
            publisher_subs = User.objects.none()

        # Combine and deduplicate readers
        all_readers = (journalist_subs | publisher_subs).distinct()

        subject = f"📰 Newsletter from {journalist.username}: {instance.title}"
        message = instance.body
        from_email = settings.DEFAULT_FROM_EMAIL

        for reader in all_readers:
            if reader.email:
                send_mail(
                    subject,
                    message,
                    from_email,
                    [reader.email],
                    fail_silently=True
                )
