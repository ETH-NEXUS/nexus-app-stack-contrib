from types import MappingProxyType

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


class Encoding(models.TextChoices):
    ASCII = "ascii", _("ASCII")
    UTF8 = "utf8", _("UTF-8")
    BINARY = "binary", _("Binary")


encoding__value_to_choice_mapping = MappingProxyType(dict(Encoding.choices))


class MimeType(models.TextChoices):
    PLAIN = "plain", "text/plain"
    CSV = "csv", "text/csv"
    TSV = "tsv", "text/tab-separated-values"
    EXCEL = "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    FASTA = "fasta", "text/x-fasta"
    # TODO Correct?
    CHAIN = "chain", "text/chain"
    # TODO Correct?
    MD5 = "md5", "text/md5",
    # TODO Correct?
    SHA256 = "sha256", "text/sha256"


mime_type__value_to_choice_mapping = MappingProxyType(dict(MimeType.choices))


class Checksum(models.TextChoices):
    MD5 = "md5", _("MD5")
    SHA256 = "sha256", _("SHA-256")


checksum__value_to_choice_mapping = MappingProxyType(dict(Checksum.choices))


class WellX(models.TextChoices):
    A = "A", _("A")
    B = "B", _("B")
    C = "C", _("C")
    D = "D", _("D")
    E = "E", _("E")
    F = "F", _("F")
    G = "G", _("G")
    H = "H", _("H")


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
