import streamlit as st
import openai


api_key = st.secrets["key"]["key"]

st.set_page_config(page_title="Fitness Plan Generator", page_icon="🏋️", layout="centered")

# Initialize session variables
if "stage" not in st.session_state:
    st.session_state.stage = 'input'
if "workout" not in st.session_state:
    st.session_state.workout = ""
if "meal_plan" not in st.session_state:
    st.session_state.meal_plan = ""


# ChatGPT call
def ask_chatgpt(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": question}]
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print("An error occurred:", e)
        return None

# Parse ChatGPT response
def parse_response(response):
    workout_start = "Workout Plan:"
    meal_start = "Meal Plan:"
    
    if workout_start in response and meal_start in response:
        workout = response.split(workout_start)[1].split(meal_start)[0].strip()
        meal_plan = response.split(meal_start)[1].strip()
        return workout, meal_plan
    return "", ""

# Generate question for ChatGPT
def ask_question(user_data):
    user_question = f"""
    Hi, my name is {user_data['name']}, I am {user_data['age']} years old, my weight is {user_data['weight']}kg, my height is {user_data['height']}cm. 
    I plan to work out {user_data['gym_access']} {user_data['days']} a week. My goal is to {user_data['goal']}. and these are suggestions to my work out- {user_data['suggestions']} 
    Can you make me a personalized workout program and meal plan? 
    Please provide a workout plan and a meal plan with 3 meals a day, with 5 options to choose from. 
    Do not include any tips or extra information, only the workout plan and meal plan.
    Return the workout and meal plans clearly labeled, like this:
        Workout Plan:
        [Workout details]
        Meal Plan:
        [Meal plan details]
    """
    response = ask_chatgpt(user_question)
    if response:
        return parse_response(response)
    return "", ""

# Input Form (Only show if no plan generated)
if st.session_state.stage == 'input':
    st.title("🏋️ Fitness Plan Generator")
    st.subheader("Enter your details:")

    with st.form("user_input_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0, max_value=120, step=1, format="%d", value=None)
        height = st.number_input("Height (cm)", min_value=0, max_value=300, step=1, format="%d", value=None)
        weight = st.number_input("Weight (kg)", min_value=0, max_value=500, step=1, format="%d", value=None)
        days = st.slider("How many days per week do you train?", 1, 7)
        gym_access = st.selectbox("Do you have access to a gym?", ["Yes", "No"])
        suggestions = st.text_area("Additional suggestions or goals (optional)")
        goal = st.selectbox("What is your goal?", ["Gain muscle", "Lose weight", "Gain muscle and Lose weight"])

        submitted = st.form_submit_button("Generate Plan")

        if submitted:
            user_data = {
                "name": name,
                "age": age,
                "height": height,
                "weight": weight,
                "days": days,
                "gym_access": gym_access,
                "suggestions": suggestions,
                "goal": goal
            }

            with st.spinner("Please wait while we create your personalized plan..."):
                workout, meal_plan = ask_question(user_data)
                st.session_state.workout = workout
                st.session_state.meal_plan = meal_plan
                st.session_state.stage = 'output'  # Update stage to output

                # Only trigger rerun if both plans are valid
                if workout and meal_plan:
                    print(f"Workout: {workout}")
                    print(f"Meal Plan: {meal_plan}")
                    st.rerun()

# Output Screen
if st.session_state.stage == 'output':
    st.title("✅ Your Personalized Plan")
    st.subheader("Workout Plan")
    st.write(st.session_state.workout)

    st.subheader("Meal Plan")
    st.write(st.session_state.meal_plan)

    if st.button("🔁 Start Over"):
        
        st.session_state.stage = 'input'  
        st.session_state.workout = ""
        st.session_state.meal_plan = ""
        st.session_state.name = ""
        st.session_state.age = None
        st.session_state.height = None
        st.session_state.weight = None
        st.session_state.days = None
        st.session_state.gym_access = ""
        st.session_state.suggestions = ""
        st.session_state.goal = ""
        st.rerun()