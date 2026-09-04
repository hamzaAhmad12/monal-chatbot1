"""Command-line entry points for the Monal RAG application."""

from pathlib import Path
import sys

from .retriever import CHROMA_DIR, answer_question, build_vector_store, load_documents


def ingest() -> None:
	"""Build the local Chroma database from the active knowledge-base PDF."""
	store = build_vector_store()
	count = store._collection.count()
	print(f"Indexed {len(load_documents())} pages into {count} chunks.")
	print(f"Vector database: {CHROMA_DIR}")


def chat() -> None:
	"""Run an interactive terminal conversation with the Monal assistant."""
	print("Monal Peshawar terminal chat")
	print("Type 'exit' or 'quit' to stop.\n")
	while True:
		try:
			question = input("You: ").strip()
		except (EOFError, KeyboardInterrupt):
			print("\nGoodbye!")
			return
		if question.lower() in {"exit", "quit"}:
			print("Goodbye!")
			return
		if not question:
			continue
		try:
			answer, _ = answer_question(question)
			print(f"\nMonal: {answer}\n")
		except (FileNotFoundError, RuntimeError) as error:
			print(f"\nError: {error}\n")
		except Exception as error:
			print(f"\nThe AI service could not answer: {error}\n")


def main(command: str | None = None) -> None:
	"""Dispatch the package command-line interface."""
	selected_command = command or (sys.argv[1] if len(sys.argv) > 1 else "chat")
	if selected_command == "ingest":
		ingest()
	elif selected_command == "crawl":
		from .crawler import crawl_and_update

		crawl_and_update()
	elif selected_command == "chat":
		chat()
	else:
		raise SystemExit("Usage: python -m rag [chat|ingest|crawl]")
