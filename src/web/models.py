from django.db import models
from django.urls import reverse

# Create your models here.


class Event(models.Model):
    """
    An Event.
    """

    name = models.CharField(max_length=64, help_text="name of this event")
    description = models.TextField(blank=True, null=True, help_text="name of this event")
    date_time = models.DateTimeField(auto_now=False, auto_now_add=False, help_text="")
    duration = models.IntegerField(blank=True, null=True, help_text="planned duration of this event")
    location = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="location where this event is being hosted",
    )
    # group = models.ForeignKey("TechGroup", blank=True, null=True, on_delete=models.SET_NULL)
    # labels = models.ManyToManyField("TechnicalArea")

    # class Meta:
    #     ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.name  # type: ignore

    def get_absolute_url(self) -> str:
        return reverse("web:detail_event", kwargs={"pk": self.pk})
