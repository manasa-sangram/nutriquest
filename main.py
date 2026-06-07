from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.pagelayout import PageLayout
from kivy.core.window import Window
from api import analyse_grocery_list
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.clock import Clock
import os

print(" PROGRESSSSS JSON ____________________",os.path.abspath("progress.json"))

from api import analyse_grocery_list, get_meal_plan
from progress import (
    load_progress, save_progress,
    on_daily_goal_met, xp_for_next_level,
    save_grocery_entry,
    ALL_BADGES, LEVEL_TITLES, LEVEL_THRESHOLDS,
)
 


#FRONTEND


BG      = (0.96, 0.96, 0.94, 1)  # light grey background
PRIMARY = (0.11, 0.62, 0.46, 1)  # teal green
WHITE   = (1, 1, 1, 1)
DARK    = (0.10, 0.10, 0.10, 1)
MUTED   = (0.50, 0.50, 0.50, 1)

Window.clearcolor = BG


LEVEL_TITLES = {
    1: "Nutrition Newbie" ,
    2:"Calorie Counter",
    3:"Macro Master" , 
    4: "Health Hero",
    5:"Nutriquest Legend",
}

app_progress = load_progress()

# ------------------------------------GOALS SCREEN - Screen 1 


class GoalsScreen(Screen):
  def __init__(self , **kwargs):
     super().__init__(**kwargs)


     layout = BoxLayout(orientation="vertical", padding=24, spacing=14)

     layout.add_widget(Label(
            text="NutriQuest",
            font_size=28, bold=True,
            color=PRIMARY, size_hint_y=0.1
        ))

     layout.add_widget(Label(
            text="Set Your Daily Goals",
            font_size=16, color=MUTED,
            size_hint_y=0.08

        ))
     
     layout.add_widget(Label(text="Protein goal (g):", font_size=14, color=DARK, size_hint_y=0.07))
     self.protein_input = TextInput(text="50", font_size=15, multiline=False, size_hint_y=0.1)
     layout.add_widget(self.protein_input)

     layout.add_widget(Label(text="Carbs goal (g):", font_size=14, color=DARK, size_hint_y=0.07))
     self.carbs_input = TextInput(text="250", font_size=15, multiline=False, size_hint_y=0.1)
     layout.add_widget(self.carbs_input)

     layout.add_widget(Label(text="Fibre goal (g):", font_size=14, color=DARK, size_hint_y=0.07))
     self.fibre_input = TextInput(text="30", font_size=15, multiline=False, size_hint_y=0.1)
     layout.add_widget(self.fibre_input)

     btn = Button(
            text="Save Goals & Continue →",
            font_size=16, bold=True,
            background_color=PRIMARY,
            color=WHITE, size_hint_y=0.14)
     btn.bind(on_press=self.save_goals)
     layout.add_widget(btn)

     self.add_widget(layout)

  def save_goals(self, instance):
        self.manager.current = "input"

#--------------------------------Grocery Input - Screen 2


class InputScreen(Screen):
  def __init__(self , **kwargs):
    super().__init__(**kwargs) # runs Screen's own setup first
        # NOW you can safely add your own widgets
    
    layout  = BoxLayout(orientation ="vertical" , padding=24, spacing=14)

    l1 = Label(text='NutriQuest' , font_size=28,
            bold=True,
            color=PRIMARY,
            size_hint_y=0.12)
    
    l2=Label(text ="Level 1 — Nutrition Newbie",
            font_size=14,
            color=MUTED,
            size_hint_y=0.07
        )
    self.grocery_input = TextInput(
            hint_text="Type your grocery list here...\n\n2 apples\n1L oat milk\ngreek yogurt x2",
            font_size=15,
            padding=[12, 12],
            size_hint_y=0.55
        )
    
    btn = Button ( text ="Analyze Nutrition" ,font_size=16,
            bold=True,
            background_color=PRIMARY,
            color=WHITE,
            size_hint_y=0.14
        )
    btn.bind(on_press = self.go_to_results)

    back_btn = Button(text="<-- Back",
            font_size=15,
            background_color=PRIMARY,
            color=WHITE,
            size_hint_y=0.1
        )
    back_btn.bind(on_press=self.go_back)
    
    layout.add_widget(l1)
    layout.add_widget(l2)
    layout.add_widget(self.grocery_input)
    layout.add_widget(btn)
    layout.add_widget(back_btn)

    self.add_widget(layout)
  

  def go_to_results(self , instance):
      raw_text = self.grocery_input.text.strip()
      if not raw_text:
         return
      results , not_found = analyse_grocery_list(raw_text)
      results_screen = self.manager.get_screen("results")
      results_screen.show_results(results , not_found)
      self.manager.current = "results"
    
  def go_back(self, instance):
        self.manager.current = "goals"


