from dotenv import load_dotenv

from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

# from langchain.vectorstores import Chroma

load_dotenv()

# load
embeddings = OpenAIEmbeddings()
loader = TextLoader('data/clean_transcripts/CAR0001.txt')
docs = loader.load()

# clean
# text_splitter = CharacterTextSplitter(chunk_size=2500, chunk_overlap=0)
# texts = text_splitter.split_documents(docs)

# store in ChromaDB
# docquery = Chrome.from_documents(text, embeddings)

# summarize option 1
# llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
# chain = load_summarize_chain(llm, chain_type="stuff")
#
# print(chain.run(docs))

# summarize option 2
# Define prompt
prompt_template = """Write a concise summary of the following:
"{text}"
CONCISE SUMMARY:"""
prompt = PromptTemplate.from_template(prompt_template)

llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
llm_chain = LLMChain(llm=llm, prompt=prompt)

stuff_chain = StuffDocumentsChain(
    llm_chain=llm_chain, document_variable_name="text"
)

docs = loader.load()
print(stuff_chain.run(docs))