import streamlit, json
import pandas as pd
from uuid import uuid4
from datetime import datetime

placeholder = streamlit.empty()

online_clients_data = [
    {"UUID": str(uuid4()), "Public IP": "192.168.1.1", "Time Connected": datetime.now(), "Action": "Manage"},
    {"UUID": str(uuid4()), "Public IP": "192.168.1.2", "Time Connected": datetime.now(), "Action": "Manage"},
]

total_login = 5
# Convert to DataFrame
online_clients_df = pd.DataFrame(online_clients_data)

# with placeholder.form("login"):
#     streamlit.markdown("#### Enter your credentials")
#     streamlit.markdown("The username and password is written in the json config file (`config.json`). In order to login, please use the corresponding credintials from the config files.")

#     usernameInput = streamlit.text_input("Username")
#     passwordInput = streamlit.text_input("Password", type = "password")
#     submitButton = streamlit.form_submit_button("Login")

# if submitButton and (usernameInput == 'admin' and passwordInput == 'admin'):
#     streamlit.session_state['credintials'] = {'username': usernameInput, 'password': passwordInput}
#     placeholder.empty()

# Display welcome message and header without extra spacing

section_one, section_two = streamlit.columns(2)

with section_two:
    with streamlit.container(border = True, height = 900):
        streamlit.write('tresf')

streamlit.chat_input('Execute command')

with section_one:
    streamlit.write("""
    *Welcome back, admin!*
    <br>
    ***Dashboard overview***
    """, unsafe_allow_html = True)

    # Count of online clients
    online_client_count = len(online_clients_df)

    columnOne, columnTwo = streamlit.columns(2)

    with columnOne:
        streamlit.metric(label = "Total Client", value = total_login)

    with columnTwo:
        streamlit.metric(label = "Client Online", value = online_client_count)

    # Show online clients table if there are any clients online
    if online_client_count > 0:
        # Display client details in a table with action buttons
        streamlit.dataframe(online_clients_df)

        # Simulate manage action for each client
        for index, client in online_clients_df.iterrows():
            manage_button = streamlit.button(f"Manage {client['UUID']}", key = index)
            if manage_button:
                streamlit.write(f"Managing client {client['UUID']} at {client['Public IP']}")
    else:
        streamlit.write("No clients online at the moment.")