#-----------------------------Nutrition Results - Screen 3

class ResultsScreen(Screen):
  def __init__(self , **kwargs):
    super().__init__(**kwargs)

    self.layout = BoxLayout(orientation="vertical", padding=24, spacing=14)
    
    self.title_label= Label(text ="Your Nutrition Results" , font_size=18, bold = True ,
              color =DARK , size_hint_y =0.1)
    
    self.scroll = ScrollView(size_hint_y = 0.8)
    self.results_grid = GridLayout(cols = 1 , spacing =10 , size_hint_y = None)
    self.results_grid.bind(minimum_height =self.results_grid.setter("height"))
    self.scroll.add_widget(self.results_grid)
    
    back_btn = Button(text="<- Back",
            font_size=15,
            background_color=PRIMARY,
            color=WHITE,
            size_hint_y=0.1
        )
    back_btn.bind(on_press=self.go_back)

    self.layout.add_widget(self.title_label)
    self.layout.add_widget(self.scroll)
    self.layout.add_widget(back_btn)
    self.add_widget(self.layout)

  def show_results(self, results, not_found):
        self.results_grid.clear_widgets()  # clear old results

        for item in results:
            text = (
                f"[b]{item['name'].title()}[/b]\n"
                f"Calories: {item['calories']} kcal  |  "
                f"Protein: {item['protein']}g  |  "
                f"Carbs: {item['carbs']}g  |  "
                f"Fat: {item['fat']}g"
            )
            lbl = Label(
                text=text,
                markup=True,
                font_size=14,
                color=DARK,
                size_hint_y=None,
                height=70,
                halign="left",
                valign="middle"
            )
            lbl.bind(size=lbl.setter("text_size"))
            self.results_grid.add_widget(lbl)

        if not_found:
            lbl = Label(
                text=f"[b]Not found:[/b] {', '.join(not_found)}",
                markup=True,
                font_size=13,
                color=MUTED,
                size_hint_y=None,
                height=50
            )
            self.results_grid.add_widget(lbl)

  def log_goal_hit(self, instance):
        """User taps the goal button — award XP, check badges, show feedback."""
        new_badges = on_daily_goal_met(app_progress, protein_met=True)
 
        lvl    = app_progress["level"]
        streak = app_progress["streak"]
        msg    = f"+50 XP  |  🔥 {streak}-day streak  |  Level {lvl}"
 
        if new_badges:
            names = [ALL_BADGES[b]["label"] for b in new_badges]
            msg += "\n🏅 New badge: " + ", ".join(names)
 
        self.feedback_label.text = msg
        self.goal_btn.disabled = True      # prevent double-logging
 
        # Refresh progress screen if it was already visited
        progress_screen = self.manager.get_screen("progress")
        progress_screen.refresh()
 
  def go_back(self, instance):
        self.manager.current = "input"
 
  def go_to_progress(self, instance):
        self.manager.get_screen("progress").refresh()
        self.manager.current = "progress"
 
  
  def go_back(self, instance):
        self.manager.current = "input"
   
  def go_to_progress(self, instance):
        self.manager.get_screen("progress").refresh()
        self.manager.current = "progress"

#-------------------Screen 4 Progress Hub

