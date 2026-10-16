import json
import statistics

with open("/home/snow/benchmark_results_1867.json") as f:
    single = json.load(f)
with open("/home/snow/benchmark_results_dual_gpu.json") as f:
    dual = json.load(f)

print("==================================================================")
print("1. 短提示词解码对比 (Short Prompt)")
print("==================================================================")
s_dec = [x["decode_tps"] for x in single["short_prompt"]]
d_dec = [x["decode_tps"] for x in dual["short_prompt"]]
s_ec = [x["expert_cache_hit_rate"] for x in single["short_prompt"]]
d_ec = [x["expert_cache_hit_rate"] for x in dual["short_prompt"]]
s_mtp = [x["draft_rate"] for x in single["short_prompt"]]
d_mtp = [x["draft_rate"] for x in dual["short_prompt"]]

s_dec_med = statistics.median(s_dec)
d_dec_med = statistics.median(d_dec)
s_ec_med = statistics.median(s_ec)
d_ec_med = statistics.median(d_ec)

print(f"单卡 (7900XT)      : 解码中位数 {s_dec_med:.2f} tok/s {s_dec} | 专家显存命中率中位数 {s_ec_med:.1f}%")
print(f"双卡 (7900XT+6800XT): 解码中位数 {d_dec_med:.2f} tok/s {d_dec} | 专家显存命中率中位数 {d_ec_med:.1f}%")
print(f"--> 解码速度提升: {(d_dec_med / s_dec_med - 1) * 100:+.2f}%")
print(f"--> 专家显存命中率提升: {d_ec_med - s_ec_med:+.1f}% (最高单次达到 98.0%！)")

print("\n==================================================================")
print("2. 长上下文梯度对比 (Context Gradient)")
print("==================================================================")
for g in ["8k", "32k", "48k", "80k"]:
    s_pf = [x["prefill_tps"] for x in single["context_gradient"][g]]
    d_pf = [x["prefill_tps"] for x in dual["context_gradient"][g]]
    s_dc = [x["decode_tps"] for x in single["context_gradient"][g]]
    d_dc = [x["decode_tps"] for x in dual["context_gradient"][g]]
    s_kv = [x["kv_vram_hit_rate"] for x in single["context_gradient"][g]]
    d_kv = [x["kv_vram_hit_rate"] for x in dual["context_gradient"][g]]
    s_ram = [x["kv_ram_read_mib"] for x in single["context_gradient"][g]]
    d_ram = [x["kv_ram_read_mib"] for x in dual["context_gradient"][g]]

    spf_m = statistics.median(s_pf)
    dpf_m = statistics.median(d_pf)
    sdc_m = statistics.median(s_dc)
    ddc_m = statistics.median(d_dc)

    print(f"--- 梯度 {g} (实测 ~{int(statistics.mean([x['prompt_tokens'] for x in dual['context_gradient'][g]]))}) tokens ---")
    print(f"  [Prefill] 单卡 {spf_m:.1f} tok/s  vs  双卡 {dpf_m:.1f} tok/s  ({(dpf_m/spf_m-1)*100:+.2f}%)")
    print(f"  [Decode ] 单卡 {sdc_m:.1f} tok/s  vs  双卡 {ddc_m:.1f} tok/s  ({(ddc_m/sdc_m-1)*100:+.2f}%)")
    print(f"  [KV VRAM] 单卡 {statistics.median(s_kv):.2f}% (读RAM {statistics.median(s_ram):.1f}MB) vs 双卡 {statistics.median(d_kv):.2f}% (读RAM {statistics.median(d_ram):.1f}MB)")

print("\n==================================================================")
print("3. 多轮对话前缀缓存重用对比 (Multi-turn Prefix Cache)")
print("==================================================================")
for i in range(3):
    s_m = single["multi_turn"][i]
    d_m = dual["multi_turn"][i]
    sp_ms = s_m.get("prefill_ms")
    dp_ms = d_m.get("prefill_ms")
    sd_tps = s_m.get("decode_tps")
    dd_tps = d_m.get("decode_tps")
    print(f"第 {i+1} 轮:")
    print(f"  单卡: Prefill {sp_ms} ms, Decode {sd_tps} tok/s")
    print(f"  双卡: Prefill {dp_ms} ms, Decode {dd_tps} tok/s")
