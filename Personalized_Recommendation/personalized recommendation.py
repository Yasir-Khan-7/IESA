import google.generativeai as genai
genai.configure(api_key="AIzaSyAUWQ8q6xyhRLd51aueJj0VH4C7emtWKic")

def get_ai_recommendations(predictions):
    prompt = f"""
    Analyze the following energy predictions and provide insights:
    {predictions}

    Now give me personalized recommendations based on the predictions above. 
    Keep the response concise (10 to 20 lines) and on point.
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    return response.text if response else "No response received."

# Example usage
predictions = "Increase in energy demand by 15% next quarter, renewable energy contribution expected to rise by 10%."
print(get_ai_recommendations(predictions))