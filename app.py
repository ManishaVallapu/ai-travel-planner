from flask import Flask, render_template, request
from google import genai
import os
import markdown
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    travel_plan_html = ""
    packing_html = ""
    tips_html = ""
    budget_data = {}

    if request.method == "POST":

        destination = request.form["destination"]
        days = request.form["days"]
        budget = int(request.form["budget"])

        hotel_budget = int(budget * 0.4)
        food_budget = int(budget * 0.3)
        transport_budget = int(budget * 0.2)
        activity_budget = int(budget * 0.1)

        # MAIN PROMPT
        prompt = f"""
Create a {days}-day travel plan for {destination} within total budget ₹{budget}.

Divide output into sections with headings:

Travel Plan:
Day-wise itinerary, hotels, food, activities.

Packing List:
Things user should carry.

Money Saving Tips:
Tips to reduce expenses.

Use headings and bullet points.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        full_text = response.text

        # Split sections
        travel_text = full_text
        packing_text = ""
        tips_text = ""

        if "Packing List:" in full_text:
            parts = full_text.split("Packing List:")
            travel_text = parts[0]
            remaining = parts[1]

            if "Money Saving Tips:" in remaining:
                subparts = remaining.split("Money Saving Tips:")
                packing_text = subparts[0]
                tips_text = subparts[1]
            else:
                packing_text = remaining

        # Convert markdown to HTML
        travel_plan_html = markdown.markdown(travel_text)
        packing_html = markdown.markdown(packing_text)
        tips_html = markdown.markdown(tips_text)

        budget_data = {
            "hotel": hotel_budget,
            "food": food_budget,
            "transport": transport_budget,
            "activity": activity_budget
        }

    return render_template(
        "index.html",
        travel_plan=travel_plan_html,
        packing=packing_html,
        tips=tips_html,
        budget=budget_data
    )


if __name__ == "__main__":
    app.run(debug=True)
