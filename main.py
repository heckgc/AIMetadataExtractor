import logging
import base64
import mimetypes
import os
import re
import subprocess
import tempfile
from pathlib import Path
from flask import Flask, request, render_template, jsonify
from PIL import Image, ExifTags
import io
import json

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'No file uploaded.'})

        try:
            logging.debug("Received file: %s", file.filename)

            file_data = file.read()
            logging.debug("Read %d bytes from the uploaded file.", len(file_data))

            if not file_data:
                return jsonify({'error': 'Uploaded file is empty.'})

            preview_data = base64.b64encode(file_data).decode('utf-8')
            media_kind = None
            mime_type = file.content_type or mimetypes.guess_type(file.filename)[0]

            try:
                img = Image.open(io.BytesIO(file_data))
                logging.debug(
                    "Image opened successfully: format=%s, size=%s, mode=%s", img.format, img.size, img.mode)
                image_info = extract_image_metadata(img)
                media_kind = 'image'
                mime_type = Image.MIME.get(img.format, mime_type or 'image/*')
            except Exception as image_error:
                logging.debug("Image parsing failed, trying video metadata: %s", str(image_error))
                image_info = extract_video_metadata(file_data, file.filename)
                media_kind = 'video'
                mime_type = mime_type or 'video/mp4'

            if isinstance(image_info, dict) and image_info.get('error'):
                return jsonify({'error': image_info['error']})

            response = {
                'image_info': image_info,
                'mime_type': mime_type,
                'media_kind': media_kind,
                'file_data': preview_data,
            }
            return jsonify(response)

        except Exception as e:
            logging.error("An error occurred: %s", str(e))
            return jsonify({'error': str(e)})

    # Show the form to upload an image on the first load
    return render_template('index.html')


def transform_image_info(image_info):
    if not isinstance(image_info, dict):
        return {}

    # Extract the UserComment field
    user_comment = image_info.pop("UserComment", None)

    if not user_comment:
        return image_info

    # Parse the UserComment into a structured JSON object
    parsed_comment = parse_user_comment(user_comment)

    # Merge the parsed UserComment back into the image_info dictionary
    if parsed_comment:
        image_info.update(parsed_comment)

    return image_info


