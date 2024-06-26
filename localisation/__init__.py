from .en import en
from .ru import ru
import locale


default = ru  # Default language

defaultlocale = locale.getdefaultlocale()[0]
if defaultlocale.startswith('en'):
    default = en
elif defaultlocale.startswith('ru'):
    default = ru
