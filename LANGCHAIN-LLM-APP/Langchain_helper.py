from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()

def generate_fitness_plan(age, gender, weight, height, fitness_goal, workout_days, workout_level, workout_type, diet_pref):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    
    prompt_template = PromptTemplate(
        input_variables=['age', 'gender', 'weight', 'height', 'fitness_goal', 'workout_days', 'workout_level', 'workout_type', 'diet_pref'],
        template=(
            "You are an expert fitness trainer and nutritionist. Create a comprehensive personalized fitness plan.\n"
            "User Details:\n"
            "- Age: {age}\n"
            "- Gender: {gender}\n"
            "- Weight: {weight} kg\n"
            "- Height: {height} cm\n"
            "- Fitness Goal: {fitness_goal}\n"
            "- Workout Days per Week: {workout_days}\n"
            "- Experience Level: {workout_level}\n"
            "- Workout Type Preference: {workout_type}\n"
            "- Diet Preference: {diet_pref}\n\n"
            
            "Please provide:\n"
            "1. **Weekly Workout Split Overview** - Brief summary of the training approach\n"
            "2. **Daily Calorie Requirements** - Calculate based on goals and activity level\n"
            "3. **Macronutrient Targets** - Protein, carbs, fats in grams per day\n"
            "4. **General Recommendations** - Key tips for success\n\n"
            
            "Format your response clearly with headers and bullet points."
        )
    )
    
    plan_chain = LLMChain(llm=llm, prompt=prompt_template)
    response = plan_chain.invoke({
        'age': age, 'gender': gender, 'weight': weight, 'height': height,
        'fitness_goal': fitness_goal, 'workout_days': workout_days,
        'workout_level': workout_level, 'workout_type': workout_type,
        'diet_pref': diet_pref
    })
    return response["text"]

def get_daily_workouts(workout_days, fitness_goal, workout_level, workout_type):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    
    prompt_template = PromptTemplate(
        input_variables=['workout_days', 'fitness_goal', 'workout_level', 'workout_type'],
        template=(
            "Create a day-by-day workout plan for 7 days of the week.\n"
            "Workout Days per Week: {workout_days}\n"
            "Fitness Goal: {fitness_goal}\n"
            "Experience Level: {workout_level}\n"
            "Workout Type: {workout_type}\n\n"
            
            "For each day (Monday through Sunday), provide either:\n"
            "- A specific workout plan with exercises, sets, and reps\n"
            "- 'Rest Day' for recovery days\n\n"
            
            "Format as:\n"
            "**Monday:** [workout details or Rest Day]\n"
            "**Tuesday:** [workout details or Rest Day]\n"
            "etc.\n\n"
            
            "Make sure to include exactly {workout_days} workout days and mark the rest as Rest Days."
        )
    )
    
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.invoke({
        'workout_days': workout_days,
        'fitness_goal': fitness_goal,
        'workout_level': workout_level,
        'workout_type': workout_type
    })
    
    # Parse the response into a dictionary
    lines = response["text"].split('\n')
    workout_dict = {}
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    current_day = None
    current_content = []
    
    for line in lines:
        line = line.strip()
        for day in days:
            if day in line and '**' in line:
                if current_day:
                    workout_dict[current_day] = '\n'.join(current_content).strip()
                current_day = day
                current_content = [line.replace('**', '').replace(f'{day}:', '').strip()]
                break
        else:
            if current_day and line:
                current_content.append(line)
    
    if current_day:
        workout_dict[current_day] = '\n'.join(current_content).strip()
    
    return workout_dict

