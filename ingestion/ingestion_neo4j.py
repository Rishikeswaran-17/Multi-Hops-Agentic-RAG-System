import os
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
import time

from langchain_openai import AzureOpenAIEmbeddings
from langchain_neo4j import Neo4jVector
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, PDFMinerLoader

# ---------- helpers ----------


def get_env(name: str, required=True, default=None):
    v = os.getenv(name, default)
    if required and not v:
        raise ValueError(f"Missing env var: {name}")
    return v


def _try_loader(loader_cls, path, **kwargs):
    try:
        return loader_cls(path, **kwargs).load()
    except Exception as e:
        print(f"[{loader_cls.__name__}] {os.path.basename(path)}: {e}")
        return []


def _sanitize_pdf(path: str) -> str:
    """Rewrite/repair a problematic PDF via pikepdf/QPDF; returns repaired path or original."""
    try:
        import pikepdf

        os.makedirs(".tmp_sanitized", exist_ok=True)
        out_path = os.path.join(".tmp_sanitized", os.path.basename(path))
        with pikepdf.open(path) as pdf:
            # linearize & clean objects; helps with bad resource refs/xrefs
            pdf.save(out_path, linearize=True)
        return out_path
    except Exception as e:
        print(f"[pikepdf] couldn't sanitize {os.path.basename(path)}: {e}")
        return path


def load_pdfs(docs_dir: str, default_password_env: str = "PDF_PASSWORD"):
    """
    Load PDFs with a tolerant fallback chain:
      1) PyPDFLoader (fast; supports passwords)
      2) PDFMinerLoader (robust text extractor)
      3) Sanitize via pikepdf, then retry 1) and 2)
    """
    docs = []
    pw = os.getenv(default_password_env, "") or None
    pdfs = sorted(Path(docs_dir).rglob("*.pdf"))
    print(f"Found {len(pdfs)} PDFs in {docs_dir}")
    skipped = 0

    for pdf_path in pdfs:
        path = str(pdf_path)

        # try PyPDF first
        items = _try_loader(PyPDFLoader, path, password=pw)
        if not items:
            # then PDFMiner
            items = _try_loader(PDFMinerLoader, path)

        if not items:
            # repair and retry
            repaired = _sanitize_pdf(path)
            if repaired != path:
                items = _try_loader(PyPDFLoader, repaired, password=pw)
                if not items:
                    items = _try_loader(PDFMinerLoader, repaired)

        if items:
            docs.extend(items)
        else:
            print(f"[skip] Unreadable PDF: {os.path.basename(path)}")
            skipped += 1

    print(f"Loaded {len(docs)} pages. Skipped {skipped} file(s).")
    return docs


# ---------- main pipeline ----------


def main():
    load_dotenv()
    docs_dir = get_env("DOCS_DIR")
    neo4j_url = get_env("NEO4J_URL")
    neo4j_username = get_env("NEO4J_USERNAME")
    neo4j_password = get_env("NEO4J_PASSWORD")
    endpoint = get_env("AZURE_OPENAI_ENDPOINT")
    api_key = get_env("AZURE_OPENAI_API_KEY")
    api_version = get_env("AZURE_OPENAI_API_VERSION")
    emb_deploy = get_env("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")
    index_name = get_env("INDEX_NAME")

    print(f"Loading PDFs from: {docs_dir}")
    raw_docs = load_pdfs(docs_dir)
    print(f"Loaded {len(raw_docs)} pages")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )
    docs = splitter.split_documents(raw_docs)
    print(f"Split into {len(docs)} chunks")

    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version,
        deployment=emb_deploy,
    )

    vectorstore = Neo4jVector.from_documents(
        [],
        embeddings,
        url=neo4j_url,
        username=neo4j_username,
        password=neo4j_password,
        index_name=index_name,
    )

    uuids = []
    with tqdm(total=len(docs), desc="Embedding & inserting", unit="chunk") as pbar:
        for doc in docs:
            t0 = time.time()
            ids = vectorstore.add_documents([doc])
            uuids.extend(ids)
            pbar.set_postfix({"last_time_sec": f"{time.time()-t0:.2f}"})
            pbar.update(1)

    print(f"✅ Upserted {len(uuids)} vectors")


if __name__ == "__main__":
    main()
