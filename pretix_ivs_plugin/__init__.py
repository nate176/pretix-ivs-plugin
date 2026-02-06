__version__ = "1.0.0"
from django.utils.translation import gettext_lazy as _
from pretix.base.plugins import PluginConfig

class PluginApp(PluginConfig):
    name = 'pretix_ivs_plugin'
    verbose_name = 'Pretix IVS Plugin'

    class PretixPluginMeta:
        name = _('IVS Plugin')
        author = 'Nate'
        version = '1.0.0'
        description = _('IVS Video Player')
        visible = True
        category = 'FEATURE'

    def ready(self):
        from . import signals  # NOQA

default_app_config = 'pretix_ivs_plugin.PluginApp'
