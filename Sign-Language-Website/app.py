from flask import Flask, render_template, Response, request, redirect, url_for
from sign_detection import generate_frames

app = Flask(__name__)

# Route for login page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        return redirect(url_for("welcome"))
    return render_template("login.html")

# Welcome page
@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

# Sign detection page
@app.route("/index")
def index():
    return render_template("index.html")

# Video feed route
@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    app.run(debug=True)
