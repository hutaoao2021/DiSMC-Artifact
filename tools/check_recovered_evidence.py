#!/usr/bin/env python3
import collections,csv,hashlib,json,pathlib,statistics,zipfile
R=pathlib.Path(__file__).resolve().parents[1]
def rows(p):return list(csv.DictReader((R/p).open(encoding="utf-8-sig")))
def sha(b):return hashlib.sha256(b).hexdigest()
for item in json.loads((R/"data/historical/file-provenance.json").read_text(encoding="utf-8")):
    assert sha((R/item["distributed_path"]).read_bytes())==item["distributed_sha256"]
raw=rows("results/online_fixed_queries_per_trial.csv");assert len(raw)==48
g=collections.defaultdict(list)
for x in raw:g[(x["dataset"].lower(),x["query"],x["method"].lower())].append(float(x["e2e_s"]))
for x in rows("results/online_fixed_queries.csv"):
    v=g[(x["dataset"].lower(),x["query"],x["method"].lower())];assert len(v)==3
    assert abs(statistics.mean(v)-float(x["mean_e2e_s"]))<.0011
    assert abs(statistics.stdev(v)-float(x["sample_sd_s"]))<.0011
idx=rows("configs/historical-command-index.csv")
for x in idx:
    if x["target"]=="Fig. 4":
        j=json.loads((R/x["command_record"]).read_text())
        assert j["input_current_rehash"]["sha256"]==j["input_sha256_recorded"]
        assert j["current_wrapper_jar"]["sha256"]==j["jar_sha256_recorded"]
        assert j["spark_conf_recorded"]["spark.skyline.shardReadBudget"]=="0.05"
t=[float(x["end_to_end_s"]) for x in idx if x["binding"]=="TDrive three-run paper batch"]
assert len(t)==3
assert abs(statistics.mean(t)-2958.053)<.0011 and abs(statistics.stdev(t)-75.392)<.0011
z=R/"artifact/DiSMC-source-20261111-budget10-validated.zip"
with zipfile.ZipFile(z) as f:
    m=json.loads(f.read("DiSMC-source/SOURCE_MANIFEST.json"))
    for x in m["files"]:assert sha(f.read("DiSMC-source/"+x["path"]))==x["sha256"]
    old=zipfile.ZipFile(R/"artifact/DiSMC-source-20261102-release.zip")
    production=[x for x in old.namelist() if "/src/main/" in x and not x.endswith("/")]
    delta=[x for x in production if old.read(x)!=f.read(x)]
    assert delta==["DiSMC-source/src/main/java/com/ExperimentConfig.java"],delta
print("PASS: preprocessing hashes; Fig.4 48 trials, means/SD, input/JAR bindings; Table I TDrive three trials; candidate manifest and single production delta")
