from neomodel import StructuredNode, StringProperty


class Language(StructuredNode):
    LANGUAGES = {'Arabic': 'Arabic', 'Burmese': 'Burmese', 'Chinese': 'Chinese', 'English': 'English',
                 'Korean': 'Korean', 'Mandarin': 'Mandarin', 'Nepali': 'Nepali', 'Somali': 'Somali',
                 'Spanish': 'Spanish', 'Sudanese': 'Sudanese'}
    language = StringProperty(required=True, unique_index=True, choices=LANGUAGES)

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
