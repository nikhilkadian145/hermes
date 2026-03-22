"""
Phase 16 -- Reminder + Cron Wakeup End-to-End Integration Test
Tests: cron tool configuration, briefing data assembly, reminder drafting.
"""
import tempfile
from datetime import date, timedelta
from pathlib import Path

import hermes.db as db


# ---------------------------------------------------------------------------
# Task 16.1 -- Morning briefing cron configuration
# ---------------------------------------------------------------------------

def test_phase16_cron_config():
    """Verify CronTool exists and can be referenced for daily 8 AM trigger."""
    # Import the CronTool to confirm it exists in the nanobot tools
    from nanobot.agent.tools.cron import CronTool

    # Verify the tool has the expected interface
    assert hasattr(CronTool, 'execute'), "CronTool must have an execute method"
    assert hasattr(CronTool, 'name') or hasattr(CronTool, 'tool_name'), "CronTool must have a name"

    # Verify the cron SKILL.md exists and describes cron_expr syntax
    cron_skill = Path(r"d:\HERMES\nanobot\skills\cron\SKILL.md")
    assert cron_skill.exists(), "cron SKILL.md must exist"
    content = cron_skill.read_text(encoding="utf-8")
    assert "cron_expr" in content, "cron skill must document cron_expr usage"
    assert "0 8 * * *" in content or "every day" in content.lower()

    print("  [OK] Task 16.1 - CronTool exists and cron SKILL.md properly configured")


# ---------------------------------------------------------------------------
# Task 16.2 -- Briefing data assembly and format
# ---------------------------------------------------------------------------

def test_phase16_briefing_data_assembly():
    """Assemble briefing data from DB and validate structure."""
    tmp = Path(tempfile.mkdtemp())
    db_path = str(tmp / "hermes.db")
    db.init_db(db_path)

    db.update_business(db_path, name="TestBiz", owner_name="Nikhil")
    business = db.get_business(db_path)

    # Create clients and invoices for various states
    raj_id = db.create_client(db_path, "Raj Traders", phone="9876543210")
    meena_id = db.create_client(db_path, "Meena Stores", phone="9988776655")
    kumar_id = db.create_client(db_path, "Kumar & Sons", phone="9112233445")

    yesterday = (date.today() - timedelta(days=1)).isoformat()
    five_days_ago = (date.today() - timedelta(days=5)).isoformat()
    today_str = date.today().isoformat()
    two_days_out = (date.today() + timedelta(days=2)).isoformat()

    # Overdue invoice (Meena, 5 days ago)
    inv1 = db.create_invoice(db_path, meena_id,
        items=[{"description": "Goods", "unit_price": 8500.0, "quantity": 1}],
        due_date=five_days_ago)
    db.update_invoice_status(db_path, inv1, "sent")

    # Due today (Kumar)
    inv2 = db.create_invoice(db_path, kumar_id,
        items=[{"description": "Services", "unit_price": 45000.0, "quantity": 1}],
        due_date=today_str)
    db.update_invoice_status(db_path, inv2, "sent")

    # Due in 2 days (Raj)
    inv3 = db.create_invoice(db_path, raj_id,
        items=[{"description": "Hosting", "unit_price": 7080.0, "quantity": 1}],
        due_date=two_days_out)
    db.update_invoice_status(db_path, inv3, "sent")

    # Yesterday's payment (Raj paid another earlier invoice)
    inv_paid = db.create_invoice(db_path, raj_id,
        items=[{"description": "Design", "unit_price": 21240.0, "quantity": 1}],
        due_date=yesterday)
    db.record_payment(db_path, inv_paid, 21240.0, mode="upi",
        payment_date=yesterday, reference="UPI-PAY-001")

    # Log an expense
    db.log_expense(db_path, today_str, "Office rent", "rent", 15000.0)

    # --- Now assemble the briefing data exactly as the agent would ---

    # 1. MTD summary
    mtd = db.get_mtd_summary(db_path)
    assert "mtd_revenue" in mtd
    assert "mtd_expenses" in mtd
    assert "overdue_count" in mtd
    assert mtd["overdue_count"] >= 1

    # 2. Overdue invoices
    overdue = db.get_overdue_invoices(db_path)
    assert len(overdue) >= 1
    overdue_names = [o["client_name"] for o in overdue]
    assert "Meena Stores" in overdue_names

    # 3. Due soon invoices
    due_soon = db.get_due_soon_invoices(db_path, days=3)
    assert len(due_soon) >= 1  # Kumar (today) + Raj (2 days out)

    # 4. Build briefing text (simulating what the LLM would compose)
    lines = []
    lines.append(f"Good Morning! -- {date.today().strftime('%d %b %Y')}")
    lines.append("")

    # MTD section
    lines.append("THIS MONTH SO FAR")
    lines.append(f"  Income received: {mtd['mtd_revenue']}")
    lines.append(f"  Expenses: {mtd['mtd_expenses']}")
    lines.append(f"  Net Profit: {mtd['mtd_net']}")
    lines.append("")

    # Overdue section
    lines.append(f"OVERDUE ({len(overdue)} invoices)")
    for o in overdue:
        lines.append(f"  {o['client_name']}, {o['invoice_number']} -- {o['total']}")
    lines.append("")

    # Due soon
    lines.append(f"NEXT 3 DAYS ({len(due_soon)} invoices)")
    for d in due_soon:
        lines.append(f"  {d['client_name']}, {d['invoice_number']} -- {d['total']}")

    briefing_text = "\n".join(lines)

    # Validate structure
    assert "Good Morning" in briefing_text
    assert "THIS MONTH SO FAR" in briefing_text
    assert "OVERDUE" in briefing_text
    assert "Meena Stores" in briefing_text
    assert "NEXT 3 DAYS" in briefing_text

    # Verify briefing-morning SKILL.md is in place
    skill_path = Path(r"d:\HERMES\workspace\skills\briefing-morning\SKILL.md")
    assert skill_path.exists()
    skill_content = skill_path.read_text(encoding="utf-8")
    assert "Good Morning" in skill_content
    assert "OVERDUE" in skill_content or "ACTION NEEDED" in skill_content

    print("  [OK] Task 16.2 - Briefing data assembled and format validated")


