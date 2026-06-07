from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import re
from math import sqrt
from typing import Any
from uuid import uuid5, NAMESPACE_URL

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams


@dataclass(frozen=True)
class SchemaDocument:
    id: str
    content: str
    table_schema: str
    table_name: str


class SchemaContextService:
    def __init__(
        self,
        *,
        embedding_gateway: Any,
        qdrant_url: str,
        collection_name: str,
        top_k: int = 2,
    ) -> None:
        self._embedding_gateway = embedding_gateway
        self._qdrant = QdrantClient(url=qdrant_url)
        self._collection_name = collection_name
        self._top_k = top_k

    async def retrieve_relevant_schema(
        self,
        schema: dict[str, Any],
        question: str,
        *,
        guidance: str = "",
    ) -> dict[str, Any]:
        documents = self._build_documents(schema, guidance=guidance)
        index = await self._load_or_build_index(schema, documents)
        question_embedding = await self._embedding_gateway.embed_text(question)
        scored = [
            (
                self._score_entry(question, question_embedding, entry),
                entry["document"]["id"],
            )
            for entry in index["entries"]
        ]
        scored.sort(reverse=True)
        selected_table_ids = [table_id for _, table_id in scored[: self._top_k]]
        expanded_table_ids = self._expand_with_related_tables(schema, selected_table_ids)
        return self._filter_schema_by_table_ids(schema, expanded_table_ids)

    async def ensure_schema_index(self, schema: dict[str, Any], *, guidance: str = "") -> int:
        documents = self._build_documents(schema, guidance=guidance)
        await self._load_or_build_index(schema, documents)
        return len(documents)

    def format_for_prompt(self, schema: dict[str, Any]) -> str:
        lines: list[str] = []
        for schema_name, tables in schema.items():
            lines.append(f"Schema: {schema_name}")
            for table_name, table_info in tables.items():
                lines.append(f"\nTable: {schema_name}.{table_name}")
                if table_info.get("description"):
                    lines.append(f"Description: {table_info['description']}")
                lines.append("Columns:")
                for column in table_info["columns"]:
                    nullable = "nullable" if column["nullable"] else "not nullable"
                    column_line = f"- {column['name']}: {column['type']} ({nullable})"
                    if column.get("description"):
                        column_line += f" - {column['description']}"
                    lines.append(column_line)
                foreign_keys = [
                    constraint
                    for constraint in table_info.get("constraints", [])
                    if constraint["type"] == "FOREIGN KEY"
                ]
                if foreign_keys:
                    lines.append("Foreign keys:")
                    for constraint in foreign_keys:
                        lines.append(
                            "- "
                            f"{constraint['column']} -> "
                            f"{constraint['foreign_table_schema']}."
                            f"{constraint['foreign_table_name']}."
                            f"{constraint['foreign_column_name']}"
                        )
        return "\n".join(lines)

    async def _load_or_build_index(
        self,
        schema: dict[str, Any],
        documents: list[SchemaDocument],
    ) -> dict[str, Any]:
        schema_fingerprint = self._fingerprint(schema)
        documents_fingerprint = self._fingerprint([document.content for document in documents])
        metadata = {
            "schema_fingerprint": schema_fingerprint,
            "documents_fingerprint": documents_fingerprint,
            "embedding_model": self._embedding_gateway.model,
        }
        existing_entries = self._read_entries(metadata)
        if len(existing_entries) == len(documents):
            return {"entries": existing_entries}

        embeddings = await self._embedding_gateway.embed_documents([document.content for document in documents])
        self._ensure_collection(len(embeddings[0]) if embeddings else 1)
        points = [
            PointStruct(
                id=str(uuid5(NAMESPACE_URL, f"{metadata['schema_fingerprint']}:{document.id}")),
                vector=embedding,
                payload={**metadata, "document": asdict(document)},
            )
            for document, embedding in zip(documents, embeddings, strict=True)
        ]
        if points:
            self._qdrant.upsert(collection_name=self._collection_name, points=points, wait=True)
        return {"entries": self._read_entries(metadata)}

    def _read_entries(self, metadata: dict[str, str]) -> list[dict[str, Any]]:
        if not self._qdrant.collection_exists(self._collection_name):
            return []
        records, _ = self._qdrant.scroll(
            collection_name=self._collection_name,
            scroll_filter=self._metadata_filter(metadata),
            limit=10_000,
            with_payload=True,
            with_vectors=True,
        )
        entries: list[dict[str, Any]] = []
        for record in records:
            if record.payload is None or record.vector is None:
                continue
            entries.append({"document": record.payload["document"], "embedding": record.vector})
        return entries

    def _ensure_collection(self, vector_size: int) -> None:
        if self._qdrant.collection_exists(self._collection_name):
            return
        self._qdrant.create_collection(
            collection_name=self._collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    @staticmethod
    def _metadata_filter(metadata: dict[str, str]) -> Filter:
        return Filter(
            must=[
                FieldCondition(key=key, match=MatchValue(value=value))
                for key, value in metadata.items()
            ]
        )

    def _build_documents(self, schema: dict[str, Any], *, guidance: str = "") -> list[SchemaDocument]:
        documents: list[SchemaDocument] = []
        for schema_name, tables in schema.items():
            for table_name, table_info in tables.items():
                table_terms = self._build_table_terms(schema_name, table_name, table_info)
                lines = [
                    f"Table: {schema_name}.{table_name}",
                    f"Description: {self._table_description(schema_name, table_name, table_info, table_terms)}",
                    f"Search terms: {' '.join(sorted(table_terms))}",
                    "Columns:",
                ]
                for column in table_info.get("columns", []):
                    column_terms = " ".join(sorted(identifier_terms(column["name"])))
                    column_line = f"- {column['name']}: {column['type']} ({column_terms})"
                    if column.get("description"):
                        column_line += f" - {column['description']}"
                    lines.append(column_line)
                for constraint in table_info.get("constraints", []):
                    if constraint["type"] != "FOREIGN KEY":
                        continue
                    lines.append(
                        "Relationship: "
                        f"{schema_name}.{table_name}.{constraint['column']} -> "
                        f"{constraint['foreign_table_schema']}."
                        f"{constraint['foreign_table_name']}."
                        f"{constraint['foreign_column_name']}"
                    )
                if guidance:
                    lines.extend(["Domain guidance:", guidance])
                documents.append(
                    SchemaDocument(
                        id=f"{schema_name}.{table_name}",
                        content="\n".join(lines),
                        table_schema=schema_name,
                        table_name=table_name,
                    )
                )
        return documents

    def _table_description(
        self,
        schema_name: str,
        table_name: str,
        table_info: dict[str, Any],
        table_terms: set[str],
    ) -> str:
        if table_info.get("description"):
            return str(table_info["description"])
        column_names = [column["name"].replace("_", " ") for column in table_info.get("columns", [])]
        return (
            f"{schema_name.replace('_', ' ')}.{table_name.replace('_', ' ')} records "
            f"with columns: {', '.join(column_names)}. "
            f"Identifier terms: {', '.join(sorted(table_terms))}."
        )

    def _build_table_terms(self, schema_name: str, table_name: str, table_info: dict[str, Any]) -> set[str]:
        terms = set()
        terms.update(identifier_terms(schema_name))
        terms.update(identifier_terms(table_name))
        if table_info.get("description"):
            terms.update(text_terms(str(table_info["description"])))
        for column in table_info.get("columns", []):
            terms.update(identifier_terms(column["name"]))
            if column.get("description"):
                terms.update(text_terms(str(column["description"])))
        for constraint in table_info.get("constraints", []):
            for key in ("column", "foreign_table_schema", "foreign_table_name", "foreign_column_name"):
                value = constraint.get(key)
                if value:
                    terms.update(identifier_terms(str(value)))
        return {term for term in terms if len(term) > 1}

    def _score_entry(self, question: str, question_embedding: list[float], entry: dict[str, Any]) -> float:
        return cosine_similarity(question_embedding, entry["embedding"]) + lexical_overlap_score(
            question,
            entry["document"]["content"],
        )

    def _expand_with_related_tables(self, schema: dict[str, Any], table_ids: list[str]) -> list[str]:
        expanded = set(table_ids)
        changed = True
        while changed:
            changed = False
            for schema_name, tables in schema.items():
                for table_name, table_info in tables.items():
                    table_id = f"{schema_name}.{table_name}"
                    for constraint in table_info.get("constraints", []):
                        if constraint["type"] != "FOREIGN KEY":
                            continue
                        related_id = f"{constraint['foreign_table_schema']}.{constraint['foreign_table_name']}"
                        if table_id in expanded and related_id not in expanded:
                            expanded.add(related_id)
                            changed = True
                        if related_id in expanded and table_id not in expanded:
                            expanded.add(table_id)
                            changed = True
        return sorted(expanded)

    def _filter_schema_by_table_ids(self, schema: dict[str, Any], table_ids: list[str]) -> dict[str, Any]:
        selected = set(table_ids)
        reduced: dict[str, Any] = {}
        for schema_name, tables in schema.items():
            for table_name, table_info in tables.items():
                if f"{schema_name}.{table_name}" not in selected:
                    continue
                reduced.setdefault(schema_name, {})
                reduced[schema_name][table_name] = table_info
        return reduced

    @staticmethod
    def _fingerprint(value: Any) -> str:
        return sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(left_value * right_value for left_value, right_value in zip(left, right))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def lexical_overlap_score(question: str, document_content: str) -> float:
    question_terms = set()
    for term in text_terms(question):
        question_terms.update(identifier_terms(term))
    if not question_terms:
        return 0.0
    overlap = question_terms.intersection(text_terms(document_content))
    return len(overlap) / len(question_terms)


def identifier_terms(identifier: str) -> set[str]:
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", identifier)
    raw_terms = text_terms(normalized.replace("_", " "))
    expanded = set(raw_terms)
    for term in raw_terms:
        expanded.update(simple_number_variants(term))
    return expanded


def text_terms(text: str) -> set[str]:
    return {term.lower() for term in re.findall(r"[A-Za-z0-9]+", text) if term}


def simple_number_variants(term: str) -> set[str]:
    variants = {term}
    if term.endswith("ies") and len(term) > 3:
        variants.add(f"{term[:-3]}y")
    elif term.endswith("ss"):
        pass
    elif term.endswith("s") and len(term) > 3:
        variants.add(term[:-1])
    elif term.endswith("y") and len(term) > 2:
        variants.add(f"{term[:-1]}ies")
    else:
        variants.add(f"{term}s")
    return variants
