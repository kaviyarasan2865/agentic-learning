"""
PDF Processor Module

Handles PDF parsing and text extraction for event reports.
Uses LangChain document loaders for efficient processing.
"""

import os
from typing import List, Optional
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


class PDFProcessor:
    """Handles PDF processing and text extraction for event reports."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the PDF processor.
        
        Args:
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_pdf(self, pdf_path: str) -> List[Document]:
        """
        Load and parse a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of Document objects containing the PDF content
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            # Load PDF using LangChain's PyPDFLoader
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            print(f"Successfully loaded PDF: {pdf_path}")
            print(f"Total pages: {len(documents)}")
            
            return documents
            
        except Exception as e:
            raise Exception(f"Error loading PDF {pdf_path}: {str(e)}")
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks for processing.
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of chunked Document objects
        """
        try:
            chunked_docs = self.text_splitter.split_documents(documents)
            print(f"Split {len(documents)} documents into {len(chunked_docs)} chunks")
            return chunked_docs
            
        except Exception as e:
            raise Exception(f"Error splitting documents: {str(e)}")
    
    def process_pdf(self, pdf_path: str) -> List[Document]:
        """
        Complete PDF processing pipeline.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of processed Document chunks
        """
        print(f"Processing PDF: {pdf_path}")
        
        # Load PDF
        documents = self.load_pdf(pdf_path)
        
        # Split into chunks
        chunked_docs = self.split_documents(documents)
        
        print(f"PDF processing completed. Generated {len(chunked_docs)} chunks.")
        return chunked_docs
    
    def extract_metadata(self, documents: List[Document]) -> dict:
        """
        Extract metadata from processed documents.
        
        Args:
            documents: List of Document objects
            
        Returns:
            Dictionary containing metadata
        """
        metadata = {
            "total_chunks": len(documents),
            "total_pages": len(set(doc.metadata.get("page", 0) for doc in documents)),
            "source_file": documents[0].metadata.get("source", "unknown") if documents else "unknown",
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap
        }
        
        return metadata


def create_sample_event_report() -> str:
    """
    Create a sample event report for testing purposes.
    
    Returns:
        Path to the created sample PDF
    """
    # This would typically create a sample PDF
    # For now, we'll return a placeholder path
    sample_path = "data/sample_event_report.pdf"
    
    # Create the data directory if it doesn't exist
    Path("data").mkdir(exist_ok=True)
    
    print(f"Sample event report path: {sample_path}")
    print("Please place your event report PDF in the data/ directory")
    
    return sample_path
