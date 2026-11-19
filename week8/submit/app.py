# app.py — 최종본: 근거 · 출처 · 적재 시각 · 지식베이스 상태를 함께 보여 주는 RAG 챗봇
import os

import streamlit as st
from qdrant_client import QdrantClient

from rag_env import PROVIDER, get_emb, get_llm

COLLECTION = os.getenv("COLLECTION", "lecture_kb")      # 7-4 · 8-3 DAG 와 같은 이름
THRESHOLD = float(os.getenv("THRESHOLD", "0.4"))        # 3단계에서 우리 문서로 재서 정한 값

st.title("강의 자료 RAG 챗봇")


@st.cache_resource                                      # 재실행마다 모델 · 접속을 새로 만들지 않게
def get_clients():
    return get_emb(), get_llm(), QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))


emb, llm, qdrant = get_clients()

with st.sidebar:
    st.header("지식베이스")
    try:
        info = qdrant.get_collection(COLLECTION)
        st.metric("조각 수", info.points_count)
        st.caption(f"{COLLECTION} · 차원 {info.config.params.vectors.size} · 모델 경로 {PROVIDER}")
    except Exception as e:
        st.error("Qdrant 에 연결하지 못했습니다")
        st.caption(f"{type(e).__name__}: {e}")
    st.header("설정")
    limit = st.slider("검색할 근거 개수", 1, 10, 3)
    if st.button("대화 지우기"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

question = st.chat_input("강의 자료에 대해 질문해 주세요")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            # 1) 질문 임베딩 → 2) Qdrant 검색
            hits = qdrant.query_points(COLLECTION, query=emb.embed_query(question),
                                       limit=limit, with_payload=True).points
            top = hits[0].score if hits else 0.0
            if top < THRESHOLD:                          # 근거가 약하면 LLM 을 부르지 않는다
                answer = f"강의 자료에서 관련 내용을 찾지 못했습니다. (최고 유사도 {top:.3f} < 기준 {THRESHOLD})"
                st.markdown(answer)
            else:
                # 3) 찾은 조각만 근거로 답하게 한다 — 글자가 흘러나오게
                context = "\n---\n".join(h.payload["text"] for h in hits)
                prompt = ("아래 컨텍스트만 근거로 한국어로 짧게 답해줘. 없으면 모른다고 답해줘.\n\n"
                          f"[컨텍스트]\n{context}\n\n[질문]\n{question}")
                answer = st.write_stream(llm.stream(prompt))
            with st.expander("검색 근거 보기"):
                for h in hits:
                    st.write(f"유사도 {h.score:.3f} · {h.payload['source']}")
                    st.caption(f"적재 {h.payload.get('ingested_at', '알 수 없음')} · {h.payload['text'][:200]}")
        except Exception as e:                            # 역추적 대신 무엇이 안 되는지만
            answer = f"답변을 만들지 못했습니다: {type(e).__name__}"
            st.error(answer)
            st.caption("모델 서버(Ollama)나 Qdrant 가 떠 있는지 확인해 주세요.")
    st.session_state.messages.append({"role": "assistant", "content": answer})
