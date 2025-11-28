import os
from langchain_groq import ChatGroq 
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- 1. Define the Schema (Same as before) ---
class ReceiptItem(BaseModel):
    name: str = Field(description="Name of the item purchased")
    price: Optional[float] = Field(description="Price of the individual item")

class ReceiptData(BaseModel):
    merchant: str = Field(description="Name of the store or merchant")
    date: str = Field(description="Date of transaction in YYYY-MM-DD format.")
    total: float = Field(description="The final total amount paid")
    currency: str = Field(description="Currency code (USD, EUR, etc.)")
    category: str = Field(description="Category (Groceries, Transport, Dining, Utilities)")
    items: List[ReceiptItem] = Field(description="List of line items")

# --- 2. Setup DeepSeek LLM ---
# We use ChatOpenAI class but point it to DeepSeek's server
llm = ChatGroq(
    model="llama-3.3-70b-versatile", # or "llama3-70b-8192"
    temperature=0.0,
    api_key=os.getenv("GROQ_API_KEY")
)

# --- 3. Setup the Parser ---
# This tells the LLM exactly how to format the JSON
parser = PydanticOutputParser(pydantic_object=ReceiptData)

# --- 4. The Extraction Function ---
def extract_structured_data(raw_ocr_text: str):
    print(f"--- Sending {len(raw_ocr_text)} chars to DeepSeek ---")

    # Define the prompt with instructions
    prompt = PromptTemplate(
        template="""
        You are an expert receipt assistant. Extract information from the following OCR text.
        
        OCR TEXT:
        {text}
        
        INSTRUCTIONS:
        1. Fix OCR errors (e.g., 'S' instead of '5').
        2. Extract merchant, date, total, and items.
        3. Return ONLY the JSON object.
        
        {format_instructions}
        """,
        input_variables=["text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Create the chain: Prompt -> LLM -> Parser
    chain = prompt | llm | parser

    try:
        result = chain.invoke({"text": raw_ocr_text})
        return result
    except Exception as e:
        print(f"DeepSeek Extraction Error: {e}")
        return None