from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph,START,END
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from pathlib import Path
import base64
from io import BytesIO
#from mistralai import Mistral
from typing_extensions import TypedDict
import os
from dotenv import load_dotenv

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# Initialize clients
summary_llm = ChatGroq(
    model_name="mixtral-8x7b-32768",
    temperature=0
)
analyzer_llm = ChatGroq(
    model_name="DeepSeek-R1-Distill-Llama-70B",
    temperature=0.6
)


def extracttpdf(pdf_name):
  uploaded_pdf = client.files.upload(
    file={
        "file_name": "pdf_name",
        "content": open(pdf_name, "rb"),
    },
    purpose="ocr"
  )
  #
  signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)
  #
  ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": signed_url.url,
    }
  )
  #
  text = "\n\n".join([page.markdown for page in ocr_response.pages])
  return text

#
class MedicalAnalysisState(TypedDict):
    file_name : str
    context:str
    analysis_result: str
    summary: str
    validation_result: str 


def create_medical_analysis_chain():
    # Define the nodes (agents) in our graph
    def extract_context(state:MedicalAnalysisState):
        print("----------------------------------------------------")
        print("-----------Extracting context from PDF--------------")
        print("----------------------------------------------------")
        pdf_name  = state['file_name']
        text = extracttpdf(pdf_name)
        state["context"] = text
        return state
    def analyze_document(state:MedicalAnalysisState):
        print("----------------------------------------------------")
        print("------------Analyzing context from PDF--------------")
        print("----------------------------------------------------")
        messages = state["context"]
        document_content = messages
        
        # Use Langchain groq for medical analysis
        messages = [
            SystemMessage(content="""You are a medical document analyzer. Extract key information and format it in markdown with the following sections:

### Date of Incident
- Specify the date when the medical incident occurred

### Medical Facility
- Name of the medical center/hospital
- Location details

### Healthcare Providers
- Primary physician
- Other medical staff involved

### Patient Information
- Chief complaints
- Vital signs
- Relevant medical history

### Medications
- Current medications
- New prescriptions
- Dosage information

Please ensure the response is well-formatted in markdown with appropriate headers and bullet points."""),
            HumanMessage(content=document_content)
        ]
        response = analyzer_llm.invoke(messages)
        
        state["analysis_result"] = response.content.split("</think>")[-1]
        return state

    def generate_summary(state:MedicalAnalysisState):
        print("----------------------------------------------------")
        print("------------Generating summary from PDF-------------")
        print("----------------------------------------------------")
        analysis_result = state["analysis_result"]
        
        messages = [
            SystemMessage(content="""You are a medical report summarizer. Create a detailed summary in markdown format with the following sections:

### Key Findings
- Main medical issues identified
- Critical observations

### Diagnosis
- Primary diagnosis
- Secondary conditions (if any)

### Treatment Plan
- Recommended procedures
- Medications prescribed
- Follow-up instructions

### Additional Notes
- Important considerations
- Special instructions

Please ensure proper markdown formatting with headers, bullet points, and emphasis where appropriate."""),
            HumanMessage(content=f"Generate a detailed medical summary report based on this analysis: {analysis_result}")
        ]
        response = summary_llm.invoke(messages)
        
        state["summary"] = response.content
        return state

    def validate_diagnosis(state:MedicalAnalysisState):
        print("----------------------------------------------------")
        print("------------Validating diagnosis from PDF-----------")
        print("----------------------------------------------------")
        analysis_result = state["analysis_result"]
        summary = state["summary"]
        
        messages = [
            SystemMessage(content="""You are a medical diagnosis validator. Provide your assessment in markdown format with these sections:

### Alignment Analysis
- Evaluate if diagnosis matches symptoms
- Assess treatment appropriateness
- Review medication selections

### Recommendations
- Alternative treatments to consider
- Suggested medication adjustments
- Additional tests if needed

### Risk Assessment
- Potential complications
- Drug interaction concerns
- Follow-up recommendations

Please format your response in clear markdown with appropriate headers and bullet points."""),
            HumanMessage(content=f"""Analysis: {analysis_result}\nSummary: {summary}
                         Based on the Analysis and Summary provided please provide whether diagnosis,treatment and medication provided is in alignment with medical complaint.
                         If not in alignment then specify what best treatment and medication could have been provided.
                         """)
        ]
        response = analyzer_llm.invoke(messages)
        
        state["validation_result"] = response.content.split("</think>")[-1]
        return state

    # Create the graph
    workflow = StateGraph(MedicalAnalysisState)

    # Add nodes
    workflow.add_node("extractor", extract_context)
    workflow.add_node("analyzer", analyze_document)
    workflow.add_node("summarizer", generate_summary)
    workflow.add_node("validator", validate_diagnosis)

    # Define edges
    workflow.add_edge(START, "extractor")
    workflow.add_edge("extractor", "analyzer")  
    workflow.add_edge("analyzer", "summarizer")
    workflow.add_edge("summarizer", "validator")
    workflow.add_edge("validator", END)


    # Compile the graph
    chain = workflow.compile()
    
    # Generate graph visualization
    graph_png = chain.get_graph().draw_mermaid_png()
    graph_base64 = base64.b64encode(graph_png).decode('utf-8')
    
    return chain, graph_base64

def process_medical_document(document_path: str) -> Dict[str, Any]:
    # Read the document with error handling for different encodings
    # try:
    #     # Try UTF-8 first
    #     content = Path(document_path).read_text(encoding='utf-8')
    # except UnicodeDecodeError:
    #     try:
    #         # Try cp1252 (Windows-1252) encoding
    #         content = Path(document_path).read_text(encoding='cp1252')
    #     except UnicodeDecodeError:
    #         try:
    #             # Try latin-1 as a fallback
    #             content = Path(document_path).read_text(encoding='latin-1')
    #         except UnicodeDecodeError:
    #             raise ValueError("Unable to read document - unsupported character encoding")
    
    # Create the chain and get graph visualization
    chain, graph_viz = create_medical_analysis_chain()
    print(f"Document path: {document_path}")
    # Process the document
    result = chain.invoke({"file_name": document_path})
    
    return {
        "analysis": result["analysis_result"],
        "summary": result["summary"],
        "validation": result["validation_result"],
        "graph": graph_viz
    } 