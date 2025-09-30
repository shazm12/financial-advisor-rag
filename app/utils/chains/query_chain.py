from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any
from app.utils.retreiver import Retreiver


class QueryChain:

    def __init__(
        self, transactions_retriever: Retreiver, full_text_retriever: Retreiver
    ) -> None:
        """
        Initialize query chain with retrievers

        Args:
            transactions_retriever: Retriever for transaction data
            full_text_retriever: Retriever for full text data
        """
        self.transactions_retriever = transactions_retriever
        self.full_text_retriever = full_text_retriever
        self.chain = self._build_chain()

    def _build_finance_prompt(self):
        finance_prompt = PromptTemplate(
            input_variables=["transactions", "full_text", "user_query"],
            template="""
                    You are a professional financial advisor specializing in personal finance, credit card usage, and budgeting. 
                    You are provided with the user's credit card statement and a structured list of transactions.

                    ---  
                    📄 Full Statement:  
                    {full_text}  

                    💳 Transactions (structured):  
                    {transactions}  
                    ---

                    Your task:  
                    - Base all answers ONLY on the above statement and transactions.  
                    - If information is missing, politely explain what can/cannot be inferred.  
                    - Provide responses in a structured, easy-to-read format (use bullet points, categories, or tables if helpful).  
                    - Highlight key insights: spending categories, recurring charges, unusual expenses, or savings opportunities.  
                    - Offer actionable financial advice where relevant, but do not invent transactions not listed in the data.  

                    Now, answer the following user question:  
                    {user_query}
                """,
        )
        return finance_prompt

    def _build_llm(self):
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.4)
        return llm

    def _build_chain(self):

        chain = (
            RunnableLambda(lambda x: x)
            | RunnableParallel(
                {
                    "user_query": RunnablePassthrough(),
                    "transactions": self.transactions_retriever.retreive_using_similarity(),
                    "full_text": self.full_text_retriever.retreive_using_similarity(),
                }
            )
            | self._build_finance_prompt()
            | self._build_llm()
            | StrOutputParser()
        )
        return chain

    def invoke(self, query: str) :
        try:
            result = self.chain.invoke(query)
            return result
        except Exception as e:
            raise RuntimeError(f"Chain invocation failed: {str(e)}")