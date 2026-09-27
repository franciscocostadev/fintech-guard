"""Casos de referência independentes para as definições do passo 3."""
import unittest

from scripts.security_features import extract_features


class SecurityFeaturesTests(unittest.TestCase):
    def test_manual_reference(self):
        self.assertEqual(extract_features('ABC def 12!!'), {
            'n_chars': 12, 'n_words': 2, 'mean_word_length': 3.0,
            'digit_ratio': 2 / 12, 'uppercase_ratio': 0.5,
            'n_links': 0, 'n_exclamations': 2,
        })

    def test_empty_and_no_letters(self):
        self.assertTrue(all(value == 0 for value in extract_features('').values()))
        features = extract_features('123 !!')
        self.assertEqual(features['n_words'], 0)
        self.assertEqual(features['mean_word_length'], 0)
        self.assertEqual(features['uppercase_ratio'], 0)
        self.assertEqual(features['digit_ratio'], 0.5)

    def test_tokenization(self):
        features = extract_features("Don't bank-account 42 café")
        self.assertEqual(features['n_words'], 4)
        self.assertEqual(features['mean_word_length'], 19 / 4)

    def test_links_excluded_from_words_but_not_characters(self):
        text = 'GO https://example.org/12 www.example.org!'
        features = extract_features(text)
        self.assertEqual(features['n_links'], 2)
        self.assertEqual(features['n_words'], 1)
        self.assertEqual(features['mean_word_length'], 2)
        self.assertEqual(features['n_chars'], len(text))
        self.assertEqual(features['digit_ratio'], 2 / len(text))
        self.assertEqual(features['n_exclamations'], 1)
        self.assertEqual(extract_features('HTTPS://a.test HTTPS://a.test')['n_links'], 2)

    def test_link_detection_limits(self):
        self.assertEqual(extract_features('example.org hxxp://a[.]test me@www.site')['n_links'], 0)

    def test_unicode_and_invalid_inputs(self):
        features = extract_features('Áb ١２!！')
        self.assertEqual(features['uppercase_ratio'], 0.5)
        self.assertEqual(features['digit_ratio'], 2 / 7)
        self.assertEqual(features['n_exclamations'], 1)
        for value in (None, float('nan'), 123):
            with self.assertRaises(TypeError):
                extract_features(value)


if __name__ == '__main__':
    unittest.main()
