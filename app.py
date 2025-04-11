# app.py (요약된 버전: 문서 업로드 + 키워드 추출 포함)
import streamlit as st
import pandas as pd
from fuzzywuzzy import process
import pdfplumber
from docx import Document

@st.cache_data
def load_edi():
    return pd.read_excel("data/edi_codes.xlsx")

@st.cache_data
def load_kpcs():
    return pd.read_csv("data/kpcs_codes.csv")

def extract_text_from_pdf(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        texts = [page.extract_text() for page in pdf.pages if page.extract_text()]
    return "\n".join(texts)

def extract_text_from_docx(uploaded_file):
    doc = Document(uploaded_file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_procedure_keywords(text):
    keywords = ['절제', '수술', '삽입', '봉합', '내시경', '복강경', '조영술', '생검', '절단', '절개']
    found = [line.strip() for line in text.splitlines() if any(k in line for k in keywords)]
    return list(set(found))[:20]

def fuzzy_search(query, choices, threshold=80):
    results = process.extract(query, choices, limit=10)
    return [name for name, score in results if score >= threshold]

def parse_kpcs_code(code):
    labels = ['Section', 'Body System', 'Body Part', 'Root Operation',
              'Sub Root Operation', 'Approach', 'Device', 'Qualifier']
    values = list(code)
    sub_root_extras = {'Inspection': {'0': 'capsule endoscopy', '1': 'palpation'}}
    qualifier_extras = {'robotic': '0 - robotic assisted procedure'}
    explanation = {'Device': {'Z': 'Z'}, 'Qualifier': {'Z': 'Z'}}
    result = dict(zip(labels, values))
    if result['Root Operation'] == 'K':
        result['Sub Root Operation'] = sub_root_extras['Inspection'].get(result['Sub Root Operation'], result['Sub Root Operation'])
    if result['Qualifier'] == '0':
        result['Qualifier'] = qualifier_extras['robotic']
    elif result['Qualifier'] == 'Z':
        result['Qualifier'] = 'Z'
    return result

def display_keywords_ui():
    st.markdown("## 📄 문서 업로드 (PDF, Word)")
    uploaded_file = st.file_uploader("의료행위가 포함된 문서를 업로드하세요", type=["pdf", "docx"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            extracted = extract_text_from_pdf(uploaded_file)
        else:
            extracted = extract_text_from_docx(uploaded_file)
        st.markdown("### 🔍 추출된 의료행위 키워드 후보:")
        for keyword in extract_procedure_keywords(extracted):
            st.markdown(f"- {keyword}")

st.title("🏥 EDI / K-PCS 코드 검색기")
display_keywords_ui()
