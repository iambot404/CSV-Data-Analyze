import os
import logging
from flask import Blueprint, request, jsonify, render_template, current_app
from app.config import MAX_UPLOAD_SIZE_BYTES, ALLOWED_EXTENSIONS, GEMINI_MODELS
from app.auth import (
    hash_password, verify_password, create_access_token,
    get_current_user_from_request
)
from app.analyzer import parse_csv_bytes, analyze_dataframe, build_gemini_summary_prompt
from app.visualizer import build_all_charts
from app.gemini_service import generate_deep_insights, answer_csv_question
from app.samples import SAMPLE_DATASETS
from app.supabase_service import (
    create_user, get_user_by_email, get_user_by_id,
    save_analysis, list_analyses, get_analysis, delete_analysis,
    save_chat_query, list_chat_queries
)

logger = logging.getLogger(__name__)
main_bp = Blueprint("main", __name__)

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# In-memory session cache for temporary analyses across requests
_ACTIVE_ANALYSES_CACHE = {}

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "CSV Data Analyzer",
        "gemini_models": GEMINI_MODELS,
        "max_upload_size_mb": MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
    })

# ----------------- AUTHENTICATION ROUTES ----------------- #

@main_bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()

    if not email or "@" not in email:
        return jsonify({"error": "A valid email address is required."}), 400
    if not password or len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long."}), 400

    existing = get_user_by_email(email)
    if existing:
        return jsonify({"error": "An account with this email already exists."}), 409

    pwd_hash = hash_password(password)
    user = create_user(email, pwd_hash, full_name)
    if not user:
        return jsonify({"error": "Failed to create user account."}), 500

    token = create_access_token(user["id"], user["email"], user.get("full_name", ""))
    return jsonify({
        "message": "User registered successfully",
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user.get("full_name", "")
        }
    }), 201

@main_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid email or password."}), 401

    token = create_access_token(user["id"], user["email"], user.get("full_name", ""))
    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user.get("full_name", "")
        }
    })

@main_bp.route("/api/auth/me", methods=["GET"])
def get_current_user():
    user = get_current_user_from_request()
    if not user:
        return jsonify({"user": None, "authenticated": False})
    return jsonify({"user": user, "authenticated": True})

# ----------------- CSV UPLOAD & ANALYSIS ROUTES ----------------- #

def process_and_build_report(csv_bytes: bytes, filename: str, user_id: str = None) -> dict:
    # 1. Parse dataframe in memory
    df, meta = parse_csv_bytes(csv_bytes, filename=filename)
    
    # 2. Compute rich statistical summary
    analysis = analyze_dataframe(df)
    
    # 3. Generate base64 Matplotlib charts
    charts = build_all_charts(df, analysis)
    
    # 4. Generate structured Gemini AI insights
    summary_prompt = build_gemini_summary_prompt(analysis, filename=filename)
    ai_insights = generate_deep_insights(summary_prompt, filename=filename)
    
    # 5. Persist to Supabase / local storage
    saved_record = save_analysis(
        user_id=user_id,
        filename=filename,
        file_size_bytes=len(csv_bytes),
        row_count=analysis["row_count"],
        column_count=analysis["column_count"],
        columns=analysis["columns"],
        summary_stats={
            "numeric_stats": analysis["numeric_stats"],
            "categorical_stats": analysis["categorical_stats"],
            "correlation_matrix": analysis["correlation_matrix"],
            "health_score": analysis["health_score"],
            "duplicate_rows": analysis["duplicate_rows"],
            "memory_usage_bytes": analysis["memory_usage_bytes"]
        },
        data_sample=analysis["data_sample"],
        ai_insights=ai_insights,
        charts=charts
    )
    
    # Cache in-memory for immediate Q&A prompt access
    _ACTIVE_ANALYSES_CACHE[saved_record["id"]] = {
        "summary_prompt": summary_prompt,
        "analysis": saved_record
    }
    
    return saved_record

@main_bp.route("/api/upload", methods=["POST"])
def upload_csv():
    current_user = get_current_user_from_request()
    user_id = current_user.get("sub") if current_user else None

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded. Please select a CSV file."}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    filename = file.filename
    if not allowed_file(filename):
        return jsonify({"error": "Invalid file type. Only CSV files (.csv, .tsv, .txt) are accepted."}), 400

    # In-memory buffer read with size validation
    file_bytes = file.read()
    if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
        return jsonify({
            "error": f"File is too large ({len(file_bytes) / (1024*1024):.1f} MB). Maximum upload size is {MAX_UPLOAD_SIZE_BYTES / (1024*1024):.0f} MB."
        }), 413

    if len(file_bytes) == 0:
        return jsonify({"error": "The uploaded CSV file is empty."}), 400

    try:
        record = process_and_build_report(file_bytes, filename, user_id=user_id)
        return jsonify({
            "success": True,
            "message": f"Successfully analyzed '{filename}'",
            "analysis": record
        })
    except Exception as e:
        logger.error(f"Error processing CSV upload: {e}", exc_info=True)
        return jsonify({"error": f"Error parsing CSV: {str(e)}"}), 422

