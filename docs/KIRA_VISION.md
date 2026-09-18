# Kira Vision

Kira Vision sends frames captured only from Kira's isolated Cloud desktop to a local image-capable Ollama model. No host desktop capture is used.

Default model: qwen2.5vl:3b. Change it with the Studio setting vision_model.

The vision description is fed into Game Brain before each decision, producing a real frame -> visual description -> decision -> input -> new frame loop. Performance depends heavily on GPU/CPU and the selected model.
