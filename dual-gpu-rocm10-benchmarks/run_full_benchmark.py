import urllib.request
import json
import time
import re
import sys
import uuid
import statistics

LOG_FILE = "/home/snow/下载/Strata/strata-iq3_xxs.log"
API_URL = "http://127.0.0.1:8080/v1/chat/completions"

def parse_engine_log(log_text):
    data = {}
    p_match = re.search(r"strata serve: prompt (\d+) tokens = (\d+) reused \+ (\d+) read in (\d+) ms \(([\d\.]+) tok/s\), (\d+) generated in (\d+) ms \(([\d\.]+) tok/s\), drafts accepted (\d+) of (\d+)", log_text)
    if p_match:
        data['prompt_tokens'] = int(p_match.group(1))
        data['reused_tokens'] = int(p_match.group(2))
        data['read_tokens'] = int(p_match.group(3))
        data['prefill_ms'] = int(p_match.group(4))
        data['prefill_tps'] = float(p_match.group(5))
        data['gen_tokens'] = int(p_match.group(6))
        data['decode_ms'] = int(p_match.group(7))
        data['decode_tps'] = float(p_match.group(8))
        data['drafts_accepted'] = int(p_match.group(9))
        data['drafts_total'] = int(p_match.group(10))
        data['draft_rate'] = round(data['drafts_accepted'] / max(1, data['drafts_total']) * 100, 2)
    
    ec_match = re.search(r"expert cache hit rate: ([\d\.]+)%", log_text)
    if ec_match:
        data['expert_cache_hit_rate'] = float(ec_match.group(1))
        
    kv_match = re.search(r"KV streaming: ([\d\.]+)% of (\d+) block reads hit VRAM, ([\d\.]+) MiB read from RAM", log_text)
    if kv_match:
        data['kv_vram_hit_rate'] = float(kv_match.group(1))
        data['kv_ram_read_mib'] = float(kv_match.group(3))
        
    return data

def run_request(messages, max_tokens=64, temperature=0.7):
    with open(LOG_FILE, "r") as f:
        f.seek(0, 2)
        start_pos = f.tell()
        
    payload = {
        "model": "qwen3.8-flash-next-iq3_xxs",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=600) as resp:
        resp_data = json.loads(resp.read().decode("utf-8"))
    t1 = time.time()
    
    time.sleep(0.4)
    with open(LOG_FILE, "r") as f:
        f.seek(start_pos)
        new_logs = f.read()
        
    metrics = parse_engine_log(new_logs)
    metrics['wall_time_s'] = round(t1 - t0, 2)
    return metrics, resp_data

results = {
    "short_prompt": [],
    "context_gradient": {
        "8k": [],
        "32k": [],
        "48k": [],
        "80k": []
    },
    "multi_turn": []
}

print("==================================================================")
print("1. 短提示词解码性能测试（Short Prompt Decoding, 3 次采样）")
print("==================================================================")
short_prompts = [
    "请写一个快速排序算法的 Python 实现并附带详尽的单元测试与复杂度分析。",
    "请详细分析现代操作系统中虚拟内存管理机制、页表结构、TLB 快表以及缺页异常处理流程。",
    "请设计一个基于分布式一致性协议 Raft 的键值存储系统，并阐述日志复制与选举机制。"
]

for idx, p in enumerate(short_prompts, 1):
    print(f"--> [短提示采样 {idx}/3] 发送请求 (max_tokens=300)...")
    m, _ = run_request([{"role": "user", "content": p}], max_tokens=300, temperature=0.7)
    results["short_prompt"].append(m)
    print(f"    实测: 输入 {m.get('prompt_tokens')} tok | 解码 {m.get('gen_tokens')} tok @ {m.get('decode_tps')} tok/s (耗时 {m.get('decode_ms')}ms) | MTP 接受率 {m.get('draft_rate')}% | 专家缓存命中率 {m.get('expert_cache_hit_rate')}%")

decodes = [x['decode_tps'] for x in results["short_prompt"]]
print(f"--> 短提示解码实测值: {decodes} tok/s | 中位数: {statistics.median(decodes):.2f} tok/s\n")

print("==================================================================")
print("2. 长上下文梯度测试（8k / 32k / 48k / 80k Prefill & Decode，各 3 次采样）")
print("==================================================================")

base_sentence = "In deep learning, transformer-based mixture-of-experts architectures dramatically enhance model capacity and training efficiency by selectively routing tokens to specialized feed-forward network layers. "

target_repeats = {
    "8k": 440,     # ~8000 tokens
    "32k": 1750,   # ~32000 tokens
    "48k": 2650,   # ~48000 tokens
    "80k": 4400    # ~80000 tokens
}

