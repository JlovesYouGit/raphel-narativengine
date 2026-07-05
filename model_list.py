# Model List
# Wan 1.3B GGUF Models (installed locally)
wan_models = {
    "wan2.1-vace-1.3b-q4_0": "n:\\lossless agi\\wan-1.3b-gguf\\wan2.1-vace-1.3b-q4_0.gguf",
    "wan2.1_t2v_1.3b-q4_0": "n:\\lossless agi\\wan-1.3b-gguf\\wan2.1_t2v_1.3b-q4_0.gguf"
}

# Bamboo Nano Model (HuggingFace)
bamboo_nano_model = "KoalaAI/Bamboo-Nano"

# Usage examples:
from transformers import pipeline

# Load Bamboo Nano directly from HuggingFace
pipe = pipeline("text-generation", model="KoalaAI/Bamboo-Nano")

# Or load model components separately
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("KoalaAI/Bamboo-Nano")
model = AutoModelForCausalLM.from_pretrained("KoalaAI/Bamboo-Nano")
