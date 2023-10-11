from dotenv import load_dotenv
from langchain.document_loaders import TextLoader
from langchain.chat_models import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

from langchain.chains import create_extraction_chain

load_dotenv()

def highlight_text(input_text):
    # extraction chain requires a schema to extract desired entities, so...
    schema = {
        "properties": {
            "symptom": {"type": "string"}
        },
        "required": ["symptom"], # explicit request to ONLY extract this stuff
    }

    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    chain = create_extraction_chain(schema, llm)

    # this returns a dictionary of symptoms
    extracted_terms = chain.run(input_text)

    # we want strings
    symptom_terms = [term_dict['symptom'] for term_dict in extracted_terms]

    return symptom_terms

def load_text(filepath):
    # Load text from the given file path using TextLoader
    loader = TextLoader(filepath)
    docs = loader.load()
    return docs

def summarize_text(input_text, symptom_terms):
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

    # Return the summarized result
    return stuff_chain.run(input_text)

if __name__ == "__main__":
    filepath = 'data/clean_transcripts/CAR0001.txt'

    # load call
    loaded_text = load_text(filepath)

    # highlights call
    highlighted_terms = highlight_text(loaded_text)

    # notes call
    result = summarize_text(loaded_text, highlighted_terms)
    print(result)