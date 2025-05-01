import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Memory for user session data
session_data = {}

# Full chatbot menu structure
MENU_OPTIONS = {
    "main": {
        "title": "Welcome to Festiva Event Management! How may I assist you today?",
        "options": [
            {"id": "1", "text": "Book an Event", "next": "event_types"},
            {"id": "2", "text": "Customer Support", "next": "support_menu"},
            {"id": "3", "text": "About Festiva", "response": "Festiva is a premium event management company specializing in creating memorable experiences for all occasions. From weddings to corporate events, we've got you covered with our range of customizable packages."}
        ]
    },
    "event_types": {
        "title": "What type of event are you planning?",
        "options": [
            {"id": "1", "text": "Wedding", "next": "wedding_packages"},
            {"id": "2", "text": "Corporate Event", "next": "corporate_packages"},
            {"id": "3", "text": "Birthday", "next": "birthday_packages"},
            {"id": "4", "text": "Conference", "next": "conference_packages"},
            {"id": "5", "text": "Rice Ceremony", "next": "rice_ceremony_packages"},
            {"id": "6", "text": "Music Concert", "next": "concert_packages"},
            {"id": "7", "text": "Back to Main Menu", "next": "main"}
        ]
    },
    "wedding_packages": {
        "title": "Select a Wedding Package that suits your needs:",
        "options": [
            {"id": "1", "text": "Royal Wedding - $5,000", "next": "royal_wedding_details"},
            {"id": "2", "text": "Classic Wedding - $2,500", "next": "classic_wedding_details"},
            {"id": "3", "text": "Intimate Wedding - $1,000", "next": "intimate_wedding_details"},
            {"id": "4", "text": "Back to Event Types", "next": "event_types"}
        ]
    },
    "royal_wedding_details": {
        "title": "Royal Wedding Package - $5,000 (Perfect for grand celebrations)",
        "description": "• Venue for 300 guests\n• Premium catering (5-course meal)\n• Professional photography & videography\n• Floral decorations (premium flowers)\n• Live band performance\n• Wedding planner included\n• Luxury bridal suite",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Wedding Packages", "next": "wedding_packages"}
        ]
    },
    "classic_wedding_details": {
        "title": "Classic Wedding Package - $2,500 (Beautiful traditional celebration)",
        "description": "• Venue for 150 guests\n• Standard catering (3-course meal)\n• Professional photography\n• Basic floral decorations\n• DJ music service\n• Wedding planner\n• Bridal suite",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Wedding Packages", "next": "wedding_packages"}
        ]
    },
    "intimate_wedding_details": {
        "title": "Intimate Wedding Package - $1,000 (Simple and elegant)",
        "description": "• Venue for 50 guests\n• Buffet catering\n• Basic photography\n• Floral decorations\n• Music service\n• Wedding planner\n• Bridal suite",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Wedding Packages", "next": "wedding_packages"}
        ]
    },
    "corporate_packages": {
        "title": "Select a Corporate Event Package:",
        "options": [
            {"id": "1", "text": "Executive Summit - $3,000", "next": "executive_summit_details"},
            {"id": "2", "text": "Business Conference - $1,500", "next": "business_conference_details"},
            {"id": "3", "text": "Team Workshop - $750", "next": "team_workshop_details"},
            {"id": "4", "text": "Back to Event Types", "next": "event_types"}
        ]
    },
    "executive_summit_details": {
        "title": "Executive Summit Package - $3,000 (For high-profile corporate events)",
        "description": "• Conference hall for 200\n• Premium AV equipment\n• Gourmet catering\n• Professional event photography\n• Dedicated event coordinator\n• Branding package",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Corporate Packages", "next": "corporate_packages"}
        ]
    },
    "business_conference_details": {
        "title": "Business Conference Package - $1,500 (Professional business meetings)",
        "description": "• Meeting room for 100\n• Standard AV equipment\n• Buffet lunch\n• Basic event photography\n• Dedicated coordinator\n• Branding package",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Corporate Packages", "next": "corporate_packages"}
        ]
    },
    "team_workshop_details": {
        "title": "Team Workshop Package - $750 (Small team gatherings)",
        "description": "• Meeting room for 30\n• Basic projector\n• Coffee & snacks\n• Photographer\n• Event coordinator\n• Branding",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Corporate Packages", "next": "corporate_packages"}
        ]
    },
    "birthday_packages": {
        "title": "Select a Birthday Package:",
        "options": [
            {"id": "1", "text": "Grand Celebration - $1,200", "next": "grand_celebration_details"},
            {"id": "2", "text": "Family Gathering - $600", "next": "family_gathering_details"},
            {"id": "3", "text": "Kids Party - $300", "next": "kids_party_details"},
            {"id": "4", "text": "Back to Event Types", "next": "event_types"}
        ]
    },
    "grand_celebration_details": {
        "title": "Grand Celebration Package - $1,200 (Luxury birthday experience)",
        "description": "• Venue for 100 guests\n• Themed decorations\n• Premium catering\n• Professional photographer\n• DJ with lighting\n• Custom cake",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Birthday Packages", "next": "birthday_packages"}
        ]
    },
    "family_gathering_details": {
        "title": "Family Gathering Package - $600 (Perfect for family celebrations)",
        "description": "• Venue for 50 guests\n• Basic decorations\n• Buffet catering\n• Professional photographer\n• Music system\n• Standard cake",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Birthday Packages", "next": "birthday_packages"}
        ]
    },
    "kids_party_details": {
        "title": "Kids Party Package - $300 (Fun for the little ones)",
        "description": "• Venue for 25 kids\n• Balloon decorations\n• Snacks & drinks\n• Photographer\n• Music\n• Small cake",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Birthday Packages", "next": "birthday_packages"}
        ]
    },
    "conference_packages": {
        "title": "Select a Conference Package:",
        "options": [
            {"id": "1", "text": "International Conference - $4,500", "next": "international_conference_details"},
            {"id": "2", "text": "Professional Seminar - $2,000", "next": "professional_seminar_details"},
            {"id": "3", "text": "Workshop - $800", "next": "workshop_details"},
            {"id": "4", "text": "Back to Event Types", "next": "event_types"}
        ]
    },
    "international_conference_details": {
        "title": "International Conference Package - $4,500 (For large-scale professional events)",
        "description": "• Main hall + 3 breakout rooms\n• Simultaneous translation\n• High-tech AV equipment\n• Full catering service\n• Professional event recording\n• Dedicated support team",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Conference Packages", "next": "conference_packages"}
        ]
    },
    "professional_seminar_details": {
        "title": "Professional Seminar Package - $2,000 (Mid-size professional events)",
        "description": "• Main hall + 1 breakout room\n• Translation services\n• Standard AV equipment\n• Coffee breaks & lunch\n• Event recording\n• Basic support",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Conference Packages", "next": "conference_packages"}
        ]
    },
    "workshop_details": {
        "title": "Workshop Package - $800 (Small professional gatherings)",
        "description": "• Single meeting room\n• Breakout zones\n• Basic projector\n• Coffee breaks\n• Recording\n• Support team",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Conference Packages", "next": "conference_packages"}
        ]
    },
    "rice_ceremony_packages": {
        "title": "Select a Rice Ceremony Package:",
        "options": [
            {"id": "1", "text": "Grand Annaprasana - $1,500", "next": "grand_annaprasana_details"},
            {"id": "2", "text": "Traditional Ceremony - $900", "next": "traditional_ceremony_details"},
            {"id": "3", "text": "Simple Blessing - $500", "next": "simple_blessing_details"},
            {"id": "4", "text": "Back to Event Types", "next": "event_types"}
        ]
    },
    "grand_annaprasana_details": {
        "title": "Grand Annaprasana Package - $1,500 (Traditional grand ceremony)",
        "description": "• Venue for 150 guests\n• Traditional decor & setup\n• Full traditional meal\n• Professional photography\n• Cultural music performance\n• Custom ceremony accessories\n• Event coordinator",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Rice Ceremony Packages", "next": "rice_ceremony_packages"}
        ]
    },
    "traditional_ceremony_details": {
        "title": "Traditional Ceremony Package - $900 (Beautiful traditional celebration)",
        "description": "• Venue for 80 guests\n• Basic traditional decor\n• Light traditional meal\n• Basic photography\n• Music performance\n• Standard accessories\n• Event coordinator",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Rice Ceremony Packages", "next": "rice_ceremony_packages"}
        ]
    },
    "simple_blessing_details": {
        "title": "Simple Blessing Package - $500 (Intimate family ceremony)",
        "description": "• Venue for 30 guests\n• Minimal decor\n• Snacks & drinks\n• Photography\n• Music\n• Basic accessories\n• Coordinator",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Rice Ceremony Packages", "next": "rice_ceremony_packages"}
        ]
    },
    "concert_packages": {
        "title": "Select a Music Concert Package:",
        "options": [
            {"id": "1", "text": "Stadium Concert - $15,000", "next": "stadium_concert_details"},
            {"id": "2", "text": "Concert Hall Event - $7,500", "next": "concert_hall_details"},
            {"id": "3", "text": "Club Performance - $3,000", "next": "club_performance_details"},
            {"id": "4", "text": "Back to Event Types", "next": "event_types"}
        ]
    },
    "stadium_concert_details": {
        "title": "Stadium Concert Package - $15,000 (Large-scale professional production)",
        "description": "• Venue for 5,000+ attendees\n• Professional stage & lighting\n• High-end sound system\n• Backline equipment\n• Full security team\n• Professional video recording\n• Dedicated event manager",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Concert Packages", "next": "concert_packages"}
        ]
    },
    "concert_hall_details": {
        "title": "Concert Hall Event Package - $7,500 (Professional mid-size concert)",
        "description": "• Venue for 1,000 attendees\n• Standard stage & lighting\n• Professional sound system\n• Basic backline\n• Security personnel\n• Video recording\n• Dedicated manager",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Concert Packages", "next": "concert_packages"}
        ]
    },
    "club_performance_details": {
        "title": "Club Performance Package - $3,000 (Small venue musical event)",
        "description": "• Venue for 300 attendees\n• Basic stage setup\n• Standard sound system\n• Backline equipment\n• Security\n• Recording\n• Event manager",
        "options": [
            {"id": "1", "text": "Make Inquiry", "next": "inquiry_form"},
            {"id": "2", "text": "Back to Concert Packages", "next": "concert_packages"}
        ]
    },
    "support_menu": {
    "title": "How can we assist you today? Please choose an option below:",
    "options": [
        {"id": "1", "text": "Event Packages & Services", "next": "event_types"},
        {"id": "2", "text": "Check Booking Status", "next": "booking_status"},
        {"id": "3", "text": "View Payment Methods", "next": "payment_info"},
        {"id": "4", "text": "Understand Cancellation Policy", "next": "cancellation_info"},
        {"id": "5", "text": "Speak with a Representative", "next": "contact_rep"},
        {"id": "6", "text": "Return to Main Menu", "next": "main"}
    ]
},
"payment_info": {
    "title": "Payment Options",
    "response": "We accept the following payment methods:\n\n• Credit/Debit Cards\n• Bank Transfers\n• UPI & Wallets\n• EMI Installments (for bookings above ₹20,000)\n\nA 25% deposit is required to secure your event date.",
    "options": [
        {"id": "1", "text": "Back to Support Menu", "next": "support_menu"}
    ]
},
"cancellation_info": {
    "response": "Here’s how our cancellation policy works:\n\n• 60+ days before the event: 75% deposit refund\n• 30–59 days before: 50% refund\n• Less than 30 days: No refund\n\nCustom policies may apply based on event type or package. Please check your contract.",
    "options": [
        {"id": "1", "text": "Back to Support Menu", "next": "support_menu"}
    ]
},
"booking_status": {
    "response": "Thank you. A customer service representative will review your booking and reach out within 2 hours.",
    "next": "support_menu"
},
"contact_rep": {
    "response": "Thanks! One of our representatives will contact you within the next 2 hours.",
    "next": "main"
}

}


