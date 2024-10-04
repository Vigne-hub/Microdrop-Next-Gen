from dropbot.proxy import SerialProxy
from dropbot import self_test as st
import os

proxy = SerialProxy()

result = st.self_test(proxy)

st.generate_report(result, f".{os.sep}reports{os.sep}report.html", force=True)


