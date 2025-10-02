from collections.abc import Iterator
from contextlib import contextmanager

from .asgi import I18nMiddleware
from .text import DEFAULT_LANG, LANG, LangType, Text, LazyTemplate, set_default_language

__version__ = '0.1'
__all__ = (
    'DEFAULT_LANG', 'LANG', 'I18nMiddleware', 'Text',
    'LazyTemplate', 'language', 'set_default_language'
)


@contextmanager
def language(lang: LangType) -> Iterator[LangType]:
    '''
        This is a context manager for temporarily changing the current language.

        ```
        with language('ru'):
            send(message % name)

        with language(user.language) as lang:
            log.debug('Send with language %s', lang)
            send(message % name)
        ```
    '''
    origin_lang = LANG.get(DEFAULT_LANG)
    LANG.set(lang)

    yield lang

    LANG.set(origin_lang)