def get_nutrition_plan(age, gender, weight, height, fitness_goal, diet_pref, daily_calories, country):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    
    # Calculate macro percentages based on fitness goal
    if fitness_goal in ["Build Muscle", "Weight Gain"]:
        protein_pct, carb_pct, fat_pct = 0.30, 0.40, 0.30
    elif fitness_goal == "Weight Loss":
        protein_pct, carb_pct, fat_pct = 0.35, 0.35, 0.30
    else:  # Maintain, Flexibility
        protein_pct, carb_pct, fat_pct = 0.25, 0.45, 0.30
    
    # Calculate macro grams
    protein_cals = daily_calories * protein_pct
    carb_cals = daily_calories * carb_pct
    fat_cals = daily_calories * fat_pct
    
    protein_grams = int(protein_cals / 4)
    carb_grams = int(carb_cals / 4)
    fat_grams = int(fat_cals / 9)
    fiber_grams = int(weight * 0.5)
    
    # Calculate meal distribution
    breakfast_cals = int(daily_calories * 0.25)
    lunch_cals = int(daily_calories * 0.30)
    snack_cals = int(daily_calories * 0.15)
    dinner_cals = daily_calories - breakfast_cals - lunch_cals - snack_cals
    
    # Calculate water intake
    water_intake = round(weight * 35 / 1000, 1)
    
    # Country-specific meal guidance
    country_guidance = {
        "India": "Focus on traditional Indian foods like dal, roti, rice, vegetables, paneer, chicken curry, idli, dosa, upma, poha, etc.",
        "United States": "Include American staples like oatmeal, grilled chicken, salads, quinoa bowls, protein smoothies, etc.",
        "United Kingdom": "Include British foods like porridge, beans on toast, fish and chips alternatives, roast dinner components, etc.",
        "Canada": "Include Canadian foods like maple syrup options, salmon, whole grain cereals, etc.",
        "Australia": "Include Australian foods like Vegemite toast, barramundi, kangaroo meat (if available), etc.",
        "South Africa": "Include South African foods like biltong, boerewors, pap, morogo, etc.",
        "Malaysia": "Include Malaysian foods like nasi lemak, rendang, laksa, roti canai alternatives, etc.",
        "Singapore": "Include Singaporean foods like chicken rice, laksa, kaya toast, etc.",
        "UAE": "Include Middle Eastern and international foods like hummus, grilled meats, Arabic rice dishes, etc.",
        "Other": "Use commonly available international foods with local adaptations."
    }
    
    meal_guidance = country_guidance.get(country, country_guidance["Other"])
    
    prompt_template = PromptTemplate(
        input_variables=['age', 'gender', 'weight', 'height', 'fitness_goal', 'diet_pref', 
                        'daily_calories', 'protein_grams', 'carb_grams', 'fat_grams', 'fiber_grams',
                        'breakfast_cals', 'lunch_cals', 'snack_cals', 'dinner_cals', 
                        'protein_cals', 'carb_cals', 'fat_cals', 'water_intake', 'country', 'meal_guidance'],
        template=(
            "Create a detailed nutrition plan as a fitness nutritionist.\n"
            "User: {age}yo {gender}, {weight}kg, {height}cm, Goal: {fitness_goal}, Diet: {diet_pref}\n"
            "Country: {country}\n"
            "Daily Calorie Target: {daily_calories} calories\n\n"
            
            "IMPORTANT: {meal_guidance}\n"
            "Make ALL meal suggestions using foods commonly available and popular in {country}.\n\n"
            
            "## Macronutrient Breakdown\n"
            "- **Protein:** {protein_grams}g ({protein_cals} calories)\n"
            "- **Carbohydrates:** {carb_grams}g ({carb_cals} calories)\n"
            "- **Fats:** {fat_grams}g ({fat_cals} calories)\n"
            "- **Fiber:** {fiber_grams}g\n\n"
            
            "## Sample Daily Meal Plan ({country} Cuisine)\n"
            "### 🌅 Breakfast ({breakfast_cals} calories)\n"
            "Provide 2-3 traditional {country} {diet_pref} breakfast options with specific local foods and portions\n\n"
            
            "### 🍽️ Lunch ({lunch_cals} calories)\n"
            "Provide 2-3 traditional {country} {diet_pref} lunch options with specific local foods and portions\n\n"
            
            "### 🥜 Snacks ({snack_cals} calories)\n"
            "Provide healthy {country} {diet_pref} snack options available locally\n\n"
            
            "### 🌙 Dinner ({dinner_cals} calories)\n"
            "Provide 2-3 traditional {country} {diet_pref} dinner options with specific local foods and portions\n\n"
            
            "## 💧 Hydration & Supplements\n"
            "- Water intake: minimum 35ml per kg body weight = {water_intake}L per day\n"
            "- Basic supplements available in {country} for {fitness_goal} goal\n\n"
            
            "Include cooking methods and ingredient preparations common in {country}.\n"
            "Use local ingredient names and measurements familiar to {country} residents."
        )
    )
    
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.invoke({
        'age': age, 'gender': gender, 'weight': weight, 'height': height,
        'fitness_goal': fitness_goal, 'diet_pref': diet_pref, 'daily_calories': daily_calories,
        'protein_grams': protein_grams, 'carb_grams': carb_grams, 'fat_grams': fat_grams,
        'fiber_grams': fiber_grams, 'breakfast_cals': breakfast_cals, 'lunch_cals': lunch_cals,
        'snack_cals': snack_cals, 'dinner_cals': dinner_cals,
        'protein_cals': int(protein_cals), 'carb_cals': int(carb_cals), 
        'fat_cals': int(fat_cals), 'water_intake': water_intake,
        'country': country, 'meal_guidance': meal_guidance
    })
    return response["text"]

def chat_with_nutritionist(user_message, diet_pref, daily_calories, chat_history):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    
    # Create context from chat history
    context = ""
    for msg in chat_history[-6:]:  # Last 3 exchanges
        context += f"{msg['role']}: {msg['content']}\n"
    
    prompt_template = PromptTemplate(
        input_variables=['user_message', 'diet_pref', 'daily_calories', 'context'],
        template=(
            "You are an expert nutritionist and recipe consultant. The user has a {diet_pref} diet preference "
            "and a daily calorie target of {daily_calories} calories.\n\n"
            "Previous conversation:\n{context}\n\n"
            "User question: {user_message}\n\n"
            "Provide helpful, accurate advice about:\n"
            "- Recipe modifications\n"
            "- Calorie counting\n"
            "- Meal planning\n"
            "- Ingredient substitutions\n"
            "- Cooking tips\n"
            "- Nutritional information\n\n"
            "Keep responses conversational, practical, and within their dietary preferences."
        )
    )
    
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.invoke({
        'user_message': user_message,
        'diet_pref': diet_pref,
        'daily_calories': daily_calories,
        'context': context
    })
    return response["text"]

def chat_nutrition_modification(user_message, current_plan, diet_pref, daily_calories, fitness_goal, chat_history, country):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    
    # Create context from recent chat
    context = ""
    for msg in chat_history[-4:]:
        context += f"{msg['role']}: {msg['content']}\n"
    
    prompt_template = PromptTemplate(
        input_variables=['user_message', 'current_plan', 'diet_pref', 'daily_calories', 'fitness_goal', 'context', 'country'],
        template=(
            "You are an expert nutritionist specializing in {country} cuisine and meal plan customization.\n\n"
            "User's Current Meal Plan:\n{current_plan}\n\n"
            "User Preferences:\n"
            "- Diet: {diet_pref}\n"
            "- Daily Calories: {daily_calories}\n"
            "- Fitness Goal: {fitness_goal}\n"
            "- Country: {country}\n\n"
            "Recent conversation:\n{context}\n\n"
            "User request: {user_message}\n\n"
            "Please help with meal modifications by:\n"
            "1. **Understanding the request** - What meal/ingredient they want to change\n"
            "2. **Providing alternatives** - Suggest 2-3 equivalent options using {country} foods\n"
            "3. **Maintaining macros** - Keep similar protein, carbs, fats, and calories\n"
            "4. **Using local ingredients** - Only suggest foods commonly available in {country}\n\n"
            "Format your response conversationally with specific suggestions using {country} foods and local names.\n\n"
            "Example for India:\n"
            "I can help you replace that! Here are 3 Indian alternatives with similar macros:\n\n"
            "🍛 **Option 1: Paneer Bhurji with Roti** (~400 calories)\n"
            "- 100g paneer bhurji, 2 whole wheat rotis\n"
            "- Protein: 25g | Carbs: 30g | Fat: 18g\n\n"
            "Would you like me to update your meal plan with one of these {country} options?"
        )
    )
    
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.invoke({
        'user_message': user_message,
        'current_plan': current_plan,
        'diet_pref': diet_pref,
        'daily_calories': daily_calories,
        'fitness_goal': fitness_goal,
        'context': context,
        'country': country
    })
    return response["text"]

def generate_updated_nutrition_plan(user_request, current_plan, user_data, daily_calories):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    
    prompt_template = PromptTemplate(
        input_variables=['user_request', 'current_plan', 'age', 'gender', 'weight', 'height', 'fitness_goal', 'diet_pref', 'daily_calories'],
        template=(
            "Update the nutrition plan based on the user's modification request.\n\n"
            "Original Plan:\n{current_plan}\n\n"
            "User Modification Request: {user_request}\n\n"
            "User Details:\n"
            "- Age: {age}, Gender: {gender}\n"
            "- Weight: {weight}kg, Height: {height}cm\n"
            "- Goal: {fitness_goal}\n"
            "- Diet: {diet_pref}\n"
            "- Daily Calories: {daily_calories}\n\n"
            "Generate a complete updated nutrition plan with the requested changes while maintaining:\n"
            "- Same total daily calories: {daily_calories}\n"
            "- Appropriate macro balance for {fitness_goal}\n"
            "- {diet_pref} dietary preferences\n\n"
            "Use the same format as the original plan:\n\n"
            "## Macronutrient Breakdown\n"
            "- Protein: X grams (X calories)\n"
            "- Carbohydrates: X grams (X calories)\n"
            "- Fats: X grams (X calories)\n"
            "- Fiber: X grams\n\n"
            
            "## Sample Daily Meal Plan\n"
            "### 🌅 Breakfast (X calories)\n"
            "- [updated meal if requested, otherwise keep original]\n\n"
            "### 🍽️ Lunch (X calories)\n"
            "- [updated meal if requested, otherwise keep original]\n\n"
            "### 🥜 Snacks (X calories)\n"
            "- [updated meal if requested, otherwise keep original]\n\n"
            "### 🌙 Dinner (X calories)\n"
            "- [updated meal if requested, otherwise keep original]\n\n"
            
            "## 💧 Hydration & Supplements\n"
            "- Water intake recommendations\n"
            "- Basic supplement suggestions (if any)\n"
        )
    )
    
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.invoke({
        'user_request': user_request,
        'current_plan': current_plan,
        'age': user_data['age'],
        'gender': user_data['gender'],
        'weight': user_data['weight'],
        'height': user_data['height'],
        'fitness_goal': user_data['fitness_goal'],
        'diet_pref': user_data['diet_pref'],
        'daily_calories': daily_calories
    })
    return response["text"]
