import functools
from types import MappingProxyType

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.functional import classproperty
from django.utils.translation import gettext_lazy as _


def model_with_custom_manager(model_class, manager_instance):
    class Proxy(model_class):
        objects = manager_instance

        class Meta:
            proxy = True
            # TODO Really not necessary?
            # app_label = model_class._meta.app_label

    return Proxy


class OwnedModel(models.Model):
    """
    A model that has a relationship to the owner in the user model.
    """

    owner = models.ForeignKey(get_user_model(), on_delete=models.RESTRICT)

    class Meta:
        abstract = True


class EnhancedTextChoices(models.TextChoices):

    @classproperty
    def max_value_length(cls):
        return max(len(value) for value in cls.values)

    @classmethod
    @functools.lru_cache(maxsize=1)
    def get_value_to_choice_mapping(cls):
        return MappingProxyType(dict(cls.choices))

    @classmethod
    def map_value_to_choice(cls, value):
        return cls.get_value_to_choice_mapping()[value]

    @classmethod
    @functools.lru_cache(maxsize=1)
    def get_choice_to_value_mapping(cls):
        return MappingProxyType(dict(cls.values))

    @classmethod
    def map_choice_to_value(cls, choice):
        return cls.get_choice_to_value_mapping()[choice]


class Encoding(EnhancedTextChoices):
    ASCII = "ascii", _("ASCII")
    BINARY = "binary", _("Binary")
    ISO88591 = "iso-8859-1", _("ISO 8859-1")
    UTF8 = "utf-8", _("UTF-8")
    UTF8SIG = "utf-8-sig", _("UTF-8-SIG")

class MimeType(EnhancedTextChoices):
    PLAIN = "plain", "text/plain"
    CSV = "csv", "text/csv"
    TSV = "tsv", "text/tab-separated-values"
    XLSX = "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    XLS = "xls", "application/vnd.ms-excel"
    FASTA = "fasta", "text/x-fasta"
    # TODO Correct?
    CHAIN = "chain", "text/plain"
    # TODO Correct?
    MD5 = "md5", "text/plain"
    # TODO Correct?
    SHA256 = "sha256", "text/plain"
    GZ = "gz", "application/gzip"


class Checksum(EnhancedTextChoices):
    MD5 = "md5", _("MD5")
    SHA256 = "sha256", _("SHA-256")


class WellX(EnhancedTextChoices):
    A = "A", _("A")
    B = "B", _("B")
    C = "C", _("C")
    D = "D", _("D")
    E = "E", _("E")
    F = "F", _("F")
    G = "G", _("G")
    H = "H", _("H")


class Canton(EnhancedTextChoices):
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
