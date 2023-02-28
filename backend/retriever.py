import wikipedia
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import DensePassageRetriever
from yake import KeywordExtractor
import asyncio
import re

class TextRetrieverV2():
    def __init__(self) -> None:
        wikipedia.set_lang("en")
        self.kw_extractor = KeywordExtractor()
        self.document_store = InMemoryDocumentStore(embedding_dim=768, use_gpu=True)
        self.loop = asyncio.get_event_loop()
        self.retriever = DensePassageRetriever(
        document_store=self.document_store,
        query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
        passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
        use_gpu=True,
        use_fast_tokenizers=True
        )

    def __private_extractKeyWords(self, text) -> list:
        titles = []
        for i in text:
            temp_titles = self.kw_extractor.extract_keywords(i)
            for title in temp_titles:
                titles.append(title[0])
        return titles   


    async def fetch_wikipedia_page(self, title):
        wikiPages = wikipedia.search(title)
        wiki_pages = []
        for word in wikiPages:
            wiki_pages.append(word.lower())
        if len(wikiPages) > 0 and title.lower() in wiki_pages:
            try:
                page = wikipedia.page(title=wikiPages[0], auto_suggest=False)
                return page
            except wikipedia.DisambiguationError:
                pass 
                return None
        return None

    async def extract_wikipedia_pages(self, titles):
        tasks = [self.fetch_wikipedia_page(title) for title in titles]
        results = await asyncio.gather(*tasks)
        return results

    def __private_storeDocuments(self, documents):
        dicts = []
        for i in documents:
            sentences = []
            title = i.title
            summary = i.summary.split('.')
            for line in summary:
                sentences.append(line)
            text =  i.content.split('.')
            for line in text:
                sentences.append(line)
            for num, line in enumerate(sentences):
                dicts.append(
                {
                'content': line,
                'meta': {'title': title, "ID" : num}
                }
                )
        self.document_store.write_documents(dicts)
        self.document_store.update_embeddings(self.retriever)
        return self.document_store

    def public_extractPassage(self, claim, top_k):
        candidate_documents = self.retriever.retrieve(
            query=claim,
            top_k=top_k
        )
        evidence = ""
        for i in candidate_documents:
            content = i.content.replace('\n', '')
            content = re.sub("since (\d+)", r"since \1 to 2023", content)
            evidence += f"{content}\n"
        evidence = evidence.replace("–present", "-2023")
        return evidence
    
    def public_createDatabase(self, text) -> bool:
        # Example usage
        keyWords = self.__private_extractKeyWords(text)
        pages = self.loop.run_until_complete(self.extract_wikipedia_pages(keyWords))
        pages = [x for x in pages if x is not None]
        self.__private_storeDocuments(pages)
        return True

    def public_deleteDatabase(self) -> bool:
        self.document_store.delete_documents()
        return True