import json

from neomodel import StructuredNode, StringProperty, IntegerProperty


class Language(StructuredNode):
    """This  class provides the basic mechanism for creating and working with a node representing world languages.

        Typical usage example:

        foo = Language(language='Armenian')
    """

    """An integer representing the id of this language. Each language is assigned a unique id."""
    external_id = IntegerProperty(required=False, unique_index=True)

    """A string representing the name of this language. Each language is unique."""
    language = StringProperty(required=True, unique_index=True)

    @staticmethod
    def options() -> list:
        """A utility function that returns a list of languages stored in the graph database.
        """
        stored_languages = []
        for language in Language.nodes.all():
            stored_languages.append(language.language)
        return stored_languages

    def __eq__(self, other):
        """Provides the mechanism for comparing two objects of type LANGUAGE.

        Two LANGUAGES are equal if they are semantically and alphabetically the same, regardless of letters' cases.

        @param: other object to compare to.
        @return: True if the objects being compared are semantically and alphabetically equal, regardless of letters'
            cases.
        @raise: TypeError if the objects being compared are not LANGUAGE objects.
        """
        if isinstance(other, type(self)):
            return str(self.language).lower() == str(other.language).lower()
        raise TypeError(f'{type(other)} not supported.')

    def __lt__(self, other):
        """Provides the mechanism for comparing two objects of type LANGUAGE.

        A LANGUAGE is less that another if it is alphabetically less than the other, regardless of letters' cases.

        @param: other object to compare to.
        @return: True if this object is alphabetically less than the other, regardless of letters' cases.
        @raise: TypeError if the objects being compared are not LANGUAGE objects.
        """
        if isinstance(other, type(self)):
            return str(self.language).lower() < str(other.language).lower()
        raise TypeError(f'{type(other)} not supported.')

    def __str__(self):
        """Returns a readable format for this language.

        The returned value is capitalized. If the language contains more than one token, each token is capitalized.

        @return: a String representing a readable format for this language.
        """
        tokens = [token.capitalize() for token in str(self.language).split(' ')]
        return '{}'.format(' '.join(tokens))

    def serialize(self):
        """Serializes this language.

        The serializer uses the JavaScript Object Notation, JSON, and serializes this language.

            Format:
                {
                    'id': [INTEGER],
                    'day': [STRING]
                }

        @return: A JSON object representing this LANGUAGE.
        """
        obj = json.dumps({
            'id': self.external_id,
            'language': str(self.language)
        })
        return obj

    @classmethod
    def category(cls):
        pass
