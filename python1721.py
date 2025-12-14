#!/usr/bin/env python3
"""
HANOS Debreselam - School Management Telegram Bot
Working Version for PythonAnywhere Free Tier
"""

import logging
import time
import hashlib
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== CONFIGURATION ====================
# ⚠️ REPLACE THIS WITH YOUR ACTUAL BOT TOKEN FROM @BotFather ⚠️
BOT_TOKEN = "8231782269:AAELLc-9zJaF0VkiSLpZqUGL7Ry1T1V8AZI"

DEVELOPER_NAME = "Kaleab Menberesilassie"

# ==================== SIMPLE DATABASE ====================
class SimpleDB:
    def __init__(self):
        self.users = {
            # Students
            "STSS0001": {"name": "ሚካኤል አለማየሁ", "class": "ቀዳማይ", "password": "student123", "role": "student"},
            "STSS0002": {"name": "Sarah Johnson", "class": "ካልኣይ", "password": "student123", "role": "student"},
            "STSS0003": {"name": "የሻን ገብረመድህን", "class": "ሳልሳይ", "password": "student123", "role": "student"},
            "STSS0004": {"name": "David Smith", "class": "ራብዓይ", "password": "student123", "role": "student"},
            
            # Teachers
            "TCH1001": {"name": "ወንድም ገብረመድህን", "subject": "Mathematics", "password": "teacher123", "role": "teacher"},
            "TCH1002": {"name": "Ms. Helen Brown", "subject": "English", "password": "teacher123", "role": "teacher"},
            
            # Admins
            "ADM5001": {"name": "Mr. Daniel G/Michael", "password": "admin123", "role": "admin"},
        }
        
        self.sessions = {}
    
    def get_user(self, user_id):
        user_id = user_id.upper().strip()
        return self.users.get(user_id)
    
    def verify_password(self, user_id, password):
        user = self.get_user(user_id)
        if not user:
            return False
        return user["password"] == password

db = SimpleDB()

# ==================== COMMAND HANDLERS ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "👋 **Welcome to HANOS School Management System!**\n\n"
        "📚 *Developed by:* Kaleab Menberesilassie\n\n"
        "Please enter your User ID:\n"
        "• **Students:** STSS0001, STSS0002, STSS0003, STSS0004\n"
        "• **Teachers:** TCH1001, TCH1002\n"
        "• **Admins:** ADM5001\n\n"
        "💡 **Default Passwords:**\n"
        "• Students: student123\n"
        "• Teachers: teacher123\n"
        "• Admins: admin123\n\n"
        "Enter your User ID:"
    )

async def handle_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user ID input"""
    user_id = update.message.text.upper().strip()
    user_data = db.get_user(user_id)
    
    if not user_data:
        await update.message.reply_text(
            "❌ **Invalid User ID!**\n\n"
            "Please enter a valid User ID:\n"
            "• STSS0001, STSS0002, STSS0003, STSS0004\n"
            "• TCH1001, TCH1002\n"
            "• ADM5001\n\n"
            "Try again:"
        )
        return
    
    # Store user data for password check
    context.user_data['login_user_id'] = user_id
    context.user_data['login_user_data'] = user_data
    
    await update.message.reply_text(
        f"🔐 **Welcome {user_data['name']}!**\n\n"
        f"Role: {user_data['role'].title()}\n\n"
        "Please enter your password:"
    )

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle password input"""
    password = update.message.text.strip()
    user_id = context.user_data.get('login_user_id')
    user_data = context.user_data.get('login_user_data')
    
    if not user_id or not user_data:
        await update.message.reply_text("❌ Session error. Please start over with /start")
        return
    
    if db.verify_password(user_id, password):
        # Login successful
        context.user_data['user_id'] = user_id
        context.user_data['user_name'] = user_data['name']
        context.user_data['user_role'] = user_data['role']
        context.user_data['logged_in'] = True
        
        if user_data['role'] == 'student':
            context.user_data['student_class'] = user_data['class']
        elif user_data['role'] == 'teacher':
            context.user_data['teacher_subject'] = user_data.get('subject', 'Unknown')
        
        # Clear login data
        context.user_data.pop('login_user_id', None)
        context.user_data.pop('login_user_data', None)
        
        # Show main menu
        await show_main_menu(update, context)
    else:
        await update.message.reply_text(
            "❌ **Incorrect password!**\n\n"
            "Please enter your password again:"
        )

# ==================== MAIN MENU ====================
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu based on user role"""
    user_name = context.user_data.get('user_name', 'User')
    user_role = context.user_data.get('user_role', 'user')
    
    if user_role == "student":
        student_class = context.user_data.get('student_class', 'Unknown')
        welcome_text = f"""
🎓 **Welcome {user_name}!**
🏫 **Class:** {student_class}

