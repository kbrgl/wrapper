import openai
import dotenv
import os
from slack_bolt import App

dotenv.load_dotenv()


# Our little "database." Heh.
documents = []


# Set up OpenAI API.

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = "org-IlcMKzKZJGWE8QM4uHoBCayl"


def answer_question(question, documents):
    return openai.Answer.create(
        search_model="ada",
        model="curie",
        question="",
        documents=[],
        examples_context="Joel Johnson: I’m working on getting the ML pipeline ready with Kabir. We’re currently reading through the Luigi docs.",
        examples=[
            ["Who is working on the ML pipeline?", "Joel is working on it with Kabir."],
            ["What are Joel and Kabir working on?", "The ML pipeline."],
        ],
        max_tokens=64,
        stop=["\n", "<|endoftext|>"],
    )


def join_documents(documents):
    return "\n".join(
        [
            "<@" + document["event"]["user"] + ">: " + document["event"]["text"]
            for document in documents
        ]
    )


def summarize_documents(documents):
    return openai.Completion.create(
        engine="davinci-instruct-beta",
        prompt=f"""Summarize the following set of messages discussing a project:

{join_documents(documents)}

Summary:""",
        max_tokens=128,
    )["choices"][0]


def load_documents():
    return documents


# Set up Slack app.


app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)


@app.event("app_mention")
def mention(body, say, logger):
    if "update" in body["event"]["text"].lower():
        documents.append(body)
        say("Got it!")
        return
    docs = load_documents()
    if not docs:
        say(
            "You haven’t told Wrapped anything yet, push some updates to get a summary!"
        )
        return
    say(summarize_documents(load_documents()))


# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
