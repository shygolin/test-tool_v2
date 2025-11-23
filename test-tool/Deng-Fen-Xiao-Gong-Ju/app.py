import streamlit as st
import streamlit.components.v1 as components
import json
import os
import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import requests

SAVE_PATH = "numbers_dict.json"
DEFAULT_SPREADSHEET_NAME = "登分小工具 - 成績記錄"
FIXED_SPREADSHEET_ID = "10vZcrrYPBPm4kAvsOoHusaAH8bCPKjvk4qjHjZNFNC8"

# Initialize the number dictionary with all valid keys
VALID_KEYS = [
    1, 2, 5, 8, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20,
    23, 24, 25, 26, 27, 28, 30, 31, 32, 33, 34, 35, 36, 37, 38,
    40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53,
    55, 56, 57, 58, 59, 60, 61, 62, 63, 64
]

def load_dict():
    """Load the dictionary from JSON file"""
    if os.path.exists(SAVE_PATH):
        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {int(k): (int(v) if v is not None else None) for k, v in data.items()}
        except Exception:
            return None
    return None

def save_dict(numbers_dict):
    """Save the dictionary to JSON file"""
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in numbers_dict.items()}, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def initialize_dict():
    """Initialize dictionary with all keys set to None"""
    return {k: None for k in VALID_KEYS}

def get_column_letter(col_index):
    """Convert column index to column letter(s) (1->A, 27->AA, etc.)"""
    result = ""
    while col_index > 0:
        col_index -= 1
        result = chr(65 + (col_index % 26)) + result
        col_index //= 26
    return result

