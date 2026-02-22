from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from retriever import get_record, RECORDS, reload_records, write_records_csv, validate_csv_content

app = Flask(__name__)
app.secret_key = "dev-secret"

@app.get("/")
def home():
    return render_template(
        "index.html",
        result=None,
        user_text="",
        keywords=sorted(RECORDS.keys()),
        message=None,
    )

@app.post("/lookup")
def lookup():
    user_text = request.form.get("answer", "")
    result = get_record(user_text)
    return render_template(
        "index.html",
        result=result,
        user_text=user_text,
        keywords=sorted(RECORDS.keys()),
        message=None,
    )


@app.post("/upload")
def upload():
    # Accept either a file upload (multipart/form-data) named 'csvfile'
    # or a URL in the 'csvurl' field.
    csvfile = request.files.get("csvfile")
    csvurl = request.form.get("csvurl", "").strip()

    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", "")

    csvfile = request.files.get("csvfile")
    if not csvfile or not csvfile.filename:
        if is_ajax:
            return jsonify(status="error", message="No file uploaded."), 400
        return render_template(
            "index.html",
            result=None,
            user_text="",
            keywords=sorted(RECORDS.keys()),
            message="No file uploaded.",
        )

    # Read uploaded file
    raw = csvfile.read().decode("utf-8")
    if not raw.strip():
        if is_ajax:
            return jsonify(status="error", message="Uploaded CSV was empty; no changes applied."), 400
        flash("Uploaded CSV was empty; no changes applied.")
        return redirect(url_for("home"))
    # Validate CSV format before writing
    parsed, err = validate_csv_content(raw)
    if err:
        if is_ajax:
            return jsonify(status="error", message=f"CSV validation error: {err}"), 400
        return render_template(
            "index.html",
            result=None,
            user_text="",
            keywords=sorted(RECORDS.keys()),
            message=f"CSV validation error: {err}",
        )
    write_records_csv(raw)
    reload_records()
    keywords = sorted(RECORDS.keys())
    if is_ajax:
        # Return only first 20 keywords for display
        return jsonify(status="ok", message="Uploaded CSV applied.", keywords=keywords[:20], total_keywords=len(keywords))
    flash("Uploaded CSV applied.")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)