from contextvars import ContextVar
from string import Template
from typing import Any, TypeAlias

LangType: TypeAlias = str
DEFAULT_LANG: LangType = 'en'
LANG: ContextVar[LangType] = ContextVar('lang')


def set_default_language(lang: LangType) -> None:
    ''' Global set default language '''
    global DEFAULT_LANG
    DEFAULT_LANG = lang


class Text(Template):
    '''
        Text class serves as a container for representing text in different languages.
        It automatically selects the appropriate language based on the current context.
        If a suitable translation isn't found, a fallback value or the default language
        is returned. For simple usage, the class behaves like a regular string, 
        but it also allows for field replacement using a template with the operator.

        Declaration examples:

        ```
            from magic_i18n import Text, set_default_language

            # setup global default language, must be called before running application
            set_default_language('ru')

            # Basic init without translations, fallback only
            message = Text('text')
            print(message)  # print `text`

            # Text in different languages, with default language for non-defined languages
            message = Text(en='text', ru='текст')
            print(message)  # print `текст` (ru - default language)

            # Text in different languages, with fallback for non-defined languages
            message = Text('fail', en='text', ru='текст')
            print(message)  # print `текст` (ru - default language)
        ```

        For template strings, it behaves like a string requiring formatting via %.

        ```
            # Template in different languages
            message = Text(en='hello ${name}', ru='привет ${name}')

            # print `текст` (ru - default language)
            print(message % 'Alex')  
            print(message % ('Alex',))  
            print(message % {'name': 'Alex'})  
        ```
    '''

    fallback: str
    translations: dict[LangType, str]

    @property
    def template(self) -> str:
        return self.translations.get(LANG.get(DEFAULT_LANG), self.fallback)

    @template.setter
    def template(self, value: str) -> None:
        raise TypeError('template is read-only')

    def __init__(self, fallback: str = '', **translations: str) -> None:
        self.fallback = fallback or translations.get(DEFAULT_LANG, '<no-translation>')
        self.translations = translations

    def __repr__(self) -> str:
        return f'Text({self.fallback})'

    def __str__(self) -> str:
        if self.get_identifiers():
            raise TypeError('string formatting required')

        return self.template

    def __call__(self, **data: Any) -> str:
        return self.substitute(**data)

    def __mod__(self, data: Any) -> str:  # noqa ANN401
        ''' Strict formatting '''
        match data:
            case dict():
                return self(**data)

            case tuple() | list() | set():
                ids = self.get_identifiers()

                if len(ids) > len(data):
                    raise TypeError('not enough arguments for format string')

                if len(ids) < len(data):
                    raise TypeError('not all arguments converted during string formatting')

                _data = dict(zip(self.get_identifiers(), data, strict=True))
                return self(**_data)

            case _:
                ids = self.get_identifiers()

                if not ids:
                    raise TypeError('formatting not required')

                if len(ids) > 1:
                    raise TypeError('not enough arguments for format string')

                return self(**{ids[0]: data})

    def __or__(self, lang: LangType) -> 'LazyTemplate':
        ''' Get LazyTemplate by specified language '''
        return LazyTemplate(self.translations.get(lang, self.fallback))


class LazyTemplate(Template):
    '''
        LazyTemplate enables partial formatting and safe deferred evaluation.
    '''
    args: dict[str, str]

    def __init__(self, template: str) -> None:
        super().__init__(template)
        self.args = {}

    def __str__(self) -> str:
        return self.safe_substitute(**self.args)

    def __call__(self, **data: Any) -> 'LazyTemplate':
        self.args.update({name: str(value) for name, value in data.items()})
        return self

    def __mod__(self, data: Any) -> 'LazyTemplate':
        ''' Partial formatting '''

        _data: dict = {}
        ids = [_id for _id in self.get_identifiers() if _id not in self.args]

        match data:
            case dict():
                _data = data
            case tuple() | list() | set():
                if ids:
                    _data = dict(zip(ids, data, strict=False))
            case _:
                if ids:
                    _data = {ids[0]: data}

        return self(**_data)
