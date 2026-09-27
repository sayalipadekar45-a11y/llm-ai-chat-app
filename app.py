from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Read API key from .env
api_key = os.getenv("OPENAI_API_KEY")

# Create OpenAI client only if API key exists
client = OpenAI(api_key=api_key) if api_key else None


# --------------------------------------------------
# FREE DEMO AI RESPONSE
# --------------------------------------------------

def demo_ai_response(message, instructions):

    text = message.lower().strip()

    # Hello / Hi
    if text in [
        "hello",
        "hi",
        "hey",
        "hello there",
        "hi there",
        "hey there"
    ]:
        return (
            "Hello! 👋 I am your AI Assistant.\n\n"
            "This is the free demo mode of the LLM Chat Application."
        )

    # Machine Learning
    if "machine learning" in text:
        return (
            "Machine Learning (ML) is a part of Artificial Intelligence (AI) "
            "that allows computers to learn from data and make predictions "
            "or decisions without being explicitly programmed for every task.\n\n"
            "Example:\n"
            "A spam email filter can learn from previous emails and identify "
            "whether a new email is spam or not."
        )

    # Artificial Intelligence
    if (
        "artificial intelligence" in text
        or text == "ai"
        or "what is ai" in text
    ):
        return (
            "Artificial Intelligence (AI) is technology that allows computers "
            "to perform tasks that normally require human intelligence.\n\n"
            "Examples:\n"
            "• Voice assistants\n"
            "• Chatbots\n"
            "• Image recognition\n"
            "• Recommendation systems\n"
            "• Self-driving technology"
        )

    # Python
    if "python" in text:
        return (
            "Python is a popular programming language.\n\n"
            "It is commonly used for:\n"
            "• Web development\n"
            "• Data science\n"
            "• Machine Learning\n"
            "• Artificial Intelligence\n"
            "• Automation\n\n"
            "Example:\n"
            "print('Hello World')"
        )

    # LLM
    if (
        "llm" in text
        or "large language model" in text
    ):
        return (
            "LLM stands for Large Language Model.\n\n"
            "An LLM is an AI model trained on a large amount of text "
            "to understand and generate human-like language.\n\n"
            "Example:\n"
            "Chatbots can use LLMs to understand user questions and "
            "generate useful responses."
        )

    # Flask
    if "flask" in text:
        return (
            "Flask is a lightweight Python web framework.\n\n"
            "It is commonly used to build web applications and APIs.\n\n"
            "Example:\n"
            "A Flask application can receive a request from a website "
            "and return an AI-generated response."
        )

    # API
    if "api" in text:
        return (
            "API stands for Application Programming Interface.\n\n"
            "An API allows different software applications to communicate "
            "with each other.\n\n"
            "Example:\n"
            "A Flask backend can send a request to an AI API and receive "
            "an AI response."
        )

    # Chatbot
    if "chatbot" in text:
        return (
            "A chatbot is a software application that communicates with "
            "users through text or voice.\n\n"
            "Example:\n"
            "Customer support chatbots can answer common questions "
            "automatically."
        )

    # If custom instructions are provided
    if instructions:
        return (
            "Demo response based on your custom instructions.\n\n"
            f"Your instruction:\n{instructions}\n\n"
            f"Your message:\n{message}\n\n"
            "This application is currently running in Free Demo Mode."
        )

    # Default response
    return (
        "This is a free demo response.\n\n"
        f"Your message was:\n\"{message}\"\n\n"
        "The application supports:\n"
        "• Conversation History\n"
        "• Custom Instructions\n"
        "• Error Handling\n"
        "• Token Usage Tracking\n"
        "• LLM API Integration\n\n"
        "Live LLM responses require an available API credit balance."
    )


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# CHAT API
# --------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def chat():

    try:

        # Get JSON data from frontend
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Invalid request data."
            }), 400

        # Get user message
        message = data.get("message", "").strip()

        # Get previous conversation
        history = data.get("history", [])

        # Get custom instructions
        instructions = data.get(
            "instructions",
            ""
        ).strip()

        # Validate message
        if not message:
            return jsonify({
                "error": "Please enter a message."
            }), 400

        # --------------------------------------------------
        # TRY REAL OPENAI API
        # --------------------------------------------------

        if api_key and client:

            try:

                messages = []

                # Add custom instructions
                if instructions:

                    messages.append({
                        "role": "system",
                        "content": instructions
                    })

                # Add conversation history
                for item in history:

                    role = item.get("role")
                    content = item.get("content")

                    if (
                        role in ["user", "assistant"]
                        and content
                    ):

                        messages.append({
                            "role": role,
                            "content": content
                        })

                # Add current user message
                messages.append({
                    "role": "user",
                    "content": message
                })

                # OpenAI API request
                response = client.chat.completions.create(

                    model="gpt-4o-mini",

                    messages=messages,

                    temperature=0.7,

                    max_tokens=500
                )

                # Get AI response
                answer = response.choices[0].message.content

                # Get token usage
                usage = response.usage

                return jsonify({

                    "reply": answer,

                    "mode": "Live LLM API",

                    "usage": {

                        "prompt_tokens":
                            usage.prompt_tokens,

                        "completion_tokens":
                            usage.completion_tokens,

                        "total_tokens":
                            usage.total_tokens
                    }

                })

            except Exception as api_error:

                print(
                    "OPENAI API ERROR:",
                    repr(api_error)
                )

                # --------------------------------------------------
                # FALLBACK IF API CREDIT IS EXHAUSTED
                # --------------------------------------------------

                if (
                    "credit_balance_exhausted"
                    in str(api_error)
                ):

                    answer = demo_ai_response(
                        message,
                        instructions
                    )

                    return jsonify({

                        "reply": answer,

                        "mode":
                            "Free Demo Mode - API Credits Unavailable",

                        "usage": {

                            "prompt_tokens":
                                len(message.split()),

                            "completion_tokens":
                                len(answer.split()),

                            "total_tokens":
                                (
                                    len(message.split())
                                    +
                                    len(answer.split())
                                )
                        }

                    })

                # Other API error
                return jsonify({

                    "error":
                        "AI API Error: "
                        + str(api_error)

                }), 500

        # --------------------------------------------------
        # FREE DEMO MODE
        # --------------------------------------------------

        else:

            answer = demo_ai_response(
                message,
                instructions
            )

            return jsonify({

                "reply": answer,

                "mode":
                    "Free Demo Mode",

                "usage": {

                    "prompt_tokens":
                        len(message.split()),

                    "completion_tokens":
                        len(answer.split()),

                    "total_tokens":
                        (
                            len(message.split())
                            +
                            len(answer.split())
                        )
                }

            })

    except Exception as e:

        print(
            "SERVER ERROR:",
            repr(e)
        )

        return jsonify({

            "error":
                "Something went wrong: "
                + str(e)

        }), 500


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )