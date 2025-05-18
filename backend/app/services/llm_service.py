import asyncio
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import google.generativeai as genai
import groq
import openai
from app.config import settings
from app.models.document import DocumentResponse
from app.models.query import Citation, DocumentQueryResponse, QueryRequest
from app.services.vector_store import VectorStore
from sentence_transformers import SentenceTransformer

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with LLM providers and processing queries"""

    def __init__(self):
        """Initialize the LLM service with configured provider"""
        self.provider = settings.llm.provider.lower()
        self.vector_store = VectorStore()

        if self.provider == "huggingface":
            #use a model specifically for text generation (eg: gpt2)
            #the embedding model (like all-MiniLM-L6-v2) is handled by VectorStore
            self.generation_model_name = "gpt2"  #for example, could be a setting
            try:
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.generation_model_name,
                    max_length=1000, 
                    temperature=settings.llm.temperature,
                )
                logger.info(
                    f"HuggingFace text generation pipeline initialized with model: {self.generation_model_name}"
                )

            except Exception as e:
                logger.error(
                    f"Error initializing HuggingFace text generation pipeline: {str(e)}",
                    exc_info=True,
                )
                
                raise
        elif self.provider == "google":
            if not settings.GOOGLE_API_KEY:
                logger.error(
                    "GOOGLE_API_KEY is not set. Cannot initialize Google Gemini."
                )
                raise ValueError("GOOGLE_API_KEY is not set.")
            try:
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                
                self.google_model = genai.GenerativeModel("gemini-2.0-flash")
                logger.info("Google Gemini model initialized: gemini-2.0-flash")
            except Exception as e:
                logger.error(
                    f"Error initializing Google Gemini model: {str(e)}", exc_info=True
                )
                raise
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def process_query(
        self, query: QueryRequest, documents: List[DocumentResponse]
    ) -> List[DocumentQueryResponse]:
        """Process a query against documents"""
        document_responses = []

        document_ids = (
            query.document_ids if query.document_ids else [doc.id for doc in documents]
        )

        if query.max_documents and len(document_ids) > query.max_documents:
            document_ids = document_ids[: query.max_documents]

        search_results = await self.vector_store.search(
            query=query.query,
            document_ids=document_ids,
            limit=settings.vector_db.search_limit
            * len(document_ids), 
        )

        combined_context = ""
        for i, result in enumerate(search_results):
            doc_id = result["metadata"].get("document_id", "Unknown Document")
           
            doc = next((d for d in documents if d.id == doc_id), None)
            doc_name = doc.name if doc else doc_id
            page_number = result["metadata"].get("page_number", "Unknown Page")
            chunk_content = result["content"]

            combined_context += (
                f"## Document: {doc_name}, Page: {page_number}\n{chunk_content}\n\n"
            )

        synthesized_answer, citations = await self._generate_answer(
            query=query.query,
            chunks=search_results,  
            citation_level=query.citation_level,  
        )

        combined_response = DocumentQueryResponse(
            document_id="combined",  
            document_name="Combined Documents", 
            extracted_answer=synthesized_answer,
            citations=citations, 
            relevance_score=1.0,  
        )

        return [
            combined_response
        ] 

    async def _generate_answer(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        citation_level: str,
    ) -> Tuple[str, List[Citation]]:
        """Generate an answer from document chunks using the configured LLM"""
        citations = []
        #prepare context from chunks
        #concatenate content from all relevant chunks
        context_with_sources = ""
        for i, chunk in enumerate(chunks):
            doc_id = chunk["metadata"].get("document_id", "Unknown Document")
            doc_name = chunk["metadata"].get(
                "name", doc_id
            )  # Use document name from metadata if available
            page_number = chunk["metadata"].get("page_number", "Unknown Page")
            context_with_sources += (
                f"## Document: {doc_name}, Page: {page_number}\n{chunk["content"]}\n\n"
            )

        #for models with strict context windows like some guggingface models we need to truncate the context string based on token count.

        prompt = f"""