class ProgressScreen(Screen):
    def __init__(self , **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(orientation = "vertical" , padding = 24 , spacing =12)

        self.layout.add_widget(Label(text = "Progress Hub" , font_size= 22 , bold = True , color = PRIMARY , size_hint_y =0.1))


        #Level title - Level 1 : Newbie 
        self.level_label= Label(text = " " , font_size = 16 , bold = True , 
                                color = DARK , size_hint_y =0.08)
        self.layout.add_widget(self.level_label)


        #XP numbers ( 250 Xp)
        self.xp_label = Label(
            text = "" , font_size = 13 , 
            color = MUTED , size_hint_y = 0.07
        )
        self.layout.add_widget(self.xp_label)


        #XP Progress bar
        self.xp_bar = ProgressBar(max = 100 , value =0 , size_hint_y =0.06)
        self.layout.add_widget(self.xp_bar)

        #Streak
        self.streak_label = Label(
            text = "" , font_size= 14, 
            color = DARK , size_hint_y =0.08
        )
        self.layout.add_widget(self.streak_label)

        #Badges heading

        self.layout.add_widget(Label(
            text="Badges",
            font_size=15, bold=True,
            color=DARK, size_hint_y=0.07
        ))
 
        # Scrollable badge list
        scroll = ScrollView(size_hint_y=0.45)
        self.badge_grid = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.badge_grid.bind(minimum_height=self.badge_grid.setter("height"))
        scroll.add_widget(self.badge_grid)
        self.layout.add_widget(scroll)

        # Back button
        back_btn = Button(
            text="← Back to Input",
            font_size=15, background_color=PRIMARY,
            color=WHITE, size_hint_y=0.1
        )
        back_btn.bind(on_press=self.go_back)
        self.layout.add_widget(back_btn)

        #Level 3 Meal Plan
        self.meal_plan_btn = Button(
            text="🍽  Get AI Meal Plan  (Level 3 feature)",
            font_size=15, bold=True,
            background_color=PRIMARY,
            color=WHITE, size_hint_y=0.12,
            opacity=0,          # invisible
            disabled=True       # and untappable
        )
        self.meal_plan_btn.bind(on_press=self.go_to_meal_plan)
        self.layout.add_widget(self.meal_plan_btn)


# --- DEBUG ONLY:-------------------
        debug_btn = Button(
        text="[DEBUG] +50 XP",
        font_size=13,
        background_color=MUTED,
        color=WHITE, size_hint_y=0.08
        )
        debug_btn.bind(on_press=self.debug_add_xp)
        self.layout.add_widget(debug_btn)
        
 
        self.add_widget(self.layout)

    def debug_add_xp(self, instance):
        from progress import on_daily_goal_met
    # Temporarily pretend it's a different day so streak doesn't block it
        app_progress["last_log_date"] = None
        on_daily_goal_met(app_progress, protein_met=True)
        self.refresh()

    def refresh(self):
        """
        Pull the latest values from app_progress and update every widget.
        Call this whenever you navigate to this screen.
        """
        xp       = app_progress["xp"]
        level    = app_progress["level"]
        streak   = app_progress["streak"]
        badges   = app_progress["badges"]
        title    = LEVEL_TITLES.get(level, "")
 
        # --- Level label ---
        self.level_label.text = f"Level {level} — {title}"
 
        # --- XP bar ---
        next_threshold = None
        next_level     = level + 1
        if next_level in LEVEL_THRESHOLDS:
            current_threshold = LEVEL_THRESHOLDS[level]
            next_threshold    = LEVEL_THRESHOLDS[next_level]
            # XP within the current level band (0 → gap)
            gap       = next_threshold - current_threshold
            earned    = xp - current_threshold
            percent   = int((earned / gap) * 100)
            self.xp_bar.value = percent
            self.xp_label.text = (
                f"{xp} XP total  |  {earned} / {gap} XP to Level {next_level}"
            )
        else:
            # Max level reached
            self.xp_bar.value = 100
            self.xp_label.text = f"{xp} XP — Max level reached! 🎉"
 
        # --- Streak ---
        self.streak_label.text = f"🔥 Current streak: {streak} day(s)"
 
        # --- Badges ---
        self.badge_grid.clear_widgets()
        if not badges:
            self.badge_grid.add_widget(Label(
                text="No badges yet — log a goal to earn your first!",
                font_size=13, color=MUTED,
                size_hint_y=None, height=44
            ))
        else:
            for badge_id in badges:
                badge_info = ALL_BADGES.get(badge_id, {})
                label_text = (
                    f"[b]🏅 {badge_info.get('label', badge_id)}[/b]"
                    f"  —  {badge_info.get('desc', '')}"
                )
                lbl = Label(
                    text=label_text, markup=True,
                    font_size=13, color=DARK,
                    size_hint_y=None, height=44,
                    halign="left", valign="middle"
                )
                lbl.bind(size=lbl.setter("text_size"))
                self.badge_grid.add_widget(lbl)
 
        # Show the meal plan button only at level 3+
        if level >= 3:
            self.meal_plan_btn.opacity  = 1
            self.meal_plan_btn.disabled = False
        else:
            self.meal_plan_btn.opacity  = 0
            self.meal_plan_btn.disabled = True
 
    def go_to_meal_plan(self, instance):
        self.manager.get_screen("mealplan").load_plan()
        self.manager.current = "mealplan"
 
    def on_enter(self):
        """Kivy calls this automatically whenever the screen becomes active."""
        self.refresh()
 
    def go_back(self, instance):
        self.manager.current = "input"


#----------------Screen 5 Meal Plan Screen
 
class MealPlanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
 
        layout = BoxLayout(orientation="vertical", padding=24, spacing=12)
 
        layout.add_widget(Label(
            text="Your AI Meal Plan",
            font_size=22, bold=True,
            color=PRIMARY, size_hint_y=0.1
        ))
 
        # Status label — shows "Loading..." while the API call runs
        self.status_label = Label(
            text="Generating your plan...",
            font_size=13, color=MUTED,
            size_hint_y=0.07
        )
        layout.add_widget(self.status_label)
 
        # Scrollable area for the meal plan text
        scroll = ScrollView(size_hint_y=0.73)
        self.plan_label = Label(
            text="",
            font_size=14, color=DARK,
            size_hint_y=None,
            halign="left", valign="top",
            markup=False
        )
        # Let the label grow as tall as its text needs
        self.plan_label.bind(
            width=lambda *_: setattr(
                self.plan_label, "text_size",
                (self.plan_label.width, None)
            ),
            texture_size=lambda *_: setattr(
                self.plan_label, "height",
                self.plan_label.texture_size[1]
            )
        )
        scroll.add_widget(self.plan_label)
        layout.add_widget(scroll)
 
        back_btn = Button(
            text="← Back to Progress Hub",
            font_size=15, background_color=PRIMARY,
            color=WHITE, size_hint_y=0.1
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
 
        self.add_widget(layout)
 
    def load_plan(self):
        """
        Called just before the screen is shown.
        Reads grocery history + goals from app_progress,
        calls the OpenAI API, and displays the result.
        """
        self.plan_label.text  = ""
        self.status_label.text = "Talking to your nutrition coach... please wait ⏳"
 
        grocery_history = app_progress.get("grocery_history", [])
 
        # Read goals from the goals screen
        goals_screen = self.manager.get_screen("goals")
        goals = goals_screen.get_goals()
 
        try:
            plan = get_meal_plan(grocery_history, goals)
            self.plan_label.text   = plan
            self.status_label.text = "Here's your personalised plan 🍽"
        except Exception as e:
            self.plan_label.text   = f"Something went wrong:\n{e}"
            self.status_label.text = "Error — check your API key and connection"
 
    def go_back(self, instance):
        self.manager.current = "progress"







class NutriQuestApp(App):
  def build(self):

    sm = ScreenManager()
    sm.add_widget(GoalsScreen(name = "goals"))
    sm.add_widget(InputScreen(name ="input"))
    sm.add_widget(ResultsScreen(name="results"))
    sm.add_widget(ProgressScreen(name = "progress"))
    sm.add_widget(MealPlanScreen(name = "mealplan"))

    return sm

NutriQuestApp().run()



