from langchain.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch

model="Universal-NER/UniNER-7B-all"

tokenizer = AutoTokenizer.from_pretrained(model)
pipeline = transformers.pipeline(
    "text-generation", #task
    model="Universal-NER/UniNER-7B-all",
    tokenizer=tokenizer,
    trust_remote_code=True,
    device_map="auto",
    torch_dtype=torch.bfloat16,
    max_length=1000,
    do_sample=True,
    top_k=10,
    num_return_sequences=1,
    eos_token_id=tokenizer.eos_token_id,

)

llm = HuggingFacePipeline(pipeline = pipeline, model_kwargs = {'temperature':0})

from langchain import PromptTemplate,  LLMChain

template = """
              A virtual assistant answers questions from a user based on the provided text.
              USER: Text: {input_text}
              ASSISTANT: I’ve read this text.
              USER: What describes {entity_type} in the text?
              ASSISTANT:
           """

prompt = PromptTemplate(template=template, input_variables=["input_text","entity_type"])

llm_chain = LLMChain(prompt=prompt, llm=llm)

# text2 ="""
# Apple Inc. is an American multinational technology company headquartered in Cupertino, California. Apple is the world's largest technology company by revenue, with US$394.3 billion in 2022 revenue.[6] As of March 2023, Apple is the world's biggest company by market capitalization.[7] As of June 2022, Apple is the fourth-largest personal computer vendor by unit sales and the second-largest mobile phone manufacturer in the world. It is often considered as one of the Big Five American information technology companies, alongside Alphabet (parent company of Google), Amazon, Meta Platforms, and Microsoft.
#
# Apple was founded as Apple Computer Company on April 1, 1976, by Steve Wozniak, Steve Jobs (1955–2011) and Ronald Wayne to develop and sell Wozniak's Apple I personal computer. It was incorporated by Jobs and Wozniak as Apple Computer, Inc. in 1977. The company's second computer, the Apple II, became a best seller and one of the first mass-produced microcomputers. Apple went public in 1980 to instant financial success. The company developed computers featuring innovative graphical user interfaces, including the 1984 original Macintosh, announced that year in a critically acclaimed advertisement called "1984". By 1985, the high cost of its products, and power struggles between executives, caused problems. Wozniak stepped back from Apple and pursued other ventures, while Jobs resigned and founded NeXT, taking some Apple employees with him.
#
# As the market for personal computers expanded and evolved throughout the 1990s, Apple lost considerable market share to the lower-priced duopoly of the Microsoft Windows operating system on Intel-powered PC clones (also known as "Wintel"). In 1997, weeks away from bankruptcy, the company bought NeXT to resolve Apple's unsuccessful operating system strategy and entice Jobs back to the company. Over the next decade, Jobs guided Apple back to profitability through a number of tactics including introducing the iMac, iPod, iPhone and iPad to critical acclaim, launching the "Think different" campaign and other memorable advertising campaigns, opening the Apple Store retail chain, and acquiring numerous companies to broaden the company's product portfolio. When Jobs resigned in 2011 for health reasons, and died two months later, he was succeeded as CEO by Tim Cook.
#
# Apple became the first publicly traded U.S. company to be valued at over $1 trillion in August 2018, then at $2 trillion in August 2020, and at $3 trillion in January 2022. As of April 2023, it was valued at around $2.6 trillion. The company receives criticism regarding the labor practices of its contractors, its environmental practices, and its business ethics, including anti-competitive practices and materials sourcing. Nevertheless, the company has a large following and enjoys a high level of brand loyalty. It has also been consistently ranked as one of the world's most valuable brands.
# """
# entity_type="Location"
# print(llm_chain.run({"input_text":text2,"entity_type":entity_type}))