for label in ["8k", "32k", "48k", "80k"]:
    repeats = target_repeats[label]
    print(f"\n--- 测试梯度: {label} (约 {label} tokens, 3 次采样) ---")
    for r in range(1, 4):
        # 确保每次 prompt 唯一，测试纯净 Prefill（无缓存重用）
        unique_id = uuid.uuid4().hex
        full_text = f"Context Benchmark Test Run {label}-{r} [ID: {unique_id}]:\n" + (base_sentence * repeats) + f"\nQuestion {r}: Based on the text above, summarize the key benefits of MoE in one sentence."
        print(f"--> [{label} 采样 {r}/3] 发送请求 (max_tokens=64)...")
        m, _ = run_request([{"role": "user", "content": full_text}], max_tokens=64, temperature=0.7)
        results["context_gradient"][label].append(m)
        print(f"    实测: Prompt {m.get('prompt_tokens')} tok (Prefill 耗时 {m.get('prefill_ms')}ms @ {m.get('prefill_tps')} tok/s) | 解码 {m.get('gen_tokens')} tok @ {m.get('decode_tps')} tok/s | KV 显存命中率 {m.get('kv_vram_hit_rate')}% (RAM读取 {m.get('kv_ram_read_mib')}MB)")

    pf_list = [x['prefill_tps'] for x in results["context_gradient"][label]]
    dc_list = [x['decode_tps'] for x in results["context_gradient"][label]]
    print(f"--> [{label} 汇总] Prefill 速度: {pf_list} tok/s (中位数: {statistics.median(pf_list):.1f} tok/s) | 解码速度: {dc_list} tok/s (中位数: {statistics.median(dc_list):.1f} tok/s)")

print("\n==================================================================")
print("3. 多轮对话前缀缓存重用测试（Multi-turn Prefix Cache Reuse）")
print("==================================================================")

# 构造一个 4000 tokens 级别的基准前缀
context_4k = "Long reference text for multi-turn benchmark:\n" + (base_sentence * 220)
dialog_messages = [
    {"role": "user", "content": context_4k + "\n第一轮问题：请简要列出前文中提到的核心技术概念。"}
]

print("--> [第 1 轮提问] 初次建立上下文缓存...")
m1, r1 = run_request(dialog_messages, max_tokens=100)
results["multi_turn"].append(m1)
assistant_content_1 = r1["choices"][0]["message"].get("content") or r1["choices"][0]["message"].get("reasoning_content", "已解析概念。")
print(f"    第 1 轮: Prompt {m1.get('prompt_tokens')} tok (Reused {m1.get('reused_tokens')} tok, Read {m1.get('read_tokens')} tok) | Prefill {m1.get('prefill_tps')} tok/s | 解码 {m1.get('decode_tps')} tok/s")

# 追加助手回复与第 2 轮问题
dialog_messages.append({"role": "assistant", "content": assistant_content_1})
dialog_messages.append({"role": "user", "content": "第二轮跟进：请针对刚才列出的第一个核心概念，详细解释其在分布式系统中的通信开销优化策略。"})

print("--> [第 2 轮提问] 测试前缀快取重用率...")
m2, r2 = run_request(dialog_messages, max_tokens=100)
results["multi_turn"].append(m2)
reuse_rate_2 = round(m2.get('reused_tokens', 0) / max(1, m2.get('prompt_tokens', 1)) * 100, 2)
print(f"    第 2 轮: Prompt {m2.get('prompt_tokens')} tok (Reused {m2.get('reused_tokens')} tok, Read {m2.get('read_tokens')} tok) | 缓存重用率: {reuse_rate_2}% | Prefill 耗时 {m2.get('prefill_ms')}ms")

# 追加第 3 轮问题
assistant_content_2 = r2["choices"][0]["message"].get("content") or r2["choices"][0]["message"].get("reasoning_content", "已提供优化策略。")
dialog_messages.append({"role": "assistant", "content": assistant_content_2})
dialog_messages.append({"role": "user", "content": "第三轮跟进：总结一下以上两轮讨论的结论。"})

print("--> [第 3 轮提问] 测试多轮累积缓存重用率...")
m3, _ = run_request(dialog_messages, max_tokens=100)
results["multi_turn"].append(m3)
reuse_rate_3 = round(m3.get('reused_tokens', 0) / max(1, m3.get('prompt_tokens', 1)) * 100, 2)
print(f"    第 3 轮: Prompt {m3.get('prompt_tokens')} tok (Reused {m3.get('reused_tokens')} tok, Read {m3.get('read_tokens')} tok) | 缓存重用率: {reuse_rate_3}% | Prefill 耗时 {m3.get('prefill_ms')}ms")

# 保存结果
with open("/home/snow/benchmark_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
with open("/home/snow/benchmark_results_1600_dual_gpu.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n==================================================================")
print("全部测试已完成！详细数据已写入 /home/snow/benchmark_results_1600_dual_gpu.json")
print("==================================================================")
