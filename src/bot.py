"""Telegram Bot with task management conversation."""
import logging
import uuid
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from src.config import config
from src.db import save_user_task, get_user_tasks

logger = logging.getLogger(__name__)

# Conversation states
(GOAL, DUE, REMINDER, CONFIRM) = range(4)


async def start_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the task creation conversation."""
    await update.message.reply_text(
        "好的，让我们创建一个新任务。\n\n请告诉我任务目标是什么？"
    )
    return GOAL


async def received_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle goal input, ask about due date."""
    goal = update.message.text.strip()
    context.user_data["goal"] = goal

    await update.message.reply_text(
        f"任务目标：{goal}\n\n需要设置截止日期吗？"
        "（例如：这周五、2026-03-15，或者直接回复'不需要'）"
    )
    return DUE


async def received_due(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle due date input, ask about reminder."""
    due = update.message.text.strip()

    # Check if user says no
    if due.lower() in ["不需要", "没有", "否", "no", "跳过"]:
        context.user_data["due"] = None
    else:
        context.user_data["due"] = due

    await update.message.reply_text(
        "收到。需要设置提醒吗？\n"
        "（例如：每天下午3点、每周一早上、或者'不需要'）"
    )
    return REMINDER


async def received_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle reminder input, show confirmation."""
    reminder = update.message.text.strip()

    # Check if user says no
    if reminder.lower() in ["不需要", "没有", "否", "no", "跳过"]:
        context.user_data["reminder"] = None
    else:
        context.user_data["reminder"] = reminder

    # Show summary and ask for confirmation
    goal = context.user_data.get("goal", "未设置")
    due = context.user_data.get("due", "未设置")
    rem = context.user_data.get("reminder", "未设置")

    summary = f"""请确认以下任务信息：

📌 目标：{goal}
📅 截止：{due}
🔔 提醒：{rem}

确认请回复"确认"，取消请回复"取消"或输入 /cancel"""

    await update.message.reply_text(summary)
    return CONFIRM


async def confirm_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Create the task and end conversation."""
    response = update.message.text.strip().lower()

    if response in ["确认", "yes", "y", "确定"]:
        task_id = str(uuid.uuid4())
        goal = context.user_data.get("goal")
        due = context.user_data.get("due")
        reminder = context.user_data.get("reminder")

        try:
            save_user_task(task_id, goal, due, reminder)
            await update.message.reply_text(
                f"✅ 任务已创建！\n\n"
                f"ID: {task_id}\n"
                f"目标: {goal}"
            )
        except Exception as e:
            logger.error(f"Failed to save task: {e}")
            await update.message.reply_text("❌ 保存失败，请重试。")

    else:
        await update.message.reply_text("已取消任务创建。")

    # Clear user data
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text("已取消当前操作。")
    context.user_data.clear()
    return ConversationHandler.END


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all user tasks."""
    try:
        tasks = get_user_tasks()
    except Exception as e:
        logger.error(f"Failed to get tasks: {e}")
        await update.message.reply_text("❌ 获取任务失败，请重试。")
        return

    if not tasks:
        await update.message.reply_text("暂无任务。")
        return

    lines = ["📋 你的任务：\n"]
    for task in tasks[:10]:  # Show max 10
        status_emoji = "⏳" if task.status == "pending" else "✅"
        due_info = f" (截止 {task.due})" if task.due else ""
        lines.append(f"{status_emoji} {task.goal}{due_info}")

    await update.message.reply_text("\n".join(lines))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help message."""
    help_text = """SignalDesk 命令：

/task - 创建新任务
/tasks - 查看所有任务
/help - 显示帮助
/cancel - 取消当前操作
"""
    await update.message.reply_text(help_text)


def run_bot() -> None:
    """Run the Telegram bot."""
    if not config.telegram_bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN not set, skipping bot startup")
        return

    application = Application.builder().token(config.telegram_bot_token).build()

    # Conversation handler for /task
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("task", start_task)],
        states={
            GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_goal)],
            DUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_due)],
            REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_reminder)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_task)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=600,  # 10 minutes
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("tasks", list_tasks))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel))

    logger.info("Starting Telegram bot...")
    application.run_polling()


if __name__ == "__main__":
    run_bot()
