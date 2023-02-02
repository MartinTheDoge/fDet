# import transformers
# import wikipediaapi
import wikipedia
# import yake
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import DensePassageRetriever
import spacy
import en_core_web_sm
import re
# Concept
#class RetrieverV1():
#
#    def __init__(self) -> None:
#        self.model = transformers.AutoModelForTokenClassification.from_pretrained("vblagoje/bert-english-uncased-finetuned-pos")
#        self.tokenizer = transformers.AutoTokenizer.from_pretrained("vblagoje/bert-english-uncased-finetuned-pos")
#
#    def main(self, input) -> str:
#        pages = self.documentExt(self.TokenExt(input))
#        documents = self.storeDocuments(pages)
#        return self.extractPassage(documents, input)
#
#    def storeDocuments(self, documents):
#        dicts = []
#        for i in documents:
#            sentences = []
#            title = i.title
#            summary = i.summary.split('.')
#            for line in summary:
#                sentences.append(line)
#            text =  i.text.split('.')
#            for line in text:
#                sentences.append(line)
#            for num, line in enumerate(sentences):
#                dicts.append(
#                {
#                'content': line,
#                'meta': {'title': title, "ID" : num}
#                }
#                )
#        document_store = InMemoryDocumentStore(similarity="dot_product",embedding_dim=768)
#        document_store.write_documents(dicts)
#        return document_store
#    
#    def extractPassage(self, documents, claim):
#        retriever = EmbeddingRetriever(
#        document_store=documents,
#        embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1",
#        model_format="sentence_transformers"
#        )
#        documents.update_embeddings(retriever)
#        candidate_documents = retriever.retrieve(
#            query=claim,
#            top_k=3
#        )
#        return candidate_documents
#
#    def TokenExt(self, input) -> list:
#        pipe = transformers.pipeline('ner', model=self.model, tokenizer=self.tokenizer, aggregation_strategy="simple")
#        out = pipe(input)
#        # -------------------
#        # print(f"Token pipeline: {time.perf_counter()-start}")
#        # print(f"\n\t{out}")
#        # -------------------
#        words = []
#        for word in out:
#            if (word["entity_group"] == "PROPN" or word["entity_group"] == "NOUN" or word["entity_group"] == "ADP" or word["entity_group"] == "NUM"):
#                words.append(word)
#
#        comp = []
#        for j in range(len(words)):
#            Word = words[j]["entity_group"]
#            try:
#                if Word == "ADP":
#                    try:
#                        comp.append(input[word[j-1]["start"]:words[j+1]['end']])
#                    except:
#                        pass
#                if Word == "NUM":
#                    try:
#                        comp.append(input[word[j-1]["start"]:words[j+1]['end']])
#                        comp.append(input[word[j]["start"]:words[j+1]['end']])
#                        comp.append(input[word[j-1]["start"]:words[j]['end']])
#                    except:
#                        pass
#            except:
#                pass
#        # -------------------
#        # print(f"\t{comp}")
#        # -------------------
#        output = []
#        for word in words:
#            if word["entity_group"] != "ADP" or word["entity_group"] != "NUM":
#                output.append(input[word["start"]:word["end"]])
#
#
#        dups = list(dict.fromkeys(comp))
#        for dup in dups:
#            output.append(dup.strip())
#        # -------------------
#        # print(f"Title extraction: {time.perf_counter()-start}")
#        # -------------------
#        return output
#
#
#    def documentExt(self, titles) -> list:
#        wikipedia.set_lang("en")
#        pages = []
#        for title in titles:
#            wikiPages = wikipedia.search(title)
#            page = wikipedia.page(wikiPages[0])
#            pages.append(page)
#        # -------------------
#        # print(f"Document retrieve: {time.perf_counter()-start}")
#        # -------------------
#        return pages
#
#    def reranker(self, claim, docCorpus):
#        pass

