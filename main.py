import flet as ft
import requests
import json
import datetime
import os
import base64
import time

FAKKA_PRODUCTS = [
    ("فكة 2.5 جنيه | يوم واحد | 45 وحدة", "Fakka_2.5_Unite"),
    ("فكة 3 جنيه | يوم واحد | 125 وحدة", "Fakka_3_Unite"),
    ("فكة 4.25 جنيه | يوم واحد | 190 وحدة", "Fakka_4.25_Unite"),
    ("فكة 5 جنيه | يوم واحد | 225 وحدة", "Fakka_5_Unite"),
    ("فكة 7 جنيه | 3 أيام | 300 وحدة", "Fakka_7_Unite"),
    ("فكة 9 جنيه | 4 أيام | 400 وحدة", "Fakka_9_Unite"),
    ("فكة 10 جنيه | 7 أيام | 450 وحدة", "Fakka_10_Unite"),
    ("فكة 10.5 جنيه | 7 أيام | 400 وحدة + 50MB", "Fakka_10.5_Unite"),
    ("فكة 12 جنيه | 7 أيام | 425 وحدة", "Fakka_12_Unite"),
    ("فكة 13.5 جنيه | 7 أيام | 625 وحدة", "Fakka_13.5_Unite"),
    ("فكة 15 جنيه | 7 أيام | 550 وحدة", "Fakka_15_Unite"),
    ("فكة 15.5 جنيه | 7 أيام | 625 وحدة", "Fakka_15.5_Unite"),
    ("فكة 17.5 جنيه | 10 أيام | 650 وحدة", "Fakka_17.5_Unite"),
    ("فكة 20 جنيه | 10 أيام | 750 وحدة", "Fakka_20_Unite"),
    ("فكة 26 جنيه | 10 أيام | 750 وحدة", "Fakka_26_Unite"),
]

MARED_PRODUCTS = [
    ("مارد 10 دقائق | 10 دقائق", "Mared_10_Minuts"),
    ("مارد 10 فليكس | 10 فليكس", "Mared_10_Flexs"),
    ("مارد 10 سوشيال", "Mared_10_Social"),
]

ALL_PRODUCTS = FAKKA_PRODUCTS + MARED_PRODUCTS

