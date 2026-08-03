import unittest
import sys
import os
from io import BytesIO
import json
from unittest.mock import MagicMock, patch

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))

from main import app
import main


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

    def test_transform_image_info_without_user_comment(self):
        metadata = {'Artist': 'Example'}
        result = main.transform_image_info(metadata)
        self.assertEqual(result['Artist'], 'Example')

    @patch('main.subprocess.run')
    def test_post_request_with_valid_video(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = json.dumps({
            'format': {
                'format_name': 'mov,mp4,m4a,3gp,3g2,mj2',
                'format_long_name': 'QuickTime / MOV',
                'duration': '1.0',
                'size': '1024',
                'bit_rate': '8192',
                'tags': {'encoder': 'Lavf'}
            },
            'streams': [
                {
                    'codec_type': 'video',
                    'codec_name': 'h264',
                    'codec_long_name': 'H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10',
                    'width': 1920,
                    'height': 1080,
                    'pix_fmt': 'yuv420p',
                    'r_frame_rate': '30/1',
                    'avg_frame_rate': '30/1',
                    'bit_rate': '7000',
                    'nb_frames': '30'
                }
            ]
        })
        mock_run.return_value = mock_result

        response = self.app.post('/', content_type='multipart/form-data', data={
            'file': (BytesIO(b'fake video bytes'), 'sample.mp4', 'video/mp4')
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['media_kind'], 'video')
        self.assertIn('image_info', response.json)
        self.assertEqual(response.json['image_info']['container'], 'mov,mp4,m4a,3gp,3g2,mj2')


if __name__ == '__main__':
    unittest.main()
