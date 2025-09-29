from langchain_community.vectorstores.redis.base import Redis


class Retreiver:
    def __init__(self) -> None:
        pass       
    
    def set_retreiver(self, rds:Redis=None):
        self.rds = rds

    def retreive_using_similarity(self, text: str):
        retreiver = self.rds.as_retriever(search_type="similarity")
        return retreiver.invoke(text)