def main(page: ft.Page):
    page.title = "شحن فكة ومارد - فودافون"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    device_id_file = "/data/data/ru.iiec.pydroid3/cache/device_uid.txt" if os.path.exists("/data/data/ru.iiec.pydroid3") else "device_uid.txt"
    
    if os.path.exists(device_id_file):
        with open(device_id_file, "r") as f:
            my_device_id = f.read().strip()
    else:
        import uuid
        my_device_id = str(uuid.uuid4()).replace("-", "")[:16]
        try:
            with open(device_id_file, "w") as f:
                f.write(my_device_id)
        except:
            pass

    activation_file = "license.txt"
    
    def get_license_details():
        if os.path.exists(activation_file):
            try:
                with open(activation_file, "r") as f:
                    code = f.read().strip()
                if not code.startswith("VF-"):
                    return None, 0
                
                encoded_part = code[3:]
                decoded_json = base64.b64decode(encoded_part.encode()).decode()
                data = json.loads(decoded_json)
                
                saved_did = data.get("did")
                expire_time = data.get("exp", 0)
                
                if saved_did == my_device_id and time.time() < expire_time:
                    return saved_did, expire_time
            except:
                pass
        return None, 0

    content_area = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def load_main_app(expire_time):
        content_area.controls.clear()
        
        remaining_seconds = expire_time - time.time()
        rem_days = int(remaining_seconds // (24 * 3600))
        rem_hours = int((remaining_seconds % (24 * 3600)) // 3600)
        time_left_str = f"⏳ المدة المتبقية: {rem_days} يوم و {rem_hours} ساعة"

        product_dropdown = ft.Dropdown(
            label="اختر الباقة",
            options=[ft.dropdown.Option(text=name, key=pid) for name, pid in ALL_PRODUCTS],
            width=350,
        )
        
        receiver_field = ft.TextField(
            label="رقم المستلم (11 رقم)",
            keyboard_type=ft.KeyboardType.PHONE,
            max_length=11,
            width=350,
        )
        
        pin_field = ft.TextField(
            label="الرقم السري للمحفظة",
            password=True,
            can_reveal_password=True,
            keyboard_type=ft.KeyboardType.NUMBER,
            width=350,
        )
        
        status_text = ft.Text(value="", text_align=ft.TextAlign.CENTER, size=14)
        progress_ring = ft.ProgressRing(visible=False)

        def execute_recharge(e):
            if not product_dropdown.value:
                status_text.value = "❌ من فضلك اختر الباقة أولاً"
                status_text.color = ft.Colors.RED
                page.update()
                return
                
            receiver = receiver_field.value.strip()
            if not (receiver.startswith("01") and len(receiver) == 11 and receiver.isdigit()):
                status_text.value = "❌ رقم غير صحيح! يجب أن يبدأ بـ 01 ويتكون من 11 رقماً"
                status_text.color = ft.Colors.RED
                page.update()
                return
                
            pin = pin_field.value.strip()
            if not pin:
                status_text.value = "❌ الرقم السري مطلوب"
                status_text.color = ft.Colors.RED
                page.update()
                return

            product_id = product_dropdown.value
            product_name = next((name for name, pid in ALL_PRODUCTS if pid == product_id), "")
            short_product_name = product_name.split(" | ")[0]

            progress_ring.visible = True
            status_text.value = "🔄 جاري تنفيذ العملية..."
            status_text.color = ft.Colors.BLUE
            page.update()

            try:
                url = "http://mobile.vodafone.com.eg/checkSeamless/realms/vf-realm/protocol/openid-connect/auth"
                params = {'client_id': "cash-app"}
                headers = {
                    'User-Agent': "okhttp/4.12.0",
                    'Connection': "Keep-Alive",
                    'Accept-Encoding': "gzip",
                    'x-agent-operatingsystem': "16",
                    'clientId': "AnaVodafoneAndroid",
                    'Accept-Language': "ar",
                    'x-agent-device': "Samsung SM-A165F",
                    'x-agent-version': "2025.11.1",
                    'x-agent-build': "1063",
                    'digitalId': "",
                    'device-id': "b26ba335813fad21",
                    'If-Modified-Since': "Thu, 02 Apr 2026 09:09:07 GMT"
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=30)
                if response.status_code != 200:
                    raise Exception(f"فشل الاتصال (1): {response.status_code}")
                    
                data = response.json()
                seamless_token = data.get('seamlessToken')
                msisdn_sender = data.get('msisdn')
                
                if not seamless_token:
                    raise Exception("فشل الحصول على seamless token")
                    
                if msisdn_sender and msisdn_sender.startswith('1'):
                    msisdn_sender = '0' + msisdn_sender

                token_url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
                payload = {
                    'grant_type': "password",
                    'client_secret': "b86e30a8-ae29-467a-a71f-65c73f2ff5e3",
                    'client_id': "cash-app"
                }
                token_headers = {
                    'User-Agent': "okhttp/4.12.0",
                    'Accept': "application/json, text/plain, */*",
                    'Accept-Encoding': "gzip",
                    'silentLogin': "true",
                    'CRP': "false",
                    'seamlessToken': seamless_token,
                    'firstTimeLogin': "true",
                    'x-agent-operatingsystem': "16",
                    'clientId': "AnaVodafoneAndroid",
                    'Accept-Language': "ar",
                    'x-agent-device': "Samsung SM-A165F",
                    'x-agent-version': "2025.11.1",
                    'x-agent-build': "1063",
                    'digitalId': "",
                    'device-id': "b26ba335813fad21"
                }
                
                response = requests.post(token_url, data=payload, headers=token_headers, timeout=30)
                if response.status_code != 200:
                    raise Exception(f"فشل الحصول على التوكن: {response.status_code}")
                    
                token_data = response.json()
                access_token = token_data.get('access_token')
                if not access_token:
                    raise Exception("فشل الحصول على access token")

                order_url = "https://mobile.vodafone.com.eg/services/dxl/pom/productOrder"
                order_payload = {
                    "channel": {"name": "MobileApp"},
                    "orderItem": [
                        {
                            "action": "insert",
                            "id": product_id,
                            "product": {
                                "characteristic": [
                                    {"name": "PaymentMethod", "value": "VFCash"},
                                    {"name": "USE_EMONEY", "value": "False"},
                                    {"name": "MerchantCode", "value": "81841829"}
                                ],
                                "id": product_id,
                                "relatedParty": [
                                    {"id": msisdn_sender, "name": "MSISDN", "role": "Subscriber"},
                                    {"id": receiver, "name": "Receiver", "role": "Receiver"}
                                ]
                            },
                            "@type": product_id,
                            "eCode": 0
                        }
                    ],
                    "relatedParty": [{"id": pin, "name": "pin", "role": "Requestor"}],
                    "@type": "CashFakkaAndMared"
                }
                
                order_headers = {
                    'User-Agent': "okhttp/4.12.0",
                    'Accept': "application/json",
                    'Accept-Encoding': "gzip",
                    'api-host': "ProductOrderingManagement",
                    'useCase': "CashFakkaAndMared",
                    'X-Request-ID': "bb81cbe5-0c77-4673-945e-d2c0de90007a",
                    'device-id': "b26ba335813fad21",
                    'api-version': "v2",
                    'msisdn': msisdn_sender,
                    'Authorization': f"Bearer {access_token}",
                    'Accept-Language': "ar",
                    'x-agent-operatingsystem': "16",
                    'clientId': "AnaVodafoneAndroid",
                    'x-agent-device': "Samsung SM-A165F",
                    'x-agent-version': "2025.11.1",
                    'x-agent-build': "1063",
                    'digitalId': "",
                    'Content-Type': "application/json; charset=UTF-8"
                }

                res = requests.post(order_url, data=json.dumps(order_payload), headers=order_headers, timeout=30)
                current_time = datetime.datetime.now().strftime("%Y/%m/%d | %I:%M %p")
                
                success_message = (
                    f"✅ عملية ناجحة!\n\n"
                    f"رقم المستلم: {receiver}\n"
                    f"الباقة: {short_product_name}\n"
                    f"الوقت: {current_time}"
                )
                
                status_text.value = success_message
                status_text.color = ft.Colors.GREEN
                status_text.size = 16
                status_text.weight = ft.FontWeight.BOLD

            except Exception as ex:
                status_text.value = f"❌ حدث خطأ في الاتصال: {str(ex)}"
                status_text.color = ft.Colors.RED
                status_text.size = 14
                status_text.weight = ft.FontWeight.NORMAL
                
            progress_ring.visible = False
            page.update()

        submit_btn = ft.ElevatedButton(
            content=ft.Text("تنفيذ الشحن", color=ft.Colors.WHITE),
            on_click=execute_recharge,
            width=350,
            bgcolor=ft.Colors.RED,
        )

        content_area.controls.extend([
            ft.Text("فودافون فكة ومارد", size=22, weight=ft.FontWeight.BOLD),
            ft.Text(time_left_str, size=13, color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            product_dropdown,
            receiver_field,
            pin_field,
            ft.Container(height=10),
            submit_btn,
            ft.Container(height=10),
            progress_ring,
            status_text
        ])
        page.update()

    def load_activation_screen():
        content_area.controls.clear()
        
        id_field = ft.TextField(
            label="Device ID الخاص بك",
            value=my_device_id,
            read_only=True,
            width=260,
        )
        
        copy_btn = ft.IconButton(
            icon=ft.Icons.COPY,
            tooltip="نسخ الـ ID",
            on_click=lambda e: page.set_clipboard(my_device_id)
        )
        
        row_id = ft.Row([id_field, copy_btn], alignment=ft.MainAxisAlignment.CENTER)
        
        activation_input = ft.TextField(label="أدخل كود التفعيل", width=350)
        activation_status = ft.Text(value="", size=14)

        def verify_code(e):
            entered_code = activation_input.value.strip()

            try:
                if not entered_code.startswith("VF-"):
                    raise ValueError()
                
                encoded_part = entered_code[3:]
                decoded_json = base64.b64decode(encoded_part.encode()).decode()
                data = json.loads(decoded_json)
                
                saved_did = data.get("did")
                expire_time = data.get("exp", 0)
                
                if saved_did == my_device_id and time.time() < expire_time:
                    with open(activation_file, "w") as f:
                        f.write(entered_code)
                    load_main_app(expire_time)
                else:
                    activation_status.value = "❌ الكود غير صالح لهذا الجهاز أو منتهي الصلاحية!"
                    activation_status.color = ft.Colors.RED
                    page.update()
            except:
                activation_status.value = "❌ كود التفعيل خاطئ تماماً!"
                activation_status.color = ft.Colors.RED
                page.update()

        activate_btn = ft.ElevatedButton(
            content=ft.Text("تفعيل التطبيق", color=ft.Colors.WHITE),
            on_click=verify_code,
            width=350,
            bgcolor=ft.Colors.GREEN,
        )

        whatsapp_btn = ft.ElevatedButton(
            content=ft.Text("تواصل واتساب", color=ft.Colors.WHITE),
            icon=ft.Icons.PHONE,
            bgcolor=ft.Colors.GREEN_700,
            url="https://wa.me/201095486123",
            width=165
        )

        telegram_btn = ft.ElevatedButton(
            content=ft.Text("تواصل تليجرام", color=ft.Colors.WHITE),
            icon=ft.Icons.SEND,
            bgcolor=ft.Colors.BLUE_700,
            url="https://t.me/R_XTS",
            width=165
        )

        contact_row = ft.Row([whatsapp_btn, telegram_btn], alignment=ft.MainAxisAlignment.CENTER)

        content_area.controls.extend([
            ft.Text("🔒 التطبيق مقفل", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
            ft.Container(height=5),
            ft.Text("انسخ معرف جهازك وتواصل معنا للحصول على كود التفعيل:", size=12, text_align=ft.TextAlign.CENTER),
            row_id,
            ft.Container(height=5),
            activation_input,
            ft.Container(height=5),
            activate_btn,
            activation_status,
            ft.Container(height=10),
            ft.Text("للتواصل الشحن والتفعيل:", size=12, weight=ft.FontWeight.BOLD),
            ft.Container(height=5),
            contact_row
        ])
        page.add(content_area)

    did, exp = get_license_details()
    if did and exp > time.time():
        load_main_app(exp)
    else:
        load_activation_screen()

ft.app(target=main)

