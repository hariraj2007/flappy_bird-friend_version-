import os
import subprocess
import sys
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "flappy-friend-secret-2024"

UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
DEFAULT_SOUND = "win.ogg"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    errors = []

    # Validate required images
    if "friend_image" not in request.files or request.files["friend_image"].filename == "":
        errors.append("Flying photo is required.")
    if "jump_image" not in request.files or request.files["jump_image"].filename == "":
        errors.append("Jump photo is required.")

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("index"))

    friend_file = request.files["friend_image"]
    jump_file = request.files["jump_image"]
    sound_value = request.form.get("jump_sound", "").strip() or DEFAULT_SOUND

    if not allowed_file(friend_file.filename):
        flash("Flying photo must be PNG, JPG, GIF or WEBP.", "error")
        return redirect(url_for("index"))
    if not allowed_file(jump_file.filename):
        flash("Jump photo must be PNG, JPG, GIF or WEBP.", "error")
        return redirect(url_for("index"))

    friend_filename = secure_filename(friend_file.filename)
    jump_filename = secure_filename(jump_file.filename)

    friend_path = os.path.join(app.config["UPLOAD_FOLDER"], friend_filename)
    jump_path = os.path.join(app.config["UPLOAD_FOLDER"], jump_filename)

    friend_file.save(friend_path)
    jump_file.save(jump_path)

    session["friend_image"] = friend_filename
    session["jump_image"] = jump_filename
    session["jump_sound"] = sound_value

    return redirect(url_for("ready"))


@app.route("/ready")
def ready():
    friend_image = session.get("friend_image")
    jump_image = session.get("jump_image")
    jump_sound = session.get("jump_sound", DEFAULT_SOUND)

    if not friend_image or not jump_image:
        flash("Please upload your photos first.", "error")
        return redirect(url_for("index"))

    friend_path = os.path.join(app.config["UPLOAD_FOLDER"], friend_image)
    jump_path = os.path.join(app.config["UPLOAD_FOLDER"], jump_image)

    is_default_sound = jump_sound == DEFAULT_SOUND

    if is_default_sound:
        command = f'python flappy_friend.py "{friend_path}" "{jump_path}"'
    else:
        command = f'python flappy_friend.py "{friend_path}" "{jump_path}" --sound "{jump_sound}"'

    return render_template(
        "ready.html",
        friend_image=friend_image,
        jump_image=jump_image,
        jump_sound=jump_sound,
        is_default_sound=is_default_sound,
        command=command,
    )


@app.route("/launch")
def launch():
    friend_image = session.get("friend_image")
    jump_image = session.get("jump_image")
    jump_sound = session.get("jump_sound", DEFAULT_SOUND)

    if not friend_image or not jump_image:
        flash("Session expired. Please upload again.", "error")
        return redirect(url_for("index"))

    friend_path = os.path.join(app.config["UPLOAD_FOLDER"], friend_image)
    jump_path = os.path.join(app.config["UPLOAD_FOLDER"], jump_image)

    cmd = [sys.executable, "flappy_friend.py", friend_path, jump_path]
    if jump_sound != DEFAULT_SOUND:
        cmd += ["--sound", jump_sound]

    try:
        subprocess.Popen(cmd)
        launched = True
        message = "Game launched! Check your desktop."
    except Exception as ex:
        launched = False
        message = f"Could not launch: {ex}"

    return render_template(
        "ready.html",
        friend_image=friend_image,
        jump_image=jump_image,
        jump_sound=jump_sound,
        is_default_sound=(jump_sound == DEFAULT_SOUND),
        command=" ".join(cmd),
        launched=launched,
        launch_message=message,
    )


@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, port=5000)
