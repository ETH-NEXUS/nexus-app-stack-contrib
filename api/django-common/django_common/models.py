from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


class OwnedModel(models.Model):
    """
    A model that has a relationship to the owner in the user model.
    """

    owner = models.ForeignKey(get_user_model(), on_delete=models.RESTRICT)

    class Meta:
        abstract = True


class Canton(models.TextChoices):
    AG = "AG", _("Aargau")
    AI = "AI", _("Appenzell Innerrhoden")
    AR = "AR", _("Appenzell Ausserrhoden")
    BS = "BS", _("Basel-Stadt")
    BL = "BL", _("Basel-Landschaft")
    BE = "BE", _("Bern")
    FR = "FR", _("Fribourg")
    GE = "GE", _("Genève")
    GL = "GL", _("Glarus")
    GR = "GR", _("Graubünden")
    JU = "JU", _("Jura")
    LU = "LU", _("Lucerne")
    NE = "NE", _("Neuchâtel")
    NW = "NW", _("Nidwalden")
    OW = "OW", _("Obwalden")
    SH = "SH", _("Schaffhausen")
    SZ = "SZ", _("Schwyz")
    SO = "SO", _("Solothurn")
    SG = "SG", _("St. Gallen")
    TG = "TG", _("Thurgau")
    TI = "TI", _("Ticino")
    UR = "UR", _("Uri")
    VS = "VS", _("Valais")
    VD = "VD", _("Vaud")
    ZG = "ZG", _("Zug")
    ZH = "ZH", _("Zürich")
