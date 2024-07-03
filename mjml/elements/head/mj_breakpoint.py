import typing as t

import typing_extensions as te

from ._head_base import HeadComponent


if t.TYPE_CHECKING:
    from mjml._types import _Attrs


__all__ = ['MjBreakpoint']


class MjBreakpoint(HeadComponent):
    component_name: t.ClassVar[str] = 'mj-breakpoint'

    @te.override
    @classmethod
    def allowed_attrs(cls) -> "_Attrs":
        return {
            'width': 'unit(px)',
        }

    @te.override
    def handler(self) -> None:
        add = self.context['add']
        add('breakpoint', self.getAttribute('width'))