class ClaimRetrieverV2():
    def __init__(self) -> None:
        wikipedia.set_lang("en")
        # self.kw_extractor = yake.KeywordExtractor()
        self.document_store = InMemoryDocumentStore(embedding_dim=768, use_gpu=True)
        self.retriever = DensePassageRetriever(
        document_store=self.document_store,
        query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
        passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
        use_gpu=True,
        use_fast_tokenizers=True,
        embed_title=True
        )
        spacy.prefer_gpu()
        self.nlp = spacy.load("en_core_web_sm")
        self.nlp = en_core_web_sm.load()

        
        
    def extractKeyWords(self, text) -> list:
        # Extract Subject
        titles = []
        title = ""
        doc=self.nlp(text)
        sub_toks = [tok for tok in doc]
        root = 0
        if len(sub_toks) > 0:
            for i, val in enumerate(sub_toks):
                if val.dep_ == "ROOT":
                    root = i
        for i in range(0, root + 1):
            if sub_toks[i].dep_ == "nsubj":
                title += f"{sub_toks[i]} "
            elif sub_toks[i].dep_ == "compound":
                title += f"{sub_toks[i]} "
            else:
                titles.append(title)
                title = ""
        titles.append(title)
        titles += title.split(" ")
        titles = [x for x in titles if x != '']       
        return titles   

    def findDocuments(self, titles) -> list:
        pages = []
        for title in titles:
            wikiPages = wikipedia.search(title)
            if len(wikiPages) > 0:
                try:
                    page = wikipedia.page(title=wikiPages[0])
                    if page not in pages:
                        pages.append(page) 
                except wikipedia.DisambiguationError:
                    pass 
                except wikipedia.PageError: 
                    page = wikipedia.page(title=wikiPages[0], auto_suggest=False)
                    if page not in pages:
                        pages.append(page) 
        return pages
    
    def storeDocuments(self, documents):
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
        return self.document_store

    def extractPassage(self, documents, claim):      
        documents.update_embeddings(self.retriever)
        candidate_documents = self.retriever.retrieve(
            query=claim,
            top_k=3
        )
        evidence = ""
        for i in candidate_documents:
            content = i.content.replace('\n', '')
            content = re.sub("since (\d+)", r"since \1 to 2023", content)
            evidence += f"{content}\n"
        evidence = evidence.replace("–present", "-2023")
        return evidence

    def main(self, text) -> str:
        keyWords = self.extractKeyWords(text)
        pages = self.findDocuments(keyWords)
        documentStore = self.storeDocuments(pages)
        Passages = self.extractPassage(documentStore, text)
        self.document_store.delete_documents()
        return Passages

class TextRetrieverV2():
    def __init__(self) -> None:
        wikipedia.set_lang("en")
        # self.kw_extractor = yake.KeywordExtractor()
        self.document_store = InMemoryDocumentStore(embedding_dim=768, use_gpu=True)
        self.retriever = DensePassageRetriever(
        document_store=self.document_store,
        query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
        passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
        use_gpu=True,
        use_fast_tokenizers=True,
        embed_title=True
        )
        spacy.prefer_gpu()
        self.nlp = spacy.load("en_core_web_sm")
        self.nlp = en_core_web_sm.load()

        
    def __private_extractKeyWords(self, text) -> list:
        # Extract Subject
        titles = []
        for i in text:
            title = ""
            doc=self.nlp(i)
            sub_toks = [tok for tok in doc]
            if len(sub_toks) > 0:
                for i, val in enumerate(sub_toks):
                    if val.dep_ == "ROOT":
                        root = i
            for i in range(0, len(sub_toks)):
                if sub_toks[i].dep_ == "nsubj":
                    title += f"{sub_toks[i]} "
                elif sub_toks[i].dep_ == "compound" or sub_toks[i].dep_ == "attr":
                    title += f"{sub_toks[i]} "
                else:
                    titles.append(title)
                    title = ""
            titles.append(title)
            titles += title.split(" ")
            titles = [x for x in titles if x != '']       
        return titles   

    def __private_findDocuments(self, titles) -> list:
        pages = []
        for title in titles:
            wikiPages = wikipedia.search(title)
            if len(wikiPages) > 0:
                try:
                    page = wikipedia.page(title=wikiPages[0])
                    if page not in pages:
                        pages.append(page) 
                except wikipedia.DisambiguationError:
                    pass 
                except wikipedia.PageError: 
                    page = wikipedia.page(title=wikiPages[0], auto_suggest=False)
                    if page not in pages:
                        pages.append(page) 
        return pages
    
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

    def public_extractPassage(self, claim):      
        candidate_documents = self.retriever.retrieve(
            query=claim,
            top_k=3
        )
        evidence = ""
        for i in candidate_documents:
            content = i.content.replace('\n', '')
            content = re.sub("since (\d+)", r"since \1 to 2023", content)
            evidence += f"{content}\n"
        evidence = evidence.replace("–present", "-2023")
        return evidence
    
    def public_createDatabase(self, text) -> bool:
        keyWords = self.__private_extractKeyWords(text)
        pages = self.__private_findDocuments(keyWords)
        self.__private_storeDocuments(pages)
        return True

    def public_deleteDatabase(self) -> bool:
        self.document_store.delete_documents()
        return True



