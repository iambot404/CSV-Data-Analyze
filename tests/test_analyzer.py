import pytest
import pandas as pd
from app.analyzer import parse_csv_bytes, analyze_dataframe, build_gemini_summary_prompt

def test_parse_csv_bytes_standard():
    csv_data = b"name,age,salary\nAlice,30,70000\nBob,35,80000\nCharlie,25,50000"
    df, meta = parse_csv_bytes(csv_data, "test.csv")
    assert len(df) == 3
    assert list(df.columns) == ["name", "age", "salary"]
    assert meta["delimiter"] == ","

def test_parse_csv_bytes_semicolon():
    csv_data = b"product;price;quantity\nLaptop;1200.50;5\nPhone;800;10"
    df, meta = parse_csv_bytes(csv_data, "tech.csv")
    assert len(df) == 2
    assert "price" in df.columns
    assert meta["delimiter"] == ";"

def test_parse_csv_bytes_empty():
    with pytest.raises(ValueError, match="empty"):
        parse_csv_bytes(b"", "empty.csv")

def test_analyze_dataframe_metrics():
    data = {
        "A": [10, 20, 30, 40, 1000],  # 1000 is an outlier
        "B": ["cat", "dog", "cat", "cat", "bird"],
        "C": [1.1, None, 3.3, 4.4, 5.5]  # contains 1 missing value
    }
    df = pd.DataFrame(data)
    analysis = analyze_dataframe(df)

    assert analysis["row_count"] == 5
    assert analysis["column_count"] == 3
    assert analysis["total_missing"] == 1
    assert 0 <= analysis["health_score"] <= 100

    # Verify column profiling
    cols = {c["name"]: c for c in analysis["columns"]}
    assert cols["A"]["type"] == "numeric"
    assert cols["A"]["stats"]["outliers_count"] >= 1
    assert cols["B"]["type"] == "categorical"
    assert cols["B"]["stats"]["mode"] == "cat"
    assert cols["C"]["missing_count"] == 1

def test_build_gemini_summary_prompt():
    df = pd.DataFrame({"score": [85, 90, 78], "grade": ["B", "A", "C"]})
    analysis = analyze_dataframe(df)
    prompt = build_gemini_summary_prompt(analysis, "grades.csv")
    assert "Dataset: grades.csv" in prompt
    assert "score" in prompt
    assert "grade" in prompt
