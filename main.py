from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.anchorlayout import AnchorLayout
from kivy.metrics import dp
from kivy.graphics import RoundedRectangle, Color
from kivy.core.text import LabelBase
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty, ObjectProperty
from sqlite.db_utils import create_user, authenticate_user, save_game, get_user_games
import sqlite3


# Register custom font
LabelBase.register(name='GameFont', fn_regular='assets/game_font.ttf')

class RoundedLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0, 0, 0, 0.5)  # Background color for readability
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
            self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size

class RoundedTextInput(TextInput):
    def __init__(self, **kwargs):
        kwargs['foreground_color'] = (0, 0, 0, 1)  # Ensure text color is black
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 0)  # Remove background color for text input (or set it to transparent if needed)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
            self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.1, 0.6, 0.1, 1)  # Green color for buttons
        with self.canvas.before:
            Color(0.1, 0.6, 0.1, 1)  # Button color
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
            self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size


class LoginScreen(Screen):
    def build(self):
        self.clear_widgets()
        self.layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(15))
        
        # Background Image
        self.add_widget(Image(source='assets/background.jpg', allow_stretch=True, keep_ratio=False))  # Background image

        # Title
        title = RoundedLabel(
            text='Retro-Game', 
            font_size=dp(45), 
            font_name='GameFont', 
            bold=True, 
            size_hint_y=None, 
            height=dp(350),
            pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.layout.add_widget(title)
        
        # Email Input
        self.email = TextInput(hint_text='Username', multiline=False, size_hint_y=None, height=dp(50), foreground_color=(0, 0, 0, 1))        
        self.layout.add_widget(self.email)
        
        # Password Input
        self.password = TextInput(hint_text='Password', multiline=False, password=True, size_hint_y=None, height=dp(50), foreground_color=(0, 0, 0, 1))
        self.layout.add_widget(self.password)
        
        # Error Label (removed)
        self.error = Label(text='', font_size=dp(14), font_name='GameFont', color=(1, 0, 0, 1), size_hint_y=None, height=dp(40))
        
        # Login Button
        self.login_button = RoundedButton(text='Login', on_press=self.validate_user, size_hint_y=None, height=dp(50))
        self.layout.add_widget(self.login_button)

        # create account button
        self.create_account_button = RoundedButton(text='Create New Account', background_color=(0.0, 0.0, 0.9, 1), size_hint_y=None, height=dp(50))
        self.create_account_button.bind(on_press=self.goto_create_account)
        self.layout.add_widget(self.create_account_button)

        self.add_widget(self.layout)

    def goto_create_account(self, instance):
        self.manager.current = 'create_account'

    def _update_bg(self, instance, value):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def validate_user(self, instance):
        username = self.email.text
        password = self.password.text
        
        app = App.get_running_app()
        app.cursor.execute('''
            SELECT * FROM users WHERE username = ? AND password = ?
        ''', (username, password))
        
        user = app.cursor.fetchone()
        
        if user:
            app.username = username  # Set the username in the App instance
            self.manager.current = 'dashboard'
        else:
            self.show_error_popup()


    def save_account(self, instance):
        username = self.username.text
        password = self.password.text

        app = App.get_running_app()
        try:
            app.cursor.execute('''
                INSERT INTO users (username, password) VALUES (?, ?)
            ''', (username, password))
            app.conn.commit()
            print(f'Username: {username}, Password: {password}')
            self.manager.current = 'login'
        except sqlite3.IntegrityError:
            print("Username already exists")

    def show_error_popup(self):
        error_popup = Popup(title='Login Error', size_hint=(0.5, 0.3))
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text='Invalid credentials', font_size=dp(14), font_name='GameFont', color=(1, 0, 0, 1)))
        close_button = Button(text='Close', size_hint_y=None, height=dp(50), on_press=error_popup.dismiss)
        content.add_widget(close_button)
        error_popup.content = content
        error_popup.open()

        
