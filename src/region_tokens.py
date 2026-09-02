"""District -> model input (the injection half of the method).

The entire intervention at the model boundary is this one string operation:
the (province, district) pair from geocode.py is prepended to the report text
as plain surface tokens,

    [경기도 수원시] 도로에 포트홀이 생겨 신고합니다

and the string is tokenized by the backbone's ordinary subword tokenizer.
No vocabulary additions, no special tokens, no architecture change, no extra
serving path. The paper's M2 (learned region embeddings) and M3 (coordinate
encodings) alternatives both change the model and both score lower.
"""
from __future__ import annotations

from typing import List, Optional


def build_model_input(text: str, sido: str, sigungu: str) -> str:
    """Exactly what the trained classifier sees for one report."""
    prefix = " ".join(p.strip() for p in (sido, sigungu))
    return f"[{prefix}] {text}"


def show_tokenization(model_input: str,
                      backbone: str = "klue/roberta-base") -> Optional[List[str]]:
    """Subword pieces the backbone tokenizer produces, for inspection.

    Returns None when the optional `transformers` dependency is missing.
    The region prefix segments into ordinary subwords -- there is nothing
    special about it from the tokenizer's point of view.
    """
    try:
        from transformers import AutoTokenizer
    except ImportError:
        return None
    tokenizer = AutoTokenizer.from_pretrained(backbone)
    return tokenizer.tokenize(model_input)
