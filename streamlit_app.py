import streamlit as st
from src.rag_pipeline import RAGPipeline

st.set_page_config(page_title="საგადასახადო RAG ასისტენტი", page_icon="🤖")

@st.cache_resource
def load_rag():
    return RAGPipeline()

try:
    rag = load_rag()
    
    st.title("🤖 საგადასახადო და საბაჟო RAG ასისტენტი")
    st.markdown("დასვი კითხვები საგადასახადო და საბაჟო საკითხებზე")
    
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
    
    st.markdown("### 📋 მაგალითები:")
    if st.button("რა არის დღგ და როგორ გამოითვლება?"):
        st.rerun()
    if st.button("როგორ უნდა მოვახდინო საბაჟო დეკლარირება?"):
        st.rerun()

except Exception as e:
    st.error(f"შეცდომა სისტემის ჩატვირთვისას: {str(e)}")
    st.info("გთხოვთ, შეამოწმოთ GROQ_API_KEY Secrets-ში")