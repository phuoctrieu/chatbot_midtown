import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import webbrowser
from history import INITIAL_CHAT_HISTORY
import requests
from datetime import datetime

# Configure the page
st.set_page_config(
    page_title="Midtown Restaurant AI Assistant",
    page_icon="🍽️",
    layout="wide"
)

# Tải các biến môi trường từ file .env
api_key = "AIzaSyC6TsnVHQ8S8RDkNmZo-cnIZODJqeA_-Ek"
genai.configure(api_key=api_key)



def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "model" not in st.session_state:
        generation_config = {
            "temperature": 0.9,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]
        
        st.session_state.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
    
    if "chat" not in st.session_state:
        st.session_state.chat = st.session_state.model.start_chat(
            history=INITIAL_CHAT_HISTORY
        )

def display_chat_interface():
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["parts"])

    # Chat input
    if prompt := st.chat_input("Nhập tin nhắn của bạn... (Ask your questions ...)"):
        # Add user message to chat
        st.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "parts": prompt})

        try:
            # Get bot response with loading indicator
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.chat.send_message(prompt)
                    st.write(response.text)
                    st.session_state.messages.append({"role": "assistant", "parts": response.text})
        except Exception as e:
            st.error(f"Có lỗi xảy ra: {str(e)}")

# Thêm hàm xử lý form đặt món
def display_order_form():
    # Container cho các món ăn
    if 'order_items' not in st.session_state:
        st.session_state.order_items = [{"dish": "", "quantity": 1}]
    
    # Tạo danh sách tạm để lưu các món sẽ xóa
    items_to_remove = []
    
    # Hiển thị các món ăn đã chọn
    for idx, item in enumerate(st.session_state.order_items):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            # Lưu giá trị vào item trong order_items
            item["dish"] = st.text_input("Món ăn/Food", value=item["dish"], key=f"dish_{idx}")
        with col2:
            # Lưu giá trị vào item trong order_items
            item["quantity"] = st.number_input("SL/Quant", min_value=1, value=item["quantity"], key=f"quantity_{idx}")
        with col3:
            # Chỉ hiển thị nút xóa nếu có nhiều hơn 1 món
            if len(st.session_state.order_items) > 1:
                if st.button("❌", key=f"delete_{idx}"):
                    items_to_remove.append(idx)
    
    # Xóa các món đã đánh dấu
    for idx in reversed(items_to_remove):
        st.session_state.order_items.pop(idx)
        st.rerun()
    
    # Nút thêm món
    if st.button("➕ Thêm món"):
        st.session_state.order_items.append({"dish": "", "quantity": 1})
        st.rerun()
    
    # Phương thức nhận hàng
    delivery_method = st.radio(
        "Phương thức nhận hàng/Delivery method",
        ["Ăn tại nhà hàng/Eat in", "Mang về/Take away"]
    )
    
    # Thời gian đến/giao hàng
    time_label = "Giờ đến/Time to arrive" if delivery_method == "Ăn tại nhà hàng" else "Giờ giao hàng/Time to deliver"
    delivery_time = st.time_input(time_label)
    
    # Địa chỉ ship nếu chọn mang về
    if delivery_method == "Mang về":
        shipping_address = st.text_area("Địa chỉ giao hàng/Delivery address")
    
    # Thông tin người đặt
    customer_name = st.text_input("Tên người đặt/Customer name", placeholder="Nhập tên của bạn/Enter your name")
    customer_phone = st.text_input(
        "Số điện thoại/Phone number", 
        placeholder="Nhập số điện thoại của bạn/Enter your phone number",
        help="Chỉ được nhập số/Only numbers"
    )
    
    # Validate phone number
    if customer_phone:
        if not customer_phone.isdigit():
            st.error("Số điện thoại chỉ được chứa các chữ số/Phone number only numbers")
            customer_phone = ""  # Reset invalid input
    
    # Tạo 2 cột cho nút Đặt hàng và nút Xóa
    col1, col2 = st.columns(2)

    with col1:
        # Nút đặt hàng
        place_order = st.button("🛍️ Đặt hàng/Order", type="primary")

    with col2:
        # Nút Xóa để reset form
        if st.button("🗑️ Xóa/Delete", type="secondary"):
            # Reset tất cả các trường nhập món ăn
            st.session_state.order_items = [{"dish": "", "quantity": 1}]
            
            # Xóa các giá trị món ăn trong session state
            for key in list(st.session_state.keys()):
                if key.startswith(("dish_", "quantity_")):
                    del st.session_state[key]
            
            # Reset các trường thông tin khách hàng
            if 'customer_name' in st.session_state:
                del st.session_state.customer_name
            if 'customer_phone' in st.session_state:
                del st.session_state.customer_phone
            if 'shipping_address' in st.session_state:
                del st.session_state.shipping_address
            if 'delivery_time' in st.session_state:
                del st.session_state.delivery_time
            if 'delivery_method' in st.session_state:
                del st.session_state.delivery_method
            
            st.rerun()

    # Di chuyển phần hiển thị thông báo ra ngoài cột
    if place_order:
        if not customer_name or not customer_phone:
            st.error("⚠️ Vui lòng điền đầy đủ tên và số điện thoại!/Please fill in your name and phone number")
        else:
            # Tạo tóm tắt đơn hàng
            current_date = datetime.now().strftime("%d/%m/%Y")
            order_summary = f"📋 CHI TIẾT ĐƠN HÀNG - {current_date}:\n\n"
            order_summary += "👤 Khách hàng:\n    " + customer_name + "\n\n"
            order_summary += "📞 Số điện thoại:\n    " + customer_phone + "\n\n"
            order_summary += "🚚 Phương thức:\n    " + delivery_method + "\n\n"
            order_summary += "⏰ Thời gian:\n    " + delivery_time.strftime('%H:%M') + "\n\n"
            
            if delivery_method == "Mang về":
                order_summary += f"📍 Địa chỉ: {shipping_address}\n"
            
            order_summary += "\n🍽️ Các món đã đặt:\n"
            for item in st.session_state.order_items:
                dish = st.session_state[f"dish_{st.session_state.order_items.index(item)}"]
                quantity = st.session_state[f"quantity_{st.session_state.order_items.index(item)}"]
                if dish:  # Chỉ hiển thị các món có tên
                    order_summary += f"   • {dish} x{quantity}\n"

            # Hiển thị tóm tắt trong dialog box
            st.info(order_summary)
            
            # Gửi đơn hàng đến Telegram
            telegram_response = send_telegram_message(order_summary)
            
            if telegram_response and telegram_response.get('ok'):
                st.success("Đặt hàng thành công! Chúng tôi sẽ liên hệ với bạn sớm nhất./Order successful! We will contact you soon.")
            else:
                st.warning("Đặt hàng không thành công! Vui lòng liên hệ 0788677778 để được hỗ trợ./Order failed! Please contact 0788677778 for support.")