# ---------------------------------------------------------------------------
# Task 16.3 -- Manual reminder drafting
# ---------------------------------------------------------------------------

def test_phase16_reminder_drafting():
    """Fetch outstanding for a client, draft reminder, log it."""
    tmp = Path(tempfile.mkdtemp())
    db_path = str(tmp / "hermes.db")
    db.init_db(db_path)

    db.update_business(db_path, name="TestBiz")
    raj_id = db.create_client(db_path, "Raj", phone="9876543210")

    # Create an overdue invoice
    overdue_date = (date.today() - timedelta(days=10)).isoformat()
    inv_id = db.create_invoice(db_path, raj_id,
        items=[{"description": "Consulting", "unit_price": 21240.0, "quantity": 1}],
        due_date=overdue_date)
    db.update_invoice_status(db_path, inv_id, "sent")

    # Step 1: Agent fetches outstanding for Raj
    clients = db.find_client(db_path, "Raj")
    assert len(clients) >= 1
    client = clients[0]

    outstanding = db.get_outstanding_balance(db_path, client_id=client["id"])
    assert outstanding == 21240.0

    unpaid = db.list_invoices(db_path, status="sent", client_id=client["id"])
    assert len(unpaid) == 1
    inv = unpaid[0]

    # Step 2: Draft a reminder message (simulating what LLM would compose)
    days_overdue = (date.today() - date.fromisoformat(inv["due_date"])).days

    if days_overdue <= 7:
        tone = "friendly"
    elif days_overdue <= 20:
        tone = "firm"
    else:
        tone = "formal"

    reminder_text = (
        f"Namaste {client['name']} ji!\n\n"
        f"Invoice {inv['invoice_number']} ke baare mein yaad dilana tha.\n"
        f"Amount: {inv['total']}\n"
        f"Due Date: {inv['due_date']}\n"
        f"({days_overdue} din overdue)\n\n"
        f"Dhanyawad!"
    )

    assert tone == "firm"  # 10 days overdue should be "firm"
    assert client["name"] in reminder_text
    assert str(inv["total"]) in reminder_text

    # Step 3: Log the reminder
    reminder_id = db.log_reminder(db_path, inv_id, client["id"], reminder_text)
    assert reminder_id is not None

    # Verify reminder logged
    reminders = db.get_reminders_for_invoice(db_path, inv_id)
    assert len(reminders) == 1
    assert "Namaste" in reminders[0]["message_text"]

    # Verify reminder-draft SKILL.md is in place
    skill_path = Path(r"d:\HERMES\workspace\skills\reminder-draft\SKILL.md")
    assert skill_path.exists()
    skill_content = skill_path.read_text(encoding="utf-8")
    assert "Friendly" in skill_content
    assert "Firm" in skill_content
    assert "Formal" in skill_content

    print("  [OK] Task 16.3 - Reminder drafted with tone escalation and logged")


if __name__ == "__main__":
    test_phase16_cron_config()
    test_phase16_briefing_data_assembly()
    test_phase16_reminder_drafting()
    print("\n[PASS] Phase 16 - All Reminder + Cron Wakeup E2E tests passed!")
