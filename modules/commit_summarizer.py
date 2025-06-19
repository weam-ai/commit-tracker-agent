import openai
from logger_config import logger

def summarize_commit(diff_text, openai_api_key, task_name=""):
    """
    Summarize a Git commit diff using OpenAI's GPT model.
    
    Args:
        diff_text (str): The Git diff content.
        openai_api_key (str): OpenAI API key.
        task_name (str): Optional task name associated with the commit.
    
    Returns:
        str: Human-readable summary or error message.
    """
    try:
        openai.api_key = openai_api_key

        prompt = (
            f"You are an expert code reviewer. "
            f"Analyze the following Git commit diff and summarize what the developer has done.\n\n"
            f"Task: \"{task_name}\"\n\n"
            f"Diff:\n{diff_text}\n\n"
            "Provide a concise summary in 1-3 sentences."
        )

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a senior software engineer reviewing Git commits."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )

        content = response.choices[0].message.content
        return content.strip() if content else "⚠️ Empty response from OpenAI."

    except Exception as e:
        logger.error(f"❌ Error summarizing commit: {e}")
        logger.debug(traceback.format_exc())
        return f"Error summarizing commit: {e}"