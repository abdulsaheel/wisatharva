import json
from flask import request, Flask
from g4f.image import is_allowed_extension, to_image
from .api import Api
from flask import request, Response
import json
import logging


class Backend_Api(Api):    
    """
    Handles various endpoints in a Flask application for backend operations.

    This class provides methods to interact with models, providers, and to handle
    various functionalities like conversations, error handling, and version management.

    Attributes:
        app (Flask): A Flask application instance.
        routes (dict): A dictionary mapping API endpoints to their respective handlers.
    """
    def __init__(self, app: Flask) -> None:
        """
        Initialize the backend API with the given Flask application.

        Args:
            app (Flask): Flask application instance to attach routes to.
        """
        self.app: Flask = app
        self.routes = {
            '/backend-api/v2/models': {
                'function': self.get_models,
                'methods': ['GET']
            },
            '/backend-api/v2/models/<provider>': {
                'function': self.get_provider_models,
                'methods': ['GET']
            },
            '/backend-api/v2/image_models': {
                'function': self.get_image_models,
                'methods': ['GET']
            },
            '/backend-api/v2/providers': {
                'function': self.get_providers,
                'methods': ['GET']
            },
            '/backend-api/v2/version': {
                'function': self.get_version,
                'methods': ['GET']
            },
            '/backend-api/v2/conversation': {
                'function': self.handle_conversation,
                'methods': ['POST']
            },
            '/backend-api/v2/error': {
                'function': self.handle_error,
                'methods': ['POST']
            },
            '/images/<path:name>': {
                'function': self.serve_images,
                'methods': ['GET']
            }
        }

    def handle_error(self):
        """
        Initialize the backend API with the given Flask application.

        Args:
            app (Flask): Flask application instance to attach routes to.
        """
        print(request.json)
        return 'ok', 200



    def handle_conversation(self):
        """
        Handles conversation requests and streams responses back.

        Returns:
            Response: A Flask response object for streaming.
        """

        # List of models to try
        models = [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0613",
            "gpt-4o",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-16k-0613",
            "gpt-3.5-long",
            "gpt-4",
            "gpt-4-0613",
            "gpt-4-32k",
            "gpt-4-32k-0613",
            "gpt-4-turbo",
            "meta-ai",
            "llama3-8b",
            "llama3-70b",
            "llama3-8b-instruct",
            "llama3-70b-instruct",
            "codellama-34b-instruct",
            "codellama-70b-instruct",
            "mixtral-8x7b",
            "mistral-7b",
            "mistral-7b-v02",
            "gemini",
            "gemini-pro",
            "claude-v2",
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
            "reka",
            "blackbox",
            "command-r+",
            "dbrx-instruct",
            "gigachat",
            "pi"
        ]

        # Initialize kwargs dictionary
        kwargs = {}

        try:
            # Handle file upload if present
            if "file" in request.files:
                file = request.files['file']
                if file.filename != '' and is_allowed_extension(file.filename):
                    kwargs['image'] = to_image(file.stream, file.filename.endswith('.svg'))
                    kwargs['image_name'] = file.filename
            
            # Parse JSON data from request
            if "json" in request.form:
                json_data = json.loads(request.form['json'])
            else:
                json_data = request.json

            # Validate json_data
            if not json_data:
                raise ValueError("JSON data is missing or invalid")
            
            # Prepare additional conversation kwargs
            kwargs = self._prepare_conversation_kwargs(json_data, kwargs)

            # Try each model until one works without raising an exception
            for model in models:
                try:
                    kwargs['model'] = model
                    logging.debug(f"Trying model: {model}")

                    # Create the response stream
                    response_stream = self._create_response_stream(
                        kwargs, json_data.get("conversation_id"), json_data.get("provider")
                    )

                    # Return the streaming response
                    return self.app.response_class(
                        response_stream,
                        mimetype='text/event-stream'
                    )
                except Exception as e:
                    logging.error(f"Model {model} failed with error: {e}")
                    continue  # Try the next model

            # If no model succeeds, return an error response
            return self.app.response_class(
                "All models failed to process the request",
                mimetype='text/event-stream',
                status=500
            )

        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Error processing request: {e}")
            return self.app.response_class(
                "Invalid request data",
                mimetype='text/event-stream',
                status=400
            )
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return self.app.response_class(
                "Internal server error",
                mimetype='text/event-stream',
                status=500
            )

                
    def get_provider_models(self, provider: str):
        models = super().get_provider_models(provider)
        if models is None:
            return 404, "Provider not found"
        return models

    def _format_json(self, response_type: str, content) -> str:
        """
        Formats and returns a JSON response.

        Args:
            response_type (str): The type of the response.
            content: The content to be included in the response.

        Returns:
            str: A JSON formatted string.
        """
        return json.dumps(super()._format_json(response_type, content)) + "\n"