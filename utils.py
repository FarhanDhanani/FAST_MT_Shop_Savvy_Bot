import json
import random
import string
import requests
from PIL import Image
from enum import Enum
from io import BytesIO
from solutions.graph import simple_content_based_filtering
import streamlit as st

class MessageType(Enum):
    SIMPLE = "simple"
    PRODUCT_ITEMS = "product_items"
    CART_ITEMS = "cart_items"

def save_message_for_simple_type(role, content, type=MessageType.SIMPLE):
    st.session_state.messages.append({"role": role, "content": content, "type":type.value})
    return

def save_message_for_product_item_type(role, content, items, type=MessageType.PRODUCT_ITEMS):
    st.session_state.messages.append({"role": role, "content": content, "product_items":items, "type":type.value})
    return

def save_message_for_cart_item_type(role, items, type=MessageType.CART_ITEMS):
    st.session_state.messages.append({"role": role, "cart_items":items, "type":type.value})
    return

def id_generator(size=4, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def render_messages(messages):
    for message in messages:
        if(message['type']== MessageType.PRODUCT_ITEMS.value):
            list_product_items(message['role'], message['content'], message['product_items'], save=False)
        elif(message['type']== MessageType.CART_ITEMS.value):
            list_cart_items(message['cart_items'], role=message['role'], save=False)
        else:
            write_message(message['role'], message['content'], save=False)
    return

# tag::write_message[]
def write_message(role, content, save = True):
    """
    This is a helper function that saves a message to the
     session state and then writes a message to the UI
    """
    # Append to session state
    if save:
        save_message_for_simple_type(role, content)

    # Write to UI
    with st.chat_message(role):
        st.markdown(content)
    return
# end::write_message[]

@st.cache_data
def get_image(url):
    headers = {
        'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'referer': url,
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    r = requests.get(url, headers=headers)
    image = Image.open(BytesIO(r.content))
    return image

def add_product_in_cart(product_item):
    st.session_state.cart_items.append({
        "ProductName": product_item["ProductName"],
        "UnitPrice": product_item["UnitPrice"],
        "QuantityPerUnit": product_item["QuantityPerUnit"],
        "CategoryID": product_item["CategoryID"],
        "NumberOfUnitOrdered": 1
    })


def show_item_detail(item, index):
    st.write(f"### {item['ProductName']} Details")
    st.write(f"Price: ${item['UnitPrice']}")
    if(item['Discontinued']):
        st.write(f"Product Available: Yes")
        st.write(f"No. Units in Stock: ${item['UnitsInStock']}")
        st.write(f"Quantity Per Each Unit: ${item['QuantityPerUnit']}")
    else:
         st.write(f"Product Available: No")
    st.image(get_image(item['ProductImageUrl']), caption=f"Description: {item['ProductDescription']}")
    st.button(f"Add to card", 
              key=f"##{index}"+id_generator(),
              on_click=add_product_in_cart,
              args=[item])
    # Add more details as needed

def check_product_exist_in_cart(product_name)->bool:
    cart_items = st.session_state.cart_items
    for item in cart_items:
        if(product_name == item["ProductName"]):
           return True
    return False

# tag::write_custom_message[]
def list_product_items(role, content, items, save = True):
    """
    This is a helper function that saves a message to the
     session state and then writes a message to the UI
    """
    # Append to session state
    if save:
        save_message_for_product_item_type(role, content, items)

    # Write to UI
    with st.chat_message(role):
        st.markdown(content)
        for i, item in enumerate(items):
            expander_content = f"Details of product '{item['ProductName']}' having price '{item['UnitPrice']}'"
            if(check_product_exist_in_cart(item['ProductName'])):
                expander_content = f"ADDED IN YOUR CART: details of product '{item['ProductName']}' having price '{item['UnitPrice']}'"
            expand_state = st.expander(expander_content, expanded=False)
            with expand_state:
                show_item_detail(item, i)
    return
# end::write_custom_message[]

def display_product_details(product_details, content="", grace_message=""):
    if product_details:
        product_names = []
        products_to_display = []
        product_details_json = json.loads(product_details)
        if product_details_json:
            for product in product_details_json:
                product_names.append(product['p']['ProductName'])
                products_to_display.append({
                    'CategoryID':product['p']['CategoryID'],
                    'Discontinued': product['p']['Discontinued'],
                    'ProductName': product['p']['ProductName'],
                    'UnitsInStock': product['p']['UnitsInStock'],
                    'ProductImageUrl': product['p']['ProductImageUrl'],
                    'QuantityPerUnit': product['p']['QuantityPerUnit'],
                    'UnitPrice': product['p']['UnitPrice'],
                    'ProductDescription': product['p']['ProductDescription']
                })
            result = ', '.join(product_names)
            response_message = content+"Please check the details of "+ result+ " products."
            list_product_items('assistant', response_message, products_to_display)
        else:
            write_message('assistant', grace_message)
    else:
        write_message('assistant', grace_message)
    return

def delete_cart_items(index):
    del st.session_state.cart_items[index]
    messages = st.session_state.messages
    for msg in messages:
        if msg["type"] == MessageType.CART_ITEMS:
            msg["cart_items"] = st.session_state.cart_items
    return

def get_cart_items():
    cart_items = st.session_state.cart_items
    return cart_items

def order_my_cart():
    category_ids = []
    product_names = []
    for cart_item in st.session_state.cart_items:
        category_ids.append(cart_item['CategoryID'])
        product_names.append(cart_item['ProductName'])
    response = simple_content_based_filtering(category_ids, product_names)
    display_product_details(product_details=response, 
                            content="Thank you for your purchase. Your order has been processed successfully. Based on your purchase, we believe you'll also like the following products\n",
                            grace_message="Thank you for your purchase. Your order has been processed successfully."
                            )
    st.session_state.cart_items = []
    return

def list_cart_items(cart_items, role="assistant", save = True):
    content=''
    message = st.chat_message(role)
    if(not cart_items):
        content = 'Appologies your cart is empty'
        message.write(content)
    else:
        total_price = 0
        for item in cart_items:
            total_price+=item["UnitPrice"]

        content = f"Items in your cart are listed below, total bill = {total_price}"
        message.write(content)
        leftcol, mid1col, mid2col, mid3col, rightcol = message.columns(5)

        for i, (item) in enumerate(cart_items):
            leftcol.markdown(f"Product: {item['ProductName']}")
            mid1col.markdown(f"Price: {item['UnitPrice']}")
            mid2col.markdown(f"Quantity/Unit: {item['QuantityPerUnit']}")
            mid3col.markdown(f"Units Ordered: {item['NumberOfUnitOrdered']}")
            rightcol.button(f"Delete", 
                            key=f"##{i}"+id_generator(),
                            on_click=delete_cart_items,
                            args=[i])
            
        message.button(f"Order Cart", 
                       type="primary", 
                       on_click=order_my_cart,
                       key=f"##order"+id_generator(),
                       use_container_width=True)
    if save:
        save_message_for_cart_item_type(role=role, items=cart_items)

    return