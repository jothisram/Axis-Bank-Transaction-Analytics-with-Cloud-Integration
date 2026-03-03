from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from backend.database import query
from backend.auth import decode_token

router  = APIRouter(prefix="/management", tags=["Management"])
bearer  = HTTPBearer()

def get_mgmt(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        data = decode_token(creds.credentials)
        if data.get("role") != "management":
            raise HTTPException(403, "Not a management token")
        return data
    except Exception:
        raise HTTPException(401, "Invalid token")


@router.get("/branches")
def get_all_branches():
    """Public endpoint — returns all branch names for autocomplete in registration."""
    rows = query("""
        SELECT DISTINCT branch FROM accounts
        WHERE branch IS NOT NULL AND branch != 'Unknown'
        ORDER BY branch
    """)
    return [r["branch"] for r in rows]


@router.get("/branch_summary")
def branch_summary(user=Depends(get_mgmt)):
    branch = user["branch"]
    row = query("""
        SELECT
            COUNT(DISTINCT account_number)  AS total_customers,
            SUM(total_credits)              AS total_credits,
            SUM(total_debits)               AS total_debits,
            SUM(closing_balance)            AS total_deposits,
            AVG(closing_balance)            AS avg_balance,
            SUM(total_transactions)         AS total_transactions,
            MAX(closing_balance)            AS max_balance,
            MIN(closing_balance)            AS min_balance
        FROM accounts
        WHERE branch = %s
    """, (branch,), fetchone=True)
    return dict(row) if row else {}


@router.get("/customers")
def customers(limit: int = 500, offset: int = 0, search: Optional[str] = None, user=Depends(get_mgmt)):
    filters = ["branch = %s"]
    params  = [user["branch"]]
    if search:
        filters.append("(LOWER(account_holder) LIKE %s OR account_number LIKE %s)")
        params.extend([f"%{search.lower()}%", f"%{search}%"])
    where = " AND ".join(filters)
    rows = query(f"""
        SELECT account_number, account_holder, account_type,
               customer_id, closing_balance, total_transactions,
               total_credits, total_debits, opening_balance
        FROM accounts
        WHERE {where}
        ORDER BY closing_balance DESC
        LIMIT %s OFFSET %s
    """, params + [limit, offset])
    return [dict(r) for r in rows]


@router.get("/customers/count")
def customers_count(user=Depends(get_mgmt)):
    row = query("SELECT COUNT(*) AS cnt FROM accounts WHERE branch = %s",
                (user["branch"],), fetchone=True)
    return {"count": row["cnt"] if row else 0}


@router.get("/monthly_activity")
def monthly_activity(user=Depends(get_mgmt)):
    rows = query("""
        SELECT TO_CHAR(t.date,'YYYY-MM') AS month,
               SUM(t.debit)  AS debit,
               SUM(t.credit) AS credit,
               COUNT(*)      AS txn_count
        FROM transactions t
        JOIN accounts a ON t.account_number = a.account_number
        WHERE a.branch = %s
        GROUP BY TO_CHAR(t.date,'YYYY-MM')
        ORDER BY month
    """, (user["branch"],))
    return [dict(r) for r in rows]


@router.get("/category_breakdown")
def category_breakdown(user=Depends(get_mgmt)):
    rows = query("""
        SELECT t.category,
               t.sub_category,
               SUM(t.debit)  AS total,
               COUNT(*)      AS count
        FROM transactions t
        JOIN accounts a ON t.account_number = a.account_number
        WHERE a.branch = %s AND t.transaction_type = 'DR'
        GROUP BY t.category, t.sub_category
        ORDER BY total DESC
    """, (user["branch"],))
    return [dict(r) for r in rows]


@router.get("/top_customers")
def top_customers(user=Depends(get_mgmt)):
    rows = query("""
        SELECT account_number, account_holder,
               total_credits, total_debits, closing_balance,
               total_transactions
        FROM accounts
        WHERE branch = %s
        ORDER BY closing_balance DESC
        LIMIT 15
    """, (user["branch"],))
    return [dict(r) for r in rows]


@router.get("/account_type_distribution")
def account_type_distribution(user=Depends(get_mgmt)):
    rows = query("""
        SELECT account_type,
               COUNT(*) AS count,
               SUM(closing_balance) AS total_balance,
               AVG(closing_balance) AS avg_balance
        FROM accounts
        WHERE branch = %s
        GROUP BY account_type
        ORDER BY count DESC
    """, (user["branch"],))
    return [dict(r) for r in rows]


@router.get("/cashflow_trend")
def cashflow_trend(user=Depends(get_mgmt)):
    rows = query("""
        SELECT TO_CHAR(t.date, 'YYYY-MM') AS month,
               SUM(t.credit) - SUM(t.debit) AS net_flow
        FROM transactions t
        JOIN accounts a ON t.account_number = a.account_number
        WHERE a.branch = %s
        GROUP BY TO_CHAR(t.date, 'YYYY-MM')
        ORDER BY month
    """, (user["branch"],))
    return [dict(r) for r in rows]


@router.get("/customer/{account_number}")
def view_customer(account_number: str, user=Depends(get_mgmt)):
    """Manager views full customer detail — only their branch customers."""
    # Verify customer belongs to manager's branch
    acc = query("""
        SELECT account_number, account_holder, account_type,
               ifsc_code, branch, customer_id, currency,
               statement_period, opening_balance, total_credits,
               total_debits, closing_balance, total_transactions
        FROM accounts
        WHERE account_number = %s AND branch = %s
    """, (account_number, user["branch"]), fetchone=True)
    if not acc:
        raise HTTPException(404, "Customer not found in your branch.")
    return dict(acc)


@router.get("/customer/{account_number}/transactions")
def view_customer_transactions(
    account_number: str,
    limit: int = 100,
    offset: int = 0,
    category: Optional[str] = None,
    txn_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    user=Depends(get_mgmt)
):
    """Manager views transactions for a customer in their branch."""
    # Verify branch ownership
    acc = query("SELECT account_number FROM accounts WHERE account_number=%s AND branch=%s",
                (account_number, user["branch"]), fetchone=True)
    if not acc:
        raise HTTPException(403, "Customer is not in your branch.")

    filters = ["t.account_number = %s"]
    params  = [account_number]
    if category:
        filters.append("t.category = %s"); params.append(category)
    if txn_type:
        filters.append("t.transaction_type = %s"); params.append(txn_type.upper())
    if date_from:
        filters.append("t.date >= %s::date"); params.append(date_from)
    if date_to:
        filters.append("t.date <= %s::date"); params.append(date_to)
    where = " AND ".join(filters)
    rows = query(f"""
        SELECT t.id, t.date::text AS date, t.description, t.reference,
               t.transaction_type, t.debit, t.credit, t.balance,
               t.category, t.sub_category
        FROM transactions t
        WHERE {where}
        ORDER BY t.date DESC, t.id DESC
        LIMIT %s OFFSET %s
    """, params + [limit, offset])
    return [dict(r) for r in rows]


@router.get("/customer/{account_number}/monthly")
def view_customer_monthly(account_number: str, user=Depends(get_mgmt)):
    acc = query("SELECT account_number FROM accounts WHERE account_number=%s AND branch=%s",
                (account_number, user["branch"]), fetchone=True)
    if not acc:
        raise HTTPException(403, "Customer is not in your branch.")
    rows = query("""
        SELECT TO_CHAR(date,'YYYY-MM') AS month,
               SUM(debit)             AS total_debit,
               SUM(credit)            AS total_credit,
               COUNT(*)               AS txn_count
        FROM transactions WHERE account_number=%s
        GROUP BY TO_CHAR(date,'YYYY-MM') ORDER BY month
    """, (account_number,))
    return [dict(r) for r in rows]


@router.get("/customer/{account_number}/categories")
def view_customer_categories(account_number: str, user=Depends(get_mgmt)):
    acc = query("SELECT account_number FROM accounts WHERE account_number=%s AND branch=%s",
                (account_number, user["branch"]), fetchone=True)
    if not acc:
        raise HTTPException(403, "Customer is not in your branch.")
    rows = query("""
        SELECT category, sub_category, SUM(debit) AS total_spent, COUNT(*) AS txn_count
        FROM transactions WHERE account_number=%s AND transaction_type='DR'
        GROUP BY category, sub_category ORDER BY total_spent DESC
    """, (account_number,))
    return [dict(r) for r in rows]