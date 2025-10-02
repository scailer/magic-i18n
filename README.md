[![Version][version-image]][pypi-url]
[![Supported Python Version][py-versions-image]][pypi-url]
[![Downloads][downloads-image]][pypi-url]
[![Build Status][build-image]][build-url]

---

# Magic-i18n

Internationalization with special contextvars magic.


Key features:

- Relies on a mechanism of implicit context passing for asynchronous functions.
- Supports template formatting via %.
- Texts are defined separately from their usage location and passed as variables.
- Supports temporary (local) language overrides.
- Can be used both standalone and within ASGI applications.


Provides:

- container for text/template variations,
- language context manager,
- middleware for ASGI-compatible frameworks.


## Install

```sh
pip install magic-i18n
```


## Declaration and basic usage

```python
from magic_i18n import Text, set_default_language, language

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

Template in different languages

```python
message = Text(en='hello ${name}', ru='привет ${name}')

print(message % 'Alex')  
print(message % ('Alex',))  
print(message % {'name': 'Alex'})  
# all prints `привет Alex` (ru - default language)
```

Context manager for temporarily changing the current language.

```python
with language('ru'):
    print(message % name)

with language(language) as lang:
    log.debug('Send with language %s', lang)
    print(message % name)
```


## LazyTemplate

LazyTemplate enables partial formatting and deferred evaluation.

Separate declaration

```python
from magic_i18n import LazyTemplate

lazy_template = LazyTemplate('привет ${name}, открой ${target}')
```

Get LazyTemplate from Text container

```python
message = Text(en='hello ${name}, open ${target}', ru='привет ${name}, открой ${target}')

lazy_template = message | 'en'
```

Usage

```python
print(lazy_template)
# print `привет ${name}, открой ${target}`

lazy_template % 'Alex'
print(lazy_template)
# print `привет Alex, открой ${target}`

lazy_template % 'Telegram'
print(lazy_template)
# print `привет Alex, открой Telegram`

lazy_template % {'target': 'Site'}  # set or replace
print(lazy_template)
# print `привет Alex, открой Site`

lazy_template(target='Calc')  # set or replace
print(lazy_template)
# print `привет Alex, открой Calc`
```


## ASGI middleware
The ASGI middleware retrieves the language from the `Accept-Language` header 
and sets it as the current language if it's present in the `accept_languages` option.

Options:
- `application` - wrapped ASGI application.
- `default_language` - (default: en) Used when the user's language is unknown or 
    unavailable. This is the default only for ASGI and does not call `set_default_language`.
- `accept_languages` - list of available languages. The `default_language` must be included 
    in this list.

```python
application = I18nMiddleware(
    application,
    default_language='en',
    accept_languages=['en', 'ru'],
)
```

The header parser pattern `r'([a-zA-Z]{2}[-a-zA-Z0-9]*)'` can be modified in 
`header_parser` class attribute.

```python
I18nMiddleware.header_parser = re.compile(...)
```


<!-- Badges -->
[pypi-url]: https://pypi.org/project/magic-i18n
[version-image]: https://img.shields.io/pypi/v/magic-i18n.svg
[py-versions-image]: https://img.shields.io/pypi/pyversions/magic-i18n.svg
[downloads-image]: https://img.shields.io/pypi/dm/magic-i18n.svg
[build-url]: https://github.com/scailer/magic-i18n/actions
[build-image]: https://github.com/scailer/magic-i18n/workflows/Tests/badge.svg
