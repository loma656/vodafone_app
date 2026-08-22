import flet as ft
import json
import base64
import time

def main(page: ft.Page):
    page.title = "لوحة تحكم الأدمن - توليد الأكواد"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    target_did_field = ft.TextField(label="Device ID الخاص بالعميل", width=350)
    
    duration_type_dropdown = ft.Dropdown(
        label="نوع المدة",
        options=[
            ft.dropdown.Option(text="أيام (Days)", key="days"),
            ft.dropdown.Option(text="أشهر (Months)", key="months"),
            ft.dropdown.Option(text="سنة (Years)", key="years"),
        ],
        value="days",
        width=350,
    )
    
    duration_value_field = ft.TextField(label="العدد (مثلاً: 7 أو 30 أو 1)", keyboard_type=ft.KeyboardType.NUMBER, width=350)
    result_code_field = ft.TextField(label="كود التفعيل الناتج للعميل", read_only=True, width=350, multiline=True)
    admin_status = ft.Text(value="", size=14)

    def generate_code(e):
        try:
            did = target_did_field.value.strip()
            dtype = duration_type_dropdown.value
            val = int(duration_value_field.value.strip())
            
            if not did:
                admin_status.value = "❌ يجب إدخال Device ID للعميل"
                admin_status.color = ft.Colors.RED
                page.update()
                return
            
            current_time = int(time.time())
            if dtype == 'days':
                expire_time = current_time + (val * 24 * 60 * 60)
            elif dtype == 'months':
                expire_time = current_time + (val * 30 * 24 * 60 * 60)
            elif dtype == 'years':
                expire_time = current_time + (val * 365 * 24 * 60 * 60)
            else:
                expire_time = current_time + (24 * 60 * 60)
                
            payload = {"did": did, "exp": expire_time}
            encoded = base64.b64encode(json.dumps(payload).encode()).decode()
            final_code = f"VF-{encoded}"
            
            result_code_field.value = final_code
            admin_status.value = "✅ تم توليد الكود بنجاح!"
            admin_status.color = ft.Colors.GREEN
        except:
            admin_status.value = "❌ تأكد من كتابة أرقام صحيحة في خانة العدد"
            admin_status.color = ft.Colors.RED
        page.update()

    gen_btn = ft.ElevatedButton(
        content=ft.Text("توليد الكود", color=ft.Colors.WHITE),
        on_click=generate_code,
        bgcolor=ft.Colors.BLUE,
        width=350
    )

    page.add(
        ft.Column([
            ft.Text("👑 لوحة تحكم الأدمن الخاصة بك", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
            ft.Divider(),
            target_did_field,
            duration_type_dropdown,
            duration_value_field,
            ft.Container(height=5),
            gen_btn,
            ft.Container(height=5),
            result_code_field,
            admin_status
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main)
