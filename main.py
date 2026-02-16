import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from perplexity import Perplexity
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_client():
    api_key = os.getenv("PERPLEXITY")
    if not api_key:
        raise HTTPException(status_code=500, detail="PERPLEXITY_API_KEY environment variable is missing")
    return Perplexity(api_key=api_key)  # Explicit for clarity [web:2]


class Visit(BaseModel):
    name:str
    age:int
    problem:str

print('backend is on!\n')

@app.post('/api')
async def consultation(visit:Visit):
    user_prompt = f"""this is visitor details, create a short summary for this
    patientName:{visit.name}
    patientage:{visit.age}
    patient_notes:{visit.problem}
    
    """

    system_prompt = """
    You are provided with notes written by a doctor from a patient's visit.
    Your job is to summarize the visit for the doctor and provide an email.
    Reply with exactly three sections with the headings:
    ### Summary of visit for the doctor's records
    ### Next steps for the doctor
    ### Draft of email to patient in patient-friendly language
    """

    try:
        client = get_client()
        query = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        completion = client.chat.completions.create(
            model="sonar",
            messages=query,
            max_tokens=100
        )
        reply = completion.choices[0].message.content
    
        return {
            "ai_response":reply
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API Error: {str(e)}")
    
print("backend is on!")
