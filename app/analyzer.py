import io
import csv
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List, Optional

logger = logging.getLogger(__name__)

def clean_value_for_json(val: Any) -> Any:
    if pd.isna(val) or val is None:
        return None
    if isinstance(val, (np.integer, np.int64, np.int32)):
        return int(val)
    if isinstance(val, (np.floating, np.float64, np.float32)):
        if np.isnan(val) or np.isinf(val):
            return None
        return round(float(val), 4)
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    if isinstance(val, (pd.Timestamp, np.datetime64)):
        return str(val)
    return str(val)

def detect_delimiter(sample_bytes: bytes) -> str:
    sample_text = ""
    for enc in ["utf-8", "latin-1", "cp1252"]:
        try:
            sample_text = sample_bytes[:4096].decode(enc)
            break
        except UnicodeDecodeError:
            continue
            
    if not sample_text:
        return ","

    try:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample_text, delimiters=",\t;|")
        return dialect.delimiter
    except Exception:
        # Fallback check count of common delimiters
        counts = {
            ",": sample_text.count(","),
            ";": sample_text.count(";"),
            "\t": sample_text.count("\t"),
            "|": sample_text.count("|")
        }
        best = max(counts, key=counts.get)
        return best if counts[best] > 0 else ","

def parse_csv_bytes(file_bytes: bytes, filename: str = "dataset.csv") -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Parses CSV in-memory, returning the DataFrame and extraction metadata.
    """
    if not file_bytes or len(file_bytes.strip()) == 0:
        raise ValueError("The provided CSV file is empty.")

    delimiter = detect_delimiter(file_bytes)
    df = None
    
    # Try different encodings
    for encoding in ["utf-8", "latin-1", "cp1252"]:
        try:
            df = pd.read_csv(
                io.BytesIO(file_bytes),
                sep=delimiter,
                encoding=encoding,
                on_bad_lines="skip",
                low_memory=False
            )
            break
        except Exception as e:
            logger.warning(f"Failed to read CSV with {encoding}: {e}")
            continue

    if df is None or df.empty:
        raise ValueError("The provided CSV file is empty or could not be decoded.")

    # Clean column names (strip whitespace)
    df.columns = [str(c).strip() if str(c).strip() else f"Unnamed_{i}" for i, c in enumerate(df.columns)]
    
    return df, {
        "filename": filename,
        "delimiter": delimiter,
        "raw_size_bytes": len(file_bytes)
    }

def analyze_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs comprehensive statistical analysis on the DataFrame.
    """
    row_count = int(len(df))
    col_count = int(len(df.columns))
    memory_usage_bytes = int(df.memory_usage(deep=True).sum())
    duplicate_rows = int(df.duplicated().sum())

    total_cells = row_count * col_count
    total_missing = int(df.isna().sum().sum())
    completeness_ratio = max(0.0, 1.0 - (total_missing / max(1, total_cells)))
    
    # Calculate Data Health Score (0-100)
    health_score = int(round(
        (completeness_ratio * 70) +
        (max(0.0, 1.0 - (duplicate_rows / max(1, row_count))) * 20) +
        (10 if col_count >= 2 else 0)
    ))
    health_score = max(5, min(100, health_score))

    columns_meta = []
    numeric_stats = {}
    categorical_stats = {}

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    for col in df.columns:
        series = df[col]
        missing_count = int(series.isna().sum())
        missing_pct = round((missing_count / max(1, row_count)) * 100, 2)
        unique_count = int(series.nunique(dropna=True))
        
        # Determine column data type
        if pd.api.types.is_numeric_dtype(series):
            inferred_type = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(series):
            inferred_type = "datetime"
        elif pd.api.types.is_bool_dtype(series):
            inferred_type = "boolean"
        elif unique_count <= 25 or (row_count > 0 and (unique_count / row_count) <= 0.6):
            inferred_type = "categorical"
        else:
            inferred_type = "text"

        col_info = {
            "name": col,
            "type": inferred_type,
            "raw_dtype": str(series.dtype),
            "missing_count": missing_count,
            "missing_pct": missing_pct,
            "unique_count": unique_count,
            "sample_values": [clean_value_for_json(v) for v in series.dropna().head(5).tolist()]
        }

        # Numeric statistics
        if inferred_type == "numeric":
            valid = series.dropna()
            if not valid.empty:
                q25 = float(valid.quantile(0.25))
                q75 = float(valid.quantile(0.75))
                iqr = q75 - q25
                lower_bound = q25 - (1.5 * iqr)
                upper_bound = q75 + (1.5 * iqr)
                outliers_count = int(((valid < lower_bound) | (valid > upper_bound)).sum())

                stat_entry = {
                    "count": int(len(valid)),
                    "mean": clean_value_for_json(valid.mean()),
                    "std": clean_value_for_json(valid.std()),
                    "min": clean_value_for_json(valid.min()),
                    "q25": clean_value_for_json(q25),
                    "median": clean_value_for_json(valid.median()),
                    "q75": clean_value_for_json(q75),
                    "max": clean_value_for_json(valid.max()),
                    "skew": clean_value_for_json(valid.skew()) if len(valid) > 2 else 0,
                    "outliers_count": outliers_count
                }
                col_info["stats"] = stat_entry
                numeric_stats[col] = stat_entry

        # Categorical statistics
        if inferred_type in ("categorical", "text", "boolean"):
            top_counts = series.value_counts(dropna=True).head(5)
            cat_entry = {
                "top_categories": [
                    {"value": str(idx), "count": int(cnt), "pct": round((int(cnt) / max(1, row_count)) * 100, 1)}
                    for idx, cnt in top_counts.items()
                ],
                "mode": str(top_counts.index[0]) if not top_counts.empty else None
            }
            col_info["stats"] = cat_entry
            categorical_stats[col] = cat_entry

        columns_meta.append(col_info)

    # Correlation Matrix for Numeric Columns
    correlation_matrix = {}
    if len(numeric_cols) >= 2:
        try:
            corr_df = df[numeric_cols].corr()
            corr_dict = {}
            for c1 in numeric_cols:
                corr_dict[c1] = {}
                for c2 in numeric_cols:
                    val = corr_df.loc[c1, c2]
                    corr_dict[c1][c2] = clean_value_for_json(val)
            correlation_matrix = corr_dict
        except Exception as e:
            logger.warning(f"Error calculating correlation matrix: {e}")

    # Data sample for preview (first 25 rows)
    preview_df = df.head(25)
    data_sample = [
        {col: clean_value_for_json(row[col]) for col in df.columns}
        for _, row in preview_df.iterrows()
    ]

    return {
        "row_count": row_count,
        "column_count": col_count,
        "memory_usage_bytes": memory_usage_bytes,
        "duplicate_rows": duplicate_rows,
        "total_missing": total_missing,
        "health_score": health_score,
        "columns": columns_meta,
        "numeric_stats": numeric_stats,
        "categorical_stats": categorical_stats,
        "correlation_matrix": correlation_matrix,
        "data_sample": data_sample,
        "numeric_column_names": numeric_cols
    }

def build_gemini_summary_prompt(meta: Dict[str, Any], filename: str) -> str:
    """
    Builds a concise summary string from calculated statistics to feed into Gemini.
    """
    col_summary = []
    for c in meta.get("columns", []):
        info = f"- {c['name']} ({c['type']}): missing={c['missing_pct']}%, unique={c['unique_count']}"
        if "stats" in c:
            st = c["stats"]
            if c["type"] == "numeric":
                info += f" | mean={st.get('mean')}, min={st.get('min')}, median={st.get('median')}, max={st.get('max')}, outliers={st.get('outliers_count')}"
            elif "top_categories" in st:
                top_str = ", ".join([f"{item['value']} ({item['count']})" for item in st["top_categories"][:3]])
                info += f" | top: [{top_str}]"
        col_summary.append(info)

    # Top sample rows
    samples = meta.get("data_sample", [])[:3]
    samples_str = str(samples)

    prompt = f"""
Dataset: {filename}
Overview: {meta.get('row_count')} rows, {meta.get('column_count')} columns, {meta.get('duplicate_rows')} duplicate rows, Health Score: {meta.get('health_score')}/100.

Columns Profile:
{chr(10).join(col_summary[:25])}

Sample Data Rows:
{samples_str}
"""
    return prompt
