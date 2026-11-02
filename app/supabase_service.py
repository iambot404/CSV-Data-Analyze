import logging
from typing import Optional, Dict, Any, List
from app.config import SUPABASE_URL, SUPABASE_ANON_KEY

logger = logging.getLogger(__name__)

# In-memory fallback storage in case Supabase is offline or unreachable
_MEMORY_USERS: Dict[str, Dict[str, Any]] = {}
_MEMORY_ANALYSES: List[Dict[str, Any]] = []
_MEMORY_QUERIES: List[Dict[str, Any]] = []

def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return None
    try:
        from supabase import create_client, Client
        return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    except Exception as e:
        logger.warning(f"Could not initialize Supabase client: {e}")
        return None

def create_user(email: str, password_hash: str, full_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    client = get_supabase_client()
    if client:
        try:
            res = client.table("csv_users").insert({
                "email": email.lower().strip(),
                "password_hash": password_hash,
                "full_name": full_name or email.split("@")[0]
            }).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.error(f"Supabase create_user error: {e}")
    
    # Fallback to in-memory
    user_id = f"mem_usr_{len(_MEMORY_USERS) + 1}"
    record = {
        "id": user_id,
        "email": email.lower().strip(),
        "password_hash": password_hash,
        "full_name": full_name or email.split("@")[0],
        "created_at": "2026-11-02T00:00:00Z"
    }
    _MEMORY_USERS[email.lower().strip()] = record
    return record

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    client = get_supabase_client()
    if client:
        try:
            res = client.table("csv_users").select("*").eq("email", email.lower().strip()).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.error(f"Supabase get_user_by_email error: {e}")
            
    return _MEMORY_USERS.get(email.lower().strip())

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    client = get_supabase_client()
    if client:
        try:
            res = client.table("csv_users").select("*").eq("id", user_id).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.error(f"Supabase get_user_by_id error: {e}")

    for user in _MEMORY_USERS.values():
        if user["id"] == user_id:
            return user
    return None

def save_analysis(
    user_id: Optional[str],
    filename: str,
    file_size_bytes: int,
    row_count: int,
    column_count: int,
    columns: List[Dict[str, Any]],
    summary_stats: Dict[str, Any],
    data_sample: List[Dict[str, Any]],
    ai_insights: Dict[str, Any],
    charts: List[Dict[str, Any]]
) -> Dict[str, Any]:
    client = get_supabase_client()
    payload = {
        "user_id": user_id,
        "filename": filename,
        "file_size_bytes": file_size_bytes,
        "row_count": row_count,
        "column_count": column_count,
        "columns": columns,
        "summary_stats": summary_stats,
        "data_sample": data_sample,
        "ai_insights": ai_insights,
        "charts": charts
    }
    
    if client and user_id:
        try:
            res = client.table("csv_analyses").insert(payload).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.error(f"Supabase save_analysis error: {e}")
            
    # Fallback in-memory
    import uuid
    from datetime import datetime, timezone
    fallback_record = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        **payload
    }
    _MEMORY_ANALYSES.insert(0, fallback_record)
    return fallback_record

def list_analyses(user_id: Optional[str], limit: int = 20) -> List[Dict[str, Any]]:
    client = get_supabase_client()
    if client and user_id:
        try:
            res = client.table("csv_analyses")\
                .select("id, user_id, filename, file_size_bytes, row_count, column_count, created_at, ai_insights")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            if res.data is not None:
                return res.data
        except Exception as e:
            logger.error(f"Supabase list_analyses error: {e}")

    # Fallback
    if user_id:
        return [a for a in _MEMORY_ANALYSES if a.get("user_id") == user_id][:limit]
    return _MEMORY_ANALYSES[:limit]

def get_analysis(analysis_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    client = get_supabase_client()
    if client:
        try:
            query = client.table("csv_analyses").select("*").eq("id", analysis_id)
            if user_id:
                query = query.eq("user_id", user_id)
            res = query.execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.error(f"Supabase get_analysis error: {e}")

    for a in _MEMORY_ANALYSES:
        if a.get("id") == analysis_id:
            if not user_id or a.get("user_id") == user_id:
                return a
    return None

def delete_analysis(analysis_id: str, user_id: Optional[str] = None) -> bool:
    client = get_supabase_client()
    if client and user_id:
        try:
            client.table("csv_analyses").delete().eq("id", analysis_id).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase delete_analysis error: {e}")

    global _MEMORY_ANALYSES
    _MEMORY_ANALYSES = [a for a in _MEMORY_ANALYSES if a.get("id") != analysis_id]
    return True

def save_chat_query(
    analysis_id: str,
    user_id: Optional[str],
    query_text: str,
    ai_response: str,
    suggested_chart: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    client = get_supabase_client()
    payload = {
        "analysis_id": analysis_id,
        "user_id": user_id,
        "query_text": query_text,
        "ai_response": ai_response,
        "suggested_chart": suggested_chart
    }
    if client and user_id:
        try:
            res = client.table("csv_chat_queries").insert(payload).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.error(f"Supabase save_chat_query error: {e}")
            
    import uuid
    from datetime import datetime, timezone
    record = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        **payload
    }
    _MEMORY_QUERIES.append(record)
    return record

def list_chat_queries(analysis_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    client = get_supabase_client()
    if client and user_id:
        try:
            res = client.table("csv_chat_queries")\
                .select("*")\
                .eq("analysis_id", analysis_id)\
                .eq("user_id", user_id)\
                .order("created_at", desc=False)\
                .execute()
            if res.data is not None:
                return res.data
        except Exception as e:
            logger.error(f"Supabase list_chat_queries error: {e}")
            
    return [q for q in _MEMORY_QUERIES if q.get("analysis_id") == analysis_id]
