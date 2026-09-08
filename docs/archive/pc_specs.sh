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