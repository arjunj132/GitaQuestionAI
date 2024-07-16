from huggingface_hub import InferenceClient
import json
import os
import random
import http.client
from tqdm import tqdm


def generate():
    conn = http.client.HTTPSConnection("bhagavad-gita3.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': os.environ['RAPIDAPI_KEY'],
        'x-rapidapi-host': "bhagavad-gita3.p.rapidapi.com"
    }

    shlokas = [
        "0",
        "4",
        "7",
        "4",
        "4",
        "2",
        "4",
        "3",
        "2",
        "3",
        "4",
        "5",
        "2",
        "3",
        "2",
        "2",
        "2",
        "2",
        "7",
    ]


    chapter = random.randint(1, 18)
    shlokarange = random.randint(1, int(shlokas[chapter]))
    fullresults = []
    for x in tqdm(range(shlokarange*10-9, shlokarange*10+1)):
        tqdm.write("Calling Shloka")
        conn.request("GET", f"/v2/chapters/{chapter}/verses/{x}/", headers=headers)
        res = conn.getresponse()
        data = res.read()
        shlokasverse = json.loads(data.decode("utf-8"))["translations"][2]["description"]
        tqdm.write(f"Running AI script {chapter}.{x}")
        client = InferenceClient(
            "meta-llama/Meta-Llama-3-8B-Instruct",
            token=os.environ["HUGGING_FACE_TOKEN"],
        )
        result = []
        for message in client.chat_completion(
            messages=[{"role": "user", "content": f"""
I have a Shloka from the Bhagavad Gita. The shloka is Chapter {chapter}, Shloka {x}:

{shlokasverse}

This shloka is your only reference. DO NOT use other shlokas. Do not use your other sources or other shlokas unless your validating if the question makes sense.
Make a multiple choice question, with 4 answers based on this shloka and thats it. Provide the result in JSON format:

{{
"question": "<ENTER QUESTION HERE>",
"answeroptiona": "<ANSWER OPTION A>",
"answeroptionb": "<ANSWER OPTION B>",
"answeroptionc": "<ANSWER OPTION C>",
"answeroptiond": "<ANSWER OPTION D>",
"answer": "<A, B, C, D>"
}}

Make sure the answer is just one letter, A, B, C, or D.

Make sure your question makes sense, and remember the contents of the Bhagavad Gita and validate, "Is the answer I provided correct in the terms of the bhagavad gita?"
I should only see the JSON. The point is that the user should of read the shlokas in advance and now is tested on the shlokas. 
The user does not know which shloka the question is from, so it is a collection of multiple shlokas and it is a random shloka slected that this question is coming from, so the don't have a shloka with them. DO NOT REFERENCE THE SHLOKA OR ASK THEM TO.

Make sure that the correct answer is one letter, like A or C. Do not reference the shloka at all. Do NOT give "who said this" or "what happened in this shloka" questions or anything where the shloka needs to be in hand - the user is given a question relating to one of the 700 verses and they dont know which shloka or what the shloka is about. So you have to ask general knowledge questions, relating to the shloka. There is no SHLOKA, EXCEPT, OR PASSAGE of any sort avalible to the user.
            
Use previous and after shlokas to validate your answer. 

Remember, do not respond any other text other than the JSON. Make sure you complete the json in the exact format, with all keys and with both curly braces.
"""}],
            max_tokens=7000,
            stream=True,
            temperature=0
        ):
            result.append(message.choices[0].delta.content)

        # result of the ai response:
        tqdm.write("Converting AI response into JSON")
        result = ''.join(result)
        result = os.linesep.join(result.split(os.linesep)[:8])
        result = result.replace('shloka', 'shlokas')
        result = result.replace('verse', 'verses')
        result = result.replace('teaching', 'teachings')
        try:
            result = json.loads(result)
            result["answer"] = result["answer"].upper()
            fullresults.append(result)
        except json.decoder.JSONDecodeError as e:
            try:
                result = result + "\n}"
                result = json.loads(result)
                result["answer"] = result["answer"].upper()
                fullresults.append(result)
            except:
                tqdm.write("ERROR :( - Using backup AI JSON stripping")
                result1 = []
                client = InferenceClient(
                    "mistralai/Mixtral-8x7B-Instruct-v0.1",
                    token=os.environ["HUGGING_FACE_TOKEN"],
                )
                for message in client.chat_completion(
                    messages=[{"role": "user", "content": f"""
                I have this result from a previous AI Response (backticks indicate start and finish of AI response):
                
                `
                {result}
                `
                
                I am expecting just some json to be in there, but it contains some random words apart from the JSON, which is in this format:

                {{
                    "question": "<ENTER QUESTION HERE>",
                    "answeroptiona": "<ANSWER OPTION A>",
                    "answeroptionb": "<ANSWER OPTION B>",
                    "answeroptionc": "<ANSWER OPTION C>",
                    "answeroptiond": "<ANSWER OPTION D>",
                    "answer": "<EITHER A, B, C, D>"
                }}

                Fix all syntax errors, and remove all extra words. Add the proper extra braces as required. Do not respond any other data.
                """}],
                    max_tokens=7000,
                    stream=True,
                    temperature=0.2
                ):
                    result1.append(message.choices[0].delta.content)
                result = result1
                try:
                    result = json.loads(result)
                    result["answer"] = result["answer"].upper()
                    fullresults.append(result)
                except:
                    tqdm.write("FAILED TO GENERATE QUESTION")
                    fullresults.append({
                    "question": "AI: Failed to generate the question :(",
                    "answeroptiona": "Awww",
                    "answeroptionb": ":(",
                    "answeroptionc": "Oh well...",
                    "answeroptiond": "Come ON!!!",
                    "answer": "B"
                })


    return fullresults
