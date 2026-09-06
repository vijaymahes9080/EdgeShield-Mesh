"""
RAG Document Chunking and Metadata Indexer
Reads markdown files, parses YAML frontmatter and markdown sections, and produces structured document chunks.
"""
import os
import re
import hashlib
from typing import List, Dict, Any, Optional
from packages.shared.models import Citation


class DocumentChunk:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        version: str,
        title: str,
        section: str,
        content: str,
        effective_date: str,
        source_type: str,
        chunk_hash: str,
        page: Optional[int] = None
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.version = version
        self.title = title
        self.section = section
        self.content = content
        self.effective_date = effective_date
        self.source_type = source_type
        self.chunk_hash = chunk_hash
        self.page = page

    def to_citation(self, relevance_score: float) -> Citation:
        return Citation(
            document_id=self.document_id,
            version=self.version,
            title=self.title,
            section=self.section,
            page=self.page,
            snippet=self.content[:400],
            relevance_score=round(relevance_score, 3),
            doc_hash=self.chunk_hash,
            source_type=self.source_type
        )


class RunbookIndexer:
    def __init__(self, runbooks_dir: str = "data/runbooks"):
        self.runbooks_dir = runbooks_dir
        self.chunks: List[DocumentChunk] = []

    def load_and_index(self) -> List[DocumentChunk]:
        self.chunks = []
        if not os.path.exists(self.runbooks_dir):
            return self.chunks

        for filename in os.listdir(self.runbooks_dir):
            if filename.endswith(".md"):
                file_path = os.path.join(self.runbooks_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                file_chunks = self._parse_file(text, filename)
                self.chunks.extend(file_chunks)

        return self.chunks

    def _parse_file(self, text: str, filename: str) -> List[DocumentChunk]:
        chunks = []
        # Parse Frontmatter
        frontmatter = {}
        body = text
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                fm_text = parts[1]
                body = parts[2]
                for line in fm_text.strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        frontmatter[k.strip()] = v.strip().strip('"').strip("'")

        doc_id = frontmatter.get("document_id", filename.replace(".md", ""))
        version = frontmatter.get("version", "1.0.0")
        title = frontmatter.get("title", filename)
        effective_date = frontmatter.get("effective_date", "2026-01-01")
        source_type = frontmatter.get("source_type", "runbook")

        # Split body into sections by markdown headings ##
        sections = re.split(r"(^##\s+.+$)", body, flags=re.MULTILINE)
        current_section = "General"

        for i in range(len(sections)):
            part = sections[i].strip()
            if not part:
                continue
            if part.startswith("## "):
                current_section = part.replace("## ", "").strip()
            else:
                # Content under current_section
                content_hash = hashlib.sha256(part.encode("utf-8")).hexdigest()
                chunk_id = f"{doc_id}-{hashlib.md5(current_section.encode('utf-8')).hexdigest()[:6]}"
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=doc_id,
                    version=version,
                    title=title,
                    section=current_section,
                    content=part,
                    effective_date=effective_date,
                    source_type=source_type,
                    chunk_hash=content_hash
                )
                chunks.append(chunk)

        return chunks
