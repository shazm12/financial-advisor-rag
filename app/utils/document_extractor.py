from langchain_community.document_loaders import PyPDFLoader
from langchain_core.runnables import RunnableParallel, RunnableLambda
from app.utils.decorators.singleton import singleton
from app.utils.tools.table_extractor import TableExtractionTool


@singleton
class DocumentExtractor:
    
    def __init__(self):
        self.table_extractor_tool = TableExtractionTool()
        
    def extract_statement(self, pdf_path):
        
        extraction_chain = (
            RunnableLambda(lambda x: x) # pass through input
            | RunnableParallel({
                "full_text": RunnableLambda(self._extract_text),
                "tables_data": RunnableLambda(self._extract_tables),
                "metadata": RunnableLambda(self._create_metadata)
            })
        )
        return extraction_chain.invoke(pdf_path)
    
    def _extract_text(self, pdf_path):
        
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        return "\n".join([page.page_content for page in docs])
        
    def _extract_tables(self, pdf_path):
        return self.table_extractor_tool.run(pdf_path)
    
    def _create_metadata(self,pdf_path):
        with open(pdf_path, 'rb') as f:
            pages = f.read().count(b'/Type/Page')
        
        return {
            'source': pdf_path,
            'document_type': 'bank_statement',
            'total_pages': pages
        }
    
    
    