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

    def test_language_valid_choices(self):
        languages = ['english', 'spanish', 'mandarin', 'chinese', 'arabic', 'sudanese',
                     'EnGlisH', 'spaNish', 'manDARin', 'CHinese', 'araBIC', 'Sudanese']
        [self.assertTrue(language.capitalize() in Language.options()) for language in languages]

    def test_language_invalid_choices(self):
        languages = ['language1', 'language2', 'language3', 'italian', 'portuguese']
        [self.assertFalse(language.capitalize() in Language.options()) for language in languages]

    def test_language_new_language(self):
        with self.assertRaises(DeflateError):
            language = Language(language='Hindi').save()

    def test_language_handling_new_language(self):
        language_names = ['Hindi', 'Malagasy']
        for language_name in language_names:
            if language_name in Language.options():
                language = Language(language=language_name)
            else:
                Language.add_languages(language_name)
                language = Language(language=language_name)

            self.assertEqual(language, Language(language=language_name))


if __name__ == '__main__':
    unittest.main()
