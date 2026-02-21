from flask import Flask, request, render_template
from retriever import get_record

app = Flask(__name__)

@app.get("/")
def home():
    return render_template("index.html", result=None, user_text="")

@app.post("/lookup")
def lookup():
    user_text = request.form.get("answer", "")
    result = get_record(user_text)
    return render_template("index.html", result=result, user_text=user_text)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)