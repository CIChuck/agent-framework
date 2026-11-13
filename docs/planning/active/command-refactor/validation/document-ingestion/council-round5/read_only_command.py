from pathlib import Path
import datetime,json,os,subprocess,sys
R=Path("/Users/chuckrussell/Dev/gendev/agent-framework").resolve()
I=Path(__file__).parent.resolve()
if len(sys.argv)<4 or sys.argv[2]!="--":raise SystemExit("usage: read_only_command.py OWN_FRESH_SCRATCH -- COMMAND ARGS...")
own=Path(sys.argv[1]).resolve()
if not own.is_dir() or own==R or R in own.parents or own==I or I in own.parents:raise SystemExit("output root must be YOUR existing fresh external scratch, outside repository and supplied inputs")
args=sys.argv[3:]
if Path(args[0]).name=="git":
 if len(args)<2 or args[1] not in {"ls-files","rev-parse","branch","status","diff","show","log","check-ignore","merge-base","ls-tree","cat-file"}:raise SystemExit("only direct read-only git subcommands are permitted")
 if args[1]=="branch" and args[2:]!=["--show-current"]:raise SystemExit("only branch --show-current is permitted")
 if any(x.startswith("--output") for x in args):raise SystemExit("write redirections belong only in your own scratch")
env=dict(os.environ,GIT_OPTIONAL_LOCKS="0",PYTHONDONTWRITEBYTECODE="1",UV_OFFLINE="1",UV_NO_SYNC="1",UV_FROZEN="1",UV_PYTHON_DOWNLOADS="never",UV_CACHE_DIR=str(own/"uv-cache"),XDG_CACHE_HOME=str(own/"xdg-cache"),TMPDIR=str(own/"tmp"))
(own/"tmp").mkdir(exist_ok=True,mode=0o700)
audit={"argv":args,"cwd":str(R),"git_optional_locks":env["GIT_OPTIONAL_LOCKS"],"pythondontwritebytecode":env["PYTHONDONTWRITEBYTECODE"],"recorded_at":datetime.datetime.now(datetime.UTC).isoformat()}
with (own/"command-audit.jsonl").open("a") as f:f.write(json.dumps(dict(audit,event="start"))+"\n")
p=subprocess.run(args,cwd=R,env=env)
with (own/"command-audit.jsonl").open("a") as f:f.write(json.dumps(dict(audit,event="end",exit=p.returncode))+"\n")
raise SystemExit(p.returncode)
