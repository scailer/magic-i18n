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

# Template in different languages
message = Text(en='hello ${name}', ru='привет ${name}')

# print `привет Alex` (ru - default language)
print(message % 'Alex')  
print(message % ('Alex',))  
print(message % {'name': 'Alex'})  

# temporarily changing language
with language('en') as lang:
    # print `hello Alex` (en - temporal language)
    print(f'LANG={lang}', message % 'Alex') 
