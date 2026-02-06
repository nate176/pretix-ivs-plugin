from django.utils.translation import gettext_lazy

from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = "pretix_ivs_plugin"
    verbose_name = "IVS Plugin"

    class PretixPluginMeta:
        name = gettext_lazy("IVS Plugin")
        author = "Nate"
        description = gettext_lazy("Display a Amazon Interactive Video Service livestream in it's native player.")
        visible = True
        version = __version__
        category = "FEATURE"
        compatibility = "pretix>=2.7.0"
        settings_links = []
        navigation_links = []

    def ready(self):
        from . import signals  # NOQA
