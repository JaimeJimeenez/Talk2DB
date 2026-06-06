from app.application.rag.service import RagService


def test_default_answer_summarizes_numeric_result_by_label():
    answer = RagService._default_answer(
        ["mes", "ingresos"],
        [
            {"mes": "2026-01-01T00:00:00+00:00", "ingresos": 2910.0},
            {"mes": "2026-02-01T00:00:00+00:00", "ingresos": 1600.0},
            {"mes": "2026-03-01T00:00:00+00:00", "ingresos": 1400.0},
            {"mes": "2026-04-01T00:00:00+00:00", "ingresos": 2890.0},
        ],
    )

    assert answer.startswith("He calculado ingresos para 4 categorías.")
    assert "2026-01: 2,910" in answer
    assert answer.endswith("...")


def test_default_answer_summarizes_single_row_values():
    answer = RagService._default_answer(
        ["producto", "ingresos"],
        [{"producto": "Pro Analytics", "ingresos": 2800.0}],
    )

    assert answer == "He calculado ingresos para 1 categoría. Pro Analytics: 2,800."
