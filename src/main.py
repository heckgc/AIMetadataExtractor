from flask import Flask, request, render_template, jsonify
from PIL import Image
import io
import base64

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            try:
                # Read the image file
                img_data = file.read()
                img = Image.open(io.BytesIO(img_data))

                # Extract image info (metadata)
                # This includes metadata like parameters, icc_profile, etc.
                img_info = img.info

                # Convert the image to base64 for rendering in the browser
                img_base64 = base64.b64encode(img_data).decode('utf-8')

                # Prepare the response
                response = {
                    'img_data': img_base64,  # base64 encoded image
                    'image_info': img_info,  # image metadata
                    # MIME type for the image (JPEG, PNG, etc.)
                    'mime_type': file.content_type
                }
                return jsonify(response)

            except Exception as e:
                return jsonify({'error': str(e)})

    # Show the form to upload an image on the first load
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="50001", debug=True)
