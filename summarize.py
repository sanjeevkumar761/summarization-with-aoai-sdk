import os  
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI  

endpoint = os.getenv("ENDPOINT_URL", "Your Azure OpenAI endpoint URL")  
deployment = os.getenv("DEPLOYMENT_NAME", "Your Azure OpenAI model deployment name")  
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "Your Azure OpenAI API key")  
form_recognizer_endpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT", "Your Azure Document Intelligence endpoint URL")
form_recognizer_key = os.getenv("FORM_RECOGNIZER_KEY", "Your Azure Document Intelligence API key")

# Initialize Azure OpenAI client with key-based authentication
client = AzureOpenAI(  
    azure_endpoint=endpoint,  
    api_key=subscription_key,  
    api_version="2024-05-01-preview",  
)  

# Initialize Form Recognizer client
form_recognizer_client = DocumentAnalysisClient(
    endpoint=form_recognizer_endpoint,
    credential=AzureKeyCredential(form_recognizer_key)
)

def extract_text_from_page(pdf_path, page_number):
    with open(pdf_path, "rb") as f:
        poller = form_recognizer_client.begin_analyze_document("prebuilt-document", document=f)
        result = poller.result()

    extracted_text = ""
    for page in result.pages:
        if page.page_number == page_number:
            for line in page.lines:
                extracted_text += line.content + "\n"
            break  # Exit the loop once the desired page is processed

    return extracted_text

# Example usage
pdf_path = "path/to/your/pdf/file.pdf"
page_number = 10  # Specify the page number you want to extract
page_text = extract_text_from_page(pdf_path, page_number)
print(page_text)

# Prepare the chat prompt  
chat_prompt = [
    {
        "role": "system",
        "content": "You are an AI assistant that helps summarize a given document in 5-bullet points."
    },
    {
        "role": "user",
        "content": "Summarize the document given here. " + f"Here is is the document: {page_text}"  # Replace with the actual user prompt
    }
]  

# Generate the completion  
completion = client.chat.completions.create(
    messages=chat_prompt,
    model=deployment  # Assuming the deployment name is the model name
)

# Access the content from the completion object
content = completion.choices[0].message.content
print(content)