"""Export compiled author materials to a local research corpus; no publication."""
import json
import os
import sqlite3
from collections import Counter
from pathlib import Path

P = Path(__file__).resolve().parent.parent
R = P.parent.parent
OUT = R / "materials"
OUT.mkdir(exist_ok=True)
worklist = P / "PREPARATION_WORKLIST.jsonl"
rows = [json.loads(line) for line in worklist.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))
def excerpt(spans):
    parts = []
    for span in spans:
        lines = (P / span["path"]).read_text(encoding="utf-8-sig").splitlines()
        parts.append("% Original source: " + span["path"] + ":" + str(span["start_line"]) + "-" + str(span["end_line"]) + "\n" + "\n".join(lines[span["start_line"]-1:span["end_line"]]))
    return "\n\n".join(parts)
def relative(path):
    return os.path.relpath(path, R).replace("\\", "/")
records = []
for row in rows:
    if row["state"] not in ("ready_for_assembly", "prepared_unpublished"):
        continue
    candidates = [P/"jobs/materials-150"/row["task_id"]/row["revision"], R/"materials-150"/row["task_id"]/row["revision"], R/"materials"/row["task_id"]/row["revision"]]
    success = []
    for job in candidates:
        if not (job/"job-state.json").exists():
            continue
        state = load(job/"job-state.json")
        if state["status"] == "compiled_pending_qa":
            success.append((job,state))
    if not success:
        continue
    job,state = success[-1]
    manifest = load(job/state["package"]/"manifest.json")["items"][0]
    tex = job/state["package"]/manifest["item_path"]
    receipt = load(job/state["receipt_root"]/(state["problem_id"]+".json"))
    pdf = job/receipt["pdf_path"]
    if not receipt["ok"] or not pdf.is_file():
        continue
    task = load(P/row["task_path"])
    slot = "formal" if len(records)<100 else "reserve"
    row.update(state="prepared_unpublished", handoff_slot=slot, assembly_job=relative(job), assembly_status="compiled", tex_path=relative(tex), pdf_path=relative(pdf))
    records.append((row,task,tex,pdf))
columns = ["task_id","title","route","difficulty_level","slot","source_id","source_version","source_url","claim_key","authors_json","license_json","statement_text","proof_text","context_text","tex_content","tex_path","pdf_path","task_json","public_problem_id","local_material_id","publication_status"]
db = sqlite3.connect(OUT/"PREPARED_MATERIALS.sqlite3")
with db:
    db.execute("CREATE TABLE IF NOT EXISTS problems (" + ",".join(c+" TEXT"+(" PRIMARY KEY" if c=="task_id" else "") for c in columns) + ", UNIQUE(source_id,claim_key))")
    for row,task,tex,pdf in records:
        values = [task["task_id"], task["title"], task["route"], task["difficulty_level"], row["handoff_slot"], task["source_id"], task["source_version"], task["source_url"], task["claim_key"], json.dumps(task["authors"],ensure_ascii=False), json.dumps(task["license"],ensure_ascii=False), excerpt(task["statement_spans"]), excerpt(task["proof_spans"]), excerpt(task["context_spans"]), tex.read_text(encoding="utf-8"), relative(tex), relative(pdf), json.dumps(task,ensure_ascii=False), row.get("problem_id"), task.get("local_material_id"), "local_prepared_unpublished"]
        db.execute("INSERT INTO problems VALUES ("+",".join("?" for _ in columns)+") ON CONFLICT(task_id) DO UPDATE SET "+",".join(c+"=excluded."+c for c in columns[1:]), values)
    count = db.execute("SELECT count(*) FROM problems").fetchone()[0]
    assert count == len(records), "Existing corpus has entries outside this export; preserve it and inspect the changed selection."
    assert db.execute("SELECT count(*) FROM problems WHERE length(statement_text)=0 OR length(proof_text)=0 OR length(tex_content)=0").fetchone()[0] == 0
index = ["# 未公开题证材料索引", "", f"共 {count} 道已编译作者题证材料；正式/后备按下表槽位区分，满150时为100正式加50后备。原作者承担数学内容责任，本库记录来源、完整摘录和可编辑成品，不表示独立数学认证或公开发布。", "", "数据库：`PREPARED_MATERIALS.sqlite3`，表 `problems`。数据库内含题面、证明、上下文原文和成品TeX；路径相对于维护树根目录。", "", "| 槽位 | 方向 | 难度 | 题目 | 成品 |", "|---|---|---|---|---|"]
for row,task,tex,pdf in records:
    links = "[TeX]("+os.path.relpath(tex,OUT).replace("\\","/")+") · [PDF]("+os.path.relpath(pdf,OUT).replace("\\","/")+")"
    index.append("| "+" | ".join([row["handoff_slot"],task["route"],task["difficulty_level"],task["title"].replace("|","/"),links])+" |")
(OUT/"INDEX.md").write_text("\n".join(index)+"\n",encoding="utf-8")
worklist.write_text("".join(json.dumps(row,ensure_ascii=False)+"\n" for row in rows),encoding="utf-8")
status = load(P/"STATUS.json")
status.update(work_status="materials_prepared" if count==150 else "materials_assembly_in_progress", prepared_unpublished_materials=count, ready_unpublished_formal_tasks=sum(row["handoff_slot"]=="formal" for row,_,_,_ in records), ready_unpublished_reserve_tasks=sum(row["handoff_slot"]=="reserve" for row,_,_,_ in records), new_prepared_materials_this_run=max(0,count-80), public_deliveries_this_run=0, next="Use the prepared author materials for corpus intake and cross-theory research; no DeepSeek handoff or extra review.", counting_note="Compiled local author materials are separate from historical public counts; no independent mathematical certification is claimed.", local_material_index=relative(OUT/"INDEX.md"), local_material_database=relative(OUT/"PREPARED_MATERIALS.sqlite3"))
(P/"STATUS.json").write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"prepared":count,"routes":dict(Counter(task["route"] for _,task,_,_ in records)),"difficulty":dict(Counter(task["difficulty_level"] for _,task,_,_ in records)),"public_added":0},ensure_ascii=False))
db.close()
