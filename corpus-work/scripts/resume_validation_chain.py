"""Resume the existing schema2 artifact chain without changing its format or helper.

Private stage attempts are preserved. This performs transport restoration only;
qualification, SQL/full gate and remote delivery accounting remain separate.
"""
from pathlib import Path
import argparse
import json
import os
import shutil
import types
import restore_validation_chain as chain


def dump(path, value):
    temporary = Path(path).with_name(Path(path).name + ".writing")
    chain.dump(temporary, value)
    os.replace(temporary, path)


def schema1_module(plan):
    module = types.ModuleType("_captured_schema1_restore")
    module.__file__ = str(plan["helper"])
    exec(compile(plan["helper_bytes"], str(plan["helper"]), "exec"), module.__dict__)
    if not callable(getattr(module, "restore", None)):
        raise ValueError("trusted schema1 helper has no restore interface")
    return module


def complete_stage(stage, record):
    if not stage.is_dir() or stage.is_symlink() or not (stage / "RESTORE_RECEIPT.json").is_file():
        return None
    receipt = chain.load(chain.ordinary(stage / "RESTORE_RECEIPT.json"))
    if (receipt.get("status") != "actual_restore_complete" or
            receipt.get("artifact_files") != len(record["filemap"]) or
            receipt.get("archive_sha256") != record["delivery"]["archive_sha256"]):
        return None
    actual = {path.relative_to(stage).as_posix() for path in stage.rglob("*") if path.is_file()}
    if actual != set(record["filemap"]) | {"RESTORE_RECEIPT.json"}:
        return None
    for name, pin in record["filemap"].items():
        path = chain.local(stage, name)
        if path.stat().st_size != pin["bytes"] or chain.sha(path) != pin["sha256"]:
            return None
    return receipt


def restore(chain_path, expected_chain_sha256, archive_roots, helper_path, expected_helper_sha256, output):
    output = chain.no_symlink(output)
    # Original preflight remains authoritative; its output marker must be absent.
    plan = chain.preflight(chain_path, expected_chain_sha256, archive_roots, helper_path,
                           expected_helper_sha256, output / "unused-preflight-output" if output.exists() else output)
    identity = {"chain_sha256": plan["chain_sha256"], "externally_trusted_schema1_helper_sha256": plan["helper_sha256"],
                "archive_roots": {key: str(chain.no_symlink(value)) for key, value in archive_roots.items()}}
    identity_path = output / "CHAIN_INPUT.json"
    if output.exists():
        if not identity_path.is_file() or chain.load(chain.ordinary(identity_path)) != identity:
            raise ValueError("existing chain restore output identity mismatch")
    else:
        output.mkdir(parents=True)
        dump(identity_path, identity)
    helper = schema1_module(plan)
    results, stages = [], {}
    reused = 0
    try:
        for record in plan["plans"]:
            prefix = f"{record['index']:05}-{record['id']}-attempt-"
            parent = output / "stages"
            attempts = sorted(parent.glob(prefix + "*")) if parent.exists() else []
            stage, receipt = None, None
            for candidate in attempts:
                recovered = complete_stage(candidate, record)
                if recovered is not None:
                    stage, receipt = candidate, recovered
                    reused += 1
                    break
            if stage is None:
                # Never overwrite/delete a partial stage; only this archive gets a new attempt.
                numbers = [int(path.name[len(prefix):]) for path in attempts if path.name[len(prefix):].isdigit()]
                stage = parent / (prefix + f"{max(numbers, default=0) + 1:03}")
                receipt = helper.restore(record["root"], stage)
                if complete_stage(stage, record) is None:
                    raise ValueError("schema1 restored stage inventory/bytes differ")
            stages[record["id"]] = stage
            results.append({"index": record["index"], "id": record["id"],
                "delivery_sha256": record["descriptor_sha256"], "archive_sha256": record["delivery"]["archive_sha256"],
                "stage": str(stage), "actual_schema1_restore": receipt})
        for name, pin in plan["final"].items():
            target = chain.no_symlink(output.joinpath(*chain.canonical(name).parts))
            if target.exists() and target.is_file() and target.stat().st_size == pin["bytes"] and chain.sha(target) == pin["sha256"]:
                continue
            source = chain.local(stages[pin["archive_id"]], name)
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = chain.no_symlink(target.with_name(target.name + ".restoring"))
            shutil.copyfile(source, temporary)
            temporary.chmod(0o644)
            os.replace(temporary, target)
            if target.stat().st_size != pin["bytes"] or chain.sha(target) != pin["sha256"]:
                raise ValueError("final artifact bytes differ")
        for record in plan["plans"]:
            if chain.sha(record["descriptor"]) != record["descriptor_sha256"]:
                raise ValueError("input descriptor changed during restoration")
            for path, pin in record["parts"]:
                chain.ordinary(path)
                if path.stat().st_size != pin["bytes"] or chain.sha(path) != pin["sha256"]:
                    raise ValueError("input part changed during restoration")
        if chain.sha(chain.ordinary(plan["helper"])) != plan["helper_sha256"] or chain.sha(chain.ordinary(plan["chain"])) != plan["chain_sha256"]:
            raise ValueError("helper/chain changed during restoration")
        result = {"schema_version": 2, "status": "actual_validation_chain_restore_complete_not_qualified_or_remote",
            "chain_sha256": plan["chain_sha256"], "externally_trusted_schema1_helper_sha256": plan["helper_sha256"],
            "destination": str(output), "build_root": str(output / "build"), "receipt_root": str(output / "receipts"),
            "artifact_files": len(plan["final"]), "archives": results, "final_filemap": plan["final"],
            "stage_only_paths": plan["stage_only"], "inputs_unchanged_and_all_history_stages_retained": True,
            "new_compile": False, "qualified_count_increment": 0, "remote_count_increment": 0,
            "reused_completed_archives": reused}
        dump(output / "CHAIN_RESTORE_RECEIPT.json", result)
        return result
    except Exception as error:
        dump(output / "CHAIN_RESTORE_FAILED.json", {"status": "failed_partial_output_preserved", "error": str(error),
            "chain_sha256": plan["chain_sha256"], "inputs_not_modified_by_this_tool": True, "completed_stages": results})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chain", required=True, type=Path)
    parser.add_argument("--expected-chain-sha256", required=True)
    parser.add_argument("--archive-root", required=True, action="append", metavar="ID=LOCAL_DIRECTORY")
    parser.add_argument("--schema1-helper", required=True, type=Path)
    parser.add_argument("--expected-helper-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    roots = {}
    for value in args.archive_root:
        ident, separator, location = value.partition("=")
        if not separator or not location or ident in roots:
            parser.error("archive-root must be unique ID=LOCAL_DIRECTORY")
        roots[chain.identifier(ident)] = Path(location)
    print(json.dumps(restore(args.chain, args.expected_chain_sha256, roots, args.schema1_helper,
                             args.expected_helper_sha256, args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
