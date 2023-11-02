from dotenv import load_dotenv
import aiofiles
from langchain.document_loaders import TextLoader
from langchain.chat_models import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
import asyncio
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_extraction_chain

def load_text(filepath):
    # Load text from the given file path using TextLoader
    loader = TextLoader(filepath)
    docs = loader.load()
    return docs

def split_transcript(transcript):
    """
    Split an array of strings transcribing a doctor-patient conversation into
    documents for processing.
    """
    # We will probably want to use a more advanced splitter that is aware of
    # who is talking. See transcript section in `README.md`.
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size = 100, # TODO just for testing
        chunk_overlap = 0,
    )
    # If we pass in a list of strings it will not combine them, only separate
    # them.
    text = "\n\n".join(transcript)
    docs = text_splitter.create_documents([text])
    print(docs)
    return docs

async def highlight_text(input_text):
    # extraction chain requires a schema to extract desired entities, so...
    schema = {
        "properties": {
            "symptom": {"type": "string"}
        },
        "required": ["symptom"], # explicit request to ONLY extract this stuff
    }

    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    chain = create_extraction_chain(schema, llm)
    print("before running highlight chain")

    # this returns a dictionary of symptoms
    extracted_terms = await chain.arun(input_text)

    # we want strings
    symptom_terms = [term_dict['symptom'] for term_dict in extracted_terms]
    print(f"after running highlight chain {symptom_terms}")

    return symptom_terms

async def summarize_text(input_text, symptom_terms):
    # prompt string
    prompt_template = """Write doctor's notes on the following patient visit conversation:
"{text}"
Notes:"""
    # this is where the highlights are passed to OpenAI through the prompt
    if symptom_terms:
        prompt_template += f"\nEnsure to include the terms: {', '.join(symptom_terms)}"
    prompt = PromptTemplate.from_template(prompt_template)

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    stuff_chain = StuffDocumentsChain(
        llm_chain=llm_chain, document_variable_name="text"
    )
    print("before running summary chain")
    result = await stuff_chain.arun(input_text)
    print("after running summary chain")

    # Return the summarized result
    return result

async def create_transcript_notes(transcript):
    """Take notes on a transcript of a doctor-patient conversation."""
    transcript = [f"{line['speaker']}: {line['text']}" for line in transcript] 
    docs = split_transcript(transcript)
    # Get important terms
    highlights = await highlight_text(docs)
    # notes call
    return await summarize_text(docs, highlights)

if __name__ == "__main__":
    # How many lines from the transcript to use.
    LINE_COUNT = 15
    filepath = './data/clean_transcripts/CAR0001.txt'
    load_dotenv()
    async def main():
        async with aiofiles.open(filepath) as file:
            # load file, turn into transcript, contract transcript, split
            # transcript into docs.
            text = await file.read()
            transcript = text.split("\n\n")
            # contracting transcript to lower api usage when testing.
            transcript = transcript[:LINE_COUNT]
            docs = split_transcript(transcript)
            print(f"docs #{len(docs)}")
            # Get important terms
            highlights = await highlight_text(docs)
            # notes call
            result = await summarize_text(docs, highlights)
            print(result)
    asyncio.run(main())