def chatbot_page(request):
    return render(request, 'chat3.html')


@csrf_exempt
def get_chat_response(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("msg", "").strip()
        current_menu = data.get("menu", "main")
        session_id = data.get("session_id", "default")

        if session_id not in session_data:
            session_data[session_id] = {"context": {}}

        greeting_keywords = ["hi", "hello", "hey", "greetings", "howdy", "start", "help"]
        if any(keyword in user_message.lower() for keyword in greeting_keywords) or not user_message:
            return JsonResponse({
                "menu": "main",
                "response": MENU_OPTIONS["main"]["title"],
                "options": MENU_OPTIONS["main"]["options"],
                "status": "menu"
            })

        if current_menu in MENU_OPTIONS and MENU_OPTIONS[current_menu].get("is_form", False):
            next_menu = MENU_OPTIONS[current_menu]["next"]
            return JsonResponse({
                "menu": next_menu,
                "response": MENU_OPTIONS[current_menu]["response"],
                "options": MENU_OPTIONS[next_menu]["options"],
                "status": "menu"
            })

        option_selected = None
        for option in MENU_OPTIONS.get(current_menu, {}).get("options", []):
            if user_message == option["id"] or user_message.lower() == option["text"].lower():
                option_selected = option
                break

        if option_selected:
            if "response" in option_selected:
                return JsonResponse({
                    "menu": current_menu,
                    "response": option_selected["response"],
                    "options": MENU_OPTIONS[current_menu]["options"],
                    "status": "response"
                })
            elif "next" in option_selected:
                next_menu = option_selected["next"]
                response_text = MENU_OPTIONS[next_menu].get("title", "")
                if "description" in MENU_OPTIONS[next_menu]:
                    response_text += "\n\n" + MENU_OPTIONS[next_menu]["description"]

                return JsonResponse({
                    "menu": next_menu,
                    "response": response_text,
                    "options": MENU_OPTIONS[next_menu]["options"],
                    "status": "menu"
                })

        return JsonResponse({
            "menu": "main",
            "response": "Sorry, I didn’t understand. Please try again.",
            "options": MENU_OPTIONS["main"]["options"],
            "status": "error"
        })