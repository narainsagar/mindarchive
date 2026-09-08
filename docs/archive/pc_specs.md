
Before we install anything, let's determine exactly what your machine can handle.

```bash
echo "=== CPU ==="
lscpu | grep -E 'Model name|CPU\(s\)'

echo
echo "=== RAM ==="
free -h

echo
echo "=== GPU ==="
nvidia-smi 2>/dev/null || echo "No NVIDIA GPU detected"

echo
echo "=== DISK ==="
df -h /
```

If nvidia-smi doesn't work, that's fine.


Paste the output here or on any agent.

I'll then tell you exactly:

which Qwen model to use
how many parameters
which quantization
whether Ollama should run inside WSL or Windows
how much RAM/VRAM it will consume
whether Docker + WSL + Qwen can comfortably run together
and the exact installation plan for your machine.

We should do this before creating the Mind Archive development environment, rather than blindly installing a large model.