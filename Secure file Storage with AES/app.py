import os
import hashlib
import datetime
import json
from flask import Flask, request, render_template, send_file
from cryptography.fernet import Fernet

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

KEY_FILE = "key.key"
if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as f:
        f.write(Fernet.generate_key())
with open(KEY_FILE, "rb") as f:
    key = f.read()
cipher = Fernet(key)

@app.route("/")
def index():
    return render_template("index.html", message="")

@app.route("/encrypt", methods=["POST"])
def encrypt():
    file = request.files["file"]
    if not file:
        return render_template("index.html", message="No file selected.")

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    with open(filepath, "rb") as f:
        data = f.read()

    encrypted = cipher.encrypt(data)
    enc_filename = file.filename + ".enc"
    enc_path = os.path.join(UPLOAD_FOLDER, enc_filename)
    with open(enc_path, "wb") as f:
        f.write(encrypted)

    metadata = {
        "original_filename": file.filename,
        "timestamp": datetime.datetime.now().isoformat(),
        "sha256_hash": hashlib.sha256(data).hexdigest()
    }
    meta_filename = enc_filename + ".meta"
    meta_path = os.path.join(UPLOAD_FOLDER, meta_filename)
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=4)

    return render_template("index.html", message=f"File encrypted.",
                           enc_file=enc_filename, meta_file=meta_filename)

@app.route("/decrypt", methods=["POST"])
def decrypt():
    enc_file = request.files["enc_file"]
    meta_file = request.files["meta_file"]
    if not enc_file or not meta_file:
        return render_template("index.html", message="Please upload both .enc and .meta files.")

    enc_path = os.path.join(UPLOAD_FOLDER, enc_file.filename)
    meta_path = os.path.join(UPLOAD_FOLDER, meta_file.filename)
    enc_file.save(enc_path)
    meta_file.save(meta_path)

    with open(enc_path, "rb") as f:
        encrypted_data = f.read()
    with open(meta_path, "r") as f:
        metadata = json.load(f)

    decrypted = cipher.decrypt(encrypted_data)
    file_hash = hashlib.sha256(decrypted).hexdigest()
    if file_hash != metadata["sha256_hash"]:
        return render_template("index.html", message="Hash mismatch! File may be tampered.")

    restored_filename = "restored_" + metadata["original_filename"]
    restored_path = os.path.join(UPLOAD_FOLDER, restored_filename)
    with open(restored_path, "wb") as f:
        f.write(decrypted)

    return render_template("index.html", message="File decrypted successfully.",
                           restored_file=restored_filename)

@app.route("/download/<filename>")
def download(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
