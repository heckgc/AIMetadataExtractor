import logging
import re
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
        file = request.files['file']
        if file:
            try:
                logging.debug("Received file: %s", file.filename)

                # Read the image file
                img_data = file.read()
                logging.debug(
                    "Read %d bytes from the uploaded file.", len(img_data))

                # Attempt to open the image
                try:
                    img = Image.open(io.BytesIO(img_data))
                    logging.debug(
                        "Image opened successfully: format=%s, size=%s, mode=%s", img.format, img.size, img.mode)
                except Exception as e:
                    logging.error("Failed to open image: %s", str(e))
                    return jsonify({'error': f"Failed to open image: {str(e)}"})

                # Extract image info (metadata)
                img_info = img.info

                if (check_and_decode_exif(img_data)):
                    img_info = read_exif(img)
                    img_info = transform_image_info(
                        img_info["image_info"])
                else:
                    logging.debug("No EXIF data found in the image.")

                # Prepare the response
                response = {
                    # 'img_data': img_base64,  # base64 encoded image
                    # image metadata
                    'image_info': img_info,
                    # 'mime_type': file.content_type,  # MIME type for the image
                    # EXIF data
                    # 'exif_data': read_info_from_image(img)
                }
                return jsonify(response)

            except Exception as e:
                logging.error("An error occurred: %s", str(e))
                return jsonify({'error': str(e)})

    # Show the form to upload an image on the first load
    return render_template('index.html')


def transform_image_info(image_info):
    # Extract the UserComment field
    user_comment = image_info.get("UserComment", "")

    # Parse the UserComment into a structured JSON object
    parsed_comment = parse_user_comment(user_comment)

    # Merge the parsed UserComment back into the image_info dictionary
    image_info.update(parsed_comment)

    # Remove the original UserComment field
    del image_info["UserComment"]

    return image_info


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