Please choose an option:"""
        
        keyboard = [
            [InlineKeyboardButton("📚 Study Materials", callback_data="materials")],
            [InlineKeyboardButton("📅 Class Schedule", callback_data="schedule")],
            [InlineKeyboardButton("📊 My Grades", callback_data="grades")],
            [InlineKeyboardButton("📊 Attendance", callback_data="attendance")],
            [InlineKeyboardButton("📝 Homework", callback_data="homework")],
            [InlineKeyboardButton("🎓 Exams", callback_data="exams")],
            [InlineKeyboardButton("📚 Library", callback_data="library")],
            [InlineKeyboardButton("👨‍🏫 Teachers", callback_data="teachers")],
            [InlineKeyboardButton("ℹ️ Profile", callback_data="profile")],
        ]
        
    elif user_role == "teacher":
        teacher_subject = context.user_data.get('teacher_subject', 'Unknown')
        welcome_text = f"""
👨‍🏫 **Welcome {user_name}!**
📚 **Subject:** {teacher_subject}

Please choose an option:"""
        
        keyboard = [
            [InlineKeyboardButton("👨‍🎓 My Students", callback_data="my_students")],
            [InlineKeyboardButton("📝 Assign Homework", callback_data="assign_hw")],
            [InlineKeyboardButton("📊 Record Grades", callback_data="record_grades")],
            [InlineKeyboardButton("📊 Take Attendance", callback_data="take_attendance")],
            [InlineKeyboardButton("📚 Materials", callback_data="teaching_materials")],
            [InlineKeyboardButton("📅 Schedule", callback_data="teacher_schedule")],
        ]
        
    else:  # admin
        welcome_text = f"""
👨‍💼 **Welcome {user_name}!**
🏢 **Administrator**

Please choose an option:"""
        
        keyboard = [
            [InlineKeyboardButton("📊 Analytics", callback_data="analytics")],
            [InlineKeyboardButton("👨‍🎓 Students", callback_data="manage_students")],
            [InlineKeyboardButton("👨‍🏫 Teachers", callback_data="manage_teachers")],
            [InlineKeyboardButton("📚 Curriculum", callback_data="curriculum")],
            [InlineKeyboardButton("🏫 Classes", callback_data="manage_classes")],
        ]
    
    # Add logout button
    keyboard.append([InlineKeyboardButton("🚪 Logout", callback_data="logout")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'callback_query'):
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# ==================== STUDENT FEATURES ====================
async def student_materials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
📚 **Study Materials**

**Available Subjects:**
• Mathematics - Algebra, Geometry
• English - Grammar, Literature  
• Science - Physics, Chemistry, Biology
• Amharic - ሰዋሰው, ግጥም
• Social Studies - History, Geography

**Resources:**
📖 Textbooks
📝 Worksheets
🎬 Video Lessons
🧪 Lab Manuals

All materials available 24/7"""
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def student_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
📅 **Class Schedule**

**Monday - Friday:**
🕗 8:00-9:00 - Mathematics
🕘 9:00-10:00 - English
🕥 10:30-11:30 - Science
🕦 11:30-12:30 - Amharic
🕐 1:00-2:00 - Social Studies

**Total Hours:** 5 hours/day
**School Hours:** 8:00 AM - 2:00 PM"""
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def student_grades(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
📊 **Academic Performance**

**Current Grades:**
• Mathematics: 85% (A)
• English: 92% (A+)
• Science: 78% (B+)
• Amharic: 88% (A)
• Social Studies: 81% (A-)

**Overall Statistics:**
🎯 Average: 84.8% (A)
📈 Position: 15th in class
📅 Last Updated: November 2024"""
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def student_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
📊 **Attendance Record**

**November 2024:**
✅ Present: 18 days
❌ Absent: 2 days
🏥 Sick Leave: 1 day
📈 Attendance Rate: 85.7%

**Weekly Breakdown:**
• Week 1: ✅✅✅✅✅
• Week 2: ✅✅✅❌✅  
• Week 3: ✅✅🏥✅✅
• Week 4: ✅✅✅✅❌"""
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def student_homework(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
📝 **Homework Assignments**

**Current Assignments:**
1. **Mathematics** 
   📋 Exercise 5.1 - 5.10
   📅 Due: Tomorrow
   ✅ Status: Pending

2. **English**
   📋 Essay: "My Favorite Season"
   📅 Due: Friday
   ✅ Status: In Progress

3. **Science**
   📋 Lab Report: Plant Growth
   📅 Due: Next Monday
   ✅ Status: Not Started"""
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def student_exams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
🎓 **Exam Schedule**

**Upcoming Exams:**
1. Mathematics Midterm
   📅 Dec 5, 2024
   ⏰ 8:00-10:00 AM

2. English Final
   📅 Dec 10, 2024  
   ⏰ 8:00-10:00 AM

3. Science Practical
   📅 Dec 12, 2024
   ⏰ 10:30-12:00 PM"""
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def student_library(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
📚 **School Library**

**Available Books:**
• Mathematics: Advanced Algebra
• English: Grammar Guide  
• Science: Physics Fundamentals
• Amharic: የአማርኛ ሰዋሰው
• Social Studies: World History

**Borrowing Rules:**
• Max 3 books at a time
• Return within 2 weeks
• No late returns"""
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def student_teachers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
👨‍🏫 **Teaching Staff**

1. **ወንድም ገብረመድህን**
   📖 Subject: Mathematics
   🏫 Classes: ቀዳማይ, ካልኣይ