class CreateAccountScreen(Screen):
    def build(self):
        self.clear_widgets()
        self.layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(15))

        # Background Image
        self.add_widget(Image(source='assets/background.jpg', allow_stretch=True, keep_ratio=False))

        # Title
        title = RoundedLabel(text='Create Account', font_size=dp(30), font_name='GameFont', bold=True, size_hint_y=None, height=dp(200), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.layout.add_widget(title)

        # Username Input
        self.username = TextInput(hint_text='Username', multiline=False, size_hint_y=None, height=dp(50), foreground_color=(0, 0, 0, 1))
        self.layout.add_widget(self.username)

        # Password Input
        self.password = TextInput(hint_text='Password', multiline=False, password=True, size_hint_y=None, height=dp(50), foreground_color=(0, 0, 0, 1))
        self.layout.add_widget(self.password)

        # Save Button
        self.save_button = RoundedButton(text='Save', on_press=self.save_account, size_hint_y=None, height=dp(50))
        self.layout.add_widget(self.save_button)

        self.add_widget(self.layout)


    def save_account(self, instance):
        username = self.username.text
        password = self.password.text

        app = App.get_running_app()
        try:
            app.cursor.execute('''
                INSERT INTO users (username, password) VALUES (?, ?)
            ''', (username, password))
            app.conn.commit()
            print(f'Username: {username}, Password: {password}')
            self.manager.current = 'login'
        except sqlite3.IntegrityError:
            print("Username already exists")


class GameHistoryPopup(Popup):
    def __init__(self, game_name, **kwargs):
        super().__init__(**kwargs)
        self.title = game_name + " History"
        self.size_hint = (None, None)
        self.size = (dp(400), dp(300))

        # Conditional text based on game_name
        if game_name == 'Chowka':
            content = "Chowka is a traditional Indian board game involving strategy and dice rolls."
        elif game_name == 'Pagade':
            content = "Pagade, also known as Pachisi, is a cross and circle board game."
        elif game_name == 'Navakankari':
            content = "Navakankari is a traditional board game played in India with a grid and dice."
        else:
            content = "No history available."

        # Update content to be a plain text box
        self.content_label = Label(text=content, size_hint=(None, None), size=(dp(380), dp(280)), font_name='GameFont', text_size=(dp(380), None))
        self.close_button = RoundedButton(text='Back to Dashboard', size_hint=(None, None), size=(dp(150), dp(50)))
        self.close_button.bind(on_press=self.dismiss)

        self.layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        self.layout.add_widget(self.content_label)
        self.layout.add_widget(self.close_button)

        self.add_widget(self.layout)


class DashboardScreen(Screen):
    def build(self):
        self.clear_widgets()  # Clear any existing widgets

        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        # Background Image
        self.add_widget(Image(source='assets/background.jpg', allow_stretch=True, keep_ratio=False))  # Background imag

        # Centered layout for game history list
        self.center_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        self.games_list = BoxLayout(orientation='vertical', spacing=dp(10), size_hint=(None, None))

        games = ['Chowka', 'Pagade', 'Navakankari']
        for game in games:
            game_label = Label(text=f"[u][ref={game}]{game}[/ref][/u]", markup=True,color=(0, 0, 1, 1),font_name='GameFont',font_size=dp(17))
            game_label.bind(on_ref_press=lambda instance, ref: self.show_game_history(ref))
            self.games_list.add_widget(game_label)


        self.center_layout.add_widget(self.games_list)

        self.layout.add_widget(RoundedLabel(text='History of Games', font_size=dp(22), font_name='GameFont'))
        self.layout.add_widget(self.center_layout)

        self.layout.add_widget(RoundedLabel(text='Leaderboard', font_size=dp(20), font_name='GameFont'))
        # Dummy data for leaderboard
        self.leaderboard = [
            {'name': 'Rama', 'W': 10, 'L': 5, 'D': 0, 'NR': 0},
            {'name': 'Bheema', 'W': 8, 'L': 2, 'D': 1, 'NR': 0},
            {'name': 'Soma', 'W': 5, 'L': 3, 'D': 2, 'NR': 0},
            {'name': 'Sita', 'W': 6, 'L': 2, 'D': 0, 'NR': 0}
        ]

        for player in self.leaderboard:
            self.layout.add_widget(RoundedLabel(text=f"{player['name']}: W: {player['W']}, L: {player['L']}, D: {player['D']}, NR: {player['NR']}", font_name='GameFont', font_size=dp(20)))


        self.buttons_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.create_game_button = RoundedButton(text='Create Game', on_press=self.goto_create_game)
        self.player_details_button = RoundedButton(text='Player Details', on_press=self.goto_player_details)
        self.buttons_layout.add_widget(self.create_game_button)
        self.buttons_layout.add_widget(self.player_details_button)

        self.layout.add_widget(self.buttons_layout)
        self.add_widget(self.layout)

    def show_game_history(self, game_name):
        popup = GameHistoryPopup(game_name)
        popup.open()

    def goto_create_game(self, instance):
        self.manager.current = 'create_game'

    def goto_player_details(self, instance):
        self.manager.current = 'player_details'


class PlayerDetailsScreen(Screen):
    def build(self):
        self.clear_widgets()
        self.layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Background Image
        self.add_widget(Image(source='assets/background.jpg', allow_stretch=True, keep_ratio=False))  # Background image

        # Player Stats
        self.layout.add_widget(RoundedLabel(text='Player Stats', font_size=dp(20), font_name='GameFont', size_hint_y=None, height=dp(40)))

        # Player Stats Image
        player_stats_image = Image(source='assets/player-stats.jpeg')
        self.layout.add_widget(player_stats_image)

        self.layout.add_widget(RoundedLabel(text='Total Wins: 127', font_size=dp(20), font_name='GameFont', size_hint_y=None, height=dp(40)))

        self.layout.add_widget(RoundedLabel(text='Total Losses: 78', font_size=dp(20), font_name='GameFont', size_hint_y=None, height=dp(40)))

        self.layout.add_widget(RoundedLabel(text='Player Rank: 6238', font_size=dp(20), font_name='GameFont', size_hint_y=None, height=dp(40)))

         # Horizontal BoxLayout for buttons
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50), size_hint_x=1)

        # Back button to go to the dashboard
        self.back_button = RoundedButton(text='Back to Dashboard', size_hint=(1, None), height=dp(50), on_press=self.goto_dashboard)
        button_layout.add_widget(self.back_button)

        #delete profile button
        self.delete_button = RoundedButton(text='Delete Profile', size_hint=(1, None), height=dp(50), on_press=self.goto_dashboard)
        self.delete_button.background_color = (1, 0, 0, 1)  # Red color
        button_layout.add_widget(self.delete_button)

        self.layout.add_widget(button_layout)

        self.add_widget(self.layout)

    def _update_bg(self, instance, value):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def goto_dashboard(self, instance):
        self.manager.current = 'dashboard'


