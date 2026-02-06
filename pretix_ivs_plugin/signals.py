import jwt
from django.dispatch import receiver
from django.template.loader import get_template
from pretix.presale.signals import order_info_top
from pretix.control.signals import nav_event_settings
from pretix.base.models import Checkin
from django.urls import resolve,reverse
from django.utils.translation import gettext_lazy as _,get_language
from i18nfield.strings import LazyI18nString

def _generate_ivs_token(event):
    private_key = event.settings.get('ivs_private_key')
    payload = {
        'channel-arn': event.settings.get('ivs_channel_arn')
    }
    return jwt.encode(payload, private_key, algorithm="ES384")

@receiver(nav_event_settings, dispatch_uid='ivs_nav_settings')
def navbar_settings(sender, request, **kwargs):
    url = resolve(request.path_info)
    return [{
        'label': _('AWS IVS Streaming'),
        'url': reverse('plugins:pretix_ivs_plugin:settings', kwargs={
            'organizer': sender.organizer.slug,
            'event': sender.slug
        }),
        'active': url.namespace == 'plugins:pretix_ivs_plugin' and url.url_name == 'settings',
    }]

@receiver(order_info_top)
def s_order_info(sender, order, **kwargs):
    allowed_product_ids = sender.settings.get('ivs_eligible_products', as_type=list) or []
    has_eligible_ticket = order.positions.filter(item_id__in=allowed_product_ids).exists()
    if not has_eligible_ticket:
        return '' # Hide the whole widget if they don't have the right ticket

    request = kwargs.get('request')

    ivs_url = sender.settings.get('ivs_url')
    gen_token = sender.settings.get('ivs_generate_token', as_type=bool, default=False)
    is_checked_in = Checkin.objects.filter(
        position__order=order,
        list__name='Online Stream'
    ).exists()

    # If there is no URL, don't show the player at all
    if not ivs_url:
        return ''
    elif gen_token and is_checked_in:
        ivs_url += '?token=' + _generate_ivs_token(sender)


    context = {
        'title': LazyI18nString(sender.settings.get('ivs_title')),
        'content': LazyI18nString(sender.settings.get('ivs_content')).localize(get_language()),
        'is_checked_in': is_checked_in,
        'checkin_url': f"ivs_checkin/",
        'url': ivs_url,
    }
    if gen_token and is_checked_in:
        context['jwt'] = _generate_ivs_token(sender)
    # Check Access Policy
    # if settings.ivs_only_paid and order.status != 'p':
        # return ""

    template = get_template('pretix_ivs_plugin/order_info.html')
    return template.render(context, request=request)

