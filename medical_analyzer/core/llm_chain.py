"""
LangGraph chain implementation for medical document analysis
"""

from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
import base64
import logging

from medical_analyzer.core.config import settings
from medical_analyzer.services.ocr import extract_text_from_pdf
from medical_analyzer.services.llm import get_llm_client

# Configure logging
logger = logging.getLogger(__name__)

# Initialize LLM clients
summary_llm = get_llm_client(model_type="summary")
analyzer_llm = get_llm_client(model_type="analyzer", temperature=0.6)

# Define the state for our graph
class MedicalAnalysisState(TypedDict):
    file_name: str
    context: str
    analysis_result: str
    summary: str
    validation_result: str

def create_medical_analysis_chain():
    """
    Create a LangGraph chain for medical document analysis
    
    Returns:
        tuple: (compiled_chain, graph_base64)
    """
    # Define the nodes (agents) in our graph
    def extract_context(state: MedicalAnalysisState):
        """Extract text from PDF document"""
        print("----------------------------------------------------")
        print("-----------Extracting context from PDF--------------")
        print("----------------------------------------------------")
        
        pdf_name = state['file_name']
        text = extract_text_from_pdf(pdf_name)
        state["context"] = text
        return state
    
    def analyze_document(state: MedicalAnalysisState):
        """Analyze the extracted text"""
        print("----------------------------------------------------")
        print("------------Analyzing context from PDF--------------")
        print("----------------------------------------------------")
        
        document_content = state["context"]
        
        # Use Langchain with open-source LLM for medical analysis
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
        
        # Clean up response if it contains thinking process markers
        analysis = response.content
        if "</think>" in analysis:
            analysis = analysis.split("</think>")[-1]
            
        state["analysis_result"] = analysis
        return state

    def generate_summary(state: MedicalAnalysisState):
        """Generate a summary of the analysis"""
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

    def validate_diagnosis(state: MedicalAnalysisState):
        """Validate the diagnosis and treatment plan"""
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
                         Based on the Analysis and Summary provided please provide whether diagnosis, treatment and medication provided is in alignment with medical complaint.
                         If not in alignment then specify what best treatment and medication could have been provided.
                         """)
        ]
        response = analyzer_llm.invoke(messages)
        
        # Clean up response if it contains thinking process markers
        validation = response.content
        if "</think>" in validation:
            validation = validation.split("</think>")[-1]
            
        state["validation_result"] = validation
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