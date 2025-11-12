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
                    - Also highlight any EMI spends and interest charged if found ONLY.
                    - Give the report/answer in a rich markdown format with proper line breaks and indentation.
                    
                    QUESTION: {user_query}

                    IMPORTANT OUTPUT RULES:
                    - Start each section with ### followed by a space and title
                    - Add blank line after each header
                    - Add blank line before bullet lists
                    - Add blank line after bullet lists
                    - Use * for bullet points with a space after

                    CRITICAL: You MUST format your response EXACTLY like this example. Add blank lines between sections.

                    ### Section Name

                    Explanation text here with proper spacing.

                    #### Subsection

                    * Point one
                    * Point two
                    * Point three

                    Another paragraph here.

                    ### Another Section

                    More content here.

                    Now answer the question. Remember: blank line after headers, blank line before lists, blank line after lists.
                """,
        )
        return finance_prompt

    def _build_llm(self):
        llm = ChatGroq(model="openai/gpt-oss-120b",
                       temperature=0.4, streaming=True)
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

    async def generate_response(self, query: str):
        try:
            async for chunk in self.chain.astream(query):
                if chunk:
                    yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
            raise RuntimeError(f"Chain invocation failed: {str(e)}")
