from backend.app.services.llm_inference import LLMInferenceService


class RecordingTokenizer:
    def __init__(self, inputs=None, decode_map=None):
        self.inputs = inputs or {"input_ids": [[11, 12, 13]]}
        self.decode_map = decode_map or {}
        self.chat_template_calls = []
        self.tokenizer_calls = []
        self.decode_calls = []

    def apply_chat_template(self, messages, tokenize, add_generation_prompt):
        self.chat_template_calls.append(
            {
                "messages": messages,
                "tokenize": tokenize,
                "add_generation_prompt": add_generation_prompt,
            }
        )
        return "formatted"

    def __call__(self, text, return_tensors):
        self.tokenizer_calls.append(
            {"text": text, "return_tensors": return_tensors}
        )
        return self.inputs

    def decode(self, output, skip_special_tokens):
        tokens = list(output)
        self.decode_calls.append(
            {"output": tokens, "skip_special_tokens": skip_special_tokens}
        )
        return self.decode_map.get(tuple(tokens), " ".join(str(token) for token in tokens))


class RecordingModel:
    def __init__(self, output=None, device=None):
        self.output = output or [[11, 12, 13, 21, 22]]
        self.device = device
        self.generate_calls = []

    def generate(self, **kwargs):
        self.generate_calls.append(kwargs)
        return self.output


class FakeTensor:
    def __init__(self, values, device=None):
        self.values = list(values)
        self.device = device
        self.to_calls = []

    @property
    def shape(self):
        return (1, len(self.values))

    def to(self, device):
        self.to_calls.append(device)
        return FakeTensor(self.values, device=device)


def build_service(tokenizer, model):
    return LLMInferenceService(
        tokenizer,
        model,
        max_new_tokens=110,
        temperature=0.55,
        top_p=0.9,
        repetition_penalty=1.1,
    )


def test_generate_applies_chat_template_with_system_prompt_first():
    tokenizer = RecordingTokenizer()
    model = RecordingModel()
    service = build_service(tokenizer, model)
    messages = [
        {"role": "user", "content": "I feel anxious"},
        {"role": "assistant", "content": "Tell me more."},
    ]

    service.generate(messages=messages, system_prompt="Stay grounded.")

    assert tokenizer.chat_template_calls == [
        {
            "messages": [
                {"role": "system", "content": "Stay grounded."},
                *messages,
            ],
            "tokenize": False,
            "add_generation_prompt": True,
        }
    ]


def test_generate_forwards_sampling_configuration_to_model_generate():
    tokenizer = RecordingTokenizer(
        inputs={
            "input_ids": [[11, 12, 13]],
            "attention_mask": [[1, 1, 1]],
        }
    )
    model = RecordingModel()
    service = build_service(tokenizer, model)

    service.generate(
        messages=[{"role": "user", "content": "I feel anxious"}],
        system_prompt="Prompt",
    )

    assert model.generate_calls == [
        {
            "input_ids": [[11, 12, 13]],
            "attention_mask": [[1, 1, 1]],
            "max_new_tokens": 110,
            "temperature": 0.55,
            "top_p": 0.9,
            "do_sample": True,
            "repetition_penalty": 1.1,
        }
    ]


def test_generate_decodes_only_completion_tokens_when_prompt_ends_with_capitalized_assistant():
    tokenizer = RecordingTokenizer(
        decode_map={
            (21, 22): "It sounds like you're carrying a lot right now.",
        }
    )
    model = RecordingModel(output=[[11, 12, 13, 21, 22]])
    service = build_service(tokenizer, model)

    response = service.generate(
        messages=[{"role": "user", "content": "I feel anxious"}],
        system_prompt="Prompt",
    )

    assert response == "It sounds like you're carrying a lot right now."
    assert tokenizer.decode_calls == [
        {"output": [21, 22], "skip_special_tokens": True}
    ]


def test_generate_keeps_assistant_word_when_it_appears_inside_reply_text():
    tokenizer = RecordingTokenizer(
        decode_map={
            (21, 22): "The word assistant can appear in the reply itself.",
        }
    )
    model = RecordingModel(output=[[11, 12, 13, 21, 22]])
    service = build_service(tokenizer, model)

    response = service.generate(
        messages=[{"role": "user", "content": "I feel anxious"}],
        system_prompt="Prompt",
    )

    assert response == "The word assistant can appear in the reply itself."


def test_generate_moves_tensor_like_inputs_to_model_device_when_available():
    input_ids = FakeTensor([11, 12, 13])
    attention_mask = FakeTensor([1, 1, 1])
    tokenizer = RecordingTokenizer(
        inputs={"input_ids": input_ids, "attention_mask": attention_mask}
    )
    model = RecordingModel(device="cuda:1")
    service = build_service(tokenizer, model)

    service.generate(
        messages=[{"role": "user", "content": "I feel anxious"}],
        system_prompt="Prompt",
    )

    generate_kwargs = model.generate_calls[0]
    assert input_ids.to_calls == ["cuda:1"]
    assert attention_mask.to_calls == ["cuda:1"]
    assert generate_kwargs["input_ids"].device == "cuda:1"
    assert generate_kwargs["attention_mask"].device == "cuda:1"
