import typing as t

import typing_extensions as te

from ._head_base import HeadComponent


if t.TYPE_CHECKING:
    from mjml._types import _Attrs


__all__ = ['MjFont']


class MjFont(HeadComponent):
    component_name: t.ClassVar[str] = 'mj-font'

    @te.override
    @classmethod
    def allowed_attrs(cls) -> "_Attrs":
        return {
            'href'            : 'string',
            'name'            : 'string',
        }

    @te.override
    def handler(self) -> None:
        add = self.context['add']
        add('fonts', self.getAttribute('name'), self.getAttribute('href'))
