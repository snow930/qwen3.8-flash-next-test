import json
import statistics

with open("/home/snow/benchmark_results_dual_gpu.json") as f:
    d1867 = json.load(f)
with open("/home/snow/benchmark_results_1600_dual_gpu.json") as f:
    d1600 = json.load(f)

print("==================================================================")
print("1. 短提示词解码对比 (Short Prompt)")
print("==================================================================")
d18_dec = [x["decode_tps"] for x in d1867["short_prompt"]]
d16_dec = [x["decode_tps"] for x in d1600["short_prompt"]]
d18_ec = [x["expert_cache_hit_rate"] for x in d1867["short_prompt"]]
d16_ec = [x["expert_cache_hit_rate"] for x in d1600["short_prompt"]]

m18 = statistics.median(d18_dec)
m16 = statistics.median(d16_dec)
print(f"双卡 @ 1867 MT/s: 解码中位数 {m18:.2f} tok/s {d18_dec} | 专家显存命中率 {d18_ec}%")
print(f"双卡 @ 1600 MT/s: 解码中位数 {m16:.2f} tok/s {d16_dec} | 专家显存命中率 {d16_ec}%")
print(f"--> 解码速度变化: {(m16/m18 - 1)*100:+.2f}%")

print("\n==================================================================")
print("2. 长上下文梯度对比 (Context Gradient)")
print("==================================================================")
for g in ["8k", "32k", "48k", "80k"]:
    pf18 = [x["prefill_tps"] for x in d1867["context_gradient"][g]]
    pf16 = [x["prefill_tps"] for x in d1600["context_gradient"][g]]
    dc18 = [x["decode_tps"] for x in d1867["context_gradient"][g]]
    dc16 = [x["decode_tps"] for x in d1600["context_gradient"][g]]
    kv18 = [x["kv_vram_hit_rate"] for x in d1867["context_gradient"][g]]
    kv16 = [x["kv_vram_hit_rate"] for x in d1600["context_gradient"][g]]

    mpf18 = statistics.median(pf18)
    mpf16 = statistics.median(pf16)
    mdc18 = statistics.median(dc18)
    mdc16 = statistics.median(dc16)

    print(f"--- 梯度 {g} ---")
    print(f"  [Prefill] 1867: {mpf18:.1f} tok/s  vs  1600: {mpf16:.1f} tok/s  ({(mpf16/mpf18-1)*100:+.2f}%)")
    print(f"  [Decode ] 1867: {mdc18:.1f} tok/s  vs  1600: {mdc16:.1f} tok/s  ({(mdc16/mdc18-1)*100:+.2f}%)")
    print(f"  [KV VRAM] 1867: {statistics.median(kv18):.2f}%  vs  1600: {statistics.median(kv16):.2f}%")

print("\n==================================================================")
print("3. 多轮对话前缀缓存重用对比 (Multi-turn Prefix Cache)")
print("==================================================================")
for i in range(3):
    m18_r = d1867["multi_turn"][i]
    m16_r = d1600["multi_turn"][i]
    p18 = m18_r.get("prefill_ms")
    p16 = m16_r.get("prefill_ms")
    d18 = m18_r.get("decode_tps")
    d16 = m16_r.get("decode_tps")
    print(f"第 {i+1} 轮:")
    print(f"  1867 MT/s: Prefill 耗时 {p18} ms, Decode {d18} tok/s")
    print(f"  1600 MT/s: Prefill 耗时 {p16} ms, Decode {d16} tok/s")
