from neomodel import StructuredNode, StringProperty, ArrayProperty


class Language(StructuredNode):
    LANGUAGES = {'English': 'English'}
    language = StringProperty(required=True, unique_index=True, choices=LANGUAGES)
