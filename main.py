import flet as ft
import requests
import json

# قائمة المنتجات
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
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.DARK

    # حقول الإدخال
    receiver_input = ft.TextField(label="رقم المستلم (11 رقم)", prefix_icon=ft.icons.PHONE, max_length=11)
    pin_input = ft.TextField(label="الرقم السري للمحفظة", password=True, can_reveal_password=True, prefix_icon=ft.icons.LOCK)
    
    # قائمة اختيار الباقات
    product_dropdown = ft.Dropdown(
        label="اختر الباقة",
        options=[ft.dropdown.Option(text=name, key=pid) for name, pid in ALL_PRODUCTS],
        width=350
    )
    
    status_text = ft.Text(value="", size=14, selectable=True)

    def execute_recharge(e):
        receiver = receiver_input.value.strip()
        pin = pin_input.value.strip()
        selected_product_id = product_dropdown.value

        if not receiver or not pin or not selected_product_id:
            status_text.value = "❌ جميع الحقول مطلوبة واختيار الباقة أساسي!"
            page.update()
            return

        if not (receiver.startswith("01") and len(receiver) == 11 and receiver.isdigit()):
            status_text.value = "❌ رقم غير صحيح! يجب أن يبدأ بـ 01 ويكون 11 رقماً."
            page.update()
            return

        status_text.value = "🔄 جاري تسجيل الدخول والحصول على التوكن..."
        page.update()

        try:
            # 1. الحصول على seamless token
            url = "http://mobile.vodafone.com.eg/checkSeamless/realms/vf-realm/protocol/openid-connect/auth"
            params = {'client_id': "cash-app"}
            headers = {
                'User-Agent': "okhttp/4.12.0",
                'clientId': "AnaVodafoneAndroid",
                'Accept-Language': "ar",
                'x-agent-device': "Samsung SM-A165F",
                'x-agent-version': "2025.11.1",
                'x-agent-build': "1063",
                'device-id': "b26ba335813fad21"
            }

            res = requests.get(url, params=params, headers=headers, timeout=30)
            if res.status_code != 200:
                status_text.value = f"❌ فشل الاتصال بخدمة التحقق: {res.status_code}"
                page.update()
                return

            data = res.json()
            seamless_token = data.get('seamlessToken')
            msisdn_sender = data.get('msisdn')

            if not seamless_token:
                status_text.value = "❌ فشل الحصول على seamless token"
                page.update()
                return

            if msisdn_sender and msisdn_sender.startswith('1'):
                msisdn_sender = '0' + msisdn_sender

            # 2. الحصول على access token
            status_text.value = "🔄 جاري توثيق الحساب..."
            page.update()

            token_url = "https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token"
            payload = {
                'grant_type': "password",
                'client_secret': "b86e30a8-ae29-467a-a71f-65c73f2ff5e3",
                'client_id': "cash-app"
            }
            token_headers = headers.copy()
            token_headers.update({
                'Accept': "application/json, text/plain, */*",
                'silentLogin': "true",
                'CRP': "false",
                'seamlessToken': seamless_token,
                'firstTimeLogin': "true"
            })

            res_token = requests.post(token_url, data=payload, headers=token_headers, timeout=30)
            if res_token.status_code != 200:
                status_text.value = "❌ فشل الحصول على توكن الوصول."
                page.update()
                return

            access_token = res_token_data = res_token.json().get('access_token')
            if not access_token:
                status_text.value = "❌ توكن الوصول غير متوفر."
                page.update()
                return

            # 3. تنفيذ طلب الشحن
            status_text.value = "🔄 جاري تنفيذ عملية الشحن..."
            page.update()

            order_url = "https://mobile.vodafone.com.eg/services/dxl/pom/productOrder"
            order_payload = {
                "channel": {"name": "MobileApp"},
                "orderItem": [{
                    "action": "insert",
                    "id": selected_product_id,
                    "product": {
                        "characteristic": [
                            {"name": "PaymentMethod", "value": "VFCash"},
                            {"name": "USE_EMONEY", "value": "False"},
                            {"name": "MerchantCode", "value": "81841829"}
                        ],
                        "id": selected_product_id,
                        "relatedParty": [
                            {"id": msisdn_sender, "name": "MSISDN", "role": "Subscriber"},
                            {"id": receiver, "name": "Receiver", "role": "Receiver"}
                        ]
                    },
                    "@type": selected_product_id,
                    "eCode": 0
                }],
                "relatedParty": [{"id": pin, "name": "pin", "role": "Requestor"}],
                "@type": "CashFakkaAndMared"
            }

            order_headers = headers.copy()
            order_headers.update({
                'Accept': "application/json",
                'api-host': "ProductOrderingManagement",
                'useCase': "CashFakkaAndMared',
                'X-Request-ID': "bb81cbe5-0c77-4673-945e-d2c0de90007a",
                'api-version': "v2",
                'msisdn': msisdn_sender,
                'Authorization': f"Bearer {access_token}",
                'Content-Type': "application/json; charset=UTF-8"
            })

            res_order = requests.post(order_url, data=json.dumps(order_payload), headers=order_headers, timeout=30)
            result = res_order.json()

            if res_order.status_code == 200 and (result.get('complete') == True or result.get('code') == '0000'):
                status_text.value = "✅ تم الشحن بنجاح تام!"
            else:
                reason = result.get('reason', result.get('message', 'تأكد من الرصيد أو الرقم السري'))
                status_text.value = f"❌ فشل الشحن: {reason}"
            page.update()

        except Exception as ex:
            status_text.value = f"❌ حدث خطأ غير متوقع: {str(ex)}"
            page.update()

    charge_btn = ft.ElevatedButton(text="تنفيذ الشحن الآن", icon=ft.icons.SEND, on_click=execute_recharge)

    page.add(
        ft.Text("شحن فكة ومارد - فودافون", size=20, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        receiver_input,
        pin_input,
        product_dropdown,
        ft.VerticalDivider(height=10),
        charge_btn,
        ft.Divider(),
        status_text
    )

if __name__ == "__main__":
    ft.app(target=main)

