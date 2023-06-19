from django.db import models
from django.contrib.auth import get_user_model


class OwnedModel(models.Model):
    """
    A model that has a relationship to the owner in the user model
    """

    owner = models.ForeignKey(get_user_model(), on_delete=models.RESTRICT)

    class Meta:
        abstract = True
