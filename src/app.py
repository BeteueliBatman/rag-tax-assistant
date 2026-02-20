import gradio as gr
from rag_pipeline import RAGPipeline
import os

# RAG Pipeline-ის ინიციალიზაცია (ერთხელ)
print("🔄 Loading RAG system...")
rag = RAGPipeline()
print("✅ System ready!\n")

def answer_query(question, num_sources):
    """კითხვაზე პასუხის გენერირება Gradio-სთვის"""
    
    if not question.strip():
        return "⚠️ გთხოვთ, ჩაწეროთ კითხვა.", ""
    
    # პასუხის გენერირება
    result = rag.answer_question(question, n_results=num_sources)
    
    # პასუხი
    answer_text = result['answer']
    
    # წყაროები
    sources_text = "### 📚 გამოყენებული წყაროები:\n\n"
    for source in result['sources']:
        sources_text += f"**[{source['number']}] {source['title']}**\n"
        sources_text += f"🔗 [{source['url']}]({source['url']})\n\n"
    
    return answer_text, sources_text

# Gradio ინტერფეისი
demo = gr.Blocks(title="საგადასახადო RAG ასისტენტი", theme=gr.themes.Soft())

with demo:
    gr.Markdown("""
    # 🤖 საგადასახადო და საბაჟო RAG ასისტენტი
    
    დასვი კითხვები საგადასახადო და საბაჟო ადმინისტრირებასთან დაკავშირებით.
    სისტემა მოძებნის შესაბამის ინფორმაციას **infohub.rs.ge** საიტიდან და მოგცემს პასუხს წყაროების მითითებით.
    """)
    
    with gr.Row():
        with gr.Column(scale=3):
            # Input
            question_input = gr.Textbox(
                label="📝 შენი კითხვა",
                placeholder="მაგ: რა არის დღგ და როგორ გამოითვლება?",
                lines=3
            )
            
            num_sources_slider = gr.Slider(
                minimum=3,
                maximum=10,
                value=5,
                step=1,
                label="📊 წყაროების რაოდენობა",
                info="რამდენი დოკუმენტი გამოიყენოს სისტემამ"
            )
            
            submit_btn = gr.Button("🔍 ძებნა და პასუხის მიღება", variant="primary", size="lg")
        
        with gr.Column(scale=2):
            gr.Markdown("""
            ### 💡 რჩევები:
            
            - დასვი **კონკრეტული** კითხვები
            - გამოიყენე **ქართული** ენა
            - შეგიძლია ჰკითხო:
              - დღგ-ის შესახებ
              - საბაჟო პროცედურების შესახებ  
              - გადასახადების გადახდის წესების შესახებ
              - საგადასახადო დეკლარაციების შესახებ
            """)
    
    # Outputs
    with gr.Row():
        answer_output = gr.Markdown(label="💬 პასუხი")
    
    with gr.Row():
        sources_output = gr.Markdown(label="📚 წყაროები")
    
    # ღილაკის დაჭერაზე
    submit_btn.click(
        fn=answer_query,
        inputs=[question_input, num_sources_slider],
        outputs=[answer_output, sources_output]
    )
    
    # მაგალითები
    gr.Markdown("### 📋 მაგალითები:")
    gr.Examples(
        examples=[
            ["რა არის დღგ და როგორ გამოითვლება?", 5],
            ["როგორ უნდა მოვახდინო საბაჟო დეკლარირება?", 5],
            ["რა დოკუმენტებია საჭირო გადასახადის გადასახდელად?", 5],
            ["როდის უნდა გადავიხადო საშემოსავლო გადასახადი?", 5],
        ],
        inputs=[question_input, num_sources_slider],
    )

# აპლიკაციის გაშვება
if __name__ == "__main__":
    # Render.com-ისთვის
    port = int(os.environ.get("PORT", 10000))
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False
    )