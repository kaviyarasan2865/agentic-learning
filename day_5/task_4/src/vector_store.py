"""
Vector Store Module

Handles document storage and retrieval using DocArrayInMemorySearch.
Provides semantic search capabilities for event report analysis.
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path

from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.schema.retriever import BaseRetriever


class VectorStoreManager:
    """Manages vector storage and retrieval for event report documents."""
    
    def __init__(self, persist_directory: str = "data/docarray_db", embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the vector store manager.
        
        Args:
            persist_directory: Directory to store vector data
            embedding_model: HuggingFace embedding model to use
        """
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.vector_store = None

    def create_vector_store(self, documents: List[Document]) -> DocArrayInMemorySearch:
        """
        Create and populate the vector store with documents.
        
        Args:
            documents: List of documents to store
            
        Returns:
            Configured vector store
        """
        try:
            # Ensure documents have proper metadata
            processed_documents = []
            for i, doc in enumerate(documents):
                # Create a new document with proper metadata
                processed_doc = Document(
                    page_content=doc.page_content,
                    metadata={
                        "source": doc.metadata.get("source", "unknown"),
                        "page": doc.metadata.get("page", i),
                        "chunk_id": i
                    }
                )
                processed_documents.append(processed_doc)
            
            # Create vector store with processed documents
            self.vector_store = DocArrayInMemorySearch.from_documents(
                documents=processed_documents,
                embedding=self.embeddings
            )
            return self.vector_store
            
        except Exception as e:
            print(f"Error creating vector store: {str(e)}")
            # Fallback: create empty vector store and add documents one by one
            self.vector_store = DocArrayInMemorySearch(embedding=self.embeddings)
            for doc in documents:
                try:
                    self.vector_store.add_documents([doc])
                except Exception as add_error:
                    print(f"Error adding document: {str(add_error)}")
            return self.vector_store

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """
        Perform similarity search on the vector store.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        if not self.vector_store:
            raise Exception("Vector store not initialized.")
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            print(f"Error in similarity search: {str(e)}")
            # Return empty list if search fails
            return []

    def get_retriever(self, search_type: str = "similarity", k: int = 5) -> BaseRetriever:
        """
        Get a retriever for the vector store.
        
        Args:
            search_type: Type of search to perform
            k: Number of results to return
            
        Returns:
            Configured retriever
        """
        if not self.vector_store:
            raise Exception("Vector store not initialized.")
        
        if search_type == "similarity":
            return self.vector_store.as_retriever(search_kwargs={"k": k})
        else:
            raise ValueError(f"Unsupported search type: {search_type}")

    def get_vector_store_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary containing vector store statistics
        """
        if not self.vector_store:
            return {"status": "not_initialized"}
        
        try:
            # For DocArrayInMemorySearch, we can get basic info
            return {
                "status": "initialized",
                "embedding_model": self.embedding_model,
                "store_type": "DocArrayInMemorySearch"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
