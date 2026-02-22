from flask import Flask, request, render_template
from retriever import get_record, RECORDS

app = Flask(__name__)

@app.get("/")
def home():
    return render_template("index.html", result=None, user_text="", keywords=sorted(RECORDS.keys()))

@app.post("/lookup")
def lookup():
    user_text = request.form.get("answer", "")
    result = get_record(user_text)
    return render_template("index.html", result=result, user_text=user_text, keywords=sorted(RECORDS.keys()))

if __name__ == "__main__":
    app.run(debug=True)