text3 ="""
[**2163-12-16**] 3:09 PM
 LUMBO-SACRAL SPINE (AP & LAT)                                   Clip # [**Clip Number (Radiology) 37163**]
 Reason: eval for lbp
 ______________________________________________________________________________
 [**Hospital 2**] MEDICAL CONDITION:
  72 year old man with hx prostate ca and low back pain
 REASON FOR THIS EXAMINATION:
  eval for lbp
 ______________________________________________________________________________
                                 FINAL REPORT
 STUDY:  Lumbosacral spine, two views [**2163-12-16**].

 HISTORY:  72-year-old man with history of prostate cancer and lower back pain.

 FINDINGS:  Comparison is made to the MRI from [**2162-1-25**].

 There are five non-rib-bearing lumbar-type vertebral bodies.  There is some
 slight scoliosis of the lumbar spine with convexity to the right side.  There
 is marked loss of intervertebral disc height at L5/S1 with endplate sclerosis
 and vacuum gas phenomenon.  There is slight wedging of the L1 vertebral body
 anteriorly, which is stable when compared to the MRI from [**2162-1-16**].

 Abdominal aortic calcifications are seen. Sacroiliac joints and hip joints are
 grossly preserved.

 IMPRESSION:
 Degenerative changes seen of the L5/S1 disc space which allowing for
 differences in modality has increased since the MRI from [**2162-1-25**].  No
 new compression deformities noted.

"""
entity_type="Disease"
print(llm_chain.run({"input_text":text3,"entity_type":entity_type}))

# text2 ="""
# Apple Inc. is an American multinational technology company headquartered in Cupertino, California. Apple is the world's largest technology company by revenue, with US$394.3 billion in 2022 revenue.[6] As of March 2023, Apple is the world's biggest company by market capitalization.[7] As of June 2022, Apple is the fourth-largest personal computer vendor by unit sales and the second-largest mobile phone manufacturer in the world. It is often considered as one of the Big Five American information technology companies, alongside Alphabet (parent company of Google), Amazon, Meta Platforms, and Microsoft.
#
# Apple was founded as Apple Computer Company on April 1, 1976, by Steve Wozniak, Steve Jobs (1955–2011) and Ronald Wayne to develop and sell Wozniak's Apple I personal computer. It was incorporated by Jobs and Wozniak as Apple Computer, Inc. in 1977. The company's second computer, the Apple II, became a best seller and one of the first mass-produced microcomputers. Apple went public in 1980 to instant financial success. The company developed computers featuring innovative graphical user interfaces, including the 1984 original Macintosh, announced that year in a critically acclaimed advertisement called "1984". By 1985, the high cost of its products, and power struggles between executives, caused problems. Wozniak stepped back from Apple and pursued other ventures, while Jobs resigned and founded NeXT, taking some Apple employees with him.
#
# As the market for personal computers expanded and evolved throughout the 1990s, Apple lost considerable market share to the lower-priced duopoly of the Microsoft Windows operating system on Intel-powered PC clones (also known as "Wintel"). In 1997, weeks away from bankruptcy, the company bought NeXT to resolve Apple's unsuccessful operating system strategy and entice Jobs back to the company. Over the next decade, Jobs guided Apple back to profitability through a number of tactics including introducing the iMac, iPod, iPhone and iPad to critical acclaim, launching the "Think different" campaign and other memorable advertising campaigns, opening the Apple Store retail chain, and acquiring numerous companies to broaden the company's product portfolio. When Jobs resigned in 2011 for health reasons, and died two months later, he was succeeded as CEO by Tim Cook.
#
# Apple became the first publicly traded U.S. company to be valued at over $1 trillion in August 2018, then at $2 trillion in August 2020, and at $3 trillion in January 2022. As of April 2023, it was valued at around $2.6 trillion. The company receives criticism regarding the labor practices of its contractors, its environmental practices, and its business ethics, including anti-competitive practices and materials sourcing. Nevertheless, the company has a large following and enjoys a high level of brand loyalty. It has also been consistently ranked as one of the world's most valuable brands.
# """
# entity_type="Person"
# print(llm_chain.run({"input_text":text2,"entity_type":entity_type}))