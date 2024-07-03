import typing as t


__all__ = ['suffixCssClasses']


def suffixCssClasses(classes: t.Optional[str], suffix: str) -> str:
    if classes is None or not (stripped := classes.strip()):
        return ""

    _classes = stripped.split(' ')
    suffixed = map(lambda _class: f'{_class}-{suffix}', _classes)
    return ' '.join(suffixed)
