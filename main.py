import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from streamlit_folium import st_folium
from helper.map import create_map
import streamlit as st
from logistic_agents.vrp_agent_runner import VRPAssistant
from helper.clean_output import clean_output
from helper.map_tile import set_tile, tile_providers
from helper.optimize_by import set_optimize_by
from db_config import save_conversation
from inventory import display_inventory, display_orders
from route_optimization import solve_tsp

# UI
st.set_page_config(page_title="Vehicle Route Optimizer", page_icon="🗺️")
st.title("🗺️ Vehicle Route Optimizer")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Home", "VRP Optimization", "TSP Optimization", "Inventory Management", "Orders"])

if st.experimental_user.is_logged_in:
    # Initialize VRP Assistant with user_id
    if 'vrp_assistant' not in st.session_state:
        st.session_state.vrp_assistant = VRPAssistant(user_id=st.experimental_user.sub)

    # Home Tab
    with tab1:
        st.write(f"Welcome **{st.experimental_user.name}** to the Vehicle Route Optimization App!")
        st.write("This app helps you optimize delivery routes for your supply chain.")

        st.subheader("📝 FAQ")

        with st.expander("What is an optimization problem?"):
            st.write("""
            The goal of optimization is to find the best solution to a problem out of a large set of possible solutions. (Sometimes you'll be satisfied with finding any feasible solution; OR-Tools can do that as well.)

            Here's a typical optimization problem. Suppose that a shipping company delivers packages to its customers using a fleet of trucks. Every day, the company must assign packages to trucks, and then choose a route for each truck to deliver its packages. Each possible assignment of packages and routes has a cost, based on the total travel distance for the trucks, and possibly other factors as well. The problem is to choose the assignments of packages and routes that has the least cost.

            Like all optimization problems, this problem has the following elements:

            The objective—the quantity you want to optimize. In the example above, the objective is to minimize cost. To set up an optimization problem, you need to define a function that calculates the value of the objective for any possible solution. This is called the objective function. In the preceding example, the objective function would calculate the total cost of any assignment of packages and routes.

            An optimal solution is one for which the value of the objective function is the best. ("Best" can be either a maximum or a minimum.)

            The constraints—restrictions on the set of possible solutions, based on the specific requirements of the problem. For example, if the shipping company can't assign packages above a given weight to trucks, this would impose a constraint on the solutions.

            A feasible solution is one that satisfies all the given constraints for the problem, without necessarily being optimal.

            The first step in solving an optimization problem is identifying the objective and constraints.
            """)

        with st.expander("What is TSP Optimization?"):
            st.write("""
            One of the most common optimization tasks is vehicle routing, in which the goal is to find the best routes for a fleet of vehicles visiting a set of locations. Usually, "best" means routes with the least total distance or cost. Here are a few examples of routing problems:

            A package delivery company wants to assign routes for drivers to make deliveries.
            A cable TV company wants to assign routes for technicians to make residential service calls.
            A ride-sharing company wants to assign routes for drivers to pick up and drop off passengers.
            The most famous routing problem is the Traveling Salesperson Problem (TSP): find the shortest route for a salesperson who needs to visit customers at different locations and return to the starting point. A TSP can be represented by a graph, in which the nodes correspond to the locations, and the edges (or arcs) denote direct travel between locations. For example, the graph below shows a TSP with just four locations, labeled A, B, C, and D. The distance between any two locations is given by the number next to the edge joining them.
            """)

        with st.expander("What is VRP Optimization?"):
            st.write("""
            In the Vehicle Routing Problem (VRP), the goal is to find optimal routes for multiple vehicles visiting a set of locations. (When there's only one vehicle, it reduces to the Traveling Salesperson Problem.)

            But what do we mean by "optimal routes" for a VRP? One answer is the routes with the least total distance. However, if there are no other constraints, the optimal solution is to assign just one vehicle to visit all locations, and find the shortest route for that vehicle. This is essentially the same problem as the TSP.

            A better way to define optimal routes is to minimize the length of the longest single route among all vehicles. This is the right definition if the goal is to complete all deliveries as soon as possible.
            """)
        with st.expander("What is the difference between VRP and TSP?"):
            st.write("""
            The Traveling Salesperson Problem (TSP) is a special case of the Vehicle Routing Problem (VRP).

            In TSP, a single vehicle must visit all locations exactly once and return to the starting point, with the goal of minimizing the total travel distance or cost.

            In contrast, VRP involves multiple vehicles that start from a depot and must each serve a subset of locations. VRP can include additional constraints like vehicle capacity, delivery time windows, or specific priorities.

            In short:
            - TSP: Single vehicle, visit all nodes once.
            - VRP: Multiple vehicles, each with constraints (like capacity), optimized for overall efficiency.

            VRP is more realistic for logistics and delivery applications where resources and limits must be considered.
            """)

        st.subheader("For more information, please visit the following links: https://developers.google.com/optimization/routing")
        if st.button("Logout", use_container_width=True):
            st.logout()

    # VRP Optimization
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
                set_optimize_by(optimize_by)
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

                            with st.expander("📝 Output"):
                                st.write(output)

                            # Clean and verify output
                            output_dict = clean_output(output)                 
                            
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

                # Tile selector
                selected_tile = st.selectbox("Select a map tile:", list(tile_providers.keys()), key="vrp_tile_selector")
                set_tile(selected_tile)

                # Generate map only if it doesn't exist or tile has changed
                st.subheader("Optimized VRP Route Map")
                if "vrp_map" not in st.session_state or st.session_state.get("last_tile") != selected_tile:
                    with st.spinner("Generating map..."):
                        st.session_state.vrp_map = create_map(
                            st.session_state.coordinates,
                            st.session_state.addresses,
                            st.session_state.routes,
                            st.session_state.demands
                        )
                        st.session_state.last_tile = selected_tile

                # Display the map
                if "vrp_map" in st.session_state and st.session_state.vrp_map:
                    st_folium(
                        st.session_state.vrp_map,
                        width=700,
                        height=500,
                        key="tsp_map",
                        returned_objects=[]  # Prevent capturing map interactions
                    )

    # TSP Optimization
    with tab3:
        st.subheader("TSP Optimization")
        if st.button("Solve TSP and Show Map", use_container_width=True):
            with st.spinner("Optimizing route..."):
                try:
                    output, routes, coordinates, addresses, demands = solve_tsp()
                    st.session_state.plan_output_tsp = output
                    st.session_state.routes_tsp = routes
                    st.session_state.coordinates_tsp = coordinates
                    st.session_state.addresses_tsp = addresses
                    st.session_state.demands_tsp = demands
                except Exception as e:
                    st.error(f"Error solving TSP: {str(e)}")

        # Only show map if we have valid routes
        if "routes_tsp" in st.session_state and st.session_state.routes_tsp:
            st.write("✅ Route optimization completed!")
            st.subheader("🛣️ **Optimized TSP Solution:**")
            st.write(st.session_state.plan_output_tsp)

            # Display the solution details
            for i, route in enumerate(st.session_state.routes_tsp):
                st.write(f"Route {i + 1}: {' → '.join(str(node) for node in route)}")

            save_conversation(
                st.experimental_user.sub,
                "TSP Optimization",
                "TSP optimization completed.",
                st.session_state.addresses_tsp,
                st.session_state.demands_tsp,
                st.session_state.plan_output_tsp
            )

            # Tile selector
            selected_tile = st.selectbox("Select a map tile:", list(tile_providers.keys()), key="tsp_tile_selector")
            set_tile(selected_tile)

            # Generate map only if it doesn't exist or tile has changed
            st.subheader("Optimized TSP Route Map")
            if "tsp_map" not in st.session_state or st.session_state.get("last_tile") != selected_tile:
                with st.spinner("Generating map..."):
                    st.session_state.tsp_map = create_map(
                        st.session_state.coordinates_tsp,
                        st.session_state.addresses_tsp,
                        st.session_state.routes_tsp,
                        st.session_state.demands_tsp,
                    )
                    st.session_state.last_tile = selected_tile

            # Display the map
            if "tsp_map" in st.session_state and st.session_state.tsp_map:
                st_folium(
                    st.session_state.tsp_map,
                    width=700,
                    height=500,
                    key="tsp_map",
                    returned_objects=[]  # Prevent capturing map interactions
                )

    # Inventory Management Tab
    with tab4:
        # I want to use this tab to display inventory and orders in table
        st.subheader("Inventory Management Tab Content")
        st.table(display_inventory())

    # Orders Tab
    with tab5:
        st.subheader("Orders Tab Content")
        st.write("This tab will display orders and their status.")
        st.table(display_orders())

else:
    st.subheader("🔑 Login to Access the App")
    st.write("Please log in using your configured account, to use the Vehicle Route Optimizer.")
    if st.button("Login with Google", use_container_width=True):
        st.login("google")
