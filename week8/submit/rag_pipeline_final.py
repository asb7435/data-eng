# rag_pipeline.py — 수집 → 검증 → 색인 → 보고 (7주차 build_kb.py 를 태스크로)
import os
from datetime import datetime, timedelta

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator

INCOMING = "/opt/airflow/dags/data/incoming"   # 새 문서 투입구 = 내 PC 의 ~/airflow-lab/dags/data/incoming
PREFIX = "incoming/"                            # MinIO raw-docs 버킷 안의 자리


def collect():
    """투입구의 .txt 를 MinIO(raw-docs/incoming/)에 올린다 — 같은 키에 덮어써서 몇 번 돌려도 같다"""
    from minio_env import mc, BUCKET
    os.makedirs(INCOMING, exist_ok=True)
    local = sorted(n for n in os.listdir(INCOMING) if n.endswith(".txt"))
    for name in local:
        mc.fput_object(BUCKET, PREFIX + name, os.path.join(INCOMING, name), content_type="text/plain")
    for obj in mc.list_objects(BUCKET, prefix=PREFIX):          # 투입구에서 지운 파일은 Lake 에서도 지운다
        if obj.object_name[len(PREFIX):] not in local:
            mc.remove_object(BUCKET, obj.object_name)
    print(f"수집 {len(local)}건 → minio://{BUCKET}/{PREFIX}")


def validate():
    """나쁜 문서가 지식베이스로 내려가지 않게 여기서 막는다"""
    from minio_env import mc, BUCKET, read_text
    keys = [o.object_name for o in mc.list_objects(BUCKET, recursive=True) if o.object_name.endswith(".txt")]
    if not keys:
        raise ValueError("raw-docs 에 문서가 없습니다")
    short = [k for k in keys if len(read_text(BUCKET, k).strip()) < 20]
    if short:
        raise ValueError(f"너무 짧은 문서: {short}")
    print(f"검증 통과: {len(keys)}건 {keys}")
    return len(keys)          # 작은 값이라 XCom 으로 넘겨도 된다


def build_index():
    """7-5 의 build_kb.py 를 그대로 부른다 — 문서마다 옛 조각을 지우고 다시 넣는다"""
    import build_kb           # 무거운 import 는 태스크 안에서(파일을 읽을 때마다 돌지 않게)
    build_kb.main()
    from datetime import timezone
    from qdrant_client.models import Filter, FilterSelector
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    build_kb.qc.set_payload(
        build_kb.COLLECTION,
        payload={"ingested_at": now},
        points=FilterSelector(filter=Filter()),
        wait=True,
    )


def prune():
    """Lake 에서 사라진 문서의 조각을 지식베이스에서도 지운다"""
    from qdrant_client.models import Filter, FieldCondition, MatchAny, FilterSelector
    from build_kb import mc, qc, BUCKET, COLLECTION
    live = [f"minio://{BUCKET}/{o.object_name}"
            for o in mc.list_objects(BUCKET, recursive=True) if o.object_name.endswith(".txt")]
    before = qc.count(COLLECTION).count
    qc.delete(COLLECTION, points_selector=FilterSelector(filter=Filter(
        must_not=[FieldCondition(key="source", match=MatchAny(any=live))])))
    print(f"정리: {before} → {qc.count(COLLECTION).count} 조각")


def report():
    from build_kb import qc, COLLECTION
    print(f"{COLLECTION} 조각 수: {qc.count(COLLECTION).count}")


with DAG(
    dag_id="rag_pipeline_final",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=1)},
    tags=["week8", "final"],
) as dag:
    t_collect = PythonOperator(task_id="collect", python_callable=collect)
    t_validate = PythonOperator(task_id="validate", python_callable=validate)
    t_index = PythonOperator(task_id="build_index", python_callable=build_index)
    t_prune = PythonOperator(task_id="prune", python_callable=prune)
    t_report = PythonOperator(task_id="report", python_callable=report)

    t_collect >> t_validate >> t_index >> t_prune >> t_report
