from pretix.base.models import Event
from pretix.control.views.event import EventSettingsFormView,EventSettingsViewMixin
from pretix.presale.views.event import EventViewMixin
from pretix.presale.views.order import OrderDetailMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.urls import reverse
from .forms import IvsSettingsForm
from django.utils.translation import gettext_lazy as _

class IvsSettingsView(EventSettingsViewMixin, EventSettingsFormView):
    model = Event
    permission = 'can_change_settings'
    form_class = IvsSettingsForm
    template_name = 'pretix_ivs_plugin/settings.html'
 
    def get_success_url(self, **kwargs):
        return reverse('plugins:pretix_ivs_plugin:settings', kwargs={
            'organizer': self.request.event.organizer.slug,
            'event': self.request.event.slug,
        })

class IvsCheckinView(EventViewMixin, OrderDetailMixin, View):
    def post(self, request, *args, **kwargs):
        order = self.order
        event = self.request.event

        clist, _ = event.checkin_lists.get_or_create(name="Online Stream")

        for op in order.positions.all():
            if not op.checkins.filter(list=clist).exists():
                op.checkins.create(list=clist)
        messages.success(request, _("You are now checked in! Enjoy the stream."))
        return redirect(self.get_order_url())

@method_decorator(xframe_options_exempt, name='dispatch')
class IvsPlayerView(TemplateView):
    template_name = "pretix_ivs_plugin/iframe_player.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self.request.GET.get('url')
        return context

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        csp_parts = [
            "default-src 'self'",
            "script-src 'self' https://player.live-video.net 'unsafe-inline' 'unsafe-eval' blob:",
            "worker-src 'self' blob:",
            "connect-src 'self' https://*.live-video.net https://*.amazonaws.com blob: data:",
            "media-src 'self' https://*.live-video.net https://*.amazonaws.com blob:",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https://*.live-video.net",
            "frame-ancestors 'self'"
        ]

        response['Content-Security-Policy'] = "; ".join(csp_parts)
        
        response['X-Content-Type-Options'] = 'nosniff'

        if "X-Frame-Options" in response:
            del response["X-Frame-Options"]

        return response
