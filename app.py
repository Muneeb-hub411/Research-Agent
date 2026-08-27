import streamlit as st
import time
from src.agents.agent import create_research_agent
from src.tools.tool import scrape_urls, get_tavily_search_tool
from src.pipelines.pipeline import get_writer_chain, get_critic_chain

# Streamlit Page Configuration
st.set_page_config(
    page_title="NexusResearch AI | Multi-Agent Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling & Professional Dark/Tech Theme Palette
st.markdown("""
<style>
    /* Global Styling adjustments */
    .main {
        background-color: #0e1117;
        color: #c9d1d9;
    }
    
    /* Header Card Banner */
    .hero-container {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid #374151;
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #f3f4f6;
        margin-bottom: 0.5rem;
        letter-spacing: -0.025em;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #9ca3af;
        line-height: 1.5;
    }
    
    /* Agent Card Styling */
    .agent-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .agent-title {
        font-weight: 600;
        color: #58a6ff;
        font-size: 1.1rem;
        margin-bottom: 0.25rem;
    }
    .agent-desc {
        color: #8b949e;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Configuration & Architecture Overview
with st.sidebar:
    st.markdown("### 🧬 Architecture Pipeline")
    st.markdown("This system orchestrates **4 autonomous components** powered by **Google Gemini**:")
    
    st.markdown("""
    1. 🔍 **Research Agent**  
       *Queries Tavily API for real-time web context & URLs.*
    2. 🕷️ **Scraper Agent**  
       *Extracts raw body text cleanly via BeautifulSoup.*
    3. ✍️ **Writer Chain (LCEL)**  
       *Synthesizes findings into an executive report.*
    4. 🎯 **Critic Chain (LCEL)**  
       *Evaluates accuracy, structure, and gives scoring.*
    """)
    
    st.markdown("---")
    st.markdown("### ⚙️ System Configuration")
    model_choice = st.selectbox("LLM Engine", ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.7-flash"], index=0)
    search_depth = st.slider("Max Search Results", min_value=2, max_value=8, value=4)
    
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #6b7280; font-size: 0.8rem;'>NexusResearch Agent v2.0<br>Built with LangChain & Streamlit</div>", unsafe_allow_html=True)

# Main Hero Header
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🧬 NexusResearch AI Agent</div>
    <div class="hero-subtitle">
        Autonomous multi-agent research pipeline that crawls the live web, extracts structured data, 
        synthesizes deep technical reports, and critiques output quality in real-time.
    </div>
</div>
""", unsafe_allow_html=True)

# Input Section inside a clean card layout
col1, col2 = st.columns([3, 1])
with col1:
    topic = st.text_input("Enter research topic or query:", placeholder="e.g., State of AI Agents and LangGraph Multi-Agent Workflows 2026")
with col2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    run_button = st.button("🚀 Initialize Pipeline", use_container_width=True, type="primary")

if run_button:
    if not topic.strip():
        st.warning("⚠️ Please provide a valid research topic to begin.")
        st.stop()

    # Layout progress workflow
    st.markdown("### ⚡ Pipeline Execution Status")
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    with st.container():
        # ==========================================
        # STEP 1: Research Agent Execution
        # ==========================================
        status_text.markdown("🔍 **[1/4] Research Agent active:** Querying Tavily Search API for authoritative sources...")
        progress_bar.progress(15)
        
        try:
            research_agent = create_research_agent(model_name=model_choice)
            search_query = f"Find comprehensive information, recent technical updates, and deep analysis about: {topic}"
            
            agent_response = research_agent.invoke({
                "messages": [{"role": "user", "content": search_query}]
            })
            
            messages = agent_response.get("messages", []) if isinstance(agent_response, dict) else []
            agent_output_text = ""
            if messages:
                last_msg = messages[-1]
                content = getattr(last_msg, "content", last_msg)
                if isinstance(content, str):
                    agent_output_text = content
                elif isinstance(content, list):
                    texts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            texts.append(block.get("text", ""))
                        elif isinstance(block, str):
                            texts.append(block)
                    agent_output_text = "\n".join(texts)
                else:
                    agent_output_text = str(content)
            
            # Fetch structured URLs
            tavily = get_tavily_search_tool(max_results=search_depth)
            raw_search_results = tavily.invoke({"query": topic})
            
            urls = []
            if isinstance(raw_search_results, list):
                for res in raw_search_results:
                    if isinstance(res, dict) and "url" in res:
                        urls.append(res["url"])
            
            time.sleep(0.3)
        except Exception as e:
            st.error(f"❌ Research Agent Error: {e}")
            st.stop()

        # ==========================================
        # STEP 2: Scraper Agent Execution
        # ==========================================
        status_text.markdown(f"🕷️ **[2/4] Scraper Agent active:** Extracting clean content from {len(urls)} discovered web endpoints...")
        progress_bar.progress(40)
        
        try:
            if urls:
                scraped_content = scrape_urls(urls)
            else:
                scraped_content = agent_output_text
            time.sleep(0.3)
        except Exception as e:
            st.error(f"❌ Scraper Agent Error: {e}")
            st.stop()

        # ==========================================
        # STEP 3: Writer Chain Execution (LCEL)
        # ==========================================
        status_text.markdown("✍️ **[3/4] Writer Chain active:** Synthesizing scraped context into a comprehensive technical report...")
        progress_bar.progress(70)
        
        try:
            writer_chain = get_writer_chain(model_name=model_choice)
            draft_article = writer_chain.invoke({
                "topic": topic,
                "scraped_content": scraped_content
            })
            time.sleep(0.3)
        except Exception as e:
            st.error(f"❌ Writer Chain Error: {e}")
            st.stop()

        # ==========================================
        # STEP 4: Critic Chain Execution (LCEL)
        # ==========================================
        status_text.markdown("🎯 **[4/4] Critic Chain active:** Evaluating technical rigor, completeness, and scoring draft...")
        progress_bar.progress(90)
        
        try:
            critic_chain = get_critic_chain(model_name=model_choice)
            critique = critic_chain.invoke({
                "topic": topic,
                "draft": draft_article
            })
            progress_bar.progress(100)
            status_text.markdown("✅ **Pipeline Execution Complete!** All agents finished successfully.")
        except Exception as e:
            st.error(f"❌ Critic Chain Error: {e}")
            st.stop()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    # Display Results in Modern Tabs
    tab1, tab2, tab3 = st.tabs(["📝 Final Research Report", "🔍 Editorial Review & Score", "🌐 Discovered Sources"])
    
    with tab1:
        st.markdown("### Executive Synthesis Report")
        st.markdown(f"<div class='agent-card'>{draft_article}</div>", unsafe_allow_html=True)
        
        st.download_button(
            label="📥 Download Report as Markdown",
            data=draft_article,
            file_name=f"research_report_{topic.lower().replace(' ', '_')[:30]}.md",
            mime="text/markdown"
        )
        
    with tab2:
        st.markdown("### Quality Evaluation & Feedback")
        st.markdown(f"<div class='agent-card'>{critique}</div>", unsafe_allow_html=True)
        
    with tab3:
        st.markdown("### Web References & Extracted Endpoints")
        if urls:
            for i, url in enumerate(urls, 1):
                st.markdown(f"""
                <div class='agent-card'>
                    <div class='agent-title'>Source #{i}</div>
                    <a href="{url}" target="_blank" style="color: #58a6ff; text-decoration: none; word-break: break-all;">{url}</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No external URLs parsed; synthesis relied on core model search grounding.")