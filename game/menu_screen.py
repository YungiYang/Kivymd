from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText


class MenuScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "menu_screen"
        
        layout = BoxLayout(orientation="vertical", padding=30, spacing=20)
        
        title = MDLabel(
            text="GALAXY DEFENDER",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.2, 0.85, 1.0, 1.0),
            font_style="Display",
            role="small",
            bold=True
        )
        layout.add_widget(title)
        
        start_btn = MDButton(
            MDButtonText(text="ПОЧАТИ ГРУ", font_style="Title", role="medium"),
            style="filled",
            size_hint=(1, None),
            height=54,
            theme_bg_color="Custom",
            md_bg_color=(0.1, 0.65, 0.95, 1.0),
        )
        start_btn.bind(on_release=self.start_game)
        layout.add_widget(start_btn)

        self.add_widget(layout)

    def start_game(self, *args):
        self.manager.current = "game_screen"
