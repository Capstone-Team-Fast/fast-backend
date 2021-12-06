import json

from neomodel import StructuredNode, StringProperty, IntegerProperty


class Language(StructuredNode):
    __LANGUAGES = {'Afrikaans': 'Afrikaans', 'Albanian': 'Albanian', 'Amharic': 'Amharic', 'Arabic': 'Arabic',
                   'Armenian': 'Armenian', 'Assamese': 'Assamese', 'Aymara': 'Aymara', 'Azeri': 'Azeri',
                   'Belarusian': 'Belarusian', 'Bengali': 'Bengali', 'Bislama': 'Bislama', 'Bosnian': 'Bosnian',
                   'Bulgarian': 'Bulgarian', 'Burmese': 'Burmese', 'Catalan': 'Catalan', 'Chinese': 'Chinese',
                   'Croatian': 'Croatian', 'Czech': 'Czech', 'Danish': 'Danish', 'Dari': 'Dari', 'Dhivehi': 'Dhivehi',
                   'Dutch': 'Dutch', 'Dzongkha': 'Dzongkha', 'English': 'English', 'Estonian': 'Estonian',
                   'Fijian': 'Fijian', 'Filipino': 'Filipino', 'Finnish': 'Finnish', 'French': 'French',
                   'Gagauz': 'Gagauz', 'Georgian': 'Georgian', 'German': 'German', 'Greek': 'Greek',
                   'Gujarati': 'Gujarati', 'Haitian Creole': 'Haitian Creole', 'Hebrew': 'Hebrew', 'Hindi': 'Hindi',
                   'Hiri Motu': 'Hiri Motu', 'Hungarian': 'Hungarian', 'Icelandic': 'Icelandic',
                   'Indonesian': 'Indonesian', 'Irish Gaelic': 'Irish Gaelic', 'Italian': 'Italian',
                   'Japanese': 'Japanese', 'Kannada': 'Kannada', 'Kashmiri': 'Kashmiri', 'Kazakh': 'Kazakh',
                   'Khmer': 'Khmer', 'Korean': 'Korean', 'Kurdish': 'Kurdish', 'Kyrgyz': 'Kyrgyz',
                   'Lao': 'Lao', 'Latvian': 'Latvian', 'Lithuanian': 'Lithuanian', 'Luxembourgish': 'Luxembourgish',
                   'Macedonian': 'Macedonian', 'Malagasy': 'Malagasy', 'Malay': 'Malay', 'Malayalam': 'Malayalam',
                   'Maltese': 'Maltese', 'Mandarin': 'Mandarin', 'Marathi': 'Marathi', 'Moldovan': 'Moldovan',
                   'Mongolian': 'Mongolian', 'Montenegrin': 'Montenegrin', 'Ndebele': 'Ndebele', 'Nepali': 'Nepali',
                   'New Zealand Sign Language': 'New Zealand Sign Language', 'Northern Sotho': 'Northern Sotho',
                   'Norwegian': 'Norwegian', 'Oriya': 'Oriya', 'Papiamento': 'Papiamento', 'Pashto': 'Pashto',
                   'Persian': 'Persian', 'Polish': 'Polish', 'Portuguese': 'Portuguese', 'Punjabi': 'Punjabi',
                   'Quechua': 'Quechua', 'Romanian': 'Romanian', 'Russian': 'Russian', 'Somali': 'Somali',
                   'Sotho': 'Sotho', 'Spanish': 'Spanish', 'Sudanese': 'Sudanese', 'Swahili': 'Swahili',
                   'Swati': 'Swati', 'Swedish': 'Swedish', 'Tajik': 'Tajik', 'Tamil': 'Tamil', 'Telugu': 'Telugu',
                   'Tetum': 'Tetum', 'Thai': 'Thai', 'Tok Pisin': 'Tok Pisin', 'Tsonga': 'Tsonga', 'Tswana': 'Tswana',
                   'West Frisian': 'West Frisian', 'Yiddish': 'Yiddish', 'Zulu': 'Zulu'}

    external_id = IntegerProperty(required=False, unique_index=True)
    language = StringProperty(required=True, unique_index=True, choices=__LANGUAGES)

    @staticmethod
    def options() -> list:
        return list(Language.__LANGUAGES.keys())

    @staticmethod
    def add_languages(language: str):
        if language not in Language.__LANGUAGES:
            Language.__LANGUAGES[language.capitalize()] = language.capitalize()

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return str(self.language).lower() == str(other.language).lower()
        raise TypeError(f'{type(other)} not supported.')

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return str(self.language).lower() < str(other.language).lower()
        raise TypeError(f'{type(other)} not supported.')

    def __str__(self):
        return '{}'.format(str(self.language).capitalize())

    def serialize(self):
        obj = json.dumps({
            'id': self.external_id,
            'language': str(self.language)
        })
        return obj

    @classmethod
    def category(cls):
        pass
