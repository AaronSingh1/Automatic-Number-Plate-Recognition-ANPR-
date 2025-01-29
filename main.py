import os
import win10toast  # For notification
import datetime
from tkinter import *  # For GUI
from twilio.rest import Client  # For message sending
import easyocr  # For extracting text from the image
import cv2  # For computer vision
from PIL import ImageTk, Image  # Image compressor

# Twilio credentials (hardcoded or use environment variables securely)
sid = "ACf76343c2c2b30e01ea171d443a3575b8"  # Your Twilio SID
auttoken = "09cb48041e1b8f5f75dbdef39ac2970e"  # Your Twilio Auth Token
twilio_phone_number = "+18312650893"  # Your Twilio phone number

# Function to send E-Challan
def send_e_challan(name, no, num):
    # Generate the message to send
    message = msg(name, no)
    
    try:
        # Initialize the Twilio client
        cl = Client(sid, auttoken)
        
        # Send the message
        cl.messages.create(
            body=message,  # Message content
            from_=twilio_phone_number,  # Your Twilio phone number
            to=num  # Recipient phone number (ensure it's in international format, e.g. +91XXXXXXXXXX)
        )
        
        print("Message sent successfully!")

        # Show a notification about the success
        toaster = win10toast.ToastNotifier()
        toaster.show_toast("E-Challan", "The E-Challan has been successfully sent.", duration=5)
    
    except Exception as e:
        print(f"Error sending message: {e}")

# Function to create a fine message
def msg(Owner, vehicle_no):
    date_today = datetime.date.today()
    time_today = datetime.datetime.now().strftime("%H:%M:%S")
    
    return (
        f"Dear {Owner},\nThis is to inform you that your vehicle {vehicle_no} has been found parked in the wrong parking zone."
        f"\nOffense Date: {date_today}, Time: {time_today}\n"
        f"Location: XXdelXX\n"
        f"According to the Motor Vehicles Act, 1988, Section 48, Clause 8C, you must pay a fine."
        f"\nFine Amount: INR 1000\nDue Date: 27-05-2023\nPayment: Online/Offline"
        f"\nFailure to pay will result in additional fines or vehicle impoundment."
        f"\nTo appeal before 25-05-2023, contact RTO: +18006478965 or mhtrrto@gov.in.\n"
        f"Ministry of Transport"
    )

# GUI Function
def window(name, no, state, num):  
    # Initialize the root window
    root = Tk()
    root.config(bg="lightblue")
    root.geometry('1500x650')
    root.title("Team Immortals ANPR")

    label_0 = Label(root, text="Team Immortals ANPR", width=20, font=("bold", 35), bg="yellow", fg="red")
    label_0.place(x=620, y=5)

    labels = [("Name", name, "orange"), ("Vehicle No.", no, "white"), ("Area", state, "green"), ("Phone No.", num, "orange")]
    y_positions = [150, 220, 280, 350]

    for i, (text, value, color) in enumerate(labels):
        Label(root, text=text, width=20, font=("bold", 25), bg=color).place(x=570, y=y_positions[i])
        Label(root, text=value, font="bold 25").place(x=1000, y=y_positions[i])

    # Load the saved image for the GUI
    img = Image.open("C:/Users/aaron/OneDrive/Desktop/git/Automatic-Number-Plate-Recognition-ANPR-/scanned_img_0.jpg")
    img_new = img.resize((450, 350))
    image = ImageTk.PhotoImage(img_new)
    Label(root, image=image).place(x=20, y=90)

    root.mainloop()

# Dictionary for State Identification
states_dict = {
    "AP": "Andhra Pradesh", "AR": "Arunachal Pradesh", "AS": "Assam", "BR": "Bihar", "CG": "Chhattisgarh",
    "GA": "Goa", "GJ": "Gujarat", "HR": "Haryana", "HP": "Himachal Pradesh", "JH": "Jharkhand",
    "KA": "Karnataka", "KL": "Kerala", "DL": "Delhi", "MP": "Madhya Pradesh", "MH": "Maharashtra",
    "MN": "Manipur", "ML": "Meghalaya", "MZ": "Mizoram", "NL": "Nagaland", "OD": "Odisha",
    "PB": "Punjab", "RJ": "Rajasthan", "SK": "Sikkim", "TN": "Tamil Nadu", "TS": "Telangana",
    "TR": "Tripura", "UP": "Uttar Pradesh", "WB": "West Bengal"
}

# Haar Cascade for Number Plate detection
harcascade = "C:/Users/aaron/OneDrive/Desktop/git/Automatic-Number-Plate-Recognition-ANPR-/haarcascade_russian_plate_number.xml"

cap = cv2.VideoCapture(0)  # Start Camera
cap.set(3, 640)  # width
cap.set(4, 480)  # height

min_area = 500
count = 0

os.makedirs("plates", exist_ok=True)  # Ensure directory exists

while True:
    success, img = cap.read()
    plate_cascade = cv2.CascadeClassifier(harcascade)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)

    for (x, y, w, h) in plates:
        if w * h > min_area:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, "Number Plate", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)
            img_roi = img[y: y + h, x:x + w]
            cv2.imshow("Number Plate", img_roi)

    cv2.imshow("INPUT FEED", img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):  # Save when 's' is pressed
        print("Saving captured plate image...")

        if 'img_roi' not in locals():
            print("No number plate detected, try again.")
            continue

        plate_path = f"plates/scanned_img_{count}.jpg"
        cv2.imwrite(plate_path, img_roi)
        print(f"Image saved at {plate_path}")

        # Perform OCR
        reader = easyocr.Reader(['en'])
        result = reader.readtext(plate_path)
        print(f"OCR Result: {result}")

        if result:
            number_plate = result[0][1]
            state = number_plate[:2]
            state_name = states_dict.get(state, "Unknown State")

            print(f"Vehicle Number: {number_plate}")
            print(f"Vehicle Registration Area: {state_name}")

            owner_name = "MR. XXDXJX"
            phone_number = "+918630065185"

            # Show GUI
            window(owner_name, number_plate, state_name, phone_number)

            # Twilio message sending
            send_e_challan(owner_name, number_plate, phone_number)
            
            count += 1
        else:
            print("OCR failed to read the number plate. Try again.")
        
    elif key == ord('q'):  # Quit when 'q' is pressed
        break

cv2.destroyAllWindows()
