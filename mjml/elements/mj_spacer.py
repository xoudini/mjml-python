import typing as t

from ._base import BodyComponent


if t.TYPE_CHECKING:
    from mjml._types import _Attrs


__all__ = ['MjSpacer']


class MjSpacer(BodyComponent):
    component_name = 'mj-spacer'

    @classmethod
    def allowed_attrs(cls) -> "_Attrs":
        return {
            'border'                    : 'string',
            'border-bottom'             : 'string',
            'border-left'               : 'string',
            'border-right'              : 'string',
            'border-top'                : 'string',
            'container-background-color': 'color',
            'padding-bottom'            : 'unit(px,%)',
            'padding-left'              : 'unit(px,%)',
            'padding-right'             : 'unit(px,%)',
            'padding-top'               : 'unit(px,%)',
            'padding'                   : 'unit(px,%){1,4}',
            'height'                    : 'unit(px,%)',
        }

    @classmethod
    def default_attrs(cls) -> "_Attrs":
        return {
            'height': '20px',
        }

    def get_styles(self):
        return {
            'div': {
                'height'     : self.getAttribute('height'),
                'line-height': self.getAttribute('height'),
            },
        }

    def render(self):
        html_attrs = self.html_attrs(style='div')
        return f'<div {html_attrs}>&#8202;</div>'