def sanitize_metadata(value):
    if isinstance(value, dict):
        return {str(key): sanitize_metadata(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [sanitize_metadata(item) for item in value]

    if isinstance(value, bytes):
        return decode_exif(value)

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


def extract_image_metadata(image: Image.Image):
    logging.debug("Reading image metadata.")
    image_info = sanitize_metadata(getattr(image, "info", {}))

    if hasattr(image, "getexif"):
        exif_data = image.getexif()
        if exif_data:
            exif_info = {}
            for tag, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag, f"Unknown Tag ({tag})")
                exif_info[tag_name] = sanitize_metadata(value)
            image_info.update(transform_image_info(exif_info))

    return image_info


def extract_video_metadata(file_data, filename):
    suffix = Path(filename).suffix or '.mp4'
    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file.write(file_data)
            temp_file_path = temp_file.name

        probe = subprocess.run(
            [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                temp_file_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        probe_data = json.loads(probe.stdout or '{}')
        format_info = probe_data.get('format', {})
        streams = probe_data.get('streams', [])
        video_stream = next((stream for stream in streams if stream.get('codec_type') == 'video'), {})
        audio_stream = next((stream for stream in streams if stream.get('codec_type') == 'audio'), {})

        metadata = {
            'file_name': filename,
            'container': format_info.get('format_name'),
            'container_long_name': format_info.get('format_long_name'),
            'duration': format_info.get('duration'),
            'size': format_info.get('size'),
            'bit_rate': format_info.get('bit_rate'),
            'tags': sanitize_metadata(format_info.get('tags', {})),
            'streams': sanitize_metadata(streams),
        }

        if video_stream:
            metadata['video_stream'] = sanitize_metadata({
                'codec_name': video_stream.get('codec_name'),
                'codec_long_name': video_stream.get('codec_long_name'),
                'width': video_stream.get('width'),
                'height': video_stream.get('height'),
                'pix_fmt': video_stream.get('pix_fmt'),
                'r_frame_rate': video_stream.get('r_frame_rate'),
                'avg_frame_rate': video_stream.get('avg_frame_rate'),
                'bit_rate': video_stream.get('bit_rate'),
                'nb_frames': video_stream.get('nb_frames'),
            })

        if audio_stream:
            metadata['audio_stream'] = sanitize_metadata({
                'codec_name': audio_stream.get('codec_name'),
                'codec_long_name': audio_stream.get('codec_long_name'),
                'channels': audio_stream.get('channels'),
                'channel_layout': audio_stream.get('channel_layout'),
                'sample_rate': audio_stream.get('sample_rate'),
                'bit_rate': audio_stream.get('bit_rate'),
            })

        return metadata

    except FileNotFoundError:
        logging.error('ffprobe is not available on this system.')
        return {'error': 'ffprobe is not available on this system.'}
    except subprocess.CalledProcessError as exc:
        logging.error('Failed to read video metadata: %s', exc.stderr or str(exc))
        return {'error': f'Failed to read video metadata: {exc.stderr or str(exc)}'}
    except json.JSONDecodeError as exc:
        logging.error('Failed to decode ffprobe output: %s', str(exc))
        return {'error': f'Failed to decode video metadata: {str(exc)}'}
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


def parse_user_comment(user_comment):
    """
    Parse the UserComment field into a structured JSON object.
    """
    try:
        # Split the string into lines and remove empty lines
        lines = [line.strip()
                 for line in user_comment.split("\n") if line.strip()]

        # Initialize the result dictionary
        result = {"Positive Prompt": None, "Negative prompt": None}

        # Iterate through the lines
        positive_prompt = []
        for line in lines:
            if line.startswith("Negative prompt:"):
                # Extract the negative prompt
                result["Negative prompt"] = line.split(
                    "Negative prompt:")[1].strip()
            elif line.startswith("Civitai resources:"):
                # Extract the entire JSON-like structure for Civitai resources
                resources_match = re.search(r"Civitai resources: (.+)", line)
                if resources_match:
                    resources_json = resources_match.group(1)
                    result["Civitai resources"] = json.loads(resources_json)
            elif ": " in line:
                # Split the line into key and value
                key, value = line.split(": ", 1)
                result[key.strip()] = value.strip()
            else:
                # Treat remaining lines as part of the positive prompt
                positive_prompt.append(line)

        # Join the positive prompt lines into a single string
        result["Positive Prompt"] = " ".join(positive_prompt).strip()

        return result
    except Exception as e:
        print(f"Error parsing UserComment: {e}")
        return None


def check_and_decode_exif(image_data):
    if b'Exif' in image_data:
        logging.debug("Image contains EXIF data.")
        return True
    else:
        logging.debug("Image does not contain EXIF data.")
        return False


def read_exif(image: Image.Image):
    logging.debug("Reading EXIF data from image.")
    # Create a dictionary to store the image data
    image_data = {
        "image_info": {}
    }

    # Extract EXIF data if available
    if hasattr(image, "_getexif") and image._getexif() is not None:
        exif_data = image._getexif()
        for tag, value in exif_data.items():
            tag_name = ExifTags.TAGS.get(tag, f"Unknown Tag ({tag})")
            if isinstance(value, bytes):
                # Decode bytes to a string
                value = decode_exif(value)
            else:
                # Convert non-string values to strings
                value = str(value) if value is not None else "None"
            image_data["image_info"][tag_name] = value
        # logging.debug("EXIF data extracted: %s", image_data["exif_data"])
    else:
        logging.debug("No EXIF data found in the image.")

    return image_data


def decode_exif(exif_data):
    try:
        # Remove null bytes
        cleaned_data = exif_data.replace(b'\x00', b'')  # Remove null bytes

        # Decode as UTF-8
        decoded_data = cleaned_data.decode('utf-8', errors='ignore')

        # Remove the "UNICODE" prefix if it exists
        if decoded_data.startswith("UNICODE"):
            decoded_data = decoded_data[len("UNICODE"):].strip()

        # logging.debug("Decoded EXIF data: %s", decoded_data)
        return decoded_data
    except Exception as e:
        logging.error("Error decoding EXIF data: %s", str(e))
        return "Error decoding EXIF data"


if __name__ == '__main__':
    logging.info("Starting Flask application.")
    app.run(host="0.0.0.0", port="50001", debug=True)