class CreateGameScreen(Screen):
    def build(self):
        self.clear_widgets()
        self.layout = GridLayout(cols=1, padding=dp(10), spacing=dp(10))

        # Background Image
        self.add_widget(Image(source='assets/background.jpg', allow_stretch=True, keep_ratio=False))  # Background image

        self.layout.add_widget(RoundedLabel(text='Select Your Game', font_size=dp(20), font_name='GameFont'))
        self.game_options = ['Chowkabara', 'Pagade', 'Navakankari', 'Tambola']
        self.game_selector = Spinner(text='Select a game', values=self.game_options, size_hint_y=None, height=dp(50))
        self.layout.add_widget(self.game_selector)

        self.layout.add_widget(RoundedLabel(text='Mode', font_size=dp(20), font_name='GameFont'))
        self.mode_options = ['Casual', 'Arena', 'Competitive']
        self.mode_selector = Spinner(text='Select a mode', values=self.mode_options, size_hint_y=None, height=dp(50))
        self.layout.add_widget(self.mode_selector)

        self.layout.add_widget(RoundedLabel(text='Add Players', font_size=dp(20), font_name='GameFont'))
        self.players = Spinner(text='Select number of players', values=[str(i) for i in range(1, 7)], size_hint_y=None, height=dp(50))
        self.layout.add_widget(self.players)

        self.save_button = RoundedButton(text='Save', on_press=self.save_game, size_hint_y=None, height=dp(50))
        self.layout.add_widget(self.save_button)

        self.add_widget(self.layout)

    def save_game(self, instance):
        selected_game = self.game_selector.text
        selected_mode = self.mode_selector.text

        app = App.get_running_app()
        username = app.username  # Access the username attribute
        
        if username:  # Check if the username is set
            app.cursor.execute('''INSERT INTO Games (save_game, mode, players, username) 
                      VALUES (?, ?, ?, ?)''', (save_game, mode, players, username))
            app.conn.commit()

            app.selected_game = selected_game
            app.selected_mode = selected_mode
            self.manager.current = 'game_session'
        else:
            # Handle the case where username is not set (optional)
            print("Error: Username is not set")


