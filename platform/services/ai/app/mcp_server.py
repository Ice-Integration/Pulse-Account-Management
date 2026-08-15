import os
import asyncpg
from mcp.server.fastmcp import FastMCP

mcp = FastMCP('pulse-support-tools')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://pulse:pulse@localhost:5432/pulse')

@mcp.tool()
async def get_account_summary(account_id: str) -> dict:
    """Return a read-only account summary for authorized support workflows."""
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        row = await conn.fetchrow('SELECT id, account_number, full_name, phone, status FROM accounts WHERE id=$1::uuid', account_id)
        return dict(row) if row else {"error": "account_not_found"}
    finally:
        await conn.close()

@mcp.tool()
async def list_open_invoices(account_id: str) -> list[dict]:
    """List unpaid invoices. This tool never charges a payment method."""
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        rows = await conn.fetch("SELECT id,total,status,due_at FROM invoices WHERE account_id=$1::uuid AND status IN ('open','past_due') ORDER BY due_at", account_id)
        return [dict(r) for r in rows]
    finally:
        await conn.close()

@mcp.tool()
async def draft_plan_change(account_id: str, to_plan_id: str) -> dict:
    """Create an approval-required plan-change draft. Does not change service directly."""
    return {"accountId": account_id, "toPlanId": to_plan_id, "status": "requires_human_approval"}

if __name__ == '__main__':
    mcp.run()
