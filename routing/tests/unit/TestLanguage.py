import json
import unittest

from neomodel import config, db, DeflateError

from backend import settings
from routing.models.language import Language


class MyTestCase(unittest.TestCase):
    config.DATABASE_URL = settings.NEOMODEL_NEO4J_BOLT_URL
    db.set_connection(url=config.DATABASE_URL)

    def test_serializer(self):
        language = Language(language='English').save()
        expected_result = json.dumps({
            'id': None,
            'language': 'English'
        })
        self.assertEqual(language.serialize(), expected_result)
        language.delete()

    def test_language_handling_new_language(self):
        language_names = ['Hindi', 'Malagasy']
        for language_name in language_names:
            if language_name in Language.options():
                language = Language(language=language_name)
            else:
                language_name = ' '.join([token.capitalize() for token in language_name.split(' ')])
                language = Language(language=language_name)

            self.assertEqual(language, Language(language=language_name))


if __name__ == '__main__':
    unittest.main()
