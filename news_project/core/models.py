from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.

    Fields:
        - role: Defines the user's role ('reader', 'journalist', or 'editor')
        - subscribed_publishers: Many-to-many relationship for readers
        to follow publishers
        - subscribed_journalists: Many-to-many relationship for readers
        to follow journalists

    Methods:
        - is_reader(): Returns True if user is a reader
        - is_journalist(): Returns True if user is a journalist
        - is_editor(): Returns True if user is an editor
        - save(): Overrides save to enforce mutual exclusivity between roles
        and clear irrelevant data
        - assign_group(): Automatically assigns user to group based on role
    """
    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('journalist', 'Journalist'),
        ('editor', 'Editor'),
        ('publisher', 'Publisher')
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Reader-specific fields
    subscribed_publishers = models.ManyToManyField(
        'Publisher',
        blank=True,
        related_name='subscribed_readers'
    )
    subscribed_journalists = models.ManyToManyField(
        'CustomUser',
        blank=True,
        related_name='followers'
    )

    # Journalist-specific fields
    def is_reader(self):
        return self.role == 'reader'

    def is_journalist(self):
        return self.role == 'journalist'

    def is_editor(self):
        return self.role == 'editor'

    def is_publisher(self):
        return self.role == 'publisher'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Ensure mutual exclusivity
        if self.role == 'journalist':
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()
        elif self.role == 'reader':
            # Prevent journalist-related reverse relationships
            self.article_set.all().delete()
            self.newsletter_set.all().delete()
        self.assign_group()

    def assign_group(self):
        group, _ = Group.objects.get_or_create(name=self.role.capitalize())
        self.groups.clear()
        self.groups.add(group)


class Publisher(models.Model):
    """
    Represents a publishing entity in the system.

    Fields:
        - name: Name of the publisher
        - editors: Users with editor roles affiliated with this publisher
        - journalists: Users with journalist roles affiliated with publisher

    Methods:
        - __str__(): Returns the name of the publisher
    """
    name = models.CharField(max_length=100)
    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='editor_publishers',
        blank=True
    )
    journalists = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='journalist_publishers',
        blank=True
    )

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    Represents a news article written by a journalist.

    Fields:
        - title: Title of the article
        - content: Full text of the article
        - created_at: Timestamp of article creation
        - approved: Boolean indicating approval by an editor
        - journalist: Author of the article (must be a CustomUser)
        - publisher: Optional publisher associated with the article

    Methods:
        - __str__(): Returns the article title
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    journalist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    """
    Represents a newsletter created by a journalist.

    Fields:
        - title: Title of the newsletter
        - body: Content of the newsletter
        - created_at: Timestamp of creation
        - journalist: The journalist who authored the newsletter
        - publisher: Optional publisher under which the newsletter is released

    Methods:
        - __str__(): Returns the newsletter title
    """
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    journalist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    publisher = models.ForeignKey(
        'Publisher',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='newsletters'
    )

    def __str__(self):
        return self.title
