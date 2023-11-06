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

summary_prompt_template = """Write doctor's notes on the following patient consultation:
{transcript}

Ensure you include the terms: {symptoms}

Notes:"""
summary_prompt = PromptTemplate(
    input_variables=["transcript", "symptoms"],
    template=summary_prompt_template
)

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
        chunk_size = 1000,
        chunk_overlap = 0,
    )
    # If we pass in a list of strings it will not combine them, only separate
    # them.
    text = "\n\n".join(transcript)
    # print(f"transcript text:\n{text}")
    docs = text_splitter.create_documents([text])
    print(f"Docs #{len(docs)}")
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

async def summarize_text(transcript_docs, symptom_terms):
    # prompt string
    # this is where the highlights are passed to OpenAI through the prompt
    symptoms_text = ", ".join(symptom_terms)

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
    llm_chain = LLMChain(llm=llm, prompt=summary_prompt, verbose=True)

    stuff_chain = StuffDocumentsChain(
        llm_chain=llm_chain, document_variable_name="transcript"
    )
    print("before running summary chain")
    result = await stuff_chain.arun(
        input_documents=transcript_docs,
        symptoms=symptoms_text)
    print("after running summary chain")

    # Return the summarized result
    return result

async def create_transcript_notes(transcript):
    """Take notes on a transcript of a doctor-patient conversation."""
    def mk_line(line):
      speaker = "Doctor" if line['speaker'] == "Guest-1" else "Patient"
      text = line['text']
      return f"{speaker}: {text}"
    formatted_transcript = [mk_line(line) for line in transcript] 
    docs = split_transcript(formatted_transcript)
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
            # transcript = transcript[:LINE_COUNT]
            docs = split_transcript(transcript)
            print(f"docs #{len(docs)}")
            # Get important terms
            highlights = await highlight_text(docs)
            # notes call
            result = await summarize_text(docs, highlights)
            print(result)
    asyncio.run(main())
