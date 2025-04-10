import lmstudio as lms

models: list[str] = [
    "gemma-3-12b-it",
    "jonahhenry/mistral-7b-instruct-v0.2.Q4_K_M-GGUF",
]

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

    
    @staticmethod
    def get_models() -> list[str]:
        """
        Get a list of available models.
        """
        return models
    

    def get_actual_model(self) -> lms.LLM:
        """
        Get the model instance based on the selected model.
        """
        return self.client.llm.model(self.model)


    def analyze(self, prompt: str | None = None, image: str | None = None, temperature: float = 0.7) -> lms.PredictionResult:
        """
        Analyze a prompt or an image using the selected model.

        Args:
            prompt: The prompt to analyze.
            image: The path to the image to analyze.
        Returns:
            The result of the analysis.
        """
        if not prompt and not image:
            raise ValueError("At least one of prompt or image must be provided.")

        model = self.get_actual_model()
        chat = lms.Chat()
        config = lms.LlmPredictionConfig(
            temperature=temperature,
        )

        if image:
            image_handle = lms.prepare_image(image)
            chat.add_user_message(self.initial_prompt, images=[image_handle])
        else:
            chat.add_user_message(prompt or "Say 'meow :3'")
        
        return model.respond(chat, config=config)
