# forms.py
from django import forms
from pretix.base.forms import SettingsForm
from pretix.base.models import Item
from i18nfield.forms import I18nFormField, I18nTextInput, I18nTextarea
from django.utils.translation import gettext_lazy as _

class IvsSettingsForm(SettingsForm):
    ivs_url = forms.URLField(
        label=_("Stream URL"),
        required=False,
    )
    ivs_eligible_products = forms.ModelMultipleChoiceField(
        label=_("Eligible Products"),
        help_text=_("Only users with these ticket types will see the stream."),
        queryset=Item.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    ivs_generate_token = forms.BooleanField(
        label=_("Generate Token"),
        required=False
    )
    ivs_private_key = forms.CharField(
        label=_("Private Key"),
        required=False,
        help_text=_("Required to Generate Tokens."),
        widget=forms.PasswordInput()
    )
    ivs_channel_arn = forms.CharField(
        label=_("Channel ARN"),
        help_text=_("Required to Generate Tokens."),
        required=False
    )
    ivs_title = I18nFormField(
        label=_("Title"),
        help_text=_("Title to display on the order page."),
        widget=I18nTextInput,
        required=False
    )
    ivs_content = I18nFormField(
        label=_("Content"),
        help_text=_("Text to be displayed under the video. HTML is allowed."),
        widget=I18nTextarea,
        required=False
    )


    def __init__(self, *args, **kwargs):
        self.event = kwargs.get('obj')
        super().__init__(*args, **kwargs)
        self.fields['ivs_eligible_products'].queryset = self.event.items.all()
        if self.event.settings.ivs_eligible_products:
            self.initial['ivs_eligible_products'] = self.event.items.filter(
                id__in=self.event.settings.get('ivs_eligible_products', as_type=list) or []
            )
        
    def save(self):
        items = self.cleaned_data.get('ivs_eligible_products')
        if items is not None:
            self.cleaned_data['ivs_eligible_products'] = [i.id for i in items]
        
        return super().save()

