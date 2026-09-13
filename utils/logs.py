import pandas as pd
import sqlite3
import json


def get_log(dbname="logs.db", table="chat_completions"):
    try:
        con = sqlite3.connect(dbname)
        query = f"SELECT * from {table}"
        cursor = con.execute(query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        data = [dict(zip(column_names, row)) for row in rows]
        con.close()
        return data
    except Exception:
        return []


def str_to_dict(s):
    try:
        return json.loads(s)
    except Exception:
        return {}


def print_usage_statistics(logging_session_id):
    log_data = get_log()
    if not log_data:
        print("No usage statistics recorded.")
        return

    log_data_df = pd.DataFrame(log_data)
    if "response" not in log_data_df.columns:
        print("No response log entries found.")
        return

    log_data_df["total_tokens"] = log_data_df.apply(
        lambda row: str_to_dict(row.get("response", "{}"))
        .get("usage", {})
        .get("total_tokens", 0) or 0,
        axis=1,
    )

    # Sum total tokens for all sessions
    total_tokens = log_data_df["total_tokens"].sum()

    # Sum total cost for all sessions
    total_cost = log_data_df["cost"].sum() if "cost" in log_data_df.columns else 0

    # Total tokens for specific session
    session_rows = (
        log_data_df[log_data_df["session_id"] == logging_session_id]
        if "session_id" in log_data_df.columns
        else pd.DataFrame()
    )
    session_tokens = session_rows["total_tokens"].sum() if not session_rows.empty else 0
    session_cost = (
        session_rows["cost"].sum()
        if (not session_rows.empty and "cost" in session_rows.columns)
        else 0
    )

    print("==============================")
    print(
        f"Total tokens for all sessions: {total_tokens}, total cost: {round(total_cost, 4)}"
    )
    print(
        f"Total tokens for session {logging_session_id}: {session_tokens}, cost: {round(session_cost, 4)}"
    )