# ----------------- SAMPLE DATASETS ----------------- #

@main_bp.route("/api/samples", methods=["GET"])
def list_samples():
    samples_list = [
        {
            "id": s["id"],
            "name": s["name"],
            "filename": s["filename"],
            "description": s["description"]
        }
        for s in SAMPLE_DATASETS.values()
    ]
    return jsonify({"samples": samples_list})

@main_bp.route("/api/samples/<sample_id>/load", methods=["POST"])
def load_sample(sample_id):
    current_user = get_current_user_from_request()
    user_id = current_user.get("sub") if current_user else None

    sample = SAMPLE_DATASETS.get(sample_id)
    if not sample:
        return jsonify({"error": f"Sample dataset '{sample_id}' not found."}), 404

    csv_bytes = sample["csv_text"].encode("utf-8")
    try:
        record = process_and_build_report(csv_bytes, sample["filename"], user_id=user_id)
        return jsonify({
            "success": True,
            "message": f"Loaded sample '{sample['name']}'",
            "analysis": record
        })
    except Exception as e:
        logger.error(f"Error loading sample: {e}", exc_info=True)
        return jsonify({"error": f"Error analyzing sample dataset: {str(e)}"}), 500

# ----------------- NATURAL LANGUAGE Q&A CHAT ----------------- #

@main_bp.route("/api/analysis/<analysis_id>/query", methods=["POST"])
def query_analysis(analysis_id):
    current_user = get_current_user_from_request()
    user_id = current_user.get("sub") if current_user else None

    data = request.get_json() or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Question cannot be empty."}), 400

    # Retrieve prompt context from cache or recreate from analysis
    summary_prompt = ""
    cached = _ACTIVE_ANALYSES_CACHE.get(analysis_id)
    if cached and "summary_prompt" in cached:
        summary_prompt = cached["summary_prompt"]
    else:
        record = get_analysis(analysis_id, user_id=user_id)
        if not record:
            return jsonify({"error": "Analysis session not found."}), 404
        
        # Reconstruct prompt from recorded stats
        stats = record.get("summary_stats", {})
        summary_prompt = f"Dataset: {record.get('filename')}\nRows: {record.get('row_count')}, Cols: {record.get('column_count')}\nHealth Score: {stats.get('health_score')}\nColumns: {str(record.get('columns', []))[:1500]}"

    # Fetch previous chat history
    chat_history = list_chat_queries(analysis_id, user_id=user_id)
    ai_answer = answer_csv_question(question, summary_prompt, chat_history=chat_history)

    # Save to history
    saved_q = save_chat_query(
        analysis_id=analysis_id,
        user_id=user_id,
        query_text=question,
        ai_response=ai_answer
    )

    return jsonify({
        "success": True,
        "query": saved_q,
        "answer": ai_answer
    })

# ----------------- HISTORY & SAVED REPORTS ----------------- #

@main_bp.route("/api/history", methods=["GET"])
def get_user_history():
    current_user = get_current_user_from_request()
    user_id = current_user.get("sub") if current_user else None

    analyses = list_analyses(user_id=user_id, limit=25)
    return jsonify({"history": analyses})

@main_bp.route("/api/analysis/<analysis_id>", methods=["GET"])
def get_saved_analysis(analysis_id):
    current_user = get_current_user_from_request()
    user_id = current_user.get("sub") if current_user else None

    record = get_analysis(analysis_id, user_id=user_id)
    if not record:
        return jsonify({"error": "Analysis not found."}), 404

    # Also fetch any past Q&A queries for this dataset
    queries = list_chat_queries(analysis_id, user_id=user_id)

    return jsonify({
        "analysis": record,
        "queries": queries
    })

@main_bp.route("/api/analysis/<analysis_id>", methods=["DELETE"])
def delete_saved_analysis(analysis_id):
    current_user = get_current_user_from_request()
    user_id = current_user.get("sub") if current_user else None

    success = delete_analysis(analysis_id, user_id=user_id)
    if analysis_id in _ACTIVE_ANALYSES_CACHE:
        del _ACTIVE_ANALYSES_CACHE[analysis_id]
        
    return jsonify({"success": success})
