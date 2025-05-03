import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from streamlit_folium import st_folium
from map import create_map
import streamlit as st
from vrp_agent_runner import VRPAssistant
import utils
from db_config import save_conversation
from inventory import display_inventory, display_orders


# UI
st.set_page_config(page_title="Vehicle Route Optimizer", page_icon="🗺️")
st.title("🗺️ Vehicle Route Optimizer")

tab1, tab2, tab3, tab4 = st.tabs(["Home", "Route Optimization", "Inventory Management", "Orders"])

if st.experimental_user.is_logged_in:
    # Initialize VRP Assistant with user_id
    if 'vrp_assistant' not in st.session_state:
        st.session_state.vrp_assistant = VRPAssistant(user_id=st.experimental_user.sub)

    with tab1:
        st.write(f"Welcome **{st.experimental_user.name}** to the Vehicle Route Optimization App!")
        st.write("This app helps you optimize delivery routes for your supply chain.")

        if st.button("Logout", use_container_width=True):
            st.logout()

    with tab2:
        user_query = st.text_area("Enter your query here:", height=80)

        with st.expander("Example Query"):
            st.write("""
            Please optimize delivery routes with:
            - 3 vehicles available
            - Each vehicle can carry 5 items
            """)

        if user_query:
            optimize_by = st.selectbox("Optimize by: ", ["Distance", "Time"])
            if optimize_by:
                # Set the optimization preference in config
                utils.set_optimize_by(optimize_by)
                if st.button("Solve VRP and Show Map", use_container_width=True):
                    with st.spinner("Optimizing route..."):
                        try:
                            try:
                                loop = asyncio.get_event_loop()
                            except RuntimeError:
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                
                            result = st.session_state.vrp_assistant.run(user_query)
                            output = result.final_output
                            st.session_state.output = output
                            st.write(output)

                            # Clean and verify output
                            output_dict = utils.clean_output(output)                 
                            
                            if isinstance(output_dict, dict):
                                # Store solution components in session state
                                st.session_state.explanation = output_dict.get('explanation', '')
                                st.session_state.routes = output_dict.get('routes', [])
                                st.session_state.coordinates = output_dict.get('coordinates', [])
                                st.session_state.addresses = output_dict.get('addresses', [])
                                st.session_state.demands = output_dict.get('demands', [])
                                st.session_state.plan_output = output_dict.get('plan_output', '')
                                st.session_state.user_query = output_dict.get('user_query', '')
                                
                            else:
                                st.error("Unexpected response format from the route optimizer")

                        except Exception as e:
                            st.error(f"Error solving VRP: {str(e)}")
                            st.error("Please check your query format and try again")


            # Only show map if we have valid routes
            if "routes" in st.session_state and st.session_state.routes:
                st.write("✅ Route optimization completed!")
                st.subheader("🛣️ **Optimized VRP Solution:**")
                st.write(st.session_state.explanation)

                if "plan_output" in st.session_state and st.session_state.plan_output:
                    st.text(st.session_state.plan_output)  # use st.text to preserve line breaks
                else:
                    st.error("❌ No plan output found.")

                save_conversation(
                    st.experimental_user.sub,
                    st.session_state.user_query,
                    st.session_state.explanation,
                    st.session_state.addresses,
                    st.session_state.demands,
                    st.session_state.plan_output
                )

                # Display the solution details
                for i, route in enumerate(st.session_state.routes):
                    st.write(f"Route {i + 1}: {' → '.join(str(node) for node in route)}")

                with st.spinner("Generating map..."):
                    st.subheader("Optimized Route Map")
                    try:
                        folium_map = create_map(
                            st.session_state.coordinates,
                            st.session_state.addresses,
                            st.session_state.routes,
                            st.session_state.demands
                        )
                        st_folium(folium_map, width=700, height=500)
                    except Exception as e:
                        st.error(f"Error generating map: {str(e)}")
                        st.error("Please make sure you have valid coordinates and routes")

    with tab3:
        # I want to use this tab to display inventory and orders in table
        st.subheader("Inventory Management Tab Content")
        st.table(display_inventory())
    
    with tab4:
        st.subheader("Orders Tab Content")
        st.write("This tab will display orders and their status.")
        st.table(display_orders())
else:
    st.subheader("🔑 Login to Access the App")
    st.write("Please log in using your configured account, to use the Vehicle Route Optimizer.")
    if st.button("Login with Google", use_container_width=True):
        st.login("google")
