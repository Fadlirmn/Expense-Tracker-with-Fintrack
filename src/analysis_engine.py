import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

class FinancialCompanion:
    def __init__(self):
        # Setup Groq (Llama 3)
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7, # Slightly creative but focused
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.output_parser = StrOutputParser()

    def _get_analysis_chain(self):
        """Creates the 'Natural Human' Agent Logic"""
        
        system_msg = """
        You are a sharp, pragmatic financial assistant. 
        Analyze the user's receipt and summarize it in ONE or TWO natural paragraphs.
        
        RULES FOR YOUR STYLE:
        1. **NO HEADERS** (Do not use "Context:", "Tip:", etc.).
        2. **NO ROBOTIC FLUFF** (Do not say "Dining out is a great way to unwind").
        3. **NO JUDGMENT** (Don't say "Good job" or "Bad job").
        
        HOW TO ANALYZE:
        - Weave the context (date/time) naturally into the sentence.
        - Mention the total and the merchant clearly.
        - If the spending seems high for the category (e.g., $50 for breakfast), point it out objectively.
        - If there is a practical tip (like loyalty cards or bulk buying), add it naturally at the end.
        
        Your goal is to sound exactly like a human accountant texting a client. Brief, smart, realistic.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_msg),
            ("human", """
            Analyze this receipt:
            Merchant: {merchant}
            Date: {date}
            Total: {total}
            Items: {items}
            """)
        ])
        
        return prompt | self.llm | self.output_parser

    def run_analysis(self, receipt_data):
        """Runs the single agent"""
        print("🤖 Financial Companion is reviewing your receipt...")
        
        chain = self._get_analysis_chain()
        
        # Prepare the list of items as a string
        items_list = ", ".join([f"{item.name} (${item.price})" for item in receipt_data.items])
        
        result = chain.invoke({
            "merchant": receipt_data.merchant,
            "date": receipt_data.date,
            "total": receipt_data.total,
            "items": items_list
        })
        
        return result

# Helper function
def run_agent_team(receipt_data):
    # We pass the full data object now for easier handling
    agent = FinancialCompanion()
    return agent.run_analysis(receipt_data)