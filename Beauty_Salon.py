import tkinter
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import glob
from datetime import datetime,timedelta
from tkcalendar import Calendar

class Services:
    def __init__(self, name, masters, schedule=None):
        self.name = name
        self.master = masters
        self.schedule = schedule

    def get_master_filename(self,master):
        return "{}.csv".format(master.replace(" ","_"))

    def book_appointment(self,master, date, time, client_name, phone,service_type):
        filename = self.get_master_filename(master)
        try:
            with open(filename,"a",newline='') as file:
                writer = csv.writer(file)
                writer.writerow([date.strftime("%Y-%m-%d"), time, service_type, client_name, phone])

            sort_csv_by_datetime(filename)
            print("Appointment booked for ",master, "on ",date.strftime("%Y-%m-%d"), "at ", time,"Saved in ",filename)

            self.update_beauty_bar()
        except FileNotFoundError:
            pass  # no booking for this master yet

    def get_booked_hours(self,master, date):
        filename = self.get_master_filename(master)
        booked_hours=[]
        try:
            with open(filename,"r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) < 2:  # Ensure the row has at least date and time
                        continue
                    booked_date, booked_time, *_ = row
                    if booked_date == date.strftime("%Y-%m-%d"):
                        booked_hours.append(booked_time)
        except FileNotFoundError:
            print("No bookings found for "+master+".") #no booking for this master yet
        return booked_hours

    def update_beauty_bar(self):
        master_files_pattern = "Master_*.csv"
        output_file = "Beauty_Bar.csv"

        #Gather data from all Master files
        combined_data = []
        try:

            for file in glob.glob(master_files_pattern):
                master_name = file.replace("Master_", "").replace(".csv", "").replace("_", " ")
                with open(file, "r") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if len(row) < 2:  # Ensure the row has at least date and time
                            continue
                        combined_data.append(row+[master_name])

            #Sort the combined data by Date and Time
            def sort_key(row):
                date_str, time_str, *_ = row
                datetime_obj = datetime.strptime(date_str+" " + time_str,"%Y-%m-%d %I:%M %p")
                return datetime_obj

            sorted_data = sorted(combined_data, key=sort_key)

            #Write sorted data into the Beauty_Bar.csv file
            with open(output_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Time", "Service Type", "Client Name", "Phone", "Master"])
                writer.writerows(sorted_data)

            print("New appointment has been saved into Beauty_Bar.csv")
        except FileNotFoundError:
            print("File Beauty_Bar.csv has not found")

    def show_available_hours(self, master, date):
        booked_hours = self.get_booked_hours(master,date)
        return [hour for hour, available in self.schedule.items() if available and hour not in booked_hours]

    def highlight_weekends(self,calendar, mindate, maxdate):
        current_date = mindate
        while current_date <= maxdate:
            # Check if the current day is a Saturday (5) or Sunday (6)
            if current_date.weekday() in (5, 6):
                calendar.calevent_create(current_date, 'Weekend', 'weekend')
            current_date += timedelta(days=1)
        calendar.tag_config('weekend', background='lightgray', foreground='red')

    def highlight_today(self, calendar):
        today = datetime.today().date()
        calendar.calevent_create(today, 'Today', 'today')
        calendar.tag_config('today', foreground='blue', background='lightyellow')

    def open_new_window(self,service_type):
        for widget in frame.winfo_children():
            widget.destroy()

        go_back_button = tkinter.Button(frame, text="Main Menu", command=lambda:go_back())
        go_back_button.grid(row=0, column=0)

        service_label = tkinter.Label(frame, text="Select Your "+service_type+ " Master and Preferable Time ")
        service_label.grid(row=0, column=1,columnspan=3, padx=10, pady=10, sticky='n')

        service_type_label = tkinter.Label(frame, text="Choose Service Type:")
        service_type_label.grid(row=1, column=0, padx=10, pady=10)

        service_options = [f"{service} - ${price}" for service, price in self.prices.items()]
        service_type_combo = ttk.Combobox(frame, values=service_options)
        service_type_combo.grid(row=1, column=1, padx=10, pady=10)
        service_type_combo.current(0)

        master_label = tkinter.Label(frame, text="Choose Master:")
        master_label.grid(row=2, column=0, padx=10, pady=10)

        master_combo = ttk.Combobox(frame, values=self.master)
        master_combo.grid(row=2, column=1, padx=10, pady=10)
        master_combo.current(0)

        date_label = tkinter.Label(frame, text="Choose Date:")
        date_label.grid(row=3, column=0, padx=10, pady=10)

        #get first and last day of the month
        today = datetime.today()
        next_month = today +  timedelta(days=30)

        calendar = Calendar(
            frame,
            selectmode='day',
            date_pattern = 'yyyy-mm-dd',
            mindate=datetime.today(),
            maxdate=next_month,
            showweeknumbers=False,  # Hides the week numbers
            firstweekday='monday',
            locale = 'en_US'
        )
        calendar.grid(row=3,column=1,padx=10,pady=10)

        self.highlight_weekends(calendar, datetime.today(), next_month)
        self.highlight_today(calendar)

        hour_label = tkinter.Label(frame, text="Choose Time:")
        hour_label.grid(row=4, column=0, padx=10, pady=10)

        hours_combo = ttk.Combobox(frame)
        hours_combo.grid(row=4, column=1, padx=10, pady=10)

        def update_available_hours(event):
            selected_date = datetime.strptime(calendar.get_date(), '%Y-%m-%d')

            if selected_date.weekday() in (5,6):
                hours_combo['values'] = []
                messagebox.showinfo("Unavailable","Bookings are not available on weekends.")
            else:
                selected_master = master_combo.get()
                available_hours = self.show_available_hours(selected_master, selected_date)

                if available_hours:
                    hours_combo["values"] = available_hours
                    hours_combo.current(0)
                else:
                    hours_combo['values'] = []
                    messagebox.showinfo("Unavailable","No available hours for the selected day.")

        calendar.bind("<<CalendarSelected>>", update_available_hours)

        # name
        name_label = tkinter.Label(frame, text="Your Name:")
        name_label.grid(row=5, column=0, padx=10, pady=10)
        name_entry = tkinter.Entry(frame)
        name_entry.grid(row=5, column=1, padx=10, pady=10)

        def format_phone_number(P):
            P = ''.join(filter(str.isdigit, P))

            # Format phone number as xxx-xxx-xxxx
            if len(P) <= 3:
                return P
            elif len(P) <= 6:
                return f"{P[:3]}-{P[3:]}"
            elif len(P) <= 10:
                return f"{P[:3]}-{P[3:6]}-{P[6:]}"
            else:
                return f"{P[:3]}-{P[3:6]}-{P[6:10]}"

        def on_keyrelease(event):
            current_value = phone_number_var.get()  # Get current value
            formatted_value = format_phone_number(current_value)  # Format the phone number
            phone_number_var.set(formatted_value)  # Update the variable with formatted value

            phone_number_entry.icursor(len(formatted_value))
        # Set up a StringVar to monitor changes in the phone number Entry
        phone_number_var = tk.StringVar()

        # phone number
        phone_number_label = tkinter.Label(frame, text="Your Phone Number:")
        phone_number_label.grid(row=6, column=0, padx=10, pady=10)
        phone_number_entry = tkinter.Entry(frame, textvariable=phone_number_var)
        phone_number_entry.grid(row=6, column=1, padx=10, pady=10)

        phone_number_entry.bind("<KeyRelease>", on_keyrelease)

        def go_back():
            for widget in frame.winfo_children():
                widget.destroy()

            empty_label = tkinter.Label(frame, text=" ")
            empty_label.grid(row=0, column=0)

            book_label = tkinter.Label(frame, text="Book an appointment:")
            book_label.grid(row=1, column=0)

            empty_label = tkinter.Label(frame, text=" ")
            empty_label.grid(row=2, column=0)

            hair_button = tkinter.Button(frame, text='Hair Services', width=20, height=2, command=lambda: hair_service.open_new_window("Hair Services"))
            hair_button.grid(row=3, column=0)

            nails_button = tkinter.Button(frame, text='Nail Services', width=20, height=2, command=lambda: nail_service.open_new_window("Nail Services"))
            nails_button.grid(row=4, column=0)

            makeup_button = tkinter.Button(frame, text='Makeup Services', width=20, height=2, command=lambda: makeup_service.open_new_window("Makeup Services"))
            makeup_button.grid(row=5, column=0)

            empty_label = tkinter.Label(frame, text=" ")
            empty_label.grid(row=6, column=0)

            empty_label = tkinter.Label(frame, text=" ")
            empty_label.grid(row=7, column=0)

            empty_label = tkinter.Label(frame, text=" ")
            empty_label.grid(row=8, column=0)

            empty_label = tkinter.Label(frame, text=" ")
            empty_label.grid(row=9, column=0)

            review_label = tkinter.Label(frame, text="Leave a review:")
            review_label.grid(row=13, column=0)

            global review_entry
            review_entry = tkinter.Text(frame, width=30, height=4)
            review_entry.grid(row=14, column=0, padx=10, pady=10)

            submit_review_button = tkinter.Button(frame, text='Submit review', width=20, height=2, command=submit_review)
            submit_review_button.grid(row=15, column=0)

            view_review_button = tkinter.Button(frame, text='View Reviews', command=view_reviews, font=("Arial", 14))
            view_review_button.grid(row=16, column=0)

        def book_and_save(name_entry, phone_number_entry, master_combo, calendar, hours_combo, service_type_combo):
            name = name_entry.get().strip()
            phone = phone_number_entry.get().strip()
            master = master_combo.get()
            selected_date = datetime.strptime(calendar.get_date(),'%Y-%m-%d')
            time = hours_combo.get()
            service_type = service_type_combo.get()

            if name and phone and time and master and selected_date:
                self.book_appointment(master, selected_date, time, name, phone, service_type)
                messagebox.showinfo(
                    "Appointment Booked",
                    "Appointment Booked\n\n• Service Type - " + service_type + "\n• Date - "+ selected_date.strftime("%Y-%m-%d") +"\n• Master's Name - " + master + "\n• Time - " + time)
                go_back()
            else:
                messagebox.showerror("Booking Error",
                                     "Please make sure you enter all required information.")

        # book appointment button
        book_button = tk.Button(frame, text="Book Appointment", command=lambda: book_and_save(name_entry, phone_number_entry, master_combo, calendar, hours_combo, service_type_combo))
        book_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

def sort_csv_by_datetime(filename):
    try:
        with open(filename, "r") as file:
            reader = csv.reader(file)
            rows = list(reader)
        if not rows:
            print("No data found in "+filename+".")
            return
        rows.sort(key=lambda row: datetime.strptime(row[0] + " " + row[1], "%Y-%m-%d %I:%M %p"))
        with open(filename, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)  # Write the sorted rows

    except Exception as e:
        print("Error while sorting"+filename+": ",e)

class HairService(Services):
    def __init__(self):
        super().__init__("Hair", masters=["Master Mia", "Master Ana"])
        self.prices = {
            "Hair Cut": 50,
            "Hair Color": 90,
            "Hair Styling": 70,
        }
        self.schedule = {
        "09:00 AM":True,
        "10:00 AM": True,
        "11:00 AM": True,
        "12:00 PM": True,
        "02:00 PM": True,
        "03:00 PM": True,
        "04:00 PM": True,
        "05:00 PM": True,
    }
    def get_service_options(self):
        return list(self.prices.items())

class NailService(Services):
    def __init__(self):
        super().__init__("Nail", masters=["Master Nina", "Master Andrew"])
        self.prices = {
            "Manicure": 50,
            "Pedicure": 70,
        }
        self.schedule = {
            "08:00 AM": True,
            "09:00 AM": True,
            "10:00 AM": True,
            "11:00 AM": True,
            "12:00 PM": True,
            "02:00 PM": True,
            "03:00 PM": True,
            "04:00 PM": True,
        }
    def get_service_options(self):
        return list(self.prices.keys())

class MakeupService(Services):
    def __init__(self):
        super().__init__("Makeup", masters=["Master Robert"])
        self.prices = {
            "Day Makeup": 60,
            "Evening Makeup": 80,
            "Bridal Makeup": 150,
        }
        self.schedule = {
            "11:00 AM": True,
            "12:00 PM": True,
            "02:00 PM": True,
            "03:00 PM": True,
            "04:00 PM": True,
            "05:00 PM": True,
            "06:00 PM": True,
            "07:00 PM": True,
        }
    def get_service_options(self):
        return list(self.prices.keys())

class Review:
    def __init__(self, file_name):
        self.file_name = file_name
        self.reviews = []
        self.load_reviews()

    def load_reviews(self):
        try:
            with open(self.file_name, "r") as file:
                self.reviews = file.readlines()
        except FileNotFoundError:
            self.reviews = []

    def add_review(self, review):
        if review.strip():
            self.reviews.append(review.strip())
            with open(self.file_name, "a") as file:
                file.write(review.strip() + "\n")
            return True
        return False

    def display_reviews(self):
        if not self.reviews:
            return "No reviews available."
        return "\n\n".join(["• "+review for review in self.reviews])


review_manager = Review("reviews.txt")


def submit_review():
    review_text = review_entry.get("1.0", tk.END).strip()
    if review_manager.add_review(review_text):
        messagebox.showinfo("Review Submitted", "Your review has been submitted successfully!")
        review_entry.delete("1.0", tk.END)
        view_reviews()
    else:
        messagebox.showerror("Error", "Please enter a review before submitting.")


def view_reviews():
    # Create a new window to display reviews
    review_manager.load_reviews()
    review_window = tk.Toplevel(window)
    review_window.title("Reviews")
    review_window.geometry("600x600")

    reviews_text = tk.Text(review_window, wrap=tk.WORD)
    reviews_text.insert("1.0", review_manager.display_reviews())
    reviews_text.config(state=tk.DISABLED)  # Make the text box read-only
    reviews_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

hair_service = HairService()
nail_service = NailService()
makeup_service = MakeupService()

window=tkinter.Tk()
window.title('Beauty Bar')
window.geometry("550x550")

frame=tkinter.Frame(window)
frame.pack()

empty_label=tkinter.Label(frame,text=" ")
empty_label.grid(row=0,column=0)

book_label=tkinter.Label(frame,text="Book an appointment:")
book_label.grid(row=1,column=0)

empty_label=tkinter.Label(frame,text=" ")
empty_label.grid(row=2,column=0)

hair_button=tkinter.Button(frame, text='Hair Services',width=20,height=2,command=lambda:hair_service.open_new_window("Hair Services") )
hair_button.grid(row=3,column=0)

nails_button=tkinter.Button(frame, text='Nail Services',width=20,height=2,command=lambda:nail_service.open_new_window("Nail Services") )
nails_button.grid(row=4,column=0)

makeup_button=tkinter.Button(frame, text='Makeup Services',width=20,height=2,command=lambda:makeup_service.open_new_window("Makeup Services") )
makeup_button.grid(row=5,column=0)

empty_label=tkinter.Label(frame,text=" ")
empty_label.grid(row=6,column=0)

empty_label=tkinter.Label(frame,text=" ")
empty_label.grid(row=7,column=0)

empty_label=tkinter.Label(frame,text=" ")
empty_label.grid(row=8,column=0)

empty_label=tkinter.Label(frame,text=" ")
empty_label.grid(row=9,column=0)

review_label=tkinter.Label(frame,text="Leave a review:")
review_label.grid(row=13,column=0)

review_entry = tkinter.Text(frame, width=30,height=4)
review_entry.grid(row=14, column=0, padx=10, pady=10)

submit_review_button=tkinter.Button(frame, text='Submit review',width=20,height=2,command=submit_review)
submit_review_button.grid(row=15,column=0)

view_review_button=tkinter.Button(frame, text='View Reviews',command=view_reviews, font=("Arial", 14))
view_review_button.grid(row=16,column=0)




window.mainloop()