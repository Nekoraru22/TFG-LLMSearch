import lmstudio as lms

class LLMStudioController:
    """
    A controller for interacting with the LLM Studio API.
    """

    def __init__(self, host: str, port: int, model: str) -> None:
        self.host = host
        self.port = port
        self.model = model
        self.client = lms.get_default_client(f"{self.host}:{self.port}")

        # Load initial prompt
        with open("data/initial_prompt.md", "r") as file:
            self.initial_prompt = file.read()


    def get_model(self) -> lms.LLM:
        return self.client.llm.model(self.model)


    def analyze(self, prompt: str | None = None, image: str | None = None) -> lms.PredictionResult:
        if not prompt and not image:
            raise ValueError("At least one of prompt or image must be provided.")

        model = self.get_model()
        chat = lms.Chat()

        if image:
            image_handle = lms.prepare_image(image)
            chat.add_user_message(self.initial_prompt, images=[image_handle])
        else:
            chat.add_user_message(prompt or "Say 'meow :3'")
        
        return model.respond(chat)
