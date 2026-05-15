# test_connection.py
import pyTigerGraph as tg

conn = tg.TigerGraphConnection(
    host="https://tg-71535961-7e44-4162-ae90-03e9b6967f9e.tg-2635877100.i.tgcloud.io",
    username="hackathon_admin",
    password="HackathonPass123!",
    gsqlSecret="q1222031328i0dqejpcrtr8ih8u4q2ri"
)
print(conn.echo())  # Should print "Hello GSQL"
