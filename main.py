import flet as ft
import requests
import json

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
            res_json = res.json()

            if res.status_code == 200 and (res_json.get('complete') == True or res_json.get('code') == '0000'):
                status_text.value = f"✅ تم شحن ({product_name}) بنجاح للرقم {receiver}!"
                status_text.color = ft.Colors.GREEN
            else:
                err_msg = res_json.get('reason', res_json.get('message', 'فشلت العملية، تأكد من رصيد المحفظة'))
                status_text.value = f"❌ خطأ: {err_msg}"
                status_text.color = ft.Colors.RED

        except Exception as ex:
            status_text.value = f"❌ حدث خطأ: {str(ex)}"
            status_text.color = ft.Colors.RED
            
        progress_ring.visible = False
        page.update()

    submit_btn = ft.ElevatedButton(
        content=ft.Text("تنفيذ الشحن", color=ft.Colors.WHITE),
        on_click=execute_recharge,
        width=350,
        bgcolor=ft.Colors.RED,
    )

    page.add(
        ft.Text("فودافون فكة ومارد", size=22, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        product_dropdown,
        receiver_field,
        pin_field,
        ft.Container(height=10),
        submit_btn,
        ft.Container(height=10),
        progress_ring,
        status_text
    )

ft.app(target=main)

