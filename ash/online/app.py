from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.route("/")
def index() -> str:
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "userfile" not in request.files:
        return "No file part"

    file = request.files["userfile"]
    if file.filename == "":
        return "No selected file"

    if file:
        text = file.read().decode("utf-8")
        result = sample_analysis(text)

        # return render_template('result.html', result=result)
        return jsonify(result)


def sample_analysis(text: str):
    words = text.split()
    return {"word_count": len(words)}


if __name__ == "__main__":
    app.run(debug=True)
