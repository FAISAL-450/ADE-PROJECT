from django.db import models
from django.contrib.auth.models import User

# Role list
ROLE_CHOICES = [
    ('rm', 'RM'),
]

# Unit choices
WORK_UNIT_CHOICES = [
    ('cft', 'Cft'),
    ('sft', 'Sft'),
    ('nos', 'Nos'),
    ('pcs', 'Pcs'),
    ('rm', 'Rm'),
    ('rft', 'Rft'),
]

# Group choices
GROUP_CHOICES = [
    ('civil work', 'Civil Work'),
    ('sanitary work', 'Sanitary Work'),
    ('electrical work', 'Electrical Work'),
    ('tiles work', 'Tiles Work'),
]

class ResourceProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='resource_profile'
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='rm',   # ✅ FIXED (valid choice)
        help_text="Defines the user's role in resource operations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    class Meta:
        ordering = ['user__username']
        verbose_name = "Resource Role Profile"
        verbose_name_plural = "Resource Role Profiles"

class Resource(models.Model):
    name_of_resource = models.CharField(max_length=100, blank=True)
    resource_unit = models.CharField(
        max_length=20,
        choices=WORK_UNIT_CHOICES,
        help_text="Unit of measurement for the work"
    )
    resource_group = models.CharField(
        max_length=20,
        choices=GROUP_CHOICES,
        help_text="Unit of measurement for the work"
    )
    team = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        help_text="Team responsible for this resource"
    )
    allow_team_edit = models.BooleanField(
        default=False,
        help_text="If True, allows the team member who created this record to edit/delete it"
    )
    edit_request_pending = models.BooleanField(
        default=False,
        help_text="If True, indicates the team member has requested edit/delete access"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_resource',
        help_text="User who created this resource record"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_resource',
        help_text="User who last updated this resource record"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated"
    )

    def __str__(self):
        return f"{self.name_of_resource} ({self.resource_unit})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Resource Detail"
        verbose_name_plural = "Resource Details"

