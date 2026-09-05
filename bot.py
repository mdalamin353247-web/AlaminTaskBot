from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram.request import HTTPXRequest


# ==================================================
# BOT SETTINGS
# ==================================================

BOT_TOKEN = "8808769310:AAFO0EFkBSjAm8OXJnbyRSrUs-jHFwPvl9w"
ADMIN_ID = 7186496442


# ==================================================
# CONVERSATION STATES
# ==================================================

CATEGORY, TITLE, DESCRIPTION, REWARD, DEADLINE = range(5)


# ==================================================
# DATA
# ==================================================

tasks = []
submissions = []
users = {}


# ==================================================
# USER ACCOUNT
# ==================================================

def get_user(user_id, name):

    if user_id not in users:

        users[user_id] = {
            "name": name,
            "balance": 0,
            "total_earned": 0,
            "approved_tasks": 0
        }

    return users[user_id]


# ==================================================
# START
# ==================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    get_user(
        user.id,
        user.first_name
    )

    await update.message.reply_text(
        f"👋 স্বাগতম {user.first_name}!\n\n"
        "🤖 Alamin Task Center-এ আপনাকে স্বাগতম।\n\n"
        "📋 বিভিন্ন ধরনের কাজ এখানে পাওয়া যাবে।\n"
        "💰 কাজ সম্পন্ন করলে Reward পাওয়া যাবে।\n\n"
        "👉 কাজ দেখতে /jobs লিখুন।\n"
        "👉 Balance দেখতে /balance লিখুন।"
    )


# ==================================================
# BALANCE
# ==================================================

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    account = get_user(
        user.id,
        user.first_name
    )

    await update.message.reply_text(
        f"💰 তোমার Balance\n\n"
        f"💵 বর্তমান ব্যালেন্স: ৳{account['balance']}\n"
        f"🏆 মোট আয়: ৳{account['total_earned']}\n"
        f"✅ Approved Task: {account['approved_tasks']} টি"
    )


# ==================================================
# JOBS
# ==================================================

async def jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not tasks:

        await update.message.reply_text(
            "📋 বর্তমানে কোনো Task প্রকাশ করা হয়নি।"
        )

        return

    for i, task in enumerate(tasks):

        keyboard = [
            [
                InlineKeyboardButton(
                    "📤 Submit Task",
                    callback_data=f"submit_{i}"
                )
            ]
        ]

        text = (
            f"━━━━━━━━━━━━━━\n"
            f"🆔 Task #{i + 1}\n\n"
            f"📂 Category: {task['category']}\n"
            f"📝 Title: {task['title']}\n\n"
            f"📄 Description:\n"
            f"{task['description']}\n\n"
            f"💰 Reward: ৳{task['reward']}\n"
            f"⏰ Deadline: {task['deadline']}"
        )

        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


# ==================================================
# HELP
# ==================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🆘 Help\n\n"
        "/start - Bot শুরু করুন\n"
        "/jobs - Available Task দেখুন\n"
        "/balance - নিজের Balance দেখুন\n"
        "/help - সাহায্য\n"
        "/admin - Admin Panel"
    )


# ==================================================
# ADMIN PANEL
# ==================================================

