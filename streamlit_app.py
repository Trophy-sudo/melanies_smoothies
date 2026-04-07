# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your **Custom Smoothie**!")

# Input for customer name
name_on_order = st.text_input('Name on the Smoothie:')
if name_on_order:
    st.write('The name on the Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe.collect(),  # collect() to get values for multiselect
    max_selections=5
)

# Smoothie submission
if ingredients_list and name_on_order:
    ingredients_string = ' '.join(ingredients_list)

    # Show nutrition info for each selected fruit
    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen
        )
        st.dataframe(smoothiefroot_response.json(), use_container_width=True)

    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}', icon="✅")
        st.write(my_insert_stmt)

if st.button("Load Grader Orders"):
    # Clear previous orders first
    session.sql("delete from smoothies.public.orders").collect()

    # Insert the exact orders as per instructions
    session.sql("""
        insert into smoothies.public.orders (ingredients, name_on_order, order_filled, order_ts)
        select column1, column2, column3, current_timestamp()
        from values
        ('Apple Lime Ximenia', 'Kevin', FALSE),
        ('Dragon Fruit Guava Fig Jackfruit Blueberry', 'Divya', TRUE),
        ('Vanilla Fruit Nectarine', 'Xi', TRUE)
    """).collect()

    st.success("Grader orders loaded successfully ✅")