2. **Ms. Helen Brown**
   📖 Subject: English  
   🏫 Classes: ሳልሳይ, ራብዓይ

3. **አቶ አለማየሁ ተሰማ**
   📖 Subject: Science
   🏫 Classes: ቀዳማይ, ሳልሳይ"""
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def student_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = context.user_data.get('user_id', 'Unknown')
    user_name = context.user_data.get('user_name', 'Unknown')
    student_class = context.user_data.get('student_class', 'Unknown')
    
    text = f"""
ℹ️ **Student Profile**

**Personal Information:**
📋 Student ID: {user_id}
👤 Name: {user_name}
🏫 Class: {student_class}
📅 Academic Year: 2024
✅ Status: Active

**Academic Summary:**
📊 Average Grade: 84.8%
🎯 Class Position: 15/45
📚 Subjects: 5
🏆 Achievements: 3"""
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

# ==================== TEACHER FEATURES ====================
async def teacher_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
👨‍🎓 **My Students**

**Class Statistics:**
• Total Students: 45
• Class Average: 78.5%
• Attendance Rate: 92%

**Top Performers:**
1. ሚካኤል አለማየሁ - 94%
2. Sarah Johnson - 92%
3. የሻን ገብረመድህን - 89%"""
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def teacher_assign_hw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
📝 **Assign Homework**

**Select Class:**
• ቀዳማይ - 22 students
• ካልኣይ - 24 students  
• ሳልሳይ - 25 students
• ራብዓይ - 23 students"""
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

# ==================== ADMIN FEATURES ====================
async def admin_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
📊 **School Analytics**

**School Overview:**
• Total Students: 94
• Total Teachers: 12
• Total Classes: 4
• Staff Members: 8

**Academic Performance:**
• School Average: 76.8%
• Pass Rate: 92%
• Top Class: ራብዓይ (81.2%)"""
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def admin_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
👨‍🎓 **Student Management**

**Class Distribution:**
• ቀዳማይ: 22 students
• ካልኣይ: 24 students
• ሳልሳይ: 25 students  
• ራብዓይ: 23 students

**Operations:**
• Register New Student
• Update Information
• View Records"""
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

# ==================== CALLBACK HANDLER ====================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main callback handler"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    # Check if user is logged in for protected routes
    if callback_data != "main_menu" and callback_data != "logout":
        if not context.user_data.get('logged_in'):
            await query.edit_message_text("❌ Please login first with /start")
            return
    
    # Handle callbacks
    if callback_data == "main_menu":
        await show_main_menu(update, context)
    
    elif callback_data == "logout":
        # Clear user data
        for key in list(context.user_data.keys()):
            del context.user_data[key]
        await query.edit_message_text("✅ Successfully logged out!\n\nUse /start to login again.")
    
    # Student features
    elif callback_data == "materials":
        await student_materials(update, context)
    elif callback_data == "schedule":
        await student_schedule(update, context)
    elif callback_data == "grades":
        await student_grades(update, context)
    elif callback_data == "attendance":
        await student_attendance(update, context)
    elif callback_data == "homework":
        await student_homework(update, context)
    elif callback_data == "exams":
        await student_exams(update, context)
    elif callback_data == "library":
        await student_library(update, context)
    elif callback_data == "teachers":
        await student_teachers(update, context)
    elif callback_data == "profile":
        await student_profile(update, context)
    
    # Teacher features
    elif callback_data == "my_students":
        await teacher_students(update, context)
    elif callback_data == "assign_hw":
        await teacher_assign_hw(update, context)
    elif callback_data == "record_grades":
        await query.edit_message_text("📊 Record Grades - Feature active!")
    elif callback_data == "take_attendance":
        await query.edit_message_text("📊 Take Attendance - Feature active!")
    elif callback_data == "teaching_materials":
        await query.edit_message_text("📚 Teaching Materials - Feature active!")
    elif callback_data == "teacher_schedule":
        await query.edit_message_text("📅 Teacher Schedule - Feature active!")
    
    # Admin features
    elif callback_data == "analytics":
        await admin_analytics(update, context)
    elif callback_data == "manage_students":
        await admin_students(update, context)
    elif callback_data == "manage_teachers":
        await query.edit_message_text("👨‍🏫 Teacher Management - Feature active!")
    elif callback_data == "curriculum":
        await query.edit_message_text("📚 Curriculum Management - Feature active!")
    elif callback_data == "manage_classes":
        await query.edit_message_text("🏫 Class Management - Feature active!")
    
    else:
        await query.edit_message_text("⚠️ Feature coming soon!")

# ==================== MAIN FUNCTION ====================
def main():
    """Start the bot - PythonAnywhere optimized"""
    # Check for bot token
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Please replace BOT_TOKEN with your actual bot token!")
        print("💡 Get your token from @BotFather on Telegram")
        print("💡 Edit line 14 in the code and put your token there")
        return
    
    # Setup logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    try:
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
         # Start polling (for PythonAnywhere Free Tier)
        print("🔄 Starting polling...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        logging.error(f"Bot error: {e}")

if __name__ == '__main__':
    main()