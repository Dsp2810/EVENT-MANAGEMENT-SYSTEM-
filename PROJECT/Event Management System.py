import pandas as pd
import gradio as gr
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import tempfile

# Load Data from Excel File
def load_data():
    # This needs to be hosted or uploaded in a place that's accessible on the server.
    sports_file_path = "spoural_sports.xlsx"  # assuming file uploaded or accessible via URL
    sports_df = pd.read_excel(sports_file_path)
    
    sports_participants = {}
    
    for _, row in sports_df.iterrows():
        if 'Department' in sports_df.columns and 'Sport' in sports_df.columns:
            participant_tuple = (row['Name'], row['Contact No.'], row['Department'], 'Not Attended')
            sports_participants.setdefault(row['Sport'], []).append(participant_tuple)
        else:
            print("Warning: Missing columns in sports data.")
    
    return sports_participants

sports_participants = load_data()

def display_participants(event_name):
    participants = sports_participants.get(event_name, [])
    if participants:
        return pd.DataFrame(participants, columns=["Name", "Contact No.", "Department", "Participation Status"])
    return "No participants found for this event."

def search_participant(name):
    results = []
    for event, participants in sports_participants.items():
        for participant in participants:
            if name.lower() in participant[0].lower():
                results.append([event] + list(participant))
    
    if results:
        return pd.DataFrame(results, columns=["Event", "Name", "Contact No.", "Department", "Participation Status"])
    
    return "Participant not found."

def mark_attendance(name, status):
    for event, participants in sports_participants.items():
        for i, participant in enumerate(participants):
            if name.lower() == participant[0].lower():
                updated_participant = (participant[0], participant[1], participant[2], status)
                participants[i] = updated_participant
                return f"✅ {participant[0]}'s attendance updated to '{status}' in {event}."
    
    return "❌ Participant not found."

def summary():
    sports_summary = {event: len(participants) for event, participants in sports_participants.items()}
    return f"🏅 **Sports Events Summary**: {sports_summary}"

def generate_pdf():
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(pdf_file.name, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(200, 750, "📄 Event Participation Report")
    
    y = 720
    c.setFont("Helvetica", 10)
    c.drawString(20, y, "Student Name")
    c.drawString(220, y, "Event")
    c.drawString(335, y, "Contact No.")
    c.drawString(450, y, "Department")
    c.drawString(530, y, "Status")
    
    y -= 20
    for event, participants in sports_participants.items():
        for participant in participants:
            c.drawString(20, y, participant[0])
            c.drawString(225, y, event)
            c.drawString(350, y, str(participant[1]))
            c.drawString(450, y, participant[2])
            c.drawString(530, y, participant[3])
            y -= 20
            if y < 50:
                c.showPage()
                y = 750
    
    c.save()
    return pdf_file.name  # Returning the file path for download

with gr.Blocks() as gui:
    gr.Markdown("# College Sports Event Management System")

    sports_event_name = gr.Dropdown(label="Select Sports Event", choices=list(sports_participants.keys()))
    sports_display_button = gr.Button("Display Participants")
    sports_participants_output = gr.Dataframe(label="Sports Participants")
    sports_display_button.click(display_participants, inputs=sports_event_name, outputs=sports_participants_output)
    
    search_name = gr.Textbox(label="Search Participant")
    search_button = gr.Button("Search")
    search_output = gr.Dataframe(label="Search Results")
    search_button.click(search_participant, inputs=search_name, outputs=search_output)

    mark_name = gr.Textbox(label="Participant Name")
    mark_status = gr.Dropdown(label="Attendance Status", choices=["Attended", "Not Attended"])
    mark_button = gr.Button("Mark Attendance")
    mark_output = gr.Textbox(label="Attendance Result")
    mark_button.click(mark_attendance, inputs=[mark_name, mark_status], outputs=mark_output)

    summary_button = gr.Button("Show Summary")
    summary_output = gr.Textbox(label="Summary")
    summary_button.click(summary, outputs=summary_output)

    pdf_button = gr.Button("Generate PDF Report")
    pdf_output = gr.File(label="Download PDF")
    pdf_button.click(generate_pdf, outputs=pdf_output)

gui.launch(share=True)