def get_google_sheets_client():
    """Get Google Sheets client using Replit connection, uploaded credentials, Streamlit Secrets, or local secrets.json"""
    try:
        hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
        x_replit_token = None
        
        repl_identity = os.environ.get('REPL_IDENTITY')
        web_repl_renewal = os.environ.get('WEB_REPL_RENEWAL')
        
        # Try Replit connection first
        if repl_identity:
            x_replit_token = 'repl ' + repl_identity
        elif web_repl_renewal:
            x_replit_token = 'depl ' + web_repl_renewal
        
        if x_replit_token and hostname:
            url = f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=google-sheet'
            headers = {
                'Accept': 'application/json',
                'X_REPLIT_TOKEN': x_replit_token
            }
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    
                    if items:
                        connection_settings = items[0]
                        access_token = connection_settings.get('settings', {}).get('access_token')
                        
                        if not access_token:
                            oauth_creds = connection_settings.get('settings', {}).get('oauth', {}).get('credentials', {})
                            access_token = oauth_creds.get('access_token')
                        
                        if access_token:
                            credentials = Credentials(token=access_token)
                            client = gspread.authorize(credentials)
                            return client, None
            except Exception:
                pass
        
        # Try uploaded credentials from session state
        try:
            if 'uploaded_credentials' in st.session_state and st.session_state.uploaded_credentials:
                creds_dict = st.session_state.uploaded_credentials
                
                from google.oauth2.service_account import Credentials as ServiceAccountCredentials
                scopes = [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
                credentials = ServiceAccountCredentials.from_service_account_info(
                    creds_dict,
                    scopes=scopes
                )
                client = gspread.authorize(credentials)
                return client, None
        except Exception:
            pass
        
        # Try Streamlit Secrets (for Streamlit Cloud)
        try:
            if 'google_sheets_credentials' in st.secrets:
                import json as json_module
                creds_dict = st.secrets['google_sheets_credentials']
                if isinstance(creds_dict, str):
                    creds_dict = json_module.loads(creds_dict)
                
                from google.oauth2.service_account import Credentials as ServiceAccountCredentials
                scopes = [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
                credentials = ServiceAccountCredentials.from_service_account_info(
                    creds_dict,
                    scopes=scopes
                )
                client = gspread.authorize(credentials)
                return client, None
        except Exception as secret_error:
            pass
        
        # Try local secrets.json file
        try:
            secrets_path = os.path.join(os.path.dirname(__file__), 'secrets.json')
            if os.path.exists(secrets_path):
                with open(secrets_path, 'r', encoding='utf-8') as f:
                    creds_dict = json.load(f)
                
                from google.oauth2.service_account import Credentials as ServiceAccountCredentials
                scopes = [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
                credentials = ServiceAccountCredentials.from_service_account_info(
                    creds_dict,
                    scopes=scopes
                )
                client = gspread.authorize(credentials)
                return client, None
        except Exception as file_error:
            pass
        
        return None, "未找到Google Sheets認證信息。請上傳密鑰文件或在本地創建 secrets.json。"
        
    except Exception as e:
        return None, f"連接Google Sheets時出錯: {str(e)}"

def upload_to_google_sheets(numbers_dict, column_title, spreadsheet_name, spreadsheet_id=None):
    """Upload data to Google Sheets"""
    try:
        client, error = get_google_sheets_client()
        if error:
            return False, error
        
        spreadsheet_found = False
        spreadsheet = None
        
        if spreadsheet_id and spreadsheet_id.strip():
            try:
                spreadsheet = client.open_by_key(spreadsheet_id.strip())
                spreadsheet_found = True
            except Exception as id_error:
                return False, f"無法用ID打開試算表: {str(id_error)}"
        else:
            spreadsheet_name = spreadsheet_name.strip() if spreadsheet_name else DEFAULT_SPREADSHEET_NAME
            
            try:
                spreadsheet = client.open(spreadsheet_name)
                spreadsheet_found = True
            except gspread.SpreadsheetNotFound:
                spreadsheet_found = False
            except Exception as open_error:
                return False, f"查找試算表時出錯: {str(open_error)}"
            
            if not spreadsheet_found:
                try:
                    spreadsheet = client.create(spreadsheet_name)
                except Exception as create_error:
                    return False, f"創建試算表時出錯: {str(create_error)}"
        
        try:
            worksheet = spreadsheet.sheet1
        except Exception as ws_error:
            return False, f"訪問工作表時出錯: {str(ws_error)}"
        
        all_values = worksheet.get_all_values()
        
        if not all_values or (len(all_values) == 1 and all_values[0] == []):
            headers = ["座號"]
            seat_numbers = [[key] for key in sorted(VALID_KEYS)]
            
            worksheet.update('A1', [headers])
            worksheet.update('A2', seat_numbers)
        
        all_values = worksheet.get_all_values()
        
        # Search for the first empty column
        empty_col_index = None
        max_col_index = len(all_values[0]) if all_values and all_values[0] else 1
        
        for col_idx in range(1, max_col_index + 1):
            # Check if this column is empty (all cells are empty or don't exist)
            is_empty = True
            for row_idx in range(1, len(all_values)):  # Skip header row
                cell_value = ""
                if col_idx <= len(all_values[row_idx]):
                    cell_value = all_values[row_idx][col_idx - 1].strip()
                
                if cell_value:
                    is_empty = False
                    break
            
            if is_empty:
                empty_col_index = col_idx
                break
        
        # If no empty column found, append to the end
        if empty_col_index is None:
            empty_col_index = max_col_index + 1
        
        next_col_letter = get_column_letter(empty_col_index)
        
        worksheet.update(f'{next_col_letter}1', [[column_title]])
        
        score_data = []
        for key in sorted(VALID_KEYS):
            value = numbers_dict.get(key)
            score_data.append([value if value is not None else ""])
        
        worksheet.update(f'{next_col_letter}2', score_data)
        
        msg = f"成功上傳到Google Sheets！\n試算表：{spreadsheet_name}\n列名：{column_title}"
        return True, msg
        
    except Exception as e:
        return False, f"上傳失敗: {str(e)}"

# Initialize session state
if "numbers_dict" not in st.session_state:
    # Load from file if exists, otherwise initialize empty
    loaded_dict = load_dict()
    if loaded_dict is not None:
        st.session_state.numbers_dict = loaded_dict
    else:
        st.session_state.numbers_dict = initialize_dict()
        save_dict(st.session_state.numbers_dict)

if "message" not in st.session_state:
    st.session_state.message = None
if "message_type" not in st.session_state:
    st.session_state.message_type = "info"
if "show_upload_dialog" not in st.session_state:
    st.session_state.show_upload_dialog = False

# Page config
st.set_page_config(page_title="登分小工具", layout="wide")

# Title
st.title("登分小工具")

# Instructions
with st.expander("📖 使用說明", expanded=False):
    st.markdown("""
    **如何使用：**
    - 輸入數字（前兩位座號，後2-3位為成績）
    - 例如：`1025` 表示10號25分
    - 例如：`45123` 表示將45號123分
    - 點擊「顯示所有對應」查看完整列表
    - 點擊「複製所有值」將所有值複製到剪貼簿
    - 點擊「清空所有值」重置所有數據
    - 點擊enter會自動清空數據,紀錄後回到輸入框,不用一直點提交按鈕
    """)

# Main input section
st.subheader("輸入成績")

with st.form(key="input_form", clear_on_submit=True):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_input = st.text_input(
            "輸入 4-5 位數字",
            max_chars=5,
            placeholder="例如：1025 或 45123"
        )
    
    with col2:
        st.write("")  # Spacing
        submit_button = st.form_submit_button("提交", type="primary", use_container_width=True)

# Process input
if submit_button and user_input:
    user_input = user_input.strip()
    
    # Validate input
    if not user_input.isdigit() or len(user_input) not in [4, 5]:
        st.session_state.message = "❌ 格式不符"
        st.session_state.message_type = "error"
    else:
        key = int(user_input[:2])
        value = int(user_input[2:])
        
        if key not in VALID_KEYS:
            st.session_state.message = f"❌ 錯誤：座號 {key:02d} 不在系統中，請重新輸入"
            st.session_state.message_type = "error"
        else:
            st.session_state.numbers_dict[key] = value
            save_dict(st.session_state.numbers_dict)
            st.session_state.message = f"✅ 成功：座號 {key:02d} 已設定為 {value}"
            st.session_state.message_type = "success"

# Display message
if st.session_state.message:
    if st.session_state.message_type == "success":
        st.success(st.session_state.message)
    elif st.session_state.message_type == "error":
        st.error(st.session_state.message)
    else:
        st.info(st.session_state.message)
    st.session_state.message = None

# Action buttons
st.subheader("操作")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📋 顯示所有對應", use_container_width=True):
        st.session_state.show_all = True

with col2:
    values = ["" if st.session_state.numbers_dict[k] is None else str(st.session_state.numbers_dict[k]) 
              for k in sorted(VALID_KEYS)]
    
    if all(v == "" for v in values):
        st.button("📎 複製所有值", disabled=True, use_container_width=True)
        if st.session_state.get("show_copy_warning"):
            st.warning("⚠️ 沒有可複製的值")
    else:
        text = "\n".join(values)
        # Escape special characters for JavaScript
        text_escaped = text.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
        
        # Create a custom HTML button with direct clipboard access
        copy_button_html = f"""
        <div style="width: 100%;">
            <button id="copyBtn" style="
                width: 100%;
                padding: 0.5rem 1rem;
                background-color: #ff4b4b;
                color: white;
                border: none;
                border-radius: 0.5rem;
                font-size: 1rem;
                cursor: pointer;
                font-weight: 500;
            ">📎 複製所有值</button>
            <div id="copyStatus" style="margin-top: 0.5rem; font-size: 0.875rem;"></div>
            <textarea id="fallbackText" style="
                position: absolute;
                left: -9999px;
                width: 1px;
                height: 1px;
            ">{text_escaped}</textarea>
        </div>
        <script>
            const btn = document.getElementById('copyBtn');
            const status = document.getElementById('copyStatus');
            const fallbackText = document.getElementById('fallbackText');
            
            btn.addEventListener('click', async function() {{
                const text = `{text_escaped}`;
                let success = false;
                
                // Method 1: Try modern Clipboard API
                try {{
                    await navigator.clipboard.writeText(text);
                    success = true;
                }} catch (err) {{
                    // Method 2: Fallback to execCommand (works on mobile Safari)
                    try {{
                        fallbackText.value = text;
                        fallbackText.select();
                        fallbackText.setSelectionRange(0, 99999);
                        success = document.execCommand('copy');
                    }} catch (err2) {{
                        success = false;
                    }}
                }}
                
                if (success) {{
                    status.innerHTML = '<span style="color: #0e7c46;">✅ 值已複製到剪貼簿</span>';
                    btn.style.backgroundColor = '#0e7c46';
                    setTimeout(() => {{
                        btn.style.backgroundColor = '#ff4b4b';
                        status.innerHTML = '';
                    }}, 2000);
                }} else {{
                    status.innerHTML = '<span style="color: #ff8c00;">⚠️ 複製失敗，請使用下方文字框手動複製</span>';
                }}
            }});
        </script>
        """
        
        components.html(copy_button_html, height=100)
        
        # Always show the fallback text area for manual copy
        with st.expander("📝 手動複製（如果上方按鈕無效）"):
            st.text_area("所有值", value=text, height=200, label_visibility="collapsed")

with col3:
    if st.button("🗑️ 清空所有值", use_container_width=True):
        st.session_state.numbers_dict = initialize_dict()
        save_dict(st.session_state.numbers_dict)
        st.success("✅ 所有值已清空")
        st.rerun()

with col4:
    filled_count = sum(1 for v in st.session_state.numbers_dict.values() if v is not None)
    if filled_count == 0:
        st.button("📤 上傳到Google Sheets", disabled=True, use_container_width=True)
    else:
        if st.button("📤 上傳到Google Sheets", use_container_width=True):
            st.session_state.show_upload_dialog = True

if st.session_state.show_upload_dialog:
    st.divider()
    st.subheader("上傳到Google Sheets")
    
    # File upload section
    st.markdown("### 📁 上傳您的Google服務帳戶密鑰")
    uploaded_file = st.file_uploader(
        "選擇您的 secrets.json 文件",
        type=['json'],
        help="上傳您從 Google Cloud Console 下載的 JSON 密鑰文件"
    )
    
    if uploaded_file is not None:
        try:
            file_content = json.loads(uploaded_file.getvalue().decode("utf-8"))
            if 'type' in file_content and file_content['type'] == 'service_account':
                st.session_state.uploaded_credentials = file_content
                st.success("✅ 密鑰文件已上傳成功！")
            else:
                st.error("❌ 這不是有效的服務帳戶JSON文件")
        except json.JSONDecodeError:
            st.error("❌ 文件格式錯誤，請上傳有效的JSON文件")
    
    if 'uploaded_credentials' in st.session_state and st.session_state.uploaded_credentials:
        st.info(f"✅ 已加載密鑰：{st.session_state.uploaded_credentials.get('client_email', '未知')}")
    
    st.divider()
    
    with st.form(key="upload_form"):
        column_title = st.text_input(
            "列標題",
            placeholder="例如：第一次段考",
            help="這個標題將成為新增列的標題"
        )
        
        col_upload1, col_upload2 = st.columns([1, 1])
        with col_upload1:
            upload_submit = st.form_submit_button("確認上傳", type="primary", use_container_width=True)
        with col_upload2:
            upload_cancel = st.form_submit_button("取消", use_container_width=True)
        
        if upload_submit and column_title:
            with st.spinner("正在上傳到Google Sheets..."):
                success, message = upload_to_google_sheets(
                    st.session_state.numbers_dict, 
                    column_title, 
                    "", 
                    FIXED_SPREADSHEET_ID
                )
                
                if success:
                    st.success(message)
                    st.session_state.show_upload_dialog = False
                    st.rerun()
                else:
                    st.error(message)
                    
                    # Show setup instructions if running on Streamlit Cloud
                    if "未找到Google Sheets認證" in message:
                        st.info("""
### 🔧 Streamlit Cloud上的Google Sheets設置說明

此應用在Streamlit Cloud上需要Google服務帳戶認證才能訪問Google Sheets。

**步驟1: 建立Google服務帳戶**
1. 訪問 [Google Cloud Console](https://console.cloud.google.com/)
2. 創建新項目或選擇現有項目
3. 啟用 "Google Sheets API"
4. 創建服務帳戶 (IAM & Admin → Service Accounts)
5. 為服務帳戶創建JSON密鑰並下載

**步驟2: 在Streamlit Cloud中設置密鑰**
1. 在應用設置中選擇 "Secrets"
2. 將下載的JSON內容粘貼到 `Secrets` 欄中
3. 秘密名稱應為：`google_sheets_credentials`
4. 值為完整的JSON內容（從下載的JSON文件複製）

**步驟3: 在Google Sheets中授予權限**
1. 打開要編輯的Google Sheet
2. 點擊「共享」按鈕
3. 將服務帳戶的電子郵件地址添加為編輯者
   (電子郵件形式：xxx@xxx.iam.gserviceaccount.com)

完成後刷新此頁面即可使用！
                        """)
        elif upload_submit and not column_title:
            st.error("❌ 請輸入列標題")
        
        if upload_cancel:
            st.session_state.show_upload_dialog = False
            st.rerun()

# Display all mappings in a table
if "show_all" in st.session_state and st.session_state.show_all:
    st.subheader("所有對應列表")
    
    # Create columns for better display
    cols = st.columns(4)
    sorted_keys = sorted(VALID_KEYS)
    
    for idx, key in enumerate(sorted_keys):
        value = st.session_state.numbers_dict[key]
        col_idx = idx % 4
        
        with cols[col_idx]:
            if value is not None:
                st.markdown(f"**{key:02d}** → `{value}`")
            else:
                st.markdown(f"**{key:02d}** → —")
    
    if st.button("隱藏列表"):
        st.session_state.show_all = False
        st.rerun()

# Statistics
st.divider()
filled_count = sum(1 for v in st.session_state.numbers_dict.values() if v is not None)
total_count = len(VALID_KEYS)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("總人數", total_count)
with col2:
    st.metric("已填寫", filled_count)
with col3:
    st.metric("未填寫", total_count - filled_count)

# Grid view
st.subheader("快速檢視")
st.caption("綠色表示已設定值，灰色表示未設定")

# Create a grid layout
cols_per_row = 10
rows = []
current_row = []

for key in sorted(VALID_KEYS):
    value = st.session_state.numbers_dict[key]
    if value is not None:
        current_row.append(f"🟢 {key:02d}")
    else:
        current_row.append(f"⚪ {key:02d}")
    
    if len(current_row) == cols_per_row:
        rows.append(current_row)
        current_row = []

if current_row:
    rows.append(current_row)

for row in rows:
    cols = st.columns(cols_per_row)
    for idx, item in enumerate(row):
        with cols[idx]:
            st.markdown(f"<div style='text-align: center; font-size: 0.8em;'>{item}</div>", 
                       unsafe_allow_html=True)

# Auto-focus input field on page load
components.html(
    """
    <script>
        // Focus input field only once on page load
        setTimeout(function() {
            const inputs = window.parent.document.querySelectorAll('input[type="text"]');
            if (inputs.length > 0) {
                inputs[0].focus();
            }
        }, 100);
    </script>
    """,
    height=0,
)
