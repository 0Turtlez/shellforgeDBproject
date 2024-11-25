from io import BytesIO
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import webbrowser
import requests
import mysql.connector

connection = None
cursor = None

# Function to establish database connection
def create_db_connection(username, password):
    try:
        conn = mysql.connector.connect(
            host="localhost",  # Change to your server's IP if remote
            user=username,
            password=password,
            database="shellforgeDB"
        )
        return conn, None  # Return connection and no error
    except mysql.connector.Error as err:
        return None, str(err)  # Return None and the error message

# Function to handle login
def handle_login():
    global connection, cursor  # Declare global variables to modify them
    username = username_entry.get()
    password = password_entry.get()

    # Attempt to connect to the database with provided credentials
    connection, error = create_db_connection(username, password)
    if connection:
        cursor = connection.cursor()  # Initialize the cursor
        login_window.destroy()        # Close the login window
        open_main_app()               # Launch the main application
    else:
        messagebox.showerror("Login Failed", f"Error: {error}")  # Show error message

# Function to open the main application
def open_main_app():
    global cursor

    def open_new_window(data):
        # Extract data variables
        modId = data[0]
        mod_name = data[12]
        download_count = data[6]
        summary = data[16]

        # Fetch the logo
        query = "SELECT * FROM logo WHERE modDataId = %s"
        cursor.execute(query, (modId,))
        logo_data = cursor.fetchone()
        url = logo_data[3] if logo_data else None

        query = "SELECT * FROM LINKS WHERE modDataId = %s"
        cursor.execute(query, (modId,))
        link_data = cursor.fetchone()
        mod_url = link_data[3]

        # Load the image
        try:
            if url:
                response = requests.get(url)
                response.raise_for_status()
                img_data = BytesIO(response.content)
                img = Image.open(img_data)
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                tk_image = ImageTk.PhotoImage(img)
            else:
                raise ValueError("No valid URL found for the image.")
        except Exception as e:
            print(f"Error loading image: {e}")
            tk_image = None

        # Create the new pop-out window
        popout_window = Toplevel(root)
        popout_window.title("Details")
        popout_window.geometry("400x500")

        # Display mod name
        Label(popout_window, text=mod_name, font=("Helvetica", 16)).pack(pady=10)

        # Display image if loaded
        if tk_image:
            img_label = Label(popout_window, image=tk_image)
            img_label.image = tk_image
            img_label.pack(pady=10)
        else:
            Label(popout_window, text="Failed to load image", fg="red").pack(pady=10)

        # Display download count
        Label(popout_window, text=f"Download Count: {download_count}", font=("Helvetica", 12)).pack(pady=5)

        # Display summary
        Label(popout_window, text="Summary:", font=("Helvetica", 12)).pack(pady=5)
        text_widget = Text(popout_window, wrap=WORD, height=10, width=40, font=("Helvetica", 12))
        text_widget.insert(1.0, summary)
        text_widget.config(state=DISABLED)  # Make it read-only
        text_widget.pack(pady=10, anchor="center", expand=True)

        # Add download button
        def open_url():
            if mod_url:
                webbrowser.open(mod_url)

        Button(popout_window, text="Website", command=open_url).pack(pady=20)

    # Main app window
    root = Tk()
    root.title("🐢ShellForge")
    root.geometry("300x500")

    Label(root, text="Mods:").pack(pady=10)

    frame = Frame(root)
    frame.pack(fill=BOTH, expand=True)

    canvas = Canvas(frame)
    scrollbar = Scrollbar(frame, orient=VERTICAL, command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side=RIGHT, fill=Y)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    button_frame = Frame(canvas)

    # Add buttons to the frame
    cursor.execute("SELECT * FROM ModData ORDER BY downloadCount DESC LIMIT 100")
    for row in cursor.fetchall():
        button_text = row[12][:25] + "..." if len(row[12]) > 25 else row[12]
        Button(
            button_frame,
            text=button_text,
            command=lambda data=row: open_new_window(data),
            width=25,
            bg="#d3d3d3",
            fg="black"
        ).pack(pady=5, anchor="center")

    button_frame.update_idletasks()
    canvas.create_window((0, 0), window=button_frame, anchor="nw")
    canvas.configure(scrollregion=canvas.bbox("all"))

    def _on_mousewheel(event):
        canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    root.mainloop()


# Login window
login_window = Tk()
login_window.title("Login")
login_window.geometry("300x200")

Label(login_window, text="Username:").pack(pady=5)
username_entry = Entry(login_window)
username_entry.pack(pady=5)

Label(login_window, text="Password:").pack(pady=5)
password_entry = Entry(login_window, show="*")
password_entry.pack(pady=5)

Button(login_window, text="Login", command=handle_login).pack(pady=20)

login_window.mainloop()

# Close connection on exit
if connection:
    connection.close()
