#!/usr/bin/env python3
"""
Sustained CUDA stress test for diagnosing PCIe/Xid stability issues.

Runs heavy GPU compute AND repeated host<->device transfers (to actively
exercise the PCIe link, not just the GPU cores) for a target duration,
logging progress + telemetry to a CSV so a crash can be correlated
against `dmesg` timestamps afterwards.

Usage:
    python3 gpu_stress_test.py --minutes 60
    python3 gpu_stress_test.py --minutes 60 --size 8192 --log run1.csv
"""

import argparse
import csv
import datetime as dt
import subprocess
import sys
import time


def get_gpu_stats():
    """Best-effort GPU telemetry via nvidia-smi. Returns a dict or None."""
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,utilization.memory,temperature.gpu,power.draw,memory.used",
                "--format=csv,noheader,nounits",
            ],
            timeout=5,
        ).decode().strip()
        vals = [v.strip() for v in out.split(",")]
        return {
            "util_gpu_pct": vals[0],
            "util_mem_pct": vals[1],
            "temp_c": vals[2],
            "power_w": vals[3],
            "mem_used_mib": vals[4],
        }
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Sustained CUDA + PCIe stress test")
    parser.add_argument("--minutes", type=float, default=60.0, help="Duration in minutes (default: 60)")
    parser.add_argument("--size", type=int, default=8192, help="Matrix dimension for matmul (default: 8192)")
    parser.add_argument("--transfer-mb", type=int, default=256, help="Host<->device transfer size per iteration, MB (default: 256)")
    parser.add_argument("--log", type=str, default="gpu_stress_log.csv", help="CSV log file path")
    args = parser.parse_args()

    try:
        import torch
    except ImportError:
        sys.exit(
            "PyTorch is not installed in this environment.\n"
            "Install it first, e.g.:\n"
            "  pip install torch --index-url https://download.pytorch.org/whl/cu121\n"
            "(pick the cu1xx tag matching your installed CUDA toolkit)"
        )

    if not torch.cuda.is_available():
        sys.exit("CUDA is not available to PyTorch. Check your driver/install (torch.cuda.is_available() is False).")

    device = torch.device("cuda:0")
    name = torch.cuda.get_device_name(device)
    now = dt.datetime.now
    print(f"[{now()}] Using GPU: {name}")
    print(f"[{now()}] Target duration: {args.minutes:.1f} minutes")
    print(f"[{now()}] Logging to: {args.log}")
    print(f"[{now()}] In another terminal, watch for the fault with:")
    print(f"[{now()}]   sudo dmesg -T -w | grep -iE 'xid|aer'")
    print()

    n = args.size
    a = torch.randn((n, n), device=device, dtype=torch.float32)
    b = torch.randn((n, n), device=device, dtype=torch.float32)

    # Pinned host buffer + device buffer to actively exercise the PCIe link
    # in both directions every iteration (not just GPU-local compute).
    transfer_elems = (args.transfer_mb * 1024 * 1024) // 4
    pinned_buf = torch.empty(transfer_elems, dtype=torch.float32, pin_memory=True)
    gpu_buf = torch.empty(transfer_elems, dtype=torch.float32, device=device)

    end_time = time.time() + args.minutes * 60
    start_time = time.time()
    iteration = 0

    with open(args.log, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "timestamp", "iteration", "elapsed_s", "iter_ms", "gflops",
                "util_gpu_pct", "util_mem_pct", "temp_c", "power_w", "mem_used_mib",
            ]
        )
        f.flush()

        while time.time() < end_time:
            iter_start = time.time()

            # Compute: repeated matmul + elementwise ops to keep the cores busy.
            c = a @ b
            c = torch.sin(c) + torch.cos(a)
            a = (c / (c.abs().mean() + 1e-6)).contiguous()  # keep values bounded

            # PCIe traffic: host -> device -> host every iteration.
            gpu_buf.copy_(pinned_buf, non_blocking=True)
            pinned_buf.copy_(gpu_buf, non_blocking=True)

            torch.cuda.synchronize()

            iter_ms = (time.time() - iter_start) * 1000
            flops = 2 * n**3
            gflops = flops / (iter_ms / 1000) / 1e9

            stats = get_gpu_stats() or {}
            elapsed = time.time() - start_time
            writer.writerow(
                [
                    now().isoformat(),
                    iteration,
                    f"{elapsed:.1f}",
                    f"{iter_ms:.1f}",
                    f"{gflops:.1f}",
                    stats.get("util_gpu_pct", ""),
                    stats.get("util_mem_pct", ""),
                    stats.get("temp_c", ""),
                    stats.get("power_w", ""),
                    stats.get("mem_used_mib", ""),
                ]
            )
            f.flush()

            if iteration % 10 == 0:
                print(
                    f"[{now()}] iter={iteration} elapsed={elapsed/60:.1f}min "
                    f"iter_ms={iter_ms:.0f} gflops={gflops:.0f} "
                    f"temp={stats.get('temp_c', '?')}C power={stats.get('power_w', '?')}W"
                )

            iteration += 1

    print()
    print(f"[{now()}] Completed {iteration} iterations over {args.minutes:.1f} minutes without a fatal error.")
    print(f"[{now()}] If the process instead died/hung, check `dmesg -T` around the last CSV timestamp.")


if __name__ == "__main__":
    main()