class GameSessionScreen(Screen):
    def build(self):
        self.clear_widgets()
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        # Background Image
        self.add_widget(Image(source='assets/background.jpg', allow_stretch=True, keep_ratio=False))

        self.layout.add_widget(RoundedLabel(text='Game Session', font_size=dp(20), font_name='GameFont', size_hint_y=None, height=dp(40)))

        self.game_mode_label = RoundedLabel(text='', font_size=dp(20), font_name='GameFont', size_hint_y=None, height=dp(40))
        self.layout.add_widget(self.game_mode_label)

        self.chess_board_image = Image(source='')
        self.layout.add_widget(self.chess_board_image)

        self.controls = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.pause_button = RoundedButton(text='Pause', on_press=self.pause_game)
        self.back_button = RoundedButton(text='Back', on_press=self.goto_dashboard)
        self.controls.add_widget(self.pause_button)
        self.controls.add_widget(self.back_button)

        self.layout.add_widget(self.controls)
        self.add_widget(self.layout)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        selected_game = app.selected_game.lower()
        if selected_game in ['chowkabara', 'pagade', 'navakankari', 'tambola']:
            self.chess_board_image.source = f'assets/{selected_game}.jpg'
        self.game_mode_label.text = app.selected_mode

    ''' def on_pre_enter(self, *args):
            app = App.get_running_app()
            user_id = 1  # Retrieve this dynamically based on the logged-in user
            games = get_user_games(user_id)
        # Use 'games' to update the screen '''

    def pause_game(self, instance):
        pause_popup = Popup(title='Game Paused', size_hint=(0.8, 0.5))

        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        layout.add_widget(RoundedLabel(text='Game Status: Paused', font_size=dp(20), font_name='GameFont'))
        layout.add_widget(RoundedLabel(text='Player Points: 100', font_size=dp(20), font_name='GameFont'))
        layout.add_widget(RoundedLabel(text='Minutes Since Started: 10', font_size=dp(20), font_name='GameFont'))

        resume_button = RoundedButton(text='Resume Game', size_hint_y=None, height=dp(50), on_press=pause_popup.dismiss)
        layout.add_widget(resume_button)

        pause_popup.content = layout
        pause_popup.open()

    def goto_dashboard(self, instance):
        self.manager.current = 'dashboard'


class TollugattiApp(App):
    username = StringProperty('')
    def build(self):
        self.sm = ScreenManager()
        self.conn = sqlite3.connect('sqlite/tollugatti.db')
        self.cursor = self.conn.cursor()
        self.username = ''  # Initialize the username attribute
        self.login_screen = LoginScreen(name='login')
        self.dashboard_screen = DashboardScreen(name='dashboard')
        self.create_game_screen = CreateGameScreen(name='create_game')
        self.player_details_screen = PlayerDetailsScreen(name='player_details')
        self.game_session_screen = GameSessionScreen(name='game_session')
        self.create_account_screen = CreateAccountScreen(name='create_account')

        self.sm.add_widget(self.login_screen)
        self.sm.add_widget(self.dashboard_screen)
        self.sm.add_widget(self.create_game_screen)
        self.sm.add_widget(self.player_details_screen)
        self.sm.add_widget(self.game_session_screen)
        self.sm.add_widget(self.create_account_screen)

        self.login_screen.build()
        self.dashboard_screen.build()
        self.create_game_screen.build()
        self.player_details_screen.build()
        self.game_session_screen.build()
        self.create_account_screen.build()

        return self.sm

        def set_username(self, value):
            if value is not None:
                self.username = value
            else:
                self.username = ''

        #close db after exit
        def on_stop(self):
            self.conn.close()


if __name__ == '__main__':
    TollugattiApp().run()
