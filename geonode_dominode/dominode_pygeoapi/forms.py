import datetime as dt
import typing

from django import forms
from django.utils.translation import gettext_lazy as _


class GeojsonField(forms.CharField):

    def validate(self, value: str) -> typing.Dict:
        # TODO: convert input to GeoJSON
        return value


class BboxField(forms.MultiValueField):

    def __init__(self, **kwargs):
        fields = (
            forms.FloatField(help_text='lower left corner, coordinate axis 1'),
            forms.FloatField(help_text='lower left corner, coordinate axis 2'),
            forms.FloatField(
                required=False,
                help_text='minimum value, coordinate axis 3'
            ),
            forms.FloatField(help_text='upper right corner, coordinate axis 1'),
            forms.FloatField(help_text='upper right corner, coordinate axis 2'),
            forms.FloatField(
                required=False,
                help_text='maximum value, coordinate axis 3'
            ),
        )
        super().__init__(fields=fields, require_all_fields=False, **kwargs)

    def compress(self, data_list):
        # TODO: return a geojson polygon
        return data_list


class StringListField(forms.CharField):

    def __init__(self, separator: typing.Optional[str] = ',', **kwargs):
        super().__init__(**kwargs)
        self.separator = separator

    def validate(self, value: str) -> typing.List[str]:
        return [i.strip() for i in value.split(self.separator)]


class StacDatetimeField(forms.Field):

    def validate(
            self,
            value: str
    ) -> typing.List[typing.Union[str, dt.datetime]]:
        # can either be a single datetime, a closed interval or an open interval
        open_side = '..'
        parts = value.split('/')
        result = []
        if len(parts) == 1:
            # a single value
            # FIXME: guard this with a try block
            result.append(dt.datetime.fromisoformat(parts[0]))
        elif len(parts) == 2:
            start, end = parts
            if start == open_side and end == open_side:
                raise forms.ValidationError(
                    _('Interval cannot be open on both sides'),
                    code='invalid',
                )
            elif start == open_side:
                result.append(start)
            else:
                result.append(dt.datetime.fromisoformat(start))
            if end == open_side:
                result.append(end)
            else:
                result.append(dt.datetime.fromisoformat(end))
        else:
            raise forms.ValidationError(
                _('Invalid datetime format'),
                code='invalid'
            )
        return result


class StacSearchSimpleForm(forms.Form):
    bbox = BboxField(required=False)
    bbox_crs = forms.CharField(label='bbox-crs', required=False)
    datetime_ = StacDatetimeField(label='datetime', required=False)
    limit = forms.IntegerField(
        min_value=1,
        max_value=10000,
        initial=10,
        required=False
    )
    ids = StringListField(required=False)
    collections = StringListField(required=False)


class StacSearchCompleteForm(StacSearchSimpleForm):
    intersects = GeojsonField(required=False)