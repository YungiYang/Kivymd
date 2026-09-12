from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText

class GameOverScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "game_over_screen"
        
        layout = BoxLayout(orientation="vertical", padding=30, spacing=20)

        title = MDLabel(
            text="GAME OVER",
            halign="center",
            theme_text_color="Custom",
            text_color=(1.0, 0.2, 0.2, 1.0),
            font_style="Display",
            role="small",
            bold=True
        )

        layout.add_widget(title)


        restart_btn = MDButton(
            MDButtonText(text="RESTART", font_style="Title", role="medium"),
            style="filled",
            size_hint=(1, None),
            height=54,
            theme_bg_color="Custom",
            md_bg_color=(0.1, 0.65, 0.95, 1.0),
        )


        restart_btn.bind(on_press=self.restart_game)
        layout.add_widget(restart_btn)

        self.add_widget(layout)