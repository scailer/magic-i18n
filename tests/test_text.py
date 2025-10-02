import asyncio
import random

import pytest

from magic_i18n import LANG, Text, LazyTemplate, language, set_default_language


async def test_set_default_language():
    set_default_language('ru')
    set_default_language('en')


async def test_language_ok():
    LANG.set('en')

    assert LANG.get() == 'en'

    with language('ru'):
        assert LANG.get() == 'ru'

        with language('fr'):
            assert LANG.get() == 'fr'

        assert LANG.get() == 'ru'

    assert LANG.get() == 'en'


def test_Text_repr_ok():
    text = Text(en='text', ru='текст')
    assert repr(text) == 'Text(text)'

    text = Text('fallback', en='text', ru='текст')
    assert repr(text) == 'Text(fallback)'

    text = Text('${a} fallback')
    assert repr(text) == 'Text(${a} fallback)'


def test_Text_str_ok():
    text = Text(en='plain text', ru='простой текст')

    with language('en'):
        assert str(text) == 'plain text'
        assert f'Is it {text}?' == 'Is it plain text?'
        assert str(text) + '.' == 'plain text.'
        assert ', '.join([str(text), str(text)]) == 'plain text, plain text'

    with language('ru'):
        assert str(text) == 'простой текст'
        assert f'Это {text}?' == 'Это простой текст?'
        assert str(text) + '.' == 'простой текст.'
        assert ', '.join([str(text), str(text)]) == 'простой текст, простой текст'


def test_Text_str_fail():
    text = Text(en='${a} text', ru='${a} текст')

    with pytest.raises(TypeError) as err:
        str(text)

    assert err.value.args == ('string formatting required', )


def test_Text_mod_ok_one_argument():
    text = Text(en='hello ${name}', ru='привет ${name}')

    with language('en'):
        name, result = 'Alex', 'hello Alex'
        assert text % name == result
        assert text % (name, ) == result
        assert text % {'name': name} == result

    with language('ru'):
        name, result = 'Алек', 'привет Алек'
        assert text % name == result
        assert text % (name, ) == result
        assert text % {'name': name} == result 

    assert text % 1 == 'hello 1'
    assert text % None == 'hello None'
    assert text % True == 'hello True'
    assert text % Text == 'hello <class \'magic_i18n.text.Text\'>'


def test_Text_mod_ok_many_arguments():
    text = Text(
        en='hello ${name}, welcome to ${team}',
        ru='привет ${name}, добро пожаловать в ${team}'
    )

    with language('en'):
        name, team, result = 'Alex', 'DreamTeam', 'hello Alex, welcome to DreamTeam'
        assert text % (name, team) == result
        assert text % {'name': name, 'team': team} == result

    with language('ru'):
        name, team, result = 'Алек', 'КомандаМечты', 'привет Алек, добро пожаловать в КомандаМечты'
        assert text % (name, team) == result
        assert text % {'name': name, 'team': team} == result 


def test_Text_mod_fail_not_enough_arguments():
    text = Text(
        en='hello ${name}, welcome to ${team}',
        ru='привет ${name}, добро пожаловать в ${team}'
    )

    with pytest.raises(TypeError) as err:
        text % ('Alex', )

    assert err.value.args == ('not enough arguments for format string', )

    with pytest.raises(TypeError) as err:
        text % 'Alex'

    assert err.value.args == ('not enough arguments for format string', )


def test_Text_mod_fail_not_all_arguments_converted():
    text = Text(
        en='hello ${name}, welcome to ${team}',
        ru='привет ${name}, добро пожаловать в ${team}'
    )

    with pytest.raises(TypeError) as err:
        text % ('Alex', 'Team', 'Q')

    assert err.value.args == ('not all arguments converted during string formatting', )


def test_Text_mod_fail_formatting_not_required():
    text = Text(en='hello', ru='привет')

    with pytest.raises(TypeError) as err:
        text % 'Alex'

    assert err.value.args == ('formatting not required', )


def test_Text_call_ok():
    text = Text(en='hello ${name}', ru='привет ${name}')

    with language('en'):
        name, result = 'Alex', 'hello Alex'
        assert text(name=name) == result

    with language('ru'):
        name, result = 'Алек', 'привет Алек'
        assert text(name=name) == result


def test_Text_template_setter_fail():
    text = Text(en='hello ${name}', ru='привет ${name}')

    with pytest.raises(TypeError) as err:
        text.template = ''

    assert err.value.args == ('template is read-only', )


async def test_Text_str_ok_async():
    text = Text(en='plain text', ru='простой текст')

    async def _func(lang) -> str:
        await asyncio.sleep(.0001)

        with language(lang):
            return str(text)

    langs = [random.choice(['ru', 'en']) for x in range(1_000)]
    results = await asyncio.gather(*[_func(lang) for lang in langs])

    for lang, val in zip(langs, results):
        assert text.translations.get(lang) == val

def test_Text_or_ok():
    text = Text(en='hello ${name}', ru='привет ${name}')
    lazy_template = text | 'ru'

    assert isinstance(lazy_template, LazyTemplate)
    assert lazy_template.template == text.translations['ru']


def test_LazyTemplate_str_ok():
    assert str(LazyTemplate('hello')) == 'hello'
    assert str(LazyTemplate('hello ${name}')) == 'hello ${name}'


def test_LazyTemplate_mod_ok_simple():
    assert str(LazyTemplate('hello') % 'Alex') == 'hello'
    assert str(LazyTemplate('hello') % ('Alex', 'else')) == 'hello'
    assert str(LazyTemplate('hello') % {'name': 'Alex', 'a': 'else'}) == 'hello'

def test_LazyTemplate_mod_ok_one_argument():
    assert str(LazyTemplate('hello ${name}') % 'Alex') == 'hello Alex'
    assert str(LazyTemplate('hello ${name}') % {'name': 'Alex'}) == 'hello Alex'
    assert str(LazyTemplate('hello ${name}') % ('Alex', 'other')) == 'hello Alex'
    assert str(LazyTemplate('hello ${name}') % {'name': 'Alex', 'a': 'other'}) == 'hello Alex'

def test_LazyTemplate_mod_ok_partial():
    lazy_template = LazyTemplate('hello ${name}, welcome to ${team}, visit ${url}')
    assert str(lazy_template) == 'hello ${name}, welcome to ${team}, visit ${url}'

    lazy_template % 'Alex'
    assert str(lazy_template) == 'hello Alex, welcome to ${team}, visit ${url}'

    lazy_template % ('Team', 'URL')
    assert str(lazy_template) == 'hello Alex, welcome to Team, visit URL'

    lazy_template % {'team': 'MyTeam'}
    assert str(lazy_template) == 'hello Alex, welcome to MyTeam, visit URL'
