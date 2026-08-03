const imageInput = document.createElement('input');
imageInput.type = 'file';
imageInput.style.display = 'none';

const imageInfoBox = document.getElementById('image-info-box');
const imageInfo = document.getElementById('image-info');
const messageContainer = document.getElementById('message-container');
const uploadedVideo = document.getElementById('uploaded-video');

let imageInfoData = {}; // Store raw JSON data here

// Initialize container
const container = document.querySelector('.container');
const container2 = document.querySelector('.container2');

const dropArea = document.getElementById('drop-area');
const uploadedImage = document.getElementById('uploaded-image');
let isValidDrop = false; // Track if the drop is valid

function isSupportedMedia(file) {
    return Boolean(file) && (file.type.startsWith('image/') || file.type.startsWith('video/'));
}

function showPreview(mimeType, base64Data) {
    const source = `data:${mimeType};base64,${base64Data}`;

    if (mimeType && mimeType.startsWith('video/')) {
        uploadedImage.style.display = 'none';
        uploadedImage.removeAttribute('src');
        uploadedVideo.src = source;
        uploadedVideo.style.display = 'block';
        return;
    }

    uploadedVideo.pause();
    uploadedVideo.removeAttribute('src');
    uploadedVideo.load();
    uploadedVideo.style.display = 'none';
    uploadedImage.src = source;
    uploadedImage.style.display = 'block';
}

// Prevent the default behavior (allowing drag and drop) globally
document.addEventListener('dragover', function (event) {
    event.preventDefault(); // Prevent default behavior for all areas
});

// Handle drag and drop
dropArea.addEventListener('dragover', function (event) {
    event.preventDefault();  // Allow dropping
    dropArea.classList.add('dragover');  // Highlight drop area
});

dropArea.addEventListener('dragleave', function () {
    dropArea.classList.remove('dragover');  // Remove highlight
});

dropArea.addEventListener('drop', function (event) {
    event.preventDefault();
    dropArea.classList.remove('dragover');  // Remove highlight

    const file = event.dataTransfer.files[0];  // Get the dropped file
    uploadImage(file);
});

// Prevent drag over outside the drop area
document.addEventListener('dragover', function (event) {
    // If the dragover is not inside the drop area, prevent default behavior
    if (!dropArea.contains(event.target)) {
        event.preventDefault();
    }
});

// Prevent drop outside the drop area
document.addEventListener('drop', function (event) {
    // If the drop is outside the drop area, prevent default behavior
    if (!dropArea.contains(event.target)) {
        event.preventDefault();
    }
});

// Handle file input change event
const fileInput = document.getElementById('file-upload');
fileInput.addEventListener('change', function (event) {
    const file = event.target.files[0]; // Get the selected file
    if (isSupportedMedia(file)) {
        uploadImage(file); // Read the image file as data URL
    } else {
        showMessage('Please upload a valid image or video file.', 'red');
    }
});

// Add event listener to uploaded image to trigger file input click
uploadedImage.addEventListener('click', function () {
    // alert('Please upload a valid image file.');
    fileInput.click();
});

// Handle image upload logic
function uploadImage(file) {
    messageContainer.textContent = ''; // Clear any existing message
    messageContainer.style.display = 'none'; // Hide the message

    const formData = new FormData();
    formData.append('file', file);

    fetch('/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const previewData = data.file_data || data.img_data;
        showPreview(data.mime_type, previewData);

        // Store the image info as raw JSON in JavaScript
        imageInfoData = data.image_info;

        // Display image info in a readable format
        let htmlContent = "<div class='image-info' id='image-info'>";

        // Loop through each key-value pair in image_info
        for (const [key, value] of Object.entries(imageInfoData)) {
            htmlContent += `<div class='info-item' id=info-item><strong>${key}</strong><div class='info-item-content id=info-item-content'>`;

            // If the value is an object (like parameters), format it properly
            if (typeof value === 'object' && value !== null) {
                htmlContent += `<pre>${JSON.stringify(value, null, 2)}</pre>`;
            } else {
                htmlContent += value;
            }

            // Add Save to JSON button for each parameter
            htmlContent += `</div>
            <div class='info-item-buttons'>
                    <button class="save-button" onclick="saveToJSON('${key}')">Save to JSON</button>
                    <button class="copy-button" onclick="copyToClipboard('${key}')">Copy to Clipboard</button>
                    </div>
            </div>`;
        }

        htmlContent += "</div>";

        // Show the image info box and insert the content
        imageInfo.innerHTML = htmlContent;
        imageInfoBox.style.display = 'block';

        // Show container2 if it has content
        if (htmlContent.trim() !== "") {
            container2.style.display = 'block';
            container.style.marginLeft = '5%';
        } else {
            container2.style.display = 'none';
            container.style.marginLeft = '0px';
        }
    })
    .catch(error => {
        container2.style.display = 'none';
        container.style.marginLeft = '0px';
        console.error('Error:', error);
        showMessage('An error occurred while decoding the file. It probably has no readable metadata.', 'red');
    });
}

// Function to save the parameter to a JSON file
function saveToJSON(key) {
    const value = imageInfoData[key]; // Get the value directly from imageInfoData

    // If the key is "workflow", we save only its content (without the key name)
    let jsonObject = value;

    // Convert the object to a string
    let jsonString = JSON.stringify(jsonObject, null, 2);

    // Remove any escaped quotes in the string
    jsonString = jsonString.replace(/\\"/g, '"');
    jsonString = jsonString.replace(/"{/g, '{');
    jsonString = jsonString.replace(/}"/g, '}');

    // Create a Blob from the sanitized JSON string
    const jsonBlob = new Blob([jsonString], { type: 'application/json' });
    
    // Create a download link and trigger it
    const link = document.createElement('a');
    link.href = URL.createObjectURL(jsonBlob);
    link.download = `${key}.json`;
    link.click();
}

function copyToClipboard(key) {
    const value = imageInfoData[key]; // Get the value directly from imageInfoData
    const textValue = typeof value === 'string' ? value : JSON.stringify(value, null, 2);

    navigator.clipboard.writeText(textValue).then(() => {
        // Optionally, display a message to the user
        showMessage('Content copied to clipboard!', 'green');
    }).catch(err => {
        console.error('Failed to copy: ', err);
        showMessage('Failed to copy content to clipboard.', 'red');
    });
    container2.style.display = 'block';
    container.style.marginLeft = '5%';
}


function showMessage(message, color) {
    // Set the message text and color
    if (color === 'red') {
        messageContainer.style.backgroundColor = 'rgb(185, 91, 91)';
        messageContainer.style.color = 'rgb(255, 255, 255)';
        messageContainer.style.border = '1px solid rgb(185, 91, 91)';
    } else if (color === 'green') {
        messageContainer.style.backgroundColor = 'rgb(94, 177, 94)';
        messageContainer.style.color = 'rgb(255, 255, 255)';
        messageContainer.style.border = '1px solid rgb(94, 177, 94)';
    } else if (color === 'blue') {
        messageContainer.style.backgroundColor = 'rgb(57, 117, 196)';
        messageContainer.style.color = 'rgb(255, 255, 255)';
        messageContainer.style.border = '1px solid rgb(57, 117, 196)';
    }
    messageContainer.textContent = message;
    messageContainer.style.display = 'block'; // Make the message visible
    messageContainer.classList.add('fade', 'show'); // Add fade and show classes to trigger fade-in effect
    setTimeout(() => {
    messageContainer.classList.remove('show'); // Remove show class to trigger fade-out effect
    }, 5000);
}