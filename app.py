import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# -----------------------------------------------------------------------------
# CONFIG & PAGE SETUP
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Hệ Thống Quản Lý Khách Sạn",
    page_icon="🏨",
    layout="wide"
)

# Custom CSS cho giao diện chuyên nghiệp
st.markdown("""
<style>
    .room-card {
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e0e0e0;
    }
    .room-available {
        background-color: #e8f5e9;
        border-left: 6px solid #2e7d32;
    }
    .room-occupied {
        background-color: #ffebee;
        border-left: 6px solid #c62828;
    }
    .room-dirty {
        background-color: #fff8e1;
        border-left: 6px solid #f57f17;
    }
    .stat-box {
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HELPER FUNCTION FOR IMAGES
# -----------------------------------------------------------------------------
def display_image(image_path, fallback_url, use_container_width=True):
    """
    Hàm hiển thị hình ảnh an toàn: Nếu file local tồn tại thì dùng file local,
    nếu không tìm thấy sẽ tự động fallback sang URL online để không bị lỗi FileNotFoundError.
    """
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=use_container_width)
    else:
        st.image(fallback_url, use_container_width=use_container_width)

# -----------------------------------------------------------------------------
# INITIALIZE STATE (DATABASE MÔ PHỎNG CÓ KHỞI TẠO ẢNH)
# -----------------------------------------------------------------------------
if 'rooms' not in st.session_state:
    st.session_state.rooms = {
        "101": {
            "type": "Đơn", 
            "price_hour": 50000, 
            "price_day": 300000, 
            "status": "Trống", 
            "checkin": None, 
            "guest": "", 
            "phone": "",
            "image": "ks.jpeg",
            "fallback_url": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=500"
        },
        "102": {
            "type": "Đơn", 
            "price_hour": 50000, 
            "price_day": 300000, 
            "status": "Trống", 
            "checkin": None, 
            "guest": "", 
            "phone": "",
            "image": "ks.jpeg",
            "fallback_url": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=500"
        },
        "201": {
            "type": "Đôi", 
            "price_hour": 80000, 
            "price_day": 500000, 
            "status": "Trống", 
            "checkin": None, 
            "guest": "", 
            "phone": "",
            "image": "ks.jpeg",
            "fallback_url": "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=500"
        },
        "202": {
            "type": "Đôi", 
            "price_hour": 80000, 
            "price_day": 500000, 
            "status": "Trống", 
            "checkin": None, 
            "guest": "", 
            "phone": "",
            "image": "ks.jpeg",
            "fallback_url": "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=500"
        },
        "301": {
            "type": "VIP", 
            "price_hour": 150000, 
            "price_day": 900000, 
            "status": "Trống", 
            "checkin": None, 
            "guest": "", 
            "phone": "",
            "image": "ks.jpeg",
            "fallback_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=500"
        },
    }

if 'history' not in st.session_state:
    st.session_state.history = []

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def calculate_bill(room_id, checkout_time, rent_type):
    """Tính tiền phòng dựa trên hình thức thuê (Giờ/Ngày)"""
    room = st.session_state.rooms[room_id]
    checkin_time = room['checkin']
    
    if not checkin_time:
        return 0, 0, 0
    duration = checkout_time - checkin_time
    total_hours = max(1, int(duration.total_seconds() // 3600))
    total_days = max(1, duration.days if duration.days > 0 else (1 if duration.total_seconds() > 43200 else 0))
    if rent_type == "Theo giờ":
        total_amount = total_hours * room['price_hour']
        duration_str = f"{total_hours} giờ"
    else:
        if total_days == 0:
            total_days = 1
        total_amount = total_days * room['price_day']
        duration_str = f"{total_days} ngày"
    return total_amount, duration_str, checkin_time

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION & STATS
# -----------------------------------------------------------------------------
# Hiển thị Logo khách sạn ở Thanh bên (Sidebar)
display_image("logo.png", "https://cdn-icons-png.flaticon.com/512/2983/2983780.png", use_container_width=False)
st.sidebar.title("🏨 Hotel Manager")

menu = st.sidebar.radio("Điều hướng", ["Sơ đồ phòng & Tác vụ", "Thống kê & Lịch sử", "Cấu hình phòng"])

# Thống kê nhanh ở Sidebar
total_rooms = len(st.session_state.rooms)
occupied_rooms = sum(1 for r in st.session_state.rooms.values() if r['status'] == 'Có khách')
available_rooms = sum(1 for r in st.session_state.rooms.values() if r['status'] == 'Trống')
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Trạng thái nhanh")
st.sidebar.write(f"🔴 Đang có khách: **{occupied_rooms}/{total_rooms}**")
st.sidebar.write(f"🟢 Phòng trống: **{available_rooms}/{total_rooms}**")

# -----------------------------------------------------------------------------
# SCREEN 1: SƠ ĐỒ PHÒNG & TÁC VỤ
# -----------------------------------------------------------------------------
if menu == "Sơ đồ phòng & Tác vụ":
    st.title("📌 Sơ đồ phòng & Quản lý Nhận/Trả")
    
    # Grid sơ đồ phòng
    cols = st.columns(3)
    for idx, (room_id, info) in enumerate(st.session_state.rooms.items()):
        col = cols[idx % 3]
        
        status_class = "room-available" if info['status'] == "Trống" else ("room-occupied" if info['status'] == "Có khách" else "room-dirty")
        status_icon = "🟢" if info['status'] == "Trống" else ("🔴" if info['status'] == "Có khách" else "🧹")
        
        with col:
            # Hiển thị ảnh của từng phòng
            display_image(info.get('image', 'ks.jpeg'), info.get('fallback_url', 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=500'))
            
            st.markdown(f"""
            <div class="room-card {status_class}">
                <h3>Phòng {room_id} <small>({info['type']})</small></h3>
                <p><b>Trạng thái:</b> {status_icon} {info['status']}</p>
                <p><b>Giá giờ:</b> {info['price_hour']:,} VNĐ | <b>Ngày:</b> {info['price_day']:,} VNĐ</p>
                {f"<p><b>Khách:</b> {info['guest']} - {info['phone']}</p>" if info['status'] == 'Có khách' else ''}
                {f"<p><b>Check-in:</b> {info['checkin'].strftime('%H:%M %d/%m/%Y')}</p>" if info['status'] == 'Có khách' else ''}
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("---")
    
    # Khu vực thao tác Check-in / Check-out
    col_in, col_out = st.columns(2)
    # BLOCK CHECK-IN
    with col_in:
        st.subheader("📥 Nhận phòng (Check-in)")
        available_list = [r for r, info in st.session_state.rooms.items() if info['status'] == "Trống"]
        
        if available_list:
            with st.form("checkin_form"):
                selected_room = st.selectbox("Chọn phòng trống", available_list)
                guest_name = st.text_input("Họ tên khách hàng")
                guest_phone = st.text_input("Số điện thoại")
                checkin_dt = st.datetime_input("Thời gian Check-in", value=datetime.now())
                
                submit_in = st.form_submit_button("Xác nhận Check-in", use_container_width=True)
                
                if submit_in:
                    if not guest_name:
                        st.error("Vui lòng nhập tên khách hàng!")
                    else:
                        st.session_state.rooms[selected_room]['status'] = "Có khách"
                        st.session_state.rooms[selected_room]['checkin'] = checkin_dt
                        st.session_state.rooms[selected_room]['guest'] = guest_name
                        st.session_state.rooms[selected_room]['phone'] = guest_phone
                        st.success(f"Đã nhận phòng {selected_room} thành công!")
                        st.rerun()
        else:
            st.info("Hiện không có phòng trống.")

    # BLOCK CHECK-OUT & TÍNH TIỀN
    with col_out:
        st.subheader("📤 Trả phòng & Thanh toán")
        occupied_list = [r for r, info in st.session_state.rooms.items() if info['status'] == "Có khách"]
        
        if occupied_list:
            selected_out_room = st.selectbox("Chọn phòng trả", occupied_list)
            rent_type = st.radio("Hình thức tính tiền", ["Theo giờ", "Theo ngày"], horizontal=True)
            checkout_dt = st.datetime_input("Thời gian Check-out", value=datetime.now())
            
            # Tính toán tiền phòng thời gian thực
            amount, duration, checkin_dt = calculate_bill(selected_out_room, checkout_dt, rent_type)
            
            st.warning(f"💰 **Tổng tiền thanh toán:** {amount:,} VNĐ")
            st.caption(f"Thời gian ở: {duration} (Từ {checkin_dt.strftime('%H:%M %d/%m')} đến {checkout_dt.strftime('%H:%M %d/%m')})")
            
            if st.button("Xác nhận Thanh toán & Trả phòng", type="primary", use_container_width=True):
                # Lưu lịch sử
                room_info = st.session_state.rooms[selected_out_room]
                st.session_state.history.append({
                    "Phòng": selected_out_room,
                    "Khách hàng": room_info['guest'],
                    "SĐT": room_info['phone'],
                    "Check-in": checkin_dt.strftime("%d/%m/%Y %H:%M"),
                    "Check-out": checkout_dt.strftime("%d/%m/%Y %H:%M"),
                    "Hình thức": rent_type,
                    "Thời lượng": duration,
                    "Tổng tiền (VNĐ)": amount
                })
                
                # Reset trạng thái phòng
                st.session_state.rooms[selected_out_room]['status'] = "Trống"
                st.session_state.rooms[selected_out_room]['checkin'] = None
                st.session_state.rooms[selected_out_room]['guest'] = ""
                st.session_state.rooms[selected_out_room]['phone'] = ""
                
                st.success(f"Thanh toán thành công phòng {selected_out_room}!")
                st.rerun()
        else:
            st.info("Không có phòng nào đang sử dụng.")

# -----------------------------------------------------------------------------
# SCREEN 2: THỐNG KÊ & LỊCH SỬ
# -----------------------------------------------------------------------------
elif menu == "Thống kê & Lịch sử":
    st.title("📈 Thống kê & Lịch sử giao dịch")
    
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        
        # Dashboard thẻ chỉ số
        total_revenue = df["Tổng tiền (VNĐ)"].sum()
        total_trans = len(df)
        
        m1, m2 = st.columns(2)
        m1.metric("💵 Tổng doanh thu", f"{total_revenue:,} VNĐ")
        m2.metric("📋 Tổng lượt thuê", f"{total_trans} lượt")
        
        st.markdown("---")
        st.subheader("Bảng lịch sử thanh toán")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Chưa có giao dịch thanh toán nào được ghi nhận.")

# -----------------------------------------------------------------------------
# SCREEN 3: CẤU HÌNH PHÒNG
# -----------------------------------------------------------------------------
elif menu == "Cấu hình phòng":
    st.title("⚙️ Cấu hình Danh sách phòng")
    
    # Form thêm phòng mới
    with st.expander("➕ Thêm phòng mới"):
        with st.form("add_room_form"):
            new_id = st.text_input("Số/Mã phòng (VD: 103)")
            new_type = st.selectbox("Loại phòng", ["Đơn", "Đôi", "VIP"])
            new_price_hour = st.number_input("Giá/Giờ (VNĐ)", value=50000, step=10000)
            new_price_day = st.number_input("Giá/Ngày (VNĐ)", value=300000, step=50000)
            new_img_file = st.text_input("Tên file ảnh (local) hoặc Đường dẫn URL", value="ks.jpeg")
            
            if st.form_submit_button("Lưu phòng"):
                if new_id in st.session_state.rooms:
                    st.error("Mã phòng này đã tồn tại!")
                elif not new_id:
                    st.error("Vui lòng nhập số phòng!")
                else:
                    st.session_state.rooms[new_id] = {
                        "type": new_type,
                        "price_hour": new_price_hour,
                        "price_day": new_price_day,
                        "status": "Trống",
                        "checkin": None,
                        "guest": "",
                        "phone": "",
                        "image": new_img_file,
                        "fallback_url": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=500"
                    }
                    st.success(f"Đã thêm phòng {new_id}!")
                    st.rerun()

    # Danh sách phòng hiện tại
    st.subheader("Danh sách phòng hiện có")
    rooms_data = []
    for r_id, r_info in st.session_state.rooms.items():
        rooms_data.append({
            "Mã phòng": r_id,
            "Loại phòng": r_info['type'],
            "Giá giờ (VNĐ)": f"{r_info['price_hour']:,}",
            "Giá ngày (VNĐ)": f"{r_info['price_day']:,}",
            "Trạng thái": r_info['status']
        })
    st.table(pd.DataFrame(rooms_data))