async def admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:

        await update.message.reply_text(
            "❌ আপনার Admin Access নেই।"
        )

        return

    keyboard = [
        [
            InlineKeyboardButton(
                "➕ Create Task",
                callback_data="create_task"
            )
        ],
        [
            InlineKeyboardButton(
                "📋 All Tasks",
                callback_data="all_tasks"
            )
        ],
        [
            InlineKeyboardButton(
                "📥 Submissions",
                callback_data="submissions"
            )
        ],
    ]

    await update.message.reply_text(
        "👨‍💼 Admin Panel\n\n"
        "নিচের অপশন নির্বাচন করুন:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==================================================
# CREATE TASK START
# ==================================================

async def create_task_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if query.from_user.id != ADMIN_ID:

        await query.edit_message_text(
            "❌ আপনার Admin Access নেই।"
        )

        return ConversationHandler.END

    keyboard = [
        [
            InlineKeyboardButton(
                "📸 Photo",
                callback_data="cat_photo"
            ),
            InlineKeyboardButton(
                "🎥 Video",
                callback_data="cat_video"
            ),
        ],
        [
            InlineKeyboardButton(
                "🎨 Graphic",
                callback_data="cat_graphic"
            ),
            InlineKeyboardButton(
                "💼 Business Card",
                callback_data="cat_business"
            ),
        ],
        [
            InlineKeyboardButton(
                "👕 T-Shirt",
                callback_data="cat_tshirt"
            ),
            InlineKeyboardButton(
                "🛍️ Product",
                callback_data="cat_product"
            ),
        ],
        [
            InlineKeyboardButton(
                "📘 Facebook",
                callback_data="cat_facebook"
            ),
            InlineKeyboardButton(
                "📱 WhatsApp",
                callback_data="cat_whatsapp"
            ),
        ],
        [
            InlineKeyboardButton(
                "📸 Instagram",
                callback_data="cat_instagram"
            ),
            InlineKeyboardButton(
                "📝 Registration",
                callback_data="cat_registration"
            ),
        ],
    ]

    await query.edit_message_text(
        "📂 Task Category নির্বাচন করুন:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return CATEGORY


# ==================================================
# CATEGORY
# ==================================================

async def category_selected(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    categories = {

        "cat_photo": "📸 Photo",
        "cat_video": "🎥 Video",
        "cat_graphic": "🎨 Graphic Design",
        "cat_business": "💼 Business Card",
        "cat_tshirt": "👕 T-Shirt Design",
        "cat_product": "🛍️ Product Design",
        "cat_facebook": "📘 Facebook",
        "cat_whatsapp": "📱 WhatsApp",
        "cat_instagram": "📸 Instagram",
        "cat_registration": "📝 Account Registration",
    }

    category = categories.get(
        query.data
    )

    context.user_data["new_task"] = {
        "category": category
    }

    await query.edit_message_text(
        f"✅ Category: {category}\n\n"
        "📝 এখন Task-এর নাম লিখুন।"
    )

    return TITLE


# ==================================================
# TITLE
# ==================================================

async def task_title(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["new_task"]["title"] = (
        update.message.text
    )

    await update.message.reply_text(
        "📄 এখন Task-এর বিস্তারিত Description লিখুন।"
    )

    return DESCRIPTION


# ==================================================
# DESCRIPTION
# ==================================================

async def task_description(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["new_task"]["description"] = (
        update.message.text
    )

    await update.message.reply_text(
        "💰 এই Task-এর Reward কত টাকা?\n\n"
        "শুধু সংখ্যা লিখুন।\n"
        "উদাহরণ: 50"
    )

    return REWARD


# ==================================================
# REWARD
# ==================================================

async def task_reward(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    reward = update.message.text.strip()

    if not reward.isdigit():

        await update.message.reply_text(
            "❌ শুধু সংখ্যা লিখুন।\n\n"
            "উদাহরণ: 50"
        )

        return REWARD

    context.user_data["new_task"]["reward"] = int(
        reward
    )

    await update.message.reply_text(
        "⏰ Task-এর Deadline লিখুন।\n\n"
        "উদাহরণ:\n"
        "24 Hours\n"
        "3 Days\n"
        "7 Days"
    )

    return DEADLINE


# ==================================================
# DEADLINE
# ==================================================

async def task_deadline(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["new_task"]["deadline"] = (
        update.message.text
    )

    task = context.user_data["new_task"]

    tasks.append(task)

    await update.message.reply_text(
        "🎉 Task সফলভাবে Publish হয়েছে!\n\n"
        f"📂 Category: {task['category']}\n"
        f"📝 Title: {task['title']}\n"
        f"💰 Reward: ৳{task['reward']}\n"
        f"⏰ Deadline: {task['deadline']}"
    )

    context.user_data.pop(
        "new_task",
        None
    )

    return ConversationHandler.END


# ==================================================
# CANCEL
# ==================================================

async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.pop(
        "new_task",
        None
    )

    await update.message.reply_text(
        "❌ Task Creation বাতিল করা হয়েছে।"
    )

    return ConversationHandler.END


# ==================================================
# SUBMIT TASK
# ==================================================

async def submit_task(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    task_id = int(
        query.data.split("_")[1]
    )

    if task_id >= len(tasks):

        await query.edit_message_text(
            "❌ Task পাওয়া যায়নি।"
        )

        return

    task = tasks[task_id]

    context.user_data["submission_task"] = task_id

    await query.edit_message_text(
        f"📤 Submit Task\n\n"
        f"📝 {task['title']}\n\n"
        "এখন তোমার সম্পন্ন করা কাজের "
        "প্রমাণ/ফাইল পাঠাও।\n\n"
        "📸 Photo\n"
        "🎥 Video\n"
        "📄 Document\n"
        "অথবা প্রয়োজনীয় তথ্য পাঠাতে পারো।"
    )


# ==================================================
# RECEIVE SUBMISSION
# ==================================================

async def receive_submission(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if "submission_task" not in context.user_data:

        return

    task_id = context.user_data[
        "submission_task"
    ]

    if task_id >= len(tasks):

        await update.message.reply_text(
            "❌ এই Task আর পাওয়া যাচ্ছে না."
        )

        context.user_data.pop(
            "submission_task",
            None
        )

        return

    task = tasks[task_id]

    user = update.effective_user

    get_user(
        user.id,
        user.first_name
    )

    submission = {

        "task_id": task_id,
        "user_id": user.id,
        "user_name": user.full_name,
        "status": "Pending",
        "text": None,
        "file_type": None,
        "file_id": None,
        "reward_paid": False,
    }

    # TEXT

    if update.message.text:

        submission["text"] = (
            update.message.text
        )

    # PHOTO

    elif update.message.photo:

        submission["file_type"] = "photo"

        submission["file_id"] = (
            update.message.photo[-1].file_id
        )

    # VIDEO

    elif update.message.video:

        submission["file_type"] = "video"

        submission["file_id"] = (
            update.message.video.file_id
        )

    # DOCUMENT

    elif update.message.document:

        submission["file_type"] = "document"

        submission["file_id"] = (
            update.message.document.file_id
        )

    else:

        await update.message.reply_text(
            "❌ এই ধরনের ফাইল এখন গ্রহণ করা হচ্ছে না।"
        )

        return

    submissions.append(
        submission
    )

    submission_id = len(submissions) - 1

    await update.message.reply_text(
        "✅ তোমার Task Submission সফলভাবে জমা হয়েছে!\n\n"
        "⏳ Admin এখন এটি Review করবে।\n"
        "Admin Approve করলে Reward Balance-এ যোগ হবে।"
    )

    # ADMIN BUTTONS

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Approve",
                callback_data=f"approve_{submission_id}"
            ),
            InlineKeyboardButton(
                "❌ Reject",
                callback_data=f"reject_{submission_id}"
            ),
        ]
    ]

    admin_text = (

        "📥 নতুন Task Submission!\n\n"

        f"🆔 Submission #{submission_id + 1}\n"

        f"👤 User: {user.full_name}\n"

        f"🆔 User ID: {user.id}\n\n"

        f"📋 Task: {task['title']}\n"

        f"💰 Reward: ৳{task['reward']}\n\n"

        "⏳ Status: Pending"
    )

    await context.bot.send_message(

        chat_id=ADMIN_ID,

        text=admin_text,

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )

    # SEND PHOTO

    if submission["file_type"] == "photo":

        await context.bot.send_photo(

            chat_id=ADMIN_ID,

            photo=submission["file_id"],

            caption=f"📎 Submission #{submission_id + 1}"
        )

    # SEND VIDEO

    elif submission["file_type"] == "video":

        await context.bot.send_video(

            chat_id=ADMIN_ID,

            video=submission["file_id"],

            caption=f"📎 Submission #{submission_id + 1}"
        )

    # SEND DOCUMENT

    elif submission["file_type"] == "document":

        await context.bot.send_document(

            chat_id=ADMIN_ID,

            document=submission["file_id"],

            caption=f"📎 Submission #{submission_id + 1}"
        )

    # SEND TEXT

    elif submission["text"]:

        await context.bot.send_message(

            chat_id=ADMIN_ID,

            text=(
                f"📎 Submission #{submission_id + 1}\n\n"
                f"📝 User's Submission:\n"
                f"{submission['text']}"
            )
        )

    context.user_data.pop(
        "submission_task",
        None
    )


# ==================================================
# APPROVE / REJECT
# ==================================================

async def review_submission(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if query.from_user.id != ADMIN_ID:

        await query.answer(
            "❌ Admin only!",
            show_alert=True
        )

        return

    await query.answer()

    action, submission_id_text = (
        query.data.split("_")
    )

    submission_id = int(
        submission_id_text
    )

    if submission_id >= len(submissions):

        await query.edit_message_text(
            "❌ Submission পাওয়া যায়নি।"
        )

        return

    submission = submissions[
        submission_id
    ]

    # PREVENT DOUBLE PROCESSING

    if submission["status"] != "Pending":

        await query.edit_message_text(
            f"ℹ️ এই Submission ইতোমধ্যে "
            f"{submission['status']} হয়েছে।"
        )

        return

    task = tasks[
        submission["task_id"]
    ]

    # ==================================================
    # APPROVE
    # ==================================================

    if action == "approve":

        submission["status"] = "Approved"

        if not submission["reward_paid"]:

            account = get_user(
                submission["user_id"],
                submission["user_name"]
            )

            reward = task["reward"]

            account["balance"] += reward

            account["total_earned"] += reward

            account["approved_tasks"] += 1

            submission["reward_paid"] = True

        else:

            account = get_user(
                submission["user_id"],
                submission["user_name"]
            )

        await query.edit_message_text(

            f"✅ Submission Approved!\n\n"

            f"👤 User: {submission['user_name']}\n"

            f"📋 Task: {task['title']}\n"

            f"💰 Reward: ৳{task['reward']}\n"

            f"💵 User Balance: ৳{account['balance']}"
        )

        await context.bot.send_message(

            chat_id=submission["user_id"],

            text=(

                "🎉 তোমার Task Approved!\n\n"

                f"📋 Task: {task['title']}\n"

                f"💰 Reward: ৳{task['reward']}\n\n"

                "✅ Admin তোমার কাজ Approve করেছেন।\n"

                f"💵 বর্তমান Balance: ৳{account['balance']}\n"

                f"🏆 মোট আয়: ৳{account['total_earned']}"
            )
        )

    # ==================================================
    # REJECT
    # ==================================================

    elif action == "reject":

        submission["status"] = "Rejected"

        await query.edit_message_text(

            f"❌ Submission Rejected!\n\n"

            f"👤 User: {submission['user_name']}\n"

            f"📋 Task: {task['title']}"
        )

        await context.bot.send_message(

            chat_id=submission["user_id"],

            text=(

                "❌ তোমার Task Submission Reject হয়েছে।\n\n"

                f"📋 Task: {task['title']}\n\n"

                "প্রয়োজনে সঠিক কাজ/প্রমাণ আবার জমা দিতে পারো।"
            )
        )


# ==================================================
# ALL TASKS
# ==================================================

async def all_tasks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if query.from_user.id != ADMIN_ID:

        await query.edit_message_text(
            "❌ আপনার Admin Access নেই।"
        )

        return

    if not tasks:

        await query.edit_message_text(
            "📋 এখনো কোনো Task তৈরি করা হয়নি।"
        )

        return

    text = "📋 All Tasks\n\n"

    for i, task in enumerate(
        tasks,
        start=1
    ):

        text += (

            f"#{i}\n"

            f"📝 {task['title']}\n"

            f"📂 {task['category']}\n"

            f"💰 ৳{task['reward']}\n"

            f"⏰ {task['deadline']}\n\n"
        )

    await query.edit_message_text(
        text
    )


# ==================================================
# ALL SUBMISSIONS
# ==================================================

async def all_submissions(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if query.from_user.id != ADMIN_ID:

        await query.edit_message_text(
            "❌ আপনার Admin Access নেই।"
        )

        return

    if not submissions:

        await query.edit_message_text(
            "📥 এখনো কোনো Submission আসেনি।"
        )

        return

    text = "📥 All Submissions\n\n"

    for i, submission in enumerate(
        submissions,
        start=1
    ):

        task = tasks[
            submission["task_id"]
        ]

        text += (

            f"#{i}\n"

            f"👤 {submission['user_name']}\n"

            f"📋 {task['title']}\n"

            f"💰 ৳{task['reward']}\n"

            f"📌 Status: {submission['status']}\n\n"
        )

    await query.edit_message_text(
        text
    )


# ==================================================
# MAIN
# ==================================================

def main():

    # INCREASE TELEGRAM CONNECTION TIMEOUT

    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=60.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .request(request)
        .build()
    )

    # ==================================================
    # COMMANDS
    # ==================================================

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "jobs",
            jobs
        )
    )

    app.add_handler(
        CommandHandler(
            "balance",
            balance
        )
    )

    app.add_handler(
        CommandHandler(
            "help",
            help_command
        )
    )

    app.add_handler(
        CommandHandler(
            "admin",
            admin
        )
    )

    # ==================================================
    # CREATE TASK CONVERSATION
    # ==================================================

    task_conversation = ConversationHandler(

        entry_points=[

            CallbackQueryHandler(
                create_task_start,
                pattern="^create_task$"
            )
        ],

        states={

            CATEGORY: [

                CallbackQueryHandler(
                    category_selected,
                    pattern="^cat_"
                )
            ],

            TITLE: [

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    task_title
                )
            ],

            DESCRIPTION: [

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    task_description
                )
            ],

            REWARD: [

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    task_reward
                )
            ],

            DEADLINE: [

                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    task_deadline
                )
            ],
        },

        fallbacks=[

            CommandHandler(
                "cancel",
                cancel
            )
        ],

        allow_reentry=True,
    )

    app.add_handler(
        task_conversation
    )

    # ==================================================
    # ADMIN BUTTONS
    # ==================================================

    app.add_handler(

        CallbackQueryHandler(
            all_tasks,
            pattern="^all_tasks$"
        )
    )

    app.add_handler(

        CallbackQueryHandler(
            all_submissions,
            pattern="^submissions$"
        )
    )

    # ==================================================
    # USER SUBMIT
    # ==================================================

    app.add_handler(

        CallbackQueryHandler(
            submit_task,
            pattern="^submit_"
        )
    )

    # ==================================================
    # APPROVE / REJECT
    # ==================================================

    app.add_handler(

        CallbackQueryHandler(
            review_submission,
            pattern="^(approve|reject)_"
        )
    )

    # ==================================================
    # RECEIVE USER SUBMISSION
    # ==================================================

    app.add_handler(

        MessageHandler(

            filters.PHOTO
            |
            filters.VIDEO
            |
            filters.Document.ALL
            |
            (filters.TEXT & ~filters.COMMAND),

            receive_submission
        )
    )

    print(
        "🤖 Alamin Task Center চালু হয়েছে..."
    )

    app.run_polling()


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":

    main()