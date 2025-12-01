import streamlit as st
import re
from datetime import datetime

# ---------------- CUSTOM EXCEPTIONS ----------------
class ProductNotFoundError(Exception):
    pass

class InvalidQuantityError(Exception):
    pass

class ValidationError(Exception):
    pass


# ---------------- SHOPPING SYSTEM CLASS ----------------
class ShoppingSystem:
    def __init__(self):
        self.products = {
            "Laptop": 50000,
            "Headphones": 1500,
            "SamsungS22": 60000,
            "Shirt": 800,
            "Pant": 1200,
            "Apple": 80,
            "Banana": 40,
            "Papaya": 60
        }

    def validate_name(self, name):
        if not re.fullmatch(r"[A-Za-z ]+", name):
            raise ValidationError("Customer name must contain only alphabets and spaces.")
        return True

    def validate_phone(self, phone):
        if not re.fullmatch(r"(0|91)?[0-9]{10}", phone):
            raise ValidationError("Phone number must be 10 digits (0 or 91 optional).")
        return True

    def generate_invoice(self, filename, customer_name, phone, cart):
        total = 0
        gst_rate = 0.10

        # Preparing Invoice Text
        invoice = []
        invoice.append("********** INVOICE **********\n")
        invoice.append(f"Customer Name: {customer_name}")
        invoice.append(f"Phone Number: {phone}")
        invoice.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        invoice.append("Items Purchased:")

        for item, d in cart.items():
            cost = d['price'] * d['qty']
            total += cost
            invoice.append(f"{item} - {d['qty']} pcs - ₹{cost}")

        gst_amount = total * gst_rate
        grand_total = total + gst_amount

        invoice.append(f"\nSubtotal: ₹{total}")
        invoice.append(f"GST (10%): ₹{gst_amount}")
        invoice.append(f"Total Amount: ₹{grand_total}")
        invoice.append("\nThank you for shopping with us!")

        invoice_text = "\n".join(invoice)

        with open(filename + ".txt", "w") as f:
            f.write(invoice_text)

        return filename + ".txt"  


# ---------------- STREAMLIT APP ----------------
st.set_page_config(page_title="Online Shopping System", layout="centered")
st.title("🛒 Online Shopping System - Streamlit Version")

system = ShoppingSystem()

# Initialize Session State
if "cart" not in st.session_state:
    st.session_state.cart = {}

# ---------------- SHOW PRODUCTS ----------------
st.header("Available Products")
for name, price in system.products.items():
    st.write(f"**{name}** - ₹{price}")

st.markdown("---")

# ---------------- ADD TO CART ----------------
st.subheader("Add Product to Cart")

product = st.selectbox("Select Product", list(system.products.keys()))
quantity = st.number_input("Enter Quantity", min_value=1, value=1, step=1)

if st.button("Add to Cart"):
    try:
        if product not in system.products:
            raise ProductNotFoundError("Product not available!")

        price = system.products[product]

        if product in st.session_state.cart:
            st.session_state.cart[product]["qty"] += quantity
        else:
            st.session_state.cart[product] = {"price": price, "qty": quantity}

        st.success(f"Added {quantity} x {product} to cart.")
    except Exception as e:
        st.error(e)

st.markdown("---")

# ---------------- CART DISPLAY ----------------
st.subheader("🛒 Your Cart")

if not st.session_state.cart:
    st.info("Cart is empty.")
else:
    for item, d in st.session_state.cart.items():
        st.write(f"{item} - {d['qty']} pcs - ₹{d['price'] * d['qty']}")

# ---------------- UPDATE & REMOVE ----------------
st.markdown("### Update or Remove Product")

if st.session_state.cart:
    item_list = list(st.session_state.cart.keys())
    selected_item = st.selectbox("Choose item", item_list)

    new_qty = st.number_input("New Quantity", min_value=1, value=1, step=1)
    
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Update Quantity"):
            try:
                st.session_state.cart[selected_item]["qty"] = new_qty
                st.success(f"Updated {selected_item} quantity to {new_qty}.")
            except Exception as e:
                st.error(e)

    with col2:
        if st.button("Remove Item"):
            try:
                del st.session_state.cart[selected_item]
                st.success(f"Removed {selected_item} from cart.")
            except Exception as e:
                st.error(e)

st.markdown("---")

# ---------------- CLEAR CART ----------------
if st.button("Clear Cart"):
    st.session_state.cart.clear()
    st.success("Cart cleared successfully!")

st.markdown("---")

# ---------------- PLACE ORDER ----------------
st.header("📦 Place Order")

customer_name = st.text_input("Enter Customer Name")
phone = st.text_input("Enter Phone Number")
filename = st.text_input("Enter Invoice File Name (without .txt)")

if st.button("Place Order"):
    try:
        if not st.session_state.cart:
            st.error("Cart is empty! Add items before placing order.")
        else:
            system.validate_name(customer_name)
            system.validate_phone(phone)

            if not filename.strip():
                st.error("File name cannot be empty!")
            else:
                file_path = system.generate_invoice(filename, customer_name, phone, st.session_state.cart)
                st.success(f"Order placed! Invoice generated: {file_path}")

                with open(file_path, "rb") as file:
                    st.download_button("Download Invoice", file, file_name=file_path)

                st.session_state.cart.clear()

    except Exception as e:
        st.error(e)
