from langchain.chains import RetrievalQA #检索QA链，在文档上进行检索
from langchain.chat_models import ChatOpenAI #openai模型
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document

documents = []
participants = self.dialogue.participants_to_export()

for turn in self.dialogue.turns:
    metadata = {"source": f"Dialogue File：{self.dialogue.file_path},"
                          f"speaker：{turn.speaker.name}，"
                          f"participant：{participants}"}
    turn_document = Document(page_content=turn.message, metadata=metadata.copy())
    documents.append(turn_document)
    
text_splitter = CharacterTextSplitter(chunk_size=3, chunk_overlap=1)
texts = text_splitter.split_documents(documents)
model_kwargs = {
    'device': 'cuda'
}
embeddings = HuggingFaceEmbeddings(model_name="model/text2vec-large-chinese", model_kwargs=model_kwargs)
docsearch = Chroma.from_documents(texts, embeddings, collection_name="state-of-history")

llm = ChatOpenAI(model_name = "gpt-3.5-turbo", temperature = 0.0, max_tokens=1024)

state_of_history = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever())