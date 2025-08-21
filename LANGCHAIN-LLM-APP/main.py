import streamlit as st
import Langchain_helper as lch

st.set_page_config(page_title="FitVisor", page_icon="💪", layout="centered")

# ---------------- STATE ----------------
if "step" not in st.session_state:
    st.session_state.step = 1
if "plan" not in st.session_state:
    st.session_state.plan = None
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def next_step():
    st.session_state.step += 1

def prev_step():
    if st.session_state.step > 1:
        st.session_state.step -= 1

def calculate_bmr_bmi(weight, height, age, gender):
    # BMI calculation
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    
    # BMR calculation using Harris-Benedict equation
    if gender.lower() == "male":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    
    return round(bmi, 1), round(bmr, 0)

# ---------------- UI FLOW ----------------
st.title("🏋️ FitVisor - Your AI Fitness Coach")

# ---------------- STEP 1 ----------------
if st.session_state.step == 1:
    st.subheader("Step 1 of 3 - Personal Info")
    
    with st.form("step1_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=15, max_value=80, step=1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        height = st.number_input("Height (cm)", min_value=120, max_value=220)
        weight = st.number_input("Weight (kg)", min_value=30, max_value=200)
        
        # Country/Region selection
        country = st.selectbox("Country/Region", [
            "India", "United States", "United Kingdom", "Canada", 
            "Australia", "South Africa", "Malaysia", "Singapore",
            "UAE", "Other"
        ])
        
        submitted = st.form_submit_button("Next ➡️")
        if submitted and name and age and height and weight:
            st.session_state.user_data = {
                "name": name,
                "age": age,
                "gender": gender,
                "height": height,
                "weight": weight,
                "country": country
            }
            next_step()
            st.rerun()

# ---------------- STEP 2 ----------------
elif st.session_state.step == 2:
    st.subheader("Step 2 of 3 - Goals")
    
    with st.form("step2_form"):
        fitness_goal = st.radio("Fitness Goal", ["Weight Loss", "Weight Gain", "Build Muscle", "Improve Flexibility", "Maintain"])
        workout_level = st.radio("Workout Level", ["Beginner", "Intermediate", "Advanced"])
        workout_type = st.radio("Preferred Workout Type", ["Home", "Gym", "Yoga"])
        
        col1, col2 = st.columns(2)
        with col1:
            back_submitted = st.form_submit_button("⬅️ Back")
        with col2:
            next_submitted = st.form_submit_button("Next ➡️")
        
        if back_submitted:
            prev_step()
            st.rerun()
        elif next_submitted:
            st.session_state.user_data.update({
                "fitness_goal": fitness_goal,
                "workout_level": workout_level,
                "workout_type": workout_type
            })
            next_step()
            st.rerun()

# ---------------- STEP 3 ----------------
elif st.session_state.step == 3:
    st.subheader("Step 3 of 3 - Preferences")
    
    with st.form("step3_form"):
        workout_days = st.slider("Days per Week", 1, 7, 4)
        workout_time = st.radio("Preferred Workout Time", ["Morning", "Evening", "Anytime"])
        diet_pref = st.radio("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan"])
        food_allergy = st.text_area("Any Food Allergies?")
        terms = st.checkbox("I accept all the Terms and Conditions")
        privacy = st.checkbox("I accept the Privacy Policy")
        
        col1, col2 = st.columns(2)
        with col1:
            back_submitted = st.form_submit_button("⬅️ Back")
        with col2:
            continue_submitted = st.form_submit_button("✅ Continue")
        
        if back_submitted:
            prev_step()
            st.rerun()
        elif continue_submitted and terms and privacy:
            st.session_state.user_data.update({
                "workout_days": workout_days,
                "workout_time": workout_time,
                "diet_pref": diet_pref,
                "food_allergy": food_allergy
            })
            
            # Generate Plan
            with st.spinner("Generating your personalized fitness plan..."):
                user = st.session_state.user_data
                st.session_state.plan = lch.generate_fitness_plan(
                    user["age"], user["gender"], user["weight"], 
                    user["height"], user["fitness_goal"], user["workout_days"],
                    user["workout_level"], user["workout_type"], user["diet_pref"]
                )
            next_step()
            st.rerun()

# ---------------- FINAL DASHBOARD ----------------
elif st.session_state.step == 4:
    st.success(f"✅ Plan generated for **{st.session_state.user_data['name']}**")
    
    # Sidebar Navigation
    page = st.sidebar.radio("📂 Sections", ["Home", "Workouts", "Nutrition", "Recipe Chat", "Progress"])
    
    if page == "Home":
        st.header("📊 Today's Activity")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Calories Burned", "450 Cal")
            st.metric("Calories Intake", "1600 Cal")
        with col2:
            st.metric("Step Count", "5432 Steps")
            st.metric("Today's Workout", "Push Day")
        
        st.progress(5/7)
        st.info("Tomorrow's Workout: Pull Day")
    
    if page == "Workouts":
        st.header("🏋️ Weekly Workout Plan")
        st.write("Your personalized workout schedule:")
        
        # Get day-specific workouts
        user_data = st.session_state.user_data
        workout_plans = lch.get_daily_workouts(
            user_data["workout_days"], user_data["fitness_goal"], 
            user_data["workout_level"], user_data["workout_type"]
        )
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day in days:
            with st.expander(f"📅 {day}", expanded=False):
                day_plan = workout_plans.get(day, "Rest Day - Recovery and stretching")
                if "rest" in day_plan.lower():
                    st.info(f"🛌 **Rest Day** - Focus on recovery, light stretching, or a gentle walk")
                else:
                    st.markdown(day_plan)
    
    elif page == "Nutrition":
        st.header("🥗 Nutrition Plan")
        
        user_data = st.session_state.user_data
        bmi, bmr = calculate_bmr_bmi(
            user_data["weight"], user_data["height"], 
            user_data["age"], user_data["gender"]
        )
        
        # Calculate TDEE and weight loss calories with better clarity
        activity_multiplier = 1.6  # Moderate activity
        tdee = int(bmr * activity_multiplier)  # Total Daily Energy Expenditure
        
        if user_data["fitness_goal"] == "Weight Loss":
            daily_calories = tdee - 500  # Safe 500 cal deficit
            calculation_note = f"TDEE ({tdee}) - 500 deficit"
        elif user_data["fitness_goal"] == "Weight Gain":
            daily_calories = tdee + 500  # 500 cal surplus
            calculation_note = f"TDEE ({tdee}) + 500 surplus"
        elif user_data["fitness_goal"] == "Build Muscle":
            daily_calories = tdee + 200  # Slight surplus
            calculation_note = f"TDEE ({tdee}) + 200 surplus"
        else:
            daily_calories = tdee  # Maintenance
            calculation_note = f"TDEE ({tdee}) maintenance"
        
        # Display BMR, BMI and Calorie targets
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("BMI", f"{bmi}")
            if bmi < 18.5:
                st.info("Underweight")
            elif 18.5 <= bmi < 25:
                st.success("Normal weight")
            elif 25 <= bmi < 30:
                st.warning("Overweight")
            else:
                st.error("Obese")
        
        with col2:
            st.metric("BMR", f"{int(bmr)} cal/day")
            st.caption("Basal Metabolic Rate")
        
        with col3:
            st.metric("Daily Calorie Target", f"{daily_calories} cal")
            st.caption(calculation_note)
            if user_data["fitness_goal"] == "Weight Loss":
                st.info(f"⚠️ Never eat below BMR: {int(bmr)} calories")
        
        st.divider()
        
        # Initialize nutrition plan in session state
        if "nutrition_plan" not in st.session_state:
            with st.spinner("Generating your personalized nutrition plan..."):
                st.session_state.nutrition_plan = lch.get_nutrition_plan(
                    user_data["age"], user_data["gender"], user_data["weight"],
                    user_data["height"], user_data["fitness_goal"], user_data["diet_pref"],
                    daily_calories, user_data["country"]
                )
        
        # Display current nutrition plan
        st.subheader("📋 Your Personalized Meal Plan")
        st.markdown(st.session_state.nutrition_plan)
        
        st.divider()
        
        # Meal Customization Chatbot
        st.subheader("🤖 Meal Customization Assistant")
        st.write("Don't like a specific meal? Ask me to modify it while keeping the same macros!")
        
        # Initialize nutrition chat history
        if "nutrition_chat_history" not in st.session_state:
            st.session_state.nutrition_chat_history = []
            # Add welcome message
            welcome_msg = f"""Hi! I'm your meal customization assistant for **{user_data['country']}**. I can help you:

🔄 **Replace meals** - "Change the grilled chicken lunch to something local"
📊 **Adjust macros** - "Make the breakfast higher in protein"  
🥗 **Suggest alternatives** - "Give me traditional {user_data['country']} options for dinner"
📱 **Calculate calories** - "How many calories in 100g paneer?"

Your current targets: **{daily_calories} calories/day** | **{user_data['diet_pref']} diet** | **{user_data['country']} cuisine**

What would you like to modify in your meal plan?"""
            
            st.session_state.nutrition_chat_history.append({
                "role": "assistant", 
                "content": welcome_msg
            })
        
        # Display chat history
        for message in st.session_state.nutrition_chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Chat input for meal modifications
        user_message = st.chat_input("Ask me to modify meals, suggest alternatives, or adjust macros...")
        
        if user_message:
            st.session_state.nutrition_chat_history.append({"role": "user", "content": user_message})
            
            with st.chat_message("user"):
                st.write(user_message)
            
            # Get nutritionist response for meal modification
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    bot_response = lch.chat_nutrition_modification(
                        user_message, 
                        st.session_state.nutrition_plan,
                        user_data["diet_pref"], 
                        daily_calories,
                        user_data["fitness_goal"],
                        st.session_state.nutrition_chat_history,
                        user_data["country"]
                    )
                    st.write(bot_response)
            
            st.session_state.nutrition_chat_history.append({"role": "assistant", "content": bot_response})
            
            # If the response contains a new meal plan, update it
            if "## Updated Meal Plan" in bot_response or "**Updated" in bot_response:
                with st.spinner("Updating your meal plan..."):
                    # Generate updated plan
                    updated_plan = lch.generate_updated_nutrition_plan(
                        user_message, 
                        st.session_state.nutrition_plan,
                        user_data, 
                        daily_calories
                    )
                    if updated_plan:
                        st.session_state.nutrition_plan = updated_plan
                        st.success("✅ Meal plan updated! Refresh to see changes above.")
    
    elif page == "Recipe Chat":
        st.header("👨‍🍳 Recipe & Nutrition Chat")
        st.write("Ask me about recipes, meal modifications, or nutrition advice!")
        
        user_data = st.session_state.user_data
        
        # Calculate daily calories for recipe chat
        bmi, bmr = calculate_bmr_bmi(
            user_data["weight"], user_data["height"], 
            user_data["age"], user_data["gender"]
        )
        activity_multiplier = 1.6
        tdee = int(bmr * activity_multiplier)
        
        if user_data["fitness_goal"] == "Weight Loss":
            daily_calories = tdee - 500
        elif user_data["fitness_goal"] == "Weight Gain":
            daily_calories = tdee + 500
        elif user_data["fitness_goal"] == "Build Muscle":
            daily_calories = tdee + 200
        else:
            daily_calories = tdee
        
        # Display chat history first
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Chat input
        user_message = st.chat_input("Ask about recipes, calories, meal prep...")
        
        if user_message:
            st.session_state.chat_history.append({"role": "user", "content": user_message})
            
            with st.chat_message("user"):
                st.write(user_message)
            
            # Get chatbot response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    bot_response = lch.chat_with_nutritionist(
                        user_message, user_data["diet_pref"], 
                        daily_calories, st.session_state.chat_history
                    )
                    st.write(bot_response)
            
            st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
    
    elif page == "Progress":
        st.header("📈 Progress Tracking")
        st.metric("Calories Burned this week", "4250 Cal")
        st.metric("Steps Count this week", "57,252")
        st.line_chart([10, 30, 50, 20, 60, 80, 40])
        st.caption("Weekly activity trend")