# Constants
RESTAURANT_INFO = """
MIDTOWN RESTAURANT\n
Địa chỉ: đường Kon-Khoai, thị trấn A Lưới, huyện A Lưới, tỉnh Thừa Thiên Huế
\n
Liên hệ: Ánh Nguyễn (0344135008)
"""
# Thay đổi để sử dụng link trực tiếp
MAPS_LINK = "https://maps.app.goo.gl/35fL6oFzKuVM6gJp6"



def main():
    # Add logo and title in columns
    col1, col2 = st.columns([1, 5])
    
    with col1:
        st.image("logo.png", width=100)
    with col2:
        st.title("TRỢ LÝ NHÀ HÀNG MIDTOWN\n ASSISTANT RESTAURANT")

    st.markdown("""
    Chào mừng bạn đến với trợ lý ảo của nhà hàng Midtown! \n
                 
    Chúng tôi có thể giúp bạn tìm hiểu về menu, đặt bàn và trả lời mọi thắc mắc về nhà hàng. \n
    Welcome to the Midtown restaurant virtual assistant!\n
    We can help you learn about the menu, book a table and answer any questions about the restaurant.
    """)

    # Thêm CSS cho màu nền
    st.markdown("""
        <style>
            [data-testid="column"] {
                background-color: #f0f2f6;
                padding: 20px;
                border-radius: 10px;
                margin: 10px;
            }
            [data-testid="column"]:nth-of-type(2) {
                background-color: #e6f3ff;
            }
        </style>
    """, unsafe_allow_html=True)

    # Chia layout thành 2 cột chính
    chat_col, order_col = st.columns([2, 1])
    
    with chat_col:
        st.markdown("""
            <div style="
                background-color: #e6f3ff;
                padding: 20px;
                border-radius: 10px;
                margin: 10px;
            ">
        """, unsafe_allow_html=True)
        st.subheader("💬 Trò chuyện với trợ lý")
        initialize_session_state()
        display_chat_interface()
        st.markdown("</div>", unsafe_allow_html=True)
    
    with order_col:
        st.markdown("""
            <div style="
                background-color: #e6f3ff;
                padding: 20px;
                border-radius: 10px;
                margin: 10px;
            ">
        """, unsafe_allow_html=True)
        st.subheader("📝 Đặt món")
        display_order_form()
        st.markdown("</div>", unsafe_allow_html=True)

    # Sidebar content
    with st.sidebar:
        st.header("📍 Thông tin nhà hàng")
        st.info(RESTAURANT_INFO)
        st.link_button("🗺️ Xem chỉ đường (Directions)", MAPS_LINK, use_container_width=True)
        
        st.header("⏰ Giờ mở cửa")
        st.write("Hàng ngày: 10:00 (open) - 23:00 (closed)")
        
        st.header("🔄 Điều khiển (Control)")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Xem menu", use_container_width=True):
                st.session_state.show_menu = True
        with col2:
            if st.button("🔄 Reset chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.chat = st.session_state.model.start_chat()
                st.rerun()
                
        # Thêm nút About Midtown
        st.header("🏠 Giới thiệu")
        if st.button("About Midtown", use_container_width=True):
            st.session_state.show_about = True

    # Initialize session state for menu visibility
    if 'show_menu' not in st.session_state:
        st.session_state.show_menu = False

    # Display full-screen menu if show_menu is True
    if st.session_state.show_menu:
        modal = st.container()
        with modal:
            st.markdown("<h3 style='text-align: center;'>Menu Nhà hàng Midtown</h3>", unsafe_allow_html=True)
            st.image("menu.png", use_container_width=True)
            if st.button("Đóng menu"):
                st.session_state.show_menu = False
                st.rerun()

    # Initialize session state for about modal
    if 'show_about' not in st.session_state:
        st.session_state.show_about = False

    # Display about modal if show_about is True
    if st.session_state.show_about:
        modal = st.container()
        with modal:
            st.markdown("<h3 style='text-align: center;'>About Midtown Restaurant</h3>", unsafe_allow_html=True)
            
            # Hiển thị hình ảnh trong grid layout
            col1, col2 = st.columns(2)
            with col1:
                st.image("restaurant1.jpg", caption="Khu vực sân vườn", use_container_width=True)
                st.image("restaurant3.jpg", caption="Không gian trong nhà", use_container_width=True)
            with col2:
                st.image("restaurant2.jpg", caption="Không gian ngoài trời", use_container_width=True)
                st.image("restaurant4.jpg", caption="Cảnh sân vườn", use_container_width=True)
                
            if st.button("Đóng"):
                st.session_state.show_about = False
                st.rerun()

def send_telegram_message(message):
    bot_token = "7284894507:AAHBTQdC9OStTmZADff417XqNjcIV-BNP_Q"
    chat_id = "1785297395"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    try:
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload)
        print(f"Sending message to Telegram: {payload}")
        print(f"Telegram API Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error sending telegram message: {e}")
        return None

if __name__ == "__main__":
    main()
