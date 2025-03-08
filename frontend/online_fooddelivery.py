import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'cart' not in st.session_state:
    st.session_state.cart = []

# Sample data (In real app, this would come from your database)
SAMPLE_RESTAURANTS = {
    1: {"name": "Tasty Bites", "address": "123 Main St", "phone": "555-0123"},
    2: {"name": "Spice Garden", "address": "456 Oak Ave", "phone": "555-0456"},
}

SAMPLE_MENU = {
    1: [
        {"id": 1, "name": "Burger", "price": 9.99},
        {"id": 2, "name": "Pizza", "price": 12.99},
        {"id": 3, "name": "Salad", "price": 7.99},
    ],
    2: [
        {"id": 4, "name": "Curry", "price": 11.99},
        {"id": 5, "name": "Noodles", "price": 10.99},
        {"id": 6, "name": "Rice Bowl", "price": 8.99},
    ],
}

SAMPLE_USERS = {
    "user1": {"password": "pass1", "name": "John Doe", "phone": "555-1111", "address": "789 Pine Rd"},
}

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            if username in SAMPLE_USERS and SAMPLE_USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.success("Login successful!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    with col2:
        if st.button("Register"):
            st.session_state.page = "register"
            st.rerun()

def register_page():
    st.title("Register")
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    name = st.text_input("Full Name")
    phone = st.text_input("Phone")
    address = st.text_area("Address")
    
    if st.button("Submit Registration"):
        if new_username not in SAMPLE_USERS:
            SAMPLE_USERS[new_username] = {
                "password": new_password,
                "name": name,
                "phone": phone,
                "address": address
            }
            st.success("Registration successful! Please login.")
            time.sleep(1)
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("Username already exists")
    
    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

def restaurant_listing():
    st.title("Restaurants")
    for rest_id, rest_info in SAMPLE_RESTAURANTS.items():
        col1, col2, col3 = st.columns([2,2,1])
        with col1:
            st.subheader(rest_info["name"])
            st.write(f"📍 {rest_info['address']}")
            st.write(f"📞 {rest_info['phone']}")
        with col2:
            st.write("")
            st.write("")
            if st.button("View Menu", key=f"view_menu_{rest_id}"):
                st.session_state.selected_restaurant = rest_id
                st.session_state.page = "menu"
                st.rerun()
        st.divider()

def menu_page():
    rest_id = st.session_state.selected_restaurant
    rest_info = SAMPLE_RESTAURANTS[rest_id]
    
    st.title(f"{rest_info['name']} - Menu")
    
    for item in SAMPLE_MENU[rest_id]:
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            st.write(f"**{item['name']}**")
        with col2:
            st.write(f"${item['price']:.2f}")
        with col3:
            if st.button("Add to Cart", key=f"add_{item['id']}"):
                st.session_state.cart.append({
                    "restaurant": rest_info["name"],
                    "item": item["name"],
                    "price": item["price"]
                })
                st.success(f"Added {item['name']} to cart!")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Restaurants"):
            st.session_state.page = "restaurants"
            st.rerun()
    with col2:
        if st.button("View Cart"):
            st.session_state.page = "cart"
            st.rerun()

def cart_page():
    st.title("Shopping Cart")
    
    if not st.session_state.cart:
        st.write("Your cart is empty!")
    else:
        total = 0
        for item in st.session_state.cart:
            col1, col2, col3 = st.columns([2,1,1])
            with col1:
                st.write(f"**{item['item']}**")
                st.write(f"From: {item['restaurant']}")
            with col2:
                st.write(f"${item['price']:.2f}")
            with col3:
                if st.button("Remove", key=f"remove_{item['item']}"):
                    st.session_state.cart.remove(item)
                    st.rerun()
            total += item['price']
        
        st.divider()
        st.subheader(f"Total: ${total:.2f}")
        
        if st.button("Proceed to Checkout"):
            # In a real app, this would process the order
            st.success("Order placed successfully!")
            st.session_state.cart = []
            time.sleep(2)
            st.session_state.page = "restaurants"
            st.rerun()
    
    if st.button("Back to Restaurants"):
        st.session_state.page = "restaurants"
        st.rerun()

def main():
    st.sidebar.title("Navigation")
    
    if not st.session_state.logged_in:
        if 'page' not in st.session_state:
            st.session_state.page = "login"
            
        if st.session_state.page == "login":
            login_page()
        elif st.session_state.page == "register":
            register_page()
    else:
        user_info = SAMPLE_USERS[st.session_state.current_user]
        st.sidebar.write(f"Welcome, {user_info['name']}!")
        
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.page = "login"
            st.rerun()
        
        if 'page' not in st.session_state:
            st.session_state.page = "restaurants"
            
        if st.session_state.page == "restaurants":
            restaurant_listing()
        elif st.session_state.page == "menu":
            menu_page()
        elif st.session_state.page == "cart":
            cart_page()

if __name__ == "__main__":
    st.set_page_config(page_title="Food Delivery System", layout="wide")
    main()