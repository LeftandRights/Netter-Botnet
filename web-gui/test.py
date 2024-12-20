import json, time

from utils import send_packet, BackendPacket
from utils import variable

import streamlit as st
import pandas as pd

from uuid import uuid4
from datetime import datetime
from streamlit_option_menu import option_menu

st.set_page_config(layout = 'wide')
placeholder = st.empty()
_state = False

if (st.session_state.get('connected', None) is None):
    with placeholder:
        with st.status('Checking availability', expanded = True) as _status:
            st.write('Checking server connection..')

            if not (_state := send_packet(BackendPacket.SERVER_STATUS, '0').decode('UTF-8') == '0'):
                with st.container(border = True):
                    st.error('Server is not started properly, in order to start the server, run the following command ' \
                        '`python server.py`. For more information, see the documentation.'
                    )

                    _status.update(label = 'Checking complete', state = 'error', expanded = True)

            else:
                time.sleep(0.8)

                with st.container(border = True):
                    st.success('Connection to the server is established')
                    _status.update(label = 'Checking complete', state = 'error', expanded = True)

    time.sleep(2)

if (_state or st.session_state.get('connected')):
    placeholder.empty()
    st.session_state['connected'] = True

    selectedPage = option_menu(
        menu_title = None,
        options = ['Home', 'Client Manage', 'About'],
        orientation = 'horizontal',
        default_index = 0,
    )

    if (selectedPage == "Home"):
        st.markdown("<h1 style='text-align: center;'>Dashboard Overview</h1><br></br>", unsafe_allow_html = True)

        c1, c2 = st.columns([4, 4])
        to, tc = 5, 10

        dataFrame: dict = [
            {"UUID": str(uuid4()), "Public IP": "192.168.1.1", "Time Connected": datetime.now(), "Action": "Manage"}
            for i in range(20)
        ]

        with c2:
            with st.container(border = True, height = 540):
                st.map(
                    pd.DataFrame({
                        'lat': [-8.6500, 37.4056],
                        'lon': [115.2167, -122.0775]
                    })
                )

        with c1:
            col1, col2 = st.columns([2, 2])

            with col1:
                with st.container(border = True):
                    st.metric(label = "Online Client", value = to, delta = str(int((to / tc) * 100)) + "%")

            with col2:
                with st.container(border = True):
                    st.metric(label = "Total Client", value = tc, delta = f"-%{100 - int((to / tc) * 100)}")

            st.dataframe(pd.DataFrame(dataFrame), width = 800)

    if (selectedPage == "Client Manage"):
        if ('panel_' not in st.session_state):
            st.session_state['panel_'] = []

        with st.container(border = True):
            clientList: list[dict] = send_packet(BackendPacket.GET_CLIENT_ONLINE, '0')
            clientList = json.loads(clientList)

            usernameList = {client['username']: client['UUID'] for client in clientList}
            clientSelection = st.multiselect("Select client", (usernameList if usernameList else []))

            panel = st.container(border = True, height = 360)
            c = st.chat_input("Execute command")

            if (c):
                # if (not clientSelection):
                #     panel.chat_message('assistant').write('Please atleast select a client first')

                variable('_chatbox', default_value = list).insert(0, lambda: panel.chat_message('user').write(c))

                response = send_packet(BackendPacket.RUN_SERVER_COMMAND, c.encode('UTF-8'))
                response = json.loads(response.decode('UTF-8'))

                variable('_chatbox').insert(0, lambda: panel.chat_message('assistant').write('\n'.join(response)))

                for func in variable('_chatbox'):
                    func()
