from openai import OpenAI
from logger_config import logger

def predict_delay_status(task_description, end_date, commit_summary, openai_api_key):
    prompt = f"""
You are a senior technical project manager and developer.

TASK DESCRIPTION:
{task_description}

EXPECTED END DATE: {end_date}

COMMIT SUMMARY (all commits made so far related to this task):
{commit_summary}

OBJECTIVE:
You must determine:
1. What percentage of the task is already complete
2. What is still remaining
3. Whether the task is on track or delayed
4. How long it would take to finish (in hours)

Respond in this format:
1. Status: 😎 On Track / 😩  Risk of Delay / 💀 Likely Delayed  
2. Reason: (brief explanation of what has been done vs what's pending)  
3. AI Evaluation Score: (0–100) — how confident you are in your judgment based on evidence  
4. AI Estimated Completion Time: X–Y hours — time it would take to complete the remaining work  
5. Completion: Z% complete ✅, R% remaining ⏳
"""

    try:
        client = OpenAI(api_key=openai_api_key)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI project reviewer evaluating software task progress based on commit summaries."
                        " Analyze the commits, understand what parts of the task are complete, and estimate what remains."
                        " Your completion percentage must reflect actual progress based on code-level summaries — not just assumptions."
                        "\n\n"
                        "Be honest and realistic. If only partial work is seen, say so clearly. Do not assume things are done unless the commits confirm it."
                        "\n\n"
                        "Provide completion as a percent. If nothing has been committed that touches core functionality, say 0–10%."
                        " If only UI is built but no logic or API, say 30–40%. If most of it is done, say 80–95%."
                        " Combine this with your best estimate of how many hours of work remain to finish it properly."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=400
        )

        content = response.choices[0].message.content
        return content.strip() if content else "⚠️ No response generated"

    except Exception as e:
        logger.error(f"AI prediction failed: {e}")
        return f"⚠️ Evaluation error: {e}"