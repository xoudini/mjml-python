import itertools
import typing as t

from ..core import Component, initComponent
from ..core.registry import components
from ..helpers import *
from ..lib import merge_dicts


if t.TYPE_CHECKING:
    from mjml._types import _Attr, _Attrs, _Direction


__all__ = [
    'BodyComponent',
]


class BodyComponent(Component):
    def render(self) -> str:
        raise NotImplementedError(f'{self.__class__.__name__} should override ".render()"')

    # TODO typing: split into _ShorthandAttr?
    def getShorthandAttrValue(self,
                              attribute: "_Attr", direction: "_Direction",
                              attr_with_direction: bool=True) -> int:
        if attr_with_direction:
            mjAttributeDirection = self.getAttribute(f'{attribute}-{direction}')
        else:
            mjAttributeDirection = 0
        mjAttribute = self.getAttribute(attribute)

        if mjAttributeDirection:
            return strip_unit(mjAttributeDirection)
        if not mjAttribute:
            return 0
        return shorthandParser(mjAttribute, direction)

    def getShorthandBorderValue(self, direction: t.Optional["_Direction"]) -> int:
        def _get_partial_border(_direction: "_Direction") -> t.Optional[t.Any]:
            if _direction is None:
                return None

            _attrs: t.Dict["_Direction", "_Attr"] = {
                "bottom": "border-bottom",
                "left": "border-left",
                "right": "border-right",
                "top": "border-top",
            }
            _attr = _attrs[_direction]
            return self.get_attr(_attr)

        partial_border = _get_partial_border(direction)
        border =  self.get_attr("border")
        return borderParser(partial_border or border or '0')

    def getBoxWidths(self) -> t.Dict[str, t.Any]:
        containerWidth = self.context['containerWidth']
        parsedWidth = strip_unit(containerWidth)
        get_padding = lambda d: self.getShorthandAttrValue('padding', d)
        paddings = get_padding('right') + get_padding('left')
        borders = self.getShorthandBorderValue('right') + self.getShorthandBorderValue('left')

        return {
            'totalWidth': parsedWidth,
            'borders'   : borders,
            'paddings'  : paddings,
            'box'       : parsedWidth - paddings - borders,
        }

    # TODO typing: fix with `te.Unpack["_Attrs"]`
    # js: htmlAttributes(attributes)
    def html_attrs(self, **attrs: t.Any) -> str:
        def _to_str(key: str, value: t.Optional[t.Any]) -> t.Optional[str]:
            if key == 'style':
                value = self.styles(value)
            elif key in ['class_', 'for_']:
                key = key[:-1]
                if not value:
                    return None
            if value is None:
                return None
            return f'{key}="{value}"'
        serialized_attrs = itertools.starmap(_to_str, attrs.items())
        return ' '.join(filter(None, serialized_attrs))

    # js: getStyles()
    def get_styles(self) -> t.Dict[str, t.Any]:
        return {}

    # js: styles(styles)
    def styles(self, key: t.Optional[t.Any]=None) -> str:
        _styles: t.Optional[t.Dict[str, t.Any]] = None

        if key and isinstance(key, str):
            _styles_dict = self.get_styles()
            keys = key.split('.')
            _styles = _styles_dict.get(keys[0])
            if len(keys) > 1:
                # TODO typing: fix
                if not _styles:
                    raise RuntimeError()
                _styles = _styles.get(keys[1])
            if _styles and not isinstance(_styles, dict):
                raise ValueError(f'key={key}')
        elif key:
            # predefined dict
            _styles = key

        if not _styles:
            _styles = {}

        def serializer(k: str, v: t.Any) -> t.Optional[str]:
            return f'{k}:{v}' if is_not_empty(v) else None

        style_attr_strs = filter(None, itertools.starmap(serializer, _styles.items()))
        style_str = ';'.join(style_attr_strs)
        return style_str

    # TODO typing: finish rest of type annotations
    def renderChildren(self, childrens=None, props=None,
                       renderer: t.Optional[t.Callable[[Component], str]]=None,
                       attributes=None, rawXML=False) -> str:
        if not props:
            props = {}
        if not renderer:
            renderer = lambda component: component.render()
        if not attributes:
            attributes = {}
        childrens = childrens or self.props.get("children")

        if rawXML:
            # return childrens.map(child => jsonToXML(child)).join('\n')
            raise NotImplementedError
        sibling = len(childrens)

        # code to calculate "nonRawSiblings" seemed too compressed/complicated
        # to me (traded readability for fewer lines of code) so the Python code
        # looks quite a bit different. However the final HTML looks the same
        # so I guess I got it right somehow :-)
        #
        # upstream:
        # const rawComponents = filter(components, c => c.isRawElement())
        # const nonRawSiblings = childrens.filter(
        #  child => !find(rawComponents, c => c.getTagName() === child.tagName),
        #).length
        raw_tag_names = set()
        for tag_name, component_cls in components.items():
            if component_cls.isRawElement():
                raw_tag_names.add(tag_name)
        is_raw_element = lambda c: (c['tagName'] in raw_tag_names)

        _nonRawSiblings = []
        for child in childrens:
            if (child is None) or is_raw_element(child):
                continue
            _nonRawSiblings.append(child)
        nonRawSiblings = len(_nonRawSiblings)

        output = ''
        index = 0
        for children in childrens:
            if children is None:
                # "comment" node
                continue
            child_props = merge_dicts(props, {
                'first': (index == 0),
                'index': index,
                'last': (index+1 == sibling),
                'sibling': sibling,
                'nonRawSiblings': nonRawSiblings,
            })
            initialDatas = merge_dicts(children,{
                'attributes': merge_dicts(attributes, children['attributes']),
                'context': self.getChildContext(),
                'props': child_props,
            })
            initialDatas.pop('tagName')

            component = initComponent(
                name = children['tagName'],
                **initialDatas,
            )
            if component:
                output += renderer(component)
            index += 1
        return output
