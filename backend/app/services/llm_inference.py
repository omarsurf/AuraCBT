import torch


class LLMInferenceService:
    def __init__(
        self,
        tokenizer,
        model,
        max_new_tokens: int,
        temperature: float,
        top_p: float,
        repetition_penalty: float,
    ):
        self.tokenizer = tokenizer
        self.model = model
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.repetition_penalty = repetition_penalty

    def generate(self, messages: list[dict[str, str]], system_prompt: str) -> str:
        prompt_messages = [{"role": "system", "content": system_prompt}, *messages]
        text = self.tokenizer.apply_chat_template(
            prompt_messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = self._move_inputs_to_model_device(
            self.tokenizer(text, return_tensors="pt")
        )

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                do_sample=True,
                repetition_penalty=self.repetition_penalty,
            )

        completion = outputs[0][self._prompt_token_count(inputs["input_ids"]) :]
        return self.tokenizer.decode(completion, skip_special_tokens=True).strip()

    def _move_inputs_to_model_device(self, inputs):
        device = getattr(self.model, "device", None)
        if device is None:
            return inputs

        moved_inputs = {}
        for key, value in inputs.items():
            moved_inputs[key] = value.to(device) if hasattr(value, "to") else value
        return moved_inputs

    def _prompt_token_count(self, input_ids) -> int:
        shape = getattr(input_ids, "shape", None)
        if shape is not None:
            return shape[-1]

        if not input_ids:
            return 0

        first_item = input_ids[0]
        if hasattr(first_item, "__len__") and not isinstance(first_item, (str, bytes)):
            return len(first_item)
        return len(input_ids)
