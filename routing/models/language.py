from neomodel import StructuredNode, StringProperty, ArrayProperty


class Language(StructuredNode):
    LANGUAGES = {'Arabic': 'Arabic', 'Burmese': 'Burmese', 'Chinese': 'Chinese', 'English': 'English',
                 'Korean': 'Korean', 'Mandarin': 'Mandarin', 'Nepali': 'Nepali', 'Somali': 'Somali',
                 'Spanish': 'Spanish', 'Sudanese': 'Sudanese'}
    language = StringProperty(required=True, unique_index=True, choices=LANGUAGES)
