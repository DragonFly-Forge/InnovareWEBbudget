from datetime import datetime, date
import calendar
from db_connection import get_db_connection

def get_daily_spending_limit(user_id):
    conn = get_db_connection()
    if not conn:
        return "Database connection failed"
    
    cur = conn.cursor()
    try:
        today = date.today()
        # Get the total budget limit for the current month
        cur.execute("""
            SELECT monthly_limit FROM budgets 
            WHERE user_id = %s AND month_year = %s
        """, (user_id, today.replace(day=1)))
        budget_row = cur.fetchone()
        
        if not budget_row:
            return "No budget set for this month"
        
        monthly_budget = float(budget_row[0])

        # Get total income logged this month
        cur.execute("""
            SELECT SUM(amount) FROM transactions 
            WHERE user_id = %s AND type = 'income' 
            AND date >= %s
        """, (user_id, today.replace(day=1)))
        income_row = cur.fetchone()
        logged_income = float(income_row[0]) if income_row[0] else 0.0

        # FALLBACK LOGIC: If no income is logged, use monthly_budget as total_income
        total_income = monthly_budget + logged_income

        # Get total expenses logged this month
        cur.execute("""
            SELECT SUM(amount) FROM transactions 
            WHERE user_id = %s AND type = 'expense' 
            AND date >= %s
        """, (user_id, today.replace(day=1)))
        expense_row = cur.fetchone()
        total_spent = float(expense_row[0]) if expense_row[0] else 0.0

        # Calculate remaining budget and days
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        days_left = (days_in_month - today.day) + 1
        
        remaining_budget = monthly_budget - total_spent
        daily_limit = round(remaining_budget / days_left, 2) if days_left > 0 else 0

        return {
            "daily_limit": daily_limit,
            "days_left": days_left,
            "total_income": total_income,
            "total_spent": total_spent,
            "remaining_budget": remaining_budget
        }
    except Exception as e:
        return str(e)
    finally:
        cur.close()
        conn.close()