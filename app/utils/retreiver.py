from langchain_community.vectorstores.redis.base import Redis


class Retreiver:
    def __init__(self, rds: Redis=None) -> None:
        self.rds = rds       
    
    def retreive_using_similarity(self):
        if self.rds is None:
            raise ValueError("Retreiver is not initialized")
        retreiver = self.rds.as_retriever(search_type="similarity",search_kwargs={"k": 4})
        return retreiver
