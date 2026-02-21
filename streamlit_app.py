import streamlit as st
from src.rag_pipeline import RAGPipeline
import os

st.set_page_config(
    page_title="საგადასახადო RAG ასისტენტი",
    page_icon="🤖",
    layout="wide"
)

# Initialize RAG
@st.cache_resource
def load_rag():
    return RAGPipeline()

rag = load_rag()

# UI
st.title("🤖 საგადასახადო და საბაჟო RAG ასისტენტი")
st.markdown("დასვი კითხვები საგადასახადო და საბაჟო საკითხებზე")

# Input
question = st.text_area("📝 შენი კითხვა:", placeholder="მაგ: რა არის დღგ?", height=100)
num_sources = st.slider("📊 წყაროების რაოდენობა:", 3, 10, 5)

if st.button("🔍 ძებნა", type="primary"):
    if question.strip():
        with st.spinner("ვეძებ პასუხს..."):
            result = rag.answer_question(question, n_results=num_sources)
            
            st.markdown("### 💬 პასუხი:")
            st.write(result['answer'])
            
            st.markdown("### 📚 წყაროები:")
            for source in result['sources']:
                st.markdown(f"**[{source['number']}] {source['title']}**")
                st.markdown(f"🔗 [{source['url']}]({source['url']})")
    else:
        st.warning("გთხოვთ, ჩაწეროთ კითხვა")

# Examples
st.markdown("### 📋 მაგალითები:")
examples = [
    "რა არის დღგ და როგორ გამოითვლება?",
    "როგორ უნდა მოვახდინო საბაჟო დეკლარირება?",
    "რა დოკუმენტებია საჭირო გადასახადის გადასახდელად?"
]

for ex in examples:
    if st.button(ex):
        st.session_state.question = ex