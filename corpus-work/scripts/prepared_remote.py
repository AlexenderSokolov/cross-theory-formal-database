"""One prepared batch through SSH metadata/bundle and the existing local Git relay.

No credentials are changed. The server authorizes the candidate; local Git has
at most one durable CAS attempt; the server then performs exact public restore.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import shlex
import subprocess
import time

import prepared_delivery as d
import prepared_publish as p

SSH_OPTIONS = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-o", "ProxyCommand=none",
               "-o", "ProxyJump=none", "-o", "ClearAllForwardings=yes"]
IDENTITY = ("batch_id", "actor", "candidate_commit", "public_base_commit", "branch", "origin_url", "material_count")


class SSHTransport:
    def __init__(self, spec, logs):
        self.spec, self.logs, self.last_connection = spec, Path(logs), 0.0
        d.require(re.fullmatch(r"[A-Za-z0-9_.-]+", spec["ssh_alias"]), "explicit SSH config alias required")
        for key in ("remote_python", "remote_script", "remote_batch"):
            value = spec[key]
            d.require(isinstance(value, str) and PurePosixPath(value).is_absolute() and "\n" not in value and "\0" not in value,
                      "absolute remote path required: " + key)

    def call(self, argv, label):
        remaining = 3.1 - (time.monotonic() - self.last_connection)
        if remaining > 0:
            time.sleep(remaining)
        self.last_connection = time.monotonic()
        result = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
                                timeout=int(self.spec.get("transport_timeout_seconds", 900)))
        (self.logs / (label + ".stdout.log")).write_text(result.stdout, encoding="utf-8")
        (self.logs / (label + ".stderr.log")).write_text(result.stderr, encoding="utf-8")
        d.require(result.returncode == 0, label + " failed; see " + str(self.logs / (label + ".stderr.log")))
        return result.stdout

    def server(self, action, *, restore_only=False):
        args = [self.spec["remote_python"], self.spec["remote_script"], action, "--batch", self.spec["remote_batch"]]
        if restore_only:
            args.append("--restore-only")
        command = "exec " + " ".join(shlex.quote(value) for value in args)
        prefix = self.spec.get("remote_path_prepend", [])
        d.require(isinstance(prefix, list) and all(isinstance(value, str) and PurePosixPath(value).is_absolute() and
                  ":" not in value and "\n" not in value for value in prefix), "remote_path_prepend must list existing absolute directories")
        if prefix:
            command = "export PATH=" + shlex.quote(":".join(prefix)) + ':"$PATH"; ' + command
        output = self.call(["ssh", *SSH_OPTIONS, self.spec["ssh_alias"], command], action)
        return json.loads(output)

    def begin(self):
        return self.server("begin-relay")

    def fetch_bundle(self, remote, local):
        path, batch = PurePosixPath(remote), PurePosixPath(self.spec["remote_batch"])
        d.require(path.is_absolute() and ".." not in path.parts and path.is_relative_to(batch) and path.suffix == ".bundle",
                  "server bundle must belong to this exact remote batch")
        d.require(re.fullmatch(r"[A-Za-z0-9_./-]+", remote), "unsupported SCP bundle path")
        d.require(not Path(local).exists(), "received bundle destination must be fresh")
        self.call(["scp", *SSH_OPTIONS, self.spec["ssh_alias"] + ":" + remote, str(local)], "scp-bundle")

    def complete(self):
        return self.server("publish", restore_only=True)


def run(spec, *, transport=None):
    repo = Path(spec["relay_git_dir"]).resolve()
    d.require((repo / "objects").is_dir(), "existing local bare relay is required")
    batch = PurePosixPath(spec["remote_batch"]).name
    d.require(d.ID.fullmatch(batch), "invalid explicit remote batch ID")
    folder = Path(spec["output_root"]).resolve() / batch
    folder.mkdir(parents=True, exist_ok=True)
    with p.file_guard(repo / "prepared-relay.lock"):
        state_path = folder / "relay-state.json"
        state = d.load(state_path) if state_path.exists() else {"schema_version": 2, "policy": d.POLICY, "batch_id": batch, "push_attempted": False}
        d.require(state.get("policy") == d.POLICY and state["batch_id"] == batch, "local relay state belongs to another batch")
        attempt = int(state.get("transport_attempts", 0)) + 1
        state["transport_attempts"] = attempt
        d.save(state_path, state)
        logs = folder / ("attempt-" + str(attempt).zfill(3))
        logs.mkdir(exist_ok=False)
        channel = transport or SSHTransport(spec, logs)
        try:
            envelope = channel.begin()
            d.require(envelope.get("schema_version") == 2 and envelope.get("policy") == d.POLICY and envelope["batch_id"] == batch and
                      envelope["actor"] == spec["actor"] and envelope["origin_url"] == spec["expected_origin_url"] and
                      envelope["branch"] == spec["expected_branch"], "server relay identity differs from explicit local configuration")
            identity = {key: envelope[key] for key in IDENTITY}
            if "identity" in state:
                d.require(identity == state["identity"], "same local batch cannot change candidate/base/actor")
            state["identity"] = identity
            state["stage"] = envelope["status"]
            d.save(state_path, state)
            candidate, base, origin, branch = [envelope[k] for k in ("candidate_commit", "public_base_commit", "origin_url", "branch")]
            d.require(p.COMMIT.fullmatch(candidate) and p.COMMIT.fullmatch(base), "full candidate and public base Git commits required")
            if envelope["status"] == "reconciled":
                d.require(envelope.get("verified_corpus_commit") == candidate, "completed server receipt commit mismatch")
                state.update(stage="reconciled", server_result=envelope, completed_at=d.utc_now())
                if "error" in state:
                    state["previous_error"] = state.pop("error")
                d.save(state_path, state)
                return state
            d.require(envelope["status"] in ("relay_ready", "awaiting_public_restore"), "server did not authorize this relay phase")
            observed = p.remote_commit(repo, origin, branch)
            d.require(observed in (base, candidate), "local relay observed another public branch commit")
            if observed == base:
                d.require(not state.get("push_attempted"), "a CAS push was already attempted while public ref remains base; needs_codex, no repeated push")
                d.require(d.nonempty(envelope.get("bundle_path")), "server did not declare a candidate bundle")
                p.git(["--git-dir", repo, "cat-file", "-t", base])
                bundle = logs / "received.bundle"
                channel.fetch_bundle(envelope["bundle_path"], bundle)
                heads = p.git(["--git-dir", repo, "bundle", "list-heads", bundle, "HEAD"]).split()
                d.require(heads == [candidate, "HEAD"], "received bundle is not the exact candidate HEAD")
                ref = "refs/prepared-relay/" + batch
                p.git(["--git-dir", repo, "fetch", "--no-tags", bundle, "HEAD:" + ref])
                d.require(p.git(["--git-dir", repo, "rev-parse", ref]) == candidate and
                          p.git(["--git-dir", repo, "show", "-s", "--format=%P", candidate]) == base,
                          "relay candidate/ref parent differs from exact public base")
                observed = p.remote_commit(repo, origin, branch)
                d.require(observed in (base, candidate), "public branch moved before relay CAS")
                if observed == base:
                    state.update(stage="external_write_unknown", push_attempted=True, push_started_at=d.utc_now(), fetched_ref=ref)
                    d.save(state_path, state)
                    p.git(["--git-dir", repo, "push", "--force-with-lease=refs/heads/" + branch + ":" + base,
                           origin, candidate + ":refs/heads/" + branch], env={"GIT_TERMINAL_PROMPT": "0"})
            d.require(p.remote_commit(repo, origin, branch) == candidate, "relay candidate is not the exact public branch commit")
            state.update(stage="public_candidate_awaiting_restore", publicly_observed_commit=candidate)
            d.save(state_path, state)
            result = channel.complete()
            d.require(result.get("stage") == "reconciled" and result.get("verified_corpus_commit") == candidate and
                      result.get("material_count") == envelope["material_count"], "server did not return exact restored reconciliation")
            state.update(stage="reconciled", server_result=result, completed_at=d.utc_now())
            if "error" in state:
                state["previous_error"] = state.pop("error")
            d.save(state_path, state)
            return state
        except Exception as exc:
            state["error"] = str(exc)
            d.save(state_path, state)
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run(d.load(args.spec))
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "needs_codex", "error": str(exc)}, ensure_ascii=False)); return 1


if __name__ == "__main__":
    raise SystemExit(main())
