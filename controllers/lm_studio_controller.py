import lmstudio as lms
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

models: list[str] = os.environ.get("LM_STUDIO_MODELS", "").split(" ")
query_window_limit: int = int(os.environ.get("QUERY_MODEL_WINDOW_LIMIT", 4096))
processing_window_limit: int = int(os.environ.get("PROCESSING_MODEL_WINDOW_LIMIT", 4096))

class LMStudioController:
    """
    A controller for interacting with the LLM Studio API.
    """

    def __init__(self, host: str, port: int, model: str) -> None:
        self.host = host
        self.port = port
        self.model = model
        self.client = lms.get_default_client(f"{self.host}:{self.port}")

        # Load initial prompt
        with open(str(os.environ.get("LM_STUDIO_INITIAL_PROMPT")), "r") as file:
            self.initial_prompt = file.read()

    
    @staticmethod
    def get_models() -> list[str]:
        """
        Get a list of available models.
        """
        return models
    

    def get_actual_model(self, is_image: bool) -> lms.LLM:
        """
        Get the model instance based on the selected model.
        """
        return self.client.llm.model(self.model, config={
            "contextLength": processing_window_limit if is_image else query_window_limit
        })


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

        model = self.get_actual_model(image != None)
        chat = lms.Chat()
        config = lms.LlmPredictionConfig(
            temperature=temperature,
        )

        if image:
            image_handle = lms.prepare_image(image)
            chat.add_user_message(self.initial_prompt, images=[image_handle])
        else:
            # Truncate the prompt if it exceeds the limit
            if prompt and len(prompt) > query_window_limit:
                prompt = prompt[:query_window_limit]
            chat.add_user_message(prompt or "Say 'meow :3'")
        
        return model.respond(chat, config=config)
