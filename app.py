"""Enhanced RAG system with detailed print statements - FINAL FIXED VERSION."""

import streamlit as st
from uuid import uuid4
import time
from multi_hops_agentic_rag import EnhancedRAGPipeline
print("true")

# # Import the enhanced RAG pipeline
# try:
#     from enhanced.enhanced_rag import EnhancedRAGPipeline
# except ImportError:
#     st.error(
#         "Enhanced RAG module not found. Please ensure enhanced_rag.py is in the same directory."
#     )
#     st.stop()

# Page configuration
st.set_page_config(page_title="RAG Final Fixed", page_icon="🔍", layout="wide")

# Custom CSS for better print display
st.markdown(
    """
<style>
    .print-box {
        background-color: #1e1e1e;
        color: #00ff00;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        white-space: pre-wrap;
        margin: 0.5rem 0;
        border-left: 4px solid #00ff00;
        max-height: 600px;
        overflow-y: auto;
    }
    .answer-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .sources-box {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "rag_thread_id" not in st.session_state:
    st.session_state.rag_thread_id = f"final-rag-{uuid4().hex}"

# Sample Title 
# Add The title as per your Domain Project
st.title("🔍 Multi Hops Agentic RAG System ")

# Question input
question = st.text_area(
    "Ask a question:",
    placeholder="e.g., What are the key requirements for documentary credit MT700?",
    height=100,
)

# Configuration
col1, col2, col3 = st.columns(3)
with col1:
    max_hops = st.slider("Max Hops", 2, 6, 3)
with col2:
    min_hops = st.slider("Min Hops", 1, 3, 1)
with col3:
    recursion_limit = st.slider("Recursion Limit", 15, 40, 25)


# Custom RAG Pipeline with Print Statements and Proper Answer Extraction
class FinalRAGPipeline(EnhancedRAGPipeline):
    """Final RAG Pipeline with proper answer extraction."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.print_container = None
        self.print_text = ""
        self.iteration_count = 0
        self.max_iterations = 3  # Conservative limit
        self.final_state = None

    def set_print_container(self, container):
        """Set the Streamlit container for print output."""
        self.print_container = container
        self.print_text = ""
        self.iteration_count = 0
        self.final_state = None

    def print_node(self, message):
        """Add a print message to the display."""
        self.print_text += message + "\n"
        if self.print_container:
            self.print_container.markdown(
                f'<div class="print-box">{self.print_text}</div>',
                unsafe_allow_html=True,
            )

    def _analyze_question(self, state):
        """Analyze question with detailed prints."""
        self.print_node("=" * 80)
        self.print_node("🔍 NODE: ANALYZE_QUESTION")
        self.print_node("=" * 80)

        question = state["question"]
        self.print_node(f"📝 INPUT: {question}")
        self.print_node("🧠 THINKING: Analyzing question complexity and type...")

        result = super()._analyze_question(state)

        self.print_node("📊 ANALYSIS COMPLETE:")
        self.print_node(
            f"   • Complexity: {result.get('question_complexity', 0):.1f}/10"
        )
        self.print_node(f"   • Type: {result.get('question_type', 'unknown')}")
        self.print_node(f"   • Est. Hops: {result.get('estimated_hops', 0)}")
        self.print_node("")

        return result

    def _enhanced_plan(self, state):
        """Enhanced planning with iteration tracking."""
        self.iteration_count += 1

        self.print_node("=" * 80)
        self.print_node("📋 NODE: ENHANCED_PLAN")
        self.print_node("=" * 80)

        iteration = state.get("iteration", 0)
        self.print_node(f"🔄 ITERATION: {iteration} (Count: {self.iteration_count})")

        # Force stop if too many iterations
        if self.iteration_count > self.max_iterations:
            self.print_node("⚠️ FORCE STOP: Max iterations reached")
            return {
                "sub_questions": [
                    {
                        "query": state["question"],
                        "priority": 1.0,
                        "strategy": "semantic",
                    }
                ],
                "current_query_batch": [state["question"]],
                "sub_question": state["question"],
            }

        evidence_count = len(state.get("evidence_docs", []))
        self.print_node(f"📚 Current Evidence: {evidence_count} documents")
        self.print_node("🧠 THINKING: Planning retrieval strategy...")

        result = super()._enhanced_plan(state)

        sub_questions = result.get("sub_questions", [])
        self.print_node(f"🎯 PLAN: {len(sub_questions)} sub-questions generated")
        self.print_node("")

        return result

    def _parallel_retrieve(self, state):
        """Parallel retrieval with progress tracking."""
        self.print_node("=" * 80)
        self.print_node("🔍 NODE: PARALLEL_RETRIEVE")
        self.print_node("=" * 80)

        queries = state.get("current_query_batch", [])
        self.print_node(f"🎯 EXECUTING: {len(queries)} parallel queries")
        self.print_node("🧠 THINKING: Searching multiple strategies...")

        result = super()._parallel_retrieve(state)

        total_evidence = len(result.get("evidence_docs", []))
        new_docs = len(result.get("fused_results", []))

        self.print_node(f"📊 RESULTS: {new_docs} new docs, {total_evidence} total")
        self.print_node("")

        return result

    def _advanced_assess(self, state):
        """Assessment with quality metrics."""
        self.print_node("=" * 80)
        self.print_node("📊 NODE: ADVANCED_ASSESS")
        self.print_node("=" * 80)

        evidence_docs = state.get("evidence_docs", [])
        self.print_node(f"📚 ASSESSING: {len(evidence_docs)} documents")
        self.print_node("🧠 THINKING: Evaluating quality and completeness...")

        result = super()._advanced_assess(state)

        quality = result.get("context_quality_score", 0)
        coverage = result.get("coverage_score", 0)

        self.print_node(f"📈 QUALITY: {quality:.3f}, COVERAGE: {coverage:.3f}")
        self.print_node("")

        return result

    def _intelligent_decide(self, state):
        """Decision making with clear reasoning."""
        self.print_node("=" * 80)
        self.print_node("🤔 NODE: INTELLIGENT_DECIDE")
        self.print_node("=" * 80)

        iteration = state.get("iteration", 0)
        quality = state.get("context_quality_score", 0)

        self.print_node(f"🔄 ITERATION: {iteration}")
        self.print_node(f"📊 QUALITY: {quality:.3f}")
        self.print_node("🧠 THINKING: Continue or stop?")

        # Force stop conditions
        if self.iteration_count >= self.max_iterations:
            self.print_node("🛑 DECISION: STOP (Max iterations)")
            return {
                "stop": True,
                "iteration": iteration + 1,
                "stop_reasons": ["Maximum iterations reached"],
                "decision_factors": {"force_stop": True},
            }

        result = super()._intelligent_decide(state)

        should_stop = result.get("stop", False)
        decision = "🛑 STOP" if should_stop else "🔄 CONTINUE"
        self.print_node(f"🎯 DECISION: {decision}")
        self.print_node("")

        return result

    def _enhanced_synthesis(self, state):
        """Synthesis with answer generation."""
        self.print_node("=" * 80)
        self.print_node("✍️ NODE: ENHANCED_SYNTHESIS")
        self.print_node("=" * 80)

        evidence_docs = state.get("evidence_docs", [])
        self.print_node(f"📚 SYNTHESIZING: {len(evidence_docs)} sources")
        self.print_node("🧠 THINKING: Creating comprehensive answer...")

        result = super()._enhanced_synthesis(state)

        final_answer = result.get("final_answer", "")
        confidence = result.get("answer_confidence", 0)

        self.print_node(
            f"📝 ANSWER: {len(final_answer)} chars, {confidence:.3f} confidence"
        )
        self.print_node("")

        return result

    def _advanced_verify(self, state):
        """Verification with final state capture."""
        self.print_node("=" * 80)
        self.print_node("✅ NODE: ADVANCED_VERIFY")
        self.print_node("=" * 80)

        final_answer = state.get("final_answer", "")
        evidence_docs = state.get("evidence_docs", [])

        self.print_node(f"🔍 VERIFYING: {len(evidence_docs)} sources")
        self.print_node("🧠 THINKING: Checking grounding...")

        result = super()._advanced_verify(state)

        grounded = result.get("grounded_ok", False)
        self.print_node(f"✅ GROUNDING: {'PASSED' if grounded else 'FAILED'}")
        self.print_node(
            f"📊 FINAL: {len(final_answer)} chars, {len(evidence_docs)} sources"
        )
        self.print_node("🎉 PROCESSING COMPLETE!")
        self.print_node("=" * 80)

        # Store final state for extraction
        self.final_state = {
            "final_answer": final_answer,
            "evidence_docs": evidence_docs,
            "answer_confidence": state.get("answer_confidence", 0),
            "grounded_ok": grounded,
            "context_quality_score": state.get("context_quality_score", 0),
            "coverage_score": state.get("coverage_score", 0),
        }

        return result

    def get_final_state(self):
        """Get the final state after processing."""
        return self.final_state


# Run button
if st.button("🚀 Run RAG (Final Fixed)", type="primary"):
    if question.strip():
        try:
            # Initialize pipeline
            pipeline = FinalRAGPipeline(max_iters=max_hops, min_iters=min_hops)

            # Create containers
            print_container = st.container()
            answer_container = st.container()

            with print_container:
                st.subheader("🖥️ Detailed Node Execution")
                print_placeholder = st.empty()
                pipeline.set_print_container(print_placeholder)

            # Execute with proper state tracking
            final_answer = ""
            evidence_docs = []
            answer_confidence = 0

            try:
                # Use direct ask method for more reliable results
                pipeline.print_node("🚀 STARTING RAG EXECUTION...")
                pipeline.print_node("")

                final_answer, debug_info = pipeline.ask(
                    question,
                    max_iters=max_hops,
                    thread_id=st.session_state.rag_thread_id,
                )

                evidence_docs = debug_info.get("evidence_docs", [])
                answer_confidence = debug_info.get("answer_confidence", 0)

                pipeline.print_node("✅ EXECUTION COMPLETED SUCCESSFULLY!")
                pipeline.print_node(f"📊 FINAL RESULTS:")
                pipeline.print_node(f"   • Answer: {len(final_answer)} characters")
                pipeline.print_node(f"   • Sources: {len(evidence_docs)} documents")
                pipeline.print_node(f"   • Confidence: {answer_confidence:.3f}")

            except Exception as e:
                pipeline.print_node(f"❌ ERROR: {str(e)}")
                st.error(f"Execution error: {str(e)}")

            # Display results
            with answer_container:
                if final_answer and final_answer.strip():
                    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                    st.subheader("📝 Final Answer")
                    st.markdown(final_answer)

                    # Show confidence and metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Confidence", f"{answer_confidence:.1%}")
                    with col2:
                        st.metric("Sources", len(evidence_docs))
                    with col3:
                        st.metric("Answer Length", f"{len(final_answer)} chars")

                    st.markdown("</div>", unsafe_allow_html=True)

                    # Show sources
                    if evidence_docs:
                        st.markdown('<div class="sources-box">', unsafe_allow_html=True)
                        st.subheader("📚 Sources Used")

                        # Group sources by document
                        sources_by_doc = {}
                        for doc in evidence_docs:
                            source = doc.metadata.get("source", "Unknown")
                            page = doc.metadata.get("page", "?")
                            key = source

                            if key not in sources_by_doc:
                                sources_by_doc[key] = []
                            sources_by_doc[key].append(page)

                        # Display grouped sources
                        for i, (source, pages) in enumerate(sources_by_doc.items(), 1):
                            pages_str = ", ".join(map(str, sorted(set(pages))))
                            st.write(f"**[{i}]** {source} (pages: {pages_str})")

                        # Detailed source content
                        with st.expander("📖 View Source Content", expanded=False):
                            for i, doc in enumerate(evidence_docs[:8], 1):
                                source = doc.metadata.get("source", "Unknown")
                                page = doc.metadata.get("page", "?")
                                content = (
                                    doc.page_content[:200] + "..."
                                    if len(doc.page_content) > 200
                                    else doc.page_content
                                )

                                st.markdown(
                                    f"""
**Source {i}: {source} (page {page})**
{content}
---
"""
                                )

                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error(
                        "❌ No answer was generated. Please try again with a different question or check your configuration."
                    )

                    # Show debug info
                    if evidence_docs:
                        st.info(
                            f"ℹ️ Found {len(evidence_docs)} source documents, but answer generation failed."
                        )

        except Exception as e:
            st.error(f"Error: {str(e)}")
            import traceback

            with st.expander("Error Details", expanded=False):
                st.code(traceback.format_exc())
    else:
        st.warning("Please enter a question.")

# Footer
st.markdown("---")
st.markdown("🔍 RAG System - Final Fixed Version with Proper Answer Extraction")
