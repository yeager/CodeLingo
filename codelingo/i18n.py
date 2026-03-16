import gettext
import os

DOMAIN = "codelingo"
LOCALEDIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locale")
gettext.bindtextdomain(DOMAIN, LOCALEDIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext
