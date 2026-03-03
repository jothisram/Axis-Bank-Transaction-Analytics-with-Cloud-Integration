from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from backend.database import query
from backend.auth import decode_token


router = APIRouter(prefix="/customer", tags=["Customer"])
bearer = HTTPBearer()


def get_customer(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        data = decode_token(creds.credentials)
        if data.get("role") != "customer":
            raise HTTPException(403, "Not a customer token")
        return data
    except Exception:
        raise HTTPException(401, "Invalid token")


@router.get("/profile")
def profile(user=Depends(get_customer)):
    acc = query(
        """SELECT account_number, account_holder, account_type,
                  ifsc_code, branch, customer_id, currency,
                  statement_period, opening_balance, total_credits,
                  total_debits, closing_balance, total_transactions
           FROM accounts
           WHERE account_number = %s""",
        (user["account_number"],), fetchone=True
    )
    if not acc:
        raise HTTPException(404, "Account not found")
    return dict(acc)


@router.get("/categories")
def get_categories(user=Depends(get_customer)):
    """Returns {category: [sub_categories]} for cascading filter."""
    rows = query("""
        SELECT DISTINCT category, sub_category
        FROM transactions
        WHERE account_number = %s
        ORDER BY category, sub_category
    """, (user["account_number"],))
    cat_map = {}
    for r in rows:
        cat = r["category"]
        sub = r["sub_category"]
        if cat not in cat_map:
            cat_map[cat] = []
        if sub and sub not in cat_map[cat]:
            cat_map[cat].append(sub)
    return cat_map


@router.get("/transactions")
def transactions(
    limit: int = 100,
    offset: int = 0,
    category: Optional[str] = None,
    sub_category: Optional[str] = None,
    txn_type: Optional[str] = None,   # DR or CR
    date_from: Optional[str] = None,  # YYYY-MM-DD
    date_to: Optional[str] = None,
    search: Optional[str] = None,
    user=Depends(get_customer)
):
    filters = ["account_number = %s"]
    params  = [user["account_number"]]

    if category:
        filters.append("category = %s")
        params.append(category)
    if sub_category:
        filters.append("sub_category = %s")
        params.append(sub_category)
    if txn_type:
        filters.append("transaction_type = %s")
        params.append(txn_type.upper())
    if date_from:
        filters.append("date >= %s::date")
        params.append(date_from)
    if date_to:
        filters.append("date <= %s::date")
        params.append(date_to)
    if search:
        filters.append("(LOWER(description) LIKE %s OR LOWER(reference) LIKE %s)")
        params.extend([f"%{search.lower()}%", f"%{search.lower()}%"])

    where = " AND ".join(filters)
    rows = query(
        f"""SELECT id, account_number, date::text AS date, description, reference,
                   transaction_type, debit, credit, balance,
                   category, sub_category
            FROM transactions
            WHERE {where}
            ORDER BY date DESC, id DESC
            LIMIT %s OFFSET %s""",
        params + [limit, offset]
    )
    total = query(
        f"SELECT COUNT(*) AS cnt FROM transactions WHERE {where}",
        params,
        fetchone=True
    )
    return {
        "data": [dict(r) for r in rows],
        "total": total["cnt"] if total else 0
    }


@router.get("/transactions/count")
def transactions_count(
    category: Optional[str] = None,
    sub_category: Optional[str] = None,
    txn_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None,
    user=Depends(get_customer)
):
    filters = ["account_number = %s"]
    params  = [user["account_number"]]
    if category:
        filters.append("category = %s"); params.append(category)
    if sub_category:
        filters.append("sub_category = %s"); params.append(sub_category)
    if txn_type:
        filters.append("transaction_type = %s"); params.append(txn_type.upper())
    if date_from:
        filters.append("date >= %s::date"); params.append(date_from)
    if date_to:
        filters.append("date <= %s::date"); params.append(date_to)
    if search:
        filters.append("(LOWER(description) LIKE %s OR LOWER(reference) LIKE %s)")
        params.extend([f"%{search.lower()}%", f"%{search.lower()}%"])
    where = " AND ".join(filters)
    total = query(f"SELECT COUNT(*) AS cnt FROM transactions WHERE {where}", params, fetchone=True)
    return {"total": total["cnt"] if total else 0}


@router.get("/summary/monthly")
def monthly_summary(user=Depends(get_customer)):
    rows = query("""
        SELECT TO_CHAR(date, 'YYYY-MM')  AS month,
               SUM(debit)               AS total_debit,
               SUM(credit)              AS total_credit,
               COUNT(*)                 AS txn_count
        FROM transactions
        WHERE account_number = %s
        GROUP BY TO_CHAR(date, 'YYYY-MM')
        ORDER BY month
    """, (user["account_number"],))
    return [dict(r) for r in rows]


@router.get("/summary/category")
def category_summary(user=Depends(get_customer)):
    rows = query("""
        SELECT category,
               sub_category,
               SUM(debit)  AS total_spent,
               SUM(credit) AS total_received,
               COUNT(*)    AS txn_count
        FROM transactions
        WHERE account_number = %s
        GROUP BY category, sub_category
        ORDER BY total_spent DESC
    """, (user["account_number"],))
    return [dict(r) for r in rows]


@router.get("/summary/top_merchants")
def top_merchants(user=Depends(get_customer)):
    rows = query("""
        SELECT sub_category AS merchant,
               SUM(debit)   AS total,
               COUNT(*)     AS count
        FROM transactions
        WHERE account_number = %s
          AND transaction_type = 'DR'
          AND sub_category IS NOT NULL
          AND sub_category != 'Uncategorized'
        GROUP BY sub_category
        ORDER BY total DESC
        LIMIT 10
    """, (user["account_number"],))
    return [dict(r) for r in rows]


@router.get("/summary/balance_trend")
def balance_trend(user=Depends(get_customer)):
    rows = query("""
        SELECT date::text AS date, balance,
               debit, credit, description
        FROM transactions
        WHERE account_number = %s
        ORDER BY date ASC, id ASC
    """, (user["account_number"],))
    return [dict(r) for r in rows]


@router.get("/summary/weekly_heatmap")
def weekly_heatmap(user=Depends(get_customer)):
    """Returns spending by day-of-week and hour for heatmap."""
    rows = query("""
        SELECT
            EXTRACT(DOW FROM date)::int  AS dow,
            EXTRACT(MONTH FROM date)::int AS month,
            TO_CHAR(date, 'Mon')          AS month_name,
            SUM(debit)                    AS total_debit,
            COUNT(*)                      AS txn_count
        FROM transactions
        WHERE account_number = %s AND transaction_type = 'DR'
        GROUP BY dow, month, month_name
        ORDER BY month, dow
    """, (user["account_number"],))
    return [dict(r) for r in rows]


@router.get("/summary/cashflow")
def cashflow_summary(user=Depends(get_customer)):
    """Monthly net cashflow (credit - debit)."""
    rows = query("""
        SELECT TO_CHAR(date, 'YYYY-MM') AS month,
               SUM(credit) - SUM(debit) AS net_flow,
               SUM(credit)              AS income,
               SUM(debit)               AS expense
        FROM transactions
        WHERE account_number = %s
        GROUP BY TO_CHAR(date, 'YYYY-MM')
        ORDER BY month
    """, (user["account_number"],))
    return [dict(r) for r in rows]
