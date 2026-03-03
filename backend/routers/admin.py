from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from backend.database import query, execute
from backend.auth import decode_token, hash_password


router = APIRouter(prefix="/admin", tags=["Admin"])
bearer = HTTPBearer()


def get_admin(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        data = decode_token(creds.credentials)
        if data.get("role") != "admin":
            raise HTTPException(403, "Not an admin token")
        return data
    except Exception:
        raise HTTPException(401, "Invalid token")


@router.get("/overview")
def overview(_=Depends(get_admin)):
    stats = query("""
        SELECT
            COUNT(DISTINCT account_number)  AS total_customers,
            COUNT(DISTINCT branch)          AS total_branches,
            SUM(total_credits)              AS total_credits,
            SUM(total_debits)               AS total_debits,
            SUM(closing_balance)            AS total_deposits,
            SUM(total_transactions)         AS total_transactions,
            AVG(closing_balance)            AS avg_balance,
            MAX(closing_balance)            AS max_balance
        FROM accounts
    """, fetchone=True)
    pending = query(
        "SELECT COUNT(*) AS cnt FROM managers WHERE status = 'pending'",
        fetchone=True
    )
    approved = query(
        "SELECT COUNT(*) AS cnt FROM managers WHERE status = 'approved'",
        fetchone=True
    )
    blocked = query(
        "SELECT COUNT(*) AS cnt FROM managers WHERE status = 'blocked'",
        fetchone=True
    )
    return {
        **dict(stats),
        "pending_managers":  pending["cnt"],
        "approved_managers": approved["cnt"],
        "blocked_managers":  blocked["cnt"],
    }


@router.get("/branches")
def get_all_branches(_=Depends(get_admin)):
    rows = query("""
        SELECT DISTINCT branch FROM accounts
        WHERE branch IS NOT NULL AND branch != 'Unknown'
        ORDER BY branch
    """)
    return [r["branch"] for r in rows]


@router.get("/pending_managers")
def pending_managers(_=Depends(get_admin)):
    rows = query("""
        SELECT id, name, branch, created_at
        FROM managers
        WHERE status = 'pending'
        ORDER BY created_at DESC
    """)
    return [dict(r) for r in rows]


@router.post("/approve_manager/{manager_id}")
def approve_manager(manager_id: int, _=Depends(get_admin)):
    execute("UPDATE managers SET status = 'approved' WHERE id = %s", (manager_id,))
    return {"message": f"Manager {manager_id} approved"}


@router.post("/block_manager/{manager_id}")
def block_manager(manager_id: int, _=Depends(get_admin)):
    execute("UPDATE managers SET status = 'blocked' WHERE id = %s", (manager_id,))
    return {"message": f"Manager {manager_id} blocked"}


@router.get("/all_managers")
def all_managers(_=Depends(get_admin)):
    rows = query("""
        SELECT id, name, branch, status, created_at
        FROM managers
        ORDER BY created_at DESC
    """)
    return [dict(r) for r in rows]


@router.get("/all_customers")
def all_customers(
    limit: int = 200,
    offset: int = 0,
    search: Optional[str] = None,
    branch: Optional[str] = None,
    _=Depends(get_admin)
):
    filters = []
    params  = []
    if search:
        filters.append("(LOWER(account_holder) LIKE %s OR account_number LIKE %s)")
        params.extend([f"%{search.lower()}%", f"%{search}%"])
    if branch:
        filters.append("branch = %s")
        params.append(branch)
    where = "WHERE " + " AND ".join(filters) if filters else ""
    rows = query(f"""
        SELECT account_number, account_holder, account_type,
               branch, customer_id, closing_balance, total_transactions,
               total_credits, total_debits
        FROM accounts
        {where}
        ORDER BY closing_balance DESC
        LIMIT %s OFFSET %s
    """, params + [limit, offset])
    return [dict(r) for r in rows]


@router.get("/branch_performance")
def branch_performance(_=Depends(get_admin)):
    rows = query("""
        SELECT branch,
               COUNT(DISTINCT account_number)  AS customers,
               SUM(total_credits)              AS credits,
               SUM(total_debits)               AS debits,
               SUM(closing_balance)            AS deposits,
               AVG(closing_balance)            AS avg_balance,
               MAX(closing_balance)            AS max_balance,
               SUM(total_transactions)         AS total_transactions
        FROM accounts
        GROUP BY branch
        ORDER BY deposits DESC
    """)
    return [dict(r) for r in rows]


@router.get("/monthly_overview")
def monthly_overview(_=Depends(get_admin)):
    rows = query("""
        SELECT TO_CHAR(date, 'YYYY-MM')  AS month,
               SUM(debit)               AS debit,
               SUM(credit)              AS credit,
               COUNT(*)                 AS txn_count
        FROM transactions
        GROUP BY TO_CHAR(date, 'YYYY-MM')
        ORDER BY TO_CHAR(date, 'YYYY-MM')
    """)
    return [dict(r) for r in rows]


@router.get("/branch_compare")
def branch_compare(b1: str, b2: str, _=Depends(get_admin)):
    """Side-by-side analytics for two branches."""
    def branch_stats(branch_name):
        row = query("""
            SELECT
                COUNT(DISTINCT account_number)  AS customers,
                SUM(total_credits)              AS total_credits,
                SUM(total_debits)               AS total_debits,
                SUM(closing_balance)            AS total_deposits,
                AVG(closing_balance)            AS avg_balance,
                MAX(closing_balance)            AS max_balance,
                MIN(closing_balance)            AS min_balance,
                SUM(total_transactions)         AS total_transactions
            FROM accounts WHERE branch = %s
        """, (branch_name,), fetchone=True)
        cat_rows = query("""
            SELECT t.category, SUM(t.debit) AS total
            FROM transactions t
            JOIN accounts a ON t.account_number = a.account_number
            WHERE a.branch = %s AND t.transaction_type = 'DR'
            GROUP BY t.category ORDER BY total DESC LIMIT 5
        """, (branch_name,))
        monthly_rows = query("""
            SELECT TO_CHAR(t.date,'YYYY-MM') AS month,
                   SUM(t.credit) AS credit, SUM(t.debit) AS debit
            FROM transactions t
            JOIN accounts a ON t.account_number = a.account_number
            WHERE a.branch = %s
            GROUP BY TO_CHAR(t.date,'YYYY-MM') ORDER BY month
        """, (branch_name,))
        return {
            "stats": dict(row) if row else {},
            "top_categories": [dict(r) for r in cat_rows],
            "monthly": [dict(r) for r in monthly_rows],
        }

    return {
        "branch1": {"name": b1, **branch_stats(b1)},
        "branch2": {"name": b2, **branch_stats(b2)},
    }


@router.get("/customer/{account_number}")
def view_customer(account_number: str, _=Depends(get_admin)):
    """Admin views any customer's full profile."""
    acc = query("""
        SELECT account_number, account_holder, account_type,
               ifsc_code, branch, customer_id, currency,
               statement_period, opening_balance, total_credits,
               total_debits, closing_balance, total_transactions
        FROM accounts WHERE account_number = %s
    """, (account_number,), fetchone=True)
    if not acc:
        raise HTTPException(404, "Customer not found.")
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
    _=Depends(get_admin)
):
    filters = ["account_number = %s"]
    params  = [account_number]
    if category:
        filters.append("category = %s"); params.append(category)
    if txn_type:
        filters.append("transaction_type = %s"); params.append(txn_type.upper())
    if date_from:
        filters.append("date >= %s::date"); params.append(date_from)
    if date_to:
        filters.append("date <= %s::date"); params.append(date_to)
    where = " AND ".join(filters)
    rows = query(f"""
        SELECT id, date::text AS date, description, reference,
               transaction_type, debit, credit, balance,
               category, sub_category
        FROM transactions
        WHERE {where}
        ORDER BY date DESC, id DESC
        LIMIT %s OFFSET %s
    """, params + [limit, offset])
    return [dict(r) for r in rows]


@router.get("/customer/{account_number}/monthly")
def view_customer_monthly(account_number: str, _=Depends(get_admin)):
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
def view_customer_categories(account_number: str, _=Depends(get_admin)):
    rows = query("""
        SELECT category, sub_category, SUM(debit) AS total_spent, COUNT(*) AS txn_count
        FROM transactions WHERE account_number=%s AND transaction_type='DR'
        GROUP BY category, sub_category ORDER BY total_spent DESC
    """, (account_number,))
    return [dict(r) for r in rows]


@router.get("/global_category")
def global_category(_=Depends(get_admin)):
    rows = query("""
        SELECT category,
               SUM(debit)  AS total_debit,
               COUNT(*)    AS txn_count
        FROM transactions
        WHERE transaction_type = 'DR'
        GROUP BY category
        ORDER BY total_debit DESC
    """)
    return [dict(r) for r in rows]


@router.get("/top_customers")
def top_customers(limit: int = 20, _=Depends(get_admin)):
    rows = query("""
        SELECT account_number, account_holder, branch, account_type,
               closing_balance, total_transactions, total_credits, total_debits
        FROM accounts
        ORDER BY closing_balance DESC
        LIMIT %s
    """, (limit,))
    return [dict(r) for r in rows]
