import os
import shutil
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, send_file

# Initialize Flask App
app = Flask(__name__)
app.secret_key = "nebula_smart_file_organizer"

# Define and create necessary directories
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Category mapping for file extensions
file_categories = {
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'],
    'Documents': ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls', '.pptx', '.ppt'],
    'Videos': ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
    'Audio': ['.mp3', '.wav', '.aac', '.ogg'],
    'JSON': ['.json'],
    'Archives': ['.zip', '.rar', '.tar', '.gz', '.7z'],
    'Others': []
}

def organize_files_by_category(target_file_path):
    """Organizes files in the target directory into category subfolders."""
    if not os.path.exists(target_file_path):
        return

    for filename in os.listdir(target_file_path):
        file_path = os.path.join(target_file_path, filename)

        # Skip directories to avoid infinite loops
        if os.path.isdir(file_path):
            continue

        # Get the file extension
        _, file_extension = os.path.splitext(filename)
        file_extension = file_extension.lower()

        # Determine the category for the file
        category_found = False
        for category, extensions in file_categories.items():
            if file_extension in extensions:
                category_folder = os.path.join(target_file_path, category)
                os.makedirs(category_folder, exist_ok=True)
                shutil.move(file_path, os.path.join(category_folder, filename))
                category_found = True
                break

        # If no category was found, move to 'Others'
        if not category_found:
            others_folder = os.path.join(target_file_path, 'Others')
            os.makedirs(others_folder, exist_ok=True)
            shutil.move(file_path, os.path.join(others_folder, filename))

def create_zip_archive(source_dir, output_filename):
    """Creates a ZIP archive of the organized files."""
    output_base = os.path.join(OUTPUT_FOLDER, output_filename)
    shutil.make_archive(output_base, 'zip', source_dir)
    return f"{output_base}.zip"

# Flask Routes
@app.route('/')
def index():
    """Renders the main frontend interface."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles file uploads, organizes them, and returns a ZIP file."""
    # 'files' is the name of the input field in HTML
    uploaded_files = request.files.getlist('files')
    
    if not uploaded_files or uploaded_files[0].filename == '':
        return "No files selected for uploading. Please go back and try again.", 400

    # Clear previous uploads and outputs for a fresh start
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Save uploaded files
    for file in uploaded_files:
        if file and file.filename:
            # We use os.path.basename to strip any folder paths from the filename
            filename = secure_filename(os.path.basename(file.filename))
            if filename:
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)

    # Organize files by category
    organize_files_by_category(UPLOAD_FOLDER)

    # Create a zip file named 'Nebula_Organized_Files.zip'
    final_zip_path = create_zip_archive(UPLOAD_FOLDER, 'Nebula_Organized_Files')

    # Send the zip file back to the browser for download
    return send_file(final_zip_path, as_attachment=True)

if __name__ == "__main__":
    # Start the Flask development server
    app.run(debug=True)