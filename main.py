import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from streamlit_folium import st_folium
from map import create_map
import streamlit as st
from agents import Runner
from vrp_agent_runner import assistant
import json
import re
import utils

# UI
st.set_page_config(page_title="Vehicle Route Optimizer", page_icon="🗺️")
st.title("🗺️ Vehicle Route Optimizer")

user_query = st.text_area("Enter your query here:", height=120)

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
                        
                    result = Runner.run_sync(assistant, user_query)
                    output = result.final_output
                    st.session_state.output = output

                    # Clean and verify output
                    try:
                        output_clean = output.strip()
                        output_json_match = re.search(r"\{.*\}", output_clean, re.DOTALL)
                        
                        if not output_json_match:
                            raise ValueError("No valid JSON object found in the output")

                        output_dict = json.loads(output_json_match.group())

                    except Exception as e:
                        st.error(f"❌ Failed to parse final_output as JSON: {str(e)}")
                        st.stop()                    
                    
                    if isinstance(output_dict, dict):
                        # Store solution components in session state
                        st.session_state.explanation = output_dict.get('explanation', '')
                        st.session_state.routes = output_dict.get('routes', [])
                        st.session_state.coordinates = output_dict.get('coordinates', [])
                        st.session_state.addresses = output_dict.get('addresses', [])
                        st.session_state.demands = output_dict.get('demands', [])
                        st.session_state.plan_output = output_dict.get('plan_output', '')
                        
                    else:
                        st.error("Unexpected response format from the route optimizer")

                except Exception as e:
                    st.error(f"Error solving VRP: {str(e)}")
                    st.error("Please check your query format and try again")


    # Only show map if we have valid routes
    if "routes" in st.session_state and st.session_state.routes:
        st.write("✅ Route optimization completed!")
        st.write(st.session_state.explanation)

        if "plan_output" in st.session_state and st.session_state.plan_output:
            st.write("🛣️ **Optimized VRP Solution:**")
            st.text(st.session_state.plan_output)  # use st.text to preserve line breaks
        else:
            st.error("❌ No plan output found.")

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