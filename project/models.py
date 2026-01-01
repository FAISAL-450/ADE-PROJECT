from django.db import models
from django.contrib.auth.models import User

# Role list for project app (only Manager)
ROLE_CHOICES = [
    ('manager', 'Manager'),
]

# Profile model to assign roles to users
class ProjectProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='project_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager',
        help_text="Defines the user's role in project operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "Project Role Profile"
        verbose_name_plural = "Project Role Profiles"

# Main model for storing project details
class Project(models.Model):
    name_of_project = models.CharField(
        max_length=100,
        help_text="Name of the project"
    )
    project_address = models.CharField(
        max_length=200,
        help_text="Project site address"
    )
    contact_person_name = models.CharField(
        max_length=100,
        help_text="Primary contact person for the project"
    )
    contact_person_number = models.CharField(
        max_length=20,
        help_text="Phone number of the contact person"
    )
    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='manager',
        help_text="Team responsible for this project"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_projects',
        help_text="User who created this project"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_projects',
        help_text="User who last updated this project record"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated"
    )

    def __str__(self):
        return self.name_of_project

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Project"
        verbose_name_plural = "Projects"

