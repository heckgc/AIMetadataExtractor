from main import app
import unittest
import sys
import os
from io import BytesIO

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_request(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_post_request_with_valid_image(self):
        with open('tests/test_image.png', 'rb') as img:
            img_data = img.read()
        response = self.app.post('/', content_type='multipart/form-data', data={
            'file': (BytesIO(img_data), 'tests/test_image.png')
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('image_info', response.json)
        image_info = response.json['image_info']
        # Check for transformed keys if EXIF/UserComment exists
        if "Positive Prompt" in image_info or "Negative prompt" in image_info:
            self.assertIn('Positive Prompt', image_info)
            self.assertIn('Negative prompt', image_info)
        # Always check that image_info is a dict
        self.assertIsInstance(image_info, dict)

    def test_post_request_with_invalid_file(self):
        response = self.app.post('/', content_type='multipart/form-data', data={
            'file': (BytesIO(b'not an image'), 'test.txt')
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.json)


if __name__ == '__main__':
    unittest.main()
