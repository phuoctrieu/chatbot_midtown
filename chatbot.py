import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import webbrowser
from history import INITIAL_CHAT_HISTORY

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
                with st.spinner("Đang suy nghĩ..."):
                    response = st.session_state.chat.send_message(prompt)
                    st.write(response.text)
                    st.session_state.messages.append({"role": "assistant", "parts": response.text})
        except Exception as e:
            st.error(f"Có lỗi xảy ra: {str(e)}")
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
        st.image("logo.png", width=100)  # Adjust width as needed
    with col2:
        st.title("TRỢ LÝ NHÀ HÀNG MIDTOWN\n ASSISTANT RESTAURANT")

    st.markdown("""
    Chào mừng bạn đến với trợ lý ảo của nhà hàng Midtown! (Welcome to the Midtown restaurant virtual assistant!)\n
                 
    Tôi có thể giúp bạn tìm hiểu về menu, đặt bàn và trả lời mọi thắc mắc về nhà hàng. (I can help you learn about the menu, book a table and answer any questions about the restaurant.)
    """)
    
   
    

    # Sidebar content
    with st.sidebar:
        st.header("📍 Thông tin nhà hàng")
        st.info(RESTAURANT_INFO)
        # Thêm nút chỉ đường với link trực tiếp
        if st.button("🗺️ Xem chỉ đường", use_container_width=True):
            webbrowser.open_new_tab(MAPS_LINK)
        
        st.header("⏰ Giờ mở cửa")
        st.write("Hàng ngày: 10:00 - 23:00")
        
        st.header("🔄 Điều khiển")
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

    # Initialize session state
    initialize_session_state()

    # Display chat interface
    display_chat_interface()

if __name__ == "__main__":
    main()