Human:
        You are an AI assistant that provides accurate information based on document content.
        
        CONTEXT:
        {context_with_sources}
        
        USER QUERY: {query}
        
        Provide a comprehensive answer to the query based ONLY on the information in the CONTEXT.
        If the answer cannot be determined from the context, say "I don't have enough information to answer this question based on the document content."
        
        Format your response in the following structure:
        
        # Answer
        [Your detailed answer here with proper markdown formatting]
        
        # Citations
        For each piece of information in your answer, provide a citation in this format:
        - [Document Name, Page X]: "[exact quoted text from the document]"
        
        Guidelines:
        1. Use proper markdown formatting:
           - Use **bold** for emphasis
           - Use bullet points for lists
           - Use proper headings with # for sections
           - Use code blocks with ``` for any code or technical content
           - Use blockquotes with > for important quotes
        
        2. Citation Rules:
           - Each major point in your answer must have at least one citation
           - Include the complete quoted text for each citation
           - Do not truncate or modify the quoted text
           - If a page number is available, include it
           - Format citations as a bulleted list
        
        3. Answer Structure:
           - Start with a brief overview
           - Break down complex topics into sections
           - Use bullet points for lists of features or characteristics
           - End with a summary if appropriate
        
        Example format:
        # Answer
        [Your detailed answer with proper markdown formatting]
        
        # Citations
        - [Document Name, Page 1]: "[exact quoted text from document]"
        - [Another Document Name, Page 5]: "[exact quoted text from document]"

Assistant:
        """

        response = ""
        try:
            if settings.llm.provider.lower() == "openai":
                response = await self._call_openai(prompt)
            elif settings.llm.provider.lower() == "google":
                response = await self._call_google(prompt)
            elif settings.llm.provider.lower() == "groq":
                response = await self._call_groq(prompt)
            else:
                raise ValueError(f"Unsupported LLM provider: {settings.llm.provider}")

        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            return f"Error generating answer: {str(e)}", []

        answer_section = ""
        citations_section = ""

        if "Answer:" in response:
            parts = response.split("Answer:", 1)
            answer_section = parts[1].strip()
            if "Citations:" in answer_section:
                parts = answer_section.split("Citations:", 1)
                answer = parts[0].strip()
                citations_section = parts[1].strip()
            else:
                answer = answer_section  
        else:
            answer = response.strip()

        if citations_section:
            citation_lines = citations_section.split("\n")
            current_citation = None
            current_quote = []

            for line in citation_lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith("["):
                    if current_citation and current_quote:
                        current_citation.quote = " ".join(current_quote)
                        citations.append(current_citation)
                        current_quote = []

                    if line.startswith("-"):
                        line = line[1:].strip()

                    match = re.match(r'\[(.*?)(?:,\s*Page\s*(\d+))?\]:\s*"(.*)', line)
                    if match:
                        doc_name = match.group(1).strip()
                        page_num = match.group(2) if match.group(2) else None
                        quote = match.group(3).strip()
                        current_citation = Citation(
                            document_name=doc_name, page_number=page_num, quote=quote
                        )
                        current_quote.append(quote)
                elif current_citation:
                    current_quote.append(line)

            if current_citation and current_quote:
                current_citation.quote = " ".join(current_quote)
                citations.append(current_citation)

        return answer, citations

    async def _call_huggingface(self, prompt: str) -> str:
        """Internal method to call Hugging Face models for text generation."""
        logger.info(
            f"Calling Hugging Face with prompt: {prompt[:200]}..."
        ) 
        try:
            max_model_input_length = self.pipeline.model.config.max_position_embeddings

            generate_kwargs = {
                #setting hard limit on *total* sequence length(input + generated)
                "max_length": max_model_input_length,
                "temperature": settings.llm.temperature,
                #explicitly set max_new_tokens to None to prioritize max_length
                "max_new_tokens": None,
                "truncation": True,
            }

            result = self.pipeline(
                prompt,
                **generate_kwargs, 
            )

            logger.info("Hugging Face generation successful.")  
            if (
                result
                and isinstance(result, list)
                and len(result) > 0
                and "generated_text" in result[0]
            ):
                generated_text_with_prompt = result[0]["generated_text"]
                start_index = len(
                    self.pipeline.tokenizer.encode(prompt, add_special_tokens=False)
                )
                generated_text = generated_text_with_prompt[start_index:].strip()
                logger.debug(
                    f"Generated text (stripped prompt): {generated_text[:200]}..."
                ) 
                return generated_text
            else:
                logger.warning("Hugging Face pipeline returned unexpected format.")
                return "Error: Unable to generate text from Hugging Face."

        except Exception as e:
            logger.error(
                f"Error processing with Hugging Face: {str(e)}", exc_info=True
            )  
            return f"Error processing with Hugging Face: {str(e)}"

    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides accurate information based on document content.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=1000,
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    async def _call_google(self, prompt: str) -> str:
        """Internal method to call Google Gemini model for text generation."""
        logger.info(
            f"Calling Google Gemini with prompt: {prompt[:200]}..."
        )  
        try:
            
            generation_config = {
                "temperature": settings.llm.temperature,
                "max_output_tokens": 1000, 
            }

            response = self.google_model.generate_content(
                prompt, generation_config=generation_config
            )

            logger.info("Google Gemini call successful.")  
            if (
                response
                and response.candidates
                and response.candidates[0].content
                and response.candidates[0].content.parts
            ):
                generated_text = "".join(
                    [part.text for part in response.candidates[0].content.parts]
                )
                logger.debug(
                    f"Generated text from Gemini: {generated_text[:200]}..."
                )  
                return generated_text.strip()
            else:
                logger.warning("Google Gemini generation returned no text.")
                return "Error: Google Gemini generation returned no text."

        except Exception as e:
            logger.error(
                f"Error processing with Google Gemini: {str(e)}", exc_info=True
            )  
            return f"Error processing with Google Gemini: {str(e)}"

    async def _call_groq(self, prompt: str) -> str:
        """Call Groq API"""
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides accurate information based on document content.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=1000,
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise


