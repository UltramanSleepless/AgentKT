set -euo pipefail

FILE_ID="1sKMq5nmOJAGjKP6geAohuekTZbrAzGK2"
OUT_ZIP="pretrained_lm.zip"
MODEL_DIR="../model"

mkdir -p "$MODEL_DIR"

download_with_gdown() {
  gdown --id "$FILE_ID" -O "$OUT_ZIP" --no-cookies
}

download_with_wget() {
  TMP_COOKIES="$(mktemp)"
  CONFIRM_TOKEN=$(wget --quiet --save-cookies "$TMP_COOKIES" --keep-session-cookies --no-check-certificate "https://docs.google.com/uc?export=download&id=$FILE_ID" -O- \
    | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1/p' | head -n1)
  if [ -z "${CONFIRM_TOKEN:-}" ]; then
    # Fallback to drive.usercontent direct link
    wget --quiet --load-cookies "$TMP_COOKIES" "https://drive.usercontent.google.com/download?id=$FILE_ID&export=download" -O "$OUT_ZIP" || true
  else
    wget --quiet --load-cookies "$TMP_COOKIES" "https://docs.google.com/uc?export=download&confirm=$CONFIRM_TOKEN&id=$FILE_ID" -O "$OUT_ZIP"
  fi
  rm -f "$TMP_COOKIES"
}

echo "Downloading pretrained language models archive..."
if command -v gdown >/dev/null 2>&1; then
  download_with_gdown || true
fi

if [ ! -s "$OUT_ZIP" ]; then
  download_with_wget
fi

if [ ! -s "$OUT_ZIP" ]; then
  echo "Error: Download failed. '$OUT_ZIP' is missing or empty." >&2
  exit 1
fi

# Verify zip integrity
if ! unzip -tq "$OUT_ZIP" >/dev/null 2>&1; then
  echo "Error: The downloaded file is not a valid zip. Please check network/proxy and retry." >&2
  exit 1
fi

echo "Extracting archive to $MODEL_DIR ..."
unzip -o -q "$OUT_ZIP" -d "$MODEL_DIR"

# Move expected directories up one level if present
if [ -d "$MODEL_DIR/pretrained_lm/gpt_code_v1" ]; then
  mv "$MODEL_DIR/pretrained_lm/gpt_code_v1" "$MODEL_DIR/"
fi
if [ -d "$MODEL_DIR/pretrained_lm/gpt_code_v1_student" ]; then
  mv "$MODEL_DIR/pretrained_lm/gpt_code_v1_student" "$MODEL_DIR/"
fi

# Cleanup extracted wrapper directory if it exists
if [ -d "$MODEL_DIR/pretrained_lm" ]; then
  rm -rf "$MODEL_DIR/pretrained_lm"
fi

rm -f "$OUT_ZIP"
echo "Done. Models available under $MODEL_DIR."